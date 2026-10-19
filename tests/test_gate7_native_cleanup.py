"""Native lifecycle unit controls; actual owned-kernel proof is named separately."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from ctypes import wintypes
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
native_editor = importlib.import_module("native_editor")
native_process = importlib.import_module("native_process")


class Gate7NativeCleanupTests(unittest.TestCase):
    def actor(self):
        actor = native_process.WindowsJob.__new__(native_process.WindowsJob)
        actor.handle, actor.api = 41, mock.Mock()
        actor.active = mock.Mock(return_value=0)
        actor.owned_member_handles = mock.Mock(return_value=[(7, 101)])
        return actor

    def test_natural_physical_completion_precedes_force_inside_original_deadline(self):
        actor = self.actor()
        actor.api.WaitForSingleObject.side_effect = [258, 0]
        with (
            mock.patch.object(native_process.time, "monotonic", side_effect=[0, 0.01, 0.05]),
            mock.patch.object(native_process.time, "sleep"),
        ):
            result = actor.close()
        actor.api.TerminateJobObject.assert_not_called()
        self.assertEqual(result["observedProcessCount"], 1)
        self.assertEqual(result["signaledProcessCount"], 1)
        self.assertFalse(result["forcedTermination"])
        actor.api.CloseHandle.assert_has_calls([mock.call(101), mock.call(41)])

    def test_deadline_retains_red_bounded_physical_facts(self):
        actor = self.actor()
        actor.api.WaitForSingleObject.return_value = 258
        with (
            mock.patch.object(native_process.time, "monotonic", side_effect=[0, 11, 11]),
            self.assertRaisesRegex(RuntimeError, "did not drain") as failure,
        ):
            actor.close()
        observed = failure.exception.observation
        self.assertEqual(observed["result"], "FAIL")
        self.assertEqual(observed["totalDeadlineSeconds"], 10)
        self.assertEqual(observed["remainingJobActive"], 0)
        self.assertEqual(observed["pendingProcessCount"], 1)
        self.assertEqual(observed["signaledProcessCount"], 0)
        self.assertNotIn("101", json.dumps(observed))
        actor.api.CloseHandle.assert_has_calls([mock.call(101), mock.call(41)])

    def test_forced_fallback_pins_late_members_without_extending_deadline(self):
        actor = self.actor()
        actor.owned_member_handles.side_effect = [[(7, 101)], [(7, 201), (8, 102)]]
        actor.api.WaitForSingleObject.side_effect = [258, 0, 0]
        with (
            mock.patch.object(native_process.time, "monotonic", side_effect=[0, 1.01, 1.1]),
            mock.patch.object(native_process.time, "sleep"),
        ):
            result = actor.close()
        actor.api.TerminateJobObject.assert_called_once_with(41, 1)
        self.assertTrue(result["forcedTermination"])
        self.assertEqual(result["observedProcessCount"], 2)
        self.assertEqual(result["signaledProcessCount"], 2)
        actor.api.CloseHandle.assert_has_calls(
            [mock.call(201), mock.call(101), mock.call(102), mock.call(41)]
        )

    def test_physical_signal_observed_after_total_deadline_remains_fail(self):
        actor = self.actor()
        actor.api.WaitForSingleObject.return_value = 0
        with (
            mock.patch.object(native_process.time, "monotonic", side_effect=[0, 11]),
            self.assertRaisesRegex(RuntimeError, "did not drain") as failure,
        ):
            actor.close()
        self.assertEqual(failure.exception.observation["totalDeadlineSeconds"], 10)
        self.assertEqual(failure.exception.observation["result"], "FAIL")
        self.assertEqual(failure.exception.observation["pendingProcessCount"], 0)

    def test_failed_force_snapshot_stays_red_and_releases_original_handles(self):
        actor = self.actor()
        actor.owned_member_handles.side_effect = [[(7, 101)], RuntimeError("private-body")]
        actor.api.WaitForSingleObject.return_value = 258
        with (
            mock.patch.object(native_process.time, "monotonic", side_effect=[0, 1.01]),
            self.assertRaises(native_process.NativeJobCleanupError) as failure,
        ):
            actor.close()
        actor.api.TerminateJobObject.assert_not_called()
        self.assertEqual(failure.exception.observation["phase"], "FORCE_SNAPSHOT")
        self.assertNotIn("private-body", json.dumps(failure.exception.observation))
        self.assertNotIn("private-body", str(failure.exception))
        actor.api.CloseHandle.assert_has_calls([mock.call(101), mock.call(41)])

    def test_failed_physical_wait_never_becomes_success_or_exposes_exception_body(self):
        for status in (0xFFFFFFFF, 129):
            with self.subTest(status=status):
                actor = self.actor()
                actor.api.WaitForSingleObject.return_value = status
                with self.assertRaises(native_process.NativeJobCleanupError) as failure:
                    actor.close()
                self.assertEqual(failure.exception.observation["result"], "FAIL")
                self.assertEqual(failure.exception.observation["pendingProcessCount"], 1)
                actor.api.CloseHandle.assert_has_calls([mock.call(101), mock.call(41)])

    def test_native_run_keeps_drain_failure_red_even_with_a_child_pass_report(self):
        with tempfile.TemporaryDirectory(prefix="iacode-g7-native-red-") as raw:
            actor = native_editor.NativeEditor.__new__(native_editor.NativeEditor)
            actor.directory = actor.extensions = actor.driver = actor.workspace = Path(raw)
            actor.common = ["Code.exe"]
            actor.protocol_digest = "a" * 64
            failure = native_process.NativeJobCleanupError(
                "owned native process job did not drain",
                {"result": "FAIL", "phase": "FORCED_DRAIN", "pendingProcessCount": 2},
            )

            def failed_host(*_args, **_kwargs):
                (Path(raw) / "untrusted.json").write_text('{"result":"PASS"}\n', encoding="utf-8")
                raise failure

            with mock.patch.object(native_editor, "run_owned", side_effect=failed_host):
                observed = actor.run("untrusted")
            self.assertEqual(observed["result"], "FAIL")
            self.assertEqual(observed["mode"], "untrusted")
            self.assertEqual(observed["processCleanup"], failure.observation)
            self.assertIsNone(observed["exitCode"])

    def test_owned_bootstrap_disables_external_reporting_not_native_or_trust_controls(self):
        with tempfile.TemporaryDirectory(prefix="iacode-g7-native-bootstrap-") as raw:
            actor = native_editor.NativeEditor.__new__(native_editor.NativeEditor)
            actor.directory = actor.extensions = actor.driver = actor.workspace = Path(raw)
            actor.common = ["Code.exe", "--user-data-dir", str(Path(raw) / "profile")]
            actor.protocol_digest = "a" * 64
            completed = subprocess.CompletedProcess([], 0, "", "")
            for mode in ("package", "untrusted"):
                with mock.patch.object(native_editor, "run_owned", return_value=completed) as run:
                    result = actor.run(mode)
                arguments = run.call_args.args[0]
                self.assertIn("--disable-crash-reporter", arguments)
                self.assertIn("--disable-telemetry", arguments)
                self.assertIn("--extensionDevelopmentPath=" + str(actor.driver), arguments)
                self.assertNotIn("--disable-extensions", arguments)
                self.assertNotIn("--no-sandbox", arguments)
                self.assertNotIn("--disable-gpu-sandbox", arguments)
                self.assertEqual("--disable-workspace-trust" in arguments, mode == "package")
                self.assertEqual(result["result"], "FAIL", "absent actual child report stays red")

    @unittest.skipUnless(os.name == "nt", "Windows Job Objects require Windows")
    def test_real_owned_member_premise_and_natural_exit_preserve_outside_sentinel(self):
        import ctypes

        with native_process.owned_directory("iacode-g7-native-members-") as owned:
            ready = owned["path"] / "ready.txt"
            child_code = (
                "from pathlib import Path;import time;"
                f"Path({str(ready)!r}).write_bytes(b'ready');time.sleep(.5)"
            )
            child_job = native_process.WindowsJob()
            child = outside = None
            close_started = False
            pinned = []
            try:
                outside = subprocess.Popen(
                    [sys.executable, "-c", "import time;time.sleep(60)"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                child = subprocess.Popen(
                    [sys.executable, "-c", child_code],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW | 4,
                )
                child_job.attach_and_resume(child)
                deadline = time.monotonic() + 5
                while not ready.exists() and child.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(ready.is_file(), "real child-ready premise must reach the target")
                self.assertEqual(ready.read_bytes(), b"ready")
                pinned = child_job.owned_member_handles()
                self.assertTrue(pinned, "observed membership, never guessed exact count")
                self.assertTrue(any(pid == child.pid for pid, _ in pinned))
                contained = wintypes.BOOL()
                self.assertTrue(
                    child_job.api.IsProcessInJob(
                        wintypes.HANDLE(int(outside._handle)),
                        child_job.handle,
                        ctypes.byref(contained),
                    )
                )
                self.assertFalse(contained.value)
                self.assertIsNone(outside.poll())
                for _, handle in pinned:
                    child_job.api.CloseHandle(handle)
                pinned = []
                close_started = True
                observed = child_job.close()
                self.assertGreaterEqual(observed["observedProcessCount"], 1)
                self.assertEqual(observed["observedProcessCount"], observed["signaledProcessCount"])
                self.assertEqual(observed["remainingAfterCleanup"], 0)
                self.assertFalse(observed["forcedTermination"])
                self.assertEqual(child.wait(timeout=2), 0)
                self.assertIsNone(outside.poll(), "the independent outside sentinel survives")
            finally:
                for _, handle in pinned:
                    child_job.api.CloseHandle(handle)
                if not close_started:
                    child_job.close()
                if child is not None:
                    child.wait(timeout=12)
                if outside is not None:
                    outside.kill()  # Only this freshly owned Popen, never a historical PID.
                    outside.wait(timeout=5)
        self.assertTrue(owned["removed"])

    def test_archived_native_contexts_are_exact_inert_main_checkout_evidence(self):
        import hashlib

        checkpoint = ROOT / "docs/checkpoints/GATE-7-CP-0001"
        names = set()
        for name in ("NATIVE-REWORK-CONTEXT.json", "NATIVE-REWORK-CONTEXT-02.json"):
            manifest = json.loads((checkpoint / name).read_bytes())
            self.assertFalse(manifest["canonicalCommandIdsAdopted"])
            self.assertFalse(manifest["gateVerdictIssued"])
            self.assertFalse(manifest["trainingAllowed"])
            self.assertEqual(manifest["originalCount"], len(manifest["files"]))
            for row in manifest["files"]:
                path = checkpoint / row["archive"]
                self.assertEqual(path.suffix, ".raw")
                raw = path.read_bytes()
                self.assertEqual(len(raw), row["bytes"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
                names.add(row["originalName"])
        self.assertIn("NATIVE-OBSERVED-TRACE.json", names)
        self.assertIn("NATIVE-RELEASE-EXPERIMENT-02-TRACE.json", names)
        self.assertIn("NATIVE-GRACE-EXPERIMENT-03-TRACE.json", names)
        self.assertIn("NATIVE-CLI-WAIT-06-TRACE.json", names)
        self.assertIn("NATIVE-CRASH-OPT-OUT-07-TRACE.json", names)
        self.assertIn("native-current-local-01.json", names)


if __name__ == "__main__":
    unittest.main()
