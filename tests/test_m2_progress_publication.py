"""Publication policy controls; modeled lint facts never mean repository lint ran."""

import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import override
from unittest.mock import patch

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "docs/checkpoints/GATE-7-CP-0003/audit-harness")
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/development-ledger"))
import authored_python_quality
import ledger_common
from ledger_common import canonical_hash_path, write_json

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/checkpoints/GATE-7-CP-0003/audit-harness"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


publication = module("m2_publication_unit", HERE / "publish_progress.py")
quality = module("m2_quality_owner_unit", HERE / "run_published_green_keeper.py")


class PublicationCallerTests(unittest.TestCase):
    def assert_precondition_first(self, source):
        tree = ast.parse(source)
        main = next(
            node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"
        )
        steps = next(
            node.value
            for node in ast.walk(main)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "steps" for target in node.targets
            )
        )
        self.assertEqual(
            "current-lint-precondition",
            ast.literal_eval(steps.elts[0].elts[0]),
            "current canonical lint must be checked before staging/commit/tag/push",
        )
        self.assertEqual(
            "current-authored-quality-precondition", ast.literal_eval(steps.elts[1].elts[0])
        )

    def test_actual_publisher_checks_current_lint_before_publication_effects(self):
        self.assert_precondition_first((HERE / "publish_progress.py").read_text(encoding="utf-8"))

    def test_archived_actual_publisher_without_precondition_is_rejected(self):
        source = (
            ROOT
            / "docs/checkpoints/GATE-7-CP-0003/raw-preimages/PRE-PUSH-LINT-001-publish-progress.py"
        )
        with self.assertRaises(AssertionError):
            self.assert_precondition_first(source.read_text(encoding="utf-8"))

    def test_unchanged_whole_tree_codepage_guard_covers_current_m2_sources(self):
        inherited = module("m2_inherited_decoder_guard", ROOT / "tests/test_gate0_foundation.py")
        case = inherited.SubprocessDecodingTests("test_no_capture_relies_on_the_platform_codepage")
        case.test_no_capture_relies_on_the_platform_codepage()


class PublicationProofDecisionTests(unittest.TestCase):
    """Modeled lint facts for a verifier decision, never live lint or a real push."""

    @override
    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="iacode-m2-publish-policy-")
        self.addCleanup(self.owner.cleanup)
        self.root = Path(self.owner.name).resolve()
        self.checkpoint = self.root / "docs/checkpoints/GATE-7-CP-0003"
        self.checkpoint.mkdir(parents=True)
        self.git("init", "-b", "main")
        (self.root / "README.md").write_text(
            "Modeled publication proof unit fixture\n", encoding="utf-8"
        )
        self.git("add", "README.md")
        self.git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "fixture",
        )
        self.head = self.git("rev-parse", "HEAD").strip()
        policy = self.root / ".iacode/policies/quality-gates.json"
        policy.parent.mkdir(parents=True)
        policy.write_bytes((ROOT / ".iacode/policies/quality-gates.json").read_bytes())
        self.wrapper = "docs/checkpoints/GATE-7-CP-0003/audit-harness/run_causal.py"
        (self.root / self.wrapper).parent.mkdir()
        (self.root / self.wrapper).write_text(
            "# Modeled wrapper identity, not executed\n", encoding="utf-8"
        )
        self.folder = self.checkpoint / "quality-attempts/lint"
        self.folder.mkdir(parents=True)
        self.proof = self.folder / "run-0001.json"
        self.fingerprint = "f" * 64
        streams = {}
        for name, raw in (("stdout", b"MODELED_UNIT_OBSERVATION\n"), ("stderr", b"")):
            path = self.folder / ("run-0001." + name + ".log")
            path.write_bytes(raw)
            streams[name] = {
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "refused": False,
                "path": path.relative_to(self.root).as_posix(),
            }
        self.receipt = {
            "startedAt": "2026-10-22T00:00:00Z",
            "finishedAt": "2026-10-22T00:00:01Z",
            "sourceFingerprint": self.fingerprint,
            "sourceUnchanged": True,
            "exitCode": 0,
            "arguments": [sys.executable, "scripts/iacode/gates/lint.py"],
            "streams": streams,
        }
        self.record = {
            "id": "cmd-unit-modeled",
            "timestamp": "2026-10-22T00:00:02Z",
            "result": "COMPLETED",
            "exitCode": 0,
            "subjectCommit": self.head,
            "stdoutArtifact": "quality-attempts/lint/run-0001.json",
            "arguments": [self.wrapper, "--gate", "lint"],
            "inputsDigest": [
                {"path": self.wrapper, "hash": canonical_hash_path(self.root / self.wrapper)}
            ],
        }
        self.write()
        self.addCleanup(patch.stopall)
        patch.object(publication, "ROOT", self.root).start()
        patch.object(publication, "CHECKPOINT", self.checkpoint).start()
        patch.object(ledger_common, "scope_fingerprint", return_value=self.fingerprint).start()

    def git(self, *arguments):
        return subprocess.run(
            ["git", *arguments],
            cwd=self.root,
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
        ).stdout

    def write(self):
        write_json(self.proof, self.receipt)
        (self.checkpoint / "COMMANDS.jsonl").write_text(
            json.dumps(self.record) + "\n", encoding="utf-8"
        )

    def test_modeled_valid_proof_is_accepted_without_git_state_effects(self):
        before = self.git("status", "--porcelain")
        result = publication.require_current_lint()
        self.assertEqual(self.head, result["subjectCommit"])
        self.assertEqual("cmd-unit-modeled", result["commandId"])
        self.assertEqual(before, self.git("status", "--porcelain"))

    def test_actual_git_capture_states_decoder_and_preserves_unicode(self):
        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        owner = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == type(self).__name__
        )
        caller = next(
            node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == "git"
        )
        capture = next(
            node
            for node in ast.walk(caller)
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "subprocess.run"
        )
        decoder = next((item.value for item in capture.keywords if item.arg == "encoding"), None)
        self.assertIsInstance(decoder, ast.Constant)
        self.assertEqual(decoder.value, "utf-8")
        message = "Actual Git Unicode capture: ação — 東京"
        self.git("-c", "i18n.commitEncoding=utf-8", "commit", "--allow-empty", "-m", message)
        observed = self.git("-c", "i18n.logOutputEncoding=utf-8", "log", "-1", "--format=%B")
        self.assertIn(message, observed)

    def test_missing_stale_failed_and_bool_exit_proofs_are_refused(self):
        original = self.proof.read_bytes()
        self.proof.unlink()
        with self.assertRaises(ValueError):
            publication.require_current_lint()
        for field, value in (
            ("sourceFingerprint", "0" * 64),
            ("exitCode", 1),
            ("exitCode", False),
            ("sourceUnchanged", False),
        ):
            with self.subTest(field=field, value=value):
                self.receipt = json.loads(original)
                self.receipt[field] = value
                self.write()
                with self.assertRaises(ValueError):
                    publication.require_current_lint()

    def test_other_head_or_unbound_artifact_cannot_serve_as_current_prepublication_proof(self):
        for field, value in (("subjectCommit", "0" * 40), ("stdoutArtifact", None)):
            original = dict(self.record)
            self.record[field] = value
            self.write()
            with self.assertRaises(ValueError):
                publication.require_current_lint()
            self.record = original

    def test_actual_stream_tamper_and_wrapper_identity_change_are_refused(self):
        path = self.root / self.receipt["streams"]["stdout"]["path"]
        original = path.read_bytes()
        path.write_bytes(b"CHANGED_ORIGINAL_BYTES\n")
        with self.assertRaises(ValueError):
            publication.require_current_lint()
        path.write_bytes(original)
        (self.root / self.wrapper).write_text("# Different wrapper identity\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            publication.require_current_lint()

    def test_latest_failed_attempt_cannot_fall_back_to_older_success(self):
        value = {**self.receipt, "exitCode": 1}
        write_json(self.folder / "run-0002.json", value)
        with self.assertRaises(ValueError):
            publication.require_current_lint()


class AuthoredQualityDecisionTests(unittest.TestCase):
    """Modeled helper receipts exercise refusal decisions, not a live Ruff verdict."""

    @override
    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="iacode-authored-proof-model-")
        self.addCleanup(self.owner.cleanup)
        self.root = Path(self.owner.name).resolve()
        self.checkpoint = self.root / "docs/checkpoints/GATE-7-CP-0003"
        self.output = self.checkpoint / "quality-attempts/helper-quality/run-0001"
        self.output.mkdir(parents=True)
        self.paths = ["helper.py"]
        (self.root / "helper.py").write_bytes(b"# Modeled source identity only\n")
        hashes = {
            name: hashlib.sha256((self.root / name).read_bytes()).hexdigest() for name in self.paths
        }
        self.proof = {
            "mode": "check",
            "result": "PASS",
            "sourceUnchanged": True,
            "sourceFingerprint": "f" * 64,
            "paths": self.paths,
            "hashesBefore": hashes,
            "hashesAfter": hashes,
            "executions": [
                {
                    "step": "check",
                    "cleanup": {"result": "PASS"},
                    "producer": {
                        "status": "COMPLETED",
                        "exitCode": 0,
                        "arguments": ["ruff", "check", *self.paths],
                    },
                }
            ],
        }
        for name, raw in (("stdout", b"MODELED_RUFF_RESULT\n"), ("stderr", b"")):
            (self.output / ("check." + name + ".log")).write_bytes(raw)
            self.proof["executions"][0]["producer"][name] = {
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "refusal": None,
            }
        self.write()
        self.addCleanup(patch.stopall)
        patch.object(publication, "ROOT", self.root).start()
        patch.object(publication, "CHECKPOINT", self.checkpoint).start()
        patch.object(ledger_common, "scope_fingerprint", return_value="f" * 64).start()
        patch.object(authored_python_quality, "authored_paths", return_value=self.paths).start()

    def write(self):
        write_json(self.output / "RECEIPT.json", self.proof)

    def test_modeled_valid_whole_scope_acceptance_has_no_source_effects(self):
        before = (self.root / "helper.py").read_bytes()
        self.assertEqual(1, publication.require_current_authored_quality()["paths"])
        self.assertEqual(before, (self.root / "helper.py").read_bytes())

    def test_missing_stale_narrowed_format_and_nonzero_proofs_are_refused(self):
        path = self.output / "RECEIPT.json"
        original = path.read_bytes()
        path.unlink()
        with self.assertRaises(ValueError):
            publication.require_current_authored_quality()
        for field, value in (
            ("mode", "format"),
            ("sourceFingerprint", "0" * 64),
            ("paths", []),
            ("sourceUnchanged", False),
        ):
            with self.subTest(field=field):
                self.proof = json.loads(original)
                self.proof[field] = value
                self.write()
                with self.assertRaises(ValueError):
                    publication.require_current_authored_quality()
        for value in (1, False):
            self.proof = json.loads(original)
            self.proof["executions"][0]["producer"]["exitCode"] = value
            self.write()
            with self.assertRaises(ValueError):
                publication.require_current_authored_quality()

    def test_changed_original_bytes_failed_cleanup_and_latest_failure_are_refused(self):
        original = json.loads(json.dumps(self.proof))
        stream = self.output / "check.stdout.log"
        raw = stream.read_bytes()
        stream.write_bytes(b"TAMPERED_UNIT_OBSERVATION\n")
        with self.assertRaises(ValueError):
            publication.require_current_authored_quality()
        stream.write_bytes(raw)
        self.proof["executions"][0]["cleanup"]["result"] = "FAIL"
        self.write()
        with self.assertRaises(ValueError):
            publication.require_current_authored_quality()
        self.proof = original
        self.write()
        later = self.output.parent / "run-0002"
        later.mkdir()
        write_json(later / "RECEIPT.json", {**self.proof, "result": "FAIL"})
        with self.assertRaises(ValueError):
            publication.require_current_authored_quality()


class QualityTemporaryOwnerTests(unittest.TestCase):
    def test_temporary_selection_is_child_local_and_contained_in_fresh_owner(self):
        before = dict(os.environ)
        with tempfile.TemporaryDirectory(prefix="iacode-m2-quality-owner-") as temporary:
            owner = Path(temporary)
            with patch.object(quality, "child_environment", return_value={"SENTINEL": "preserve"}):
                environment = quality.quality_environment(owner)
                self.assertEqual(str(owner / "temporary"), environment["TMP"])
                self.assertEqual(environment["TMP"], environment["TEMP"])
                self.assertEqual("preserve", environment["SENTINEL"])
                self.assertTrue((owner / "temporary").is_dir())
                with self.assertRaises(ValueError):
                    quality.quality_environment(owner)
            self.assertEqual(before, dict(os.environ))


if __name__ == "__main__":
    unittest.main()
