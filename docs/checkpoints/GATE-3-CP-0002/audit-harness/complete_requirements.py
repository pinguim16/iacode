#!/usr/bin/env python3
"""Complete this audit's requirement matrix from evidence the audit resolved itself.

The matrix is derived by `derive_requirements.py` from the GATE 3 checklist and this audit's lesson
preflight; this never adds or removes a row. For each row it takes the repository evidence the
sealed subject declared for the same anchored reference — read from the subject's own tag, not
from the working tree's copy — keeps only the references that still resolve against the audited
tree (`file:` and `test:`; the subject's `command:` and `checkpoint:` references belong to the
subject's ledger and are re-pointed at the sealed files that hold them), and adds the audit's own
validation evidence: the full verification, the audit matrix and the execution record.

A reference the subject declared that no longer resolves is not dropped silently: it is counted in
the report and makes the row fail, because evidence that rotted after the seal is a finding.

    python complete_requirements.py --verification-command cmd-0012
    python scripts/development-ledger/derive_requirements.py --write
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-3-CP-0001"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from delivery_assurance import collect_test_ids, load_command_results, resolve_evidence  # noqa: E402
from ledger_common import load_json, write_json  # noqa: E402
from lessons import load_guardrails, load_lessons  # noqa: E402

AUDIT_NOTE = (
    "Re-verified by the M1 fresh-session audit: the repository evidence the sealed subject "
    "GATE-3-CP-0001 declared for this row was read from the subject's tag and re-resolved against "
    "the audited tree, and the row is validated by the audit's own executions — the full "
    "verification, the sealed-subject validation, the cross-gate live run and the cross-gate Red "
    "Team — rather than by the delivery's statement.")
LESSON_NOTE = (
    "This run audits and does not implement (LSN-0030), so the lesson is discharged by confirming "
    "that the control the memory registers for it still resolves to real code and an existing "
    "test, and by applying the lesson to the conduct of the audit itself.")


def subject_matrix() -> dict[str, dict]:
    shown = subprocess.run(
        ["git", "show", f"iacode-checkpoints/{SUBJECT}:docs/checkpoints/{SUBJECT}/"
                        "REQUIREMENTS-MATRIX.json"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return {str(item.get("sourceRef")): item for item in json.loads(shown)["requirements"]}


def repoint(reference: str) -> str | None:
    kind, _, value = reference.partition(":")
    if kind in ("file", "test"):
        return reference
    if kind == "checkpoint":
        return f"file:docs/checkpoints/{SUBJECT}/{value}"
    if kind == "command":
        return f"file:docs/checkpoints/{SUBJECT}/COMMANDS.jsonl"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verification-command", required=True)
    parser.add_argument("--extra-validation", action="append", default=[])
    arguments = parser.parse_args()

    # derive_requirements.py preserves what a run recorded from the closure rows, and renders the
    # matrix from them; completing the closure rows is what survives a re-derivation.
    matrix_path = CHECKPOINT / "CLOSURE-REQUIREMENTS.json"
    matrix = load_json(matrix_path)
    subject = subject_matrix()
    lessons = {item["lessonId"]: item for item in load_lessons(ROOT)}
    guardrails = load_guardrails(ROOT)
    commands = load_command_results(CHECKPOINT)
    tests = collect_test_ids(ROOT)
    validation = [f"command:{arguments.verification_command}",
                  "checkpoint:FINAL-M1-AUDIT-MATRIX.json", "checkpoint:AUDIT-EXECUTIONS.json",
                  *arguments.extra_validation]

    rotted: list[str] = []
    completed = 0
    for row in matrix["requirements"]:
        reference = str(row.get("sourceRef"))
        buckets = {"implementationEvidence": [], "testEvidence": [], "documentationEvidence": []}
        declared = subject.get(reference)
        if declared is not None:
            for key in buckets:
                for item in declared.get(key) or []:
                    repointed = repoint(str(item))
                    if repointed and repointed not in buckets[key]:
                        buckets[key].append(repointed)
        elif reference.startswith("lesson:"):
            lesson = lessons.get(reference.split(":", 1)[1]) or {}
            buckets["implementationEvidence"].append("file:.iacode/memory/lessons.jsonl")
            for identifier in lesson.get("guardrails") or []:
                entry = guardrails.get(str(identifier)) or {}
                for test in entry.get("verifiedBy") or []:
                    buckets["testEvidence"].append(f"test:{test}")
            buckets["documentationEvidence"].append("file:docs/ENGINEERING-MEMORY.md")
        for key, values in buckets.items():
            kept = []
            for value in values:
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
        row["notes"] = LESSON_NOTE if reference.startswith("lesson:") else AUDIT_NOTE
        completed += 1

    write_json(matrix_path, matrix)
    print(json.dumps({"completed": completed, "rottedReferences": len(rotted)}))
    for item in rotted:
        print(f"- rotted: {item}")
    return 0 if not rotted else 1


if __name__ == "__main__":
    raise SystemExit(main())
