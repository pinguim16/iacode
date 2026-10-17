"""Synchronize incomplete rework counters without completing a step or resolving a finding."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from delivery_assurance import evaluate_matrix
from ledger_common import load_json, use_utf8_stdout, write_json
from lessons import guardrail_effectiveness
from sync_in_progress_metadata import synchronize


def main() -> int:
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS":
        raise ValueError("only incomplete implementing state may be synchronized")
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    report = evaluate_matrix(ROOT, CHECKPOINT, matrix)
    state["requirementsMatrix"].update({"total": report["totalRequirements"],
        "mandatory": report["mandatoryRequirements"], "complete": report["complete"],
        "partial": report["partial"], "missing": report["missing"],
        "notApplicable": report["notApplicable"], "coveragePercent": report["coveragePercent"]})
    measured = guardrail_effectiveness(ROOT)
    state["guardrailEffectiveness"] = {key: measured[key] for key in (
        "guardrailsTotal", "guardrailsResolved", "guardrailsTested", "guardrailsEffective", "guardrailFailures")}
    state["guardrailEffectiveness"]["evidence"] = ["checkpoint:FINDINGS.json", "command:cmd-0056"]
    write_json(CHECKPOINT / "STATE.json", state)
    synchronize(ROOT, CHECKPOINT)
    print("INCOMPLETE_REWORK_SYNCHRONIZED; no finding, step or Gate promoted")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
