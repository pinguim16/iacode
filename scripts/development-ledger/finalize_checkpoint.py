#!/usr/bin/env python3
"""Finalize checkpoint metadata for a clean post-commit handoff.

Finalization is observable: every attempt appends its own sanitized record, with its
exit code, to the checkpoint's COMMANDS.jsonl. A failed attempt stays recorded, and the
successful attempt is recorded before the inventory hashes are sealed, so the final
state of the checkpoint is reproducible from its own ledger.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

from ledger_common import (
    CURRENT_SCHEMA_VERSION,
    DELIVERY_SCHEMA_VERSIONS,
    EVIDENCE_SCHEMA_VERSION,
    INVENTORY_SELF_REFERENTIAL_FILES,
    STATUSES,
    LedgerError,
    append_command_record,
    blob_hash,
    build_command_record,
    canonical_hash_path,
    find_root,
    git_snapshot,
    load_json,
    redact_text,
    resolve_latest,
    runtime_label,
    utc_now,
    write_json,
)
from validate_checkpoint import _resolve_expected_commit, validate_checkpoint

FINALIZED_FILES = ("STATE.json", "RUN-METADATA.json", "STATUS.md", "HANDOFF.md")

# The literal, portable invocation of this tool from the repository root. Recording the bare script
# name made the CP-0003 ledger unexecutable from its own working directory.
INVOCATION_PREFIX = "python scripts/development-ledger/finalize_checkpoint.py"

HASHED_INVENTORY_VERSIONS = (EVIDENCE_SCHEMA_VERSION,) + DELIVERY_SCHEMA_VERSIONS


def _next_attempt_id(checkpoint: Path) -> str:
    """Stable per-checkpoint attempt identifier, independent of the command numbering."""
    attempts = 0
    commands_path = checkpoint / "COMMANDS.jsonl"
    if commands_path.is_file():
        for line in commands_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("operation") == "finalize-checkpoint":
                attempts += 1
    return f"finalize-attempt-{attempts + 1:04d}"


def _repository_state(root: Path) -> dict[str, Any]:
    try:
        snapshot = git_snapshot(root)
    except LedgerError:
        return {"branch": None, "head": None, "dirty": None, "detached": None}
    return {
        "branch": snapshot["branch"],
        "head": snapshot["head"],
        "dirty": snapshot["dirty"],
        "detached": snapshot["detached"],
    }


def _record_attempt(
    checkpoint: Path,
    root: Path,
    command: str,
    arguments: list[str],
    *,
    phase: str,
    result: str,
    result_code: str,
    exit_code: int | None,
    duration_ms: int,
    preconditions: list[dict[str, Any]],
    failure_reason: str | None,
    notes: str | None = None,
) -> str:
    """Append this finalization attempt to the ledger. Every attempt is recorded, including a
    refusal decided before the operation ran, so the ledger explains why nothing happened."""
    record = build_command_record(
        root,
        command=command,
        arguments=arguments,
        purpose="Finalize the checkpoint metadata for a clean post-commit handoff.",
        working_directory=str(root),
        runtime=runtime_label("python"),
        inputs=[
            str((checkpoint / name).relative_to(root)).replace("\\", "/")
            for name in ("STATE.json", "RUN-METADATA.json", "FILES.json")
            if (checkpoint / name).is_file()
        ],
        result=result,
        result_code=result_code,
        exit_code=exit_code,
        duration_ms=duration_ms,
        stdout_artifact="STATE.json" if result == "COMPLETED" and exit_code == 0 else None,
        operation="finalize-checkpoint",
        phase=phase,
        attempt_id=_next_attempt_id(checkpoint),
        preconditions=preconditions,
        failure_reason=failure_reason,
        repository_state=_repository_state(root),
        notes=redact_text(notes) if notes else None,
    )
    return append_command_record(checkpoint / "COMMANDS.jsonl", record)


def _refresh_inventory_hashes(root: Path, checkpoint: Path, state: dict[str, Any], files: Any) -> Any:
    """Re-derive declared content hashes from the repository. Never invents a declaration."""
    if not isinstance(files, dict):
        return files
    updated = json.loads(json.dumps(files))
    version = state.get("schemaVersion")
    base = state.get("baseCommit")
    self_referential = {
        str((checkpoint / name).relative_to(root)).replace("\\", "/") for name in INVENTORY_SELF_REFERENTIAL_FILES
    }

    if version not in HASHED_INVENTORY_VERSIONS:
        finalized_paths = {
            str((checkpoint / name).relative_to(root)).replace("\\", "/") for name in FINALIZED_FILES
        }
        for category in ("filesRead", "filesCreated", "filesModified"):
            for item in updated.get(category, []):
                if item.get("path", "").replace("\\", "/") in finalized_paths and "hashAfter" in item:
                    item["hashAfter"] = canonical_hash_path(root / item["path"])
        return updated

    base_commit = _resolve_expected_commit(root, base, "UNBORN", False) if isinstance(base, str) else None
    for category, needs_after, needs_before in (
        ("filesCreated", True, False),
        ("filesModified", True, True),
        ("filesDeleted", False, True),
    ):
        for item in updated.get(category, []):
            path = item.get("path", "").replace("\\", "/")
            if not path or path in self_referential:
                continue
            if needs_after:
                candidate = root / path
                if candidate.is_file():
                    item["hashAfter"] = canonical_hash_path(candidate)
            if needs_before and base_commit and base_commit != "UNBORN":
                observed = blob_hash(root, base_commit, path)
                if observed is not None:
                    item["hashBefore"] = observed
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--status", choices=STATUSES)
    parser.add_argument("--commit-ref", help="exact SHA or refs/tags/iacode-checkpoints/... binding")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    latest = resolve_latest(root)
    checkpoint = args.checkpoint
    if checkpoint is None:
        checkpoint = latest
    elif not checkpoint.is_absolute():
        checkpoint = root / checkpoint
    checkpoint = checkpoint.resolve()

    arguments: list[str] = ["scripts/development-ledger/finalize_checkpoint.py"]
    if args.status:
        arguments += ["--status", args.status]
    if args.commit_ref:
        arguments += ["--commit-ref", args.commit_ref]
    invocation = "python " + " ".join(arguments)
    started = time.monotonic()

    snapshot = _repository_state(root)
    commit_ref = args.commit_ref or ("HEAD" if snapshot.get("head") not in (None, "UNBORN") else "UNBORN")
    canonical_ref = not (commit_ref.startswith("refs/") and not commit_ref.startswith("refs/tags/iacode-checkpoints/"))

    # Preconditions are evaluated before anything is written, and the attempt is recorded even when
    # they refuse the operation, so a refusal never disappears from the ledger.
    preconditions = [
        {
            "name": "checkpoint-is-latest",
            "expected": str(latest),
            "observed": str(checkpoint),
            "satisfied": checkpoint == latest,
        },
        {
            "name": "attached-branch",
            "expected": "an attached branch",
            "observed": "detached HEAD" if snapshot.get("detached") else f"branch {snapshot.get('branch')}",
            "satisfied": not snapshot.get("detached"),
        },
        {
            "name": "canonical-commit-ref",
            "expected": "refs/tags/iacode-checkpoints/... or an exact commit",
            "observed": commit_ref,
            "satisfied": canonical_ref,
        },
    ]
    refusals = {
        "checkpoint-is-latest": (
            "E_NOT_LATEST_CHECKPOINT",
            "finalization is restricted to the checkpoint named by LATEST.md",
        ),
        "attached-branch": (
            "E_DETACHED_HEAD",
            "finalization requires an attached branch; detached HEAD is read-only for validation",
        ),
        "canonical-commit-ref": (
            "E_INVALID_COMMIT_REF",
            "checkpoint commit refs must use refs/tags/iacode-checkpoints/",
        ),
    }
    unsatisfied = [item for item in preconditions if not item["satisfied"]]
    if unsatisfied:
        result_code, message = refusals[unsatisfied[0]["name"]]
        _record_attempt(
            latest,
            root,
            invocation,
            arguments,
            phase="precondition",
            result="PRECONDITION_REJECTED",
            result_code=result_code,
            exit_code=None,
            duration_ms=int((time.monotonic() - started) * 1000),
            preconditions=preconditions,
            failure_reason=message,
        )
        print("CHECKPOINT_NOT_FINALIZED")
        print(f"- {message}")
        return 2

    now = utc_now()

    original_state = load_json(checkpoint / "STATE.json")
    original_metadata = load_json(checkpoint / "RUN-METADATA.json")
    status_path = checkpoint / "STATUS.md"
    handoff_path = checkpoint / "HANDOFF.md"
    files_path = checkpoint / "FILES.json"
    original_status_text = status_path.read_text(encoding="utf-8")
    original_handoff_text = handoff_path.read_text(encoding="utf-8")
    original_files = load_json(files_path)

    def restore() -> None:
        write_json(checkpoint / "STATE.json", original_state)
        write_json(checkpoint / "RUN-METADATA.json", original_metadata)
        status_path.write_text(original_status_text, encoding="utf-8")
        handoff_path.write_text(original_handoff_text, encoding="utf-8")
        write_json(files_path, _refresh_inventory_hashes(root, checkpoint, original_state, original_files))

    def fail(reasons: list[str]) -> int:
        summary = f"{len(reasons)} validation error(s): " + "; ".join(reasons[:5])
        _record_attempt(
            checkpoint,
            root,
            invocation,
            arguments,
            phase="validation",
            result="COMPLETED",
            result_code="E_VALIDATION_FAILED",
            exit_code=1,
            duration_ms=int((time.monotonic() - started) * 1000),
            preconditions=preconditions,
            failure_reason=summary,
        )
        restore()
        print("CHECKPOINT_NOT_FINALIZED")
        for reason in reasons:
            print(f"- {reason}")
        return 1

    state = dict(original_state)
    metadata = dict(original_metadata)
    if args.status:
        state["status"] = args.status
    state["branch"] = snapshot["branch"]
    state["currentCommit"] = commit_ref
    state["dirty"] = False
    state["updatedAt"] = now
    metadata["finishedAt"] = now
    metadata["branch"] = snapshot["branch"]
    metadata["finalCommit"] = commit_ref
    write_json(checkpoint / "STATE.json", state)
    write_json(checkpoint / "RUN-METADATA.json", metadata)
    if args.status:
        status_text = re.sub(r"\b(?:" + "|".join(STATUSES) + r")\b", args.status, original_status_text, count=1)
        handoff_text = re.sub(r"(?m)^Current Status:\s*.*$", f"Current Status: {args.status}", original_handoff_text, count=1)
        status_path.write_text(status_text, encoding="utf-8")
        handoff_path.write_text(handoff_text, encoding="utf-8")
    write_json(files_path, _refresh_inventory_hashes(root, checkpoint, state, original_files))

    errors = validate_checkpoint(
        root, checkpoint, allow_dirty=True, allow_pending_ref=True, allow_pending_seal=True)
    if errors:
        return fail(errors)

    # Record the successful attempt before sealing the hashes, so the ledger entry that
    # produced the final state is itself covered by the inventory it seals.
    _record_attempt(
        checkpoint,
        root,
        invocation,
        arguments,
        phase="seal",
        result="COMPLETED",
        result_code="OK",
        exit_code=0,
        duration_ms=int((time.monotonic() - started) * 1000),
        preconditions=preconditions,
        failure_reason=None,
    )
    # The audit found a run that claimed to finish before the finalizer that sealed it. The end of
    # the run is therefore stamped after the last record the run produced, never before it.
    metadata = load_json(checkpoint / "RUN-METADATA.json")
    metadata["finishedAt"] = utc_now()
    write_json(checkpoint / "RUN-METADATA.json", metadata)
    state = load_json(checkpoint / "STATE.json")
    state["updatedAt"] = metadata["finishedAt"]
    write_json(checkpoint / "STATE.json", state)
    write_json(files_path, _refresh_inventory_hashes(root, checkpoint, state, load_json(files_path)))

    errors = validate_checkpoint(
        root, checkpoint, allow_dirty=True, allow_pending_ref=True, allow_pending_seal=True)
    if errors:
        return fail(errors)

    print("CHECKPOINT_FINALIZED_PRE_COMMIT")
    print("Commit the checkpoint, create the declared checkpoint tag when used, then run validate_checkpoint.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
