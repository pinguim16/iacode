"""Real Git input-view controls; no snapshot ceiling, mandatory project or assertion is relaxed."""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from typing import override
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
POLICY = {
    "schemaVersion": "2.0.0",
    "additionalRootFiles": [".dockerignore", ".gitignore", "ruff.toml", "verify.ps1"],
}


class M2SelfSnapshotTests(unittest.TestCase):
    @override
    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="iacode-m2-self-view-")
        self.addCleanup(self.owner.cleanup)
        self.directory = Path(self.owner.name)
        self.source = self.directory / "source"
        self.source.mkdir()
        self.git("init", "--quiet", "--initial-branch=main")
        self.files = {
            ".iacode/policies/assurance-scope.json": json.dumps(POLICY).encode(),
            ".dockerignore": b"local-only\n",
            "LICENSE": b"fixture license\n",
            "apps/api/pyproject.toml": b'[project]\nname="actual-api"\nversion="0.1.0"\n',
            "apps/api/tests/test_real.py": b"def test_actual():\n    assert 2 + 2 == 4\n",
            "apps/api/docs/checkpoints/test_not_top_level.py": b"# keep actual nested input\n",
            "future-project/package.json": (
                b'{"name":"actual-future-project","scripts":{"test":"node test.cjs"}}\n'
            ),
            "future-project/test.cjs": b"require('node:assert').equal(2 + 2, 4);\n",
            "future-project/binary.dat": b"actual binary\x00\xff\r\n",
            "docs/checkpoints/FIXTURE/REPORT.json": b'{"kind":"old-audit-output"}\n',
            "docs/checkpoints/FIXTURE/audit-harness/helper.py": (
                b"# separately validated checkpoint helper\n"
            ),
        }
        for name, raw in self.files.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.commit()
        path = ROOT / "scripts/iacode/self_qualification_source.py"
        spec = importlib.util.spec_from_file_location("m2_actual_self_snapshot", path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def git(self, *arguments, data=None):
        result = subprocess.run(
            ["git", "-c", "core.longpaths=true", "-c", "core.autocrlf=false", *arguments],
            cwd=self.source,
            input=data,
            capture_output=True,
            check=True,
        )
        return result.stdout

    def commit(self):
        self.git("add", "--all")
        self.git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "owned inputs",
        )

    def test_every_committed_non_checkpoint_file_and_future_project_remains_byte_exact(self):
        target = self.directory / "view"
        before = (self.source / ".git/config").read_bytes()
        manifest = self.module.materialize_committed_source(self.source, target)
        expected = {
            name: raw
            for name, raw in self.files.items()
            if not name.startswith("docs/checkpoints/")
        }
        actual = {
            path.relative_to(target).as_posix(): path.read_bytes()
            for path in target.rglob("*")
            if path.is_file()
        }
        self.assertEqual(set(actual), set(expected) | {self.module.SIDECAR})
        for name, raw in expected.items():
            self.assertEqual(actual[name], raw)
        self.assertEqual(
            manifest["subjectCommit"], self.git("rev-parse", "HEAD").decode("ascii").strip()
        )
        self.assertEqual(manifest["selectedFiles"], len(expected))
        self.assertEqual(manifest["selectedBytes"], sum(map(len, expected.values())))
        self.assertEqual(manifest["excludedCheckpointFiles"], 2)
        self.assertFalse(manifest["generalSnapshotLimitsChanged"])
        self.assertEqual(before, (self.source / ".git/config").read_bytes())

    def test_dirty_source_policy_changes_and_untracked_files_cannot_replace_committed_inputs(self):
        (self.source / ".iacode/policies/assurance-scope.json").write_bytes(
            b"not the committed policy"
        )
        (self.source / "future-project/test.cjs").write_bytes(b"uncommitted replacement")
        (self.source / "untracked.txt").write_bytes(b"untracked input")
        target = self.directory / "view"
        self.module.materialize_committed_source(self.source, target)
        self.assertEqual(
            (target / "future-project/test.cjs").read_bytes(), self.files["future-project/test.cjs"]
        )
        self.assertEqual(
            (target / ".iacode/policies/assurance-scope.json").read_bytes(),
            self.files[".iacode/policies/assurance-scope.json"],
        )
        self.assertFalse((target / "untracked.txt").exists())

    def test_repeated_views_bind_the_same_tree_and_complete_selection_without_observation_time(
        self,
    ):
        first, second = self.directory / "first", self.directory / "second"
        one = self.module.materialize_committed_source(self.source, first)
        two = self.module.materialize_committed_source(self.source, second)
        self.assertEqual(one, two)
        self.assertEqual(
            (first / self.module.SIDECAR).read_bytes(), (second / self.module.SIDECAR).read_bytes()
        )

    def test_real_archive_export_filters_cannot_replace_the_committed_blob(self):
        content = b"// $Format:%H$\nrequire('node:assert').equal(2 + 2, 4);\n"
        (self.source / ".gitattributes").write_bytes(b"*.cjs export-subst\n")
        (self.source / "future-project/test.cjs").write_bytes(content)
        self.commit()
        archive_bytes = self.git("archive", "--format=tar", "HEAD", "--", "future-project/test.cjs")
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:") as archive:
            stream = archive.extractfile("future-project/test.cjs")
            with stream:
                exported = stream.read()
        self.assertNotEqual(exported, content)
        self.assertIn(self.git("rev-parse", "HEAD").strip(), exported)
        target = self.directory / "actual-view"
        self.module.materialize_committed_source(self.source, target)
        self.assertEqual((target / "future-project/test.cjs").read_bytes(), content)

    def test_canonical_scope_disagreement_is_a_refusal_not_a_narrowed_view(self):
        target = self.directory / "never"
        with (
            mock.patch.object(self.module, "in_assurance_scope", return_value=True),
            self.assertRaisesRegex(ValueError, "CANONICAL_SCOPE_REQUIRES_CHECKPOINT_INPUTS"),
        ):
            self.module.materialize_committed_source(self.source, target)
        self.assertFalse(target.exists())

    def test_existing_destination_is_not_overwritten_or_cleaned(self):
        target = self.directory / "existing"
        target.mkdir()
        (target / "sentinel").write_bytes(b"preserve")
        with self.assertRaisesRegex(ValueError, "FRESH_UNREDIRECTED"):
            self.module.materialize_committed_source(self.source, target)
        self.assertEqual((target / "sentinel").read_bytes(), b"preserve")
        self.assertEqual(list(target.iterdir()), [target / "sentinel"])

    def test_real_nonregular_git_object_is_refused_before_any_materialization(self):
        identifier = (
            self.git("hash-object", "-w", "--stdin", data=b"outside-target\n")
            .decode("ascii")
            .strip()
        )
        for label, mode, name in (
            ("nonregular", "120000", "alias"),
            ("windows-alternate-stream", "100644", "future-project/owned.txt:stream"),
        ):
            with self.subTest(premise=label):
                scoped = ("-c", "core.protectNTFS=false")
                self.git(
                    *scoped,
                    "update-index",
                    "--add",
                    "--cacheinfo",
                    mode + "," + identifier + "," + name,
                )
                self.git(
                    *scoped,
                    "-c",
                    "user.name=Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "commit",
                    "-qm",
                    label,
                )
                target = self.directory / label
                with self.assertRaisesRegex(ValueError, "NONREGULAR_OR_AMBIGUOUS"):
                    self.module.materialize_committed_source(self.source, target)
                self.assertFalse(target.exists())
                self.git(*scoped, "update-index", "--force-remove", name)

    def test_unknown_committed_policy_is_not_silently_downgraded(self):
        (self.source / ".iacode/policies/assurance-scope.json").write_text(
            json.dumps({"schemaVersion": "999", "additionalRootFiles": []}), encoding="utf-8"
        )
        self.commit()
        target = self.directory / "never"
        ledger_error = sys.modules["ledger_common"].LedgerError
        with self.assertRaisesRegex(ledger_error, "unsupported or narrowed"):
            self.module.materialize_committed_source(self.source, target)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
