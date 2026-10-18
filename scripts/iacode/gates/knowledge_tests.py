#!/usr/bin/env python3
"""Rebuild the actual knowledge/API image, execute its whole domain suite and compare schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import build_service, compose, log, main_guard
from knowledge_schema import schema


def main() -> int:
    build_service("api")
    result = compose(
        "run",
        "--rm",
        "--no-deps",
        "--entrypoint",
        "",
        "api",
        "python",
        "-m",
        "pytest",
        "/app/knowledge_tests",
        "-p",
        "no:cacheprovider",
        "--no-header",
        capture=False,
    )
    declared = Path(__file__).resolve().parents[3] / ".iacode/schemas/knowledge.schema.json"
    matches = declared.is_file() and json.loads(declared.read_bytes()) == schema(build=False)
    log(f"KNOWLEDGE_TESTS={'PASS' if result.ok and matches else 'FAIL'} schemaMatches={matches}")
    return result.exit_code or (0 if matches else 1)


if __name__ == "__main__":
    main_guard(main)
