#!/usr/bin/env python3
"""Finalize checkpoint metadata for a clean post-commit handoff."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from ledger_common import STATUSES, find_root, git_snapshot, load_json, resolve_latest, utc_now, write_json
from validate_checkpoint import _canonical_hash, validate_checkpoint


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
    now = utc_now()

    original_state = load_json(checkpoint / "STATE.json")
    original_metadata = load_json(checkpoint / "RUN-METADATA.json")
    status_path = checkpoint / "STATUS.md"
    handoff_path = checkpoint / "HANDOFF.md"
    files_path = checkpoint / "FILES.json"
    original_status_text = status_path.read_text(encoding="utf-8")
    original_handoff_text = handoff_path.read_text(encoding="utf-8")
    original_files = load_json(files_path)
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

    finalized_paths = {
        str((checkpoint / "STATE.json").relative_to(root)).replace("\\", "/"),
        str((checkpoint / "RUN-METADATA.json").relative_to(root)).replace("\\", "/"),
        str(status_path.relative_to(root)).replace("\\", "/"),
        str(handoff_path.relative_to(root)).replace("\\", "/"),
    }
    updated_files = json.loads(json.dumps(original_files))
    for category in ("filesRead", "filesCreated", "filesModified"):
        for item in updated_files.get(category, []):
            if item.get("path", "").replace("\\", "/") in finalized_paths and "hashAfter" in item:
                item["hashAfter"] = _canonical_hash(root / item["path"])
    write_json(files_path, updated_files)

    errors = validate_checkpoint(root, checkpoint, allow_dirty=True, allow_pending_ref=True)
    if errors:
        write_json(checkpoint / "STATE.json", original_state)
        write_json(checkpoint / "RUN-METADATA.json", original_metadata)
        status_path.write_text(original_status_text, encoding="utf-8")
        handoff_path.write_text(original_handoff_text, encoding="utf-8")
        write_json(files_path, original_files)
        print("CHECKPOINT_NOT_FINALIZED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CHECKPOINT_FINALIZED_PRE_COMMIT")
    print("Commit the checkpoint, create the declared checkpoint tag when used, then run validate_checkpoint.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
