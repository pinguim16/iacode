"""Real owned Python producers; injected callbacks are fault controls, not OS acceptance."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/iacode"))
import client_checks
import native_editor
from native_process import NativeJobCleanupError, WindowsJob

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


class NativeProducerObservationTests(unittest.TestCase):
    def produce(self, source, *, timeout=5, cleanup_fault=False, arguments=None):
        actual = arguments or [sys.executable, "-c", source]

        class FaultAfterRealOwnedDrain(WindowsJob):
            def close(self):
                observation = super().close()
                raise NativeJobCleanupError(
                    "controlled fault after actual owned drain", observation
                )

        def execute():
            try:
                return native_editor.run_owned(
                    actual, environment={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=timeout
                )
            except Exception as error:
                return error

        if cleanup_fault:
            if os.name != "nt":
                self.skipTest("Actual Windows Job callback fault requires Windows")
            with patch.object(native_editor, "WindowsJob", FaultAfterRealOwnedDrain):
                return execute()
        return execute()

    def observation(self, outcome):
        report = getattr(outcome, "report", None)
        self.assertIsInstance(
            report, dict, "the original producer must survive cleanup/transport failure"
        )
        self.assertEqual("FAIL", report["result"])
        return report

    def test_completed_nonzero_null_preserves_interface_and_safe_exact_bytes(self):
        result = self.produce("print('NATIVE_NULL');raise SystemExit(7)")
        self.assertIsInstance(result, subprocess.CompletedProcess)
        self.assertEqual(7, result.returncode)
        self.assertIn("NATIVE_NULL", result.stdout)
        report = getattr(result, "execution", None)
        self.assertIsInstance(report, dict)
        producer = report["producer"]
        raw = ("NATIVE_NULL" + os.linesep).encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), producer["stdoutSha256"])
        self.assertEqual(len(raw), producer["stdoutBytes"])
        self.assertEqual("PASS", report["cleanup"]["result"])

    def test_failed_callback_cannot_replace_real_nonzero_producer(self):
        outcome = self.produce("print('NATIVE_PRIMARY');raise SystemExit(19)", cleanup_fault=True)
        self.assertIsInstance(outcome, NativeJobCleanupError)
        report = self.observation(outcome)
        self.assertEqual(19, report["producer"]["exitCode"])
        self.assertIn("NATIVE_PRIMARY", report["producer"]["stdout"])
        self.assertEqual("FAIL", report["cleanup"]["result"])
        self.assertEqual(0, outcome.observation["remainingAfterCleanup"])

    def test_successful_producer_with_cleanup_fault_stays_red(self):
        report = self.observation(self.produce("print('NATIVE_OK')", cleanup_fault=True))
        self.assertEqual(0, report["producer"]["exitCode"])
        self.assertEqual("FAIL", report["cleanup"]["result"])

    def test_timeout_has_partial_prefix_and_independent_actual_cleanup(self):
        result = self.produce(
            "import time;print('NATIVE_PARTIAL',flush=True);time.sleep(30)", timeout=0.5
        )
        self.assertIsInstance(result, subprocess.TimeoutExpired)
        report = self.observation(result)
        self.assertEqual("TIMEOUT", report["producer"]["status"])
        self.assertIsNone(report["producer"]["exitCode"])
        self.assertIn("NATIVE_PARTIAL", report["producer"]["stdout"])
        self.assertEqual("PASS", report["cleanup"]["result"])

    def test_timeout_and_callback_failure_keep_both_observations(self):
        report = self.observation(
            self.produce(
                "import time;print('NATIVE_PARTIAL',flush=True);time.sleep(30)",
                timeout=0.5,
                cleanup_fault=True,
            )
        )
        self.assertEqual("TIMEOUT", report["producer"]["status"])
        self.assertIn("NATIVE_PARTIAL", report["producer"]["stdout"])
        self.assertEqual("FAIL", report["cleanup"]["result"])

    def test_actual_missing_executable_has_typed_launch_fact(self):
        with tempfile.TemporaryDirectory(prefix="iacode-native-launch-control-") as raw:
            result = self.produce("", arguments=[str(Path(raw) / "absent.exe")])
        report = self.observation(result)
        self.assertEqual("LAUNCH_ERROR", report["producer"]["status"])
        self.assertIsNone(report["producer"]["exitCode"])

    def test_invalid_utf8_keeps_original_digest_without_replacement(self):
        result = self.produce("import sys;sys.stdout.buffer.write(bytes([255,254,65]))")
        fact = self.observation(result)["producer"]
        self.assertIsNone(fact["stdout"])
        self.assertEqual("OUTPUT_ENCODING", fact["stdoutRefusal"])
        self.assertEqual(hashlib.sha256(bytes([255, 254, 65])).hexdigest(), fact["stdoutSha256"])

    def test_output_limit_refuses_text_but_keeps_exact_raw_identity(self):
        size = client_checks.MAX_OBSERVATION_BYTES + 1
        result = self.produce("import sys;sys.stdout.buffer.write(b'x'*" + str(size) + ")")
        fact = self.observation(result)["producer"]
        self.assertIsNone(fact["stdout"])
        self.assertEqual("OUTPUT_LIMIT", fact["stdoutRefusal"])
        self.assertEqual(size, fact["stdoutBytes"])
        self.assertEqual(hashlib.sha256(b"x" * size).hexdigest(), fact["stdoutSha256"])

    def test_scanner_failure_refuses_without_publishing_exception_body(self):
        with patch.object(
            client_checks, "find_secret_kinds", side_effect=RuntimeError("PRIVATE_SCANNER_BODY")
        ):
            result = self.produce("print('NATIVE_SCANNER')")
        report = self.observation(result)
        self.assertEqual("OUTPUT_SCAN_FAILED", report["producer"]["stdoutRefusal"])
        self.assertNotIn("PRIVATE_SCANNER_BODY", str(result))

    def test_native_actor_forwards_producer_facts_without_approving_cleanup_failure(self):
        with tempfile.TemporaryDirectory(prefix="iacode-native-observation-forward-") as raw:
            actor = native_editor.NativeEditor.__new__(native_editor.NativeEditor)
            actor.directory = actor.extensions = actor.driver = actor.workspace = Path(raw)
            actor.common = ["Code.exe"]
            actor.protocol_digest = "a" * 64
            fact = {"result": "FAIL", "phase": "FORCED_DRAIN", "pendingProcessCount": 1}
            error = NativeJobCleanupError("owned native process cleanup failed", fact)
            error.report = {
                "result": "FAIL",
                "producer": {
                    "status": "COMPLETED",
                    "exitCode": 17,
                    "stdout": "ACTUAL_RETAINED_PREFIX",
                },
                "cleanup": {"result": "FAIL", "observation": fact},
            }
            with patch.object(native_editor, "run_owned", side_effect=error):
                observed = actor.run("untrusted")
            self.assertEqual("FAIL", observed["result"])
            self.assertEqual(17, observed["exitCode"])
            self.assertEqual(error.report, observed["execution"])
            self.assertEqual(fact, observed["processCleanup"])

    def test_capture_handle_release_failure_cannot_replace_primary_observation(self):
        actual_file = tempfile.TemporaryFile

        def controlled_release_fault(*args, **kwargs):
            actual = actual_file(*args, **kwargs)

            class ActualFileWithPostReleaseFault:
                def __enter__(self):
                    return self

                def __exit__(self, *_args):
                    self.close()

                def __getattr__(self, key):
                    return getattr(actual, key)

                def close(self):
                    actual.close()
                    raise OSError("PRIVATE_RELEASE_BODY")

            return ActualFileWithPostReleaseFault()

        with patch.object(tempfile, "TemporaryFile", side_effect=controlled_release_fault):
            result = self.produce("print('NATIVE_RELEASE_PRIMARY')")
        report = self.observation(result)
        self.assertEqual(0, report["producer"]["exitCode"])
        self.assertIn("NATIVE_RELEASE_PRIMARY", report["producer"]["stdout"])
        self.assertEqual("FAIL", report["outputRelease"]["result"])
        self.assertNotIn("PRIVATE_RELEASE_BODY", str(result))


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    unittest.main()
