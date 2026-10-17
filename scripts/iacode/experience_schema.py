#!/usr/bin/env python3
"""Derive/compare the closed JSON schema using the owning pinned API image, never host imports."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import REPOSITORY_ROOT, StackError, build_service, main_guard, project_image


def schema(*, build: bool = True) -> dict:
    if build:
        build_service("api")
    code = (
        "import json; from iacode_contracts.experience import ExperienceDocument; "
        "print(json.dumps(ExperienceDocument.model_json_schema(mode='serialization')))"
    )
    result = subprocess.run(
        ["docker", "run", "--rm", project_image("api"), "python", "-c", code],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode:
        raise StackError("experience schema derivation failed in its owning production image")
    value = json.loads(result.stdout)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://iacode.local/schemas/experience.schema.json",
        **value,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    options = parser.parse_args()
    value = schema()
    path = REPOSITORY_ROOT / ".iacode/schemas/experience.schema.json"
    if options.write:
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    if json.loads(path.read_bytes()) != value:
        raise StackError("the versioned experience schema differs from the actual wire contract")
    print("EXPERIENCE_SCHEMA=PASS (actual pinned image; closed versioned contract)")
    return 0


if __name__ == "__main__":
    main_guard(main)
