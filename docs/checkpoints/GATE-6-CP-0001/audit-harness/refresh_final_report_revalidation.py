"""Refresh unchanged full lesson applicability and serialize canonical rework bookkeeping."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger_common import load_json, use_utf8_stdout
from validate_serial_bookkeeping import run_sequence


def main() -> int:
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    state = load_json(CHECKPOINT / "STATE.json")
    if preflight["gate"] != "GATE-6" or preflight["scope"] != state["lessonPreflight"]["scope"]:
        raise ValueError("the complete original applicability must remain unchanged")
    arguments = ["scripts/development-ledger/lesson_preflight.py", "--gate", preflight["gate"],
                 "--scope", preflight["scope"]]
    for option, values in (("--technology", preflight["technologies"]), ("--module", preflight["modules"])):
        for value in values:
            arguments.extend([option, value])
    recorder = str(ROOT / "scripts/development-ledger/record_command.py")
    harness = CHECKPOINT.relative_to(ROOT).as_posix() + "/audit-harness/"
    steps = [
        ("Refresh every original lesson selector after observed canonical report recurrence without exclusions", [*arguments, "--write"]),
        ("Derive the complete canonical lesson and finding set after explicit local guard restoration", ["scripts/development-ledger/derive_requirements.py", "--write"]),
        ("Invalidate stale v6 acceptance and bind actual local final report repair without granting a Gate verdict", [harness + "prepare_final_report_revalidation.py"]),
        ("Derive actual canonical counts from current evidence before inventory", ["scripts/development-ledger/derive_counts.py", "--write"]),
        ("Explicitly declare every current Gate6 path before hash binding", [harness + "declare_inventory.py"]),
        ("Validate actual quiescent complete rework metadata after all writers finish", [harness + "run_checkpoint_validation.py"]),
    ]
    return run_sequence([[sys.executable, recorder, "--purpose", purpose, "--", "python", *command]
                         for purpose, command in steps], ROOT)


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
