#!/usr/bin/env python3
"""Copy into STATE.json the blocks that are derived from other artifacts, never typed by hand.

The preflight counts come from LESSON-PREFLIGHT.json, the requirement counts from the matrix as the
completeness audit evaluates it, the anchor count from the integrity chain and the guardrail
measurement from the memory. Validation recomputes every one of them, so this only saves the run
from transcribing a number the tooling already owns.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from anchors import load_anchors  # noqa: E402
from delivery_assurance import evaluate_matrix, load_matrix  # noqa: E402
from ledger_common import load_json, write_json  # noqa: E402
from lessons import guardrail_effectiveness  # noqa: E402


def main() -> int:
    state = load_json(CHECKPOINT / "STATE.json")

    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    block = state["lessonPreflight"]
    block.update({
        "path": "LESSON-PREFLIGHT.json",
        "gate": preflight["gate"],
        "scope": preflight["scope"],
        "lessonsConsidered": preflight["lessonsConsidered"],
        "lessonsApplicable": preflight["lessonsApplicable"],
        "derivedRequirements": len(preflight.get("derivedRequirements") or []),
    })
    if not block.get("evidence"):
        block["evidence"] = ["checkpoint:LESSON-PREFLIGHT.json"]

    report = evaluate_matrix(ROOT, CHECKPOINT, load_matrix(CHECKPOINT))
    state["requirementsMatrix"].update({
        "path": "REQUIREMENTS-MATRIX.json",
        "total": report["totalRequirements"],
        "mandatory": report["mandatoryRequirements"],
        "complete": report["complete"],
        "partial": report["partial"],
        "missing": report["missing"],
        "notApplicable": report["notApplicable"],
        "coveragePercent": report["coveragePercent"],
    })

    state["integrity"]["anchors"] = len(load_anchors(ROOT))

    measured = guardrail_effectiveness(ROOT)
    for key in ("guardrailsTotal", "guardrailsResolved", "guardrailsTested",
                "guardrailsEffective", "guardrailFailures"):
        state["guardrailEffectiveness"][key] = measured[key]
    if not state["guardrailEffectiveness"].get("evidence"):
        state["guardrailEffectiveness"]["evidence"] = [
            "file:.iacode/memory/guardrails/registry.json", "file:.iacode/memory/lessons.jsonl"]

    write_json(CHECKPOINT / "STATE.json", state)
    print(json.dumps({
        "preflight": [block["lessonsConsidered"], block["lessonsApplicable"],
                      block["derivedRequirements"]],
        "matrix": state["requirementsMatrix"],
        "anchors": state["integrity"]["anchors"],
        "guardrails": {key: measured[key] for key in ("guardrailsTotal", "guardrailsEffective",
                                                         "guardrailFailures")},
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
