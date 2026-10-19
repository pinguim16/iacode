"""Real literal Git staging across the Windows aggregate argv boundary."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Gate7PublicationPathTests(unittest.TestCase):
    def owner(self):
        path = ROOT / "docs/checkpoints/GATE-7-CP-0001/audit-harness/publish_progress.py"
        spec = importlib.util.spec_from_file_location("g7_publish_path_tests", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def git(self, root, *args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True).stdout

    def initialize(self, root):
        self.git(root, "init", "--quiet", "--initial-branch=main")
        (root / "base.txt").write_bytes(b"base\n")
        self.git(root, "add", "base.txt")
        self.git(
            root,
            "-c",
            "user.name=IACode fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "base",
        )

    def test_literal_nul_transport_stages_every_path_beyond_windows_aggregate_limit(self):
        with tempfile.TemporaryDirectory(prefix="iacode-g7-pathspec-") as raw:
            root = Path(raw)
            self.initialize(root)
            names = [f"item-{index:04d}-" + "x" * 104 + ".txt" for index in range(300)]
            names += ["literal[0].txt", "unicode-ç.txt", "space file.txt"]
            for name in names:
                (root / name).write_bytes(name.encode("utf-8"))
            self.assertGreater(len(subprocess.list2cmdline(["git", "add", "--", *names])), 32767)
            self.owner().stage_declared_paths(root, [*names, "base.txt"])
            observed = self.git(root, "diff", "--cached", "--name-only", "-z")
            self.assertEqual(set(observed.decode("utf-8").split("\0")) - {""}, set(names))
            self.assertEqual(self.git(root, "show", ":literal[0].txt"), b"literal[0].txt")

    def test_undeclared_change_refuses_before_effect_and_declared_deletion_is_staged(self):
        with tempfile.TemporaryDirectory(prefix="iacode-g7-pathspec-denied-") as raw:
            root = Path(raw)
            self.initialize(root)
            (root / "unlisted.txt").write_bytes(b"not declared")
            with self.assertRaisesRegex(ValueError, "explicitly declared"):
                self.owner().stage_declared_paths(root, ["base.txt"])
            self.assertEqual(self.git(root, "diff", "--cached", "--name-only"), b"")
            (root / "base.txt").unlink()
            self.owner().stage_declared_paths(root, ["base.txt", "unlisted.txt"])
            self.assertEqual(
                self.git(root, "diff", "--cached", "--name-status").decode().splitlines(),
                ["D\tbase.txt", "A\tunlisted.txt"],
            )


if __name__ == "__main__":
    unittest.main()
