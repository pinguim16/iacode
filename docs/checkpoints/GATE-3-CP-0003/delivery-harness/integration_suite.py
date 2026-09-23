#!/usr/bin/env python3
"""Run the API image's pytest suite against the running stack, exactly as the verification does.

The verification's ``integration`` stage runs this command inside the API image with the stack's
database, Temporal and bucket reachable. It is the only place the store's refusals, the migration
chain and the executor backfill meet a real PostgreSQL, so a targeted check of a change to any of
them runs it here too. ``--select`` narrows the run to test files or node identifiers.

    python integration_suite.py --select tests/integration/test_agent_runtime_persistence.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
COMPOSE = ROOT / "infra" / "compose"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--select", action="append", default=[])
    arguments = parser.parse_args()
    argv = ["docker", "compose", "--project-directory", str(COMPOSE),
            "--file", str(COMPOSE / "docker-compose.yml"), "--env-file", str(COMPOSE / ".env"),
            "run", "--rm", "--entrypoint", "", "api", "python", "-m", "pytest",
            *(arguments.select or ["tests"]), "-p", "no:cacheprovider", "--no-header"]
    completed = subprocess.run(argv, cwd=ROOT, check=False)
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
