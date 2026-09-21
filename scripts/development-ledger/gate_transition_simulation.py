#!/usr/bin/env python3
"""Execute the transition into the next Gate, in a disposable repository.

Finding ``CP11-F-001`` blocked two states, and the second one is the one no existing simulation
covered: *the first delivery of the next Gate*. It corrects no audit, because no audit has judged it
yet, so the two mirror dimensions that derive their work from the audit registry had nothing to
audit and reported ``FAIL``; checkpoint validation then refused every positive terminal status, and
the delivery could not be handed over at all. The audit executed exactly that in a disposable clone
rather than predicting it.

This simulation executes the whole transition:

    SETUP delivered and sealed
      -> a second checkpoint authored as its independent audit, with an attestation
      -> the milestone verdict derived as PASSED from the repository
      -> the first checkpoint of the next Gate, anchoring its sealed predecessor
      -> READY_FOR_REVIEW

Nothing of the next Gate is implemented. The disposable repository declares a synthetic
specification for it so the delivery order has a requirement set to derive; the subject of the proof
is the state machine, not the Gate's content, and no Gate 0 artifact is created in this repository.

    python scripts/development-ledger/gate_transition_simulation.py --write
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, find_root, resolve_latest, utc_now, write_json
from promotion_fixture import run_gate_transition


def evaluate(result: dict[str, Any]) -> dict[str, Any]:
    mirror = result["mirror"]
    inapplicable = result["inapplicable"]
    justified = [
        item for item in inapplicable
        if (item.get("reason") or "").strip()
        and (item.get("derivationSource") or "").strip()
        and item.get("expectedCount") == 0
    ]
    checks = [
        {
            "id": "GT-001",
            "expectation": "the milestone that precedes the next Gate is derived as PASSED from "
                           "the repository",
            "observed": f"{result['setupAudit']['checkpoint']} carries the attestation; derived "
                        f"verdict {result['milestoneVerdictBeforeTransition']}",
            "result": "PASS" if result["milestoneVerdictBeforeTransition"] == "PASSED" else "FAIL",
        },
        {
            "id": "GT-002",
            "expectation": "the next Gate has a specification the requirement set can be derived "
                           "from, inside the disposable repository only",
            "observed": f"{result['syntheticSpecification']['specification']} with "
                        f"{result['syntheticSpecification']['rows']} requirement row(s)",
            "result": "PASS" if result["syntheticSpecification"]["rows"] > 0 else "FAIL",
        },
        {
            "id": "GT-003",
            "expectation": "the first checkpoint of the next Gate is created and belongs to the "
                           "planned milestone of that Gate",
            "observed": f"{result['delivery']['checkpoint']} in {result['nextMilestone']}",
            "result": "PASS" if result["delivery"]["checkpoint"].startswith(
                f"{result['nextGate']}-CP-") else "FAIL",
        },
        {
            "id": "GT-004",
            "expectation": "the internal mirror audit of that checkpoint is produced by executing "
                           "m0_mirror_audit.py",
            "observed": f"{mirror['command']} exit={mirror['exitCode']}",
            "result": "PASS" if mirror["producedBy"] == "execution" and mirror["exitCode"] == 0
                      else "FAIL",
        },
        {
            "id": "GT-005",
            "expectation": "the dimensions with nothing to audit are NOT_APPLICABLE with a reason, "
                           "an empty expected count and a named derivation source",
            "observed": "; ".join(
                f"{item['id']} expectedCount={item['expectedCount']}" for item in inapplicable)
                        or "no dimension was inapplicable",
            "result": "PASS" if inapplicable and len(justified) == len(inapplicable) else "FAIL",
        },
        {
            "id": "GT-006",
            "expectation": "the mirror audit of a delivery that corrects no audit passes",
            "observed": f"{mirror['result']} {mirror['passed']}/{mirror['total']}, "
                        f"{mirror['notApplicable']} inapplicable, {mirror['failed']} failed",
            "result": "PASS" if mirror["result"] == "PASS" else "FAIL",
        },
        {
            "id": "GT-007",
            "expectation": "the delivery reaches READY_FOR_REVIEW and validates as sealed",
            "observed": f"{result['statusReached']}: {result['validatorOutput']}",
            "result": "PASS" if (result["statusReached"] == "READY_FOR_REVIEW"
                                 and "CHECKPOINT_VALID" in result["validatorOutput"]) else "FAIL",
        },
        {
            "id": "GT-008",
            "expectation": "the integrity chain still verifies after the Gate transition",
            "observed": "; ".join(result["chainErrors"]) or "no divergence",
            "result": "PASS" if not result["chainErrors"] else "FAIL",
        },
        {
            "id": "GT-009",
            "expectation": "no runtime of the next Gate was implemented by this simulation",
            "observed": f"no services, runtime, gateway or sandbox tree exists: "
                        f"{result['noGateRuntime']}",
            "result": "PASS" if result["noGateRuntime"] else "FAIL",
        },
    ]
    failed = [item for item in checks if item["result"] != "PASS"]
    return {
        "schemaVersion": "1.0.0",
        "generatedAt": utc_now(),
        "simulation": "transition from a closed milestone into the first delivery of the next Gate",
        "finding": "CP11-F-001",
        "scope": "the state machine only; the next Gate's specification is synthetic, lives in the "
                 "disposable repository, and no Gate 0 work exists in this repository",
        "setup": {
            "subject": result["setupSubject"]["checkpoint"],
            "audit": result["setupAudit"]["checkpoint"],
            "milestoneVerdict": result["milestoneVerdictBeforeTransition"],
        },
        "nextGate": result["nextGate"],
        "nextMilestone": result["nextMilestone"],
        "checkpoint": result["delivery"]["checkpoint"],
        "statusReached": result["statusReached"],
        "mirror": {
            "command": mirror["command"],
            "exitCode": mirror["exitCode"],
            "result": mirror["result"],
            "total": mirror["total"],
            "passed": mirror["passed"],
            "failed": mirror["failed"],
            "notApplicable": mirror["notApplicable"],
            "inapplicable": inapplicable,
            "producedBy": mirror["producedBy"],
        },
        "checks": checks,
        "total": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "result": "PASS" if not failed else "FAIL",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Gate Transition Simulation",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Simulation: {report['simulation']}",
        f"- Closes: `{report['finding']}`",
        f"- Generated: `{report['generatedAt']}`",
        f"- Preceding milestone verdict: `{report['setup']['milestoneVerdict']}`, derived from "
        f"`{report['setup']['audit']}` about `{report['setup']['subject']}`",
        f"- Next Gate: `{report['nextGate']}` in `{report['nextMilestone']}`",
        f"- First checkpoint of that Gate: `{report['checkpoint']}` at "
        f"`{report['statusReached']}`",
        "",
        "## Scope",
        "",
        report["scope"] + ".",
        "",
        "Every row below was executed in a disposable repository built by",
        "`scripts/development-ledger/promotion_fixture.py`; nothing here is asserted.",
        "",
        "| Check | Expectation | Observed | Result |",
        "|---|---|---|---|",
    ]
    for check in report["checks"]:
        lines.append("| `%s` | %s | %s | `%s` |" % (
            check["id"], check["expectation"], str(check["observed"]).replace("|", "/"),
            check["result"]))
    lines += [
        "",
        "## The dimensions with nothing to audit",
        "",
        "| ID | Expected items | Reason | Derived from |",
        "|---|---|---|---|",
    ]
    for item in report["mirror"]["inapplicable"]:
        lines.append("| `%s` | %s | %s | %s |" % (
            item["id"], item["expectedCount"], str(item["reason"]).replace("|", "/"),
            str(item["derivationSource"]).replace("|", "/")))
    lines += ["", f"Passed: `{report['passed']}` of `{report['total']}` checks."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--write", action="store_true",
                        help="write GATE0-TRANSITION-SIMULATION.json and .md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    with tempfile.TemporaryDirectory(prefix="iacode-gate-transition-") as workdir:
        result = run_gate_transition(Path(workdir))
        report = evaluate(result)

    if args.write:
        write_json(checkpoint / "GATE0-TRANSITION-SIMULATION.json", report)
        (checkpoint / "GATE0-TRANSITION-SIMULATION.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"GATE_TRANSITION={report['result']} checks={report['passed']}/{report['total']} "
              f"status={report['statusReached']}")
        for check in report["checks"]:
            if check["result"] != "PASS":
                print(f"- FAILED {check['id']}: {check['observed']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
