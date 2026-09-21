#!/usr/bin/env python3
"""Advance a sealed checkpoint chain in a disposable repository and re-check it at every state.

Finding ``CP9-F-002`` was that a guardrail test named the checkpoint it excluded by literal, so
performing the protocol's own next step -- a successor anchoring its sealed predecessor -- turned
the mandatory ``tests`` gate red, and the only remedy available was editing a guardrail test.

    python scripts/development-ledger/successor_durability.py --write

The run seals three checkpoints in succession, each one anchoring its predecessor, and after every
state re-derives the pending-anchor exclusion, verifies the chain, and runs ``verify_integrity.py``.
It then removes the anchor of a checkpoint the exclusion does not forgive and requires the control
to detect it, so the durability is not bought by weakening the check.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, find_root, resolve_latest, utc_now, write_json
from promotion_fixture import run_successor_durability


def evaluate(result: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for index, state in enumerate(result["states"], 1):
        checks.append({
            "id": "SUC-%03d" % index,
            "expectation": "the chain verifies with a derived exclusion at this state",
            "observed": (f"sealed {', '.join(state['sealed'])}; anchored "
                         f"{', '.join(state['anchored']) or 'none'}; pending anchor "
                         f"{state['pendingAnchor']}; "
                         + ("; ".join(state["chainErrors"]) or "no divergence")),
            "state": state["state"],
            "result": "PASS" if not state["chainErrors"] else "FAIL",
        })
        checks.append({
            "id": "SUC-%03dI" % index,
            "expectation": "verify_integrity.py exits zero at this state",
            "observed": f"exit={state['integrityExit']} "
                        + " ".join(state["integrityOutput"]),
            "state": state["state"],
            "result": "PASS" if state["integrityExit"] == 0 else "FAIL",
        })
    checks.append({
        "id": "SUC-DETECT",
        "expectation": "removing the anchor of a checkpoint the rule does not forgive is detected",
        "observed": f"removed {result['removedAnchor']}: "
                    + ("; ".join(result["detectionErrors"]) or "nothing reported"),
        "state": "mutation",
        "result": "PASS" if result["detected"] else "FAIL",
    })
    checks.append({
        "id": "SUC-RESTORE",
        "expectation": "the chain verifies again once the anchor is restored",
        "observed": "; ".join(result["restoredChainErrors"]) or "no divergence",
        "state": "restored",
        "result": "PASS" if not result["restoredChainErrors"] else "FAIL",
    })

    failed = [item for item in checks if item["result"] != "PASS"]
    return {
        "schemaVersion": "1.0.0",
        "generatedAt": utc_now(),
        "simulation": "successor anchor durability",
        "finding": "CP9-F-002",
        "checkpoints": [{
            "checkpoint": item["checkpoint"], "commit": item["commit"], "tag": item["tag"],
        } for item in result["checkpoints"]],
        "states": [item["state"] for item in result["states"]],
        "removedAnchor": result["removedAnchor"],
        "checks": checks,
        "total": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "result": "PASS" if not failed else "FAIL",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Successor Durability",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Simulation: {report['simulation']}",
        f"- Closes: `{report['finding']}`",
        f"- Generated: `{report['generatedAt']}`",
        f"- Checkpoints sealed: {', '.join('`%s`' % item['checkpoint'] for item in report['checkpoints'])}",
        "",
        "Each state below was produced by sealing a real checkpoint in a disposable repository and",
        "re-running the integrity controls; the exclusion is derived at every state, so advancing",
        "the chain never requires a source change.",
        "",
        "| Check | State | Expectation | Observed | Result |",
        "|---|---|---|---|---|",
    ]
    for check in report["checks"]:
        lines.append("| `%s` | %s | %s | %s | `%s` |" % (
            check["id"], check["state"], check["expectation"],
            str(check["observed"]).replace("|", "/"), check["result"]))
    lines += ["", f"Passed: `{report['passed']}` of `{report['total']}` checks."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--successors", type=int, default=2)
    parser.add_argument("--write", action="store_true",
                        help="write SUCCESSOR-DURABILITY.json and .md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    with tempfile.TemporaryDirectory(prefix="iacode-succession-") as workdir:
        result = run_successor_durability(Path(workdir), successors=args.successors)
        report = evaluate(result)

    if args.write:
        write_json(checkpoint / "SUCCESSOR-DURABILITY.json", report)
        (checkpoint / "SUCCESSOR-DURABILITY.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"SUCCESSOR_DURABILITY={report['result']} checks={report['passed']}/{report['total']}")
        for check in report["checks"]:
            if check["result"] != "PASS":
                print(f"- FAILED {check['id']} ({check['state']}): {check['observed']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
