"""Record the observed authored-source quality recurrence before repairing it."""

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
    receipt_path = CHECKPOINT / "quality-attempts/helper-quality/run-0001/RECEIPT.json"
    receipt = load_json(receipt_path)
    execution = receipt["executions"][0]
    if (
        receipt["result"] != "FAIL"
        or receipt["sourceUnchanged"] is not True
        or execution["producer"]["exitCode"] != 1
        or execution["cleanup"]["result"] != "PASS"
    ):
        raise ValueError("Require the actual read-only failed authored-source observation")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    identifier = "AUTHORED-STYLE-001"
    if any(item["id"] == identifier for item in rework["items"]):
        raise ValueError("Do not duplicate a recorded recurrence")
    lessons = load_lessons(ROOT)
    index = next(i for i, row in enumerate(lessons) if row["lessonId"] == "LSN-0105")
    if lessons[index]["status"] != "GUARDED":
        raise ValueError("Expected the existing guarded authored-source quality contract")
    evidence = "file:" + receipt_path.relative_to(ROOT).as_posix()
    revised = register_recurrence(
        lessons[index],
        CHECKPOINT.name,
        "AUTHORED-STYLE-001: unchanged pinned Ruff rules found734 errors across84 "
        "derived current helper/test/runtime paths. Canonical lint passed but does not "
        "cover these checkpoint helpers and root regressions. Preserve that narrower "
        "success and the failed additional observation; repair source, not rules or tests.",
    )
    revised["evidence"].append(evidence)
    revised["resolution"] = (
        "CP0003 AUTHORED-STYLE-001 is open; no current guarded acceptance. " + revised["resolution"]
    )
    lessons[index] = revised
    rework["items"].append(
        {
            "id": identifier,
            "status": "OPEN",
            "classification": "GUARDRAIL_FAILURE LSN-0105",
            "observed": "734 unchanged-rule Ruff errors in84 derived active authored paths.",
            "evidence": receipt_path.relative_to(CHECKPOINT).as_posix(),
            "commands": ["cmd-0275"],
            "requiredCorrection": (
                "Repair all derived source paths with unchanged rules/assertions; preserve "
                "raw preimages and sealed subjects. Recheck behavior and full current lint "
                "before publication. Prior lint run0009 is not current after source changes."
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
    quality = load_json(CHECKPOINT / "QUALITY.json")
    for key in ("lint", "staticAnalysis", "checkpointValidation"):
        quality["checks"][key].update(
            status="NOT_EXECUTED",
            evidence=[],
            justification="Authored-source recurrence changes the assurance source epoch.",
        )
    write_json(CHECKPOINT / "QUALITY.json", quality)
    active = load_json(CHECKPOINT / "ACTIVE-VALIDATION.json")
    active.update(status="IDLE", sessionId=None)
    write_json(CHECKPOINT / "ACTIVE-VALIDATION.json", active)
    print("AUTHORED-STYLE-001 recorded; LSN-0105 reopened; unchanged rules required")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
