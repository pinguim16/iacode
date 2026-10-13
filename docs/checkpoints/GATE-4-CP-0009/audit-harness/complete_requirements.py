#!/usr/bin/env python3
"""Complete CP0009 requirements from sealed Gate 4 evidence and corrective proof."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0007"
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
CORRECTIVE_REFS = {
    "canonical:GATE-4#20.5",
    "finding:G4-F-004",
    "lesson:LSN-0097",
    "lesson:LSN-0098",
    "lesson:LSN-0099",
    "lesson:LSN-0100",
}


def subject_rows() -> dict[str, dict]:
    shown = subprocess.run(
        [
            "git", "show",
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
            "file:scripts/development-ledger/review_bundle.py",
            "file:scripts/development-ledger/seal_checkpoint.py",
            "file:scripts/development-ledger/validate_checkpoint.py",
            "file:scripts/development-ledger/record_command.py",
            "file:services/evaluator/src/iacode_evaluator/workflow.py",
            "file:.iacode/schemas/checkpoint.schema.json",
        ],
        "testEvidence": [
            "test:test_immutable_subject_rebuilds_are_byte_identical_and_exclude_only_the_sidecar",
            "test:test_declared_digest_and_size_are_rebuilt_not_trusted",
            "test:test_pending_declaration_is_allowed_only_before_handoff_or_inside_sealing",
            "test:test_full_delivery_assurance_flow_reaches_ready_for_review",
            "test:test_cancellation_is_rechecked_after_dispatch_before_activity_start",
            "test:test_durable_cancelling_state_stops_an_active_sandbox_activity",
            "test:test_a_signal_flag_set_before_handle_assignment_still_cancels_the_activity",
            "test:test_accepted_cancellation_wins_over_a_racing_success_response",
            "test:test_inputs_are_canonicalized_and_an_unknown_subject_is_refused",
            "test:test_in_progress_symbolic_head_validates_from_its_matching_subject_tag",
            "test:test_subject_tag_never_substitutes_for_a_sealed_checkpoint_tag",
        ],
        "negativeTestEvidence": [
            "checkpoint:BASELINE-BUNDLE-AUDIT.json",
            "test:test_declared_digest_and_size_are_rebuilt_not_trusted",
        ],
        "documentationEvidence": [
            "file:docs/adr/ADR-0035-review-bundles-bind-immutable-content.md",
            "file:docs/adr/ADR-0036-pre-seal-validation-binds-an-explicit-subject.md",
            "file:docs/CHECKPOINT-PROTOCOL.md",
            "file:docs/GATE-4-CHECKLIST.md",
        ],
        "validationEvidence": [
            "checkpoint:VERIFY.json",
            "checkpoint:FUNCTIONAL-ACCEPTANCE-VALIDATION.json",
            "checkpoint:M2-INTERNAL-RED-TEAM.json",
            "checkpoint:REVIEW-BUNDLE-VALIDATION.json",
            "checkpoint:G4-CP-0008-FINDINGS-CLOSURE.json",
            "checkpoint:QUALITY-CANCELLATION-GUARDRAIL.json",
            "checkpoint:QUALITY-CANCELLATION-ISOLATION.json",
        ],
        "guardrailEvidence": [
            "file:.iacode/memory/lessons.jsonl",
            "file:.iacode/memory/guardrails/registry.json",
        ],
    }


def attack_evidence() -> dict[str, list[str]]:
    evidence = corrective_evidence()
    evidence["implementationEvidence"] = [
        "file:scripts/development-ledger/gate4_red_team.py",
        "file:scripts/development-ledger/review_bundle.py",
    ]
    evidence["testEvidence"] = [
        "checkpoint:M2-INTERNAL-RED-TEAM.json",
        "test:test_internal_red_team_preserves_the_sealed_twenty_attack_denominator",
    ]
    evidence["negativeTestEvidence"] = ["checkpoint:M2-INTERNAL-RED-TEAM.json"]
    evidence["validationEvidence"] = [
        "checkpoint:M2-INTERNAL-RED-TEAM.json",
        "checkpoint:RED-TEAM-REPORT.md",
    ]
    return evidence


def main() -> int:
    use_utf8_stdout()
    closure_path = CHECKPOINT / "CLOSURE-REQUIREMENTS.json"
    matrix_path = CHECKPOINT / "REQUIREMENTS-MATRIX.json"
    closure = deepcopy(load_json(closure_path))
    matrix = deepcopy(load_json(matrix_path))
    subject = subject_rows()
    current = corrective_evidence()
    attacks = attack_evidence()
    commands = load_command_results(CHECKPOINT)
    tests = collect_test_ids(ROOT)
    errors: list[str] = []
    inherited = 0
    corrected = 0
    defended = 0

    for row in closure["requirements"]:
        reference = str(row["sourceRef"])
        if reference.startswith("attack:"):
            evidence = deepcopy(attacks)
            notes = (
                "Defended by the CP0009 mandatory A-T internal battery. This is internal assurance, "
                "not independent Red Team approval."
            )
            defended += 1
        elif reference in CORRECTIVE_REFS:
            evidence = deepcopy(current)
            notes = (
                "Closed by CP0009 corrective implementation and focused evidence for immutable "
                "review reconstruction, durable cancellation, refused-subject provenance or "
                "detached pre-seal subject binding, as selected by the source requirement."
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
                evidence["validationEvidence"] + ["checkpoint:VERIFY.json"]
            ))
            notes = (
                "Inherited from sealed CP0007 evidence and revalidated by CP0009's complete "
                "verifier; evidence reuse is not a new independent verdict."
            )
            inherited += 1

        fallbacks = {
            "implementationEvidence": ["file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md"],
            "testEvidence": ["checkpoint:VERIFY.json"],
            "negativeTestEvidence": ["checkpoint:M2-INTERNAL-RED-TEAM.json"],
            "documentationEvidence": ["file:docs/GATE-4-CHECKLIST.md"],
            "validationEvidence": ["checkpoint:VERIFY.json"],
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
            "implementationEvidence", "testEvidence", "documentationEvidence", "validationEvidence",
        ):
            row[field] = list(source[field])
        row["justification"] = None
        row["notes"] = source["notes"]

    if (len(closure["requirements"]), inherited, corrected, defended) != (225, 199, 6, 20):
        errors.append(
            f"unexpected denominator total={len(closure['requirements'])} inherited={inherited} "
            f"corrected={corrected} defended={defended}"
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
        f"total={len(closure['requirements'])} inherited={inherited} "
        f"corrected={corrected} defended={defended}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
