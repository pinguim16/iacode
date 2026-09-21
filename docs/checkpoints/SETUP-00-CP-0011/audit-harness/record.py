#!/usr/bin/env python3
"""Append one audit execution record, or a batch of them, to the append-only result log.

A row of the matrix is never edited in place. Its status comes from a record written here after the
execution it describes, which is why the matrix can be rebuilt from scratch at any moment and why a
row cannot silently change without leaving a record behind.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "RESULTS.jsonl"
ALLOWED = {"COMPLETE", "FAILED", "UNVERIFIED", "IN_PROGRESS"}


def append(records: list[dict]) -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with RESULTS.open("a", encoding="utf-8", newline="\n") as handle:
        for record in records:
            if record["status"] not in ALLOWED:
                raise SystemExit(f"{record['id']}: unsupported status {record['status']!r}")
            if record["status"] in ("COMPLETE", "FAILED") and not record.get("evidence"):
                raise SystemExit(f"{record['id']}: a terminal row requires evidence")
            record.setdefault("recordedAt", stamp)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, help="a JSON array of records")
    parser.add_argument("--id")
    parser.add_argument("--status")
    parser.add_argument("--verdict")
    parser.add_argument("--observed")
    parser.add_argument("--evidence", action="append", default=[])
    args = parser.parse_args()

    if args.batch:
        records = json.loads(args.batch.read_text(encoding="utf-8"))
    else:
        records = [{
            "id": args.id,
            "status": args.status,
            "verdict": args.verdict,
            "observed": args.observed,
            "evidence": args.evidence,
        }]
    written = append(records)
    print(f"RECORDED {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
