#!/usr/bin/env python3
"""Validate one published checkpoint tag from a fresh Git transport clone."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout


def run(arguments: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--source", default="https://github.com/pinguim16/iacode.git")
    parser.add_argument(
        "--validator",
        type=Path,
        help="validator from the author checkout; omit to execute the validator carried by the tag",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="iacode-checkpoint-transport-") as temporary:
        parent = Path(temporary)
        clone = parent / "repository"
        cloned = run(["git", "clone", "--quiet", "--no-local", args.source, str(clone)], parent)
        checked = (
            run(["git", "checkout", "--quiet", "--detach", args.tag], clone)
            if cloned.returncode == 0
            else cloned
        )
        observed = (
            run(["git", "rev-parse", "HEAD"], clone)
            if checked.returncode == 0
            else checked
        )
        validator = args.validator.resolve() if args.validator else Path(
            "scripts/development-ledger/validate_checkpoint.py")
        validator_arguments = [sys.executable, str(validator)]
        if args.validator:
            validator_arguments += ["--root", str(clone)]
        validated = (
            run(validator_arguments, clone)
            if observed.returncode == 0 and observed.stdout.strip() == args.expected_commit
            else observed
        )

    passed = (
        cloned.returncode == 0
        and checked.returncode == 0
        and observed.returncode == 0
        and observed.stdout.strip() == args.expected_commit
        and validated.returncode == 0
        and "CHECKPOINT_VALID" in validated.stdout
    )
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "PUBLISHED-CHECKPOINT-TRANSPORT-VALIDATION",
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source": args.source,
        "tag": args.tag,
        "expectedCommit": args.expected_commit,
        "observedCommit": observed.stdout.strip(),
        "cloneExitCode": cloned.returncode,
        "checkoutExitCode": checked.returncode,
        "validationExitCode": validated.returncode,
        "validationOutput": validated.stdout.strip(),
        "validator": str(args.validator) if args.validator else "tag-carried validator",
        "result": "PASS" if passed else "FAIL",
    }
    args.report.resolve().write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"PUBLISHED_CHECKPOINT_TRANSPORT_VALIDATION={report['result']} "
        f"tag={args.tag} validation_exit={validated.returncode}"
    )
    if validated.stdout.strip():
        print(validated.stdout.strip())
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
