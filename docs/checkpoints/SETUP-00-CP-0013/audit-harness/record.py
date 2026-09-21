#!/usr/bin/env python3
"""Append one audit-matrix result. Append-only, so a corrected row keeps its earlier record.

    python record.py AM-001 COMPLETE PASS "observed ..." file:a checkpoint:b
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from matrix_rows import ROWS

RESULTS = Path(__file__).resolve().parent / "RESULTS.jsonl"
STATUSES = {"NOT_STARTED", "IN_PROGRESS", "COMPLETE", "FAILED", "UNVERIFIED"}
VERDICTS = {"PASS", "FAIL", "NONE"}


def main() -> int:
    if len(sys.argv) < 5:
        print(__doc__)
        return 2
    identifier, status, verdict, observed, *evidence = sys.argv[1:]
    known = {row["id"] for row in ROWS}
    if identifier not in known:
        print(f"UNKNOWN_ROW {identifier}")
        return 2
    if status not in STATUSES:
        print(f"UNKNOWN_STATUS {status}")
        return 2
    if verdict not in VERDICTS:
        print(f"UNKNOWN_VERDICT {verdict}")
        return 2
    if status in ("COMPLETE", "FAILED") and not evidence:
        print("A terminal row requires at least one evidence reference")
        return 2
    record = {
        "id": identifier,
        "status": status,
        "verdict": None if verdict == "NONE" else verdict,
        "observed": observed,
        "evidence": list(evidence),
        "recordedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with RESULTS.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"RECORDED {identifier} {status} {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
