#!/usr/bin/env python3
"""Build the current evaluator image and execute the independent G4-X7 probe."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
COMPOSE = ROOT / "infra" / "compose"
SOURCE_PROBE = ROOT / "docs" / "checkpoints" / "GATE-4-CP-0006" / "audit-harness" / "g4x7_probe.py"
PROJECT = "iacode-g4-cp0008-probe"
SUBJECT = "GATE-4-CP-0007"
SUBJECT_COMMIT = "e21d30fde473f302d0f8f60b59acf008fa52e250"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def compose(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "docker", "compose", "--project-directory", str(COMPOSE),
            "--file", str(COMPOSE / "docker-compose.yml"),
            "--env-file", str(COMPOSE / ".env"),
            "--project-name", PROJECT, *arguments,
        ],
        cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=3600,
    )


def main() -> int:
    use_utf8_stdout()
    report_path = CHECKPOINT / "G4-X7-INDEPENDENT-PROBE.json"
    result = 1
    try:
        built = compose("build", "evaluator")
        print(built.stdout, end="")
        if built.returncode != 0:
            return built.returncode
        executed = compose(
            "run", "--rm", "--no-deps", "--entrypoint", "",
            "--volume", f"{SOURCE_PROBE.as_posix()}:/audit/g4x7_probe.py:ro",
            "--volume", f"{CHECKPOINT.as_posix()}:/evidence",
            "evaluator", "python", "/audit/g4x7_probe.py",
            "--report", "/evidence/G4-X7-INDEPENDENT-PROBE.json",
        )
        print(executed.stdout, end="")
        result = executed.returncode
        if report_path.is_file():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report.update({
                "checkpoint": CHECKPOINT.name,
                "subjectCheckpoint": SUBJECT,
                "subjectCommit": SUBJECT_COMMIT,
                "sourceProbe": "docs/checkpoints/GATE-4-CP-0006/audit-harness/g4x7_probe.py",
            })
            report_path.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8", newline="\n",
            )
        return result
    finally:
        cleaned = compose("down", "--volumes", "--remove-orphans")
        print(cleaned.stdout, end="")


if __name__ == "__main__":
    raise SystemExit(main())
