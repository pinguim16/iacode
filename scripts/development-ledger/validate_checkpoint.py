#!/usr/bin/env python3
"""Validate an IACode checkpoint and its relationship to the repository."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from anchors import verify_chain
from attestation import resolve_external_pass, statuses_for_mechanism
from delivery_assurance import (
    collect_test_ids,
    completeness_scope,
    evaluate_matrix,
    load_command_results,
)
from lessons import (
    RESOLVING_MEMORY_POLICIES,
    guardrail_effectiveness,
    memory_policy_version,
    preflight_staleness,
    validate_lessons as validate_engineering_memory,
)
from policies import mandatory_gates, open_audits
from ledger_common import (
    CLOSURE_SCHEMA_VERSION,
    CLOSURE_SCHEMA_VERSIONS,
    COMMAND_RESULTS,
    CURRENT_SCHEMA_VERSION,
    DELIVERY_SCHEMA_VERSION,
    DELIVERY_SCHEMA_VERSIONS,
    EVIDENCE_SCHEMA_VERSION,
    EXTERNAL_AUDIT_TRIGGERS,
    EXTERNAL_PASS_STATUS,
    INDEPENDENT_AUDIT_PASS_STATUS,
    INDEPENDENT_DIMENSIONS,
    INVENTORY_SELF_REFERENTIAL_FILES,
    LEGACY_SCHEMA_VERSION,
    MEMORY_SCHEMA_VERSIONS,
    QUALITY_DIMENSIONS,
    QUALITY_DIMENSIONS_V3,
    QUALITY_OUTCOMES,
    REQUIRED_CHECKPOINT_FILES,
    SCHEMA_BINDINGS,
    STATUSES,
    UNBLOCKED_STATUSES,
    LedgerError,
    blob_hash,
    canonical_hash_path,
    find_root,
    find_secrets,
    git_delta,
    git_snapshot,
    load_json,
    milestone_for,
    normalize_gate,
    requires_external_validation,
    resolve_latest,
    run_git,
    scope_fingerprint,
    validate_schema,
)

# Schema versions whose FILES.json is a hash-bound description of the real change set.
HASHED_INVENTORY_VERSIONS = (EVIDENCE_SCHEMA_VERSION,) + DELIVERY_SCHEMA_VERSIONS

# The requirement set exists from the first moment of a delivery-assurance checkpoint.
REQUIRED_DELIVERY_FILES = (
    "REQUIREMENTS-MATRIX.json",
    "REQUIREMENTS-MATRIX.md",
)

# The closure view of the requirement set exists from the first moment of a 3.2.0 checkpoint,
# because the expected set is derived before anything is implemented.
REQUIRED_CLOSURE_FILES = (
    "CLOSURE-REQUIREMENTS.json",
    "CLOSURE-REQUIREMENTS.md",
)

# The assurance artifacts only have to be populated once the delivery is offered for review.
REQUIRED_HANDOFF_FILES = (
    "REWORK-LOG.jsonl",
    "COMPLETENESS-REPORT.json",
    "COMPLETENESS-REPORT.md",
    "FINAL-REPORT.md",
)

# Runtime tokens that make a recorded command literally executable from its working directory.
RUNTIME_TOKENS = ("python", "python3", "git", "bash", "sh", "powershell", "pwsh", "cmd")


HANDOFF_HEADINGS = (
    "## Objective",
    "## What was completed",
    "## What was NOT completed",
    "## Current repository state",
    "## Files changed",
    "## Important decisions",
    "## Tests executed",
    "## Known failures",
    "## Known risks",
    "## Do not repeat",
    "## Required next action",
    "## Exact continuation sequence",
    "## Validation commands",
    "## Stop conditions",
)

FINAL_REPORT_HEADINGS = (
    "## Status",
    "## Environment",
    "## Tool / Model / Effort",
    "## Deliverables",
    "## Files Created",
    "## Files Modified",
    "## Validation",
    "## Tests",
    "## Red Team",
    "## Known Risks",
    "## Remaining Work",
    "## Handoff Readiness",
    "## Next Gate",
    "## Evidence",
)

HANDOFF_READY_STATUSES = (
    "READY_FOR_REVIEW",
    "READY_FOR_RED_TEAM",
    "INTERNAL_GATE_PASS",
    "MILESTONE_INDEPENDENT_AUDIT_PASS",
    "MILESTONE_EXTERNAL_PASS",
    "GATE_PASS",
    "GATE_FAIL",
)

# Every status that asserts the delivery is good. The M0 audit escaped because the strong checks
# were attached to READY_FOR_REVIEW alone, so a mutated MILESTONE_EXTERNAL_PASS carrying a failed
# Green Keeper produced no error. One invariant now covers all of them, and each status adds
# requirements on top of it instead of replacing it.
POSITIVE_TERMINAL_STATUSES = (
    "READY_FOR_REVIEW",
    "READY_FOR_RED_TEAM",
    "INTERNAL_GATE_PASS",
    "MILESTONE_INDEPENDENT_AUDIT_PASS",
    "MILESTONE_EXTERNAL_PASS",
    "GATE_PASS",
)

# The statuses that record an independent audit's verdict about a subject checkpoint. They are
# carried by the audit checkpoint, never by the delivery being judged.
MILESTONE_VERDICT_STATUSES = (
    "MILESTONE_INDEPENDENT_AUDIT_PASS",
    "MILESTONE_EXTERNAL_PASS",
)

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _all_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _canonical_hash(path: Path) -> str:
    return canonical_hash_path(path)


def _relative_to_root(root: Path, path: Path) -> str | None:
    """Repository-relative POSIX path, or None when the path lives outside the repository.

    Test fixtures legitimately place a checkpoint outside the repository they validate against, so
    a control that needs a repository-relative name degrades instead of raising.
    """
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return None


def _resolve_expected_commit(root: Path, expected: Any, actual_head: str, allow_pending_ref: bool) -> str | None:
    if expected == "HEAD":
        return actual_head if actual_head != "UNBORN" else None
    if expected == "UNBORN":
        return "UNBORN"
    if isinstance(expected, str) and expected.startswith("refs/tags/iacode-checkpoints/"):
        code, resolved = run_git(root, "rev-parse", "--verify", f"{expected}^{{commit}}")
        if code != 0:
            return actual_head if allow_pending_ref else None
        return resolved
    return expected if isinstance(expected, str) else None


def _schema_version(state: Any) -> str:
    if isinstance(state, dict) and isinstance(state.get("schemaVersion"), str):
        return state["schemaVersion"]
    return LEGACY_SCHEMA_VERSION


def _normalize_quality(quality: Any) -> dict[str, dict[str, Any]]:
    """Return {dimension: {status, evidence, justification}} for both quality shapes."""
    normalized: dict[str, dict[str, Any]] = {}
    if not isinstance(quality, dict):
        return normalized
    checks = quality.get("checks")
    if isinstance(checks, dict):
        for dimension, entry in checks.items():
            if isinstance(entry, dict):
                normalized[dimension] = {
                    "status": entry.get("status"),
                    "evidence": entry.get("evidence") or [],
                    "justification": entry.get("justification"),
                }
        return normalized
    for dimension, status in quality.items():
        if dimension != "schemaVersion":
            normalized[dimension] = {"status": status, "evidence": [], "justification": None}
    return normalized


def _validate_git_binding(
    root: Path,
    state: dict[str, Any],
    actual: dict[str, Any],
    allow_dirty: bool,
    allow_pending_ref: bool,
    errors: list[str],
) -> None:
    """R1: bind the checkpoint to a commit, accepting a detached HEAD only at its own tag."""
    expected_commit = state.get("currentCommit")
    resolved_commit = _resolve_expected_commit(root, expected_commit, actual["head"], allow_pending_ref)
    if resolved_commit is None:
        errors.append(f"commit reference cannot be resolved: {expected_commit!r}")
    elif resolved_commit != actual["head"]:
        errors.append(
            f"commit mismatch: expected {expected_commit!r} -> {resolved_commit!r}, observed {actual['head']!r}"
        )

    if not actual["detached"]:
        if state.get("branch") != actual["branch"]:
            errors.append(f"branch mismatch: expected {state.get('branch')!r}, observed {actual['branch']!r}")
        if not allow_dirty and state.get("dirty") != actual["dirty"]:
            errors.append(f"dirty-state mismatch: expected {state.get('dirty')!r}, observed {actual['dirty']!r}")
        return

    # Detached HEAD is a legitimate way to inspect a sealed checkpoint, but it removes the
    # branch identity control, so every remaining anchor is mandatory and no relaxation applies.
    if actual["dirty"] or state.get("dirty") is not False:
        errors.append("detached HEAD validation requires a clean worktree and dirty=false")
    if not (isinstance(expected_commit, str) and expected_commit.startswith("refs/tags/iacode-checkpoints/")):
        errors.append("detached HEAD validation requires STATE.json currentCommit to name the checkpoint tag")
        return
    code, tag_commit = run_git(root, "rev-parse", "--verify", f"{expected_commit}^{{commit}}")
    if code != 0:
        errors.append(f"detached HEAD validation requires an existing checkpoint tag: {expected_commit}")
    elif tag_commit != actual["head"]:
        errors.append(
            f"checkpoint tag does not resolve to the checked-out commit: {expected_commit} -> {tag_commit}, observed {actual['head']}"
        )


def _manifest_entries(files: Any) -> tuple[dict[str, tuple[str, dict[str, Any]]], list[str]]:
    mapping: dict[str, tuple[str, dict[str, Any]]] = {}
    duplicates: list[str] = []
    for category, letter in (("filesCreated", "A"), ("filesModified", "M"), ("filesDeleted", "D")):
        for item in (files.get(category) or []) if isinstance(files, dict) else []:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                continue
            path = item["path"].replace("\\", "/")
            if path in mapping:
                duplicates.append(path)
            mapping[path] = (letter, item)
    return mapping, duplicates


def _validate_delta_inventory(
    root: Path,
    target: Path,
    state: dict[str, Any],
    files: Any,
    compare_worktree: bool,
    errors: list[str],
) -> None:
    """R2: require FILES.json to describe the real change set, with bound content hashes."""
    base = state.get("baseCommit")
    if not isinstance(base, str) or base in ("UNBORN", "HEAD"):
        errors.append("a delta checkpoint requires baseCommit to name an exact commit or checkpoint tag")
        return
    base_commit = _resolve_expected_commit(root, base, "UNBORN", False)
    if base_commit is None or base_commit == "UNBORN":
        errors.append(f"baseCommit cannot be resolved: {base!r}")
        return

    # A sealed checkpoint is compared commit to commit. While work is still uncommitted, the
    # comparison target is the working tree, so the inventory can be validated before finalization.
    try:
        delta = git_delta(root, base_commit, None if compare_worktree else "HEAD")
    except LedgerError as exc:
        errors.append(str(exc))
        return

    mapping, duplicates = _manifest_entries(files)
    for path in sorted(set(duplicates)):
        errors.append(f"FILES.json declares {path} in more than one category")

    letters = {"A": "added", "M": "modified", "D": "deleted"}
    for path in sorted(set(delta) - set(mapping)):
        errors.append(f"FILES.json omits a changed path: {path} ({letters[delta[path]]})")
    for path in sorted(set(mapping) - set(delta)):
        errors.append(f"FILES.json declares a path that did not change since baseCommit: {path}")
    for path in sorted(set(mapping) & set(delta)):
        declared, observed = mapping[path][0], delta[path]
        if declared != observed:
            errors.append(
                f"FILES.json declares {path} as {letters[declared]} but the repository shows it as {letters[observed]}"
            )

    self_referential = {
        str((target / name).relative_to(root)).replace("\\", "/") for name in INVENTORY_SELF_REFERENTIAL_FILES
    }
    for path in sorted(set(mapping) & set(delta)):
        letter, item = mapping[path]
        before, after = item.get("hashBefore"), item.get("hashAfter")
        if path in self_referential:
            continue
        if letter in ("A", "M"):
            if not isinstance(after, str) or HEX64.fullmatch(after) is None:
                errors.append(f"FILES.json requires a sha-256 hashAfter for {path}")
            else:
                candidate = root / path
                if not candidate.is_file():
                    errors.append(f"FILES.json hashed path does not exist: {path}")
                elif canonical_hash_path(candidate) != after:
                    errors.append(f"FILES.json hashAfter does not match the repository content of {path}")
        if letter in ("M", "D"):
            if not isinstance(before, str) or HEX64.fullmatch(before) is None:
                errors.append(f"FILES.json requires a sha-256 hashBefore for {path}")
            else:
                observed_before = blob_hash(root, base_commit, path)
                if observed_before is None:
                    errors.append(f"FILES.json declares {path} as pre-existing but it is absent from baseCommit")
                elif observed_before != before:
                    errors.append(f"FILES.json hashBefore does not match the baseCommit content of {path}")
        if letter == "A" and item.get("hashBefore") is not None:
            errors.append(f"FILES.json must not declare hashBefore for the added path {path}")
        if letter == "D":
            if after is not None:
                errors.append(f"FILES.json must not declare hashAfter for the deleted path {path}")
            if (root / path).exists():
                errors.append(f"FILES.json declares {path} as deleted but it still exists")


def _validate_empty_project_inventory(root: Path, files: Any, files_path: Path, errors: list[str]) -> None:
    code, tracked_output = run_git(root, "ls-files")
    if code != 0:
        errors.append("unable to enumerate tracked files for empty-project completeness")
        return
    tracked = {line.replace("\\", "/") for line in tracked_output.splitlines() if line}
    created_items = files.get("filesCreated", []) if isinstance(files, dict) else []
    created = {item.get("path", "").replace("\\", "/") for item in created_items if isinstance(item, dict)}
    missing = sorted(tracked - created)
    if missing:
        errors.append("FILES.json omits tracked files created from EMPTY_PROJECT: " + ", ".join(missing))
    own_path = str(files_path.relative_to(root)).replace("\\", "/")
    for item in created_items:
        if isinstance(item, dict) and item.get("path") != own_path and not item.get("hashAfter"):
            errors.append(f"FILES.json created entry lacks hashAfter: {item.get('path')}")


def _validate_command_reproducibility(
    root: Path,
    record: dict[str, Any],
    line_number: int,
    errors: list[str],
    bind_inputs: bool = False,
) -> None:
    """R3.2 and RT-02: a recorded command must be auditable and runnable where it says it ran."""
    prefix = f"COMMANDS.jsonl:{line_number}"
    for field in ("runtime", "commit", "purpose"):
        if not record.get(field):
            errors.append(f"{prefix}: schemaVersion 3.0.0 requires {field}")

    result = record.get("result")
    if result not in COMMAND_RESULTS:
        errors.append(f"{prefix}: unsupported result {result!r}")
    elif result == "COMPLETED":
        if not isinstance(record.get("exitCode"), int):
            errors.append(f"{prefix}: a COMPLETED command requires an integer exitCode")
    else:
        if record.get("exitCode") is not None:
            errors.append(f"{prefix}: {result} must not carry a fabricated exitCode")
        if not record.get("resultCode"):
            errors.append(f"{prefix}: {result} requires a canonical resultCode")
        if not record.get("failureReason"):
            errors.append(f"{prefix}: {result} requires a failureReason")

    command = record.get("command")
    if not isinstance(command, str) or not command.strip():
        return
    tokens = command.split()
    first = tokens[0]
    if first not in RUNTIME_TOKENS:
        errors.append(
            f"{prefix}: the recorded command must start with an explicit runtime such as "
            f"{RUNTIME_TOKENS[0]!r}, found {first!r}"
        )
    for token in tokens[1:]:
        if token.endswith(".py"):
            if not (root / token).is_file():
                errors.append(f"{prefix}: recorded script path does not resolve from the repository: {token}")
            break

    inputs = [str(item) for item in record.get("inputs") or []]
    for reference in inputs:
        if not (root / reference).exists():
            errors.append(f"{prefix}: recorded input does not exist: {reference}")

    # M0-F-009: a record that names a commit while its real inputs lived only in a dirty working
    # tree is not reproducible. The digest binds what the command actually read, so replay can be
    # verified against content instead of against a commit that never held it.
    if bind_inputs and inputs:
        digest = record.get("inputsDigest")
        if not isinstance(digest, list):
            errors.append(
                f"{prefix}: schemaVersion {CLOSURE_SCHEMA_VERSION} requires inputsDigest binding "
                f"every declared input by content")
            return
        bound = {
            str(item.get("path")): str(item.get("hash"))
            for item in digest if isinstance(item, dict)
        }
        for reference in inputs:
            if reference not in bound:
                errors.append(f"{prefix}: inputsDigest does not bind the declared input {reference}")
            elif HEX64.fullmatch(bound[reference]) is None and bound[reference] != "ABSENT":
                errors.append(f"{prefix}: inputsDigest for {reference} is not a sha-256 digest")
        for reference in sorted(set(bound) - set(inputs)):
            errors.append(f"{prefix}: inputsDigest binds {reference}, which is not a declared input")

        # When the tree was clean, the declared commit must really contain what was read, so the
        # replay context is provable rather than asserted.
        clean = (record.get("repositoryState") or {}).get("dirty") is False
        commit = record.get("commit")
        if clean and isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit):
            for reference in inputs:
                expected = bound.get(reference)
                if expected in (None, "ABSENT"):
                    continue
                observed = blob_hash(root, commit, reference)
                if observed is None:
                    errors.append(
                        f"{prefix}: the record claims a clean tree at {commit[:12]} but the input "
                        f"{reference} does not exist there")
                elif observed != expected:
                    errors.append(
                        f"{prefix}: the record claims a clean tree at {commit[:12]} but the input "
                        f"{reference} had different content there")


def _validate_status_blockers(state: dict[str, Any], errors: list[str]) -> None:
    """RT-01: a checkpoint may never claim readiness while it also claims to be blocked."""
    status = state.get("status")
    blockers = state.get("blockedBy")
    blocker_list = blockers if isinstance(blockers, list) else []
    if status in UNBLOCKED_STATUSES and blocker_list:
        errors.append(
            f"{status} is incompatible with a non-empty blockedBy: {', '.join(str(item) for item in blocker_list)}"
        )
    if status == "BLOCKED" and not blocker_list:
        errors.append("BLOCKED requires at least one entry in blockedBy")


def _validate_green_keeper_cycle(
    root: Path,
    green: dict[str, Any],
    cycle: dict[str, Any],
    errors: list[str],
    closure: bool,
) -> None:
    """A GREEN cycle must have measured the closed mandatory set against the current content.

    Two failures of ``SETUP-00-CP-0006`` meet here. The gate set was whatever the caller passed, so
    an empty selection produced a vacuous PASS; and a PASS survived any later edit, because nothing
    recorded what content the PASS was a statement about.
    """
    if not closure and not cycle.get("requiredGates"):
        return
    try:
        required = set(mandatory_gates(root))
    except LedgerError as exc:
        errors.append(f"greenKeeper=PASS cannot be verified: {exc}")
        return

    declared = {str(item) for item in cycle.get("requiredGates") or []}
    if declared != required:
        errors.append(
            "greenKeeper=PASS was measured against "
            f"{', '.join(sorted(declared)) or 'no gate'}, not the canonical mandatory set "
            f"{', '.join(sorted(required))}")

    results = {
        str(item.get("gate")): item
        for item in cycle.get("gateResults") or []
        if isinstance(item, dict)
    }
    for gate in sorted(required):
        entry = results.get(gate)
        if entry is None:
            errors.append(f"greenKeeper=PASS records no execution of the mandatory gate {gate!r}")
            continue
        if entry.get("exitCode") != 0:
            errors.append(
                f"greenKeeper=PASS records the mandatory gate {gate!r} exiting "
                f"{entry.get('exitCode')!r}")
        if not entry.get("commandId"):
            errors.append(f"greenKeeper=PASS records no command evidence for the gate {gate!r}")

    if not cycle.get("commandsExecuted"):
        errors.append("greenKeeper=PASS requires recorded command evidence for the cycle")

    observed = scope_fingerprint(root)
    recorded = cycle.get("scopeFingerprint")
    if not recorded:
        errors.append(
            "greenKeeper=PASS requires the cycle to record the scope fingerprint it was measured "
            "against; without it a PASS cannot be distinguished from a stale one")
    elif recorded != observed:
        errors.append(
            "greenKeeper=PASS is STALE: the delivery-assurance scope changed after the last GREEN "
            "cycle, so the Green Keeper must run again")
    if green.get("scopeFingerprint") not in (None, recorded):
        errors.append(
            "STATE.json greenKeeper.scopeFingerprint does not match the last GREEN rework cycle")


def _validate_delivery_assurance(
    root: Path,
    target: Path,
    state: dict[str, Any],
    normalized_quality: dict[str, dict[str, Any]],
    tests: Any,
    errors: list[str],
    closure: bool = False,
) -> None:
    """Enforce the Green Keeper and Delivery Completeness gates and their stored evidence.

    ``closure`` selects the schemaVersion 3.2.0 rules: the closed mandatory gate set, the scope
    fingerprints that make a stale PASS detectable, and the derived expected requirement set.
    Sealed 3.0.0 and 3.1.0 checkpoints predate those artifacts and keep validating under their own
    version's rules.
    """
    status = state.get("status")
    green = state.get("greenKeeper")
    delivery = state.get("deliveryCompleteness")
    matrix_state = state.get("requirementsMatrix")
    review = state.get("independentReview")
    red_team = state.get("redTeam")

    for name, block in (
        ("requirementsMatrix", matrix_state),
        ("greenKeeper", green),
        ("deliveryCompleteness", delivery),
        ("independentReview", review),
        ("redTeam", red_team),
    ):
        if not isinstance(block, dict):
            errors.append(f"STATE.json schemaVersion 3.0.0 requires the {name} block")
    if not isinstance(state.get("reworkCycles"), int):
        errors.append("STATE.json schemaVersion 3.0.0 requires an integer reworkCycles")

    # The rework log is the Green Keeper's own evidence; its last cycle must agree with the gate.
    cycles: list[dict[str, Any]] = []
    log_path = target / "REWORK-LOG.jsonl"
    if log_path.is_file():
        schema_path = root / ".iacode" / "schemas" / "rework-log.schema.json"
        schema = load_json(schema_path) if schema_path.is_file() else None
        for index, line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"REWORK-LOG.jsonl:{index}: invalid JSON: {exc}")
                continue
            if schema:
                for error in validate_schema(entry, schema):
                    errors.append(f"REWORK-LOG.jsonl:{index}: {error}")
            cycles.append(entry)

    # The gate values describe a delivery, so they are enforced when the delivery is offered. While a
    # checkpoint is still being worked on they are provisional, which is what lets the Green Keeper
    # validate the very checkpoint that records its own cycles.
    offered = status in HANDOFF_READY_STATUSES
    if isinstance(green, dict) and offered:
        if green.get("cycles") != len(cycles):
            errors.append(
                f"STATE.json greenKeeper.cycles={green.get('cycles')!r} does not match "
                f"{len(cycles)} recorded rework cycles"
            )
        if isinstance(state.get("reworkCycles"), int) and state["reworkCycles"] != len(cycles):
            errors.append("STATE.json reworkCycles does not match the recorded rework cycles")
        if green.get("status") == "PASS":
            if not cycles:
                errors.append("greenKeeper=PASS requires at least one recorded rework cycle")
            elif cycles[-1].get("result") != "GREEN":
                errors.append(
                    f"greenKeeper=PASS contradicts the last rework cycle result "
                    f"{cycles[-1].get('result')!r}"
                )
            else:
                _validate_green_keeper_cycle(root, green, cycles[-1], errors, closure)
            if green.get("remainingFailures"):
                errors.append("greenKeeper=PASS requires remainingFailures to be zero")
            if green.get("unresolvedReworkItems"):
                errors.append("greenKeeper=PASS requires unresolvedReworkItems to be zero")
            if isinstance(tests, dict):
                for key in ("unit", "integration", "e2e"):
                    result = tests.get(key)
                    if isinstance(result, dict) and result.get("failed"):
                        errors.append(f"greenKeeper=PASS contradicts TESTS.json {key}.failed={result['failed']}")
            for dimension, entry in normalized_quality.items():
                if dimension not in INDEPENDENT_DIMENSIONS and entry.get("status") == "FAIL":
                    errors.append(f"greenKeeper=PASS contradicts QUALITY.json {dimension}=FAIL")

    # The completeness report is recomputed from the matrix, so a stored verdict cannot drift.
    report_path = target / "COMPLETENESS-REPORT.json"
    matrix_path = target / "REQUIREMENTS-MATRIX.json"
    recomputed: dict[str, Any] | None = None
    if matrix_path.is_file():
        try:
            matrix = load_json(matrix_path)
        except LedgerError as exc:
            errors.append(str(exc))
            matrix = None
        if matrix is not None:
            schema_path = root / ".iacode" / "schemas" / "requirements-matrix.schema.json"
            if schema_path.is_file():
                for error in validate_schema(matrix, load_json(schema_path)):
                    errors.append(f"REQUIREMENTS-MATRIX.json: {error}")
            recomputed = evaluate_matrix(
                root, target, matrix, load_command_results(target), collect_test_ids(root))
            if isinstance(matrix_state, dict) and offered:
                for key in ("total", "mandatory", "complete", "partial", "missing", "notApplicable"):
                    source = {
                        "total": "totalRequirements", "mandatory": "mandatoryRequirements",
                        "complete": "complete", "partial": "partial",
                        "missing": "missing", "notApplicable": "notApplicable",
                    }[key]
                    if key == "mandatory" and not closure:
                        continue
                    if key == "mandatory" and "mandatory" not in matrix_state:
                        errors.append(
                            "STATE.json requirementsMatrix must declare mandatory; the audit found "
                            "a sealed state claiming a mandatory count no artifact agreed with")
                        continue
                    if matrix_state.get(key) != recomputed[source]:
                        errors.append(
                            f"STATE.json requirementsMatrix.{key}={matrix_state.get(key)!r} does not match "
                            f"the matrix value {recomputed[source]!r}"
                        )
                if matrix_state.get("coveragePercent") != recomputed["coveragePercent"]:
                    errors.append("STATE.json requirementsMatrix.coveragePercent does not match the matrix")

    if report_path.is_file():
        try:
            report = load_json(report_path)
        except LedgerError as exc:
            errors.append(str(exc))
            report = None
        if isinstance(report, dict):
            schema_path = root / ".iacode" / "schemas" / "completeness-report.schema.json"
            if schema_path.is_file():
                for error in validate_schema(report, load_json(schema_path)):
                    errors.append(f"COMPLETENESS-REPORT.json: {error}")
            if recomputed is not None and offered:
                for key in ("totalRequirements", "mandatoryRequirements", "expectedRequirements",
                            "complete", "partial", "missing", "notApplicable",
                            "coveragePercent", "evidenceCoveragePercent", "result"):
                    if key not in recomputed:
                        continue
                    # The derived expected set arrived with report schemaVersion 2.0.0; sealed
                    # 1.0.0 reports are read under their own version's rules.
                    if key in ("expectedRequirements",) and report.get("schemaVersion") != "2.0.0":
                        continue
                    if report.get(key) != recomputed[key]:
                        errors.append(
                            f"COMPLETENESS-REPORT.json {key}={report.get(key)!r} contradicts the "
                            f"recomputed value {recomputed[key]!r}"
                        )
            if offered and isinstance(delivery, dict) and delivery.get("status") != report.get("result"):
                errors.append(
                    f"STATE.json deliveryCompleteness.status={delivery.get('status')!r} contradicts "
                    f"COMPLETENESS-REPORT.json result={report.get('result')!r}"
                )
            if offered and report.get("result") == "PASS" and (
                    closure or report.get("schemaVersion") == "2.0.0"):
                observed = scope_fingerprint(root, completeness_scope(root, target))
                recorded = report.get("scopeFingerprint")
                if not recorded:
                    errors.append(
                        "a passing completeness report must record the scope fingerprint it "
                        "audited, otherwise a later change cannot make it stale")
                elif recorded != observed:
                    errors.append(
                        "DELIVERY_COMPLETENESS_GATE is STALE: the code, requirements, lessons or "
                        "policy changed after the audit, so it must run again")

    if status not in POSITIVE_TERMINAL_STATUSES:
        return

    # ---- the shared promotion invariant, identical for every positive terminal status ----
    if isinstance(green, dict) and green.get("status") != "PASS":
        errors.append(f"{status} requires GREEN_KEEPER_GATE=PASS, found {green.get('status')!r}")
    if isinstance(delivery, dict):
        if delivery.get("status") != "PASS":
            errors.append(
                f"{status} requires DELIVERY_COMPLETENESS_GATE=PASS, found {delivery.get('status')!r}")
        if delivery.get("coveragePercent") != 100.0:
            errors.append(
                f"{status} requires total requirement coverage, found "
                f"{delivery.get('coveragePercent')!r}")
        if delivery.get("evidenceCoveragePercent") not in (None, 100.0):
            errors.append(
                f"{status} requires total evidence coverage, found "
                f"{delivery.get('evidenceCoveragePercent')!r}")
    if recomputed is not None:
        if recomputed["partial"]:
            errors.append(f"{status} requires zero PARTIAL requirements, found {recomputed['partial']}")
        if recomputed["missing"]:
            errors.append(f"{status} requires zero MISSING requirements, found {recomputed['missing']}")
        if recomputed["result"] != "PASS":
            for finding in recomputed["findings"]:
                if finding["severity"] == "BLOCKING":
                    errors.append(f"{status} blocked by {finding['requirement']}: {finding['detail']}")
    for dimension in QUALITY_DIMENSIONS_V3:
        if dimension in INDEPENDENT_DIMENSIONS:
            continue
        entry = normalized_quality.get(dimension) or {}
        if entry.get("status") == "NOT_EXECUTED":
            errors.append(f"{status} requires QUALITY.json {dimension} to be executed")
        if entry.get("status") == "FAIL":
            errors.append(f"{status} cannot have QUALITY.json {dimension}=FAIL")

    # ---- what each status adds on top of the shared invariant ----
    if status in ("READY_FOR_REVIEW", "READY_FOR_RED_TEAM"):
        if isinstance(review, dict) and status == "READY_FOR_REVIEW" and review.get("status") != "PENDING":
            errors.append(
                f"READY_FOR_REVIEW requires independentReview to be PENDING, found "
                f"{review.get('status')!r}")
        if isinstance(red_team, dict) and red_team.get("status") != "PENDING":
            errors.append(f"{status} requires redTeam to be PENDING, found {red_team.get('status')!r}")
    else:
        if isinstance(review, dict) and review.get("status") not in ("APPROVED", "NOT_REQUIRED"):
            errors.append(
                f"{status} requires an independent review verdict, found {review.get('status')!r}")
        if isinstance(red_team, dict) and red_team.get("status") not in (
                "RED_TEAM_PASS", "NOT_REQUIRED"):
            errors.append(
                f"{status} requires a Red Team verdict, found {red_team.get('status')!r}")


def _validate_memory_policy(
    root: Path,
    target: Path,
    state: dict[str, Any],
    errors: list[str],
    closure: bool = False,
) -> None:
    """Engineering memory and milestone validation policy, bound to schemaVersion 3.1.0.

    ``closure`` selects the schemaVersion 3.2.0 additions: preflight freshness recomputed from the
    memory, and a milestone verdict derived from an audit attestation rather than asserted. Sealed
    3.1.0 checkpoints keep validating under their own version's rules.
    """
    status = state.get("status")
    offered = status in HANDOFF_READY_STATUSES
    review = state.get("independentReview")
    red_team = state.get("redTeam")

    # The memory is a control, so a broken memory is a broken checkpoint.
    for error in validate_engineering_memory(root):
        errors.append(f"engineering memory: {error}")
    if closure and memory_policy_version(root) not in RESOLVING_MEMORY_POLICIES:
        errors.append(
            "schemaVersion 3.2.0 requires an engineering memory policy that resolves every "
            "control, evidence and provenance reference ("
            + ", ".join(RESOLVING_MEMORY_POLICIES)
            + f"); found {memory_policy_version(root)!r}")

    preflight_state = state.get("lessonPreflight")
    if not isinstance(preflight_state, dict):
        errors.append("STATE.json schemaVersion 3.1.0 requires the lessonPreflight block")
    preflight_path = target / "LESSON-PREFLIGHT.json"
    preflight: dict[str, Any] | None = None
    if preflight_path.is_file():
        try:
            preflight = load_json(preflight_path)
        except LedgerError as exc:
            errors.append(str(exc))
        schema_path = root / ".iacode" / "schemas" / "lesson-preflight.schema.json"
        if isinstance(preflight, dict) and schema_path.is_file():
            for error in validate_schema(preflight, load_json(schema_path)):
                errors.append(f"LESSON-PREFLIGHT.json: {error}")
    elif offered:
        errors.append(f"{status} requires LESSON-PREFLIGHT.json; the lesson preflight is mandatory")

    if isinstance(preflight_state, dict) and isinstance(preflight, dict):
        for key, source in (("lessonsConsidered", "lessonsConsidered"),
                            ("lessonsApplicable", "lessonsApplicable")):
            if preflight_state.get(key) != preflight.get(source):
                errors.append(
                    f"STATE.json lessonPreflight.{key}={preflight_state.get(key)!r} does not match "
                    f"LESSON-PREFLIGHT.json {source}={preflight.get(source)!r}")
        declared = preflight_state.get("derivedRequirements")
        actual = len(preflight.get("derivedRequirements") or [])
        if declared != actual:
            errors.append(
                f"STATE.json lessonPreflight.derivedRequirements={declared!r} does not match the "
                f"{actual} requirements the preflight derived")
        if preflight_state.get("gate") and normalize_gate(preflight_state["gate"]) != normalize_gate(
                str(preflight.get("gate"))):
            errors.append("STATE.json lessonPreflight.gate does not match LESSON-PREFLIGHT.json")

    # The preflight is bound to the Gate that is actually being delivered, and to the memory it was
    # derived from. Comparing the artifact with the state that stores its own counts proves nothing:
    # the audit reused a SETUP-00 preflight for GATE 1, and kept a stale one after retiring a lesson.
    if isinstance(preflight, dict) and closure:
        if preflight.get("schemaVersion") != "2.0.0":
            errors.append(
                "schemaVersion 3.2.0 requires LESSON-PREFLIGHT.json schemaVersion 2.0.0, which "
                "carries the input fingerprint that makes a stale preflight detectable")
        for message in preflight_staleness(root, preflight, str(state.get("gate", ""))):
            errors.append(f"lesson preflight: {message}")
        if isinstance(preflight_state, dict):
            declared_fingerprint = preflight_state.get("fingerprint")
            if declared_fingerprint not in (None, preflight.get("inputsFingerprint")):
                errors.append(
                    "STATE.json lessonPreflight.fingerprint does not match LESSON-PREFLIGHT.json")

    milestone = state.get("milestone")
    expected = milestone_for(str(state.get("gate", "")))
    if not isinstance(milestone, dict):
        errors.append("STATE.json schemaVersion 3.1.0 requires the milestone block")
    else:
        if expected is None:
            errors.append(f"gate {state.get('gate')!r} does not belong to any planned milestone")
        else:
            identifier, _title, gates = expected
            if milestone.get("id") != identifier:
                errors.append(
                    f"STATE.json milestone.id={milestone.get('id')!r} does not match the planned "
                    f"milestone {identifier} for gate {state.get('gate')!r}")
            declared_gates = [normalize_gate(item) for item in milestone.get("gates") or []]
            if declared_gates != [normalize_gate(item) for item in gates]:
                errors.append(
                    f"STATE.json milestone.gates does not match the planned grouping "
                    f"{', '.join(gates)}")
        if milestone.get("status") == "PASSED" and state.get("secondToolValidation", {}).get("status") != "PASSED":
            errors.append("a milestone may only be PASSED when secondToolValidation is PASSED")
        if closure and milestone.get("status") == "PASSED" and expected is not None:
            identifier = str(milestone.get("id"))
            if not requires_external_validation(
                    str(state.get("gate", "")), bool(state.get("externalAuditRequired"))):
                errors.append(
                    f"gate {state.get('gate')!r} does not close milestone {identifier} and no "
                    f"extraordinary audit is recorded, so it may not report the milestone as PASSED")

    required = state.get("externalAuditRequired")
    reason = state.get("externalAuditReason")
    if required is None:
        errors.append("STATE.json schemaVersion 3.1.0 requires externalAuditRequired")
    if required:
        if not reason:
            errors.append(
                "externalAuditRequired demands externalAuditReason naming the recorded trigger")
        elif not any(trigger in str(reason) for trigger in EXTERNAL_AUDIT_TRIGGERS):
            errors.append(
                "externalAuditReason must name one of the recorded triggers: "
                + ", ".join(EXTERNAL_AUDIT_TRIGGERS))
    elif reason:
        errors.append("externalAuditReason is recorded while externalAuditRequired is false")

    # A milestone verdict is derived from an attestation the *audit* checkpoint wrote about the
    # sealed subject it judged. Two shapes are refused: a delivery that fills secondToolValidation
    # and milestone.status about itself, and the circular shape the second audit found, where the
    # promoted checkpoint had to contain an attestation naming its own commit. The subject stays
    # immutable; the verdict lives in the checkpoint that performed the audit, which names the
    # subject explicitly.
    second_tool = state.get("secondToolValidation") or {}
    attestation_state = state.get("externalAttestation")
    claims_verdict = closure and (
        status in MILESTONE_VERDICT_STATUSES
        or second_tool.get("status") == "PASSED"
        or (isinstance(milestone, dict) and milestone.get("status") == "PASSED")
    )
    verified: dict[str, Any] | None = None
    if claims_verdict:
        identifier = milestone.get("id") if isinstance(milestone, dict) else None
        subject = None
        if isinstance(attestation_state, dict):
            subject = attestation_state.get("subjectCheckpoint")
        if not subject:
            errors.append(
                "independent audit: a milestone verdict requires STATE.json "
                "externalAttestation.subjectCheckpoint naming the sealed checkpoint this audit "
                "judged; the verdict belongs to the audit checkpoint, never to the delivery it "
                "judges")
        else:
            attestation, reasons = resolve_external_pass(
                root, str(identifier), str(subject),
                attestation_state.get("subjectCommit") or None,
                claiming_checkpoint=target.name)
            for reason in reasons:
                errors.append(f"independent audit: {reason}")
            if attestation is not None and not reasons:
                verified = attestation
                for key in ("path", "auditId", "validationMechanism"):
                    expected_value = (
                        attestation.get("__path") if key == "path" else attestation.get(key))
                    if attestation_state.get(key) != expected_value:
                        errors.append(
                            f"STATE.json externalAttestation.{key}="
                            f"{attestation_state.get(key)!r} does not describe the attestation it "
                            f"points at ({expected_value!r})")
                if attestation_state.get("status") != "VERIFIED":
                    errors.append(
                        "STATE.json externalAttestation.status must be VERIFIED when a milestone "
                        "verdict is claimed on a verified attestation")
                if second_tool.get("status") != "PASSED":
                    errors.append(
                        "a verified independent audit attestation exists but secondToolValidation "
                        "does not record PASSED")
                if isinstance(review, dict) and review.get("status") not in ("APPROVED", None):
                    errors.append(
                        f"the attestation records reviewResult=APPROVED while this checkpoint "
                        f"records independentReview={review.get('status')!r}")
                if isinstance(red_team, dict) and red_team.get("status") not in (
                        "RED_TEAM_PASS", None):
                    errors.append(
                        f"the attestation records redTeamResult=RED_TEAM_PASS while this "
                        f"checkpoint records redTeam={red_team.get('status')!r}")

    if status in MILESTONE_VERDICT_STATUSES:
        if not isinstance(milestone, dict) or milestone.get("status") != "PASSED":
            errors.append(f"{status} requires milestone.status=PASSED")
        if second_tool.get("status") != "PASSED":
            errors.append(f"{status} requires secondToolValidation=PASSED")
        if closure and not requires_external_validation(
                str(state.get("gate", "")), bool(state.get("externalAuditRequired"))):
            errors.append(
                f"{status} is only available to a milestone-closing Gate or to a recorded "
                f"extraordinary audit; gate {state.get('gate')!r} is neither")
        if closure and verified is not None:
            permitted = statuses_for_mechanism(verified.get("validationMechanism"))
            if status not in permitted:
                errors.append(
                    f"{status} may not be derived from a "
                    f"{verified.get('validationMechanism')!r} attestation, which authorises "
                    + (", ".join(permitted) if permitted else "no milestone status")
                    + f"; {INDEPENDENT_AUDIT_PASS_STATUS} is the honest status for an audit that "
                    f"is independent of the run but not of the tool")
    if status == "INTERNAL_GATE_PASS" and state.get("secondToolValidation", {}).get("status") == "PASSED":
        # An internal verdict is not the place to record an independent one; use the milestone status.
        errors.append(
            "INTERNAL_GATE_PASS records the project's own verdict; an independently audited PASS "
            f"belongs to {INDEPENDENT_AUDIT_PASS_STATUS} or {EXTERNAL_PASS_STATUS}")


COUNT_CLAIM = re.compile(
    r"(?<![0-9])(\d+)\s*/\s*(\d+)\s+(TESTS|REQUIREMENTS|FINDINGS|ATTACKS|LESSONS|GUARDRAILS)\b")


def _validate_anchor_chain(root: Path, target: Path, state: dict[str, Any], errors: list[str]) -> None:
    """Sealed history is anchored outside the content it describes."""
    for message in verify_chain(root, require_sealed=True, exclude={target.name}):
        errors.append(f"checkpoint integrity: {message}")

    integrity = state.get("integrity")
    if not isinstance(integrity, dict):
        errors.append("STATE.json schemaVersion 3.2.0 requires the integrity block")
        return
    try:
        from anchors import load_anchors

        anchors = load_anchors(root)
    except LedgerError as exc:
        errors.append(f"checkpoint integrity: {exc}")
        return
    if integrity.get("anchors") != len(anchors):
        errors.append(
            f"STATE.json integrity.anchors={integrity.get('anchors')!r} does not match the "
            f"{len(anchors)} recorded anchors")

    # A checkpoint must anchor every sealed predecessor; its own anchor belongs to its successor,
    # because an anchor cannot contain the commit that contains it.
    anchored = {item.get("checkpointId") for item in anchors}
    checkpoints = root / "docs" / "checkpoints"
    for item in sorted(checkpoints.iterdir()) if checkpoints.is_dir() else []:
        if not item.is_dir() or item.name == target.name:
            continue
        code, _ = run_git(root, "rev-parse", "--verify",
                          f"refs/tags/iacode-checkpoints/{item.name}^{{commit}}")
        if code == 0 and item.name not in anchored:
            errors.append(
                f"checkpoint integrity: sealed predecessor {item.name} is not anchored by this "
                f"checkpoint")


def _validate_seal_chronology(
    root: Path,
    target: Path,
    state: dict[str, Any],
    metadata: Any,
    commands: list[dict[str, Any]],
    errors: list[str],
) -> None:
    """Sealing is monotonic and post-commit, and its final evidence describes the sealed content.

    The audit found a run that finished three seconds before the finalizer it recorded, and a last
    validation whose evidence pointed at a pre-tag commit with a dirty tree.
    """
    finished = _parse_datetime(metadata.get("finishedAt")) if isinstance(metadata, dict) else None
    if finished is not None:
        for record in commands:
            stamp = _parse_datetime(record.get("timestamp"))
            if stamp is not None and stamp > finished:
                errors.append(
                    f"COMMANDS.jsonl {record.get('id')} is timestamped after "
                    f"RUN-METADATA.finishedAt; sealing must be monotonic")
                break

    sealed = [
        record for record in commands
        if record.get("operation") == "post-commit-validation"
        and record.get("exitCode") == 0
        and (record.get("repositoryState") or {}).get("dirty") is False
    ]
    if not sealed:
        errors.append(
            f"{state.get('status')} requires a recorded post-commit-validation run with exit code "
            f"0 over a clean worktree; the sealed content must be validated as committed, not as a "
            f"dirty working tree")
        return

    record = sealed[-1]
    commit = str(record.get("commit"))
    code, head = run_git(root, "rev-parse", "HEAD")
    if code != 0:
        errors.append("unable to resolve HEAD for the seal chronology check")
        return
    if commit == head:
        return
    parent_code, parent = run_git(root, "rev-parse", "HEAD^")
    if parent_code != 0 or parent != commit:
        errors.append(
            f"the recorded post-commit validation describes {commit[:12]}, which is neither HEAD "
            f"nor its parent; the sealed content is not the content that was validated")
        return
    diff_code, diff = run_git(root, "diff", "--name-only", commit, head)
    if diff_code != 0:
        errors.append("unable to compare the sealed content commit with HEAD")
        return
    allowed = {
        value for value in (
            _relative_to_root(root, target / name)
            for name in ("COMMANDS.jsonl", "FILES.json", "RUN-METADATA.json")
        ) if value
    }
    unexpected = sorted({line.replace("\\", "/") for line in diff.splitlines() if line} - allowed)
    if unexpected:
        errors.append(
            "the sealing commit changed more than the append-only validation evidence: "
            + ", ".join(unexpected))


def _validate_internal_assurance(
    root: Path,
    target: Path,
    state: dict[str, Any],
    errors: list[str],
) -> None:
    """The internal Red Team and the internal mirror audit, and their freshness.

    Neither is independent validation, and neither may be described as one. They exist so that the
    external audit confirms rather than discovers.
    """
    milestone = state.get("milestone") or {}
    identifier = str(milestone.get("id") or "M0")
    observed = scope_fingerprint(root)

    red_team_path = target / f"{identifier}-INTERNAL-RED-TEAM.json"
    if not red_team_path.is_file():
        errors.append(
            f"{state.get('status')} requires {red_team_path.name}; the internal Red Team is part "
            f"of the delivery, not of the audit")
    else:
        report = load_json(red_team_path)
        schema_path = root / ".iacode" / "schemas" / "red-team-report.schema.json"
        if schema_path.is_file():
            for error in validate_schema(report, load_json(schema_path)):
                errors.append(f"{red_team_path.name}: {error}")
        if isinstance(report, dict):
            attacks = [item for item in report.get("attacks") or [] if isinstance(item, dict)]
            defended = [item for item in attacks if item.get("result") == "DEFENDED"]
            escaped = [item for item in attacks if item.get("result") == "ESCAPED"]
            if report.get("total") != len(attacks):
                errors.append(f"{red_team_path.name}: total does not match the recorded attacks")
            if report.get("defended") != len(defended):
                errors.append(f"{red_team_path.name}: defended does not match the recorded attacks")
            if report.get("escaped") != len(escaped):
                errors.append(f"{red_team_path.name}: escaped does not match the recorded attacks")
            if escaped and report.get("result") != "RED_TEAM_FAIL":
                errors.append(
                    f"{red_team_path.name}: {len(escaped)} attack(s) escaped but the result is "
                    f"{report.get('result')!r}")
            if report.get("result") != "RED_TEAM_PASS":
                errors.append(
                    f"{state.get('status')} requires the internal Red Team to report "
                    f"RED_TEAM_PASS, found {report.get('result')!r}")
            if report.get("targetFingerprint") != observed:
                errors.append(
                    f"{red_team_path.name} is STALE: the attacked content changed after the run, "
                    f"so the affected attacks must be executed again")
            # A battery without a null-mutation control proves nothing: the CP-0009 audit's first
            # harness reported every attack as defended while the refusals came from leftover
            # state rather than from the mutation under test. The rule arrived with report version
            # 1.1.0, and a report sealed under 1.0.0 keeps the rules it was written for.
            control = report.get("baselineControl")
            requires_control = str(report.get("schemaVersion")) != "1.0.0"
            if requires_control and (
                    not isinstance(control, dict) or control.get("result") != "VALID"):
                errors.append(
                    f"{red_team_path.name}: the battery must record a null-mutation control that "
                    f"the unmutated fixture passes; found "
                    f"{(control or {}).get('result') if isinstance(control, dict) else control!r}")
            recorded_ids = {str(item.get("attackId")) for item in attacks}
            for audit in _safe_open_audits(root, state, target, errors):
                from policies import audit_attacks

                for attack in audit_attacks(root, audit):
                    if attack["mandatory"] == "true" and attack["id"] not in recorded_ids:
                        errors.append(
                            f"{red_team_path.name}: mandatory attack {attack['id']} of "
                            f"{audit.get('auditId')} was not executed")

    mirror_path = target / f"{identifier}-INTERNAL-MIRROR.json"
    if not mirror_path.is_file():
        errors.append(f"{state.get('status')} requires {mirror_path.name}")
        return
    mirror = load_json(mirror_path)
    schema_path = root / ".iacode" / "schemas" / "mirror-audit.schema.json"
    if schema_path.is_file():
        for error in validate_schema(mirror, load_json(schema_path)):
            errors.append(f"{mirror_path.name}: {error}")
    if isinstance(mirror, dict):
        checks = [item for item in mirror.get("checks") or [] if isinstance(item, dict)]
        failed = [item for item in checks if item.get("result") == "FAIL"]
        passed = [item for item in checks if item.get("result") == "PASS"]
        inapplicable = [item for item in checks if item.get("result") == "NOT_APPLICABLE"]
        if mirror.get("total") != len(checks):
            errors.append(f"{mirror_path.name}: total does not match the recorded checks")
        if mirror.get("failed") != len(failed):
            errors.append(f"{mirror_path.name}: failed does not match the recorded checks")
        if mirror.get("passed") != len(passed):
            errors.append(f"{mirror_path.name}: passed does not match the recorded checks")
        if failed and mirror.get("result") != "FAIL":
            errors.append(f"{mirror_path.name}: a failed check cannot produce a PASS")
        # An inapplicable dimension is neither a pass nor a failure, and it never silently becomes
        # one: it keeps its own status in the artifact and it is counted separately. The finding
        # CP11-F-001 was the opposite collapse -- nothing to audit reported as a failure -- and the
        # rule that repairs it must not open the reverse escape, a dimension declared inapplicable
        # while the canonical sources name items for it.
        if inapplicable or "notApplicable" in mirror:
            if mirror.get("notApplicable") != len(inapplicable):
                errors.append(
                    f"{mirror_path.name}: notApplicable does not match the recorded checks")
        if len(passed) + len(failed) + len(inapplicable) != len(checks):
            errors.append(
                f"{mirror_path.name}: every check is PASS, FAIL or NOT_APPLICABLE, and the three "
                f"counts must add up to the total")
        # The justification arrived with report version 1.1.0. A 1.0.0 report has nowhere to put a
        # reason, so it may not record an inapplicable dimension at all, and the sealed 1.0.0
        # reports keep the rules they were written for.
        if inapplicable and str(mirror.get("schemaVersion")) == "1.0.0":
            errors.append(
                f"{mirror_path.name}: a NOT_APPLICABLE check requires the justification fields of "
                f"report schemaVersion 1.1.0")
        for item in inapplicable:
            identifier = item.get("id")
            if not str(item.get("reason") or "").strip():
                errors.append(
                    f"{mirror_path.name}: check {identifier} is NOT_APPLICABLE without a reason; "
                    f"an unjustified inapplicable check is indistinguishable from a skipped one")
            if not str(item.get("derivationSource") or "").strip():
                errors.append(
                    f"{mirror_path.name}: check {identifier} is NOT_APPLICABLE without naming the "
                    f"canonical source its empty applicable set was derived from")
            if item.get("expectedCount") != 0:
                errors.append(
                    f"{mirror_path.name}: check {identifier} is NOT_APPLICABLE with "
                    f"expectedCount={item.get('expectedCount')!r}; a dimension that has items to "
                    f"audit is not inapplicable")
        # Whether a dimension is applicable is decided by the canonical sources, not by the report
        # that would rather not run it. The validator re-derives the applicable set from the audit
        # registry and the sealed reports it names, so declaring a dimension inapplicable while
        # those sources name items for it is refused here as well as by the mirror itself.
        if inapplicable:
            _validate_mirror_applicability(root, state, target, mirror_path, inapplicable, errors)
        if mirror.get("result") != "PASS":
            errors.append(
                f"{state.get('status')} requires the internal mirror audit to pass, found "
                f"{mirror.get('result')!r}")
        if mirror.get("targetFingerprint") != observed:
            errors.append(
                f"{mirror_path.name} is STALE: the audited content changed after the mirror ran")
        independence = str(mirror.get("independence") or "")
        if "internal" not in independence.lower():
            errors.append(
                f"{mirror_path.name}: independence must state plainly that this is an internal "
                f"quality role and not independent external validation")


#: The mirror dimensions whose applicable set the audit registry decides, and the key of the
#: derivation each one is bound to. A dimension outside this map may be inapplicable for reasons the
#: validator cannot re-derive; these two may not, because their source is canonical.
REGISTRY_BOUND_MIRROR_CHECKS = {
    "MIR-002": ("findings", "audit finding"),
    "MIR-003": ("mandatoryAttacks", "mandatory attack"),
}


def _validate_mirror_applicability(
    root: Path,
    state: dict[str, Any],
    target: Path,
    mirror_path: Path,
    inapplicable: list[dict[str, Any]],
    errors: list[str],
) -> None:
    """Refuse an inapplicable dimension the canonical sources say is applicable.

    Repairing ``CP11-F-001`` made ``NOT_APPLICABLE`` reachable, which opens the mirror-image escape:
    a delivery that declares a dimension inapplicable rather than satisfying it. The applicable set
    is re-derived here from the audit registry and the sealed reports it names -- the same sources
    the mirror uses and none of them inside the delivery -- so the claim is checked rather than
    believed.
    """
    from policies import audit_applicability

    try:
        applicable = audit_applicability(root, str(state.get("gate", "")), target.name)
    except LedgerError as exc:
        errors.append(f"audit registry: {exc}")
        return
    for item in inapplicable:
        identifier = str(item.get("id"))
        binding = REGISTRY_BOUND_MIRROR_CHECKS.get(identifier)
        if binding is None:
            continue
        key, label = binding
        count = len(applicable[key])
        if count:
            errors.append(
                f"{mirror_path.name}: check {identifier} is recorded as NOT_APPLICABLE while the "
                f"canonical sources name {count} applicable {label}(s) for this checkpoint "
                f"({applicable['derivationSource']})")


def _safe_open_audits(
    root: Path,
    state: dict[str, Any],
    target: Path,
    errors: list[str],
) -> list[dict[str, Any]]:
    try:
        return open_audits(root, str(state.get("gate", "")), target.name)
    except LedgerError as exc:
        errors.append(f"audit registry: {exc}")
        return []


def _validate_closure_matrix(root: Path, target: Path, errors: list[str]) -> None:
    """The closure view and the schema-bound matrix describe the same requirements.

    They are generated together by ``derive_requirements.py``. Validating that they still agree is
    what stops one of them from being edited into a friendlier shape.
    """
    closure_path = target / "CLOSURE-REQUIREMENTS.json"
    matrix_path = target / "REQUIREMENTS-MATRIX.json"
    if not (closure_path.is_file() and matrix_path.is_file()):
        return
    closure = load_json(closure_path)
    matrix = load_json(matrix_path)
    if isinstance(matrix, dict) and matrix.get("schemaVersion") != "2.0.0":
        errors.append(
            f"schemaVersion {CLOSURE_SCHEMA_VERSION} requires REQUIREMENTS-MATRIX.json "
            f"schemaVersion 2.0.0, which carries the anchored sourceRef the expected-set "
            f"comparison needs; found {matrix.get('schemaVersion')!r}")
    schema_path = root / ".iacode" / "schemas" / "closure-requirements.schema.json"
    if schema_path.is_file():
        for error in validate_schema(closure, load_json(schema_path)):
            errors.append(f"CLOSURE-REQUIREMENTS.json: {error}")
    if not (isinstance(closure, dict) and isinstance(matrix, dict)):
        return

    closure_rows = {
        str(row.get("id")): row for row in closure.get("requirements") or []
        if isinstance(row, dict)
    }
    matrix_rows = {
        str(row.get("id")): row for row in matrix.get("requirements") or []
        if isinstance(row, dict)
    }
    for identifier in sorted(set(closure_rows) - set(matrix_rows)):
        errors.append(f"CLOSURE-REQUIREMENTS.json declares {identifier}, which the matrix omits")
    for identifier in sorted(set(matrix_rows) - set(closure_rows)):
        errors.append(f"REQUIREMENTS-MATRIX.json declares {identifier}, which the closure view omits")
    for identifier in sorted(set(closure_rows) & set(matrix_rows)):
        closure_row, matrix_row = closure_rows[identifier], matrix_rows[identifier]
        if closure_row.get("sourceRef") != matrix_row.get("sourceRef"):
            errors.append(f"{identifier}: the two requirement views disagree on the anchored source")
        if closure_row.get("finalStatus") != matrix_row.get("status"):
            errors.append(
                f"{identifier}: the closure view records {closure_row.get('finalStatus')!r} while "
                f"the matrix records {matrix_row.get('status')!r}")


def _validate_findings_closure(
    root: Path,
    target: Path,
    state: dict[str, Any],
    errors: list[str],
) -> None:
    """Every finding of an open audit must be closed by the corrective checkpoint."""
    from policies import audit_findings

    for audit in _safe_open_audits(root, state, target, errors):
        name = audit.get("findingsClosureFile") or "FINDINGS-CLOSURE.json"
        path = target / str(name)
        if not path.is_file():
            errors.append(
                f"the corrective checkpoint for {audit.get('auditId')} requires {name}")
            continue
        document = load_json(path)
        schema_path = root / ".iacode" / "schemas" / "findings-closure.schema.json"
        if schema_path.is_file():
            for error in validate_schema(document, load_json(schema_path)):
                errors.append(f"{name}: {error}")
        if not isinstance(document, dict):
            continue
        rows = [item for item in document.get("findings") or [] if isinstance(item, dict)]
        recorded = {str(item.get("findingId")) for item in rows}
        expected = {item["id"] for item in audit_findings(root, audit)}
        for missing in sorted(expected - recorded):
            errors.append(f"{name}: finding {missing} of {audit.get('auditId')} is not accounted for")
        for extra in sorted(recorded - expected):
            errors.append(f"{name}: {extra} is not a finding of {audit.get('auditId')}")
        closed = [item for item in rows if item.get("status") == "CLOSED"]
        if document.get("total") != len(rows):
            errors.append(f"{name}: total does not match the recorded findings")
        if document.get("closed") != len(closed):
            errors.append(f"{name}: closed does not match the recorded findings")
        open_rows = [item for item in rows if item.get("status") != "CLOSED"]
        if open_rows and document.get("result") != "OPEN":
            errors.append(f"{name}: a finding that is not CLOSED cannot produce result CLOSED")
        if open_rows:
            errors.append(
                f"{state.get('status')} is not available while "
                + ", ".join(sorted(str(item.get("findingId")) for item in open_rows))
                + f" of {audit.get('auditId')} remain open")


def _validate_derived_counts(
    root: Path,
    target: Path,
    state: dict[str, Any],
    errors: list[str],
) -> None:
    """Counts used as evidence are derived once and verified wherever a report states them."""
    from derive_counts import derive_counts

    path = target / "COUNTS.json"
    if not path.is_file():
        errors.append(f"{state.get('status')} requires COUNTS.json; an evidential count is derived")
        return
    stored = load_json(path)
    schema_path = root / ".iacode" / "schemas" / "counts.schema.json"
    if schema_path.is_file():
        for error in validate_schema(stored, load_json(schema_path)):
            errors.append(f"COUNTS.json: {error}")
    if not isinstance(stored, dict):
        return
    try:
        derived = derive_counts(root, target)
    except LedgerError as exc:
        errors.append(f"COUNTS.json cannot be recomputed: {exc}")
        return

    recorded = stored.get("counts") or {}
    for key, value in sorted(derived.items()):
        entry = recorded.get(key)
        if not isinstance(entry, dict):
            errors.append(f"COUNTS.json does not record the derived count {key}")
            continue
        # A count of executions can never exceed what exists to execute. The audit checkpoint
        # recorded one 306-case run in two categories and derived 610 of 306 passing tests, which
        # is additive nonsense rather than a measurement.
        if (isinstance(value["numerator"], int) and isinstance(value["denominator"], int)
                and value["numerator"] > value["denominator"]):
            errors.append(
                f"COUNTS.json {key}={value['numerator']}/{value['denominator']} counts more than "
                f"exists; one physical execution recorded under several categories is one "
                f"measurement, not their sum")
        if (entry.get("numerator"), entry.get("denominator")) != (value["numerator"], value["denominator"]):
            errors.append(
                f"COUNTS.json {key}={entry.get('numerator')}/{entry.get('denominator')} "
                f"contradicts the derived {value['numerator']}/{value['denominator']}")

    for document in sorted(target.glob("*.md")):
        try:
            text = document.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for numerator, denominator, label in COUNT_CLAIM.findall(text):
            value = derived.get(label)
            if value is None:
                continue
            if (int(numerator), int(denominator)) != (value["numerator"], value["denominator"]):
                errors.append(
                    f"{document.name} states {numerator}/{denominator} {label}, which contradicts "
                    f"the derived {value['numerator']}/{value['denominator']}")


def _validate_guardrail_effectiveness(root: Path, state: dict[str, Any], errors: list[str]) -> None:
    """A guardrail that cannot be resolved or is not verified by a test is not effective."""
    declared = state.get("guardrailEffectiveness")
    if not isinstance(declared, dict):
        errors.append("STATE.json schemaVersion 3.2.0 requires the guardrailEffectiveness block")
        return
    measured = guardrail_effectiveness(root)
    for key in ("guardrailsTotal", "guardrailsResolved", "guardrailsTested", "guardrailsEffective",
                "guardrailFailures"):
        if declared.get(key) != measured[key]:
            errors.append(
                f"STATE.json guardrailEffectiveness.{key}={declared.get(key)!r} does not match the "
                f"measured {measured[key]!r}")
    if measured["guardrailFailures"]:
        errors.append(
            f"{state.get('status')} is not available while {measured['guardrailFailures']} "
            f"guardrail failure(s) remain unresolved: "
            + ", ".join(measured["lessonsWithUnresolvedFailures"]))
    if measured["guardrailsEffective"] != measured["guardrailsTotal"]:
        for entry in measured["guardrails"]:
            if not entry["effective"]:
                errors.append(
                    f"guardrail {entry['guardrailId']} is not effective: {entry['detail']}")


def _validate_closure_controls(
    root: Path,
    target: Path,
    state: dict[str, Any],
    metadata: Any,
    commands: list[dict[str, Any]],
    errors: list[str],
    allow_pending_seal: bool = False,
) -> None:
    """The controls introduced by the M0 closure, bound to schemaVersion 3.2.0."""
    _validate_anchor_chain(root, target, state, errors)
    if state.get("status") not in POSITIVE_TERMINAL_STATUSES:
        return
    _validate_closure_matrix(root, target, errors)
    if not allow_pending_seal:
        _validate_seal_chronology(root, target, state, metadata, commands, errors)
    _validate_internal_assurance(root, target, state, errors)
    _validate_findings_closure(root, target, state, errors)
    _validate_derived_counts(root, target, state, errors)
    _validate_guardrail_effectiveness(root, state, errors)


def _validate_second_tool(
    state: dict[str, Any],
    target: Path,
    version: str,
    errors: list[str],
) -> None:
    """R4: represent cross-tool validation as structured state instead of a frozen sentence."""
    status = state.get("status")
    record = state.get("secondToolValidation")
    if version == LEGACY_SCHEMA_VERSION:
        resume = target / "RESUME-VALIDATION.md"
        if status == "GATE_PASS" and resume.is_file():
            if "SECOND_TOOL_VALIDATION = PENDING_MANUAL" not in resume.read_text(encoding="utf-8"):
                errors.append("RESUME-VALIDATION.md lacks the required second-tool status")
        return

    if not isinstance(record, dict):
        errors.append("STATE.json requires a secondToolValidation object")
        return
    outcome = record.get("status")
    if outcome == "PASSED":
        for field in ("tool", "provider", "validatedAt"):
            if not record.get(field):
                errors.append(f"secondToolValidation PASSED requires {field}")
        if record.get("validatedAt") and _parse_datetime(record.get("validatedAt")) is None:
            errors.append("secondToolValidation validatedAt is not an RFC 3339 value")
    if outcome == "NOT_REQUIRED" and not record.get("justification"):
        errors.append("secondToolValidation NOT_REQUIRED requires a justification")
    if status == "GATE_PASS" and outcome not in ("PASSED", "NOT_REQUIRED"):
        errors.append(f"GATE_PASS requires secondToolValidation PASSED or NOT_REQUIRED, found {outcome!r}")


def _validate_quality_evidence(
    target: Path,
    quality: Any,
    normalized: dict[str, dict[str, Any]],
    command_ids: dict[str, int],
    version: str,
    errors: list[str],
) -> None:
    """R6: a PASS must reference evidence that exists and succeeded."""
    if version == LEGACY_SCHEMA_VERSION:
        for dimension in QUALITY_DIMENSIONS:
            if not isinstance(quality, dict) or dimension not in quality:
                errors.append(f"QUALITY.json is missing the required dimension {dimension}")
        return

    if not isinstance(quality, dict) or not isinstance(quality.get("checks"), dict):
        errors.append(f"QUALITY.json schemaVersion {version} requires a checks object")
        return
    for dimension in quality:
        if dimension not in ("schemaVersion", "checks"):
            errors.append(f"QUALITY.json schemaVersion {version} must not use the flat dimension {dimension}")
    required = QUALITY_DIMENSIONS_V3 if version in DELIVERY_SCHEMA_VERSIONS else QUALITY_DIMENSIONS
    for dimension in required:
        entry = normalized.get(dimension)
        if entry is None:
            errors.append(f"QUALITY.json is missing the required dimension {dimension}")
            continue
        status = entry.get("status")
        if status not in QUALITY_OUTCOMES:
            errors.append(f"QUALITY.json {dimension} has an unsupported status {status!r}")
            continue
        evidence = entry.get("evidence") or []
        if status == "PASS" and not evidence:
            errors.append(f"QUALITY.json {dimension}=PASS requires at least one evidence reference")
        if status == "NOT_APPLICABLE" and not entry.get("justification"):
            errors.append(f"QUALITY.json {dimension}=NOT_APPLICABLE requires a justification")
        for reference in evidence:
            if not isinstance(reference, str) or ":" not in reference:
                errors.append(f"QUALITY.json {dimension} has a malformed evidence reference {reference!r}")
                continue
            kind, _, value = reference.partition(":")
            if kind == "command":
                if value not in command_ids:
                    errors.append(f"QUALITY.json {dimension} references an unknown command id {value!r}")
                elif command_ids[value] != 0:
                    errors.append(
                        f"QUALITY.json {dimension} references command {value!r}, which exited {command_ids[value]}"
                    )
            elif kind == "file":
                candidate = (target / value).resolve()
                if target.resolve() not in candidate.parents:
                    errors.append(f"QUALITY.json {dimension} references a file outside the checkpoint: {value}")
                elif not candidate.is_file() or not candidate.read_text(encoding="utf-8").strip():
                    errors.append(f"QUALITY.json {dimension} references a missing or empty file {value!r}")
            else:
                errors.append(f"QUALITY.json {dimension} has an unsupported evidence kind {kind!r}")


def validate_checkpoint(
    root: Path,
    checkpoint: Path | None = None,
    allow_dirty: bool = False,
    allow_pending_ref: bool = False,
    allow_pending_seal: bool = False,
) -> list[str]:
    """Validate a checkpoint. ``allow_pending_seal`` is for the sealing tools only.

    The seal chronology check asks for a recorded post-commit validation of the sealed content.
    The tools that produce that record obviously run before it exists, so they pass this flag. It
    is deliberately not a command-line option: the standalone validator always enforces the rule.
    """
    errors: list[str] = []
    try:
        latest_checkpoint = resolve_latest(root)
    except LedgerError as exc:
        return [str(exc)]

    target = (checkpoint or latest_checkpoint).resolve()
    if target != latest_checkpoint:
        errors.append(f"requested checkpoint is not the LATEST target: {target}")
    if not target.is_dir():
        return errors + [f"checkpoint directory does not exist: {target}"]

    declared_version = LEGACY_SCHEMA_VERSION
    state_path = target / "STATE.json"
    if state_path.is_file():
        try:
            declared_version = _schema_version(load_json(state_path))
        except LedgerError:
            declared_version = LEGACY_SCHEMA_VERSION

    required_files = REQUIRED_CHECKPOINT_FILES
    if declared_version in DELIVERY_SCHEMA_VERSIONS:
        required_files = REQUIRED_CHECKPOINT_FILES + REQUIRED_DELIVERY_FILES
    if declared_version in CLOSURE_SCHEMA_VERSIONS:
        required_files = required_files + REQUIRED_CLOSURE_FILES
    for name in required_files:
        path = target / name
        if not path.is_file():
            errors.append(f"missing required checkpoint file: {name}")
        elif path.stat().st_size == 0:
            errors.append(f"required checkpoint file is empty: {name}")

    schemas_dir = root / ".iacode" / "schemas"
    schemas: dict[str, dict] = {}
    required_schema_names = set(SCHEMA_BINDINGS.values()) | {
        "command.schema.json",
        "decision.schema.json",
        "experience.schema.json",
    }
    for schema_name in required_schema_names:
        schema_path = schemas_dir / schema_name
        try:
            schema = load_json(schema_path)
            if not isinstance(schema, dict) or "$schema" not in schema or "type" not in schema:
                errors.append(f"schema is not a usable JSON Schema document: {schema_name}")
            else:
                schemas[schema_name] = schema
        except LedgerError as exc:
            errors.append(str(exc))

    documents: dict[str, object] = {}
    for filename, schema_name in SCHEMA_BINDINGS.items():
        path = target / filename
        if not path.is_file():
            continue
        try:
            document = load_json(path)
            documents[filename] = document
            if schema_name in schemas:
                for error in validate_schema(document, schemas[schema_name]):
                    errors.append(f"{filename}: {error}")
        except LedgerError as exc:
            errors.append(str(exc))

    state = documents.get("STATE.json")
    version = _schema_version(state)

    commands_path = target / "COMMANDS.jsonl"
    command_count = 0
    command_ids: dict[str, int] = {}
    command_records: list[dict[str, Any]] = []
    if commands_path.is_file():
        for line_number, line in enumerate(commands_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            command_count += 1
            try:
                command = json.loads(line)
                for error in validate_schema(command, schemas.get("command.schema.json", {})):
                    errors.append(f"COMMANDS.jsonl:{line_number}: {error}")
                identifier = command.get("id") if isinstance(command, dict) else None
                if version in (EVIDENCE_SCHEMA_VERSION,) + DELIVERY_SCHEMA_VERSIONS:
                    if not identifier:
                        errors.append(
                            f"COMMANDS.jsonl:{line_number}: schemaVersion {version} requires a command id")
                    elif identifier in command_ids:
                        errors.append(f"COMMANDS.jsonl:{line_number}: duplicate command id {identifier!r}")
                if version in DELIVERY_SCHEMA_VERSIONS and isinstance(command, dict):
                    _validate_command_reproducibility(
                        root, command, line_number, errors,
                        bind_inputs=version in CLOSURE_SCHEMA_VERSIONS)
                if isinstance(command, dict):
                    command_records.append(command)
                if isinstance(identifier, str) and isinstance(command, dict):
                    command_ids[identifier] = command.get("exitCode")
                for value in _all_strings(command):
                    for finding in find_secrets(value):
                        errors.append(f"secret pattern detected in COMMANDS.jsonl:{line_number}: {finding}")
            except json.JSONDecodeError as exc:
                errors.append(f"COMMANDS.jsonl:{line_number}: invalid JSON: {exc}")
        if command_count == 0:
            errors.append("COMMANDS.jsonl contains no command records")

    files_path = target / "FILES.json"
    files: dict[str, Any] | None = None
    if files_path.is_file():
        try:
            files = load_json(files_path)
            for key in ("filesRead", "filesCreated", "filesModified", "filesDeleted"):
                if not isinstance(files, dict) or not isinstance(files.get(key), list):
                    errors.append(f"FILES.json: {key} must be an array")
                else:
                    for index, item in enumerate(files[key]):
                        if not isinstance(item, dict) or not item.get("path") or not item.get("reason"):
                            errors.append(f"FILES.json: {key}[{index}] requires path and reason")
                            continue
                        for field in ("hashBefore", "hashAfter"):
                            expected_hash = item.get(field)
                            if expected_hash is None:
                                continue
                            if not isinstance(expected_hash, str) or HEX64.fullmatch(expected_hash) is None:
                                errors.append(f"FILES.json: {key}[{index}] {field} is not a sha-256 digest")
                                continue
                            if field == "hashBefore":
                                continue
                            candidate = (root / item["path"]).resolve()
                            if root.resolve() not in candidate.parents:
                                errors.append(f"FILES.json: {key}[{index}] path escapes repository")
                            elif not candidate.is_file():
                                errors.append(f"FILES.json: hashed path does not exist: {item['path']}")
                            elif canonical_hash_path(candidate) != expected_hash:
                                errors.append(f"FILES.json: hash mismatch for {item['path']}")
        except LedgerError as exc:
            errors.append(str(exc))

    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts:
            try:
                text = path.read_text(encoding="utf-8")
                findings = set(find_secrets(text))
                if path.suffix.lower() == ".json":
                    try:
                        decoded = json.loads(text)
                        for value in _all_strings(decoded):
                            findings.update(find_secrets(value))
                    except json.JSONDecodeError:
                        pass
                for finding in findings:
                    errors.append(f"secret pattern detected in {path.relative_to(root)}: {finding}")
            except UnicodeDecodeError:
                continue

    metadata = documents.get("RUN-METADATA.json")
    tests = documents.get("TESTS.json")
    quality = documents.get("QUALITY.json")
    normalized_quality = _normalize_quality(quality)

    observed_dirty = False
    if isinstance(state, dict):
        try:
            actual = git_snapshot(root)
            observed_dirty = bool(actual["dirty"])
            _validate_git_binding(root, state, actual, allow_dirty, allow_pending_ref, errors)
        except LedgerError as exc:
            errors.append(str(exc))

        status_text = (target / "STATUS.md").read_text(encoding="utf-8") if (target / "STATUS.md").is_file() else ""
        status_match = re.search(r"\b(" + "|".join(STATUSES) + r")\b", status_text)
        if not status_match:
            errors.append("STATUS.md does not contain a canonical status")
        elif status_match.group(1) != state.get("status"):
            errors.append(f"status mismatch: STATE.json={state.get('status')!r}, STATUS.md={status_match.group(1)!r}")

        started = _parse_datetime(state.get("startedAt"))
        updated = _parse_datetime(state.get("updatedAt"))
        if started is None or updated is None or updated < started:
            errors.append("STATE.json timestamps are not ordered RFC 3339 values")
        if state.get("status") in HANDOFF_READY_STATUSES and state.get("currentCommit") in ("HEAD", "UNBORN"):
            errors.append(f"{state.get('status')} must be anchored to an exact commit or checkpoint tag, not HEAD/UNBORN")

        _validate_status_blockers(state, errors)
        _validate_second_tool(state, target, version, errors)
        _validate_quality_evidence(target, quality, normalized_quality, command_ids, version, errors)

        if version in DELIVERY_SCHEMA_VERSIONS:
            _validate_delivery_assurance(
                root, target, state, normalized_quality, tests, errors,
                closure=version in CLOSURE_SCHEMA_VERSIONS)
        if version in MEMORY_SCHEMA_VERSIONS:
            _validate_memory_policy(
                root, target, state, errors, closure=version in CLOSURE_SCHEMA_VERSIONS)
        if version in CLOSURE_SCHEMA_VERSIONS:
            _validate_closure_controls(
                root, target, state, metadata, command_records, errors, allow_pending_seal)

        if version in HASHED_INVENTORY_VERSIONS and files is not None:
            if state.get("baseCommit") == "UNBORN":
                _validate_empty_project_inventory(root, files, files_path, errors)
            else:
                _validate_delta_inventory(root, target, state, files, observed_dirty, errors)

    if isinstance(metadata, dict) and isinstance(state, dict):
        if metadata.get("branch") != state.get("branch"):
            errors.append("RUN-METADATA.json branch does not match STATE.json")
        if metadata.get("initialCommit") != state.get("baseCommit"):
            errors.append("RUN-METADATA.json initialCommit does not match STATE.json baseCommit")
        if metadata.get("finalCommit") != state.get("currentCommit"):
            errors.append("RUN-METADATA.json finalCommit does not match STATE.json currentCommit")
        started = _parse_datetime(metadata.get("startedAt"))
        finished = _parse_datetime(metadata.get("finishedAt"))
        if started is None or finished is None or finished < started:
            errors.append("RUN-METADATA.json timestamps are not ordered RFC 3339 values")

    if isinstance(tests, dict) and normalized_quality:
        for test_key, quality_key in (("unit", "unitTests"), ("integration", "integrationTests"), ("e2e", "e2e")):
            result = tests.get(test_key)
            verdict = (normalized_quality.get(quality_key) or {}).get("status")
            if isinstance(result, dict):
                if not result.get("executed") and (result.get("passed", 0) or result.get("failed", 0)):
                    errors.append(f"TESTS.json {test_key} has counts but executed is false")
                if verdict == "PASS" and (
                    not result.get("executed")
                    or result.get("failed") != 0
                    or result.get("passed", 0) < 1
                    or not result.get("command")
                    or not result.get("evidence")
                ):
                    errors.append(f"QUALITY.json {quality_key}=PASS contradicts TESTS.json {test_key}")

    handoff = target / "HANDOFF.md"
    next_file = target / "NEXT.md"
    if handoff.is_file():
        handoff_text = handoff.read_text(encoding="utf-8")
        if len(handoff_text.strip()) < 80:
            errors.append("HANDOFF.md is not meaningfully populated")
        for heading in HANDOFF_HEADINGS:
            if heading not in handoff_text:
                errors.append(f"HANDOFF.md is missing heading: {heading}")
    if next_file.is_file():
        next_text = next_file.read_text(encoding="utf-8")
        if len(next_text.strip()) < 40 or "# Next" not in next_text or not any(
            heading in next_text for heading in ("## Required next action", "## Next Gate")
        ):
            errors.append("NEXT.md is not meaningfully populated")

    if isinstance(state, dict) and state.get("status") in HANDOFF_READY_STATUSES:
        final_report = target / "FINAL-REPORT.md"
        required_finals: list[Path] = []
        if version in (EVIDENCE_SCHEMA_VERSION,) + DELIVERY_SCHEMA_VERSIONS or state.get("status") == "GATE_PASS":
            required_finals.append(final_report)
        if version in DELIVERY_SCHEMA_VERSIONS:
            required_finals += [target / name for name in REQUIRED_HANDOFF_FILES if name != "FINAL-REPORT.md"]
        if version == LEGACY_SCHEMA_VERSION and state.get("status") == "GATE_PASS":
            required_finals.append(target / "RESUME-VALIDATION.md")
        for required_final in required_finals:
            if not required_final.is_file() or not required_final.read_text(encoding="utf-8").strip():
                errors.append(f"{state.get('status')} requires {required_final.name}")
        if required_finals and final_report.is_file():
            report_text = final_report.read_text(encoding="utf-8")
            for heading in FINAL_REPORT_HEADINGS:
                if heading not in report_text:
                    errors.append(f"FINAL-REPORT.md is missing heading: {heading}")

    if isinstance(state, dict) and state.get("status") == "GATE_PASS":
        if state.get("dirty") is not False:
            errors.append("GATE_PASS requires dirty=false")
        if normalized_quality:
            for key, entry in normalized_quality.items():
                if entry.get("status") in ("FAIL", "NOT_EXECUTED"):
                    errors.append(f"GATE_PASS cannot have QUALITY.json {key}={entry.get('status')}")
            for key in ("security", "documentation", "checkpointValidation", "redTeam"):
                if (normalized_quality.get(key) or {}).get("status") != "PASS":
                    errors.append(f"GATE_PASS requires QUALITY.json {key}=PASS")
        else:
            errors.append("GATE_PASS requires valid QUALITY.json")

        final_report = target / "FINAL-REPORT.md"
        if final_report.is_file():
            report_text = final_report.read_text(encoding="utf-8")
            if "GATE_PASS" not in report_text or "RED_TEAM_PASS" not in report_text:
                errors.append("FINAL-REPORT.md lacks GATE_PASS or RED_TEAM_PASS evidence")

        if version == LEGACY_SCHEMA_VERSION and state.get("baseCommit") == "UNBORN" and isinstance(files, dict):
            _validate_empty_project_inventory(root, files, files_path, errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="repository root; defaults to auto-detection")
    parser.add_argument("--checkpoint", type=Path, help="checkpoint directory; must equal LATEST")
    args = parser.parse_args()

    try:
        root = find_root(args.root) if args.root else find_root()
        checkpoint = args.checkpoint
        if checkpoint and not checkpoint.is_absolute():
            checkpoint = root / checkpoint
        errors = validate_checkpoint(root, checkpoint)
    except LedgerError as exc:
        errors = [str(exc)]

    if errors:
        print("CHECKPOINT_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CHECKPOINT_VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
