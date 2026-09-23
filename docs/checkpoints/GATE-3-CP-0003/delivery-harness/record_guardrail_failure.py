#!/usr/bin/env python3
"""Record M1-F-003 as a recurrence of LSN-0040 against its guardrail GRD-0042.

`LSN-0040` exists for one class: a sealed checkpoint that does not validate from its own tag, and a
control over sealed history that could not see it. `GRD-0042` —
`test_every_sealed_checkpoint_validates_from_its_own_tag` — is the guardrail. `M1-F-003` is the same
class again: `GATE-1-CP-0001` validates from its tag in this repository and not from the published
history, and the guardrail stayed green because it cloned the local path, which carries objects no
published reference reaches. A repeat against a `GUARDED` lesson is a `GUARDRAIL_FAILURE`, so this
uses the memory's own `register_recurrence`: the count goes up, the failure is recorded, the
severity is escalated and the lesson returns to `CONFIRMED` until the repaired control is named.

    python record_guardrail_failure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from lessons import load_lessons, register_recurrence, save_lessons  # noqa: E402

LESSON = "LSN-0040"
DETAIL = (
    "M1-F-003 (GATE-3-CP-0002): GATE-1-CP-0001 validates from its own tag in the working "
    "repository and not from the published history, because its sealed record cmd-0086 names "
    "commit b59d66f9f3f9, a replaced closure commit no published reference reaches. GRD-0042 "
    "stayed green because test_every_sealed_checkpoint_validates_from_its_own_tag cloned the local "
    "path with --no-hardlinks, which copies unreachable objects; MIR-016 cloned the same way. The "
    "control could not tell a local object from a published one.")


def main() -> int:
    lessons = load_lessons(ROOT)
    index = next(i for i, item in enumerate(lessons) if item.get("lessonId") == LESSON)
    before = lessons[index]
    if any("M1-F-003" in str(item.get("detail")) for item in before.get("guardrailFailures") or []):
        print(f"{LESSON} already records M1-F-003; nothing to do")
        return 0
    lessons[index] = register_recurrence(before, "GATE-3-CP-0002", DETAIL)
    save_lessons(ROOT, lessons)
    after = lessons[index]
    print(f"{LESSON}: status {before['status']} -> {after['status']}, severity "
          f"{before['severity']} -> {after['severity']}, recurrenceCount "
          f"{before['recurrenceCount']} -> {after['recurrenceCount']}, guardrail failures "
          f"{len(after['guardrailFailures'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
