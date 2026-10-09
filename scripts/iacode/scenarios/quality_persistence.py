#!/usr/bin/env python3
"""Verify Quality Engine migration, PostgreSQL lifecycle and MinIO evidence together."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import build_service, compose, log, main_guard


def main() -> int:
    build_service("api")
    build_service("evaluator")
    migration = compose(
        "run",
        "--rm",
        "--no-deps",
        "--entrypoint",
        "",
        "api",
        "python",
        "-m",
        "pytest",
        "/app/tests/integration/test_migrations.py",
        "-p",
        "no:cacheprovider",
        "--no-header",
        capture=False,
    )
    if not migration.ok:
        log("QUALITY_PERSISTENCE=FAIL stage=migration")
        return migration.exit_code
    integration = compose(
        "run",
        "--rm",
        "--no-deps",
        "--entrypoint",
        "",
        "evaluator",
        "python",
        "-m",
        "pytest",
        "/app/evaluator_tests/integration",
        "-m",
        "integration",
        "-p",
        "no:cacheprovider",
        "--no-header",
        capture=False,
    )
    log(f"QUALITY_PERSISTENCE={'PASS' if integration.ok else 'FAIL'}")
    return integration.exit_code


if __name__ == "__main__":
    main_guard(main)
