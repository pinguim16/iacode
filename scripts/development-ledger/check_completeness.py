#!/usr/bin/env python3
"""Audit the requirements matrix and emit the delivery completeness report.

This is the evidence harness for the Delivery Completeness Validator defined in
``.iacode/agents/delivery-completeness-validator.md``. It audits; it never implements and never
silently corrects. Every requirement that claims completion must point at evidence this tool can
resolve, so "the implementer said it is done" is not acceptable input.

``DELIVERY_COMPLETENESS_GATE`` is ``PASS`` only when coverage is total, nothing is partial or
missing, and every evidence reference resolves.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from delivery_assurance import evaluate_matrix, load_matrix
from ledger_common import LedgerError, find_root, load_json, resolve_latest, utc_now, validate_schema


def render_markdown(report: dict[str, Any], matrix: dict[str, Any]) -> str:
    lines = [
        "# Delivery Completeness Report",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Checkpoint: `{report['checkpoint']}`",
        f"- Matrix: `{report['matrix']}`",
        f"- Generated: `{report['generatedAt']}`",
        f"- Auditor: {report.get('auditor', 'not recorded')}",
        "",
        "## Counts",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| totalRequirements | {report['totalRequirements']} |",
        f"| mandatoryRequirements | {report['mandatoryRequirements']} |",
        f"| complete | {report['complete']} |",
        f"| partial | {report['partial']} |",
        f"| missing | {report['missing']} |",
        f"| notApplicable | {report['notApplicable']} |",
        f"| inProgress | {report.get('inProgress', 0)} |",
        f"| notStarted | {report.get('notStarted', 0)} |",
        f"| coveragePercent | {report['coveragePercent']:.2f} |",
        f"| evidenceCoveragePercent | {report['evidenceCoveragePercent']:.2f} |",
        "",
        "## Findings",
        "",
    ]
    if report["findings"]:
        lines += ["| Requirement | Severity | Detail |", "|---|---|---|"]
        for finding in report["findings"]:
            lines.append("| `%s` | %s | %s |" % (
                finding["requirement"], finding["severity"], finding["detail"]))
    else:
        lines.append("No finding. Every requirement is satisfied and every evidence reference resolved.")
    lines += [
        "",
        "## Per-requirement audit",
        "",
        "| ID | Mandatory | Status | Evidence references |",
        "|---|---|---|---|",
    ]
    for item in matrix.get("requirements", []):
        references = []
        for key in ("implementationEvidence", "testEvidence", "documentationEvidence", "validationEvidence"):
            references.extend(item.get(key) or [])
        lines.append("| `%s` | %s | `%s` | %s |" % (
            item.get("id"),
            "yes" if item.get("mandatory") else "no",
            item.get("status"),
            ", ".join("`%s`" % value for value in references) if references else "_none_",
        ))
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--auditor", default="Delivery Completeness Validator")
    parser.add_argument("--write", action="store_true", help="write COMPLETENESS-REPORT.json and .md")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    matrix = load_matrix(checkpoint)
    schema_path = root / ".iacode" / "schemas" / "requirements-matrix.schema.json"
    if schema_path.is_file():
        schema_errors = validate_schema(matrix, load_json(schema_path))
        if schema_errors:
            print("REQUIREMENTS_MATRIX_INVALID")
            for error in schema_errors:
                print(f"- {error}")
            return 2

    report = evaluate_matrix(root, checkpoint, matrix)
    report = {
        "schemaVersion": "1.0.0",
        "checkpoint": checkpoint.name,
        "generatedAt": utc_now(),
        "matrix": "REQUIREMENTS-MATRIX.json",
        "auditor": args.auditor,
        **report,
    }

    report_schema = root / ".iacode" / "schemas" / "completeness-report.schema.json"
    if report_schema.is_file():
        errors = validate_schema(report, load_json(report_schema))
        if errors:
            print("COMPLETENESS_REPORT_INVALID")
            for error in errors:
                print(f"- {error}")
            return 2

    if args.write:
        (checkpoint / "COMPLETENESS-REPORT.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        (checkpoint / "COMPLETENESS-REPORT.md").write_text(
            render_markdown(report, matrix), encoding="utf-8", newline="\n")

    print(f"DELIVERY_COMPLETENESS_GATE={report['result']} "
          f"coverage={report['coveragePercent']:.2f} evidenceCoverage={report['evidenceCoveragePercent']:.2f} "
          f"total={report['totalRequirements']} complete={report['complete']} "
          f"partial={report['partial']} missing={report['missing']} notApplicable={report['notApplicable']}")
    for finding in report["findings"]:
        print(f"- [{finding['severity']}] {finding['requirement']}: {finding['detail']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
