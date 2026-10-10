#!/usr/bin/env python3
"""Project the latest canonical Green Keeper cycle into a stable audit artifact."""

from __future__ import annotations

import json
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent


def main() -> int:
    cycles = [json.loads(line) for line in (CHECKPOINT / "REWORK-LOG.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not cycles:
        raise RuntimeError("Green Keeper produced no cycle")
    latest = cycles[-1]
    result = "PASS" if latest.get("result") == "GREEN" and not latest.get("remainingFailures") else "FAIL"
    report = {
        "schemaVersion": "1.0.0", "artifact": "GREEN-KEEPER-REPORT",
        "checkpoint": CHECKPOINT.name, "result": result, "cycles": len(cycles),
        "latestCycle": latest, "remainingFailures": latest.get("failureEvidence") or [],
        "note": "Executable Green Keeper gates do not override the independent G4-F-001 security finding.",
    }
    (CHECKPOINT / "GREEN-KEEPER-REPORT.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"GREEN_KEEPER_REPORT={result} cycles={len(cycles)}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
