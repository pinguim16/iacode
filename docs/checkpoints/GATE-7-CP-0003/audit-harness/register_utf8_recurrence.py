"""Escalate the actual unchanged UTF-8 guard failure before repairing entry blocks."""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import load_json, write_json
from lessons import load_lessons, register_recurrence, render_index, save_lessons

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    report = load_json(CHECKPOINT / "quality-attempts/tests/run-0001.json")
    if report["exitCode"] != 1 or not report["sourceUnchanged"]:
        raise ValueError("The actual unchanged red suite is required")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    if any(item["id"] == "ROOT-UTF8-001" for item in rework["items"]):
        raise ValueError("Do not duplicate the current recurrence")
    rework["items"].append(
        {
            "id": "ROOT-UTF8-001",
            "status": "OPEN",
            "observed": (
                "The unchanged complete Root1018 scan finds six current captu"
                "ring entrypoints without their own UTF-8 stream bootstrap. E"
                "xisting guards correctly remain red."
            ),
            "evidence": "quality-attempts/tests/run-0001.stderr.log",
            "requiredCorrection": (
                "Configure actual current entry blocks through the existing b"
                "ootstrap, add cold positive/adverse startup proof and retain"
                " the unchanged whole-tree guards."
            ),
            "classification": (
                "GUARDRAIL_FAILURE LSN-0035 and LSN-0083; no maximum-severity"
                " reset or test weakening"
            ),
        }
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    lessons = load_lessons(ROOT)
    for index, lesson in enumerate(lessons):
        if lesson["lessonId"] not in {"LSN-0035", "LSN-0083"}:
            continue
        if any(row["checkpoint"] == CHECKPOINT.name for row in lesson.get("guardrailFailures", [])):
            raise ValueError("Current guarded recurrence already exists")
        revised = register_recurrence(
            lesson,
            CHECKPOINT.name,
            (
                "ROOT-UTF8-001: complete Root1018 retains six unconfigured cu"
                "rrent capture entrypoints; configure actual entry blocks and"
                " prove cold bootstrap without rerunning destructive main bod"
                "ies."
            ),
        )
        revised["resolution"] = "CP0003 recurrence remains open. " + revised["resolution"]
        for name in ("INTERNAL-ENVIRONMENT-REWORK.json", "quality-attempts/tests/run-0001.json"):
            revised["evidence"].append("file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix())
        lessons[index] = revised
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    print("Two UTF-8 guard failures escalated; statuses CONFIRMED, no effectiveness claim")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
