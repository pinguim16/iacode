#!/usr/bin/env python3
"""Validate the IACode engineering memory and optionally re-render its index.

Exit code 0 means the memory is valid. Any nonzero exit means it is not. The checks are the ones a
reviewer would otherwise have to perform by hand: schema conformance, unique identifiers, valid
status, provenance, training policy, evidence, preventive evidence behind every GUARDED lesson,
absence of secrets, and recurrence consistency.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ledger_common import LedgerError, find_root
from lessons import INDEX_FILE, load_lessons, memory_root, render_index, validate_lessons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--render-index", action="store_true",
                        help="rewrite LESSONS.md from lessons.jsonl after a successful validation")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    errors = validate_lessons(root)
    if errors:
        print("LESSONS_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    lessons = load_lessons(root)
    if args.render_index:
        (memory_root(root) / INDEX_FILE).write_text(render_index(lessons), encoding="utf-8", newline="\n")

    guarded = sum(1 for lesson in lessons if lesson.get("status") == "GUARDED")
    active = sum(1 for lesson in lessons if lesson.get("status") in ("OBSERVED", "CONFIRMED", "GUARDED"))
    print(f"LESSONS_VALID total={len(lessons)} active={active} guarded={guarded}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
