#!/usr/bin/env python3
"""Write CP0008 metadata and handoff for the blocking independent verdict."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0007"
SUBJECT_COMMIT = "e21d30fde473f302d0f8f60b59acf008fa52e250"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def command_rows() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def command_id(rows: list[dict[str, Any]], fragment: str, exit_code: int) -> str:
    matches = [
        row for row in rows
        if fragment in str(row.get("command")) and row.get("exitCode") == exit_code
    ]
    if not matches:
        raise RuntimeError(f"no command contains {fragment!r} with exit {exit_code}")
    return str(matches[-1]["id"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("pre-assurance", "final"), required=True)
    args = parser.parse_args()
    final = args.phase == "final"
    now = timestamp()
    records = command_rows()
    verifier_cmd = command_id(records, "run_published_full_verification.py", 0)
    bundle_cmd = command_id(records, "bundle_subject_audit.py", 1)
    probe_cmd = command_id(records, "run_g4x7_probe.py", 0)
    architecture_cmd = command_id(records, "architecture_review.py", 0)
    red_cmd = command_id(records, "independent_red_team.py", 1)
    anchor_cmd = command_id(records, "verify_integrity.py --rebuild", 0)

    matrix = load(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    requirements = matrix.get("requirements") or []
    counts = {
        name: sum(1 for row in requirements if row.get("status") == name)
        for name in ("COMPLETE", "PARTIAL", "MISSING", "NOT_APPLICABLE")
    }
    mandatory = sum(1 for row in requirements if row.get("mandatory") is True)
    preflight = load(CHECKPOINT / "LESSON-PREFLIGHT.json")
    chain = load(ROOT / ".iacode" / "anchors" / "checkpoint-chain.json")
    anchors = chain.get("anchors") or chain.get("checkpoints") or []
    cycles = [
        json.loads(line)
        for line in (CHECKPOINT / "REWORK-LOG.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    last_cycle = cycles[-1] if cycles else {}
    green = final and last_cycle.get("result") == "GREEN"
    completeness = (
        load(CHECKPOINT / "COMPLETENESS-REPORT.json")
        if final and (CHECKPOINT / "COMPLETENESS-REPORT.json").is_file()
        else {}
    )
    complete_ok = final and completeness.get("result") == "PASS"

    state = load(CHECKPOINT / "STATE.json")
    state.update({
        "phase": "Gate 4 fresh-session independent final audit of sealed GATE-4-CP-0007",
        "gate": "GATE-4",
        "status": "IN_PROGRESS",
        "branch": "main",
        "baseCommit": SUBJECT_COMMIT,
        "currentCommit": SUBJECT_COMMIT,
        "dirty": True,
        "updatedAt": now,
        "nextAllowedAction": (
            "Finalize, seal, tag and publish the REWORK_REQUIRED audit checkpoint; do not start Gate 5."
            if final else
            "Run Green Keeper, Delivery Completeness Validator and the internal closure mirror."
        ),
        "blockedBy": ["G4-F-004"],
        "secondToolValidation": {
            "status": "FAILED",
            "tool": "Codex desktop application, fresh session",
            "provider": "OpenAI",
            "model": "GPT-5",
            "validatedAt": now,
            "justification": "The published subject passed its full verifier, but its declared review-bundle digest was not reconstructible and attack T escaped.",
            "evidence": ["file:REVIEW-REPORT.md", "file:FINDINGS.json", f"command:{bundle_cmd}", f"command:{red_cmd}"],
        },
        "requirementsMatrix": {
            "path": "REQUIREMENTS-MATRIX.json",
            "total": len(requirements),
            "mandatory": mandatory,
            "complete": counts["COMPLETE"],
            "partial": counts["PARTIAL"],
            "missing": counts["MISSING"],
            "notApplicable": counts["NOT_APPLICABLE"],
            "coveragePercent": round(100.0 * counts["COMPLETE"] / len(requirements), 2),
        },
        "greenKeeper": {
            "status": "PASS" if green else "NOT_EXECUTED",
            "cycles": len(cycles),
            "remainingFailures": int(last_cycle.get("remainingFailures", 0)) if green else 0,
            "unresolvedReworkItems": 0,
            "log": "REWORK-LOG.jsonl",
            "externalBlockers": [],
            "requiredGates": last_cycle.get("requiredGates", []) if green else [],
            "evidence": last_cycle.get("commandsExecuted", []) if green else [],
        },
        "deliveryCompleteness": {
            "status": "PASS" if complete_ok else "NOT_EXECUTED",
            "report": "COMPLETENESS-REPORT.json",
            "coveragePercent": completeness.get("coveragePercent", 0.0),
            "evidenceCoveragePercent": completeness.get("evidenceCoveragePercent", 0.0),
            "auditor": (
                "Delivery Completeness Validator (audit checkpoint, not independent Gate approval)"
                if complete_ok else None
            ),
            "evidence": ["file:COMPLETENESS-REPORT.json"] if complete_ok else [],
        },
        "reworkCycles": len(cycles),
        "independentReview": {
            "status": "REWORK_REQUIRED",
            "tool": "Codex desktop application, OpenAI, GPT-5, fresh session",
            "reviewedAt": now,
            "justification": "G4-F-004 is HIGH: the sealed subject's declared review-bundle digest cannot be reconstructed from the published subject.",
            "evidence": ["file:REVIEW-REPORT.md", "file:FINDINGS.json", "file:FINAL-GATE-4-AUDIT-MATRIX.json"],
        },
        "redTeam": {
            "status": "RED_TEAM_FAIL",
            "tool": "Fresh-session Gate 4 independent adversarial harness",
            "executedAt": now,
            "justification": "Nineteen of twenty attacks were defended; attack T escaped because the declared bundle digest was not reconstructible.",
            "evidence": ["file:GATE-4-INDEPENDENT-RED-TEAM.json", "file:INDEPENDENT-RED-TEAM-REPORT.md", f"command:{red_cmd}"],
        },
        "lessonPreflight": {
            "path": "LESSON-PREFLIGHT.json",
            "gate": "GATE-4",
            "scope": "fresh-session independent Gate 4 final audit",
            "lessonsConsidered": preflight.get("lessonsConsidered", 0),
            "lessonsApplicable": preflight.get("lessonsApplicable", 0),
            "derivedRequirements": len(preflight.get("derivedRequirements") or []),
            "fingerprint": preflight.get("inputsFingerprint"),
            "evidence": ["checkpoint:LESSON-PREFLIGHT.json", "command:cmd-0002"],
        },
        "milestone": {
            "id": "M2",
            "title": "IACode V0 completion and experience",
            "gates": ["GATE 4", "GATE 5", "GATE 6", "GATE 7"],
            "status": "PENDING",
            "auditor": None,
            "auditedAt": None,
            "evidence": [],
        },
        "externalAuditRequired": False,
        "externalAuditReason": None,
        "guardrailEffectiveness": {
            "guardrailsTotal": 97,
            "guardrailsResolved": 97,
            "guardrailsTested": 97,
            "guardrailsEffective": 97,
            "guardrailFailures": 0,
            "evidence": ["file:.iacode/memory/guardrails/registry.json", f"command:{verifier_cmd}"],
        },
        "integrity": {
            "status": "PASS",
            "anchors": len(anchors),
            "chainFile": ".iacode/anchors/checkpoint-chain.json",
            "evidence": ["file:.iacode/anchors/checkpoint-chain.json", f"command:{anchor_cmd}"],
        },
        "externalAttestation": {
            "status": "PRESENT",
            "path": ".iacode/attestations/G4-CP-0008.json",
            "auditId": "G4-CP-0008",
            "subjectCheckpoint": SUBJECT,
            "subjectCommit": SUBJECT_COMMIT,
            "validationMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
            "evidence": ["file:REVIEW-REPORT.md", "file:INDEPENDENT-RED-TEAM-REPORT.md"],
        },
    })
    write(CHECKPOINT / "STATE.json", state)

    quality = load(CHECKPOINT / "QUALITY.json")
    quality["checks"]["build"] = {"status": "PASS", "evidence": [f"command:{verifier_cmd}", "file:VERIFICATION-REPORT.json"], "justification": None}
    quality["checks"]["unitTests"] = {"status": "PASS", "evidence": [f"command:{verifier_cmd}", "file:TESTS.json"], "justification": None}
    quality["checks"]["integrationTests"] = {"status": "PASS", "evidence": [f"command:{verifier_cmd}", "file:VERIFICATION-REPORT.json"], "justification": None}
    quality["checks"]["e2e"] = {"status": "PASS", "evidence": [f"command:{verifier_cmd}", "file:FUNCTIONAL-ACCEPTANCE-VALIDATION.json"], "justification": None}
    quality["checks"]["lint"] = {"status": "PASS", "evidence": [f"command:{verifier_cmd}"], "justification": None}
    quality["checks"]["staticAnalysis"] = {"status": "PASS", "evidence": [f"command:{architecture_cmd}", "file:ARCHITECTURE-REVIEW.json"], "justification": None}
    quality["checks"]["security"] = {"status": "PASS", "evidence": [f"command:{probe_cmd}", "file:G4-X7-INDEPENDENT-PROBE.json", "file:TRANSPORT-ATTACKS.json"], "justification": None}
    quality["checks"]["documentation"] = {"status": "PASS", "evidence": ["file:REVIEW-REPORT.md", "file:ARCHITECTURE-REVIEW.json"], "justification": None}
    quality["checks"]["redTeam"] = {"status": "FAIL", "evidence": ["file:GATE-4-INDEPENDENT-RED-TEAM.json"], "justification": "Attack T escaped because the declared subject bundle digest is not reconstructible; the preserved nonzero harness command is diagnostic evidence, not a passing quality input."}
    if final:
        gate_map = {row["gate"]: row["commandId"] for row in last_cycle.get("gateResults") or []}
        completeness_cmd = command_id(records, "check_completeness.py", 0)
        quality["checks"]["checkpointValidation"] = {"status": "PASS", "evidence": [f"command:{gate_map['checkpointValidation']}"], "justification": None}
        quality["checks"]["greenKeeper"] = {"status": "PASS", "evidence": ["file:REWORK-LOG.jsonl"], "justification": "Every policy-derived checkpoint-assurance gate passed; the independent subject finding remains blocking."}
        quality["checks"]["deliveryCompleteness"] = {"status": "PASS", "evidence": ["file:COMPLETENESS-REPORT.json", f"command:{completeness_cmd}"], "justification": "Audit coverage is complete; complete evidence does not imply approval."}
    write(CHECKPOINT / "QUALITY.json", quality)

    write(CHECKPOINT / "PROVENANCE.json", {
        "schemaVersion": "3.3.0",
        "artifacts": [{
            "artifact": "docs/checkpoints/GATE-4-CP-0008 and .iacode/attestations/G4-CP-0008.json",
            "sourceType": "repository-generated",
            "provider": "OpenAI",
            "model": "GPT-5",
            "ownership": "project",
            "license": "project-policy",
            "rights": {"storageAllowed": True, "ragAllowed": False, "trainingAllowed": False, "distillationAllowed": False},
            "evidence": "Fresh-session evidence derived from the sealed published subject and synthetic non-secret probes.",
            "notes": "No personal data, secret value, or private chain-of-thought is recorded.",
        }],
    })

    if final:
        (CHECKPOINT / "STATUS.md").write_text("# Status\n\nIN_PROGRESS\n", encoding="utf-8", newline="\n")
        (CHECKPOINT / "DIFF-SUMMARY.md").write_text(
            "# Diff Summary\n\nNo product path changed. This checkpoint adds only independent audit harnesses and evidence, the failed Gate 4 attestation, the predecessor anchor, and the LATEST pointer.\n",
            encoding="utf-8", newline="\n",
        )
        (CHECKPOINT / "RISKS.md").write_text(
            "# Risks\n\n`G4-F-004` proves that a producer-time review archive can be valid yet fail to represent the final sealed checkpoint. Promotion on that stale digest would make the review transport non-reproducible.\n",
            encoding="utf-8", newline="\n",
        )
        (CHECKPOINT / "NEXT.md").write_text(
            "# Next\n\n## Required next action\n\nOpen a new Gate 4 corrective checkpoint for `G4-F-004`. Make review transport derivable from final sealed content, prove a remote detached rebuild reproduces the declared digest, then repeat the mandatory delivery and later independent audit. Do not start Gate 5.\n",
            encoding="utf-8", newline="\n",
        )
        (CHECKPOINT / "HANDOFF.md").write_text("""# Handoff

Current Gate: GATE-4
Current Status: IN_PROGRESS

## Objective

Independently audit the sealed `GATE-4-CP-0007` subject without modifying product code.

## What was completed

Published subject identity, the single full 42-stage verifier, counts, architecture, functional acceptance, G4-X7, transport attacks, deterministic bundle rebuilds, the complete A-T Red Team, checkpoint assurance, and delivery completeness were executed.

## What was NOT completed

Gate 4 was not approved. M2 was not approved and Gate 5 was not started.

## Current repository state

See `STATE.json`; finalization records `REWORK_REQUIRED` with blocker `G4-F-004`.

## Files changed

See `FILES.json`; no product path changed.

## Important decisions

The valid and byte-identical rebuilt bundles characterize the failure; they do not replace CP0007's sealed declared digest.

## Tests executed

The published full verifier passed 42/42 in one invocation. Functional acceptance passed 12/12. The independent Red Team defended 19/20; attack T escaped.

## Known failures

`G4-F-004` (HIGH): CP0007's declared review-bundle digest and size cannot be reconstructed from its sealed published subject.

## Known risks

A stale producer-time bundle can be valid while misrepresenting the final sealed evidence set.

## Do not repeat

Do not treat archive validity or deterministic rebuilds as proof that a previously declared digest represents the final sealed content.

## Required next action

Open a corrective Gate 4 checkpoint, make review transport final-content-derived, and submit the sealed correction to a later independent audit.

## Exact continuation sequence

Lesson preflight, requirement derivation, baseline, plan, correction, tests, Green Keeper, completeness, internal Red Team, closure audit, `READY_FOR_REVIEW`, seal/publish, and a later fresh independent audit.

## Validation commands

Rebuild the declared review bundle twice from a remote detached subject tag, compare both digests to the sealed declaration, then run the standard ledger validators.

## Stop conditions

Stop on any digest mismatch, stage failure, missing evidence, escaped attack, incomplete requirement, divergence, or attempted Gate 5 change.
""", encoding="utf-8", newline="\n")
        (CHECKPOINT / "FINAL-REPORT.md").write_text("""# Final report

## Status

`REWORK_REQUIRED`. Independent Red Team: `RED_TEAM_FAIL` (19/20).

## Environment

Windows 11, Docker Compose, remote published clone, and detached canonical subject tag.

## Tool / Model / Effort

Codex desktop application, OpenAI, GPT-5, fresh session; effort not exposed.

## Deliverables

Audit matrix, precise finding, review, full verification report, subject inventory/count/mirror audits, G4-X7 probe, transport attacks, deterministic bundle audit, Red Team, completeness, internal closure mirror, and failed attestation.

## Files Created

Independent audit checkpoint evidence and `.iacode/attestations/G4-CP-0008.json`.

## Files Modified

Only the checkpoint pointer and predecessor anchor; no product path changed.

## Validation

The published full verifier passed all 42 stages once with no retry. Architecture passed 12/12, functional acceptance passed 12/12, and counts independently matched 201/201 requirements, 1709/1709 tests, 97/97 guardrails, and 13/13 subject Green Keeper gates.

## Tests

The subject's product and policy suites are green. The blocking failure is review-transport reconstruction, not product execution.

## Red Team

`RED_TEAM_FAIL`: attacks A-S were defended, but T escaped because two valid detached rebuilds did not reproduce CP0007's declared digest or size.

## Known Risks

Promotion could rely on a valid but stale archive that does not represent final sealed content.

## Remaining Work

Correct `G4-F-004` in a new implementing checkpoint and repeat the complete delivery and independent audit sequence.

## Handoff Readiness

Ready to publish the blocking audit verdict and evidence; not ready for Gate 4 approval.

## Next Gate

Gate 5 is not authorized and must not start.

## Evidence

See `FINDINGS.json`, `FINAL-GATE-4-AUDIT-MATRIX.json`, `SUBJECT-BUNDLE-AUDIT.json`, `GATE-4-INDEPENDENT-RED-TEAM.json`, `VERIFICATION-REPORT.json`, and `REVIEW-REPORT.md`.
""", encoding="utf-8", newline="\n")

    print(f"REWORK_METADATA_WRITTEN phase={args.phase} requirements={counts['COMPLETE']}/{len(requirements)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
