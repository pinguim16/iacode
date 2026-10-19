"""Real owned Git-object boundaries; synthetic blobs are not live delivery acceptance."""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class Gate7GitTransportTests(unittest.TestCase):
    def reader(self):
        path = ROOT / "scripts/development-ledger/review_bundle.py"
        spec = importlib.util.spec_from_file_location("gate7_actual_review_reader", path)
        if spec is None or spec.loader is None:
            raise ValueError("actual reader source required")
        module = importlib.util.module_from_spec(spec)
        with mock.patch.object(sys, "path", [str(path.parent), *sys.path]):
            spec.loader.exec_module(module)
        return module

    @contextmanager
    def repository(self):
        with tempfile.TemporaryDirectory(prefix="iacode-g7-longpath-test-") as raw:
            owner = Path(raw)
            if owner.resolve().parent != Path(tempfile.gettempdir()).resolve():
                raise ValueError("unexpected disposable Git owner")
            root = owner / "repository"
            root.mkdir()

            def git(*arguments):
                result = subprocess.run(
                    ["git", "-c", "core.longpaths=true", *arguments],
                    cwd=root,
                    capture_output=True,
                    check=False,
                )
                if result.returncode:
                    raise ValueError("actual owned Git premise failed")
                return result.stdout

            git("init", "--quiet", "--initial-branch=main")
            git("config", "--local", "core.longpaths", "false")
            target = max(240, len(str(root)) + 100)
            leaf_size = target - len(str(root)) - 1 - len("nested/") - len(".bin")
            if not 30 <= leaf_size <= 220:
                raise ValueError("actual bounded path premise unavailable")
            relative = Path("nested") / ("x" * leaf_size + ".bin")
            path = root / relative
            path.parent.mkdir()
            content = b"actual scoped Git object\x00\xff\r\n"
            path.write_bytes(content)
            (root / ".gitattributes").write_bytes(b"* -text\n")
            git("add", "--all")
            git(
                "-c",
                "user.name=IACode fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "-c",
                "commit.gpgsign=false",
                "commit",
                "-qm",
                "real long-path premise",
            )
            commit = git("rev-parse", "HEAD").decode("ascii").strip()
            expression = commit + ":" + relative.as_posix()
            self.assertEqual(len(commit), 40)
            self.assertEqual(len(str(path)), target)
            self.assertGreater(len(str(root / expression)), 260)
            self.assertEqual(path.read_bytes(), content)
            # The fixture itself proves the committed exact bytes before the target reader.
            self.assertEqual(git("show", expression), content)
            yield root, expression, path, content
        self.assertFalse(owner.exists())

    def global_setting(self):
        result = subprocess.run(
            ["git", "config", "--global", "--get", "core.longpaths"],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        return result.returncode, result.stdout

    def test_real_long_object_expression_returns_every_original_binary_byte(self):
        reader = self.reader()
        with self.repository() as (root, expression, _path, content):
            actual = reader.git(root, "show", expression, binary=True)
        self.assertEqual(actual, content)
        self.assertEqual(hashlib.sha256(actual).hexdigest(), hashlib.sha256(content).hexdigest())

    def test_git_override_is_child_scoped_and_leaves_local_and_global_settings_unchanged(self):
        reader = self.reader()
        before_global = self.global_setting()
        with self.repository() as (root, expression, _path, content):
            before_local = (root / ".git/config").read_bytes()
            actual_run = subprocess.run
            with mock.patch.object(reader.subprocess, "run", wraps=actual_run) as observed:
                actual = reader.git(root, "show", expression, binary=True)
            self.assertEqual(observed.call_args.args[0][:3], ["git", "-c", "core.longpaths=true"])
            self.assertEqual(observed.call_args.kwargs["cwd"], root)
            self.assertTrue(before_local == (root / ".git/config").read_bytes())
            self.assertEqual(actual, content)
        self.assertTrue(before_global == self.global_setting())

    def test_genuine_git_failure_stays_failed_without_rewriting_configuration_or_input(self):
        reader = self.reader()
        before_global = self.global_setting()
        with self.repository() as (root, _expression, path, content):
            before_local = (root / ".git/config").read_bytes()
            with self.assertRaises(reader.LedgerError):
                reader.git(root, "show", "not-an-existing-reference", binary=True)
            self.assertTrue(before_local == (root / ".git/config").read_bytes())
            self.assertEqual(path.read_bytes(), content)
        self.assertTrue(before_global == self.global_setting())


if __name__ == "__main__":
    unittest.main()
