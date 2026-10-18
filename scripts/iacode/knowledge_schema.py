#!/usr/bin/env python3
"""Derive the actual closed knowledge contract schema in its owning pinned API image."""

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
        "import json; from pydantic import TypeAdapter; "
        "from iacode_contracts import knowledge as k; "
        "print(json.dumps(TypeAdapter(k.KnowledgeDocument | k.KnowledgePolicy | "
        "k.CuratedArtifact | k.SourceRegistry | k.SourceGrant | k.IngestKnowledge | "
        "k.SearchKnowledge | k.KnowledgeCitation | "
        "k.KnowledgeHit).json_schema(mode='serialization')))"
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
        raise StackError("knowledge schema derivation failed in its owning image")
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://iacode.local/schemas/knowledge.schema.json",
        **json.loads(result.stdout),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    options = parser.parse_args()
    value = schema()
    path = REPOSITORY_ROOT / ".iacode/schemas/knowledge.schema.json"
    if options.write:
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    if not path.is_file() or json.loads(path.read_bytes()) != value:
        raise StackError("versioned knowledge schema differs from its actual wire contract")
    print("KNOWLEDGE_SCHEMA=PASS (owning pinned image; closed versioned contract)")
    return 0


if __name__ == "__main__":
    main_guard(main)
