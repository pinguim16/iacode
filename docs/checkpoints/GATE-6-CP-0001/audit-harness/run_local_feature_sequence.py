"""Finish each actual local feature phase before starting another; no assurance narrowing."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import use_utf8_stdout


def main() -> int:
    if len(sys.argv) != 1:
        raise ValueError("the complete local sequence has no phase-selection arguments")
    harness = CHECKPOINT.relative_to(ROOT).as_posix() + "/audit-harness/"
    phases = (
        ("mechanical-format", [harness + "format_new_python.py"]),
        ("owning-image-schema", ["scripts/iacode/experience_schema.py", "--write"]),
        ("complete-domain-api-unit", [harness + "run_experience_checks.py"]),
        ("complete-experience-migration-integration", [harness + "run_owned_experience_integration.py"]),
        ("mandatory-experience-gate", ["scripts/iacode/gates/experience_tests.py"]),
    )
    for name, arguments in phases:
        print("LOCAL_FEATURE_PHASE_STARTED " + name, flush=True)
        result = subprocess.run([sys.executable, *arguments], cwd=ROOT, text=True,
                                encoding="utf-8", errors="replace", check=False)
        print(f"LOCAL_FEATURE_PHASE_FINISHED {name} exit={result.returncode}", flush=True)
        if result.returncode:
            return result.returncode
    print("LOCAL_FEATURE_SEQUENCE=PASS; live acceptance/full internal assurance remain pending")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
