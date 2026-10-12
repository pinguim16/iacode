#!/usr/bin/env python3
"""Promote generated verifier reports into checkpoint-owned, transportable evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
NAMES = (
    "quality-recovery.json",
    "quality-cancellation.json",
    "quality-timeout.json",
    "sandbox-tool-result-origin.json",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    source = arguments.source.resolve()
    destination = CHECKPOINT / "runtime-reports"
    destination.mkdir(parents=True, exist_ok=True)
    reports = []
    for name in NAMES:
        source_path = source / "var" / name
        if not source_path.is_file():
            raise RuntimeError(f"the single verifier invocation did not produce {name}")
        document = json.loads(source_path.read_text(encoding="utf-8"))
        target = destination / name
        shutil.copy2(source_path, target)
        content = target.read_bytes()
        reports.append({
            "path": f"runtime-reports/{name}",
            "sha256": hashlib.sha256(content).hexdigest(),
            "sizeBytes": len(content),
            "result": document.get("result"),
        })
    passed = all(item["result"] == "PASS" for item in reports)
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "SINGLE-VERIFIER-RUNTIME-REPORTS",
        "checkpoint": CHECKPOINT.name,
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "sourceClassification": (
            "Generated output of the checkpoint's single recorded published-clone verifier; "
            "not a command input and not required after these checkpoint-owned copies are committed."
        ),
        "reports": reports,
        "result": "PASS" if passed else "FAIL",
    }
    arguments.report.resolve().write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(
        f"VERIFIER_RUNTIME_REPORTS={report['result']} "
        f"reports={sum(1 for item in reports if item['result'] == 'PASS')}/{len(reports)}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

