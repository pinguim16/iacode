"""Current canonical continuation controls; synthetic strings are structural unit fixtures only."""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "docs/checkpoints/GATE-7-CP-0001"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
validator = importlib.import_module("validate_checkpoint")


class Gate7ContinuationContractTests(unittest.TestCase):
    def current_lessons(self):
        rows = [
            json.loads(line)
            for line in (ROOT / ".iacode/memory/lessons.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        selected = [row for row in rows if row["source"]["checkpoint"] == CHECKPOINT.name]
        self.assertTrue(selected)
        return selected

    def retrospective_headings(self):
        template = (ROOT / ".iacode/templates/retrospective/TEMPLATE.md").read_text(
            encoding="utf-8"
        )
        headings = re.findall(r"^## .+$", template, flags=re.MULTILINE)
        self.assertTrue(headings)
        return headings

    def check_sections(self, text, expected):
        headings = list(re.finditer(r"^## .+$", text, flags=re.MULTILINE))
        self.assertEqual([row.group() for row in headings], list(expected))
        for index, heading in enumerate(headings):
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            self.assertGreaterEqual(len(text[heading.end() : end].strip()), 20, heading.group())

    def check_next(self, text):
        self.assertTrue(text.startswith("# Next\n"))
        headings = re.findall(r"^## .+$", text, flags=re.MULTILINE)
        self.assertEqual(len(headings), 1)
        self.assertIn(headings[0], ("## Required next action", "## Next Gate"))
        self.assertGreaterEqual(len(text.split(headings[0], 1)[1].strip()), 40)

    def check_retrospective(self, text, lessons):
        self.check_sections(text, self.retrospective_headings())
        for lesson in lessons:
            self.assertIn(lesson["lessonId"], text)
            for guard in lesson["guardrails"]:
                self.assertIn(guard, text)

    def test_actual_current_handoff_and_next_preserve_canonical_structure(self):
        self.check_sections(
            (CHECKPOINT / "HANDOFF.md").read_text(encoding="utf-8"), validator.HANDOFF_HEADINGS
        )
        self.check_next((CHECKPOINT / "NEXT.md").read_text(encoding="utf-8"))

    def test_actual_retrospective_uses_exact_template_and_every_current_lesson_guard(self):
        document = ROOT / ".iacode/memory/retrospectives/GATE-7-CP-0001.md"
        self.check_retrospective(document.read_text(encoding="utf-8"), self.current_lessons())

    def test_actual_renderer_and_each_missing_empty_extra_or_reordered_section_refusal(self):
        path = CHECKPOINT / "audit-harness/assemble_final_handoff.py"
        spec = importlib.util.spec_from_file_location("g7_canonical_renderer_control", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sections = {
            heading: "Substantive structural unit fixture for " + heading
            for heading in validator.HANDOFF_HEADINGS
        }
        rendered = module.render_handoff(sections)
        self.check_sections(rendered, validator.HANDOFF_HEADINGS)
        for heading in sections:
            for mutation in ("missing", "empty"):
                changed = dict(sections)
                if mutation == "missing":
                    del changed[heading]
                else:
                    changed[heading] = " "
                with self.assertRaises(ValueError):
                    module.render_handoff(changed)
        with self.assertRaises(ValueError):
            module.render_handoff({**sections, "## Invented": "Not a canonical section"})
        wrong = rendered.replace("## Objective", "## EXTRA", 1)
        with self.assertRaises(AssertionError):
            self.check_sections(wrong, validator.HANDOFF_HEADINGS)
        rows = list(validator.HANDOFF_HEADINGS)
        with self.assertRaises(AssertionError):
            self.check_sections(rendered, [rows[1], rows[0], *rows[2:]])
        self.check_next("# Next\n\n## Required next action\n\n" + "Substantive unit action. " * 3)
        for text in (
            "# Next\n\nUnstructured action without the required heading.",
            "# Next\n\n## Required next action\n\n",
        ):
            with self.assertRaises(AssertionError):
                self.check_next(text)

    def test_retrospective_positive_omission_extra_and_registered_lesson_growth(self):
        lessons = self.current_lessons()
        headings = self.retrospective_headings()
        text = "# Retrospective\n\n" + "\n\n".join(
            heading + "\n\nSubstantive structural unit fixture, not a delivery verdict."
            for heading in headings
        )
        for row in lessons:
            text += "\n" + row["lessonId"] + " " + " ".join(row["guardrails"])
        self.check_retrospective(text, lessons)
        for heading in headings:
            with self.assertRaises(AssertionError):
                self.check_retrospective(text.replace(heading, "", 1), lessons)
        with self.assertRaises(AssertionError):
            self.check_retrospective(text + "\n\n## Invented epoch\n\nExtra content.", lessons)
        for row in lessons:
            for value in [row["lessonId"], *row["guardrails"]]:
                with self.assertRaises(AssertionError):
                    self.check_retrospective(text.replace(value, ""), lessons)
        growth = [*lessons, {"lessonId": "LSN-9999", "guardrails": ["GRD-9999"]}]
        with self.assertRaises(AssertionError):
            self.check_retrospective(text, growth)
        self.check_retrospective(text + "\nLSN-9999 GRD-9999", growth)

    def test_original_failed_documents_remain_exact_inert_and_rejected(self):
        manifest = json.loads(
            (CHECKPOINT / "attempts/CONTINUATION-REFUSAL-0001-MANIFEST.json").read_bytes()
        )
        self.assertFalse(manifest["originalConsoleBytesRetained"])
        self.assertFalse(manifest["gateVerdictIssued"])
        self.assertEqual(len(manifest["files"]), 3)
        for row in manifest["files"]:
            raw = (CHECKPOINT / row["archive"]).read_bytes()
            self.assertEqual(len(raw), row["bytes"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
            text = raw.decode("utf-8").replace("\r\n", "\n")
            with self.assertRaises(AssertionError):
                if row["original"].endswith("/HANDOFF.md"):
                    self.check_sections(text, validator.HANDOFF_HEADINGS)
                elif row["original"].endswith("/NEXT.md"):
                    self.check_next(text)
                else:
                    self.check_retrospective(text, self.current_lessons())


if __name__ == "__main__":
    unittest.main()
