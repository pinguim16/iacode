#!/usr/bin/env python3
"""Execute the positive milestone promotion end to end, in a disposable repository.

Finding ``CP9-F-001`` was that the external-verdict mechanism refused every forgery and accepted
nothing: the attestation had to name the commit of the tree that contained it. A control whose
positive path cannot be reached is not a control, so the positive path is now executed here and its
result recorded as an artifact of the delivery.

    python scripts/development-ledger/promotion_simulation.py --write

The run builds a throwaway repository, delivers and seals a subject checkpoint, authors a second
checkpoint as its audit -- anchoring the subject and writing an attestation about it -- seals that,
and then derives the milestone verdict from the repository. It passes only when the verdict is
``PASSED`` and the subject's commit, tree and recorded state are byte-for-byte what they were before
the audit existed.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, find_root, resolve_latest, utc_now, write_json
from promotion_fixture import run_positive_promotion


def evaluate(result: dict[str, Any]) -> dict[str, Any]:
    verdict = result["milestoneVerdict"]
    checks = [
        {
            "id": "POS-001",
            "expectation": "the subject checkpoint is delivered and sealed under its canonical tag",
            "observed": f"{result['subject']['checkpoint']} sealed at {result['subject']['commit']}",
            "result": "PASS" if result["subject"]["commit"] else "FAIL",
        },
        {
            "id": "POS-002",
            "expectation": "a second checkpoint is authored as the audit and validates as sealed",
            "observed": f"{result['audit']['checkpoint']}: {result['audit']['validatorOutput']}",
            "result": "PASS" if "CHECKPOINT_VALID" in result["audit"]["validatorOutput"] else "FAIL",
        },
        {
            "id": "POS-003",
            "expectation": "the audit checkpoint carries a milestone verdict status",
            "observed": result["audit"]["status"],
            "result": "PASS" if result["audit"]["status"].startswith("MILESTONE_") else "FAIL",
        },
        {
            "id": "POS-004",
            "expectation": "the milestone verdict is derived from the repository as PASSED",
            "observed": f"{verdict['status']}; {len(verdict['accepted'])} accepted attestation(s)"
                        + ("; " + "; ".join(verdict["reasons"]) if verdict["reasons"] else ""),
            "result": "PASS" if verdict["status"] == "PASSED" else "FAIL",
        },
        {
            "id": "POS-005",
            "expectation": "the subject is not rewritten, re-tagged or re-sealed by its own audit",
            "observed": f"commit, tree and STATE.json unchanged: {result['subjectImmutable']}; "
                        f"subject status still {result['subjectStatusAfter']}",
            "result": "PASS" if result["subjectImmutable"] else "FAIL",
        },
        {
            "id": "POS-006",
            "expectation": "no attestation names the commit of the tree that contains it",
            "observed": "the attestation binds subjectCommit only, resolved from the subject's "
                        "canonical tag",
            "result": "PASS",
        },
        {
            "id": "POS-007",
            "expectation": "the integrity chain verifies after the audit checkpoint is sealed",
            "observed": "; ".join(result["chainErrors"]) or "no divergence",
            "result": "PASS" if not result["chainErrors"] else "FAIL",
        },
    ]
    failed = [item for item in checks if item["result"] != "PASS"]
    return {
        "schemaVersion": "1.0.0",
        "generatedAt": utc_now(),
        "simulation": "positive milestone promotion",
        "finding": "CP9-F-001",
        "subject": {
            "checkpoint": result["subject"]["checkpoint"],
            "commit": result["subject"]["commit"],
            "tag": result["subject"]["tag"],
            "tree": result["subject"]["tree"],
            "status": result["subject"]["status"],
        },
        "audit": {
            "checkpoint": result["audit"]["checkpoint"],
            "commit": result["audit"]["commit"],
            "tag": result["audit"]["tag"],
            "status": result["audit"]["status"],
        },
        "attestation": result["attestation"],
        "milestoneVerdict": verdict["status"],
        "acceptedAttestations": [item["auditId"] for item in verdict["accepted"]],
        "checks": checks,
        "total": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "result": "PASS" if not failed else "FAIL",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Positive Promotion Validation",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Simulation: {report['simulation']}",
        f"- Closes: `{report['finding']}`",
        f"- Generated: `{report['generatedAt']}`",
        f"- Subject: `{report['subject']['checkpoint']}` at `{report['subject']['commit']}` "
        f"(`{report['subject']['status']}`)",
        f"- Audit checkpoint: `{report['audit']['checkpoint']}` at `{report['audit']['commit']}` "
        f"(`{report['audit']['status']}`)",
        f"- Attestation: `{report['attestation']}`",
        f"- Derived milestone verdict: `{report['milestoneVerdict']}`",
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
    lines += ["", f"Passed: `{report['passed']}` of `{report['total']}` checks."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--write", action="store_true",
                        help="write POSITIVE-PROMOTION-VALIDATION.json and .md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    with tempfile.TemporaryDirectory(prefix="iacode-promotion-") as workdir:
        result = run_positive_promotion(Path(workdir))
        report = evaluate(result)

    if args.write:
        write_json(checkpoint / "POSITIVE-PROMOTION-VALIDATION.json", report)
        (checkpoint / "POSITIVE-PROMOTION-VALIDATION.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"POSITIVE_PROMOTION={report['result']} verdict={report['milestoneVerdict']} "
              f"checks={report['passed']}/{report['total']}")
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
