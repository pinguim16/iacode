#!/usr/bin/env python3
"""Build the final M0 audit matrix of this audit, recomputing its summary from the rows.

The skeleton is written first, with every row ``NOT_STARTED``. Results arrive as append-only
records in ``RESULTS.jsonl``; the matrix is rebuilt from the rows plus those records, so the
published artifact is a function of the recorded executions and never a hand-edited document.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from matrix_rows import all_rows

HARNESS = Path(__file__).resolve().parent
CHECKPOINT = HARNESS.parent
ROOT = CHECKPOINT.parents[2]
RESULTS = HARNESS / "RESULTS.jsonl"
MATRIX_JSON = CHECKPOINT / "FINAL-M0-AUDIT-MATRIX.json"
MATRIX_MD = CHECKPOINT / "FINAL-M0-AUDIT-MATRIX.md"

SUBJECT = "SETUP-00-CP-0012"
TERMINAL = {"COMPLETE", "FAILED"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def subject_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"refs/tags/iacode-checkpoints/{SUBJECT}^{{commit}}"],
        cwd=ROOT, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def load_results() -> dict[str, dict]:
    records: dict[str, dict] = {}
    if not RESULTS.is_file():
        return records
    for line in RESULTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        records[record["id"]] = record
    return records


def evidence_resolves(reference: str) -> bool:
    kind, _, value = reference.partition(":")
    if kind == "checkpoint":
        return (CHECKPOINT / value).exists()
    if kind == "file":
        return (ROOT / value).exists()
    if kind in ("command", "row", "test", "execution", "probe"):
        return bool(value)
    return False


def build() -> dict:
    rows = all_rows()
    records = load_results()
    for row in rows:
        record = records.get(row["id"])
        if record is None:
            continue
        row["status"] = record["status"]
        row["observed"] = record["observed"]
        row["evidence"] = record["evidence"]
        row["verdict"] = record.get("verdict")

    total = len(rows)
    mandatory = sum(1 for row in rows if row["mandatory"])
    complete = sum(1 for row in rows if row["status"] == "COMPLETE")
    failed = sum(1 for row in rows if row["status"] == "FAILED")
    unverified = sum(1 for row in rows if row["status"] == "UNVERIFIED")
    in_progress = sum(1 for row in rows if row["status"] == "IN_PROGRESS")
    not_started = sum(1 for row in rows if row["status"] == "NOT_STARTED")
    executed = complete + failed
    without_evidence = [
        row["id"] for row in rows if row["status"] in TERMINAL and not row["evidence"]]
    unresolvable = [
        f"{row['id']}:{reference}" for row in rows for reference in row["evidence"]
        if not evidence_resolves(reference)]
    mandatory_incomplete = [
        row["id"] for row in rows if row["mandatory"] and row["status"] not in TERMINAL]
    mandatory_failed = [
        row["id"] for row in rows if row["mandatory"] and row["status"] == "FAILED"]

    return {
        "schemaVersion": "1.0.0",
        "artifact": "FINAL-M0-AUDIT-MATRIX",
        "checkpoint": CHECKPOINT.name,
        "milestone": "M0",
        "gate": "SETUP-00",
        "subjectCheckpoint": SUBJECT,
        "subjectCommit": subject_commit(),
        "auditMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
        "sameToolAsImplementer": True,
        "sameProviderAsImplementer": True,
        "crossToolValidation": "NOT_AVAILABLE",
        "createdAt": _now(),
        "note": (
            "Rows are the dimensions of the audit mandate, written before substantive execution. "
            "Results are merged from the append-only execution record; no row is edited by hand."),
        "allowedStatuses": ["NOT_STARTED", "IN_PROGRESS", "COMPLETE", "FAILED", "UNVERIFIED"],
        "rows": rows,
        "summary": {
            "total": total,
            "mandatory": mandatory,
            "complete": complete,
            "failed": failed,
            "unverified": unverified,
            "inProgress": in_progress,
            "notStarted": not_started,
            "executed": executed,
            "missingEvidence": len(without_evidence),
            "rowsWithoutEvidence": without_evidence,
            "unresolvableEvidence": unresolvable,
            "mandatoryIncomplete": mandatory_incomplete,
            "mandatoryFailed": mandatory_failed,
            "executedPercent": round(executed / total * 100, 2) if total else 0.0,
            "evidenceCoveragePercent": (
                round((executed - len(without_evidence)) / executed * 100, 2) if executed else 0.0),
            "recomputedAt": _now(),
        },
    }


def render_markdown(matrix: dict) -> str:
    summary = matrix["summary"]
    lines = [
        "# Final M0 Audit Matrix",
        "",
        f"- Audit checkpoint: `{matrix['checkpoint']}`",
        f"- Subject: `{matrix['subjectCheckpoint']}` at `{matrix['subjectCommit']}`",
        f"- Mechanism: `{matrix['auditMechanism']}`",
        f"- Same tool as implementer: `{matrix['sameToolAsImplementer']}`; "
        f"same provider: `{matrix['sameProviderAsImplementer']}`; "
        f"cross-tool validation: `{matrix['crossToolValidation']}`",
        "",
        "## Summary",
        "",
        "| Measure | Value |",
        "|---|---|",
        f"| Rows | {summary['total']} |",
        f"| Mandatory rows | {summary['mandatory']} |",
        f"| Complete | {summary['complete']} |",
        f"| Failed | {summary['failed']} |",
        f"| Unverified | {summary['unverified']} |",
        f"| In progress | {summary['inProgress']} |",
        f"| Not started | {summary['notStarted']} |",
        f"| Rows without evidence | {summary['missingEvidence']} |",
        f"| Unresolvable evidence references | {len(summary['unresolvableEvidence'])} |",
        f"| Execution coverage | {summary['executedPercent']} per cent |",
        f"| Evidence coverage | {summary['evidenceCoveragePercent']} per cent |",
        "",
        "## Rows",
        "",
        "| Row | Dimension | Status | Verdict | Observed |",
        "|---|---|---|---|---|",
    ]
    for row in matrix["rows"]:
        observed = (row["observed"] or "").replace("|", "/").replace("\n", " ")
        lines.append(
            f"| `{row['id']}` | {row['dimension']} | `{row['status']}` | "
            f"`{row['verdict'] or 'NONE'}` | {observed} |")
    lines += ["", "## What each row would have failed on", "",
              "| Row | Expectation | Fails if |", "|---|---|---|"]
    for row in matrix["rows"]:
        lines.append(
            f"| `{row['id']}` | {row['expectation'].replace('|', '/')} | "
            f"{row['failsIf'].replace('|', '/')} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skeleton", action="store_true",
                        help="refuse to write when any result already exists")
    args = parser.parse_args()
    if args.skeleton and load_results():
        print("MATRIX_SKELETON_REFUSED: execution records already exist")
        return 2
    matrix = build()
    MATRIX_JSON.write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    MATRIX_MD.write_text(render_markdown(matrix), encoding="utf-8", newline="\n")
    summary = matrix["summary"]
    print(
        f"MATRIX rows={summary['total']} complete={summary['complete']} "
        f"failed={summary['failed']} unverified={summary['unverified']} "
        f"notStarted={summary['notStarted']} missingEvidence={summary['missingEvidence']} "
        f"unresolvable={len(summary['unresolvableEvidence'])} "
        f"executed={summary['executedPercent']}% evidence={summary['evidenceCoveragePercent']}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
