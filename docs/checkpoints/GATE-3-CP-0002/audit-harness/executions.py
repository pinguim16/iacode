#!/usr/bin/env python3
"""Append one execution this audit relied on, and assemble AUDIT-EXECUTIONS.json from the record.

The record is append-only. A non-zero exit code is kept rather than removed: some executions are
deliberately negative, and the dimension says which.

    python executions.py add --id EX-001 --dimension "..." --command "..." --exit 0 \
        --observed "..." --evidence command:cmd-0004
    python executions.py build
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
CHECKPOINT = HARNESS.parent
RECORD = HARNESS / "EXECUTIONS.jsonl"
SUBJECT = "GATE-3-CP-0001"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load() -> list[dict]:
    if not RECORD.is_file():
        return []
    return [json.loads(line) for line in RECORD.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def add(identifier: str, dimension: str, command: str, exit_code: int, observed: str,
        evidence: list[str]) -> dict:
    existing = {item["id"] for item in load()}
    if identifier in existing:
        raise SystemExit(f"{identifier} is already recorded; the record is append-only")
    entry = {"id": identifier, "dimension": dimension, "command": command,
             "exitCode": exit_code, "observed": observed, "evidence": evidence,
             "recordedAt": now()}
    with RECORD.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def build() -> Path:
    document = {
        "schemaVersion": "1.0.0",
        "artifact": "AUDIT-EXECUTIONS",
        "checkpoint": CHECKPOINT.name,
        "milestone": "M1",
        "subjectCheckpoint": SUBJECT,
        "auditMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
        "note": ("Every execution this audit relied on, appended as it happened. A non-zero exit "
                 "code is kept rather than removed: some executions are deliberately negative, "
                 "and the dimension says which."),
        "generatedAt": now(),
        "executions": load(),
    }
    target = CHECKPOINT / "AUDIT-EXECUTIONS.json"
    target.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8", newline="\n")
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    adder = sub.add_parser("add")
    adder.add_argument("--id", required=True)
    adder.add_argument("--dimension", required=True)
    adder.add_argument("--command", required=True)
    adder.add_argument("--exit", type=int, required=True)
    adder.add_argument("--observed", required=True)
    adder.add_argument("--evidence", action="append", default=[])
    sub.add_parser("build")
    arguments = parser.parse_args()
    if arguments.action == "add":
        entry = add(arguments.id, arguments.dimension, arguments.command, arguments.exit,
                    arguments.observed, arguments.evidence)
        print(json.dumps(entry, ensure_ascii=False))
    else:
        print(build())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
