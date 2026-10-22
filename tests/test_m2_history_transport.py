"""Real Git materialization; absent review producers remain failed, never bundle proof."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class M2HistoryTransportTests(unittest.TestCase):
    def reader(self):
        path = ROOT / "scripts/development-ledger/review_bundle.py"
        spec = importlib.util.spec_from_file_location("m2_real_transport_reader", path)
        reader = importlib.util.module_from_spec(spec)
        with mock.patch.object(sys, "path", [str(path.parent), *sys.path]):
            spec.loader.exec_module(reader)
        return reader

    def git(self, root, *arguments):
        result = subprocess.run(
            ["git", "-c", "core.longpaths=true", *arguments],
            cwd=root,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise ValueError("Actual owned Git fixture failed")
        return result.stdout

    def global_setting(self):
        result = subprocess.run(
            ["git", "config", "--global", "--get", "core.longpaths"],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        return result.returncode, result.stdout

    def test_real_short_null_and_long_materialization_preserve_config_and_refusal(self):
        reader = self.reader()
        before_environment, before_global = dict(os.environ), self.global_setting()
        with tempfile.TemporaryDirectory(prefix="iacode-m2-transport-") as temporary:
            owner = Path(temporary)
            source, depth = owner / "source", owner / "depth"
            source.mkdir()
            depth.mkdir()
            self.git(source, "init", "--quiet", "--initial-branch=main")
            self.git(source, "config", "--local", "core.longpaths", "false")
            self.git(
                source,
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "--allow-empty",
                "-qm",
                "empty owned base",
            )
            leaf = Path("evidence") / ("x" * 180 + ".bin")
            content = b"actual transport bytes\x00\xff\r\n"
            (source / leaf).parent.mkdir()
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
                "long owned input",
            )
            long_commit = self.git(source, "rev-parse", "HEAD").decode("ascii").strip()
            short_commit = self.git(source, "rev-parse", "HEAD~1").decode("ascii").strip()
            before_local = (source / ".git/config").read_bytes()
            actual_run = subprocess.run
            for name, commit in (("null", short_commit), ("long", long_commit)):
                with self.subTest(premise=name):
                    # Clone materializes the source HEAD before the requested detached
                    # checkout. The null must therefore expose the short source HEAD too.
                    self.git(source, "checkout", "--quiet", "--detach", commit)
                    observations = []
                    producer_scopes = []

                    def observe(arguments, results=observations, scopes=producer_scopes, **options):
                        result = actual_run(arguments, **options)
                        if arguments[0] == sys.executable:
                            environment = options.get("env") or {}
                            count = environment.get("GIT_CONFIG_COUNT")
                            index = str(int(count) - 1) if count else None
                            scopes.append(
                                (
                                    environment.get("GIT_CONFIG_KEY_" + index),
                                    environment.get("GIT_CONFIG_VALUE_" + index),
                                )
                                if index is not None
                                else None
                            )
                        if arguments[0] == "git" and "clone" in arguments:
                            clone = Path(arguments[-1])
                            path = clone / leaf
                            results.append(
                                {
                                    "clone": clone,
                                    "arguments": arguments,
                                    "actualBytes": path.read_bytes() if path.is_file() else None,
                                    "config": (clone / ".git/config").read_bytes(),
                                }
                            )
                        return result

                    # Use the real canonical caller and real Git. No successful review producer
                    # is simulated: this deliberately minimal repository contains none, so its
                    # actual Python producer exits nonzero and the whole result must remain FAIL.
                    with (
                        mock.patch.object(reader.tempfile, "tempdir", str(depth)),
                        mock.patch.object(reader.subprocess, "run", side_effect=observe),
                    ):
                        report = reader.reconstruct_twice_from_transport(
                            source,
                            source / "docs/checkpoints/TRANSPORT-CONTROL",
                            commit,
                            owner / (name + ".zip"),
                        )
                    self.assertEqual(report["cloneExitCode"], 0)
                    self.assertEqual(report["checkoutExitCode"], 0)
                    self.assertEqual(report["result"], "FAIL")
                    self.assertEqual(len(report["producerExitCodes"]), 2)
                    self.assertTrue(all(code != 0 for code in report["producerExitCodes"]))
                    self.assertEqual(producer_scopes, [("core.longpaths", "true")] * 2)
                    self.assertEqual(len(observations), 1)
                    observation = observations[0]
                    if name == "long":
                        self.assertGreater(len(str(observation["clone"] / leaf)), 260)
                        self.assertEqual(observation["actualBytes"], content)
                        self.assertEqual(
                            observation["arguments"][:3], ["git", "-c", "core.longpaths=true"]
                        )
                    else:
                        self.assertIsNone(observation["actualBytes"])
                    self.assertNotIn(b"longpaths", observation["config"])
                    self.assertFalse(observation["clone"].parent.exists())
            self.assertEqual(before_local, (source / ".git/config").read_bytes())
            self.assertFalse((owner / "null.zip").exists())
            self.assertFalse((owner / "long.zip").exists())
        self.assertFalse(owner.exists())
        self.assertEqual(before_environment, dict(os.environ))
        self.assertEqual(before_global, self.global_setting())

    def test_genuine_bad_subject_remains_refused_without_configuration_effects(self):
        reader = self.reader()
        before_environment, before_global = dict(os.environ), self.global_setting()
        with tempfile.TemporaryDirectory(prefix="iacode-m2-refusal-") as temporary:
            owner = Path(temporary)
            self.git(owner, "init", "--quiet", "--initial-branch=main")
            before = (owner / ".git/config").read_bytes()
            with self.assertRaises(reader.LedgerError):
                reader.reconstruct_twice_from_transport(
                    owner,
                    owner / "docs/checkpoints/TRANSPORT-CONTROL",
                    "not-an-existing-reference",
                    owner / "never.zip",
                )
            self.assertEqual(before, (owner / ".git/config").read_bytes())
            self.assertFalse((owner / "never.zip").exists())
        self.assertFalse(owner.exists())
        self.assertEqual(before_environment, dict(os.environ))
        self.assertEqual(before_global, self.global_setting())

    def test_legacy_git_read_gets_exact_bytes_only_with_child_runtime_override(self):
        reader = self.reader()
        path = ROOT / "tests/test_gate7_git_transport.py"
        spec = importlib.util.spec_from_file_location("m2_inherited_real_git_fixture", path)
        inherited = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(inherited)
        before_environment, before_global = dict(os.environ), self.global_setting()
        case = inherited.Gate7GitTransportTests()
        with case.repository() as (root, expression, _path, content):
            before_local = (root / ".git/config").read_bytes()
            environment = reader._transport_producer_environment()
            accepted = subprocess.run(
                ["git", "show", expression],
                cwd=root,
                env=environment,
                capture_output=True,
                check=False,
            )
            refused = subprocess.run(
                ["git", "-c", "core.longpaths=false", "show", expression],
                cwd=root,
                env=environment,
                capture_output=True,
                check=False,
            )
            self.assertEqual(accepted.returncode, 0)
            self.assertEqual(accepted.stdout, content)
            if os.name == "nt":
                self.assertNotEqual(refused.returncode, 0)
                self.assertIn(b"Filename too long", refused.stderr)
            self.assertTrue(before_local == (root / ".git/config").read_bytes())
        self.assertTrue(before_environment == dict(os.environ))
        self.assertEqual(before_global, self.global_setting())

    def test_child_runtime_configuration_preserves_existing_pairs_and_refuses_malformed_input(self):
        reader = self.reader()
        parent = dict(os.environ)
        with mock.patch.dict(
            os.environ,
            {
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "color.ui",
                "GIT_CONFIG_VALUE_0": "false",
            },
        ):
            before = dict(os.environ)
            environment = reader._transport_producer_environment()
            self.assertEqual(environment["GIT_CONFIG_COUNT"], "2")
            self.assertEqual(environment["GIT_CONFIG_KEY_0"], "color.ui")
            self.assertEqual(environment["GIT_CONFIG_VALUE_0"], "false")
            self.assertEqual(environment["GIT_CONFIG_KEY_1"], "core.longpaths")
            self.assertEqual(environment["GIT_CONFIG_VALUE_1"], "true")
            actual = subprocess.run(
                ["git", "config", "--get", "core.longpaths"],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                check=False,
            )
            self.assertEqual(actual.returncode, 0)
            self.assertEqual(actual.stdout.strip(), b"true")
            self.assertTrue(before == dict(os.environ))
        for invalid in (
            {"GIT_CONFIG_COUNT": "-1"},
            {"GIT_CONFIG_COUNT": "not-a-count"},
            {"GIT_CONFIG_COUNT": "1025"},
            {"GIT_CONFIG_COUNT": "9" * 5000},
            {"GIT_CONFIG_COUNT": "1"},
        ):
            with (
                self.subTest(premise=invalid),
                mock.patch.object(reader.os, "environ", invalid),
                mock.patch.object(reader.subprocess, "run") as process,
            ):
                with self.assertRaises(reader.LedgerError):
                    reader._transport_producer_environment()
                process.assert_not_called()
        self.assertTrue(parent == dict(os.environ))


if __name__ == "__main__":
    unittest.main()
