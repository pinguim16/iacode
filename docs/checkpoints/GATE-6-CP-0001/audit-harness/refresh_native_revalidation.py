"""Refresh complete existing applicability and serialize every rework metadata writer."""

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
        raise ValueError("the full existing Gate6 applicability must remain unchanged")
    arguments = ["scripts/development-ledger/lesson_preflight.py", "--gate", preflight["gate"],
                 "--scope", preflight["scope"]]
    for option, values in (("--technology", preflight["technologies"]), ("--module", preflight["modules"])):
        for value in values:
            arguments.extend([option, value])
    recorder = str(ROOT / "scripts/development-ledger/record_command.py")
    harness = CHECKPOINT.relative_to(ROOT).as_posix() + "/audit-harness/"
    steps = [
        ("Refresh every existing lesson selector after native guard restoration without exclusions", [*arguments, "--write"]),
        ("Derive the complete canonical lesson and open-finding requirement set after causal rework", ["scripts/development-ledger/derive_requirements.py", "--write"]),
        ("Bind actual local native correction and historical archives without granting current whole acceptance", [harness + "prepare_native_revalidation.py"]),
        ("Derive actual current distinct counters before inventory and validation", ["scripts/development-ledger/derive_counts.py", "--write"]),
        ("Explicitly declare every current Gate6 path before any hash binding", [harness + "declare_inventory.py"]),
        ("Validate quiescent current rework state after all metadata writers actually finish", [harness + "run_checkpoint_validation.py"]),
    ]
    return run_sequence([[sys.executable, recorder, "--purpose", purpose, "--", "python", *command]
                         for purpose, command in steps], ROOT)


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
