#!/usr/bin/env python3
"""Locate the first failure in an unchanged published subject; never a promotion gate."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import LedgerError, utc_now, write_json
from secret_scan import scan_text

SUBJECT = "4c53e4f788adc24e1b9cd9f581a7dc0d0f3c1340"
TAG = "iacode-subjects/GATE-4-CP-0010-internal-corrective-v2"


def git(directory: Path, *arguments: str) -> str:
    return subprocess.run(["git", *arguments], cwd=directory, check=True,
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stream-control", action="store_true")
    args = parser.parse_args()
    report = CHECKPOINT / ("PUBLISHED-V2-STREAM-FAILURE.json" if args.stream_control
                           else "PUBLISHED-V2-FIRST-FAILURE.json")
    if report.exists():
        raise LedgerError("preserve the previous diagnostic attempt")
    remote = git(ROOT, "remote", "get-url", "origin")
    with tempfile.TemporaryDirectory(prefix="iacode-cp0010-root-diagnostic-") as temporary:
        clone = Path(temporary) / "repository"
        git(Path(temporary), "clone", "--no-local", "--branch", TAG, remote, str(clone))
        if git(clone, "rev-parse", "HEAD") != SUBJECT:
            raise LedgerError("published diagnostic subject changed")
        shutil.copy2(ROOT / "infra/compose/.env", clone / "infra/compose/.env")
        command = [sys.executable, "-m", "unittest", "discover", "-s", "tests",
                   "-p", "test_*", "-f", "-v"]
        if args.stream_control:
            command = [sys.executable, "-m", "unittest", "discover", "-s", "tests",
                       "-p", "test_gate0_foundation*", "-k",
                       "test_every_tool_that_re_emits_captured_output_configures_its_own_stream",
                       "-v"]
        result = subprocess.run(command, cwd=clone, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", check=False)
        output = result.stdout + result.stderr
        headers = re.findall(r"^(?:FAIL|ERROR): test_[^\r\n]+", output, re.MULTILINE)
        marker = re.search(r"^(?:FAIL|ERROR): test_", output, re.MULTILINE)
        diagnostic = output[marker.start():][:12000] if marker else "no failure header"
        if scan_text(diagnostic):
            diagnostic = "OMITTED: canonical scanner refused the diagnostic text"
        clean = not git(clone, "status", "--porcelain")
    removed = not Path(temporary).exists()
    observed = result.returncode != 0 and bool(headers) and clean and removed
    write_json(report, {"schemaVersion": "1.0.0", "generatedAt": utc_now(),
                        "subjectCommit": SUBJECT, "tag": TAG,
                        "scope": "diagnostic only; fail-fast is not gate acceptance",
                        "command": command[1:], "exitCode": result.returncode,
                        "failureHeaders": headers, "diagnostic": diagnostic,
                        "gitStateUnchanged": clean, "temporaryCloneRemoved": removed,
                        "result": "FAILURE_REPRODUCED" if observed else "INCONCLUSIVE"})
    print(json.dumps({"diagnostic": "FAILURE_REPRODUCED" if observed else "INCONCLUSIVE",
                      "failureHeaders": headers}))
    return 0 if observed else 1


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
