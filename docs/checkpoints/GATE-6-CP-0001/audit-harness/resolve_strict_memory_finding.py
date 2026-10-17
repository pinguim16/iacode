"""Close the retained strict-content recurrence only after real unchanged scan/checkpoint proof."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, use_utf8_stdout, write_json
from lessons import load_lessons, save_lessons


def main() -> int:
    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise ValueError("only the current unsealed implementing checkpoint may be updated")
    commands = {row["id"]: row for row in (json.loads(line) for line in
        (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
    for identifier in ("cmd-0058", "cmd-0062", "cmd-0066", "cmd-0067"):
        if commands[identifier]["exitCode"] != 0:
            raise ValueError("actual completed strict-content/checkpoint acceptance missing")
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0119")
    failures = [row for row in lesson["guardrailFailures"] if row["checkpoint"] == CHECKPOINT.name
                and "G6-INT-008" in row["detail"]]
    if not failures:
        raise ValueError("the original escalated recurrence must remain recorded")
    for failure in failures:
        failure["resolvedIn"] = CHECKPOINT.name
    lesson["status"] = "GUARDED"
    lesson["updatedAt"] = utc_now()
    lesson["evidence"] = list(dict.fromkeys(lesson["evidence"] + [
        "file:docs/checkpoints/GATE-6-CP-0001/STRICT-MEMORY-FINDING.json",
        "file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json",
        "file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl"]))
    lesson["notes"] = ("Retain every original/escalated recurrence and its severity/counter. "
        "Cmd-0056 retains the actual memory-title refusal; cmd-0059 retains nine strict-delta "
        "refusals on descriptive labels/derived copies. Only labels were reworded and canonical "
        "derivations regenerated. Unchanged memory validation cmd-0058, full actual-delta strict "
        "scan cmd-0062 and quiescent current CHECKPOINT_VALID cmd-0066/0067 actually pass. "
        "Neither scanner, exception list, runtime secret type nor detection assertion was changed. "
        "This restores the causal guard, not immutable full-Gate or independent M2 approval.")
    save_lessons(ROOT, lessons)
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    finding = next(row for row in findings["findings"] if row["findingId"] == "G6-INT-008")
    finding["status"] = "CLOSED"
    finding["resolutionEvidence"] = ["command:cmd-0058", "command:cmd-0062", "command:cmd-0066", "command:cmd-0067"]
    finding["resolution"] = "Only descriptive labels and their canonical derived copies changed. Both unchanged strict boundaries and actual serialized checkpoint acceptance pass; original red observations and recurrence severity/counter remain."
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    print("G6-INT-008 CLOSED; causal strict-content guard restored; immutable assurance remains pending")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
