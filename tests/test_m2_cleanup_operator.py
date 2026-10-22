"""Operator unit controls only: real Python producers, no Docker/other-app effects.

The Docker transport and resource inventories are isolated test boundaries. These
cases never serve as live cleanup or functional acceptance for the actual engine.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import override
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/development-ledger"))
from ledger_common import load_json, write_json

HERE = Path(__file__).resolve().parents[1] / "docs/checkpoints/GATE-7-CP-0003/audit-harness"
SPEC = importlib.util.spec_from_file_location(
    "owned_cleanup_operator_unit", HERE / "owned_docker_scope.py"
)
scope_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scope_module)


class OperatorCleanupObservationTests(unittest.TestCase):
    @override
    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="iacode-m2cp3-cleanup-unit-")
        self.config = tempfile.TemporaryDirectory(prefix="iacode-m2cp3-buildx-unit-")
        self.addCleanup(self.owner.cleanup)
        self.addCleanup(self.config.cleanup)
        self.checkpoint = Path(self.owner.name)
        self.scope_path = self.checkpoint / "SCOPE.json"
        self.baseline = {
            "containers": [],
            "images": [],
            "networks": [],
            "volumes": [],
            "dockerConfigHash": "f" * 64,
        }
        self.scope = {
            "status": "ACTIVE",
            "builder": "iacode-m2cp3-unit-builder",
            "privateBuildxConfig": self.config.name,
            "inheritedOwnedProject": "iacode-m2cp3-unit-project",
            "registeredProjects": ["iacode-m2cp3-unit-project"],
            "before": self.baseline,
        }
        write_json(self.scope_path, self.scope)
        self.addCleanup(patch.stopall)
        patch.object(scope_module, "CHECKPOINT", self.checkpoint).start()
        patch.object(scope_module, "SCOPE", self.scope_path).start()
        self.snapshot = patch.object(scope_module, "snapshot", return_value=self.baseline).start()
        patch.object(scope_module, "configuration_hash", return_value="f" * 64).start()

    def produce(self, source, *, timeout=None, launch_error=False):
        actual_run = subprocess.run

        def transport(arguments, **kwargs):
            self.assertEqual(["docker", "buildx", "rm", self.scope["builder"]], arguments)
            if timeout is not None:
                kwargs["timeout"] = timeout
            executable = str(self.checkpoint / "absent.exe") if launch_error else sys.executable
            return actual_run([executable, "-c", source], **kwargs)

        with patch.object(scope_module.subprocess, "run", side_effect=transport):
            code = scope_module.cleanup()
        return code, load_json(self.checkpoint / "OWNED-RESOURCE-CLEANUP.json")

    def test_prior_receipt_refuses_before_queries_or_effects(self):
        target = self.checkpoint / "OWNED-RESOURCE-CLEANUP.json"
        target.write_bytes(b"PRIOR_OBSERVATION_MUST_NOT_CHANGE")
        with (
            patch.object(scope_module, "child_environment") as environment,
            self.assertRaises(ValueError),
        ):
            scope_module.cleanup()
        environment.assert_not_called()
        self.snapshot.assert_not_called()
        self.assertEqual(b"PRIOR_OBSERVATION_MUST_NOT_CHANGE", target.read_bytes())

    def test_nonzero_actual_child_preserves_both_safe_streams(self):
        code, receipt = self.produce(
            "import sys;print('CLEANUP_STDOUT');print('CLEANUP_STDERR',fi"
            "le=sys.stderr);raise SystemExit(23)"
        )
        self.assertEqual(1, code)
        command = receipt["commands"][0]
        self.assertEqual("COMPLETED", command["status"])
        self.assertEqual(23, command["exitCode"])
        for stream, label in (("stdout", "CLEANUP_STDOUT"), ("stderr", "CLEANUP_STDERR")):
            raw = (label + os.linesep).encode()
            fact = command["streams"][stream]
            self.assertEqual(raw, fact["text"].encode())
            self.assertEqual(hashlib.sha256(raw).hexdigest(), fact["sha256"])
            self.assertEqual(len(raw), fact["bytes"])
        self.assertTrue(receipt["privateBuildxConfigRetainedForRecovery"])
        self.assertEqual("FAIL", receipt["result"])

    def test_actual_timeout_has_partial_output_and_not_success(self):
        code, receipt = self.produce(
            "import time;print('PARTIAL_CLEANUP',flush=True);time.sleep(30)", timeout=0.3
        )
        self.assertEqual(1, code)
        command = receipt["commands"][0]
        self.assertEqual("TIMEOUT", command["status"])
        self.assertIsNone(command["exitCode"])
        self.assertIn("PARTIAL_CLEANUP", command["streams"]["stdout"]["text"])
        self.assertEqual("FAIL", receipt["result"])

    def test_actual_launch_error_is_typed_and_not_success(self):
        code, receipt = self.produce("", launch_error=True)
        self.assertEqual(1, code)
        self.assertEqual("LAUNCH_ERROR", receipt["commands"][0]["status"])
        self.assertIsNone(receipt["commands"][0]["exitCode"])

    def test_success_null_removes_only_the_owned_empty_fixture_directory(self):
        code, receipt = self.produce("print('OWNED_UNIT_NULL')")
        self.assertEqual(0, code)
        self.assertEqual("PASS", receipt["result"])
        self.assertTrue(receipt["privateBuildxConfigRemoved"])
        self.assertFalse(Path(self.config.name).exists())
        self.assertTrue(self.checkpoint.exists())


if __name__ == "__main__":
    unittest.main()
