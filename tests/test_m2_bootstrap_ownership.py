"""Actual bootstrap caller guard and owned surviving-writer proof; no engine operations."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/development-ledger"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/iacode"))
from audit_runner_bridge import Job, run_owned
from ledger_common import find_secrets
from native_process import WindowsJob

ROOT = Path(__file__).resolve().parents[1]


class BootstrapOwnershipTests(unittest.TestCase):
    def assert_owned_caller(self, source, method_name="bootstrap_builder"):
        tree = ast.parse(source)
        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == method_name
        )
        calls = [node for node in ast.walk(method) if isinstance(node, ast.Call)]
        self.assertTrue(
            any(isinstance(node.func, ast.Name) and node.func.id == "run_owned" for node in calls),
            "actual bootstrap must invoke the existing owned runner",
        )
        self.assertTrue(
            any(
                isinstance(node.func, ast.Name)
                and node.func.id == "Job"
                and len(node.args) == 2
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value == 60
                for node in calls
            ),
            "repair must preserve the measured producer budget",
        )
        self.assertFalse(
            any(
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and node.func.attr in ("run", "Popen")
                for node in calls
            ),
            "direct unowned capture cannot drain descendants",
        )

    def test_actual_bootstrap_caller_requires_owned_native_process_boundary(self):
        path = ROOT / "docs/checkpoints/GATE-7-CP-0003/audit-harness/current_resources.py"
        self.assert_owned_caller(path.read_text(encoding="utf-8"))

    def test_actual_history_query_requires_the_same_owned_native_boundary(self):
        path = ROOT / "docs/checkpoints/GATE-7-CP-0003/audit-harness/capture_owned_build_history.py"
        self.assert_owned_caller(path.read_text(encoding="utf-8"), "capture")

    def test_exact_published_history_preimage_is_rejected_by_the_same_guard(self):
        path = "docs/checkpoints/GATE-7-CP-0003/audit-harness/capture_owned_build_history.py"
        original = subprocess.run(
            ["git", "--no-pager", "show", "477ec86f09c5e03ad328cf40a3725855b3526bad:" + path],
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
        with self.assertRaises(AssertionError):
            self.assert_owned_caller(original.decode("utf-8"), "capture")

    def test_archived_actual_preimage_is_rejected_by_identical_caller_guard(self):
        path = ROOT / (
            "docs/checkpoints/GATE-7-CP-0003/raw-preimages/BOOTSTRAP-DRAIN-001-current-resources.py"
        )
        with self.assertRaises(AssertionError):
            self.assert_owned_caller(path.read_text(encoding="utf-8"))

    @unittest.skipUnless(os.name == "nt", "Uses actual Windows owned process handles")
    def test_real_parent_exit_with_inherited_output_writer_is_observed_then_exactly_drained(self):
        source = (
            "import subprocess,sys; "
            "subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],"
            "stdout=sys.stdout,stderr=sys.stderr); print('OWNED_INHERITED_WRITER',flush=True)"
        )
        with tempfile.TemporaryDirectory(prefix="iacode-m2-bootstrap-owned-") as temporary:
            result, streams = run_owned(
                Job((sys.executable, "-c", source), 5),
                Path(temporary),
                dict(os.environ),
                find_secrets,
                WindowsJob,
            )
        self.assertEqual("COMPLETED", result["producer"]["status"])
        self.assertEqual(0, result["producer"]["exitCode"])
        self.assertEqual("PASS", result["cleanup"]["result"])
        self.assertEqual(0, result["cleanup"]["observation"]["remainingAfterCleanup"])
        self.assertIn(b"OWNED_INHERITED_WRITER", streams["stdout.log"])
        self.assertIsNone(result["producer"]["stdout"]["refusal"])


if __name__ == "__main__":
    unittest.main()
