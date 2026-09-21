#!/usr/bin/env python3
"""Resolve every evidence reference of a checkpoint's requirements matrix, independently.

``file:`` must exist in the repository, ``checkpoint:`` inside the checkpoint that declares it,
``test:`` must be a test identifier the suite actually discovers, and ``command:`` must be a
record identifier present in that checkpoint's ``COMMANDS.jsonl``. Nothing here calls
``delivery_assurance.py``: agreeing with the delivery means two readers resolved the same
references.

    python resolve_evidence.py --checkpoint SETUP-00-CP-0012
"""

from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path
from typing import Any

HARNESS = Path(__file__).resolve().parent
ROOT = HARNESS.parents[3]

EVIDENCE_KEYS = (
    "implementationEvidence", "testEvidence", "documentationEvidence",
    "validationEvidence", "negativeTestEvidence",
)


def suite_identifiers() -> set[str]:
    """Every discoverable test, by full id, by ``Class.method``, by class and by method name.

    The four forms are the ones the repository actually uses. The matrix documents
    ``test:<TestClass.test_name>``, and sealed rows also carry a bare method name and a bare class
    name; all of them name cases that must exist, so all of them are resolved here rather than
    reported as unresolved for being less precise than the documented form.

    This resolver discovers the suite at runtime instead of parsing it, so agreeing with the
    delivery means a loader and a parser found the same cases.
    """
    identifiers: set[str] = set()

    def walk(suite: Any) -> None:
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                walk(item)
            elif isinstance(item, unittest.TestCase):
                full = item.id()
                identifiers.add(full)
                parts = full.split(".")
                if len(parts) >= 2:
                    identifiers.add(".".join(parts[-2:]))
                    identifiers.add(parts[-2])
                    identifiers.add(parts[-1])

    tests = ROOT / "tests"
    walk(unittest.defaultTestLoader.discover(str(tests), top_level_dir=str(tests)))
    return identifiers


def command_ids(checkpoint: Path) -> set[str]:
    path = checkpoint / "COMMANDS.jsonl"
    if not path.is_file():
        return set()
    found: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            found.add(str(json.loads(line).get("id")))
    return found


def resolve(checkpoint_name: str) -> dict:
    checkpoint = ROOT / "docs" / "checkpoints" / checkpoint_name
    matrix = json.loads((checkpoint / "REQUIREMENTS-MATRIX.json").read_text(encoding="utf-8"))
    tests = suite_identifiers()
    commands = command_ids(checkpoint)

    total = 0
    unresolved: list[str] = []
    by_kind: dict[str, int] = {}
    rows_without_evidence: list[str] = []
    for row in matrix.get("requirements") or []:
        references = [item for key in EVIDENCE_KEYS for item in (row.get(key) or [])]
        if row.get("status") == "COMPLETE" and not references:
            rows_without_evidence.append(str(row.get("id")))
        for reference in references:
            total += 1
            kind, _, value = str(reference).partition(":")
            by_kind[kind] = by_kind.get(kind, 0) + 1
            ok = False
            if kind == "file":
                ok = (ROOT / value).exists()
            elif kind == "checkpoint":
                ok = (checkpoint / value).exists()
            elif kind == "test":
                ok = value in tests
            elif kind == "command":
                ok = value in commands
            if not ok:
                unresolved.append(f"{row.get('id')}:{reference}")

    statuses: dict[str, int] = {}
    for row in matrix.get("requirements") or []:
        statuses[str(row.get("status"))] = statuses.get(str(row.get("status")), 0) + 1

    return {
        "checkpoint": checkpoint_name,
        "rows": len(matrix.get("requirements") or []),
        "statuses": statuses,
        "evidenceReferences": total,
        "byKind": by_kind,
        "unresolved": unresolved,
        "rowsWithoutEvidence": rows_without_evidence,
        "evidenceCoveragePercent": (
            round((total - len(unresolved)) / total * 100, 2) if total else 0.0),
        "allResolve": not unresolved and not rows_without_evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    result = resolve(args.checkpoint)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8", newline="\n")
    print(
        f"EVIDENCE checkpoint={result['checkpoint']} rows={result['rows']} "
        f"references={result['evidenceReferences']} unresolved={len(result['unresolved'])} "
        f"rowsWithoutEvidence={len(result['rowsWithoutEvidence'])} "
        f"coverage={result['evidenceCoveragePercent']}%")
    print("  statuses: " + ", ".join(f"{key}={value}"
                                     for key, value in sorted(result["statuses"].items())))
    print("  by kind: " + ", ".join(f"{key}={value}"
                                    for key, value in sorted(result["byKind"].items())))
    for item in result["unresolved"][:15]:
        print(f"  UNRESOLVED {item}")
    return 0 if result["allResolve"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
