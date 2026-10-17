"""Register executed sequencing prevention while keeping the recurrence open until real validation."""

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import use_utf8_stdout, write_json
from lessons import load_lessons, save_lessons


def main() -> int:
    records = {row["id"]: row for row in (json.loads(line) for line in
               (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
               if line.strip())}
    if records.get("cmd-0322", {}).get("exitCode") != 0:
        raise ValueError("actual positive/adverse sequencing control required")
    controls = [
        "test_bookkeeping_sequence_awaits_each_recorder_and_keeps_canonical_order",
        "test_bookkeeping_sequence_never_validates_after_inventory_recorder_failure",
    ]
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0011")
    if lesson["status"] != "CONFIRMED":
        raise ValueError("the actual serial main-tree validation has not restored this lesson yet")
    for control in controls:
        if not any(row["reference"] == control for row in lesson["prevention"]):
            lesson["prevention"].append({
                "kind": "test", "reference": control,
                "description": "The actual synchronous sequencer waits for complete recorder exit and never starts validation after a failed inventory recorder.",
            })
    lesson["evidence"] = list(dict.fromkeys(lesson["evidence"] + [
        "file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl",
        "file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json",
        "file:docs/checkpoints/GATE-5-CP-0001/audit-harness/validate_serial_bookkeeping.py",
        "file:tests/test_gate5_clients.py",
    ]))
    lesson["notes"] = (
        "Historical thirteen recurrences and their resolved evidence remain unchanged. "
        "G5-INT-034 is recurrence14: cmd-0317 refused six metadata hashes because the inventory "
        "recorder cmd-0316 was still active. Cmd-0322 proves actual child completion ordering and "
        "first-phase failure stops the new synchronous sequencer. Status remains CONFIRMED until "
        "the actual main-tree serial validation passes. The sequencer covers its own two phases; "
        "all unrelated metadata producers must still finish first. No global writer lock is claimed."
    )
    save_lessons(ROOT, lessons)
    registry = json.loads((ROOT / ".iacode/memory/guardrails/registry.json").read_text(encoding="utf-8"))
    guard = next(row for row in registry["guardrails"] if row["guardrailId"] == "GRD-0006")
    for control in controls:
        if control not in guard["verifiedBy"]:
            guard["verifiedBy"].append(control)
    write_json(ROOT / ".iacode/memory/guardrails/registry.json", registry)
    print("BOOKKEEPING_GUARD_REGISTERED recurrenceStillOpen=true actualMainTreeAcceptance=PENDING")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
