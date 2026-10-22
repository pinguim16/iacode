"""Unchanged continuation contract over corrective and current actual documents."""

import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/development-ledger"))
import test_gate7_continuation as continuation_contract
from validate_checkpoint import HANDOFF_HEADINGS

ROOT = Path(__file__).resolve().parents[1]
CORRECTION = ROOT / "docs/checkpoints/GATE-7-CP-0003"


class CorrectiveContinuationTests(unittest.TestCase):
    def current_checkpoints(self):
        latest = (ROOT / "docs/checkpoints/LATEST.md").read_text(encoding="utf-8")
        reference = re.search(r"Checkpoint: `([^`]+)`", latest)
        self.assertIsNotNone(reference)
        current = (ROOT / reference.group(1)).resolve()
        self.assertTrue(current.is_relative_to(ROOT))
        return sorted({CORRECTION, current})

    def lessons(self, checkpoint):
        rows = [
            json.loads(line)
            for line in (ROOT / ".iacode/memory/lessons.jsonl").read_bytes().splitlines()
            if line
        ]
        return [
            row
            for row in rows
            if row["source"]["checkpoint"] == checkpoint.name
            or any(
                item["checkpoint"] == checkpoint.name for item in row.get("guardrailFailures", [])
            )
            or any(
                "/" + checkpoint.name + "/" in reference for reference in row.get("evidence", [])
            )
        ]

    def test_actual_corrective_and_current_handoff_next_preserve_existing_contract(self):
        guard = continuation_contract.Gate7ContinuationContractTests()
        for checkpoint in self.current_checkpoints():
            with self.subTest(checkpoint=checkpoint.name):
                guard.check_sections(
                    (checkpoint / "HANDOFF.md").read_text(encoding="utf-8"), HANDOFF_HEADINGS
                )
                guard.check_next((checkpoint / "NEXT.md").read_text(encoding="utf-8"))

    def test_actual_retrospectives_keep_exact_sections_and_every_recorded_lesson_guard(self):
        guard = continuation_contract.Gate7ContinuationContractTests()
        for checkpoint in self.current_checkpoints():
            with self.subTest(checkpoint=checkpoint.name):
                path = ROOT / ".iacode/memory/retrospectives" / (checkpoint.name + ".md")
                guard.check_retrospective(
                    path.read_text(encoding="utf-8"), self.lessons(checkpoint)
                )

    def test_actual_failed_original_is_exact_inert_and_rejected_by_identical_contract(self):
        receipt_path = CORRECTION / "continuation-attempts/run-0001/RECEIPT.json"
        receipt = json.loads(receipt_path.read_bytes())
        raw = (receipt_path.parent / receipt["original"]).read_bytes()
        self.assertEqual(receipt["bytes"], len(raw))
        self.assertEqual(receipt["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual("FAIL", receipt["result"])
        guard = continuation_contract.Gate7ContinuationContractTests()
        with self.assertRaises(AssertionError):
            guard.check_retrospective(raw.decode("utf-8"), self.lessons(CORRECTION))

    def test_current_positive_and_omission_empty_extra_order_and_lesson_growth_controls(self):
        guard = continuation_contract.Gate7ContinuationContractTests()
        path = ROOT / ".iacode/memory/retrospectives/GATE-7-CP-0003.md"
        text = path.read_text(encoding="utf-8")
        lessons = self.lessons(CORRECTION)
        self.assertTrue(lessons)
        guard.check_retrospective(text, lessons)
        headings = guard.retrospective_headings()
        for heading in headings:
            with self.subTest(missing=heading), self.assertRaises(AssertionError):
                guard.check_retrospective(text.replace(heading, "", 1), lessons)
        with self.assertRaises(AssertionError):
            guard.check_retrospective(text + "\n## EXTRA\n\nForbidden section.\n", lessons)
        with self.assertRaises(AssertionError):
            guard.check_sections(text, [headings[1], headings[0], *headings[2:]])
        empty = "# Retrospective\n\n" + "\n\n".join(headings)
        with self.assertRaises(AssertionError):
            guard.check_retrospective(empty, lessons)
        grown = [*lessons, {"lessonId": "LSN-9999", "guardrails": ["GRD-9999"]}]
        with self.assertRaises(AssertionError):
            guard.check_retrospective(text, grown)
        guard.check_retrospective(text + "\nLSN-9999 GRD-9999\n", grown)
        for lesson in lessons:
            for identifier in [lesson["lessonId"], *lesson["guardrails"]]:
                with self.subTest(omitted=identifier), self.assertRaises(AssertionError):
                    guard.check_retrospective(text.replace(identifier, ""), lessons)


if __name__ == "__main__":
    unittest.main()
