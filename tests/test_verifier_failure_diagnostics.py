from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
SPEC = importlib.util.spec_from_file_location("diagnostic_repository_verify",
                                            ROOT / "scripts/iacode/verify.py")
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)


class VerifierFailureDiagnosticsTests(unittest.TestCase):
    def execute(self, lines: list[str], code: int):
        script = f"print({chr(10).join(lines)!r}); raise SystemExit({code})"
        stage = VERIFY.Stage("diagnostic-control", "actual subprocess control",
                             [sys.executable, "-c", script])
        with contextlib.redirect_stdout(io.StringIO()):
            return VERIFY.run(stage, quiet=True, environment=None)

    def test_failed_case_identifiers_survive_a_tail_longer_than_the_report_limit(self) -> None:
        header = ("FAIL: test_contract (test_example.Example.test_contract) "
                  "(checkpoint='GATE-4-CP-0009')")
        stage = self.execute([header, "FAILED suite/test_case.py::test_probe - omitted body",
                              *("ordinary progress" for _ in range(40))], 1)
        self.assertFalse(stage.ok)
        self.assertNotIn(header, stage.output_tail)
        self.assertEqual(stage.extra["failureHeaders"], [
            header, "FAILED suite/test_case.py::test_probe"])
        self.assertEqual(stage.extra["failureHeaderCount"], 2)
        self.assertFalse(stage.extra["failureHeadersTruncated"])

    def test_parameter_and_message_content_never_enters_failure_identifiers(self) -> None:
        stage = self.execute([
            "FAIL: test_contract (test_example.Example.test_contract) (payload='private')",
            "FAILED suite/test_case.py::test_probe[private] - private body",
        ], 1)
        self.assertEqual(stage.extra["failureHeaders"], [
            "FAIL: test_contract (test_example.Example.test_contract)",
            "FAILED suite/test_case.py::test_probe"])
        self.assertNotIn("private", repr(stage.extra))

    def test_successful_subprocess_cannot_create_a_failure_record_from_printed_text(self) -> None:
        stage = self.execute(["FAIL: test_fake (test_example.Example.test_fake)"], 0)
        self.assertTrue(stage.ok)
        self.assertNotIn("failureHeaders", stage.extra)

    def test_identifier_storage_is_bounded_with_truthful_total_and_truncation(self) -> None:
        stage = self.execute(["FAIL: test_probe (test_example.Example.test_probe)"] * 300, 1)
        self.assertEqual(len(stage.extra["failureHeaders"]), 256)
        self.assertEqual(stage.extra["failureHeaderCount"], 300)
        self.assertTrue(stage.extra["failureHeadersTruncated"])


if __name__ == "__main__":
    unittest.main()
