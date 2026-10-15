#!/usr/bin/env python3
"""Rebuild and exercise the real sandbox service output boundary using its deterministic suite."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from compose import build_service, compose


def main() -> int:
    build_service("sandbox")
    result = compose(
        "run", "--rm", "--no-deps", "--entrypoint", "", "sandbox",
        "python", "-m", "pytest", "/app/sandbox_tests/test_sandbox_service.py",
        "-k", "canonical_secret_output", "-p", "no:cacheprovider", "--no-header", "--tb=short",
        capture=False,
    )
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
