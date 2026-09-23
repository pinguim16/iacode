#!/usr/bin/env python3
"""Declare the change set of GATE-3-CP-0003, one entry per path, with its reason.

The tooling binds the hashes; it never invents a declaration. Every path is enumerated from Git and
matched against a reason written here, so an undeclared change fails loudly instead of being
absorbed by a catch-all.

    python declare_inventory.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASE = "3a526925cf653ffaa9497cff628d08d50424271a"

F003 = "M1-F-003 (published history): "
F001 = "M1-F-001 (envelope shape): "
F002 = "M1-F-002 (tool result origin): "

REASONS = {
    ".iacode/anchors/checkpoint-chain.json":
        "The nineteenth integrity anchor, for the sealed audit checkpoint GATE-3-CP-0002, which "
        "its own checkpoint could not write and which this successor owes it.",
    ".iacode/policies/audit-registry.json":
        "Registers audit M1-CP-0002 exactly as GATE-3-CP-0002/NEXT.md states, so its three "
        "findings become anchored requirements of this corrective delivery.",
    ".iacode/memory/lessons.jsonl":
        "LSN-0040 records M1-F-003 as a GUARDRAIL_FAILURE of GRD-0042 and its resolution in this "
        "checkpoint; LSN-0055 (M1-F-001) and LSN-0056 (M1-F-002) are new; LSN-0054 records a "
        "recurrence.",
    ".iacode/memory/LESSONS.md": "The index rendered from lessons.jsonl.",
    ".iacode/memory/guardrails/registry.json":
        "GRD-0042 is verified by the tests that fail without the published-history correction; "
        "GRD-0056 and GRD-0057 guard the two new lessons.",
    "apps/api/migrations/versions/0005_tool_request_executor.py":
        F002 + "tool_requests.executor, backfilled from the executions the sandbox recorded, "
        "with its vocabulary constraint and a real downgrade.",
    "apps/api/src/iacode_api/routes/agent_runs.py":
        F002 + "the endpoint answers only what an external producer owns; the typed refusal "
        "TOOL_RESULT_ORIGIN_REFUSED maps to 403 and names the executor.",
    "apps/api/tests/integration/test_agent_runtime_persistence.py":
        F002 + "every existing call declares its origin; the ownership refusals against the real "
        "database: forged before, during and after the sandbox's result, wrong run, after "
        "terminal, duplicate sandbox result.",
    "apps/api/tests/integration/test_migrations.py":
        F002 + "migration 0005's backfill, reversal and vocabulary against a disposable database.",
    "apps/api/tests/unit/test_agent_runtime_api.py":
        F002 + "the 403 refusal that signals nothing, and a submission that cannot claim an origin.",
    "docs/CHECKPOINT-PROTOCOL.md": F003 + "the published-history rule for sealed evidence.",
    "docs/DEVELOPMENT-CONTRACT.md":
        F003 + "preserved references and what remote synchronisation now requires.",
    "docs/HANDOFF-PROTOCOL.md":
        F003 + "a sealed checkpoint is validated from a clone of the published history.",
    "docs/adr/ADR-0022-agent-output-envelope.md":
        F001 + "the amendment: the prompt shows the exact shape rendered from the schema.",
    "docs/adr/ADR-0028-sealed-evidence-is-judged-from-the-published-history.md":
        F003 + "the decision record.",
    "docs/adr/README.md": "Lists ADR-0028.",
    "docs/checkpoints/LATEST.md": "Points at this checkpoint.",
    "docs/runbooks/AGENT-RUNTIME.md": F002 + "the fifth refused shape and who owns the origin.",
    "docs/runbooks/SANDBOX.md": F002 + "who answers a sandboxed request, and the new stage.",
    "packages/contracts/src/iacode_contracts/agent_runtime.py":
        F002 + "the executor vocabulary, written once for the database, the row and the runtime.",
    "packages/persistence/src/iacode_persistence/models.py":
        F002 + "the executor column and its constraint on the tool request row.",
    "scripts/development-ledger/gate3_red_team.py":
        "The internal Red Team attacks both runtime findings: G3-Y (forged result, M1-F-002) and "
        "G3-AA (unpublished sealed evidence, M1-F-003).",
    "scripts/development-ledger/ledger_common.py":
        F003 + "one definition of the published history: the published namespaces, "
        "published_reachability and published_clone; the clean-clone copy is a published clone.",
    "scripts/development-ledger/m0_mirror_audit.py": F003 + "MIR-016 clones the published history.",
    "scripts/development-ledger/m0_red_team.py":
        F003 + "the attack fixture is a published clone.",
    "scripts/development-ledger/remote_sync.py":
        F003 + "every local checkpoint and preserved tag must be on the remote.",
    "scripts/development-ledger/validate_checkpoint.py":
        F003 + "a commit named by a checkpoint's evidence must be reachable from a published "
        "reference, for every schema version.",
    "scripts/iacode/scenarios/sandbox_coding_e2e.py":
        F002 + "the forged-result scenario: the audit's null control and mutation on the stack.",
    "scripts/iacode/verify.py": F002 + "the sandbox-tool-result-origin verification stage.",
    "services/agent-runtime/src/iacode_agent_runtime/context.py":
        F001 + "the runtime instructions carry the rendered envelope contract.",
    "services/agent-runtime/src/iacode_agent_runtime/contracts.py":
        F002 + "a tool request carries its executor.",
    "services/agent-runtime/src/iacode_agent_runtime/engine.py":
        F001 + "the repair carries the contract with the stage's tools.",
    "services/agent-runtime/src/iacode_agent_runtime/errors.py":
        F002 + "the typed refusal TOOL_RESULT_ORIGIN_REFUSED.",
    "services/agent-runtime/src/iacode_agent_runtime/persistence.py":
        F002 + "the store records the executor and refuses a result from any other origin before "
        "storing it.",
    "services/agent-runtime/src/iacode_agent_runtime/ports.py":
        F002 + "the store port declares the executor and the origin.",
    "services/agent-runtime/src/iacode_agent_runtime/protocol.py":
        F001 + "envelope_contract and envelope_examples rendered from the schema; the tool object "
        "is closed; the repair restates the shape.",
    "services/agent-runtime/src/iacode_agent_runtime/service.py":
        F002 + "the API's path resolves with the constant origin EXTERNAL.",
    "services/agent-runtime/tests/test_context.py":
        F001 + "mandate tests A, D and E through the instructions.",
    "services/agent-runtime/tests/test_engine.py":
        F001 + "the one repair carries the shape with the stage's tools.",
    "services/agent-runtime/tests/test_protocol.py":
        F001 + "mandate tests B, C and D, and arguments outside tool.arguments refused by their "
        "real defect.",
    "services/orchestrator/rehearsal/durability.py":
        F002 + "the rehearsal answers as the API does, with the origin EXTERNAL.",
    "services/orchestrator/src/iacode_orchestrator/agent_runtime/activities.py":
        F002 + "the internal activity is the sandbox's path, with the origin SANDBOX; the "
        "request's executor is persisted.",
    "services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py":
        F002 + "the workflow records the executor from the stage's sandbox policy.",
    "tests/test_gate1_model_gateway.py":
        F003 + "the sealed-history test clones the published history.",
    "tests/test_gate3_sandbox.py":
        "M1-F-003: published history, preserved references and clone method; M1-F-002: constant "
        "origins, the workflow's executor, the submission contract and the scenario stage; the "
        "Red Team battery attacks both.",
    "tests/test_git_policy.py":
        F003 + "remote synchronisation refuses a local checkpoint or preserved tag missing from "
        "the remote.",
}

CHECKPOINT_REASONS = {
    "CLEAN-CLONE-REPORT.json":
        "The full verification of a fresh clone of the published remote after the correction.",
    "CLOSURE-REQUIREMENTS.json": "The derived requirement set of this checkpoint.",
    "CLOSURE-REQUIREMENTS.md": "Readable rendering of the closure requirements.",
    "COMMANDS.jsonl": "Append-only command ledger of this run.",
    "COMPLETENESS-REPORT.json": "Delivery completeness audit of this checkpoint.",
    "COMPLETENESS-REPORT.md": "Readable rendering of the completeness audit.",
    "COUNTS.json": "Every count this checkpoint uses as evidence, derived once.",
    "DECISIONS.md": "Decisions taken by this delivery.",
    "DIFF-SUMMARY.md": "Summary of the change set.",
    "FILES.json": "The declared inventory itself.",
    "FINAL-REPORT.md": "Closing report of this delivery.",
    "HANDOFF.md": "Handoff for the next run.",
    "LESSON-PREFLIGHT.json": "Lesson preflight of this corrective delivery.",
    "LESSON-PREFLIGHT.md": "Readable rendering of the preflight.",
    "LIVE-CODING-RUN.json":
        F001 + "the live coding run of the configured model, read from what the stack recorded.",
    "M1-FINDINGS-CLOSURE.json": "The closure of the three findings of audit M1-CP-0002.",
    "M1-FINDINGS-CLOSURE.md": "Readable rendering of the findings closure.",
    "M1-INTERNAL-MIRROR.json": "Internal mirror audit of this checkpoint.",
    "M1-INTERNAL-MIRROR.md": "Readable rendering of the internal mirror audit.",
    "M1-INTERNAL-RED-TEAM.json": "The GATE 3 internal Red Team over this delivery.",
    "NEXT.md": "The exact next allowed action.",
    "OLD-CODE-M1-F-003.json":
        F003 + "the new tests run against the old tooling fail and against the corrected pass.",
    "PLAN.md": "The plan, written before implementation.",
    "PROVENANCE.json": "Provenance and rights of the artifacts produced here.",
    "QUALITY.json": "Quality dimensions of this checkpoint with their evidence.",
    "RED-TEAM-REPORT.md": "The internal Red Team battery and its null-mutation control.",
    "REMOTE-PUBLISHED-OBJECTS.json":
        F003 + "over the remote's transport, the preserved commits are absent without their "
        "references and present with them.",
    "REQUIREMENTS-MATRIX.json": "Requirement matrix of this checkpoint.",
    "REQUIREMENTS-MATRIX.md": "Readable rendering of the requirement matrix.",
    "RESUME-VALIDATION.md": "Cold start and baseline of this delivery.",
    "REWORK-LOG.jsonl": "Green Keeper cycles of this checkpoint.",
    "RISKS.md": "Risks this delivery records.",
    "RUN-METADATA.json": "Tool, provider, model, environment and timestamps of this run.",
    "SEALED-EVIDENCE-COMMITS-BASELINE.json":
        F003 + "the baseline: every commit sealed evidence names and whether a published "
        "reference reached it.",
    "SECRET-EXPOSURE-CHECK.json":
        "The owner's check after GitGuardian's report on 7d57721: no real credential value of this "
        "machine appears in any blob, commit message or tag message of the history.",
    "SEALED-SUBJECTS-PUBLISHED.json":
        F003 + "every sealed M1 checkpoint validated from a clone of the published remote.",
    "STATE.json": "Machine-readable state of this checkpoint.",
    "STATUS.md": "The canonical status.",
    "SUITE-SNAPSHOT-FINAL.json":
        "The control-plane suite over a snapshot of the final tree, with the observed count.",
    "SUITE-SNAPSHOT-M1-F-003.json":
        F003 + "the control-plane suite over a snapshot of the corrected tree before its commit.",
    "TESTS.json": "Test execution recorded for this checkpoint.",
    "TOOL-RESULT-ORIGIN.json":
        F002 + "the verification stage's report: the forgery refused, the sandbox's result kept.",
    "VALIDATOR-BLIND-SPOT.json":
        F003 + "the old validator accepts an unpublished local commit, the corrected one refuses "
        "it.",
    "VERIFICATION-REPORT.json": "The full verification of this repository.",
}

HARNESS_REASONS = {
    "collect_reports.py": "Copies the verification's reports from var/ into the checkpoint.",
    "commit_tests.py": "Runs targeted tests on exactly one commit's content before its push.",
    "declare_inventory.py": "Declares this change set.",
    "integration_suite.py": "Runs the API image's suite against the stack, as the verification.",
    "live_coding_run.py": F001 + "the live coding run of the configured model.",
    "old_code_regression.py": "Runs the correction's tests against the code before it.",
    "real_secret_exposure.py":
        "Searches the whole history for the machine's real credential values, recording names only.",
    "record_guardrail_failure.py": F003 + "records the GUARDRAIL_FAILURE of GRD-0042 in LSN-0040.",
    "record_lessons.py": "Records LSN-0055, LSN-0056, their guardrails and the LSN-0054 recurrence.",
    "remote_published_objects.py": F003 + "the acceptance over the remote's transport.",
    "resolve_guardrail_failure.py": F003 + "resolves LSN-0040's failure in this checkpoint.",
    "sealed_evidence_commits.py":
        F003 + "measures the property over the whole ledger, independently of the validator.",
    "sealed_subjects.py": F003 + "validates every sealed M1 checkpoint from the published remote.",
    "clean_clone.py": "The full verification of a fresh clone of the published remote.",
    "complete_requirements.py": "Completes the requirement matrix from this delivery's evidence.",
    "findings_closure.py": "Writes the closure of the three findings.",
    "suite_in_snapshot.py": "Runs the control-plane suite over a frozen snapshot.",
    "sync_state.py": "Copies the derived counts into STATE.json.",
    "validator_blind_spot.py": F003 + "the old validator against the corrected one.",
}


def changed() -> list[tuple[str, str]]:
    entries: dict[str, str] = {}
    committed = subprocess.run(["git", "diff", "--name-status", BASE, "HEAD"], cwd=ROOT,
                               capture_output=True, text=True, encoding="utf-8",
                               check=True).stdout
    for line in committed.splitlines():
        status, _, path = line.partition("\t")
        if path.strip():
            entries[path.strip()] = {"A": "created", "D": "deleted"}.get(status[:1], "modified")
    status = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                            check=True).stdout
    for line in status.splitlines():
        code, path = line[:2], line[3:].strip().replace("\\", "/")
        if path.startswith('"'):
            path = json.loads(path)
        if path in entries:
            continue
        exists_at_base = subprocess.run(["git", "cat-file", "-e", f"{BASE}:{path}"], cwd=ROOT,
                                        capture_output=True, check=False).returncode == 0
        entries[path] = "deleted" if "D" in code else ("modified" if exists_at_base
                                                       else "created")
    return sorted((kind, path) for path, kind in entries.items())


def reason_for(path: str) -> str | None:
    if path in REASONS:
        return REASONS[path]
    prefix = f"docs/checkpoints/{CHECKPOINT.name}/"
    if path.startswith(prefix + "delivery-harness/"):
        return HARNESS_REASONS.get(path[len(prefix + "delivery-harness/"):])
    if path.startswith(prefix):
        return CHECKPOINT_REASONS.get(path[len(prefix):])
    return None


def main() -> int:
    created: list[dict] = []
    modified: list[dict] = []
    deleted: list[dict] = []
    undeclared: list[str] = []
    for kind, path in changed():
        reason = reason_for(path)
        if reason is None:
            undeclared.append(path)
            continue
        {"created": created, "deleted": deleted}.get(kind, modified).append(
            {"path": path, "reason": reason})
    document = {"filesRead": [], "filesCreated": created, "filesModified": modified,
                "filesDeleted": deleted}
    sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))
    from ledger_common import write_json

    write_json(CHECKPOINT / "FILES.json", document)
    print(f"declared created={len(created)} modified={len(modified)} deleted={len(deleted)}")
    for path in undeclared:
        print(f"UNDECLARED {path}")
    return 0 if not undeclared else 1


if __name__ == "__main__":
    raise SystemExit(main())
