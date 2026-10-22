"""Escalate the actual current-document contract failure before repairing documents."""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts/development-ledger"))
from ledger_common import load_json, write_json
from lesson_preflight import render_markdown
from lessons import (
    build_preflight,
    load_lessons,
    register_recurrence,
    render_index,
    save_lessons,
)

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    receipt_path = CHECKPOINT / "continuation-attempts/run-0001/RECEIPT.json"
    receipt = load_json(receipt_path)
    document = ROOT / receipt["source"]
    original = receipt_path.parent / receipt["original"]
    if (
        receipt["result"] != "FAIL"
        or receipt["checks"]
        != [
            {"document": "handoff", "result": "PASS"},
            {"document": "next", "result": "PASS"},
            {"document": "retrospective", "result": "FAIL"},
        ]
        or document.read_bytes() != original.read_bytes()
        or hashlib.sha256(original.read_bytes()).hexdigest() != receipt["sha256"]
        or load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS"
    ):
        raise ValueError("Require the actual unchanged failed document and valid nulls")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    identifier = "CONTINUATION-001"
    if any(item["id"] == identifier for item in rework["items"]):
        raise ValueError("Do not duplicate the actual recurrence")
    lessons = load_lessons(ROOT)
    index = next(i for i, row in enumerate(lessons) if row["lessonId"] == "LSN-0140")
    if lessons[index]["status"] != "GUARDED":
        raise ValueError("Expected the existing guarded continuation contract")
    revised = register_recurrence(
        lessons[index],
        CHECKPOINT.name,
        "CONTINUATION-001: the unchanged existing structural assertion rejects the actual "
        "CP0003 retrospective's extra Current correction epoch heading. Actual HANDOFF and "
        "NEXT pass as valid nulls. Existing automatic current-document tests name CP0001, "
        "so the newer corrective checkpoint escaped their scope. Preserve the exact original, "
        "retain every template and inherited assertion, and extend actual corrective coverage.",
    )
    revised["evidence"].append("file:" + receipt_path.relative_to(ROOT).as_posix())
    revised["resolution"] = (
        "CP0003 CONTINUATION-001 remains open; current documents and coverage need repair. "
        + revised["resolution"]
    )
    lessons[index] = revised
    rework["items"].append(
        {
            "id": identifier,
            "status": "OPEN",
            "classification": "GUARDRAIL_FAILURE LSN-0140",
            "observed": "Actual CP0003 retrospective fails the unchanged canonical headings.",
            "evidence": receipt_path.relative_to(CHECKPOINT).as_posix(),
            "commands": ["cmd-0305"],
            "requiredCorrection": (
                "Keep the failed original; retain canonical sections and every current changed "
                "lesson/guard identity. Extend inherited controls to this corrective checkpoint "
                "with valid nulls and omission/extra/order/growth adversaries; require current "
                "lint, helper quality and quiescent checkpoint validation before local restoration."
            ),
        }
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    prior = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(
        ROOT, prior["gate"], prior["scope"], prior["technologies"], prior["modules"]
    )
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(
        render_markdown(preflight), encoding="utf-8", newline="\n"
    )
    print("CONTINUATION-001 recorded; LSN-0140 reopened before document corrections")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
