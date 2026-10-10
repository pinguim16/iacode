#!/usr/bin/env python3
"""Run the established published-object causal probe and bind its result to this audit."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT_COMMIT = "70a22e824705f414e0c295bbdf89187db9b391f7"
HARNESS = ROOT / "docs" / "checkpoints" / "GATE-3-CP-0006" / "audit-harness" / "remote_published_objects.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="iacode-published-evidence-") as scratch:
        temporary = Path(scratch) / "report.json"
        completed = subprocess.run(
            [sys.executable, str(HARNESS), "--report", str(temporary)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            timeout=1800,
        )
        if temporary.is_file():
            document = json.loads(temporary.read_text(encoding="utf-8"))
        else:
            document = {
                "schemaVersion": "1.0.0",
                "artifact": "REMOTE-PUBLISHED-OBJECTS",
                "checks": [],
                "result": "FAIL",
            }
        document["checkpoint"] = CHECKPOINT.name
        document["subjectCommit"] = SUBJECT_COMMIT
        document["sourceHarness"] = str(HARNESS.relative_to(ROOT)).replace("\\", "/")
        document["harnessExitCode"] = completed.returncode
        document["harnessOutputTail"] = completed.stdout.strip()[-1200:]
        if (
            completed.returncode != 0
            or document.get("result") != "PASS"
            or document.get("clonedHead") != SUBJECT_COMMIT
            or not all(item.get("ok") for item in document.get("checks") or [])
        ):
            document["result"] = "FAIL"
        output = arguments.report.resolve()
        output.write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(
        f"PUBLISHED_EVIDENCE={document['result']} checks="
        f"{sum(1 for item in document.get('checks') or [] if item.get('ok'))}/"
        f"{len(document.get('checks') or [])} head={document.get('clonedHead')}"
    )
    return 0 if document["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
