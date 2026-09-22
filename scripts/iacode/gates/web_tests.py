#!/usr/bin/env python3
"""Mandatory gate: the Foundation frontend suite and its production build.

Both in one gate, because a suite that passes against code that does not build proves nothing. The
build runs first: a type error surfaces there with a better message than it does through the test
runner.

Everything happens inside the frontend toolchain image, so the gate does not depend on the Node
version a contributor happens to have. The repository's own Node is 18 and the toolchain needs 22.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import REPOSITORY_ROOT, StackError, log, main_guard, require_docker

BUILDER_IMAGE = "iacode/web-toolchain:0.1.0"


def build_toolchain() -> None:
    """Build the frontend builder stage once, so `npm ci` is cached between gate runs."""
    completed = subprocess.run(
        ["docker", "build", "--target", "builder", "--tag", BUILDER_IMAGE,
         "--file", "apps/web/Dockerfile", "."],
        cwd=str(REPOSITORY_ROOT), text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if completed.returncode != 0:
        raise StackError(
            "the frontend toolchain image could not be built:\n"
            + completed.stdout.strip()[-1500:])


def run(*command: str) -> int:
    completed = subprocess.run(
        ["docker", "run", "--rm", "--workdir", "/build", BUILDER_IMAGE, *command],
        cwd=str(REPOSITORY_ROOT), text=True, check=False)
    return completed.returncode


def main() -> int:
    require_docker()
    build_toolchain()

    for label, command in (
        ("build", ("npm", "run", "build")),
        # ``--watch=false`` explicitly: the runner defaults to watch mode on a TTY,
        # and a gate that waits for a file change never finishes.
        ("tests", ("npm", "test", "--", "--watch=false")),
    ):
        code = run(*command)
        log(f"WEB_{label.upper()}={'PASS' if code == 0 else 'FAIL'}")
        if code != 0:
            return code
    log("WEB_TESTS=PASS")
    return 0


if __name__ == "__main__":
    main_guard(main)
