#!/usr/bin/env python3
"""Attack the schema 3.3 command-input transport boundary without mutating the subject."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0007"
TAG = f"iacode-checkpoints/{SUBJECT}"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import command_input_transport_error, use_utf8_stdout  # noqa: E402


def run(arguments: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        arguments, cwd=cwd, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    return {"exitCode": completed.returncode, "output": completed.stdout.strip()}


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    direct = {
        "gitMetadata": command_input_transport_error(ROOT, ".git/HEAD"),
        "absoluteTemporary": command_input_transport_error(
            ROOT, str(Path(tempfile.gettempdir()) / "iacode-local-only.txt")
        ),
        "ignoredOutput": command_input_transport_error(ROOT, "var/local-only.txt"),
    }
    with tempfile.TemporaryDirectory(prefix="iacode-g4-untracked-attack-") as temporary:
        parent = Path(temporary)
        clone = parent / "repository"
        clone_result = run([
            "git", "clone", "--quiet", "--no-local",
            "https://github.com/pinguim16/iacode.git", str(clone),
        ], parent)
        checkout = run(["git", "checkout", "--quiet", "--detach", TAG], clone)
        local_only = clone / "audit-untracked-input.txt"
        local_only.write_text("disposable untracked input\n", encoding="utf-8", newline="\n")
        classification = command_input_transport_error(clone, local_only.name)
        recorder = run([
            sys.executable,
            "scripts/development-ledger/record_command.py",
            "--checkpoint", f"docs/checkpoints/{SUBJECT}",
            "--purpose", "Disposable attack: an untracked input must never yield a portable sealed checkpoint.",
            "--input", local_only.name,
            "--", "python", "-c", "pass",
        ], clone)
        local_only.unlink()
        validation = run([
            sys.executable, "scripts/development-ledger/validate_checkpoint.py"
        ], clone)
        untracked = {
            "classification": (
                "ELIGIBLE_ONLY_IF_COMMITTED_BEFORE_SEALING"
                if classification is None else classification
            ),
            "recorderExitCode": recorder["exitCode"],
            "recorderAcceptedInProgress": recorder["exitCode"] == 0,
            "validationExitCodeAfterLocalFileRemoval": validation["exitCode"],
            "validationRefusedMissingInput": (
                validation["exitCode"] != 0
                and "recorded input does not exist: audit-untracked-input.txt" in validation["output"]
            ),
            "validationTail": "\n".join(validation["output"].splitlines()[-20:]),
        }

    checks = {
        "gitMetadataRefused": direct["gitMetadata"] == "Git metadata is never carried in a checkout",
        "absoluteTemporaryRefused": direct["absoluteTemporary"] == "absolute paths are outside the repository transport",
        "ignoredOutputRefused": direct["ignoredOutput"] == "the path is ignored and Git transport does not carry it",
        "untrackedCannotRemainLocalOnly": (
            clone_result["exitCode"] == 0
            and checkout["exitCode"] == 0
            and untracked["classification"] == "ELIGIBLE_ONLY_IF_COMMITTED_BEFORE_SEALING"
            and untracked["recorderAcceptedInProgress"]
            and untracked["validationRefusedMissingInput"]
        ),
    }
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "COMMAND-INPUT-TRANSPORT-ATTACKS",
        "checkpoint": CHECKPOINT.name,
        "subjectCheckpoint": SUBJECT,
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "directRefusals": direct,
        "untrackedLifecycle": untracked,
        "checks": checks,
        "result": "PASS" if all(checks.values()) else "FAIL",
        "interpretation": (
            "Git metadata, absolute temporary paths and ignored outputs are refused before execution. "
            "A non-ignored untracked source is provisionally eligible only because the checkpoint must "
            "commit it before sealing; removing it proves the validator refuses a local-only record."
        ),
    }
    arguments.report.resolve().write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(
        f"TRANSPORT_ATTACKS={report['result']} "
        f"direct={sum(1 for key in ('gitMetadataRefused','absoluteTemporaryRefused','ignoredOutputRefused') if checks[key])}/3 "
        f"untracked={'REFUSED_AT_VALIDATION' if checks['untrackedCannotRemainLocalOnly'] else 'ESCAPED'}"
    )
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
