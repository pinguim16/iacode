"""Adversarial transport/producer controls for the temporary audit bridge."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "m2_closed_runner_bridge",
    ROOT / "scripts/development-ledger/audit_runner_bridge.py")
bridge_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bridge_module
SPEC.loader.exec_module(bridge_module)
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets
from native_process import WindowsJob


@unittest.skipUnless(os.name == "nt", "The isolated bridge uses the actual Windows Job Object boundary")
class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="iacode-m2-bridge-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "runner.py"
        self.source.write_text("print('PRODUCER_NULL_OK')\n", encoding="utf-8")
        self.frozen = bridge_module.FrozenInputs(self.root, [self.source])

    def service(self, jobs=None, factory=WindowsJob):
        value = bridge_module.ClosedBridge(
            self.frozen, jobs or {"null": bridge_module.Job((sys.executable, str(self.source)), 10)},
            dict(os.environ), find_secrets, factory, (Path(sys.executable),))
        server = value.listen()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(value.close)
        return value

    def request(self, bridge, path, body=None, capability=True, **headers):
        if capability:
            headers["X-IACode-Capability"] = bridge.capability
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"http://127.0.0.1:{bridge.server.server_port}{path}", body, headers)
        try:
            with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=5) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()

    def execute(self, bridge, key="null"):
        code, _ = self.request(bridge, "/jobs", json.dumps({"job": key}).encode())
        self.assertIn(code, (200, 202))
        bridge.worker.join(timeout=15)
        self.assertFalse(bridge.worker.is_alive())
        return bridge.results[key]

    def test_actual_child_null_and_duplicate_are_one_execution(self):
        bridge = self.service()
        result = self.execute(bridge)
        self.assertEqual("PASS", result["result"])
        self.assertEqual(b"PRODUCER_NULL_OK\r\n" if os.name == "nt" else b"PRODUCER_NULL_OK\n",
                         bridge.artifacts["null"]["stdout.log"])
        worker = bridge.worker
        self.assertEqual(result, self.execute(bridge))
        self.assertIs(worker, bridge.worker)

    def test_unknown_extra_argv_env_source_duplicate_and_path_refused(self):
        bridge = self.service()
        for body in (b'{"job":"null","argv":["docker","ps"]}',
                     b'{"job":"null","env":{}}', b'{"job":"null","source":"x"}',
                     b'{"job":"null","job":"null"}', b'{"job":"../null"}',
                     b'{"job":"unknown"}', b'[]', b'{"job":4}', b'x' * 257):
            self.assertEqual(400, self.request(bridge, "/jobs", body)[0])
        self.assertIsNone(bridge.worker)

    def test_capability_origin_and_artifact_traversal_refused(self):
        bridge = self.service()
        self.assertEqual(403, self.request(bridge, "/catalog", capability=False)[0])
        self.assertEqual(403, self.request(bridge, "/catalog", Origin="http://untrusted.invalid")[0])
        self.execute(bridge)
        self.assertEqual(404, self.request(bridge, "/artifacts/null/../../runner.py")[0])
        self.assertEqual(404, self.request(bridge, "/artifacts/null/%2e%2e")[0])

    def test_changed_source_refused_before_child(self):
        bridge = self.service()
        self.source.write_text("raise SystemExit(97)", encoding="utf-8")
        result = self.execute(bridge)
        self.assertEqual("FAIL", result["result"])
        self.assertNotIn("producer", result)

    def test_hardlinked_source_refused(self):
        os.link(self.source, self.root / "alias.py")
        with self.assertRaises(ValueError):
            self.frozen.verify()

    def test_primary_nonzero_survives_postprocessing_failure(self):
        self.source.write_text("print('ADVERSE_PRODUCER'); raise SystemExit(23)\n", encoding="utf-8")
        self.frozen = bridge_module.FrozenInputs(self.root, [self.source])
        bridge = self.service({"null": bridge_module.Job((sys.executable, str(self.source)), 10,
                                                       ("absent.json",))})
        result = self.execute(bridge)
        self.assertEqual(23, result["producer"]["exitCode"])
        self.assertEqual("PASS", result["cleanup"]["result"])
        self.assertEqual(["absent.json"], result["missingReports"])
        self.assertEqual("FAIL", result["result"])

    def test_real_producer_survives_cleanup_exception(self):
        class FailedCleanup(WindowsJob):
            def close(self):
                super().close()
                raise RuntimeError("unpublishable cleanup detail")

        bridge = self.service(factory=FailedCleanup)
        result = self.execute(bridge)
        self.assertEqual(0, result["producer"]["exitCode"])
        self.assertEqual("FAIL", result["cleanup"]["result"])
        self.assertEqual("FAIL", result["result"])
        self.assertNotIn("unpublishable", json.dumps(result))
        self.assertIn(b"PRODUCER_NULL_OK", bridge.artifacts["null"]["stdout.log"])

    def test_timeout_observation_and_exact_job_cleanup(self):
        self.source.write_text("import time\nprint('BEFORE_TIMEOUT', flush=True)\ntime.sleep(30)\n", encoding="utf-8")
        self.frozen = bridge_module.FrozenInputs(self.root, [self.source])
        bridge = self.service({"null": bridge_module.Job((sys.executable, str(self.source)), 1)})
        result = self.execute(bridge)
        self.assertEqual("TIMEOUT", result["producer"]["status"])
        self.assertEqual("FAIL", result["result"])
        self.assertEqual(0, result["cleanup"]["observation"]["remainingAfterCleanup"])
        self.assertIn(b"BEFORE_TIMEOUT", bridge.artifacts["null"]["stdout.log"])

    def test_launch_error_is_explicit(self):
        bridge = self.service({"null": bridge_module.Job((str(self.root / "absent.exe"),), 1)})
        result = self.execute(bridge)
        self.assertEqual("LAUNCH_ERROR", result["producer"]["status"])
        self.assertEqual("FAIL", result["result"])

    def test_attach_failure_removes_exact_suspended_child(self):
        class FailedAttachment(WindowsJob):
            def attach_and_resume(self, process):
                raise RuntimeError("attachment refused")

        bridge = self.service(factory=FailedAttachment)
        result = self.execute(bridge)
        self.assertEqual("LAUNCH_ERROR", result["producer"]["status"])
        self.assertTrue(result["cleanup"]["unattachedOwnedProcessRemoved"])
        self.assertNotIn("processStillAlive", result["cleanup"])
        self.assertEqual("FAIL", result["result"])

    def test_secret_encoding_size_and_scanner_fail_closed_with_exact_digest(self):
        cases = [(b"x" * 1025, lambda _text: [], 1024, "OUTPUT_LIMIT"),
                 (b"\xff", lambda _text: [], 1024, "OUTPUT_ENCODING"),
                 (b"safe", lambda _text: ["detected"], 1024, "UNSAFE_OUTPUT")]

        def failed(_text):
            raise RuntimeError("scanner detail")

        cases.append((b"safe", failed, 1024, "OUTPUT_SCAN_FAILED"))
        for raw, scanner, limit, expected in cases:
            fact, output = bridge_module.observe(io.BytesIO(raw), scanner, limit)
            self.assertIsNone(output)
            self.assertEqual(expected, fact["refusal"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), fact["sha256"])

    def test_stream_read_failure_never_invents_empty_success(self):
        class FailedRead(io.BytesIO):
            def read(self, _size=-1):
                raise OSError("unpublishable read error")

        fact, output = bridge_module.observe(FailedRead(b"not-empty"), find_secrets)
        self.assertIsNone(output)
        self.assertIsNone(fact["sha256"])
        self.assertIsNone(fact["bytes"])
        self.assertEqual("OUTPUT_READ_FAILED", fact["refusal"])


if __name__ == "__main__":
    unittest.main()
