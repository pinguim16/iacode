#!/usr/bin/env python3
"""Derive or validate the one resumable program-state pointer.

The checkpoint, Git checkout, authorised remote and master-plan milestone are authoritative. A
contradictory existing state is reported, never silently reconciled. ``--write`` is the explicit
operation that replaces it with freshly derived truth.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from ledger_common import (
    MILESTONES,
    STATUSES,
    LedgerError,
    find_root,
    load_json,
    normalize_gate,
    resolve_latest,
    utc_now,
    use_utf8_stdout,
    validate_schema,
)

LIVE_POLICY = {"schemaVersion": "1.0.0", "output": "var/program-state.json",
               "snapshotSchemaVersion": "1.1.0"}
LEGACY_STATUSES = {"IN_PROGRESS", "READY_FOR_REVIEW", "BLOCKED", "GATE_PASS", "MILESTONE_PASS"}


def live_policy(root: Path) -> bool:
    path = root / ".iacode/policies/program-state.json"
    if not path.is_file():
        return False
    if load_json(path) != LIVE_POLICY:
        raise LedgerError("unsupported program-state policy; output and version are canonical")
    return True


def state_target(root: Path, live: bool) -> Path:
    if not live:
        return root / "docs/program/PROGRAM-STATE.json"
    target = root / LIVE_POLICY["output"]
    if target.is_symlink() or target.resolve().parent != root.resolve() / "var":
        raise LedgerError("live program-state output is redirected outside its runtime directory")
    ignored = subprocess.run(["git", "check-ignore", "--quiet", LIVE_POLICY["output"]],
                             cwd=root, check=False)
    if ignored.returncode != 0:
        raise LedgerError("live program-state output must be ignored and never tracked")
    return target


def current_steps(document: Any, state: dict[str, Any], checkpoint: Path) -> list[dict[str, Any]]:
    if (not isinstance(document, dict) or document.get("gate") != state.get("gate")
            or document.get("checkpoint") != checkpoint.name):
        raise LedgerError("program steps have a contradictory Gate or checkpoint identity")
    steps = document.get("steps")
    if not isinstance(steps, list) or not steps:
        raise LedgerError("current program steps are missing")
    number = str(state["gate"]).removeprefix("GATE-")
    seen: set[str] = set()
    pending = False
    for step in steps:
        if not isinstance(step, dict):
            raise LedgerError("current program step must be an object")
        identifier = str(step.get("stepId") or "")
        status = step.get("status")
        if (not re.fullmatch(rf"G{re.escape(number)}-S[0-9]{{2}}", identifier)
                or identifier in seen or status not in {"COMPLETE", "IN_PROGRESS", "NOT_STARTED", "BLOCKED"}):
            raise LedgerError("current program step identity or status is invalid")
        seen.add(identifier)
        if status == "COMPLETE" and pending:
            raise LedgerError("current program steps complete out of sequence")
        pending = pending or status != "COMPLETE"
        for name in ("requirements", "implementation", "tests"):
            values = step.get(name)
            if not isinstance(values, list) or not values or not all(isinstance(value, str) and value.strip() for value in values):
                raise LedgerError(f"current program step lacks {name}")
        if (not isinstance(step.get("expectedBehavior"), str) or not step["expectedBehavior"].strip()
                or not isinstance(step.get("functionalProof"), str) or not step["functionalProof"].strip()
                or not isinstance(step.get("evidence"), list)
                or (status == "COMPLETE" and not step["evidence"])):
            raise LedgerError("current program step lacks behavior, proof or completion evidence")
    return steps


def validate_snapshot(document: Any, schema: dict[str, Any]) -> None:
    errors = validate_schema(document, schema)
    if errors:
        raise LedgerError("program state is invalid: " + "; ".join(errors))
    allowed = LEGACY_STATUSES if document["schemaVersion"] == "1.0.0" else set(STATUSES)
    if document["status"] not in allowed:
        raise LedgerError("program-state status is unsupported by its snapshot version")


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
    live = live_policy(root)
    if live and checkpoint.resolve() != resolve_latest(root):
        raise LedgerError("live program state must describe the latest checkpoint")
    state = load_json(checkpoint / "STATE.json")
    step_document = load_json(checkpoint / "STEPS.json")
    steps = (current_steps(step_document, state, checkpoint) if live
             else step_document.get("steps") or [])
    active = next((item for item in steps if item.get("status") != "COMPLETE"), None)
    completed = [item for item in steps if item.get("status") == "COMPLETE"]
    branch = git(root, "branch", "--show-current")
    if not branch:
        raise LedgerError("program state cannot be derived from detached HEAD")
    local_commit = git(root, "rev-parse", "HEAD")
    if live:
        blockers = state.get("blockedBy")
        action = state.get("nextAllowedAction")
        if (not isinstance(blockers, list)
                or not all(isinstance(value, str) and value.strip() for value in blockers)
                or not isinstance(action, str) or not action.strip()):
            raise LedgerError("checkpoint blockers or next action have invalid types")
        if "branch" in state and state["branch"] != branch:
            raise LedgerError("checkpoint branch contradicts actual Git")
        if "currentCommit" in state:
            reference = state["currentCommit"]
            if (not isinstance(reference, str)
                    or not re.fullmatch(r"HEAD|[0-9a-f]{40}|refs/tags/iacode-checkpoints/[A-Z0-9-]+", reference)):
                raise LedgerError("checkpoint currentCommit is not a canonical commit reference")
            if git(root, "rev-parse", "--verify", "--end-of-options", f"{reference}^{{commit}}") != local_commit:
                raise LedgerError("checkpoint currentCommit contradicts actual Git")
    return {
        "schemaVersion": "1.1.0" if live else "1.0.0",
        "milestone": milestone_for(str(state["gate"])),
        "gate": str(state["gate"]),
        "checkpoint": checkpoint.name,
        "step": active.get("stepId") if active else None,
        "lastCompletedStep": completed[-1].get("stepId") if completed else None,
        "localCommit": local_commit,
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
    validate_snapshot(derived, schema)

    live = live_policy(root)
    target = state_target(root, live)
    if arguments.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(derived, indent=2, ensure_ascii=False) + "\n"
        if live:
            # Replace the observation, never truncate another inode through a pre-existing link.
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=target.parent, delete=False) as output:
                temporary = Path(output.name)
                output.write(content)
            try:
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
        else:
            target.write_text(content, encoding="utf-8", newline="\n")
        print(f"PROGRAM_STATE=PASS written={target.relative_to(root)}")
        return 0
    if not target.is_file():
        raise LedgerError(f"missing {target.relative_to(root)}")
    recorded = load_json(target)
    validate_snapshot(recorded, schema)
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
