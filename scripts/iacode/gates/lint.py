#!/usr/bin/env python3
"""Mandatory gate: static analysis of the Foundation source.

Ruff over every Python source the Gate owns, and the TypeScript compiler plus Prettier over the
frontend. Both run inside the images that own the toolchain, so the result does not depend on what
a contributor happens to have installed — and the frontend toolchain needs Node 22, which the
repository's own environment does not have.

The working tree is mounted read-only rather than taken from an image layer, so the gate judges
what is on disk now instead of whatever the last image build captured.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import REPOSITORY_ROOT, log, main_guard, require_docker
from gates.web_tests import BUILDER_IMAGE, build_toolchain

API_IMAGE = "iacode/api:0.1.0"

# What ruff is pointed at. `ruff.toml` excludes the sealed development-ledger tooling; naming the
# roots here as well keeps the gate from walking the whole tree, `var/` and `node_modules`
# included.
PYTHON_ROOTS = (
    "apps/api/src",
    "apps/api/tests",
    "apps/api/migrations",
    "services/orchestrator/src",
    "packages",
    "scripts/iacode",
    "infra/tests",
)


def ruff() -> int:
    completed = subprocess.run(
        ["docker", "run", "--rm",
         # The image runs as a non-root user with a read-only /app, so ruff cannot write its cache
         # there. Sending it to a writable path keeps the run cached without loosening the image.
         "--env", "RUFF_CACHE_DIR=/tmp/ruff-cache",
         "--volume", f"{REPOSITORY_ROOT}:/repo:ro",
         "--workdir", "/repo",
         API_IMAGE, "ruff", "check", *PYTHON_ROOTS],
        cwd=str(REPOSITORY_ROOT), text=True, check=False)
    return completed.returncode


def frontend() -> int:
    build_toolchain()
    completed = subprocess.run(
        ["docker", "run", "--rm", "--workdir", "/build", BUILDER_IMAGE, "npm", "run", "lint"],
        cwd=str(REPOSITORY_ROOT), text=True, check=False)
    return completed.returncode


def main() -> int:
    require_docker()
    failures: list[str] = []

    if ruff() != 0:
        failures.append("python")
    if frontend() != 0:
        failures.append("frontend")

    log(f"LINT={'PASS' if not failures else 'FAIL'}"
        + (f" failing={','.join(failures)}" if failures else ""))
    return 0 if not failures else 1


if __name__ == "__main__":
    main_guard(main)
