#!/usr/bin/env python3
"""A regression test must fail on the code it corrects: run the new tests against the old code.

A disposable worktree is checked out at ``--base`` — the commit before the correction — and the
test files the correction adds or changes are copied over it, so the old implementation meets the
new tests. The same tests are then run in this working tree. The expected outcome is recorded, not
assumed: non-zero on the old code, zero here. A test that passes on both proves nothing about the
correction, which is exactly what this harness exists to catch.

    python old_code_regression.py --base 0e60b96 --overlay tests/test_gate3_sandbox.py \\
        --test tests.test_gate3_sandbox.PublishedHistoryTests --report ../OLD-CODE-M1-F-003.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now  # noqa: E402


def run(argv: list[str], cwd: Path, timeout: float = 3600) -> tuple[int, str]:
    completed = subprocess.run(argv, cwd=cwd, text=True, encoding="utf-8", errors="replace",
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                               timeout=timeout)
    return completed.returncode, completed.stdout


def summary(output: str) -> str:
    lines = [line for line in output.splitlines()
             if line.startswith(("Ran ", "OK", "FAILED", "ERROR:", "FAIL:"))]
    return " | ".join(lines[-12:])[:1500]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="the commit before the correction")
    parser.add_argument("--overlay", action="append", required=True,
                        help="a test file of the correction, copied over the old code")
    parser.add_argument("--test", action="append", required=True, help="a unittest identifier")
    parser.add_argument("--finding", required=True)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()

    scratch = Path(tempfile.mkdtemp(prefix="iacode-old-code-"))
    worktree = scratch / "old"
    try:
        code, output = run(["git", "worktree", "add", "--detach", "--quiet", str(worktree),
                            arguments.base], ROOT)
        if code != 0:
            raise SystemExit(f"the worktree could not be created: {output[-400:]}")
        for relative in arguments.overlay:
            shutil.copyfile(ROOT / relative, worktree / relative)
        old_code, old_output = run([sys.executable, "-m", "unittest", *arguments.test], worktree)
        new_code, new_output = run([sys.executable, "-m", "unittest", *arguments.test], ROOT)
    finally:
        run(["git", "worktree", "remove", "--force", str(worktree)], ROOT)
        run(["git", "worktree", "prune"], ROOT)
        shutil.rmtree(scratch, ignore_errors=True)

    base = run(["git", "rev-parse", arguments.base], ROOT)[1].strip()
    report = {
        "schemaVersion": "1.0.0", "artifact": "OLD-CODE-REGRESSION", "finding": arguments.finding,
        "checkpoint": CHECKPOINT.name, "generatedAt": utc_now(), "base": base,
        "overlay": arguments.overlay, "tests": arguments.test,
        "oldCode": {"exitCode": old_code, "summary": summary(old_output)},
        "correctedCode": {"exitCode": new_code, "summary": summary(new_output)},
        "result": "PASS" if old_code != 0 and new_code == 0 else "FAIL",
    }
    arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    print(f"old code exit {old_code}: {summary(old_output)[:300]}")
    print(f"corrected code exit {new_code}: {summary(new_output)[:300]}")
    print(f"OLD_CODE_REGRESSION={report['result']} finding={arguments.finding}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
