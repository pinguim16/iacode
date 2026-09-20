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
    INVENTORY_SELF_REFERENTIAL_FILES,
    STATUSES,
    LedgerError,
    blob_hash,
    canonical_hash_path,
    find_root,
    git_snapshot,
    load_json,
    redact_text,
    resolve_latest,
    utc_now,
    write_json,
)
from validate_checkpoint import _resolve_expected_commit, validate_checkpoint

FINALIZED_FILES = ("STATE.json", "RUN-METADATA.json", "STATUS.md", "HANDOFF.md")


def _next_command_id(commands_path: Path) -> str:
    highest = 0
    count = 0
    if commands_path.is_file():
        for line in commands_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            count += 1
            try:
                identifier = json.loads(line).get("id")
            except json.JSONDecodeError:
                continue
            match = re.fullmatch(r"cmd-(\d+)", identifier or "")
            if match:
                highest = max(highest, int(match.group(1)))
    return f"cmd-{max(highest, count) + 1:04d}"


def _record_attempt(
    checkpoint: Path,
    root: Path,
    command: str,
    exit_code: int,
    duration_ms: int,
    notes: str | None,
) -> None:
    commands_path = checkpoint / "COMMANDS.jsonl"
    record: dict[str, Any] = {
        "id": _next_command_id(commands_path),
        "timestamp": utc_now(),
        "command": command,
        "workingDirectory": str(root),
        "exitCode": exit_code,
        "durationMs": duration_ms,
        "stdoutArtifact": "STATE.json" if exit_code == 0 else None,
        "stderrArtifact": None,
        "notes": redact_text(notes) if notes else None,
    }
    with commands_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


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

    if version != CURRENT_SCHEMA_VERSION:
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
    if checkpoint != latest:
        print("CHECKPOINT_NOT_FINALIZED")
        print("- finalization is restricted to the checkpoint named by LATEST.md")
        return 2

    snapshot = git_snapshot(root)
    if snapshot["detached"]:
        print("CHECKPOINT_NOT_FINALIZED")
        print("- finalization requires an attached branch; detached HEAD is read-only for validation")
        return 2

    invocation = "finalize_checkpoint.py" + (f" --status {args.status}" if args.status else "")
    invocation += f" --commit-ref {args.commit_ref}" if args.commit_ref else ""
    started = time.monotonic()
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
        _record_attempt(checkpoint, root, invocation, 1, int((time.monotonic() - started) * 1000), summary)
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
    commit_ref = args.commit_ref or ("HEAD" if snapshot["head"] != "UNBORN" else "UNBORN")
    if commit_ref.startswith("refs/") and not commit_ref.startswith("refs/tags/iacode-checkpoints/"):
        print("CHECKPOINT_NOT_FINALIZED")
        print("- checkpoint commit refs must use refs/tags/iacode-checkpoints/")
        return 2
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

    errors = validate_checkpoint(root, checkpoint, allow_dirty=True, allow_pending_ref=True)
    if errors:
        return fail(errors)

    # Record the successful attempt before sealing the hashes, so the ledger entry that
    # produced the final state is itself covered by the inventory it seals.
    _record_attempt(checkpoint, root, invocation, 0, int((time.monotonic() - started) * 1000), None)
    write_json(files_path, _refresh_inventory_hashes(root, checkpoint, state, load_json(files_path)))

    errors = validate_checkpoint(root, checkpoint, allow_dirty=True, allow_pending_ref=True)
    if errors:
        return fail(errors)

    print("CHECKPOINT_FINALIZED_PRE_COMMIT")
    print("Commit the checkpoint, create the declared checkpoint tag when used, then run validate_checkpoint.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
