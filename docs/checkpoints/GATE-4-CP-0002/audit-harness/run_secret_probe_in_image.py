#!/usr/bin/env python3
"""Execute the audit-only secret evidence probe inside the delivered evaluator image."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]


def main() -> int:
    command = [
        "docker",
        "compose",
        "--env-file",
        "infra/compose/.env",
        "-f",
        "infra/compose/docker-compose.yml",
        "run",
        "--rm",
        "--no-deps",
        "-v",
        "./docs/checkpoints/GATE-4-CP-0002:/audit",
        "evaluator",
        "python",
        "/audit/audit-harness/secret_evidence_probe.py",
        "--report",
        "/audit/SECRET-EVIDENCE-PROBE.json",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
