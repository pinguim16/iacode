#!/usr/bin/env python3
"""Execute the dedicated R-G2-011 terminal SSE multi-page regression in the API image."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
COMPOSE = ROOT / "infra" / "compose"


def main() -> int:
    command = [
        "docker", "compose", "--project-directory", str(COMPOSE),
        "--file", str(COMPOSE / "docker-compose.yml"),
        "--env-file", str(COMPOSE / ".env"),
        "run", "--rm", "--no-deps", "--entrypoint", "", "api",
        "python", "-m", "pytest",
        "tests/unit/test_agent_runtime_api.py::test_a_terminal_stream_drains_every_page_after_the_cursor",
        "-p", "no:cacheprovider", "--no-header", "-q",
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8",
                               errors="replace", capture_output=True, check=False, timeout=900)
    tail = "\n".join((completed.stdout + completed.stderr).strip().splitlines()[-12:])
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "SSE-TERMINAL-DRAIN",
        "checkpoint": CHECKPOINT.name,
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "requirement": "R-G2-011 / AM-23",
        "test": "test_a_terminal_stream_drains_every_page_after_the_cursor",
        "command": " ".join(command),
        "exitCode": completed.returncode,
        "observed": tail,
        "result": "PASS" if completed.returncode == 0 else "FAIL",
    }
    (CHECKPOINT / "SSE-TERMINAL-DRAIN.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"SSE_TERMINAL_DRAIN={report['result']} exit={completed.returncode}")
    if tail:
        print(tail)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
