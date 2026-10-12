#!/usr/bin/env python3
"""Replay the canonical internal Red Team using checkpoint-owned verifier reports."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
COMPOSE = ROOT / "infra" / "compose"
PROJECT = "iacode-g4-cp0008-assurance"
NAMES = (
    "quality-recovery.json",
    "quality-cancellation.json",
    "quality-timeout.json",
    "sandbox-tool-result-origin.json",
)
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from gate4_red_team import render_markdown  # noqa: E402
from ledger_common import scope_fingerprint, use_utf8_stdout  # noqa: E402


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )


def compose_down(environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "docker", "compose", "--project-directory", str(COMPOSE),
            "--file", str(COMPOSE / "docker-compose.yml"),
            "--env-file", str(COMPOSE / ".env"),
            "--project-name", PROJECT, "down", "--volumes", "--remove-orphans",
        ],
        cwd=ROOT, env=environment, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=1800,
    )


def main() -> int:
    use_utf8_stdout()
    for name in NAMES:
        source = CHECKPOINT / "runtime-reports" / name
        if not source.is_file():
            raise RuntimeError(f"missing checkpoint-owned verifier report: {source}")
        destination = ROOT / "var" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    independent = json.loads(
        (CHECKPOINT / "GATE-4-INDEPENDENT-RED-TEAM.json").read_text(encoding="utf-8")
    )
    seed = {
        **independent,
        "schemaVersion": "1.1.0",
        "checkpoint": CHECKPOINT.name,
        "targetFingerprint": scope_fingerprint(ROOT),
        "source": (
            "Internal replay seeded from this audit session's independent A-T evidence; this "
            "same-session replay is internal quality assurance, not independent validation."
        ),
        "mandatoryTotal": independent.get("total"),
        "mandatoryDefended": independent.get("defended"),
    }
    write_json(CHECKPOINT / "M2-INTERNAL-RED-TEAM.json", seed)
    (CHECKPOINT / "RED-TEAM-REPORT.md").write_text(
        render_markdown(seed), encoding="utf-8", newline="\n"
    )
    environment = dict(os.environ)
    environment["COMPOSE_PROJECT_NAME"] = PROJECT
    command = [
        sys.executable,
        str(ROOT / "scripts" / "development-ledger" / "gate4_red_team.py"),
        "--checkpoint", str(CHECKPOINT.relative_to(ROOT)), "--write",
    ]
    try:
        completed = subprocess.run(
            command, cwd=ROOT, env=environment, text=True, encoding="utf-8",
            errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False, timeout=3600,
        )
        print(completed.stdout, end="")
        return completed.returncode
    finally:
        cleaned = compose_down(environment)
        print(cleaned.stdout, end="")


if __name__ == "__main__":
    raise SystemExit(main())
