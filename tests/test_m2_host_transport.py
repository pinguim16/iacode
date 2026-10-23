"""Actual host Red Team transport under long Windows paths; no successful producer is simulated."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import override
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class M2HostTransportTests(unittest.TestCase):
    @override
    def setUp(self):
        search = mock.patch.object(
            sys, "path", [str(ROOT / "scripts/development-ledger"), *sys.path]
        )
        search.start()
        self.addCleanup(search.stop)

    def module(self):
        path = ROOT / "scripts/development-ledger/gate4_red_team.py"
        spec = importlib.util.spec_from_file_location("m2_actual_host_transport", path)
        module = importlib.util.module_from_spec(spec)
        with mock.patch.object(sys, "path", [str(path.parent), *sys.path]):
            spec.loader.exec_module(module)
        return module

    def git(self, root, *arguments):
        return subprocess.run(
            ["git", "-c", "core.longpaths=true", *arguments],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout

    def test_real_short_null_and_long_host_transport_preserve_exact_bytes_and_parent_configuration(
        self,
    ):
        module = self.module()
        parent = dict(os.environ)
        global_before = subprocess.run(
            ["git", "config", "--global", "--get", "core.longpaths"],
            capture_output=True,
            check=False,
        )
        with tempfile.TemporaryDirectory(prefix="iacode-m2-host-transport-") as temporary:
            owner = Path(temporary)
            source = owner / "source"
            source.mkdir()
            self.git(source, "init", "--quiet", "--initial-branch=main")
            self.git(source, "config", "--local", "core.longpaths", "false")
            leaf = Path("evidence") / ("x" * 180 + ".raw")
            (source / leaf).parent.mkdir()
            content = b"actual host transport\x00\xff\r\n"
            (source / leaf).write_bytes(content)
            self.git(source, "add", "--all")
            self.git(
                source,
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "-qm",
                "owned",
            )
            local_before = (source / ".git/config").read_bytes()
            for label, relative in (
                ("null", Path("short")),
                ("long", Path("nested") / ("d" * 80) / "repository"),
            ):
                with self.subTest(premise=label):
                    clone = owner / relative
                    clone.parent.mkdir(parents=True, exist_ok=True)
                    cloned, detached, environment = module._review_transport_setup(source, clone)
                    self.assertEqual(cloned.returncode, 0, cloned.stdout)
                    self.assertEqual(detached.returncode, 0, detached.stdout)
                    self.assertEqual((clone / leaf).read_bytes(), content)
                    if label == "long":
                        self.assertGreater(len(str(clone / leaf)), 260)
                    self.assertNotIn(b"longpaths", (clone / ".git/config").read_bytes())
                    actual = subprocess.run(
                        ["git", "config", "--get", "core.longpaths"],
                        cwd=clone,
                        env=environment,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual((actual.returncode, actual.stdout.strip()), (0, b"true"))
            self.assertEqual(local_before, (source / ".git/config").read_bytes())
        self.assertFalse(owner.exists())
        self.assertEqual(parent, dict(os.environ))
        global_after = subprocess.run(
            ["git", "config", "--global", "--get", "core.longpaths"],
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            (global_before.returncode, global_before.stdout),
            (global_after.returncode, global_after.stdout),
        )

    def test_missing_source_is_a_real_nonzero_refusal_not_successful_transport(self):
        module = self.module()
        with tempfile.TemporaryDirectory(prefix="iacode-m2-host-refusal-") as temporary:
            owner = Path(temporary)
            cloned, detached, _environment = module._review_transport_setup(
                owner / "absent", owner / "clone"
            )
            self.assertNotEqual(cloned.returncode, 0)
            self.assertEqual(detached.returncode, cloned.returncode)
            self.assertFalse((owner / "clone").exists())

    def test_malformed_inherited_runtime_configuration_refuses_before_git_launch(self):
        module = self.module()
        with (
            mock.patch.dict(os.environ, {"GIT_CONFIG_COUNT": "-1"}),
            mock.patch.object(module.subprocess, "run") as run,
        ):
            with self.assertRaises(module.LedgerError):
                module._review_transport_setup(ROOT, ROOT / "not-created")
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
