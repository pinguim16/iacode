#!/usr/bin/env python3
"""Build disposable repositories that execute the protocol's own positive paths.

Two workflows are proven here, both end to end, both in throwaway repositories, and both by
execution rather than by assertion:

``run_positive_promotion``
    A subject checkpoint is delivered and sealed. A *second* checkpoint is then authored as its
    audit: it anchors the subject, writes an audit attestation naming the subject and the commit
    the subject's canonical tag already resolves to, and closes at a milestone verdict status. The
    subject is never rewritten, re-tagged or re-sealed, and the milestone verdict is derived from
    the repository afterwards. This is the path finding ``CP9-F-001`` proved did not exist: every
    forgery was refused and no honest sequence of repository states could produce a PASS.

``run_successor_durability``
    Three checkpoints are sealed in succession, each anchoring its predecessor, and the integrity
    controls are re-run at every state. The exclusion the chain check needs -- the one checkpoint
    whose anchor is still owed -- is derived from repository state, so advancing the chain never
    requires editing a test. This is the path finding ``CP9-F-002`` proved was broken by a literal
    checkpoint name inside a guardrail test.

Both builders are used by the test suite and by the two simulation entry points, so the artifacts a
delivery records and the assertions the suite makes describe the same execution.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from anchors import (
    TAG_NAMESPACE,
    commit_tree,
    pending_anchor_exclusion,
    rebuild,
    resolve_tag,
    sealed_checkpoint_ids,
    verify_chain,
)
from attestation import derive_milestone_verdict
from ledger_common import (
    LedgerError,
    blob_hash,
    canonical_hash_path,
    git_delta,
    scope_fingerprint,
    utc_now,
)
from lessons import guardrail_effectiveness
from policies import mandatory_gates

SCRIPTS = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS.parent.parent

FIXTURE_TEST = "FixtureTests.test_case"

BASE_QUALITY_DIMENSIONS = (
    "build", "unitTests", "integrationTests", "e2e", "lint", "staticAnalysis",
    "security", "documentation", "checkpointValidation", "redTeam",
)

FINAL_REPORT_HEADINGS = (
    "Status", "Environment", "Tool / Model / Effort", "Deliverables", "Files Created",
    "Files Modified", "Validation", "Tests", "Red Team", "Known Risks", "Remaining Work",
    "Handoff Readiness", "Next Gate", "Evidence",
)


class FixtureError(LedgerError):
    """A simulation could not be built, which is a failure of the simulation, not a verdict."""


# --------------------------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------------------------


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, check=False, env=environment)


def _git(root: Path, *args: str) -> str:
    completed = _run(["git", *args], root)
    if completed.returncode != 0:
        raise FixtureError(f"git {' '.join(args)} failed: {completed.stdout.strip()}")
    return completed.stdout.strip()


def _tool(root: Path, name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return _run([sys.executable, str(root / "scripts" / "development-ledger" / name),
                 "--root", str(root), *args], root)


def _require(completed: subprocess.CompletedProcess[str], what: str) -> str:
    if completed.returncode != 0:
        raise FixtureError(f"{what} failed with exit {completed.returncode}: {completed.stdout}")
    return completed.stdout


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")


def declare_inventory(root: Path, checkpoint: Path,
                      reason: str = "declared by the promotion simulation") -> None:
    """Author a complete FILES.json for the current change set, as a human author must."""
    state = read_json(checkpoint / "STATE.json")
    base = state["baseCommit"]
    delta = git_delta(root, base, None)
    files = read_json(checkpoint / "FILES.json")
    buckets: dict[str, list[dict[str, Any]]] = {
        "filesCreated": [], "filesModified": [], "filesDeleted": []}
    self_referential = str((checkpoint / "FILES.json").relative_to(root)).replace("\\", "/")
    for path, status in sorted(delta.items()):
        entry: dict[str, Any] = {"path": path, "reason": reason}
        if path != self_referential:
            if status in ("A", "M"):
                entry["hashAfter"] = canonical_hash_path(root / path)
            if status in ("M", "D"):
                entry["hashBefore"] = blob_hash(root, base, path)
        bucket = ("filesCreated" if status == "A"
                  else "filesModified" if status == "M" else "filesDeleted")
        buckets[bucket].append(entry)
    files.update(buckets)
    write_json(checkpoint / "FILES.json", files)


# --------------------------------------------------------------------------------------------
# The disposable repository
# --------------------------------------------------------------------------------------------


def build_fixture_repository(root: Path) -> None:
    """A minimal IACode repository: the policies, the tooling, a suite, and its own memory."""
    root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(PROJECT_ROOT / ".iacode", root / ".iacode",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (root / "docs" / "checkpoints").mkdir(parents=True)
    shutil.copy2(PROJECT_ROOT / "docs" / "SETUP-00-CHECKLIST.md",
                 root / "docs" / "SETUP-00-CHECKLIST.md")
    (root / "docs" / "CHECKPOINT-PROTOCOL.md").write_text(
        "# Checkpoint Protocol\n\nFixture document.\n", encoding="utf-8", newline="\n")
    shutil.copytree(SCRIPTS, root / "scripts" / "development-ledger",
                    ignore=shutil.ignore_patterns("__pycache__"))
    for name in (".gitignore", ".gitattributes"):
        if (PROJECT_ROOT / name).is_file():
            shutil.copy2(PROJECT_ROOT / name, root / name)
    (root / "tests").mkdir()
    (root / "tests" / "test_fixture.py").write_text(
        "import unittest\n\n\nclass FixtureTests(unittest.TestCase):\n"
        "    def test_case(self):\n        self.assertEqual(1, 1)\n",
        encoding="utf-8", newline="\n")
    # A fresh repository has sealed nothing, so it inherits no integrity anchors, no engineering
    # memory and no open audit: all three are statements about the real repository's history. The
    # memory is installed once the first checkpoint exists, because a lesson must cite one.
    anchors = root / ".iacode" / "anchors" / "checkpoint-chain.json"
    if anchors.is_file():
        anchors.unlink()
    if (root / ".iacode" / "memory").exists():
        shutil.rmtree(root / ".iacode" / "memory")
    registry = root / ".iacode" / "policies" / "audit-registry.json"
    document = read_json(registry)
    for audit in document.get("audits") or []:
        audit["correctiveCheckpoint"] = None
    write_json(registry, document)
    # An empty attestation directory would not survive Git, and the real repository keeps its
    # README there, so the fixture inherits the same shape.
    (root / ".iacode" / "attestations").mkdir(parents=True, exist_ok=True)

    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "IACode Promotion Simulation")
    _git(root, "config", "user.email", "iacode-simulation@example.invalid")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "test: bootstrap the promotion fixture")


def _install_memory(root: Path, checkpoint: str) -> None:
    """A complete, resolvable memory that describes the fixture rather than the real project.

    The memory validator resolves what a lesson claims, so the fixture needs a lesson whose source
    checkpoint, control and evidence all exist inside the fixture. It is installed once the first
    checkpoint exists, because the lesson has to cite one.
    """
    memory = root / ".iacode" / "memory"
    if memory.exists():
        shutil.rmtree(memory)
    (memory / "guardrails").mkdir(parents=True)
    write_json(memory / "POLICY.json", {
        "schemaVersion": "2.0.0",
        "policy": "Fixture memory under the resolving policy. The guardrail registry path is fixed.",
    })
    write_json(memory / "guardrails" / "registry.json", {
        "schemaVersion": "1.0.0",
        "guardrails": [{
            "guardrailId": "GRD-0001",
            "title": "The fixture control",
            "kind": "test",
            "reference": FIXTURE_TEST,
            "verifiedBy": [FIXTURE_TEST],
            "lessons": ["LSN-0001"],
            "removingItWouldAllow": "The fixture failure class to recur.",
        }],
    })
    (memory / "README.md").write_text(
        "# Fixture memory\n\nOne lesson, one guardrail, both resolvable.\n",
        encoding="utf-8", newline="\n")
    lesson = {
        "lessonId": "LSN-0001",
        "title": "A checkpoint may never claim readiness while it also claims to be blocked",
        "category": "checkpoint",
        "severity": "HIGH",
        "source": {"gate": "SETUP-00", "checkpoint": checkpoint, "finding": None},
        "symptom": "A resealed checkpoint validated while it declared a blocker.",
        "rootCauseSummary": "The blocker list was inspected only for one status.",
        "resolution": "The invariant applies to every readiness status and every schema version.",
        "prevention": [{
            "kind": "test",
            "reference": FIXTURE_TEST,
            "description": "Readiness with a blocker is refused.",
        }],
        "guardrails": ["GRD-0001"],
        "evidence": ["file:docs/CHECKPOINT-PROTOCOL.md"],
        "applicability": {"gates": ["*"], "scopes": [], "technologies": [], "modules": [],
                          "requiredCheck": "Readiness and blockage are never claimed together.",
                          "requiredEvidence": "A validated checkpoint with an empty blockedBy."},
        "status": "GUARDED",
        "recurrenceKey": "checkpoint/readiness-with-blockers",
        "recurrenceCount": 0,
        "guardrailFailures": [],
        "createdAt": utc_now(),
        "updatedAt": utc_now(),
        "provenance": {"sourceType": "repository-generated", "provider": "local-analysis",
                       "model": None, "ownership": "project", "license": "not-applicable",
                       "notes": None},
        "trainingEligibility": {"trainingAllowed": False, "ragAllowed": False,
                                "distillationAllowed": False, "justification": None},
        "notes": None,
    }
    (memory / "lessons.jsonl").write_text(
        json.dumps(lesson, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (memory / "LESSONS.md").write_text(
        "# Lessons\n\n| Lesson | Status |\n|---|---|\n| LSN-0001 | GUARDED |\n",
        encoding="utf-8", newline="\n")


def _write_final_report(checkpoint: Path) -> None:
    lines = ["# Final Report", ""]
    for heading in FINAL_REPORT_HEADINGS:
        lines += [f"## {heading}", "", "Simulation content.", ""]
    (checkpoint / "FINAL-REPORT.md").write_text(
        "\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


def _complete_requirements(checkpoint: Path) -> None:
    evidence = ["checkpoint:PLAN.md"]
    matrix = read_json(checkpoint / "REQUIREMENTS-MATRIX.json")
    for row in matrix["requirements"]:
        row["status"] = "COMPLETE"
        row["implementationEvidence"] = list(evidence)
    write_json(checkpoint / "REQUIREMENTS-MATRIX.json", matrix)
    closure = read_json(checkpoint / "CLOSURE-REQUIREMENTS.json")
    for row in closure["requirements"]:
        row["implementationStatus"] = "COMPLETE"
        row["finalStatus"] = "COMPLETE"
        row["implementationEvidence"] = list(evidence)
    write_json(checkpoint / "CLOSURE-REQUIREMENTS.json", closure)


def _write_internal_assurance(root: Path, checkpoint: Path) -> None:
    fingerprint = scope_fingerprint(root)
    write_json(checkpoint / "M0-INTERNAL-RED-TEAM.json", {
        "schemaVersion": "1.1.0", "checkpoint": checkpoint.name, "generatedAt": utc_now(),
        "targetFingerprint": fingerprint, "source": "promotion simulation",
        "baselineControl": {"result": "VALID",
                            "detail": "the unmutated fixture validates before any attack"},
        "attacks": [{
            "attackId": "A", "description": "simulation", "target": "simulation",
            "mutation": "simulation", "expectedDefense": "reject", "observed": "rejected",
            "result": "DEFENDED", "evidence": ["attack:A"], "mandatory": True}],
        "total": 1, "defended": 1, "escaped": 0, "mandatoryTotal": 1, "mandatoryDefended": 1,
        "result": "RED_TEAM_PASS"})
    write_json(checkpoint / "M0-INTERNAL-MIRROR.json", {
        "schemaVersion": "1.0.0", "checkpoint": checkpoint.name, "milestone": "M0",
        "generatedAt": utc_now(), "targetFingerprint": fingerprint,
        "auditorRole": "M0 Closure Auditor",
        "independence": "Internal quality assurance, not independent validation.",
        "checks": [{"id": "MIR-001", "dimension": "simulation", "expectation": "simulation",
                    "observed": "simulation", "result": "PASS",
                    "evidence": ["checkpoint:PLAN.md"]}],
        "total": 1, "passed": 1, "failed": 0, "notApplicable": 0, "result": "PASS"})


def _quality(terminal: bool) -> dict[str, Any]:
    checks = {name: {"status": "PASS", "evidence": ["command:cmd-0001"], "justification": None}
              for name in BASE_QUALITY_DIMENSIONS + ("greenKeeper", "deliveryCompleteness")}
    for name in ("integrationTests", "e2e"):
        checks[name] = {"status": "NOT_APPLICABLE", "evidence": [],
                        "justification": "no runtime exists in the simulation fixture"}
    if not terminal:
        checks["redTeam"] = {"status": "NOT_EXECUTED", "evidence": [], "justification": None}
    return {"schemaVersion": "3.2.0", "checks": checks}


def deliver_checkpoint(
    root: Path,
    *,
    scope: str,
    status: str = "READY_FOR_REVIEW",
    before_gates: Callable[[Path, Path], None] | None = None,
    state_overrides: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Run the mandatory delivery order in the fixture and seal the result.

    ``before_gates`` runs after the checkpoint exists and before any gate is measured, which is
    where content inside the delivery-assurance scope -- an integrity anchor, an attestation --
    has to be written so that the gates judge the content that is actually sealed.
    """
    created = _tool(root, "new_checkpoint.py", "--gate", "SETUP-00", "--status", "IN_PROGRESS")
    _require(created, "new_checkpoint.py")
    name = sorted(
        item.name for item in (root / "docs" / "checkpoints").iterdir() if item.is_dir())[-1]
    checkpoint = root / "docs" / "checkpoints" / name

    if not (root / ".iacode" / "memory" / "lessons.jsonl").is_file():
        _install_memory(root, name)

    if before_gates is not None:
        before_gates(root, checkpoint)

    # The anchor count is part of what the checkpoint-validation gate checks, so it has to be
    # truthful before the gates run rather than after them.
    from anchors import load_anchors

    state = read_json(checkpoint / "STATE.json")
    state["integrity"] = {"status": "PASS", "anchors": len(load_anchors(root)),
                          "chainFile": ".iacode/anchors/checkpoint-chain.json", "evidence": []}
    write_json(checkpoint / "STATE.json", state)

    preflight = _tool(root, "lesson_preflight.py", "--gate", "SETUP-00", "--scope", scope,
                      "--write", "--checkpoint", str(checkpoint))
    _require(preflight, "lesson_preflight.py")
    derived = read_json(checkpoint / "LESSON-PREFLIGHT.json")
    state = read_json(checkpoint / "STATE.json")
    state["lessonPreflight"] = {
        "path": "LESSON-PREFLIGHT.json", "gate": "SETUP-00", "scope": scope,
        "lessonsConsidered": derived["lessonsConsidered"],
        "lessonsApplicable": derived["lessonsApplicable"],
        "derivedRequirements": len(derived["derivedRequirements"]), "evidence": []}
    write_json(checkpoint / "STATE.json", state)

    _require(_tool(root, "derive_requirements.py", "--write", "--checkpoint", str(checkpoint)),
             "derive_requirements.py")
    _complete_requirements(checkpoint)
    _write_final_report(checkpoint)
    write_json(checkpoint / "TESTS.json", {
        "schemaVersion": "3.2.0",
        "unit": {"executed": True, "passed": 1, "failed": 0,
                 "command": "python -m unittest discover -s tests",
                 "runId": "simulation-suite", "evidence": "fixture suite"},
        "integration": {"executed": False, "passed": 0, "failed": 0, "command": None,
                        "runId": None, "evidence": None},
        "e2e": {"executed": False, "passed": 0, "failed": 0, "command": None,
                "runId": None, "evidence": None}})

    declare_inventory(root, checkpoint)
    keeper = _tool(root, "green_keeper.py", "--trigger", "promotion simulation", "--quiet",
                   "--checkpoint", str(checkpoint))
    _require(keeper, "green_keeper.py")
    cycle = [json.loads(line) for line
             in (checkpoint / "REWORK-LOG.jsonl").read_text(encoding="utf-8").splitlines()
             if line.strip()][-1]

    audit = _tool(root, "check_completeness.py", "--auditor", "simulation auditor", "--write",
                  "--checkpoint", str(checkpoint))
    _require(audit, "check_completeness.py")
    report = read_json(checkpoint / "COMPLETENESS-REPORT.json")

    _write_internal_assurance(root, checkpoint)
    _require(_tool(root, "derive_counts.py", "--write", "--checkpoint", str(checkpoint)),
             "derive_counts.py")

    terminal = status not in ("READY_FOR_REVIEW", "READY_FOR_RED_TEAM")
    write_json(checkpoint / "QUALITY.json", _quality(terminal))

    measured = guardrail_effectiveness(root)
    state = read_json(checkpoint / "STATE.json")
    state["requirementsMatrix"] = {
        "path": "REQUIREMENTS-MATRIX.json", "total": report["totalRequirements"],
        "mandatory": report["mandatoryRequirements"], "complete": report["complete"],
        "partial": 0, "missing": 0, "notApplicable": 0, "coveragePercent": 100.0}
    state["greenKeeper"] = {
        "status": "PASS", "cycles": 1, "remainingFailures": 0, "unresolvedReworkItems": 0,
        "log": "REWORK-LOG.jsonl", "externalBlockers": [], "evidence": [],
        "requiredGates": list(mandatory_gates(root)),
        "scopeFingerprint": cycle["scopeFingerprint"]}
    state["deliveryCompleteness"] = {
        "status": "PASS", "report": "COMPLETENESS-REPORT.json", "coveragePercent": 100.0,
        "evidenceCoveragePercent": 100.0, "auditor": "simulation auditor", "evidence": [],
        "scopeFingerprint": report["scopeFingerprint"]}
    state["reworkCycles"] = 1
    state["guardrailEffectiveness"] = {
        key: measured[key] for key in (
            "guardrailsTotal", "guardrailsResolved", "guardrailsTested", "guardrailsEffective",
            "guardrailFailures")}
    from anchors import load_anchors

    state["integrity"] = {"status": "PASS", "anchors": len(load_anchors(root)),
                          "chainFile": ".iacode/anchors/checkpoint-chain.json", "evidence": []}
    if state_overrides is not None:
        state_overrides(state)
    write_json(checkpoint / "STATE.json", state)

    declare_inventory(root, checkpoint)
    finalized = _tool(root, "finalize_checkpoint.py", "--status", status,
                      "--commit-ref", f"{TAG_NAMESPACE}{name}", "--checkpoint", str(checkpoint))
    _require(finalized, "finalize_checkpoint.py")

    _git(root, "add", "-A")
    _git(root, "commit", "-m", f"test: seal {name}")
    content_commit = _git(root, "rev-parse", "HEAD")

    sealed = _tool(root, "seal_checkpoint.py", "--checkpoint", str(checkpoint))
    _require(sealed, "seal_checkpoint.py")
    validated = _tool(root, "validate_checkpoint.py", "--checkpoint", str(checkpoint))
    _require(validated, "validate_checkpoint.py")

    tag = f"{TAG_NAMESPACE}{name}"
    commit = resolve_tag(root, tag)
    return {
        "checkpoint": name,
        "path": str(checkpoint),
        "tag": tag,
        "contentCommit": content_commit,
        "commit": commit,
        "tree": commit_tree(root, str(commit)) if commit else None,
        "status": status,
        "validatorOutput": validated.stdout.strip(),
    }


def _rebuild_anchors(root: Path, exclude: str) -> int:
    identifiers = [item for item in sealed_checkpoint_ids(root) if item != exclude]
    document = rebuild(root, identifiers)
    path = root / ".iacode" / "anchors" / "checkpoint-chain.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, document)
    return len(identifiers)


def write_attestation(
    root: Path,
    *,
    audit_id: str,
    subject: dict[str, Any],
    audit_checkpoint: str,
    mechanism: str = "FRESH_SESSION_INDEPENDENT_AUDIT",
    review: str = "APPROVED",
    red_team: str = "RED_TEAM_PASS",
    completeness: float = 100.0,
    evidence_coverage: float = 100.0,
    test_result: str = "PASS",
) -> Path:
    """Write the audit checkpoint's attestation about the sealed subject it judged."""
    document = {
        "schemaVersion": "2.0.0",
        "auditId": audit_id,
        "milestone": "M0",
        "validationMechanism": mechanism,
        "crossToolValidation": (
            "AVAILABLE" if mechanism == "CROSS_TOOL_INDEPENDENT_AUDIT" else "NOT_AVAILABLE"),
        "auditorRole": "milestone independent auditor",
        "tool": "promotion simulation",
        "provider": "local",
        "model": "not-applicable",
        "freshSession": True,
        "subjectCheckpoint": subject["checkpoint"],
        "subjectCommit": subject["commit"],
        "auditCheckpoint": audit_checkpoint,
        "reviewResult": review,
        "redTeamResult": red_team,
        "completeness": completeness,
        "evidenceCoverage": evidence_coverage,
        "testResult": test_result,
        "createdAt": utc_now(),
        "notes": "Written by the audit checkpoint about a checkpoint that was already sealed.",
    }
    path = root / ".iacode" / "attestations" / f"{audit_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, document)
    return path


# --------------------------------------------------------------------------------------------
# The two simulations
# --------------------------------------------------------------------------------------------


def run_positive_promotion(workdir: Path, *,
                           mechanism: str = "FRESH_SESSION_INDEPENDENT_AUDIT",
                           status: str = "MILESTONE_INDEPENDENT_AUDIT_PASS") -> dict[str, Any]:
    """Subject -> seal -> audit checkpoint -> attestation -> seal -> derived milestone PASS."""
    root = workdir / "promotion"
    build_fixture_repository(root)

    subject = deliver_checkpoint(root, scope="control-plane", status="READY_FOR_REVIEW")
    subject_state_before = (root / "docs" / "checkpoints" / subject["checkpoint"]
                            / "STATE.json").read_text(encoding="utf-8")

    audit_id = f"M0-AUDIT-OF-{subject['checkpoint']}"
    attestation_path: dict[str, str] = {}

    def before_gates(repository: Path, checkpoint: Path) -> None:
        # Everything the gates must judge is written before they run: the anchor this checkpoint
        # owes its sealed predecessor, and the attestation this checkpoint authors about it.
        _rebuild_anchors(repository, exclude=checkpoint.name)
        path = write_attestation(
            repository, audit_id=audit_id, subject=subject,
            audit_checkpoint=checkpoint.name, mechanism=mechanism)
        attestation_path["value"] = str(path.relative_to(repository)).replace("\\", "/")

    def state_overrides(state: dict[str, Any]) -> None:
        state["independentReview"] = {
            "status": "APPROVED", "tool": "promotion simulation", "reviewedAt": utc_now(),
            "justification": f"Independent audit of {subject['checkpoint']}", "evidence": []}
        state["redTeam"] = {
            "status": "RED_TEAM_PASS", "tool": "promotion simulation",
            "executedAt": utc_now(), "justification": "Battery executed by the auditor",
            "evidence": []}
        state["secondToolValidation"] = {
            "status": "PASSED", "tool": "promotion simulation", "provider": "local",
            "model": "not-applicable", "validatedAt": utc_now(),
            "justification": f"Independent audit of {subject['checkpoint']} by {mechanism}",
            "evidence": ["file:FINAL-REPORT.md"]}
        state["milestone"] = {
            "id": "M0", "title": "Development control plane", "gates": ["SETUP-00"],
            "status": "PASSED", "auditor": "promotion simulation", "auditedAt": utc_now(),
            "evidence": ["file:FINAL-REPORT.md"]}
        state["externalAttestation"] = {
            "status": "VERIFIED", "path": attestation_path["value"], "auditId": audit_id,
            "subjectCheckpoint": subject["checkpoint"], "subjectCommit": subject["commit"],
            "validationMechanism": mechanism, "evidence": ["file:FINAL-REPORT.md"]}

    audit = deliver_checkpoint(
        root, scope="independent-audit", status=status,
        before_gates=before_gates, state_overrides=state_overrides)

    verdict = derive_milestone_verdict(root, "M0")
    subject_after = {
        "commit": resolve_tag(root, subject["tag"]),
        "tree": commit_tree(root, str(resolve_tag(root, subject["tag"]))),
        "state": (root / "docs" / "checkpoints" / subject["checkpoint"]
                  / "STATE.json").read_text(encoding="utf-8"),
    }
    return {
        "root": str(root),
        "subject": subject,
        "audit": audit,
        "attestation": attestation_path.get("value"),
        "milestoneVerdict": verdict,
        "subjectImmutable": (
            subject_after["commit"] == subject["commit"]
            and subject_after["tree"] == subject["tree"]
            and subject_after["state"] == subject_state_before),
        "subjectStatusAfter": json.loads(subject_after["state"])["status"],
        "chainErrors": verify_chain(root, require_sealed=True,
                                    exclude=pending_anchor_exclusion(root)),
    }


def run_successor_durability(workdir: Path, *, successors: int = 2) -> dict[str, Any]:
    """Seal a chain of checkpoints, each anchoring its predecessor, and check every state."""
    root = workdir / "succession"
    build_fixture_repository(root)

    states: list[dict[str, Any]] = []
    sealed: list[dict[str, Any]] = []

    def observe(label: str) -> dict[str, Any]:
        from anchors import load_anchors, pending_anchor_checkpoint

        integrity = _tool(root, "verify_integrity.py")
        observation = {
            "state": label,
            "sealed": sealed_checkpoint_ids(root),
            "anchored": [item["checkpointId"] for item in load_anchors(root)],
            "pendingAnchor": pending_anchor_checkpoint(root),
            "chainErrors": verify_chain(root, require_sealed=True,
                                        exclude=pending_anchor_exclusion(root)),
            "integrityExit": integrity.returncode,
            "integrityOutput": integrity.stdout.strip().splitlines()[:1],
        }
        states.append(observation)
        return observation

    first = deliver_checkpoint(root, scope="control-plane", status="READY_FOR_REVIEW")
    sealed.append(first)
    observe(f"{first['checkpoint']} sealed, its anchor still owed")

    for index in range(successors):
        successor = deliver_checkpoint(
            root, scope="control-plane", status="READY_FOR_REVIEW",
            before_gates=lambda repository, checkpoint: _rebuild_anchors(
                repository, exclude=checkpoint.name))
        sealed.append(successor)
        observe(f"{successor['checkpoint']} sealed, anchoring {sealed[index]['checkpoint']}")

    # The guardrail must still bite: removing the anchor of a checkpoint the pending rule does not
    # forgive has to be detected, at the last state, without naming any checkpoint by literal.
    from anchors import load_anchors, pending_anchor_checkpoint

    pending = pending_anchor_checkpoint(root)
    anchors_path = root / ".iacode" / "anchors" / "checkpoint-chain.json"
    document = read_json(anchors_path)
    victim = [item["checkpointId"] for item in load_anchors(root)
              if item["checkpointId"] != pending][-1]
    original = json.dumps(document, ensure_ascii=False)
    document["anchors"] = [item for item in document["anchors"]
                           if item["checkpointId"] != victim]
    write_json(anchors_path, document)
    detection = verify_chain(root, require_sealed=True, exclude=pending_anchor_exclusion(root))
    anchors_path.write_text(json.dumps(json.loads(original), indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8", newline="\n")

    return {
        "root": str(root),
        "checkpoints": sealed,
        "states": states,
        "removedAnchor": victim,
        "detectionErrors": detection,
        # The chain reports a missing anchor with one message when other anchors remain and with
        # another when removing it empties the chain. Both are detections, and both must name the
        # checkpoint whose anchor went missing.
        "detected": any("integrity anchor" in error and victim in error for error in detection),
        "restoredChainErrors": verify_chain(root, require_sealed=True,
                                            exclude=pending_anchor_exclusion(root)),
    }
