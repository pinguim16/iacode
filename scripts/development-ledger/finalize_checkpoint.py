#!/usr/bin/env python3
"""Finalize checkpoint metadata for a clean post-commit handoff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ledger_common import STATUSES, find_root, git_snapshot, load_json, resolve_latest, utc_now, write_json
from validate_checkpoint import validate_checkpoint


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--status", choices=STATUSES)
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint
    if checkpoint is None:
        checkpoint = resolve_latest(root)
    elif not checkpoint.is_absolute():
        checkpoint = root / checkpoint
    checkpoint = checkpoint.resolve()
    snapshot = git_snapshot(root)
    now = utc_now()

    state = load_json(checkpoint / "STATE.json")
    metadata = load_json(checkpoint / "RUN-METADATA.json")
    if args.status:
        state["status"] = args.status
    state["branch"] = snapshot["branch"]
    state["currentCommit"] = "HEAD" if snapshot["head"] != "UNBORN" else "UNBORN"
    state["dirty"] = False
    state["updatedAt"] = now
    metadata["finishedAt"] = now
    metadata["branch"] = snapshot["branch"]
    metadata["finalCommit"] = "HEAD" if snapshot["head"] != "UNBORN" else "UNBORN"
    write_json(checkpoint / "STATE.json", state)
    write_json(checkpoint / "RUN-METADATA.json", metadata)

    errors = validate_checkpoint(root, checkpoint, allow_dirty=True)
    if errors:
        print("CHECKPOINT_NOT_FINALIZED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CHECKPOINT_FINALIZED_PRE_COMMIT")
    print("Commit the checkpoint, then run validate_checkpoint.py without --allow-dirty.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

