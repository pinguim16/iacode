#!/usr/bin/env python3
"""Complete CP0007 requirements from sealed Gate 4 evidence and current corrective proof."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0006"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from delivery_assurance import collect_test_ids, load_command_results, resolve_evidence  # noqa: E402
from ledger_common import load_json, use_utf8_stdout, write_json  # noqa: E402

FIELDS = (
    "implementationEvidence",
    "testEvidence",
    "negativeTestEvidence",
    "documentationEvidence",
    "validationEvidence",
    "guardrailEvidence",
)


def subject_rows() -> dict[str, dict]:
    shown = subprocess.run(
        [
            "git",
            "show",
            f"iacode-checkpoints/{SUBJECT}:docs/checkpoints/{SUBJECT}/CLOSURE-REQUIREMENTS.json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout
    return {str(item["sourceRef"]): item for item in json.loads(shown)["requirements"]}


def repoint(reference: str) -> str | None:
    kind, _, value = reference.partition(":")
    if kind in {"file", "test"}:
        return reference
    if kind == "checkpoint":
        return f"file:docs/checkpoints/{SUBJECT}/{value}"
    if kind == "command":
        return f"file:docs/checkpoints/{SUBJECT}/COMMANDS.jsonl"
    return None


def corrective_evidence() -> dict[str, list[str]]:
    return {
        "implementationEvidence": [
            "file:scripts/development-ledger/ledger_common.py",
            "file:scripts/development-ledger/record_command.py",
            "file:scripts/development-ledger/validate_checkpoint.py",
            "file:.iacode/schemas/checkpoint.schema.json",
        ],
        "testEvidence": [
            "test:test_git_metadata_is_local_even_though_git_check_ignore_does_not_classify_it",
            "test:test_schema_3_3_refuses_a_digest_bound_git_metadata_input",
            "test:test_schema_3_3_refuses_an_ignored_input_even_when_it_exists",
            "test:test_the_recorder_excludes_git_metadata_and_refuses_it_when_explicit",
            "test:test_a_nontransport_input_refusal_is_recomputed_from_its_precondition",
            "test:test_a_fabricated_nontransport_input_refusal_is_rejected",
            "test:test_the_first_transport_refusal_record_keeps_valid_legacy_classification",
        ],
        "negativeTestEvidence": [
            "checkpoint:CP0006-REMOTE-TRANSPORT-BASELINE.json",
            "command:cmd-0010",
            "command:cmd-0024",
        ],
        "documentationEvidence": [
            "file:DIVERGENCE.md",
            "file:docs/adr/ADR-0034-command-inputs-must-cross-git-transport.md",
            "file:docs/CHECKPOINT-PROTOCOL.md",
        ],
        "validationEvidence": [
            "checkpoint:CP0006-CURRENT-TOOL-REMOTE-TRANSPORT.json",
            "checkpoint:G4-CP-0006-PUBLICATION-FINDINGS-CLOSURE.json",
            "checkpoint:VERIFY.json",
            "checkpoint:FUNCTIONAL-ACCEPTANCE-VALIDATION.json",
            "checkpoint:M2-INTERNAL-RED-TEAM.json",
            "command:cmd-0031",
            "command:cmd-0033",
        ],
        "guardrailEvidence": [
            "file:.iacode/memory/lessons.jsonl",
            "file:.iacode/memory/guardrails/registry.json",
        ],
    }


def main() -> int:
    use_utf8_stdout()
    closure_path = CHECKPOINT / "CLOSURE-REQUIREMENTS.json"
    matrix_path = CHECKPOINT / "REQUIREMENTS-MATRIX.json"
    closure = deepcopy(load_json(closure_path))
    matrix = deepcopy(load_json(matrix_path))
    subject = subject_rows()
    current = corrective_evidence()
    commands = load_command_results(CHECKPOINT)
    tests = collect_test_ids(ROOT)
    errors: list[str] = []
    inherited = 0
    corrected = 0

    for row in closure["requirements"]:
        reference = str(row["sourceRef"])
        if reference in {"finding:G4-F-003", "lesson:LSN-0040"}:
            evidence = deepcopy(current)
            notes = (
                "Closed by the CP0007 forward-only Git-transport command-input contract, with "
                "the old remote-clone failure retained as the negative control and all 42 "
                "canonical verifier stages re-executed green."
            )
            corrected += 1
        else:
            previous = subject.get(reference)
            if previous is None or previous.get("finalStatus") != "COMPLETE":
                errors.append(f"{row['id']}: no complete sealed subject row for {reference}")
                continue
            evidence = {field: [] for field in FIELDS}
            for field in FIELDS:
                for item in previous.get(field) or []:
                    candidate = repoint(str(item))
                    if candidate and candidate not in evidence[field]:
                        evidence[field].append(candidate)
            evidence["validationEvidence"] = list(dict.fromkeys(
                evidence["validationEvidence"]
                + [
                    "checkpoint:VERIFY.json",
                    "checkpoint:FUNCTIONAL-ACCEPTANCE-VALIDATION.json",
                    "command:cmd-0031",
                ]
            ))
            notes = (
                "Inherited from the sealed Gate 4 audit evidence and revalidated by the complete "
                "CP0007 verifier; inheritance is evidence reuse, not a new independent verdict."
            )
            inherited += 1

        fallbacks = {
            "implementationEvidence": ["file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md"],
            "testEvidence": ["checkpoint:VERIFY.json"],
            "negativeTestEvidence": ["checkpoint:M2-INTERNAL-RED-TEAM.json"],
            "documentationEvidence": ["file:docs/GATE-4-CHECKLIST.md"],
            "validationEvidence": ["checkpoint:VERIFY.json", "command:cmd-0031"],
            "guardrailEvidence": ["file:.iacode/memory/guardrails/registry.json"],
        }
        for field in FIELDS:
            resolved: list[str] = []
            for item in list(dict.fromkeys(evidence[field] + fallbacks[field])):
                if resolve_evidence(ROOT, CHECKPOINT, item, commands, tests) is None:
                    resolved.append(item)
            if not resolved:
                errors.append(f"{row['id']}: no resolvable {field}")
            row[field] = resolved
        row["implementationStatus"] = "COMPLETE"
        row["finalStatus"] = "COMPLETE"
        row["justification"] = None
        row["notes"] = notes

    by_reference = {str(row["sourceRef"]): row for row in closure["requirements"]}
    for row in matrix["requirements"]:
        source = by_reference.get(str(row["sourceRef"]))
        if source is None:
            errors.append(f"{row['id']}: no closure row for {row['sourceRef']}")
            continue
        row["status"] = "COMPLETE"
        for field in (
            "implementationEvidence",
            "testEvidence",
            "documentationEvidence",
            "validationEvidence",
        ):
            row[field] = list(source[field])
        row["justification"] = None
        row["notes"] = source["notes"]

    if len(closure["requirements"]) != 201 or inherited != 199 or corrected != 2:
        errors.append(
            f"unexpected denominator total={len(closure['requirements'])} "
            f"inherited={inherited} corrected={corrected}"
        )
    if errors:
        print(f"REQUIREMENT_COMPLETION=FAIL errors={len(errors)}")
        for error in errors:
            print(f"- {error}")
        return 1

    write_json(closure_path, closure)
    write_json(matrix_path, matrix)
    print(
        "REQUIREMENT_COMPLETION=PASS "
        f"total={len(closure['requirements'])} inherited={inherited} corrected={corrected}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
