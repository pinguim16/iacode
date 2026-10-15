#!/usr/bin/env python3
"""Synchronize derived metadata before validating an unsealed in-progress checkpoint.

This updates bookkeeping only. It never declares paths, marks a requirement complete, changes a
verdict or rewrites a sealed checkpoint. The author must finish all evidence producers and declare
their outputs before validation; hashes are still bound by the canonical refresh function.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ledger_common import (
    LedgerError, find_root, load_json, normalize_gate, resolve_latest, run_git, utc_now, write_json,
)


def synchronize(root: Path, checkpoint: Path) -> None:
    state = load_json(checkpoint / "STATE.json")
    code, _ = run_git(root, "rev-parse", "--verify",
                      f"refs/tags/iacode-checkpoints/{checkpoint.name}^{{commit}}")
    if code == 0 or state.get("status") != "IN_PROGRESS":
        raise LedgerError("metadata synchronization requires an unsealed IN_PROGRESS checkpoint")
    preflight = load_json(checkpoint / "LESSON-PREFLIGHT.json")
    if normalize_gate(str(preflight.get("gate"))) != normalize_gate(str(state.get("gate"))):
        raise LedgerError("the preflight belongs to a different Gate; synchronization refused")
    record = dict(state.get("lessonPreflight") or {})
    record.update({
        "path": "LESSON-PREFLIGHT.json", "gate": preflight["gate"], "scope": preflight["scope"],
        "lessonsConsidered": preflight["lessonsConsidered"],
        "lessonsApplicable": preflight["lessonsApplicable"],
        "derivedRequirements": len(preflight.get("derivedRequirements") or []),
    })
    state["lessonPreflight"] = record
    state["dirty"] = True
    state["updatedAt"] = utc_now()
    metadata = load_json(checkpoint / "RUN-METADATA.json")
    metadata["finalCommit"] = state["currentCommit"]
    metadata["finishedAt"] = state["updatedAt"]
    write_json(checkpoint / "STATE.json", state)
    write_json(checkpoint / "RUN-METADATA.json", metadata)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args()
    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint
    synchronize(root, checkpoint)
    print(f"IN_PROGRESS_METADATA=PASS checkpoint={checkpoint.name}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as error:
        print(f"IN_PROGRESS_METADATA=FAIL {error}")
        sys.exit(1)
