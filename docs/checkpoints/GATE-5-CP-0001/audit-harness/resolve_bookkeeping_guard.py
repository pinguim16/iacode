"""Restore the unfinished-producer guard only after actual serial main-tree validation."""

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import utc_now, use_utf8_stdout
from lessons import load_lessons, save_lessons


def main() -> int:
    records = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    indices = {row["id"]: index for index, row in enumerate(records)}
    required = {
        "cmd-0322": "unittest",
        "cmd-0328": "audit-harness/declare_inventory.py",
        "cmd-0329": "audit-harness/run_checkpoint_validation.py",
        "cmd-0330": "audit-harness/validate_serial_bookkeeping.py",
    }
    for identifier, command in required.items():
        row = records[indices[identifier]]
        if row.get("exitCode") != 0 or command not in row["command"]:
            raise ValueError("actual recorded causal acceptance is missing: " + identifier)
    if not indices["cmd-0328"] < indices["cmd-0329"] < indices["cmd-0330"]:
        raise ValueError("the actual recorded sequence order is wrong")
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0011")
    failure = next(row for row in lesson["guardrailFailures"] if "G5-INT-034" in row["detail"])
    if lesson["recurrenceCount"] != 14:
        raise ValueError("the complete observed recurrence history must remain intact")
    failure["resolvedIn"] = CHECKPOINT.name
    lesson["status"] = "GUARDED"
    lesson["updatedAt"] = utc_now()
    lesson["notes"] = (
        "All fourteen recurrences, original refused commands and escalated severity remain. "
        "Cmd-0317 remains FAIL with six strict hash refusals after unfinished recorder cmd-0316. "
        "Cmd-0322 executes real synchronous positive/adverse process controls. The actual fixed "
        "sequence cmd-0330 waits for inventory recorder cmd-0328 and then canonical main-tree "
        "validation cmd-0329 returns CHECKPOINT_VALID. This restores causal prevention, not Gate "
        "readiness. The sequencer owns its two phases only; unrelated producers must finish first. "
        "Refresh all derived metadata after this memory transition and rerun the single serial "
        "sequence before publication. Full immutable v3 and ordered internal assurance remain due."
    )
    save_lessons(ROOT, lessons)
    print("BOOKKEEPING_GUARD_RESTORED actualSerialValidation=cmd-0329 recurrences=14 fullGate=PENDING")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
