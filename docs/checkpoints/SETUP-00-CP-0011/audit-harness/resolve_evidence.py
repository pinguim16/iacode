#!/usr/bin/env python3
"""Resolve every evidence reference the subject declares, with this audit's own resolver.

A completeness report that counts its own references is not evidence that the references resolve.
Each reference is resolved here against the repository: a file against the tree, a checkpoint
artifact against the checkpoint directory, a command against the ledger, a test against the
identifiers the suite actually discovers, a lesson against the memory, a guardrail against the
registry.
"""

from __future__ import annotations

import argparse
import json
import unittest
from collections import Counter
from pathlib import Path

EVIDENCE_KEYS = (
    "implementationEvidence", "testEvidence", "documentationEvidence", "validationEvidence")


def suite_identifiers(root: Path) -> set[str]:
    identifiers: set[str] = set()

    def walk(item) -> None:
        if isinstance(item, unittest.TestSuite):
            for child in item:
                walk(child)
        elif isinstance(item, unittest.TestCase):
            full = item.id()
            parts = full.split(".")
            identifiers.add(full)
            if len(parts) >= 2:
                # A reference may name the case, the class, or the class-qualified case.
                identifiers.add(".".join(parts[-2:]))
                identifiers.add(parts[-2])
                identifiers.add(parts[-1])

    walk(unittest.defaultTestLoader.discover(
        str(root / "tests"), top_level_dir=str(root / "tests")))
    return identifiers


def command_identifiers(checkpoint: Path) -> set[str]:
    path = checkpoint / "COMMANDS.jsonl"
    if not path.is_file():
        return set()
    identifiers = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        value = record.get("id") or record.get("commandId")
        if value:
            identifiers.add(str(value))
    return identifiers


def lesson_identifiers(root: Path) -> set[str]:
    path = root / ".iacode" / "memory" / "lessons.jsonl"
    if not path.is_file():
        return set()
    return {json.loads(line)["lessonId"]
            for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def guardrail_identifiers(root: Path) -> set[str]:
    path = root / ".iacode" / "memory" / "guardrails" / "registry.json"
    if not path.is_file():
        return set()
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = document.get("guardrails") if isinstance(document, dict) else document
    return {str(item.get("guardrailId")) for item in rows or [] if isinstance(item, dict)}


def resolve(reference: str, context: dict) -> str | None:
    kind, _, value = reference.partition(":")
    if not value:
        return f"{reference}: no target"
    if kind == "file":
        return None if (context["root"] / value).exists() else f"{reference}: path does not exist"
    if kind == "checkpoint":
        return (None if (context["checkpoint"] / value).exists()
                else f"{reference}: checkpoint artifact does not exist")
    if kind == "command":
        return None if value in context["commands"] else f"{reference}: no such command record"
    if kind == "test":
        return None if value in context["tests"] else f"{reference}: not discovered by the suite"
    if kind == "lesson":
        return None if value in context["lessons"] else f"{reference}: no such lesson"
    if kind == "guardrail":
        return None if value in context["guardrails"] else f"{reference}: no such guardrail"
    return f"{reference}: unsupported evidence kind {kind!r}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    checkpoint = root / "docs" / "checkpoints" / args.checkpoint
    context = {
        "root": root,
        "checkpoint": checkpoint,
        "tests": suite_identifiers(root),
        "commands": command_identifiers(checkpoint),
        "lessons": lesson_identifiers(root),
        "guardrails": guardrail_identifiers(root),
    }

    matrix = json.loads((checkpoint / "REQUIREMENTS-MATRIX.json").read_text(encoding="utf-8"))
    unresolved: list[str] = []
    without_evidence: list[str] = []
    kinds: Counter = Counter()
    statuses: Counter = Counter()
    total_references = 0
    for requirement in matrix["requirements"]:
        statuses[requirement.get("status")] += 1
        references = [item for key in EVIDENCE_KEYS for item in requirement.get(key) or []]
        if not references:
            without_evidence.append(requirement["id"])
        for reference in references:
            total_references += 1
            kinds[reference.partition(":")[0]] += 1
            problem = resolve(reference, context)
            if problem:
                unresolved.append(f"{requirement['id']} {problem}")

    report = {
        "checkpoint": args.checkpoint,
        "requirements": len(matrix["requirements"]),
        "statuses": dict(statuses),
        "evidenceReferences": total_references,
        "referenceKinds": dict(kinds),
        "requirementsWithoutEvidence": without_evidence,
        "unresolved": unresolved,
        "allResolve": not unresolved and not without_evidence,
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return 0 if report["allResolve"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
