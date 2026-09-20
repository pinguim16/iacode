#!/usr/bin/env python3
"""Derive a delivery's requirement set from the canonical sources, before anything is implemented.

The requirement set of a delivery is not an opinion. It is the union of sources the delivery does
not own:

- every row of the Gate's canonical specification;
- every lesson the mandatory preflight selected;
- every finding of an independent audit whose corrective work is this checkpoint;
- every mandatory attack of that audit's Red Team.

This tool writes two artifacts and keeps them in agreement:

- ``CLOSURE-REQUIREMENTS.json`` / ``.md``  the full closure view, with the separate evidence
  columns the closure protocol requires;
- ``REQUIREMENTS-MATRIX.json`` / ``.md``   the schema-bound matrix the delivery gates audit.

Re-running it preserves whatever a run has already recorded for a requirement and only adds,
removes or re-anchors rows to match the derived expected set, so the set cannot drift and the
evidence is not lost.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, find_root, load_json, resolve_latest, utc_now, validate_schema
from policies import expected_requirement_refs

EVIDENCE_FIELDS = (
    "implementationEvidence",
    "testEvidence",
    "negativeTestEvidence",
    "documentationEvidence",
    "validationEvidence",
    "guardrailEvidence",
)

MATRIX_EVIDENCE_FIELDS = (
    "implementationEvidence",
    "testEvidence",
    "documentationEvidence",
    "validationEvidence",
)

# Anchored kinds in the order their requirements are numbered, so identifiers stay stable across
# runs as long as the canonical sources are stable.
KIND_ORDER = ("canonical", "finding", "attack", "local")

EXPECTED_SET_SOURCE = (
    "policies.expected_requirement_refs over docs/SETUP-00-CHECKLIST.md, "
    ".iacode/policies/canonical-requirements.json, .iacode/policies/audit-registry.json and "
    "LESSON-PREFLIGHT.json"
)


def _load_preflight(checkpoint: Path) -> dict[str, Any] | None:
    path = checkpoint / "LESSON-PREFLIGHT.json"
    if not path.is_file():
        return None
    document = load_json(path)
    return document if isinstance(document, dict) else None


def _existing(checkpoint: Path) -> dict[str, dict[str, Any]]:
    """Previously recorded closure rows, keyed by anchored reference."""
    path = checkpoint / "CLOSURE-REQUIREMENTS.json"
    if not path.is_file():
        return {}
    document = load_json(path)
    rows = document.get("requirements") if isinstance(document, dict) else None
    return {
        str(row["sourceRef"]): row
        for row in rows or []
        if isinstance(row, dict) and row.get("sourceRef")
    }


def _lesson_requirement_ids(preflight: dict[str, Any] | None) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for derived in (preflight or {}).get("derivedRequirements") or []:
        if isinstance(derived, dict) and derived.get("lessonId") and derived.get("id"):
            mapping[f"lesson:{derived['lessonId']}"] = str(derived["id"])
    return mapping


def build(root: Path, checkpoint: Path, gate: str) -> tuple[dict[str, Any], dict[str, Any]]:
    preflight = _load_preflight(checkpoint)
    expected = expected_requirement_refs(root, gate, checkpoint.name, preflight)
    previous = _existing(checkpoint)
    lesson_ids = _lesson_requirement_ids(preflight)

    ordered: list[str] = []
    for kind in KIND_ORDER:
        ordered += [reference for reference in expected if reference.startswith(f"{kind}:")]
    lesson_refs = [reference for reference in expected if reference.startswith("lesson:")]

    requirements: list[dict[str, Any]] = []
    number = 0
    for reference in ordered:
        number += 1
        requirements.append(_row(f"REQ-{number:04d}", expected[reference], previous.get(reference)))
    for reference in sorted(lesson_refs, key=lambda item: lesson_ids.get(item, item)):
        identifier = lesson_ids.get(reference)
        if identifier is None:
            continue
        requirements.append(_row(identifier, expected[reference], previous.get(reference)))

    closure = {
        "schemaVersion": "1.0.0",
        "gate": gate,
        "checkpoint": checkpoint.name,
        "sources": [
            "SOURCE A: docs/SETUP-00-CHECKLIST.md, the canonical SETUP-00 specification",
            "SOURCE B: docs/MILESTONE-VALIDATION.md, the M0 milestone requirements of the audit",
            "SOURCE C: docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md, the audit findings",
            "SOURCE D: docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md, the A-Z attacks",
            "SOURCE E: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes",
        ],
        "requirements": requirements,
    }

    matrix = {
        "schemaVersion": "2.0.0",
        "gate": gate,
        "checkpoint": checkpoint.name,
        "expectedSetSource": EXPECTED_SET_SOURCE,
        "requirements": [
            {
                "id": row["id"],
                "source": row["sourceReference"],
                "sourceRef": row["sourceRef"],
                "description": row["description"],
                "mandatory": row["mandatory"],
                "status": row["finalStatus"],
                "implementationEvidence": list(row["implementationEvidence"]),
                "testEvidence": list(row["testEvidence"]) + list(row["negativeTestEvidence"]),
                "documentationEvidence": list(row["documentationEvidence"]),
                "validationEvidence": list(row["validationEvidence"]) + list(row["guardrailEvidence"]),
                "justification": row.get("justification"),
                "notes": row.get("notes", ""),
            }
            for row in requirements
        ],
    }
    return closure, matrix


def _row(identifier: str, expected: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any]:
    row = {
        "id": identifier,
        "source": expected["source"],
        "sourceRef": expected["sourceRef"],
        "sourceReference": expected["sourceReference"],
        "description": expected["description"],
        "mandatory": bool(expected["mandatory"]),
        "implementationStatus": "NOT_STARTED",
        "finalStatus": "NOT_STARTED",
        "justification": None,
        "notes": "",
    }
    for field in EVIDENCE_FIELDS:
        row[field] = []
    if previous:
        for field in EVIDENCE_FIELDS:
            values = previous.get(field)
            if isinstance(values, list):
                row[field] = [str(item) for item in values]
        for field in ("implementationStatus", "finalStatus", "justification", "notes"):
            if field in previous:
                row[field] = previous[field]
    return row


def render_closure(document: dict[str, Any]) -> str:
    lines = [
        f"# Closure Requirements - {document['checkpoint']}",
        "",
        "Derived from the canonical sources listed below, before implementation. The expected set",
        "is recomputed by `policies.expected_requirement_refs` and compared exactly with the",
        "declared set, so a requirement cannot be dropped and the denominator cannot be reduced.",
        "",
        "## Sources",
        "",
    ]
    lines += [f"- {item}" for item in document["sources"]]
    lines += [
        "",
        "## Requirements",
        "",
        "| ID | Source | Anchor | Mandatory | Implementation | Final | Description |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in document["requirements"]:
        lines.append("| `%s` | %s | `%s` | %s | `%s` | `%s` | %s |" % (
            row["id"], row["source"], row["sourceRef"], "yes" if row["mandatory"] else "no",
            row["implementationStatus"], row["finalStatus"], row["description"]))
    lines += ["", "## Evidence", ""]
    for row in document["requirements"]:
        lines += [f"### {row['id']} - {row['sourceRef']}", ""]
        lines.append(f"- Source reference: {row['sourceReference']}")
        lines.append(f"- Description: {row['description']}")
        for field, title in (
            ("implementationEvidence", "Implementation"),
            ("testEvidence", "Test"),
            ("negativeTestEvidence", "Negative test"),
            ("documentationEvidence", "Documentation"),
            ("validationEvidence", "Validation"),
            ("guardrailEvidence", "Guardrail"),
        ):
            values = row.get(field) or []
            rendered = ", ".join("`%s`" % item for item in values) if values else "_none_"
            lines.append(f"- {title}: {rendered}")
        if row.get("justification"):
            lines.append(f"- Justification: {row['justification']}")
        lines.append("")
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def render_matrix(document: dict[str, Any]) -> str:
    lines = [
        f"# Requirements Matrix - {document['checkpoint']}",
        "",
        f"Expected set derived by: `{document['expectedSetSource']}`.",
        "",
        "| ID | Anchor | Mandatory | Status | Requirement | Source |",
        "|---|---|---|---|---|---|",
    ]
    for row in document["requirements"]:
        lines.append("| `%s` | `%s` | %s | `%s` | %s | %s |" % (
            row["id"], row["sourceRef"], "yes" if row["mandatory"] else "no",
            row["status"], row["description"], row["source"]))
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--gate", default=None)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    gate = args.gate
    if gate is None:
        state = load_json(checkpoint / "STATE.json")
        gate = str(state.get("gate"))

    closure, matrix = build(root, checkpoint, gate)

    for name, document in (("closure-requirements.schema.json", closure),
                           ("requirements-matrix.schema.json", matrix)):
        schema_path = root / ".iacode" / "schemas" / name
        if schema_path.is_file():
            errors = validate_schema(document, load_json(schema_path))
            if errors:
                print("REQUIREMENTS_INVALID")
                for error in errors:
                    print(f"- {error}")
                return 2

    if args.write:
        (checkpoint / "CLOSURE-REQUIREMENTS.json").write_text(
            json.dumps(closure, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        (checkpoint / "CLOSURE-REQUIREMENTS.md").write_text(
            render_closure(closure), encoding="utf-8", newline="\n")
        (checkpoint / "REQUIREMENTS-MATRIX.json").write_text(
            json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        (checkpoint / "REQUIREMENTS-MATRIX.md").write_text(
            render_matrix(matrix), encoding="utf-8", newline="\n")

    by_source: dict[str, int] = {}
    for row in closure["requirements"]:
        by_source[row["source"]] = by_source.get(row["source"], 0) + 1
    print("REQUIREMENTS_DERIVED gate=%s checkpoint=%s total=%d" % (
        gate, checkpoint.name, len(closure["requirements"])))
    for source, count in sorted(by_source.items()):
        print(f"- {source}: {count}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
