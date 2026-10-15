#!/usr/bin/env python3
"""Bind the derived requirement set to sealed baseline and fresh corrective evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0009"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from delivery_assurance import collect_test_ids, load_command_results, resolve_evidence
from derive_requirements import EVIDENCE_FIELDS, render_closure, render_matrix
from ledger_common import LedgerError, load_json, write_json


def historical(reference: str) -> str:
    kind, _, value = reference.partition(":")
    if kind == "checkpoint":
        return f"file:docs/checkpoints/{SUBJECT}/{value}"
    if kind == "command":
        return f"file:docs/checkpoints/{SUBJECT}/COMMANDS.jsonl"
    return reference


def corrective(reference: str) -> dict[str, list[str]] | None:
    cancellation = reference in {"lesson:LSN-0098", "lesson:LSN-0111"} or any(
        reference.startswith(f"canonical:GATE-4#{section}.") for section in ("12", "16")
    )
    cadence = reference in {
        "canonical:GATE-4#20.6", "canonical:GATE-4#20.7", "canonical:GATE-4#20.8",
        "lesson:LSN-0104",
    }
    bookkeeping = reference == "lesson:LSN-0011"
    compatibility = reference in {"lesson:LSN-0012", "lesson:LSN-0113"}
    fixture = reference in {"lesson:LSN-0103", "lesson:LSN-0105"}
    output_security = reference in {
        "canonical:GATE-4#19.2", "canonical:GATE-4#20.1", "lesson:LSN-0091",
        "lesson:LSN-0106", "lesson:LSN-0107", "lesson:LSN-0110", "lesson:LSN-0112",
    }
    timestamp = reference == "lesson:LSN-0108"
    collection = reference == "lesson:LSN-0109"
    if not (cancellation or cadence or bookkeeping or fixture or output_security
            or timestamp or collection or compatibility):
        return None
    evidence = {field: [] for field in EVIDENCE_FIELDS}
    evidence["validationEvidence"] = ["checkpoint:VERIFY.json", "checkpoint:FUNCTIONAL-SCENARIOS.json"]
    evidence["negativeTestEvidence"] = ["checkpoint:FINDINGS.json"]
    evidence["guardrailEvidence"] = ["file:.iacode/memory/guardrails/registry.json"]
    if cancellation:
        evidence["implementationEvidence"] = [
            "file:services/evaluator/src/iacode_evaluator/workflow.py",
            "file:services/evaluator/src/iacode_evaluator/store.py",
            "file:services/evaluator/src/iacode_evaluator/verdict.py",
        ]
        evidence["testEvidence"] = [
            "test:test_durable_cancellation_at_activity_completion_finishes_without_a_signal",
            "test:test_durable_cancellation_during_result_write_finishes_without_a_signal",
            "test:test_durable_cancellation_during_verdict_write_finishes_without_a_signal",
            "test:test_concurrent_cancellation_and_verdict_have_one_winner",
            "test:test_unrelated_activity_failure_is_not_hidden_as_cancellation",
            "test:test_cancellation_preserves_the_digest_of_an_already_failing_derivation",
            "test:test_completed_check_joins_cancelled_durable_read_without_cancelling_run",
            "test:test_unrelated_watcher_failure_is_not_hidden_by_join_cleanup",
            "test:test_precompleted_watcher_cancellation_is_not_claimed_as_own_cleanup",
            "test:test_durable_read_completion_after_handle_clear_keeps_cancellation_authoritative",
        ]
        evidence["documentationEvidence"] = [
            "file:docs/adr/ADR-0038-cancellation-and-verdict-commit-are-serialized.md",
            "file:docs/adr/ADR-0041-polling-cleanup-preserves-completed-checks.md",
        ]
        evidence["validationEvidence"] += ["checkpoint:QUALITY-CANCELLATION-GUARDRAIL.json", "checkpoint:QUALITY-CANCELLATION-ISOLATION.json"]
    elif cadence:
        evidence["implementationEvidence"] = ["file:docs/DEVELOPMENT-CONTRACT.md", "file:scripts/development-ledger/validate_checkpoint.py"]
        evidence["testEvidence"] = ["test:test_internal_closure_cannot_claim_independent_review_or_red_team", "test:test_internal_closure_leaves_independent_milestone_validation_pending"]
        evidence["documentationEvidence"] = ["file:docs/MILESTONE-VALIDATION.md", "file:docs/adr/ADR-0037-intermediate-gates-use-internal-closure.md", "checkpoint:AUTHORIZATION.md"]
    elif bookkeeping:
        evidence["implementationEvidence"] = ["file:scripts/development-ledger/sync_in_progress_metadata.py", "checkpoint:audit-harness/run_checkpoint_validation.py"]
        evidence["testEvidence"] = ["test:InProgressMetadataTests"]
        evidence["documentationEvidence"] = ["file:scripts/development-ledger/README.md", "checkpoint:DECISIONS.md"]
    elif compatibility:
        evidence["implementationEvidence"] = ["file:.iacode/memory/POLICY.json",
                                               "file:scripts/development-ledger/validate_checkpoint.py"]
        evidence["testEvidence"] = ["test:test_live_policy_requires_strict_internal_verdict_semantics",
                                    "test:test_legacy_internal_red_team_fields_keep_their_subject_policy_semantics",
                                    "test:test_every_sealed_checkpoint_validates_from_its_own_tag"]
        evidence["documentationEvidence"] = [
            "file:docs/adr/ADR-0042-internal-verdict-semantics-follow-subject-policy.md",
        ]
        evidence["validationEvidence"] += ["checkpoint:POLICY-COMPATIBILITY.json"]
    elif output_security:
        evidence["implementationEvidence"] = [
            "file:services/sandbox/src/iacode_sandbox/output_security.py",
            "file:services/sandbox/src/iacode_sandbox/service.py",
            "file:packages/common/src/iacode_common/secret_scanning.py",
            "file:scripts/iacode/scenarios/quality_engine_e2e.py",
            "file:scripts/development-ledger/secret_scan.py",
        ]
        evidence["testEvidence"] = [
            "test:test_canonical_secret_output_is_rejected_before_durable_delivery",
            "test:test_canonical_secret_output_never_becomes_the_activity_response",
            "test:test_canonical_secret_output_workspace_diagnostic_never_reaches_session_record",
            "test:test_json_escaped_secret_is_refused_before_persistence_and_after_legacy_read",
            "test:test_live_output_control_timeout_retains_bounded_diagnostics_and_stays_red",
            "test:PublicationTransportScanningTests",
        ]
        evidence["documentationEvidence"] = [
            "file:docs/adr/ADR-0039-sandbox-output-is-scanned-before-durable-delivery.md",
            "checkpoint:HISTORICAL-SCAN-REVIEW.md",
        ]
        evidence["validationEvidence"] += ["checkpoint:QUALITY-OUTPUT-CONTAINMENT.json",
                                           "checkpoint:QUALITY-OUTPUT-ISOLATION.json"]
    elif timestamp:
        evidence["implementationEvidence"] = ["file:scripts/development-ledger/ledger_common.py"]
        evidence["testEvidence"] = ["test:test_lesson_timestamp_transport_rejects_locale_rendering"]
        evidence["documentationEvidence"] = ["checkpoint:FINDINGS.json"]
    elif collection:
        evidence["implementationEvidence"] = ["file:scripts/development-ledger/policies.py",
                                               "file:.iacode/policies/test-suites.json"]
        evidence["testEvidence"] = ["test:TestSuiteInputRepositoriesTests"]
        evidence["documentationEvidence"] = [
            "file:docs/adr/ADR-0040-test-counts-follow-policy-bound-collection.md",
        ]
    else:
        evidence["implementationEvidence"] = ["file:services/evaluator/tests/test_persistence.py", "file:scripts/iacode/gates/lint.py"]
        evidence["testEvidence"] = ["test:test_verdict_before_cancellation_refuses_late_acceptance", "test:test_mandatory_lint_covers_every_python_project_root"]
        evidence["documentationEvidence"] = ["checkpoint:FINDINGS.json", "checkpoint:DECISIONS.md"]
    return evidence


def main() -> int:
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    if (verification.get("result") != "PASS" or verification.get("fast") is not False
            or publication.get("result") != "PASS"
            or not all(item.get("result") == "PASS" for item in verification["stages"])):
        raise LedgerError("the complete published verifier must pass before requirement completion")
    raw = subprocess.run(
        ["git", "show", f"iacode-checkpoints/{SUBJECT}:docs/checkpoints/{SUBJECT}/CLOSURE-REQUIREMENTS.json"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    previous = {row["sourceRef"]: row for row in json.loads(raw)["requirements"]}
    closure = deepcopy(load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json"))
    matrix = deepcopy(load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json"))
    tests, commands = collect_test_ids(ROOT), load_command_results(CHECKPOINT)
    by_reference = {}
    for row in closure["requirements"]:
        reference = row["sourceRef"]
        evidence = corrective(reference)
        if evidence is None:
            prior = previous.get(reference)
            if prior is None or prior.get("finalStatus") != "COMPLETE":
                raise LedgerError(f"no complete baseline or corrective mapping for {reference}")
            evidence = {field: [historical(value) for value in prior.get(field, [])] for field in EVIDENCE_FIELDS}
            evidence["validationEvidence"].append("checkpoint:VERIFY.json")
            row["notes"] = "Sealed CP0009 implementation evidence, re-executed by the complete CP0010 published verifier; not independent validation."
        else:
            row["notes"] = "Direct CP0010 corrective proof and complete published verification; internal evidence only."
        for field, references in evidence.items():
            row[field] = list(dict.fromkeys(references))
            if not row[field]:
                raise LedgerError(f"{reference} has no {field}")
            for value in row[field]:
                error = resolve_evidence(ROOT, CHECKPOINT, value, commands, tests)
                if error is not None:
                    raise LedgerError(f"{reference}: {error}")
        row["implementationStatus"] = row["finalStatus"] = "COMPLETE"
        row["justification"] = None
        by_reference[reference] = row
    for row in matrix["requirements"]:
        source = by_reference[row["sourceRef"]]
        row["status"], row["justification"], row["notes"] = "COMPLETE", None, source["notes"]
        for field in ("implementationEvidence", "testEvidence", "documentationEvidence", "validationEvidence"):
            row[field] = list(source[field])
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    write_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json", matrix)
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(render_closure(closure), encoding="utf-8", newline="\n")
    (CHECKPOINT / "REQUIREMENTS-MATRIX.md").write_text(render_matrix(matrix), encoding="utf-8", newline="\n")
    print(f"REQUIREMENT_COMPLETION=PASS total={len(by_reference)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
