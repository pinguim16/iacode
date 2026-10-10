#!/usr/bin/env python3
"""Render truthful REWORK_REQUIRED metadata for the Gate 4 independent audit."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from lessons import guardrail_effectiveness  # noqa: E402


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    timestamp = now()
    matrix = load(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    requirements = matrix["requirements"]
    counts = {key: 0 for key in ("complete", "partial", "missing", "notApplicable")}
    status_key = {
        "COMPLETE": "complete", "PARTIAL": "partial", "MISSING": "missing",
        "NOT_APPLICABLE": "notApplicable",
    }
    for item in requirements:
        key = status_key.get(item["status"])
        if key:
            counts[key] += 1
    denominator = len(requirements) - counts["notApplicable"]
    coverage = round((counts["complete"] / denominator) * 100, 2) if denominator else 100.0
    mandatory = sum(1 for item in requirements if item.get("mandatory"))
    preflight = load(CHECKPOINT / "LESSON-PREFLIGHT.json")
    documentation = load(CHECKPOINT / "DOCUMENTATION-MEMORY-REVIEW.json")
    guardrails = guardrail_effectiveness(ROOT)
    red_team = load(CHECKPOINT / "GATE-4-INDEPENDENT-RED-TEAM.json")
    verification = load(CHECKPOINT / "VERIFICATION-REPORT.json")
    completeness_path = CHECKPOINT / "COMPLETENESS-REPORT.json"
    completeness = load(completeness_path) if completeness_path.is_file() else {
        "result": "FAIL", "coveragePercent": coverage, "evidenceCoveragePercent": 100.0,
    }
    green_path = CHECKPOINT / "GREEN-KEEPER-REPORT.json"
    green = load(green_path) if green_path.is_file() else {"result": "NOT_EXECUTED", "cycles": 0}

    state_path = CHECKPOINT / "STATE.json"
    state = load(state_path)
    state.update({
        "status": "REWORK_REQUIRED",
        "dirty": True,
        "updatedAt": timestamp,
        "nextAllowedAction": (
            "Open implementing checkpoint GATE-4-CP-0003, correct and close G4-F-001, "
            "seal the correction, then perform a later fresh independent Gate 4 audit. "
            "Do not start Gate 5."
        ),
        "blockedBy": ["G4-F-001"],
        "reworkCycles": int(green.get("cycles") or 0),
    })
    state["secondToolValidation"] = {
        "status": "FAILED",
        "tool": "Codex desktop application, fresh session",
        "provider": "OpenAI",
        "model": "GPT-5",
        "validatedAt": timestamp,
        "justification": (
            "The sealed Gate 4 subject was independently reproduced, but G4-F-001 proves that "
            "detected credential-shaped quality output can be durably persisted instead of quarantined."
        ),
        "evidence": ["file:REVIEW-REPORT.md", "file:FINDINGS.json", "file:SECRET-EVIDENCE-PROBE.json"],
    }
    state["requirementsMatrix"] = {
        "path": "REQUIREMENTS-MATRIX.json", "total": len(requirements), "mandatory": mandatory,
        **counts, "coveragePercent": coverage,
    }
    state["greenKeeper"] = {
        "status": green.get("result", "NOT_EXECUTED"),
        "cycles": int(green.get("cycles") or 0),
        "remainingFailures": len(green.get("remainingFailures") or []),
        "unresolvedReworkItems": 0,
        "log": "REWORK-LOG.jsonl", "externalBlockers": [],
        "evidence": ["file:GREEN-KEEPER-REPORT.json"] if green_path.is_file() else [],
    }
    state["deliveryCompleteness"] = {
        "status": completeness.get("result", "FAIL"), "report": "COMPLETENESS-REPORT.json",
        "coveragePercent": completeness.get("coveragePercent", coverage),
        "evidenceCoveragePercent": completeness.get("evidenceCoveragePercent", 100.0),
        "auditor": "Delivery Completeness Validator, Gate 4 fresh-session audit",
        "evidence": ["file:COMPLETENESS-REPORT.json"] if completeness_path.is_file() else [],
    }
    state["independentReview"] = {
        "status": "REWORK_REQUIRED",
        "tool": "Codex desktop application, OpenAI, GPT-5, fresh session",
        "reviewedAt": timestamp,
        "justification": "G4-F-001 is HIGH and violates canonical Gate 4 requirement 19.2.",
        "evidence": ["file:REVIEW-REPORT.md", "file:FINDINGS.json", "file:FINAL-GATE-4-AUDIT-MATRIX.json"],
    }
    state["redTeam"] = {
        "status": "RED_TEAM_FAIL",
        "tool": "Fresh-session Gate 4 independent adversarial harness",
        "executedAt": timestamp,
        "justification": "G4-X7 escaped the pre-persistence credential-containment boundary.",
        "evidence": ["file:GATE-4-INDEPENDENT-RED-TEAM.json", "file:RED-TEAM-REPORT.md"],
    }
    state["lessonPreflight"] = {
        "path": "LESSON-PREFLIGHT.json", "gate": "GATE-4", "scope": "independent-audit",
        "lessonsConsidered": preflight.get("lessonsConsidered"),
        "lessonsApplicable": preflight.get("lessonsApplicable"),
        "derivedRequirements": len(preflight.get("derivedRequirements") or []),
        "evidence": ["checkpoint:LESSON-PREFLIGHT.json"],
    }
    state["milestone"].update({"status": "PENDING", "auditor": None, "auditedAt": None, "evidence": []})
    state["guardrailEffectiveness"] = {
        key: guardrails[key] for key in (
            "guardrailsTotal", "guardrailsResolved", "guardrailsTested",
            "guardrailsEffective", "guardrailFailures")
    }
    state["guardrailEffectiveness"]["evidence"] = [
        "file:.iacode/memory/guardrails/registry.json", "checkpoint:DOCUMENTATION-MEMORY-REVIEW.json"]
    state["integrity"] = {
        "status": "PASS", "anchors": 24, "chainFile": ".iacode/anchors/checkpoint-chain.json",
        "evidence": ["command:cmd-0004", "file:SEALED-SUBJECT-AUDIT.json"],
    }
    state["externalAttestation"] = {
        "status": "PRESENT", "path": ".iacode/attestations/G4-CP-0002.json",
        "auditId": "G4-CP-0002", "subjectCheckpoint": "GATE-4-CP-0001",
        "subjectCommit": "70a22e824705f414e0c295bbdf89187db9b391f7",
        "validationMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
        "evidence": ["file:REVIEW-REPORT.md", "file:RED-TEAM-REPORT.md"],
    }
    write_json(state_path, state)

    passed_verification = verification.get("result") == "PASS" and len(verification.get("stages") or []) == 42
    quality = load(CHECKPOINT / "QUALITY.json")
    for key in ("build", "unitTests", "integrationTests", "e2e", "lint", "staticAnalysis"):
        quality["checks"][key] = {
            "status": "PASS" if passed_verification else "FAIL",
            "evidence": ["file:VERIFICATION-REPORT.json", "file:CLEAN-CLONE-REPORT.json"],
            "justification": None if passed_verification else "The complete clean-clone verification did not pass.",
        }
    quality["checks"]["security"] = {
        "status": "FAIL", "evidence": ["file:FINDINGS.json", "file:SECRET-EVIDENCE-PROBE.json"],
        "justification": "G4-F-001: detected credential-shaped output crossed the durable evidence boundary.",
    }
    quality["checks"]["documentation"] = {
        "status": "PASS" if documentation.get("result") == "PASS" else "FAIL",
        "evidence": ["file:DOCUMENTATION-MEMORY-REVIEW.json", "file:REVIEW-REPORT.md"], "justification": None,
    }
    quality["checks"]["checkpointValidation"] = {
        "status": "NOT_EXECUTED", "evidence": [], "justification": "Final validation runs during finalization and sealing.",
    }
    quality["checks"]["redTeam"] = {
        "status": "FAIL", "evidence": ["file:GATE-4-INDEPENDENT-RED-TEAM.json"],
        "justification": "G4-X7 escaped.",
    }
    quality["checks"]["greenKeeper"] = {
        "status": green.get("result", "NOT_EXECUTED"),
        "evidence": ["file:GREEN-KEEPER-REPORT.json"] if green_path.is_file() else [],
        "justification": "Canonical executable gates do not override the independent security finding.",
    }
    quality["checks"]["deliveryCompleteness"] = {
        "status": completeness.get("result", "FAIL"),
        "evidence": ["file:COMPLETENESS-REPORT.json"] if completeness_path.is_file() else [],
        "justification": "Canonical requirement 19.2 is missing because G4-F-001 remains open.",
    }
    write_json(CHECKPOINT / "QUALITY.json", quality)

    tests = {
        "schemaVersion": "3.2.0",
        "unit": {"executed": passed_verification, "passed": 746 if passed_verification else 0,
                 "failed": 0 if passed_verification else 1,
                 "command": "python -m unittest discover -s tests", "evidence": "command:cmd-0015",
                 "runId": "clean-clone-ledger-suite"},
        "integration": {"executed": passed_verification, "passed": 929 if passed_verification else 0,
                        "failed": 0 if passed_verification else 1,
                        "command": "python scripts/iacode/verify.py --keep-going", "evidence": "command:cmd-0015",
                        "runId": "clean-clone-complete-verification"},
        "e2e": {"executed": passed_verification, "passed": 42 if passed_verification else 0,
                "failed": 0 if passed_verification else 1,
                "command": "python scripts/iacode/verify.py --keep-going", "evidence": "command:cmd-0015",
                "runId": "clean-clone-complete-verification"},
    }
    write_json(CHECKPOINT / "TESTS.json", tests)

    audit_matrix = {
        "schemaVersion": "1.0.0", "artifact": "FINAL-GATE-4-AUDIT-MATRIX",
        "checkpoint": CHECKPOINT.name, "subjectCheckpoint": "GATE-4-CP-0001",
        "generatedAt": timestamp, "criteria": [], "result": "REWORK_REQUIRED",
    }
    failed_criteria = {7, 11, 24, 27, 28, 29, 30, 32}
    for number in range(1, 33):
        criterion = f"G4A-{number:02d}"
        result = "FAIL" if number in failed_criteria else "NOT_EXECUTED" if number == 31 else "PASS"
        audit_matrix["criteria"].append({
            "criterion": criterion, "result": result,
            "evidence": ["file:FINDINGS.json", "file:GATE-4-INDEPENDENT-RED-TEAM.json"] if result == "FAIL" else ["file:SEALED-SUBJECT-AUDIT.json", "file:VERIFICATION-REPORT.json"],
            "note": (
                "G4-F-001 and G4-X7 block this promotion criterion."
                if result == "FAIL" else
                "Not executed because the mandatory delivery order stops after completeness fails."
                if result == "NOT_EXECUTED" else
                "Satisfied by independently reproduced evidence."
            ),
        })
    write_json(CHECKPOINT / "FINAL-GATE-4-AUDIT-MATRIX.json", audit_matrix)
    lines = ["# Final Gate 4 audit matrix", "", "Result: `REWORK_REQUIRED`", "", "| Criterion | Result |", "|---|---|"]
    lines.extend(f"| `{item['criterion']}` | `{item['result']}` |" for item in audit_matrix["criteria"])
    (CHECKPOINT / "FINAL-GATE-4-AUDIT-MATRIX.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    executions = {
        "schemaVersion": "1.0.0", "artifact": "AUDIT-EXECUTIONS", "checkpoint": CHECKPOINT.name,
        "generatedAt": timestamp, "subjectCommit": "70a22e824705f414e0c295bbdf89187db9b391f7",
        "executions": [
            {"name": "sealed subject and bundle", "result": "PASS", "evidence": "SEALED-SUBJECT-AUDIT.json"},
            {"name": "published evidence objects", "result": "PASS", "evidence": "REMOTE-PUBLISHED-OBJECTS.json"},
            {"name": "architecture review", "result": "PASS", "evidence": "ARCHITECTURE-REVIEW.json"},
            {"name": "clean-clone complete verification", "result": verification.get("result"), "evidence": "VERIFICATION-REPORT.json"},
            {"name": "documentation and memory", "result": documentation.get("result"), "evidence": "DOCUMENTATION-MEMORY-REVIEW.json"},
            {"name": "secret evidence boundary", "result": "FAIL", "evidence": "SECRET-EVIDENCE-PROBE.json"},
            {"name": "independent Red Team", "result": red_team.get("result"), "evidence": "GATE-4-INDEPENDENT-RED-TEAM.json"},
            {"name": "delivery completeness", "result": completeness.get("result"), "evidence": "COMPLETENESS-REPORT.json"},
        ],
        "verdict": "REWORK_REQUIRED",
    }
    write_json(CHECKPOINT / "AUDIT-EXECUTIONS.json", executions)

    attestation = {
        "schemaVersion": "2.0.0", "auditId": "G4-CP-0002", "milestone": "M2",
        "validationMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT", "crossToolValidation": "NOT_AVAILABLE",
        "auditorRole": "Gate independent auditor", "tool": "Codex desktop application",
        "provider": "OpenAI", "model": "GPT-5", "freshSession": True,
        "subjectCheckpoint": "GATE-4-CP-0001", "subjectCommit": "70a22e824705f414e0c295bbdf89187db9b391f7",
        "auditCheckpoint": CHECKPOINT.name, "reviewResult": "REWORK_REQUIRED",
        "redTeamResult": "RED_TEAM_FAIL", "completeness": completeness.get("coveragePercent", coverage),
        "evidenceCoverage": completeness.get("evidenceCoveragePercent", 100.0), "testResult": "FAIL",
        "createdAt": timestamp,
        "notes": "The attestation records a failed fresh-session audit; it does not grant Gate 4 or milestone approval. G4-F-001 is HIGH and G4-X7 escaped.",
    }
    write_json(ROOT / ".iacode" / "attestations" / "G4-CP-0002.json", attestation)

    metadata = load(CHECKPOINT / "RUN-METADATA.json")
    metadata.update({"tool": "Codex desktop application", "toolVersion": "not exposed to the run",
                     "provider": "OpenAI", "model": "GPT-5", "operatingSystem": "Windows 11",
                     "finishedAt": timestamp, "finalCommit": state["currentCommit"]})
    write_json(CHECKPOINT / "RUN-METADATA.json", metadata)

    (CHECKPOINT / "STATUS.md").write_text("# Status\n\nREWORK_REQUIRED\n", encoding="utf-8", newline="\n")
    (CHECKPOINT / "NEXT.md").write_text(
        "# Next\n\n## Required next action\n\nOpen implementing checkpoint `GATE-4-CP-0003`. Apply the canonical scanner to the fully serialized evidence object before durable commit, quarantine or fail closed on detection, prove that prohibited bytes cannot be resolved, and add a regression test for credential material under an unremarkable structured key.\n\n## Promotion constraint\n\nClose `G4-F-001`, repeat every mandatory delivery-assurance role in order, seal and publish the correction, and submit it to a later fresh independent Gate 4 audit. Do not start Gate 5 and do not weaken the scanner, denominator, or promotion policy.\n",
        encoding="utf-8", newline="\n")
    (CHECKPOINT / "RISKS.md").write_text(
        "# Risks\n\n- `G4-F-001` (HIGH): a detected credential-shaped value can be retained in durable Quality Engine evidence.\n- Gate 4 remains unapproved; treating executable-suite green as promotion would be a false PASS.\n",
        encoding="utf-8", newline="\n")
    (CHECKPOINT / "DIFF-SUMMARY.md").write_text(
        "# Diff summary\n\nAudit evidence, finding registration, failed independent attestation, and sealed checkpoint metadata only. No product, test, dependency, or production configuration file was changed.\n",
        encoding="utf-8", newline="\n")
    (CHECKPOINT / "HANDOFF.md").write_text(
        "# Handoff\n\nCurrent Gate: GATE-4\nCurrent Status: REWORK_REQUIRED\n\n"
        "## Objective\n\nIndependently audit sealed Gate 4 without correcting production.\n\n"
        "## What was completed\n\nSubject identity, bundle, transport clone, 42-stage verification, architecture, documentation, memory, functional acceptance and independent Red Team were executed.\n\n"
        "## What was NOT completed\n\n`G4-F-001` was not corrected. Gate 4, M2 and Gate 5 were not advanced. The Milestone Closure Auditor stopped after completeness failed.\n\n"
        "## Current repository state\n\nSee `STATE.json`; the checkpoint is `REWORK_REQUIRED` and names `G4-F-001` in `blockedBy`.\n\n"
        "## Files changed\n\nSee `FILES.json`; only audit, ledger, attestation, anchor and registry paths changed.\n\n"
        "## Important decisions\n\nSee `DECISIONS.md`; the auditor made no product repair and issued no positive verdict.\n\n"
        "## Tests executed\n\nSee `TESTS.json`, `VERIFICATION-REPORT.json`, `FUNCTIONAL-ACCEPTANCE-REPORT.json`, `GATE-4-INDEPENDENT-RED-TEAM.json` and `REWORK-LOG.jsonl`.\n\n"
        "## Known failures\n\n`G4-F-001` (HIGH) and escaped attack `G4-X7`; canonical requirement 19.2 is `MISSING`.\n\n"
        "## Known risks\n\nSee `RISKS.md`; detected credential-shaped output can cross the durable evidence boundary.\n\n"
        "## Do not repeat\n\nDo not persist first and scan later. Do not treat a green ordinary suite as a security-boundary proof.\n\n"
        "## Required next action\n\nOpen `GATE-4-CP-0003`; correct and close `G4-F-001`; rerun the complete mandatory delivery order; seal and publish the correction; then use a later fresh independent audit. Gate 5 must not start.\n\n"
        "## Exact continuation sequence\n\nRead the finding; implement pre-persistence containment; add the regression guard; rerun lesson preflight, derivation, baseline, plan, implementation, tests, Green Keeper, completeness, internal Red Team and closure audit; seal; submit a later independent audit.\n\n"
        "## Validation commands\n\n`python scripts/development-ledger/validate_checkpoint.py` and the complete Gate 4 verifier.\n\n"
        "## Stop conditions\n\nStop on divergence, any persisted scanner-detected value, incomplete evidence, a red mandatory gate, or an attempted Gate 5 advance.\n",
        encoding="utf-8", newline="\n")
    (CHECKPOINT / "FINAL-REPORT.md").write_text(
        "# Final report\n\nVerdict: `REWORK_REQUIRED`. The sealed Gate 4 subject is genuine and its normal full verification reproduces, but `G4-F-001` proves that a value detected as credential-shaped can be persisted and resolved through the Quality Engine evidence boundary. Independent attack `G4-X7` escaped. No product correction or positive Gate/milestone attestation was made.\n",
        encoding="utf-8", newline="\n")
    (CHECKPOINT / "MILESTONE-REPORT.md").write_text(
        "# M2 status\n\nM2 remains `PENDING`. This checkpoint audits Gate 4 only; it does not audit or advance Gates 5–7. Gate 4 is `REWORK_REQUIRED` because `G4-F-001` is open and independent attack `G4-X7` escaped. The failed audit attestation records those facts and cannot grant a milestone verdict.\n",
        encoding="utf-8", newline="\n")
    provenance = load(CHECKPOINT / "PROVENANCE.json")
    provenance["artifacts"] = [{
        "artifact": "docs/checkpoints/GATE-4-CP-0002 and .iacode/attestations/G4-CP-0002.json",
        "sourceType": "repository-generated", "provider": "OpenAI", "model": "GPT-5",
        "ownership": "project", "license": "project-policy",
        "rights": {"storageAllowed": True, "ragAllowed": False, "trainingAllowed": False, "distillationAllowed": False},
        "evidence": "Fresh-session audit evidence derived from the sealed published subject and synthetic non-secret probes.",
        "notes": "No private data, secret value, or chain-of-thought is recorded.",
    }]
    write_json(CHECKPOINT / "PROVENANCE.json", provenance)
    print(f"FAILED_AUDIT_CLOSURE=WRITTEN coverage={coverage:.2f} redTeam={red_team.get('result')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
