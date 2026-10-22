"""Register the two authorized audit recurrences, once, without asserting repair."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts/development-ledger"))

from lessons import load_lessons, register_recurrence, save_lessons

ROOT = Path(__file__).resolve().parents[4]


def main() -> int:
    checkpoint = Path(__file__).resolve().parents[1].name
    findings = {"LSN-0010": "M2-F-001", "LSN-0135": "M2-F-002"}
    rows = load_lessons(ROOT)
    changed = []
    for index, lesson in enumerate(rows):
        identifier = lesson["lessonId"]
        if identifier not in findings:
            continue
        if any(
            item.get("checkpoint") == checkpoint for item in lesson.get("guardrailFailures", [])
        ):
            continue
        rows[index] = register_recurrence(
            lesson,
            checkpoint,
            findings[identifier] + ": independent audit found an escaped guarded failure; "
            "causal corrective verification remains pending.",
        )
        changed.append(identifier)
    save_lessons(ROOT, rows)
    print("Registered guarded recurrences: " + ", ".join(changed))
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
