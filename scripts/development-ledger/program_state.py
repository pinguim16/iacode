#!/usr/bin/env python3
"""Derive or validate the one resumable program-state pointer.

The checkpoint, Git checkout, authorised remote and master-plan milestone are authoritative. A
contradictory existing state is reported, never silently reconciled. ``--write`` is the explicit
operation that replaces it with freshly derived truth.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from ledger_common import (
    MILESTONES,
    LedgerError,
    find_root,
    load_json,
    normalize_gate,
    resolve_latest,
    utc_now,
    use_utf8_stdout,
    validate_schema,
)


def git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise LedgerError(f"git {' '.join(arguments)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def milestone_for(gate: str) -> str:
    normalized = normalize_gate(gate)
    for identifier, _title, gates in MILESTONES:
        if normalized in {normalize_gate(item) for item in gates}:
            return identifier
    raise LedgerError(f"master plan assigns no milestone to {gate}")


def remote_commit(root: Path, branch: str) -> str:
    output = git(root, "ls-remote", "--heads", "origin", f"refs/heads/{branch}")
    lines = [line for line in output.splitlines() if line.strip()]
    if len(lines) != 1:
        raise LedgerError(f"origin/{branch} does not resolve to exactly one remote head")
    commit = lines[0].split()[0]
    if len(commit) != 40:
        raise LedgerError(f"origin/{branch} returned an invalid commit")
    return commit


def derive(root: Path, checkpoint: Path) -> dict[str, Any]:
    state = load_json(checkpoint / "STATE.json")
    steps = load_json(checkpoint / "STEPS.json").get("steps") or []
    active = next((item for item in steps if item.get("status") != "COMPLETE"), None)
    completed = [item for item in steps if item.get("status") == "COMPLETE"]
    branch = git(root, "branch", "--show-current")
    if not branch:
        raise LedgerError("program state cannot be derived from detached HEAD")
    return {
        "schemaVersion": "1.0.0",
        "milestone": milestone_for(str(state["gate"])),
        "gate": str(state["gate"]),
        "checkpoint": checkpoint.name,
        "step": active.get("stepId") if active else None,
        "lastCompletedStep": completed[-1].get("stepId") if completed else None,
        "localCommit": git(root, "rev-parse", "HEAD"),
        "remoteCommit": remote_commit(root, branch),
        "branch": branch,
        "status": str(state["status"]),
        "blockers": list(state.get("blockedBy") or []),
        "nextAction": str(state["nextAllowedAction"]),
        "updatedAt": utc_now(),
    }


def comparable(document: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key != "updatedAt"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()

    root = find_root(arguments.root) if arguments.root else find_root()
    checkpoint = arguments.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint
    derived = derive(root, checkpoint)
    schema = load_json(root / ".iacode" / "schemas" / "program-state.schema.json")
    errors = validate_schema(derived, schema)
    if errors:
        raise LedgerError("derived program state is invalid: " + "; ".join(errors))

    target = root / "docs" / "program" / "PROGRAM-STATE.json"
    if arguments.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(derived, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"PROGRAM_STATE=PASS written={target.relative_to(root)}")
        return 0
    if not target.is_file():
        raise LedgerError(f"missing {target.relative_to(root)}")
    recorded = load_json(target)
    errors = validate_schema(recorded, schema)
    if errors:
        raise LedgerError("recorded program state is invalid: " + "; ".join(errors))
    if comparable(recorded) != comparable(derived):
        differences = sorted(
            key
            for key in set(recorded) | set(derived)
            if key != "updatedAt" and recorded.get(key) != derived.get(key)
        )
        raise LedgerError(
            "recorded program state is stale or contradictory: " + ", ".join(differences)
        )
    print(
        f"PROGRAM_STATE=PASS gate={recorded['gate']} checkpoint={recorded['checkpoint']} "
        f"step={recorded['step']} status={recorded['status']}"
    )
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    try:
        sys.exit(main())
    except LedgerError as error:
        print(f"PROGRAM_STATE=FAIL {error}")
        sys.exit(1)
