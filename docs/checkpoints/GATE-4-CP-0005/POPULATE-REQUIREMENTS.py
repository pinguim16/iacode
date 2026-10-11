"""Populate GATE-4-CP-0005 evidence without changing its derived requirement set.

Canonical Gate 4 and unaffected lesson requirements inherit only resolvable file/test evidence from
the sealed implementing checkpoint.  G4-F-002, the asynchronous-observation recurrence, the new
verification-ownership lesson, and all twenty attacks receive current corrective evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CHECKPOINT = Path(__file__).resolve().parent
ROOT = CHECKPOINT.parents[2]
PRIOR = ROOT / "docs" / "checkpoints" / "GATE-4-CP-0003"
FIELDS = (
    "implementationEvidence",
    "testEvidence",
    "negativeTestEvidence",
    "documentationEvidence",
    "validationEvidence",
    "guardrailEvidence",
)
DEFAULTS = {
    "implementationEvidence": ["file:docs/checkpoints/GATE-4-CP-0003/FINAL-REPORT.md"],
    "testEvidence": ["file:docs/checkpoints/GATE-4-CP-0003/TESTS.json"],
    "negativeTestEvidence": ["file:docs/checkpoints/GATE-4-CP-0003/M2-INTERNAL-RED-TEAM.json"],
    "documentationEvidence": ["file:docs/GATE-4-CHECKLIST.md"],
    "validationEvidence": ["file:docs/checkpoints/GATE-4-CP-0003/VERIFY.json"],
    "guardrailEvidence": ["file:.iacode/memory/guardrails/registry.json"],
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def retained(references: list[str], fallback: list[str]) -> list[str]:
    kept: list[str] = []
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
            "file:scripts/iacode/verify.py",
            "file:scripts/iacode/compose.py",
            "file:scripts/iacode/observability.py",
            "file:infra/tests/test_running_stack.py",
            "file:scripts/iacode/smoke.py",
            "file:scripts/iacode/scenarios/verification_order_isolation.py",
        ],
        "testEvidence": [
            "test:test_full_verification_uses_a_checkout_owned_compose_project_and_dynamic_ports",
            "test:test_each_stage_receives_the_frozen_verification_environment",
            "test:test_cleanup_refuses_the_shared_developer_project",
            "test:test_live_stack_stage_builds_every_image_before_it_is_exercised",
            "test:test_prometheus_observation_waits_on_the_versioned_scrape_cycle",
            "test:test_order_isolation_probe_preserves_the_historical_contiguous_stage_order",
            "checkpoint:ORDER-ISOLATION-PROBE.json",
        ],
        "negativeTestEvidence": [
            "file:docs/checkpoints/GATE-4-CP-0004/VERIFICATION-REPORT.json",
            "file:docs/checkpoints/GATE-4-CP-0004/CLEAN-CLONE-REPORT.json",
        ],
        "documentationEvidence": [
            "file:docs/adr/ADR-0033-verification-runtime-is-owned-by-one-checkout.md",
            "file:docs/runbooks/QUALITY-ENGINE.md",
            "checkpoint:BASELINE.md",
        ],
        "validationEvidence": [
            "checkpoint:VERIFY.json",
            "checkpoint:PUBLISHED-CLEAN-CLONE-REPORT.json",
            "checkpoint:G4-CP-0004-FINDINGS-CLOSURE.json",
        ],
        "guardrailEvidence": [
            "file:.iacode/memory/guardrails/registry.json",
            "file:.iacode/memory/lessons.jsonl",
            "file:.iacode/memory/retrospectives/GATE-4-CP-0005.md",
        ],
    }


def observation_evidence() -> dict[str, list[str]]:
    evidence = correction_evidence()
    evidence["implementationEvidence"] = [
        "file:scripts/iacode/observability.py",
        "file:infra/tests/test_running_stack.py",
        "file:scripts/iacode/smoke.py",
        "file:infra/prometheus/prometheus.yml",
    ]
    evidence["testEvidence"] = [
        "test:test_prometheus_observation_waits_on_the_versioned_scrape_cycle",
        "checkpoint:ORDER-ISOLATION-PROBE.json",
        "checkpoint:VERIFY.json",
    ]
    return evidence


def publication_evidence() -> dict[str, list[str]]:
    return {
        "implementationEvidence": [
            "checkpoint:RUN-PUBLISHED-FULL-VERIFICATION.py",
        ],
        "testEvidence": [
            "test:test_published_full_verification_counts_the_canonical_result_field",
            "test:test_published_report_reconciliation_allows_only_the_generated_report",
        ],
        "negativeTestEvidence": [
            "command:cmd-0052",
            "file:.iacode/memory/retrospectives/GATE-4-CP-0005.md",
        ],
        "documentationEvidence": [
            "file:.iacode/memory/retrospectives/GATE-4-CP-0005.md",
        ],
        "validationEvidence": [
            "checkpoint:VERIFY.json",
            "checkpoint:PUBLISHED-CLEAN-CLONE-REPORT.json",
            "command:cmd-0058",
        ],
        "guardrailEvidence": [
            "file:.iacode/memory/guardrails/registry.json",
            "file:.iacode/memory/lessons.jsonl",
        ],
    }


def assurance_evidence() -> dict[str, list[str]]:
    return {
        "implementationEvidence": [
            "file:scripts/development-ledger/green_keeper.py",
            "file:scripts/development-ledger/finalize_checkpoint.py",
        ],
        "testEvidence": [
            "test:test_green_keeper_declares_its_in_progress_evidence_dirty_before_validation",
            "test:test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes",
        ],
        "negativeTestEvidence": [
            "checkpoint:REWORK-LOG.jsonl",
            "file:.iacode/memory/retrospectives/GATE-4-CP-0005.md",
        ],
        "documentationEvidence": [
            "file:.iacode/memory/retrospectives/GATE-4-CP-0005.md",
        ],
        "validationEvidence": [
            "command:cmd-0089",
            "checkpoint:REWORK-LOG.jsonl",
        ],
        "guardrailEvidence": [
            "file:.iacode/memory/guardrails/registry.json",
            "file:.iacode/memory/lessons.jsonl",
        ],
    }


def attack_evidence(identifier: str) -> dict[str, list[str]]:
    implementation = ["file:scripts/development-ledger/gate4_red_team.py"]
    if identifier in "ABCDEFGHIJQRS":
        implementation += [
            "file:services/evaluator/src/iacode_evaluator/verdict.py",
            "file:services/evaluator/src/iacode_evaluator/evidence.py",
        ]
    elif identifier in "KLMNO":
        implementation += ["file:scripts/development-ledger/review_bundle.py"]
    elif identifier in "PT":
        implementation += [
            "file:scripts/iacode/verify.py",
            "file:scripts/iacode/scenarios/verification_order_isolation.py",
        ]
    evidence = {
        "implementationEvidence": implementation,
        "testEvidence": [
            "file:docs/checkpoints/GATE-4-CP-0004/GATE-4-INDEPENDENT-RED-TEAM.json",
        ],
        "negativeTestEvidence": [
            "file:docs/checkpoints/GATE-4-CP-0004/GATE-4-INDEPENDENT-RED-TEAM.json",
        ],
        "documentationEvidence": [
            "file:docs/checkpoints/GATE-4-CP-0004/INDEPENDENT-RED-TEAM-REPORT.md",
        ],
        "validationEvidence": [
            "checkpoint:VERIFY.json",
        ],
        "guardrailEvidence": ["file:scripts/development-ledger/gate4_red_team.py"],
    }
    if identifier == "Q":
        evidence["negativeTestEvidence"].append(
            "file:docs/checkpoints/GATE-4-CP-0004/G4-X7-INDEPENDENT-PROBE.json"
        )
    return evidence


def main() -> None:
    document = load(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    prior = {
        row["sourceRef"]: row
        for row in load(PRIOR / "CLOSURE-REQUIREMENTS.json")["requirements"]
    }
    inherited = 0
    corrected = 0
    attacks = 0
    for row in document["requirements"]:
        reference = row["sourceRef"]
        if reference.startswith("attack:"):
            complete(
                row,
                attack_evidence(reference.removeprefix("attack:")),
                "Preserved unchanged from the sealed independent twenty-attack battery; the current internal replay follows completeness in the mandatory delivery order.",
            )
            attacks += 1
        elif reference in {"finding:G4-F-002", "lesson:LSN-0095"}:
            complete(row, correction_evidence(), "Closed by the G4-F-002 deterministic-verification correction.")
            corrected += 1
        elif reference == "lesson:LSN-0049":
            complete(row, observation_evidence(), "Re-proved after the Prometheus observer guardrail recurred in infrastructure verification.")
            corrected += 1
        elif reference == "lesson:LSN-0096":
            complete(row, publication_evidence(), "Guarded after cmd-0052 exposed a noncanonical publication result alias.")
            corrected += 1
        elif reference == "lesson:LSN-0011":
            complete(row, assurance_evidence(), "Re-proved after Green Keeper cycle 1 exposed its own append-only dirty-state transition.")
            corrected += 1
        elif reference in prior and (
            reference.startswith("canonical:") or reference.startswith("lesson:")
        ):
            previous = prior[reference]
            if previous["finalStatus"] != "COMPLETE":
                raise RuntimeError(f"sealed predecessor row is not complete: {reference}")
            evidence = {field: retained(previous[field], DEFAULTS[field]) for field in FIELDS}
            complete(
                row,
                evidence,
                "Inherited from sealed Gate 4 implementation evidence and revalidated by the published complete verifier.",
            )
            inherited += 1
        else:
            raise RuntimeError(f"no evidence policy for derived requirement {reference}")

    if (inherited, corrected, attacks, len(document["requirements"])) != (196, 5, 20, 221):
        raise RuntimeError(
            "unexpected denominator: "
            f"inherited={inherited} corrected={corrected} attacks={attacks} "
            f"total={len(document['requirements'])}"
        )
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.json").write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        "REQUIREMENT_EVIDENCE_POPULATED "
        f"inherited={inherited} corrected={corrected} attacks={attacks}"
    )


if __name__ == "__main__":
    main()
