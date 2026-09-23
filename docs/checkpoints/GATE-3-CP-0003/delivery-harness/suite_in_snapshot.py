#!/usr/bin/env python3
"""Run the control-plane suite over a frozen snapshot of the working tree.

The snapshot is `ledger_common.clone_with_worktree`: a published clone of this repository with the
current working tree committed on top, so the run measures exactly the content of the moment it
started, and editing the next correction while it runs cannot change what it measures. This is a
targeted check before a commit; the Green Keeper measures the repository itself.

    python suite_in_snapshot.py --label m1-f-003 --report ../SUITE-SNAPSHOT-M1-F-003.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import clone_with_worktree, utc_now  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--test", action="append", default=[],
                        help="unittest identifiers; the whole suite when omitted")
    arguments = parser.parse_args()
    scratch = Path(tempfile.mkdtemp(prefix="iacode-snapshot-"))
    snapshot = scratch / "snapshot"
    try:
        if not clone_with_worktree(ROOT, snapshot):
            raise SystemExit("the snapshot could not be made")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=snapshot, text=True,
                              capture_output=True, check=False).stdout.strip()
        argv = ([sys.executable, "-m", "unittest", *arguments.test] if arguments.test
                else [sys.executable, "-m", "unittest", "discover", "-s", "tests"])
        started = time.monotonic()
        completed = subprocess.run(argv, cwd=snapshot, text=True, encoding="utf-8",
                                   errors="replace", stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, check=False, timeout=7200)
        seconds = round(time.monotonic() - started, 1)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    failures = [line for line in completed.stdout.splitlines()
                if line.startswith(("FAIL:", "ERROR:"))]
    tail = [line for line in completed.stdout.splitlines()
            if line.startswith(("Ran ", "OK", "FAILED"))]
    report = {
        "schemaVersion": "1.0.0", "artifact": "SUITE-SNAPSHOT", "label": arguments.label,
        "checkpoint": CHECKPOINT.name, "generatedAt": utc_now(), "snapshotHead": head,
        "command": " ".join(argv[1:]), "exitCode": completed.returncode, "seconds": seconds,
        "summary": tail[-3:], "failures": failures[:50],
        "result": "PASS" if completed.returncode == 0 else "FAIL",
    }
    arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    print("\n".join(failures[:30]))
    print(" ".join(tail[-3:]))
    print(f"SUITE_SNAPSHOT={report['result']} label={arguments.label} seconds={seconds}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
