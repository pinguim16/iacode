"""Escalate actual unchanged lint refusal; no source rule or assertion is relaxed."""

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import load_json, use_utf8_stdout, write_json
from lessons import load_lessons, register_recurrence, save_lessons


def main() -> int:
    commands = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    actual = next(row for row in commands if row["id"] == "cmd-0031")
    if actual["exitCode"] != 1:
        raise ValueError("actual original lint refusal is required")
    detail = ("G6-INT-005: Cmd-0031 reports seven E501 declarations after mechanical formatting; "
              "the formatter does not split every long literal. Preserve all unchanged lint rules, "
              "split only source expressions/strings and require the entire mandatory lint green.")
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    if not any(row["findingId"] == "G6-INT-005" for row in findings["findings"]):
        findings["findings"].append({"findingId": "G6-INT-005", "severity": "CRITICAL",
            "title": "GUARDRAIL_FAILURE: source formatting budget",
            "status": "OPEN", "expected": "The complete unchanged mandatory lint is green.",
            "observed": "Cmd-0031: seven E501 findings; both frontend/client formatting checks pass; overall exit 1.",
            "rootCause": detail, "evidence": ["command:cmd-0031"]})
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    lessons = load_lessons(ROOT)
    for index, lesson in enumerate(lessons):
        if lesson["lessonId"] == "LSN-0105" and not any("G6-INT-005" in row["detail"]
                for row in lesson.get("guardrailFailures", [])):
            lessons[index] = register_recurrence(lesson, CHECKPOINT.name, detail)
    save_lessons(ROOT, lessons)
    print("G6-INT-005 GUARDRAIL_FAILURE RECORDED; correction acceptance pending")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
