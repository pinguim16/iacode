#!/usr/bin/env python3
"""Select the engineering lessons that constrain a Gate, before the Gate starts.

The preflight is mandatory. It reads the memory, decides which lessons apply to the declared gate,
scope, technologies and modules, and writes ``LESSON-PREFLIGHT.json`` and ``LESSON-PREFLIGHT.md``
into the checkpoint. Every applicable lesson produces a derived requirement, so a lesson becomes a
requirement, the requirement carries evidence, and the evidence is validated. A lesson that is
``SUPERSEDED`` or ``RETIRED`` produces no requirement.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, find_root, load_json, resolve_latest, validate_schema
from lessons import build_preflight


def render_markdown(preflight: dict[str, Any]) -> str:
    lines = [
        "# Lesson Preflight",
        "",
        f"- Gate: `{preflight['gate']}`",
        f"- Scope: `{preflight['scope']}`",
        f"- Technologies: {', '.join('`%s`' % item for item in preflight['technologies']) or '_none declared_'}",
        f"- Modules: {', '.join('`%s`' % item for item in preflight['modules']) or '_none declared_'}",
        f"- Generated: `{preflight['generatedAt']}`",
        f"- Lessons considered: {preflight['lessonsConsidered']}",
        f"- Lessons applicable: {preflight['lessonsApplicable']}",
        "",
        "Every applicable lesson below is a requirement of this Gate. The derived identifiers must",
        "appear in `REQUIREMENTS-MATRIX.json`, and the Delivery Completeness Validator fails the",
        "delivery when one is absent.",
        "",
    ]
    if preflight["applicable"]:
        lines += [
            "| Lesson | Status | Severity | Derived requirement | Required check |",
            "|---|---|---|---|---|",
        ]
        for item in preflight["applicable"]:
            lines.append("| `%s` %s | `%s` | %s | `%s` | %s |" % (
                item["lessonId"], item.get("title", ""), item["status"], item["severity"],
                item["derivedRequirementId"], item["requiredCheck"]))
        lines += ["", "## Why each lesson applies", ""]
        for item in preflight["applicable"]:
            lines += [
                "### %s — %s" % (item["lessonId"], item.get("title", "")),
                "",
                "- Reason: %s" % item["reasonApplicable"],
                "- Required check: %s" % item["requiredCheck"],
                "- Required evidence: %s" % item["requiredEvidence"],
                "- Derived requirement: `%s`" % item["derivedRequirementId"],
                "",
            ]
    else:
        lines.append("No lesson in the memory constrains this Gate.")
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--technology", action="append", default=[])
    parser.add_argument("--module", action="append", default=[])
    parser.add_argument("--write", action="store_true", help="write LESSON-PREFLIGHT.json and .md")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    preflight = build_preflight(root, args.gate, args.scope, args.technology, args.module)

    schema_path = root / ".iacode" / "schemas" / "lesson-preflight.schema.json"
    if schema_path.is_file():
        errors = validate_schema(preflight, load_json(schema_path))
        if errors:
            print("LESSON_PREFLIGHT_INVALID")
            for error in errors:
                print(f"- {error}")
            return 2

    if args.write:
        (checkpoint / "LESSON-PREFLIGHT.json").write_text(
            json.dumps(preflight, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        (checkpoint / "LESSON-PREFLIGHT.md").write_text(
            render_markdown(preflight), encoding="utf-8", newline="\n")

    print("LESSON_PREFLIGHT gate=%s scope=%s considered=%d applicable=%d derived=%d" % (
        preflight["gate"], preflight["scope"], preflight["lessonsConsidered"],
        preflight["lessonsApplicable"], len(preflight["derivedRequirements"])))
    for item in preflight["applicable"]:
        print(f"- {item['lessonId']} -> {item['derivedRequirementId']}: {item['requiredCheck']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
