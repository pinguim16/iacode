"""Populate GATE-4-CP-0003 closure evidence from sealed inheritance and corrective proof.

This checkpoint has 216 derived rows.  The 194 Gate 4 implementation rows remain anchored in the
sealed GATE-4-CP-0001 delivery except for canonical row 19.2, which the independent audit
invalidated and this checkpoint re-proves.  The audit finding, its A-Q battery, and the three new
corrective lessons receive current evidence.  The inherited LSN-0053 row and the bundle-context
lesson also receive current
evidence because its sandbox guardrail recurred during closure.  The script changes evidence and
status only; the canonical derivation tool still owns the row set, identifiers, descriptions, and
ordering.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CHECKPOINT = Path(__file__).resolve().parent
ROOT = CHECKPOINT.parents[2]
PRIOR = ROOT / "docs" / "checkpoints" / "GATE-4-CP-0001"
FIELDS = (
    "implementationEvidence",
    "testEvidence",
    "negativeTestEvidence",
    "documentationEvidence",
    "validationEvidence",
    "guardrailEvidence",
)
DEFAULTS = {
    "implementationEvidence": ["file:docs/checkpoints/GATE-4-CP-0001/FINAL-REPORT.md"],
    "testEvidence": ["file:docs/checkpoints/GATE-4-CP-0001/TESTS.json"],
    "negativeTestEvidence": [
        "file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json"
    ],
    "documentationEvidence": ["file:docs/GATE-4-CHECKLIST.md"],
    "validationEvidence": ["file:docs/checkpoints/GATE-4-CP-0001/VERIFY.json"],
    "guardrailEvidence": ["file:.iacode/memory/guardrails/registry.json"],
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def retained(references: list[str], fallback: list[str]) -> list[str]:
    kept = []
    for reference in references:
        if reference.startswith("test:"):
            kept.append(reference)
        elif reference.startswith("file:") and (ROOT / reference.removeprefix("file:")).is_file():
            kept.append(reference)
    return list(dict.fromkeys(kept or fallback))


def complete(row: dict[str, Any], evidence: dict[str, list[str]], notes: str) -> None:
    row["implementationStatus"] = "COMPLETE"
    row["finalStatus"] = "COMPLETE"
    row["justification"] = None
    row["notes"] = notes
    for field in FIELDS:
        row[field] = list(dict.fromkeys(evidence[field]))


def correction_evidence() -> dict[str, list[str]]:
    return {
        "implementationEvidence": [
            "file:packages/common/src/iacode_common/secret_scanning.py",
            "file:services/evaluator/src/iacode_evaluator/evidence.py",
            "file:services/evaluator/src/iacode_evaluator/activities.py",
        ],
        "testEvidence": [
            "test:test_canonical_secret_is_rejected_before_any_durable_operation",
            "test:test_scanner_failure_is_fail_closed_before_any_durable_operation",
            "test:test_secret_bearing_legacy_object_cannot_resolve",
            "test:test_secret_bearing_execution_is_contained_and_derives_fail",
            "command:cmd-0008",
            "command:cmd-0017",
        ],
        "negativeTestEvidence": ["command:cmd-0017"],
        "documentationEvidence": [
            "file:docs/adr/ADR-0032-quality-evidence-is-scanned-before-durable-commit.md",
            "file:docs/runbooks/QUALITY-ENGINE.md",
        ],
        "validationEvidence": [
            "checkpoint:G4-CP-0002-FINDINGS-CLOSURE.json",
            "command:cmd-0015",
            "command:cmd-0016",
        ],
        "guardrailEvidence": [
            "file:.iacode/memory/guardrails/registry.json",
            "file:.iacode/memory/lessons.jsonl",
        ],
    }


def parser_evidence() -> dict[str, list[str]]:
    return {
        "implementationEvidence": ["file:scripts/development-ledger/policies.py"],
        "testEvidence": [
            "test:test_a_blocking_finding_paragraph_in_a_sealed_audit_is_parsed",
            "test:test_blocking_finding_prose_is_bounded_to_its_section",
            "command:cmd-0004",
        ],
        "negativeTestEvidence": [
            "test:test_a_report_whose_findings_cannot_be_parsed_is_refused_rather_than_read_as_empty"
        ],
        "documentationEvidence": ["checkpoint:DECISIONS.md"],
        "validationEvidence": ["command:cmd-0013", "command:cmd-0016"],
        "guardrailEvidence": [
            "file:.iacode/memory/guardrails/registry.json",
            "file:.iacode/memory/lessons.jsonl",
        ],
    }


def fixture_packaging_evidence() -> dict[str, list[str]]:
    return {
        "implementationEvidence": [
            "file:scripts/development-ledger/promotion_fixture.py",
            "file:tests/test_development_ledger.py",
        ],
        "testEvidence": [
            "test:test_disposable_ledger_runtime_carries_its_canonical_scanner_dependency",
            "test:test_repaired_gate_is_reported_as_green_in_a_new_cycle",
            "test:test_full_delivery_assurance_flow_reaches_ready_for_review",
            "command:cmd-0023",
            "command:cmd-0033",
        ],
        "negativeTestEvidence": [],
        "documentationEvidence": ["file:.iacode/memory/LESSONS.md"],
        "validationEvidence": ["command:cmd-0023"],
        "guardrailEvidence": [
            "file:.iacode/memory/guardrails/registry.json",
            "file:.iacode/memory/lessons.jsonl",
        ],
    }


def sandbox_reaping_evidence() -> dict[str, list[str]]:
    return {
        "implementationEvidence": [
            "file:services/sandbox/src/iacode_sandbox/helper.py",
            "file:services/sandbox/tests/test_sandbox_helper.py",
        ],
        "testEvidence": [
            "test:test_the_sweep_waits_for_zombies_to_be_reaped_before_returning",
            "test:test_a_fork_bomb_that_detaches_leaves_a_sandbox_that_still_answers",
            "command:cmd-0069",
        ],
        "negativeTestEvidence": [],
        "documentationEvidence": ["file:.iacode/memory/LESSONS.md"],
        "validationEvidence": ["command:cmd-0069"],
        "guardrailEvidence": [
            "file:.iacode/memory/guardrails/registry.json",
            "file:.iacode/memory/lessons.jsonl",
        ],
    }


def review_bundle_context_evidence() -> dict[str, list[str]]:
    return {
        "implementationEvidence": [
            "file:scripts/development-ledger/review_bundle.py",
            "file:tests/test_gate4_quality_engine.py",
        ],
        "testEvidence": [
            "test:test_review_context_includes_unchanged_migrations_schemas_and_policies",
            "command:cmd-0098",
        ],
        "negativeTestEvidence": ["command:cmd-0099"],
        "documentationEvidence": ["file:.iacode/memory/LESSONS.md"],
        "validationEvidence": ["checkpoint:REVIEW-BUNDLE-VALIDATION.json"],
        "guardrailEvidence": [
            "file:.iacode/memory/guardrails/registry.json",
            "file:.iacode/memory/lessons.jsonl",
        ],
    }


def attack_evidence(identifier: str) -> dict[str, list[str]]:
    if identifier in "ABCDEFGHIJ":
        implementation = [
            "file:services/evaluator/src/iacode_evaluator/verdict.py",
            "file:packages/contracts/src/iacode_contracts/quality.py",
        ]
    elif identifier in "KLMNO":
        implementation = ["file:scripts/development-ledger/review_bundle.py"]
    elif identifier == "P":
        implementation = [
            "file:scripts/iacode/scenarios/quality_engine_e2e.py",
            "file:scripts/iacode/scenarios/sandbox_coding_e2e.py",
            "file:scripts/iacode/verify.py",
        ]
    else:
        return correction_evidence()
    return {
        "implementationEvidence": implementation,
        "testEvidence": ["command:cmd-0017"],
        "negativeTestEvidence": [
            "file:docs/checkpoints/GATE-4-CP-0002/GATE-4-INDEPENDENT-RED-TEAM.json",
            "command:cmd-0017",
        ],
        "documentationEvidence": [
            "file:docs/checkpoints/GATE-4-CP-0002/RED-TEAM-REPORT.md"
        ],
        "validationEvidence": ["command:cmd-0017"],
        "guardrailEvidence": ["file:scripts/development-ledger/gate4_red_team.py"],
    }


def main() -> None:
    document = load(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    prior = {
        row["sourceRef"]: row
        for row in load(PRIOR / "CLOSURE-REQUIREMENTS.json")["requirements"]
    }
    inherited = 0
    corrected = 0
    for row in document["requirements"]:
        reference = row["sourceRef"]
        if reference == "lesson:LSN-0053":
            complete(
                row,
                sandbox_reaping_evidence(),
                "Re-proved after the sandbox process-sweep guardrail recurred during closure.",
            )
            corrected += 1
        elif reference in prior and reference != "canonical:GATE-4#19.2":
            previous = prior[reference]
            if previous["finalStatus"] != "COMPLETE":
                raise RuntimeError(f"sealed predecessor row is not complete: {reference}")
            evidence = {
                field: retained(previous[field], DEFAULTS[field]) for field in FIELDS
            }
            complete(
                row,
                evidence,
                "Inherited from the sealed Gate 4 implementation and revalidated by this corrective delivery.",
            )
            inherited += 1
        elif reference in {
            "canonical:GATE-4#19.2",
            "finding:G4-F-001",
            "lesson:LSN-0091",
        }:
            complete(row, correction_evidence(), "Closed by the G4-F-001 corrective slice.")
            corrected += 1
        elif reference == "lesson:LSN-0092":
            complete(row, parser_evidence(), "Closed by the bounded sealed-report parser repair.")
            corrected += 1
        elif reference == "lesson:LSN-0093":
            complete(
                row,
                fixture_packaging_evidence(),
                "Closed by the disposable ledger runtime packaging repair.",
            )
            corrected += 1
        elif reference == "lesson:LSN-0094":
            complete(
                row,
                review_bundle_context_evidence(),
                "Closed by collecting unchanged canonical review context in the bundle.",
            )
            corrected += 1
        elif reference.startswith("attack:"):
            identifier = reference.removeprefix("attack:")
            complete(
                row,
                attack_evidence(identifier),
                "Replayed by the current internal Red Team over a valid null control.",
            )
            corrected += 1
        else:
            raise RuntimeError(f"no evidence policy for derived requirement {reference}")

    if inherited != 192 or corrected != 24 or len(document["requirements"]) != 216:
        raise RuntimeError(
            f"unexpected denominator: inherited={inherited} corrected={corrected} "
            f"total={len(document['requirements'])}"
        )
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.json").write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"REQUIREMENT_EVIDENCE_POPULATED inherited={inherited} corrected={corrected}")


if __name__ == "__main__":
    main()
