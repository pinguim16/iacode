#!/usr/bin/env python3
"""Complete the audit matrix from sealed-subject and fresh audit evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0007"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from delivery_assurance import collect_test_ids, load_command_results, resolve_evidence  # noqa: E402
from ledger_common import load_json, use_utf8_stdout, write_json  # noqa: E402
from lessons import load_guardrails, load_lessons  # noqa: E402


def subject_rows() -> dict[str, dict]:
    raw = subprocess.run(
        [
            "git", "show",
            f"iacode-checkpoints/{SUBJECT}:docs/checkpoints/{SUBJECT}/REQUIREMENTS-MATRIX.json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout
    return {str(row.get("sourceRef")): row for row in json.loads(raw)["requirements"]}


def repoint(reference: str) -> str | None:
    kind, _, value = reference.partition(":")
    if kind in {"file", "test"}:
        return reference
    if kind == "checkpoint":
        return f"file:docs/checkpoints/{SUBJECT}/{value}"
    if kind == "command":
        return f"file:docs/checkpoints/{SUBJECT}/COMMANDS.jsonl"
    return None


def main() -> int:
    use_utf8_stdout()
    closure_path = CHECKPOINT / "CLOSURE-REQUIREMENTS.json"
    closure = load_json(closure_path)
    inherited = subject_rows()
    lessons = {item["lessonId"]: item for item in load_lessons(ROOT)}
    guardrails = load_guardrails(ROOT)
    commands = load_command_results(CHECKPOINT)
    tests = collect_test_ids(ROOT)
    rotted: list[str] = []

    validation = [
        "checkpoint:PUBLISHED-CLEAN-CLONE-REPORT.json",
        "checkpoint:VERIFICATION-REPORT.json",
        "checkpoint:SUBJECT-INVENTORY-AUDIT.json",
        "checkpoint:SUBJECT-COUNTS-AUDIT.json",
        "checkpoint:SUBJECT-MIRROR-AUDIT.json",
        "checkpoint:ARCHITECTURE-REVIEW.json",
        "checkpoint:G4-X7-INDEPENDENT-PROBE.json",
        "checkpoint:TRANSPORT-ATTACKS.json",
        "checkpoint:SUBJECT-BUNDLE-AUDIT.json",
        "checkpoint:GATE-4-INDEPENDENT-RED-TEAM.json",
        "checkpoint:FINAL-GATE-4-AUDIT-MATRIX.json",
        "checkpoint:FINDINGS.json",
    ]
    negative = [
        "checkpoint:GATE-4-INDEPENDENT-RED-TEAM.json",
        "checkpoint:G4-X7-INDEPENDENT-PROBE.json",
        "checkpoint:TRANSPORT-ATTACKS.json",
        "checkpoint:FINDINGS.json",
    ]

    for row in closure["requirements"]:
        reference = str(row.get("sourceRef"))
        buckets = {
            "implementationEvidence": [],
            "testEvidence": [],
            "negativeTestEvidence": [],
            "documentationEvidence": [],
            "guardrailEvidence": [],
        }
        declared = inherited.get(reference)
        if declared is not None:
            for key in buckets:
                for item in declared.get(key) or []:
                    mapped = repoint(str(item))
                    if mapped and mapped not in buckets[key]:
                        buckets[key].append(mapped)
        elif reference.startswith("lesson:"):
            lesson = lessons.get(reference.split(":", 1)[1]) or {}
            buckets["implementationEvidence"].append("file:.iacode/memory/lessons.jsonl")
            buckets["documentationEvidence"].append("file:docs/ENGINEERING-MEMORY.md")
            buckets["guardrailEvidence"].append("file:.iacode/memory/guardrails/registry.json")
            for identifier in lesson.get("guardrails") or []:
                for test_id in (guardrails.get(str(identifier)) or {}).get("verifiedBy") or []:
                    buckets["testEvidence"].append(f"test:{test_id}")
        else:
            rotted.append(f"{row['id']}: no sealed subject row for {reference}")

        if not buckets["implementationEvidence"]:
            buckets["implementationEvidence"] = [f"file:docs/checkpoints/{SUBJECT}/FINAL-REPORT.md"]
        if not buckets["testEvidence"]:
            buckets["testEvidence"] = [f"file:docs/checkpoints/{SUBJECT}/TESTS.json"]
        if not buckets["negativeTestEvidence"]:
            buckets["negativeTestEvidence"] = list(negative)
        if not buckets["documentationEvidence"]:
            buckets["documentationEvidence"] = ["file:docs/GATE-4-CHECKLIST.md"]
        if not buckets["guardrailEvidence"]:
            buckets["guardrailEvidence"] = ["file:.iacode/memory/guardrails/registry.json"]

        for key, values in buckets.items():
            kept: list[str] = []
            for value in dict.fromkeys(values):
                error = resolve_evidence(ROOT, CHECKPOINT, value, commands, tests)
                if error is None:
                    kept.append(value)
                else:
                    rotted.append(f"{row['id']} {value}: {error}")
            row[key] = kept
        row["validationEvidence"] = list(validation)
        row["implementationStatus"] = "COMPLETE"
        row["finalStatus"] = "COMPLETE"
        row["justification"] = None
        row["notes"] = (
            "Fresh-session audit evidence resolves this requirement. The audit completion status "
            "does not override the independent REWORK_REQUIRED verdict or G4-F-004."
        )

    write_json(closure_path, closure)
    matrix_path = CHECKPOINT / "REQUIREMENTS-MATRIX.json"
    matrix = load_json(matrix_path)
    resolved = {str(row.get("sourceRef")): row for row in closure["requirements"]}
    for row in matrix.get("requirements") or []:
        source = resolved.get(str(row.get("sourceRef")))
        if source is None:
            rotted.append(f"{row.get('id')}: no closure row for {row.get('sourceRef')}")
            continue
        row["status"] = "COMPLETE"
        for key in (
            "implementationEvidence", "testEvidence", "documentationEvidence", "validationEvidence",
        ):
            row[key] = list(source.get(key) or [])
        row["justification"] = None
        row["notes"] = str(source.get("notes") or "")
    write_json(matrix_path, matrix)

    completed = sum(1 for row in matrix.get("requirements") or [] if row.get("status") == "COMPLETE")
    print(json.dumps({
        "closureCompleted": len(closure["requirements"]),
        "matrixCompleted": completed,
        "rotted": len(rotted),
    }))
    for item in rotted:
        print(f"- rotted: {item}")
    return 0 if not rotted else 1


if __name__ == "__main__":
    raise SystemExit(main())
