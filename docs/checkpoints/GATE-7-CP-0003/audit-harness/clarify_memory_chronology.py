"""Distinguish earlier open local restoration from current demonstrated guard status."""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import utc_now
from lessons import load_lessons, render_index, save_lessons

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    old = (
        "M2 CP0003 adds actual child-producer and literal replay regr"
        "essions; the independent guarded recurrence remains unresolv"
        "ed until complete corrective acceptance."
    )
    new = (
        "Earlier CP0003 child-producer/replay proof preceded the nati"
        "ve and caller extension. Current local guard restoration is "
        "recorded below; final finding closure, complete immutable de"
        "livery acceptance and the later independent audit are still "
        "distinct pending obligations."
    )
    lessons = load_lessons(ROOT)
    changed = []
    for lesson in lessons:
        if lesson["lessonId"] in {"LSN-0010", "LSN-0135"}:
            if old not in lesson["notes"]:
                raise ValueError("Expected exact chronology qualifier absent")
            lesson["notes"] = lesson["notes"].replace(old, new)
            lesson["updatedAt"] = utc_now()
            changed.append(lesson["lessonId"])
    if len(changed) != 2:
        raise ValueError("Expected exactly two clarified local chronology notes")
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    print(
        "Clarified current local status versus earlier chronology; no"
        " counter, rights or historical failure removed"
    )
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
