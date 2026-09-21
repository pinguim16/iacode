#!/usr/bin/env python3
"""Append-only record of what this audit executed, and the artifact it renders.

An audit that reports only its verdict hides what it looked at. Every execution this audit relied
on is appended here with the command that produced it, its exit code and what was observed, and
``build`` renders ``AUDIT-EXECUTIONS.json`` from the records rather than from a narrative.

    python executions.py add <id> <dimension> <exitCode> <command> <observed> [evidence ...]
    python executions.py build
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
CHECKPOINT = HARNESS.parent
LOG = HARNESS / "EXECUTIONS.jsonl"
ARTIFACT = CHECKPOINT / "AUDIT-EXECUTIONS.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def add(argv: list[str]) -> int:
    if len(argv) < 5:
        print(__doc__)
        return 2
    identifier, dimension, exit_code, command, observed, *evidence = argv
    record = {
        "id": identifier,
        "dimension": dimension,
        "command": command,
        "exitCode": int(exit_code),
        "observed": observed,
        "evidence": list(evidence),
        "recordedAt": _now(),
    }
    with LOG.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"EXECUTION_RECORDED {identifier} exit={exit_code}")
    return 0


def build() -> int:
    records = []
    if LOG.is_file():
        for line in LOG.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    # A later record for the same identifier supersedes an earlier one; both stay in the log.
    latest: dict[str, dict] = {}
    for record in records:
        latest[record["id"]] = record
    executions = [latest[key] for key in sorted(latest)]
    failed = [item["id"] for item in executions if item["exitCode"] != 0]
    payload = {
        "schemaVersion": "1.0.0",
        "artifact": "AUDIT-EXECUTIONS",
        "checkpoint": CHECKPOINT.name,
        "subjectCheckpoint": "SETUP-00-CP-0012",
        "auditMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
        "crossToolValidation": "NOT_AVAILABLE",
        "note": (
            "Every execution this audit relied on, appended as it happened. A non-zero exit code "
            "is kept rather than removed: some executions are deliberately negative, and the "
            "dimension says which."),
        "generatedAt": _now(),
        "executions": executions,
        "total": len(executions),
        "nonZeroExit": failed,
        "appendOnlyRecords": len(records),
    }
    ARTIFACT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")
    print(f"EXECUTIONS_BUILT total={payload['total']} records={len(records)} "
          f"nonZeroExit={len(failed)}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    if sys.argv[1] == "add":
        return add(sys.argv[2:])
    if sys.argv[1] == "build":
        return build()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
