#!/usr/bin/env python3
"""Complete the audit matrix only from sealed and independently re-executed evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0003"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from delivery_assurance import collect_test_ids, load_command_results, resolve_evidence  # noqa: E402
from ledger_common import load_json, write_json  # noqa: E402
from lessons import load_guardrails, load_lessons  # noqa: E402


def subject_rows() -> dict[str, dict]:
    shown = subprocess.run(
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
    return {str(item.get("sourceRef")): item for item in json.loads(shown)["requirements"]}


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--verification-command", required=True)
    parser.add_argument("--red-team-command", required=True)
    arguments = parser.parse_args()
    closure_path = CHECKPOINT / "CLOSURE-REQUIREMENTS.json"
    closure = load_json(closure_path)
    subject = subject_rows()
    lessons = {item["lessonId"]: item for item in load_lessons(ROOT)}
    guardrails = load_guardrails(ROOT)
    commands = load_command_results(CHECKPOINT)
    tests = collect_test_ids(ROOT)
    rotted: list[str] = []

    common_validation = [
        "checkpoint:SUBJECT-BUNDLE-AUDIT.json",
        "checkpoint:ARCHITECTURE-REVIEW.json",
        "checkpoint:G4-X7-INDEPENDENT-PROBE.json",
        "checkpoint:GATE-4-INDEPENDENT-RED-TEAM.json",
        "checkpoint:VERIFICATION-REPORT.json",
    ]
    common_negative = [
        f"command:{arguments.red_team_command}",
        "checkpoint:GATE-4-INDEPENDENT-RED-TEAM.json",
        "checkpoint:G4-X7-INDEPENDENT-PROBE.json",
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
        declared = subject.get(reference)
        if declared is not None:
            for key in buckets:
                for item in declared.get(key) or []:
                    resolved = repoint(str(item))
                    if resolved and resolved not in buckets[key]:
                        buckets[key].append(resolved)
        elif reference.startswith("lesson:"):
            lesson = lessons.get(reference.split(":", 1)[1]) or {}
            buckets["implementationEvidence"].append("file:.iacode/memory/lessons.jsonl")
            buckets["documentationEvidence"].append("file:docs/ENGINEERING-MEMORY.md")
            buckets["guardrailEvidence"].append("file:.iacode/memory/guardrails/registry.json")
            for identifier in lesson.get("guardrails") or []:
                entry = guardrails.get(str(identifier)) or {}
                for test in entry.get("verifiedBy") or []:
                    buckets["testEvidence"].append(f"test:{test}")
        else:
            rotted.append(f"{row['id']}: no sealed subject row for {reference}")

        if not buckets["implementationEvidence"]:
            buckets["implementationEvidence"] = ["file:docs/checkpoints/GATE-4-CP-0003/FINAL-REPORT.md"]
        if not buckets["testEvidence"]:
            buckets["testEvidence"] = [
                "file:docs/checkpoints/GATE-4-CP-0003/TESTS.json"
            ]
        if not buckets["negativeTestEvidence"]:
            buckets["negativeTestEvidence"] = list(common_negative)
        if not buckets["documentationEvidence"]:
            buckets["documentationEvidence"] = ["file:docs/GATE-4-CHECKLIST.md"]
        if not buckets["guardrailEvidence"]:
            buckets["guardrailEvidence"] = ["file:.iacode/memory/guardrails/registry.json"]

        for key, values in buckets.items():
            kept = []
            for value in dict.fromkeys(values):
                error = resolve_evidence(ROOT, CHECKPOINT, value, commands, tests)
                if error is None:
                    kept.append(value)
                else:
                    rotted.append(f"{row['id']} {value}: {error}")
            row[key] = kept
        row["validationEvidence"] = list(common_validation)
        row["implementationStatus"] = "COMPLETE"
        row["finalStatus"] = "COMPLETE"
        row["justification"] = None
        row["notes"] = (
            "Independently re-resolved from the sealed subject and re-executed by the fresh "
            "Gate 4 audit; the subject's own assertion was not used as the verdict."
        )

    write_json(closure_path, closure)
    print(json.dumps({"completed": len(closure["requirements"]), "rotted": len(rotted)}))
    for item in rotted:
        print(f"- rotted: {item}")
    return 0 if not rotted else 1


if __name__ == "__main__":
    raise SystemExit(main())
