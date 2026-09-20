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

from delivery_assurance import collect_test_ids, evaluate_matrix, load_command_results
from ledger_common import (
    COMMAND_RESULTS,
    CURRENT_SCHEMA_VERSION,
    EVIDENCE_SCHEMA_VERSION,
    INDEPENDENT_DIMENSIONS,
    INVENTORY_SELF_REFERENTIAL_FILES,
    LEGACY_SCHEMA_VERSION,
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
    resolve_latest,
    run_git,
    validate_schema,
)

# Schema versions whose FILES.json is a hash-bound description of the real change set.
HASHED_INVENTORY_VERSIONS = (EVIDENCE_SCHEMA_VERSION, CURRENT_SCHEMA_VERSION)

# The requirement set exists from the first moment of a delivery-assurance checkpoint.
REQUIRED_DELIVERY_FILES = (
    "REQUIREMENTS-MATRIX.json",
    "REQUIREMENTS-MATRIX.md",
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

HANDOFF_READY_STATUSES = ("READY_FOR_REVIEW", "READY_FOR_RED_TEAM", "GATE_PASS", "GATE_FAIL")

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

    for reference in record.get("inputs") or []:
        if not (root / reference).exists():
            errors.append(f"{prefix}: recorded input does not exist: {reference}")


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


def _validate_delivery_assurance(
    root: Path,
    target: Path,
    state: dict[str, Any],
    normalized_quality: dict[str, dict[str, Any]],
    tests: Any,
    errors: list[str],
) -> None:
    """Enforce the Green Keeper and Delivery Completeness gates and their stored evidence."""
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
                for key in ("total", "complete", "partial", "missing", "notApplicable"):
                    source = {
                        "total": "totalRequirements", "complete": "complete", "partial": "partial",
                        "missing": "missing", "notApplicable": "notApplicable",
                    }[key]
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
                for key in ("totalRequirements", "complete", "partial", "missing", "notApplicable",
                            "coveragePercent", "evidenceCoveragePercent", "result"):
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

    if status != "READY_FOR_REVIEW":
        return

    if isinstance(green, dict) and green.get("status") != "PASS":
        errors.append(f"READY_FOR_REVIEW requires GREEN_KEEPER_GATE=PASS, found {green.get('status')!r}")
    if isinstance(delivery, dict):
        if delivery.get("status") != "PASS":
            errors.append(
                f"READY_FOR_REVIEW requires DELIVERY_COMPLETENESS_GATE=PASS, found {delivery.get('status')!r}")
        if delivery.get("coveragePercent") != 100.0:
            errors.append(
                f"READY_FOR_REVIEW requires total requirement coverage, found "
                f"{delivery.get('coveragePercent')!r}")
    if recomputed is not None:
        if recomputed["partial"]:
            errors.append(f"READY_FOR_REVIEW requires zero PARTIAL requirements, found {recomputed['partial']}")
        if recomputed["missing"]:
            errors.append(f"READY_FOR_REVIEW requires zero MISSING requirements, found {recomputed['missing']}")
        if recomputed["result"] != "PASS":
            for finding in recomputed["findings"]:
                if finding["severity"] == "BLOCKING":
                    errors.append(f"READY_FOR_REVIEW blocked by {finding['requirement']}: {finding['detail']}")
    for dimension in QUALITY_DIMENSIONS_V3:
        if dimension in INDEPENDENT_DIMENSIONS:
            continue
        entry = normalized_quality.get(dimension) or {}
        if entry.get("status") == "NOT_EXECUTED":
            errors.append(f"READY_FOR_REVIEW requires QUALITY.json {dimension} to be executed")
        if entry.get("status") == "FAIL":
            errors.append(f"READY_FOR_REVIEW cannot have QUALITY.json {dimension}=FAIL")
    if isinstance(review, dict) and review.get("status") != "PENDING":
        errors.append(
            f"READY_FOR_REVIEW requires independentReview to be PENDING, found {review.get('status')!r}")
    if isinstance(red_team, dict) and red_team.get("status") != "PENDING":
        errors.append(f"READY_FOR_REVIEW requires redTeam to be PENDING, found {red_team.get('status')!r}")


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
    required = QUALITY_DIMENSIONS_V3 if version == CURRENT_SCHEMA_VERSION else QUALITY_DIMENSIONS
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
) -> list[str]:
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
    if declared_version == CURRENT_SCHEMA_VERSION:
        required_files = REQUIRED_CHECKPOINT_FILES + REQUIRED_DELIVERY_FILES
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
                if version in (EVIDENCE_SCHEMA_VERSION, CURRENT_SCHEMA_VERSION):
                    if not identifier:
                        errors.append(
                            f"COMMANDS.jsonl:{line_number}: schemaVersion {version} requires a command id")
                    elif identifier in command_ids:
                        errors.append(f"COMMANDS.jsonl:{line_number}: duplicate command id {identifier!r}")
                if version == CURRENT_SCHEMA_VERSION and isinstance(command, dict):
                    _validate_command_reproducibility(root, command, line_number, errors)
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

        if version == CURRENT_SCHEMA_VERSION:
            _validate_delivery_assurance(root, target, state, normalized_quality, tests, errors)

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
        if version in (EVIDENCE_SCHEMA_VERSION, CURRENT_SCHEMA_VERSION) or state.get("status") == "GATE_PASS":
            required_finals.append(final_report)
        if version == CURRENT_SCHEMA_VERSION:
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
