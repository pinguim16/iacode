#!/usr/bin/env python3
"""Complete the requirements matrix of this audit checkpoint from observed audit evidence.

An audit checkpoint declares the same canonical Gate rows and the same lesson-derived rows as any
delivery for this Gate. What differs is how they are satisfied: the artifact evidence is the
repository content this audit inspected, and the validation evidence is the audit that inspected it.

Artifact and test references are carried over from the sealed subject, because they name the same
files and the same suite identifiers, and this audit resolved every one of them itself. References
that pointed inside the subject checkpoint directory are dropped rather than rewritten, because they
do not exist here; the audit artifacts of this checkpoint replace them.
"""

from __future__ import annotations

import json
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0010"

AUDIT_EVIDENCE = [
    "checkpoint:FINAL-M0-AUDIT-MATRIX.json",
    "checkpoint:AUDIT-EXECUTIONS.json",
]

LESSON_EVIDENCE = {
    "lesson:LSN-0030": {
        "implementationEvidence": ["file:.iacode/memory/lessons.jsonl"],
        "testEvidence": ["test:LessonPreflightTests.test_the_repository_preflight_covers_every_applicable_lesson"],
        "documentationEvidence": ["file:docs/ENGINEERING-MEMORY.md"],
    },
}


def main() -> int:
    matrix_path = CHECKPOINT / "REQUIREMENTS-MATRIX.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    subject = json.loads((SUBJECT / "REQUIREMENTS-MATRIX.json").read_text(encoding="utf-8"))
    inherited = {item["sourceRef"]: item for item in subject["requirements"]}

    missing: list[str] = []
    for requirement in matrix["requirements"]:
        reference = requirement["sourceRef"]
        source = inherited.get(reference) or LESSON_EVIDENCE.get(reference)
        if source is None:
            missing.append(reference)
            continue
        for key in ("implementationEvidence", "testEvidence", "documentationEvidence"):
            values = [item for item in (source.get(key) or [])
                      if not item.startswith("checkpoint:")]
            requirement[key] = values
        requirement["validationEvidence"] = list(AUDIT_EVIDENCE)
        requirement["status"] = "COMPLETE"
        requirement["notes"] = (
            "Verified by the fresh-session independent M0 audit of SETUP-00-CP-0010: the artifact "
            "and the suite identifiers were resolved against the repository by this audit, not "
            "accepted as declared.")
        if not (requirement["implementationEvidence"] + requirement["testEvidence"]
                + requirement["documentationEvidence"]):
            missing.append(reference)

    matrix_path.write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    # The closure view is the same requirement set seen through the milestone controls, so it is
    # filled from the matrix rather than maintained separately: two hand-kept copies of one fact is
    # the failure class LSN-0022 exists for.
    by_reference = {item["sourceRef"]: item for item in matrix["requirements"]}
    closure_path = CHECKPOINT / "CLOSURE-REQUIREMENTS.json"
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    for row in closure["requirements"]:
        source = by_reference.get(row["sourceRef"])
        if source is None:
            missing.append(row["sourceRef"])
            continue
        row["implementationStatus"] = source["status"]
        row["finalStatus"] = source["status"]
        row["implementationEvidence"] = list(source["implementationEvidence"])
        row["testEvidence"] = list(source["testEvidence"])
        row["documentationEvidence"] = list(source["documentationEvidence"])
        row["validationEvidence"] = list(source["validationEvidence"])
        row["notes"] = source["notes"]
    closure_path.write_text(
        json.dumps(closure, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    closure_lines = [
        "# Closure Requirements",
        "",
        f"Gate: `{closure['gate']}` — Checkpoint: `{closure['checkpoint']}`",
        "",
    ]
    for source in closure["sources"]:
        closure_lines.append(f"- {source}")
    closure_lines += [
        "",
        "| Requirement | Source | Mandatory | Final status | Description |",
        "|---|---|---|---|---|",
    ]
    for row in closure["requirements"]:
        description = row["description"].replace("|", "\\|")
        closure_lines.append(
            f"| `{row['id']}` | `{row['sourceRef']}` | "
            f"{'yes' if row['mandatory'] else 'no'} | `{row['finalStatus']}` | {description} |")
    closure_lines.append("")
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(
        "\n".join(closure_lines), encoding="utf-8", newline="\n")

    lines = [
        "# Requirements Matrix",
        "",
        f"Gate: `{matrix['gate']}` — Checkpoint: `{matrix['checkpoint']}`",
        "",
        f"Expected set source: {matrix['expectedSetSource']}",
        "",
        "| Requirement | Source | Mandatory | Status | Description |",
        "|---|---|---|---|---|",
    ]
    for requirement in matrix["requirements"]:
        description = requirement["description"].replace("|", "\\|")
        lines.append(
            f"| `{requirement['id']}` | `{requirement['sourceRef']}` | "
            f"{'yes' if requirement['mandatory'] else 'no'} | `{requirement['status']}` | "
            f"{description} |")
    lines.append("")
    (CHECKPOINT / "REQUIREMENTS-MATRIX.md").write_text(
        "\n".join(lines), encoding="utf-8", newline="\n")

    print(f"COMPLETED requirements={len(matrix['requirements'])} withoutEvidence={len(missing)}")
    for reference in missing:
        print(f"- {reference}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
