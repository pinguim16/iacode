#!/usr/bin/env python3
"""Copy into STATE.json the blocks that are derived from other artifacts, never typed by hand.

The preflight counts come from LESSON-PREFLIGHT.json, the requirement counts from the matrix as the
completeness audit evaluates it, the anchor count from the integrity chain and the guardrail
measurement from the memory. Validation recomputes every one of them, so this only saves the run
from transcribing a number the tooling already owns.

    python sync_state.py [--status IN_PROGRESS]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from anchors import load_anchors  # noqa: E402
from delivery_assurance import evaluate_matrix, load_matrix  # noqa: E402
from ledger_common import load_json, utc_now, write_json  # noqa: E402
from lessons import guardrail_effectiveness  # noqa: E402

PHASE = "M1 corrective delivery: close M1-F-003, M1-F-001 and M1-F-002 of audit M1-CP-0002"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default=None)
    parser.add_argument("--dirty", choices=("true", "false"), default=None,
                        help="the working tree state the checkpoint is validated against")
    arguments = parser.parse_args()
    state = load_json(CHECKPOINT / "STATE.json")
    state["phase"] = PHASE
    if arguments.dirty is not None:
        state["dirty"] = arguments.dirty == "true"
    if arguments.status:
        state["status"] = arguments.status
        (CHECKPOINT / "STATUS.md").write_text(f"# Status\n\n{arguments.status}\n",
                                              encoding="utf-8", newline="\n")
    state["updatedAt"] = utc_now()

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
    state["integrity"]["chainFile"] = ".iacode/anchors/checkpoint-chain.json"

    # The Green Keeper block is the last cycle of REWORK-LOG.jsonl, read rather than typed.
    cycles = [json.loads(line) for line in (CHECKPOINT / "REWORK-LOG.jsonl")
              .read_text(encoding="utf-8").splitlines() if line.strip()]
    if cycles:
        last = cycles[-1]
        state["greenKeeper"].update({
            "status": "PASS" if last.get("result") == "GREEN"
            and not last.get("remainingFailures") else "FAIL",
            "cycles": len(cycles),
            "remainingFailures": int(last.get("remainingFailures") or 0),
            "unresolvedReworkItems": 0,
            "log": "REWORK-LOG.jsonl",
            "externalBlockers": [],
            "evidence": ["file:REWORK-LOG.jsonl"] + [
                f"command:{item['commandId']}" for item in last.get("gateResults") or []],
        })
        state["reworkCycles"] = len(cycles)

    # The completeness block is COMPLETENESS-REPORT.json, when the audit has run.
    completeness_path = CHECKPOINT / "COMPLETENESS-REPORT.json"
    if completeness_path.is_file():
        completeness = load_json(completeness_path)
        state["deliveryCompleteness"].update({
            "status": completeness.get("result"),
            "report": "COMPLETENESS-REPORT.json",
            "coveragePercent": completeness.get("coveragePercent"),
            "evidenceCoveragePercent": completeness.get("evidenceCoveragePercent"),
            "auditor": completeness.get("auditor"),
            "evidence": ["file:COMPLETENESS-REPORT.json", "command:cmd-0104"],
        })

    measured = guardrail_effectiveness(ROOT)
    for key in ("guardrailsTotal", "guardrailsResolved", "guardrailsTested",
                "guardrailsEffective", "guardrailFailures"):
        state["guardrailEffectiveness"][key] = measured[key]
    if not state["guardrailEffectiveness"].get("evidence"):
        state["guardrailEffectiveness"]["evidence"] = [
            "file:.iacode/memory/guardrails/registry.json", "file:.iacode/memory/lessons.jsonl"]

    write_json(CHECKPOINT / "STATE.json", state)

    metadata = load_json(CHECKPOINT / "RUN-METADATA.json")
    metadata.update({
        "tool": "Claude Code (desktop application, Code tab)",
        "toolVersion": "not exposed to the run",
        "provider": "Anthropic",
        "model": "claude-opus-5-5",
        "effort": "not-exposed",
        "operatingSystem": "Windows 11 Pro 10.0.26200",
    })
    write_json(CHECKPOINT / "RUN-METADATA.json", metadata)
    print(json.dumps({
        "status": state["status"],
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
