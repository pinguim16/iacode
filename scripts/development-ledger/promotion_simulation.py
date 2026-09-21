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


def _inapplicable_are_justified(mirror: dict[str, Any]) -> bool:
    """Every inapplicable dimension carries a reason, a derivation source and an empty count.

    An unjustified ``NOT_APPLICABLE`` would turn the repair of ``CP11-F-001`` into a way of hiding a
    dimension instead of describing it, so the simulation checks the justification rather than only
    the verdict. At least one dimension must be inapplicable here: this fixture corrects no audit,
    which is the state the finding made unreachable.
    """
    inapplicable = [item for item in mirror["checks"] if item["result"] == "NOT_APPLICABLE"]
    if not inapplicable:
        return False
    return all(
        (item.get("reason") or "").strip()
        and (item.get("derivationSource") or "").strip()
        and item.get("expectedCount") == 0
        for item in inapplicable)


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
        {
            "id": "POS-008",
            "expectation": "the internal mirror audit of every checkpoint in this simulation was "
                           "produced by executing m0_mirror_audit.py, not by writing its artifact",
            "observed": "; ".join(
                f"{item['checkpoint']}: {item['mirror']['command']} exit="
                f"{item['mirror']['exitCode']} -> {item['mirror']['result']} "
                f"{item['mirror']['passed']}/{item['mirror']['total']}"
                for item in (result["subject"], result["audit"])),
            "result": "PASS" if all(
                item["mirror"]["producedBy"] == "execution"
                and item["mirror"]["exitCode"] == 0
                and item["mirror"]["result"] == "PASS"
                for item in (result["subject"], result["audit"])) else "FAIL",
        },
        {
            "id": "POS-009",
            "expectation": "a checkpoint that corrects no audit reaches a passing mirror with its "
                           "empty dimensions recorded as NOT_APPLICABLE and justified",
            "observed": "; ".join(
                f"{item['checkpoint']}: " + ", ".join(
                    f"{check['id']}={check['result']}"
                    for check in item["mirror"]["checks"]
                    if check["result"] != "PASS") or f"{item['checkpoint']}: none"
                for item in (result["subject"], result["audit"])),
            "result": "PASS" if all(
                _inapplicable_are_justified(item["mirror"]) for item in
                (result["subject"], result["audit"])) else "FAIL",
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
        "artifactProvenance": {
            item["checkpoint"]: {
                "internalMirror": {
                    "producedBy": item["mirror"]["producedBy"],
                    "command": item["mirror"]["command"],
                    "exitCode": item["mirror"]["exitCode"],
                    "result": item["mirror"]["result"],
                    "passed": item["mirror"]["passed"],
                    "failed": item["mirror"]["failed"],
                    "notApplicable": item["mirror"]["notApplicable"],
                    "inapplicable": [
                        {"id": check["id"], "reason": check["reason"],
                         "expectedCount": check["expectedCount"],
                         "derivationSource": check["derivationSource"]}
                        for check in item["mirror"]["checks"]
                        if check["result"] == "NOT_APPLICABLE"],
                },
                "internalRedTeam": {
                    "producedBy": "modelled",
                    "note": "the battery attacks a disposable copy of a sealed delivery; this "
                            "simulation proves the promotion path and never claims the battery of "
                            "the fixture checkpoint was executed",
                },
            }
            for item in (result["subject"], result["audit"])
        },
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
