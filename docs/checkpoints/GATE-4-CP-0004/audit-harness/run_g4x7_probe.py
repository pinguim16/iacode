#!/usr/bin/env python3
"""Build the evaluator image and execute the audit-owned G4-X7 probe inside it."""

from __future__ import annotations

import subprocess
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
COMPOSE = ROOT / "infra" / "compose"


def compose(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "docker", "compose",
            "--project-directory", str(COMPOSE),
            "--file", str(COMPOSE / "docker-compose.yml"),
            "--env-file", str(COMPOSE / ".env"),
            *arguments,
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=3600,
    )


def main() -> int:
    built = compose("build", "evaluator")
    print(built.stdout, end="")
    if built.returncode != 0:
        return built.returncode
    executed = compose(
        "run", "--rm", "--no-deps", "--entrypoint", "",
        "--volume", f"{CHECKPOINT.as_posix()}:/audit",
        "evaluator", "python", "/audit/audit-harness/g4x7_probe.py",
        "--report", "/audit/G4-X7-INDEPENDENT-PROBE.json",
    )
    print(executed.stdout, end="")
    return executed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
