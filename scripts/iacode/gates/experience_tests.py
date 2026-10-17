#!/usr/bin/env python3
"""Build the actual API/library image, then execute every pure Experience Store case."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import build_service, compose, log, main_guard
from experience_schema import schema


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
        "/app/experience_tests",
        "-p",
        "no:cacheprovider",
        "--no-header",
        capture=False,
    )
    declared = Path(__file__).resolve().parents[3] / ".iacode/schemas/experience.schema.json"
    schema_matches = json.loads(declared.read_bytes()) == schema(build=False)
    ok = result.ok and schema_matches
    log(f"EXPERIENCE_TESTS={'PASS' if ok else 'FAIL'} schemaMatches={schema_matches}")
    return result.exit_code or (0 if schema_matches else 1)


if __name__ == "__main__":
    main_guard(main)
