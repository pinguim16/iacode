#!/usr/bin/env python3
"""Run the canonical milestone mirror read-only against the sealed Gate 4 subject."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0005"
COMMIT = "c631270e49c095a9777825c0bc18818694c07ffb"
TAG = f"iacode-checkpoints/{SUBJECT}"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402
from m0_mirror_audit import run_audit  # noqa: E402


def execute(arguments: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="iacode-g4-subject-mirror-") as temporary:
        clone = Path(temporary) / "repository"
        cloned = execute(
            ["git", "clone", "--quiet", "--no-local", "https://github.com/pinguim16/iacode.git", str(clone)],
            Path(temporary),
        )
        checked = execute(["git", "checkout", "--quiet", "--detach", TAG], clone) if cloned.returncode == 0 else cloned
        observed = execute(["git", "rev-parse", "HEAD"], clone) if checked.returncode == 0 else checked
        mirror_report = run_audit(
            clone, clone / "docs" / "checkpoints" / SUBJECT, False
        ) if observed.returncode == 0 and observed.stdout.strip() == COMMIT else {}
        history = next(
            (item for item in mirror_report.get("checks", []) if item.get("id") == "MIR-016"),
            {},
        )
        passed = (
            cloned.returncode == 0
            and checked.returncode == 0
            and observed.returncode == 0
            and observed.stdout.strip() == COMMIT
            and mirror_report.get("result") == "PASS"
            and history.get("result") == "PASS"
            and "sealed checkpoints validate" in str(history.get("observed"))
        )
        report = {
            "schemaVersion": "1.0.0",
            "artifact": "GATE-4-SUBJECT-MIRROR-AUDIT",
            "checkpoint": CHECKPOINT.name,
            "subjectCheckpoint": SUBJECT,
            "subjectCommit": COMMIT,
            "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "cloneExitCode": cloned.returncode,
            "checkoutExitCode": checked.returncode,
            "observedCommit": observed.stdout.strip(),
            "mirror": mirror_report,
            "result": "PASS" if passed else "FAIL",
        }
        arguments.report.resolve().write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(
        f"SUBJECT_MIRROR_AUDIT={report['result']} "
        f"passed={mirror_report.get('passed')}/{mirror_report.get('total')} "
        f"history={history.get('observed')}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
