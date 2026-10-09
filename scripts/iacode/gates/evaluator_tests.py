#!/usr/bin/env python3
"""Mandatory gate: build the Quality Engine image, then run its suite inside it."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import build_service, compose, log, main_guard


def main() -> int:
    build_service("evaluator")
    result = compose(
        "run",
        "--rm",
        "--no-deps",
        "--entrypoint",
        "",
        "evaluator",
        "python",
        "-m",
        "pytest",
        "/app/evaluator_tests",
        "-m",
        "not integration",
        "-p",
        "no:cacheprovider",
        "--no-header",
        capture=False,
    )
    log(f"EVALUATOR_TESTS={'PASS' if result.ok else 'FAIL'}")
    return result.exit_code


if __name__ == "__main__":
    main_guard(main)
