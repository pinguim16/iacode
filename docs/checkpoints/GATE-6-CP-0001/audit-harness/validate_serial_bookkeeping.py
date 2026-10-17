"""Finish inventory and its recorder before starting validation; no other writer may overlap."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import use_utf8_stdout


def bookkeeping_commands() -> list[list[str]]:
    recorder = str(ROOT / "scripts/development-ledger/record_command.py")
    harness = CHECKPOINT.relative_to(ROOT).as_posix() + "/audit-harness/"
    return [
        [sys.executable, recorder, "--purpose", "Complete explicit inventory and its command record before validation",
         "--", "python", harness + "declare_inventory.py"],
        [sys.executable, recorder, "--purpose", "Validate quiescent current checkpoint after the inventory recorder has actually exited",
         "--", "python", harness + "run_checkpoint_validation.py"],
    ]


def run_sequence(commands: list[list[str]], cwd: Path) -> int:
    for index, arguments in enumerate(commands, 1):
        completed = subprocess.run(arguments, cwd=cwd, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", check=False)
        sys.stdout.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        print(f"BOOKKEEPING_PHASE_COMPLETED index={index} exit={completed.returncode}", flush=True)
        if completed.returncode:
            return completed.returncode
    return 0


def main() -> int:
    if len(sys.argv) != 1:
        raise ValueError("the complete serial bookkeeping sequence has no narrowing arguments")
    return run_sequence(bookkeeping_commands(), ROOT)


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
