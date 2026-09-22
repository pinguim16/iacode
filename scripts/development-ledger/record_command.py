#!/usr/bin/env python3
"""Run a command and append an auditable, reproducible record to the checkpoint ledger.

A future tool must be able to read a record and know exactly what ran, where, against which commit,
for what purpose, and with what result. The recorded command string is the literal, portable
invocation: the interpreter token stays ``python`` while execution uses this interpreter, and any
repository-relative file the command touches is listed under ``inputs``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from ledger_common import (
    LedgerError,
    append_command_record,
    build_command_record,
    command_replay_errors,
    find_root,
    git_snapshot,
    resolve_latest,
    runtime_label,
    use_utf8_stdout,
)

INTERPRETER_TOKENS = ("python", "python3")


def _detect_inputs(root: Path, arguments: list[str]) -> list[str]:
    """Repository-relative files the invocation depends on, so the record replays deterministically."""
    inputs: list[str] = []
    for token in arguments:
        if not token or token.startswith("-"):
            continue
        candidate = (root / token).resolve()
        try:
            relative = candidate.relative_to(root.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            value = str(relative).replace("\\", "/")
            # A path Git ignores is a generated artifact, not an input the repository carries.
            # Declaring one makes the record unreplayable from a checkout, which is how six of
            # GATE-0-CP-0001's records named a file no clone has (G1-F-007).
            if _git_ignores(root, value):
                continue
            if value not in inputs:
                inputs.append(value)
    return inputs


def _git_ignores(root: Path, reference: str) -> bool:
    """Whether Git deliberately does not carry ``reference``."""
    completed = subprocess.run(
        ["git", "check-ignore", "--quiet", "--no-index", reference],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return completed.returncode == 0


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path, help="checkpoint directory; defaults to LATEST")
    parser.add_argument("--purpose", required=True, help="why this command is evidence")
    parser.add_argument("--input", action="append", default=[], help="extra input reference to record")
    parser.add_argument("--stdout-artifact", default=None)
    parser.add_argument("--stderr-artifact", default=None)
    parser.add_argument("--operation", default=None)
    parser.add_argument("--phase", default=None)
    parser.add_argument("--subject-commit", default=None,
                        help="the commit this record is evidence about, when it is not HEAD")
    parser.add_argument("--quiet", action="store_true", help="do not echo the captured output")
    parser.add_argument("argv", nargs=argparse.REMAINDER, help="-- followed by the command to run")
    args = parser.parse_args()

    argv = list(args.argv)
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        parser.error("a command is required after --")

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    # The replay rule is asked before anything runs. A command the validator would refuse is
    # refused here instead, and the refusal is recorded: an operation that was attempted and
    # declined stays visible, without an exit code, because no process was launched. `LSN-0003`.
    command = " ".join(argv)
    replay_errors = command_replay_errors(root, command)
    if replay_errors:
        snapshot = git_snapshot(root)
        record = build_command_record(
            root,
            command=command,
            arguments=argv[1:],
            purpose=args.purpose,
            working_directory=str(root),
            runtime=runtime_label(argv[0]) if argv[0] not in INTERPRETER_TOKENS
            else runtime_label("python"),
            inputs=[],
            result="PRECONDITION_REJECTED",
            result_code="E_UNREPLAYABLE_COMMAND",
            exit_code=None,
            duration_ms=0,
            operation=args.operation,
            phase=args.phase,
            preconditions=[{"name": "command-is-replayable", "expected": "no replay error",
                            "observed": message, "satisfied": False}
                           for message in replay_errors],
            failure_reason="; ".join(replay_errors),
            subject_commit=args.subject_commit or snapshot["head"],
            repository_state={
                "branch": snapshot["branch"],
                "head": snapshot["head"],
                "dirty": snapshot["dirty"],
                "detached": snapshot["detached"],
            },
        )
        identifier = append_command_record(checkpoint / "COMMANDS.jsonl", record)
        print(f"[ledger {identifier}] PRECONDITION_REJECTED E_UNREPLAYABLE_COMMAND: "
              + "; ".join(replay_errors))
        return 2

    executable = list(argv)
    if executable[0] in INTERPRETER_TOKENS:
        executable[0] = sys.executable
        runtime = runtime_label("python")
    else:
        runtime = runtime_label(executable[0])

    inputs = _detect_inputs(root, argv) + [item for item in args.input if item]
    started = time.monotonic()
    completed = subprocess.run(
        executable, cwd=root, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    duration = int((time.monotonic() - started) * 1000)

    snapshot = git_snapshot(root)
    record = build_command_record(
        root,
        command=command,
        arguments=argv[1:],
        purpose=args.purpose,
        working_directory=str(root),
        runtime=runtime,
        inputs=inputs,
        result="COMPLETED",
        result_code="OK",
        exit_code=completed.returncode,
        duration_ms=duration,
        stdout_artifact=args.stdout_artifact,
        stderr_artifact=args.stderr_artifact,
        operation=args.operation,
        phase=args.phase,
        subject_commit=args.subject_commit or snapshot["head"],
        repository_state={
            "branch": snapshot["branch"],
            "head": snapshot["head"],
            "dirty": snapshot["dirty"],
            "detached": snapshot["detached"],
        },
    )
    identifier = append_command_record(checkpoint / "COMMANDS.jsonl", record)

    if not args.quiet:
        sys.stdout.write(completed.stdout)
    print(f"[ledger {identifier}] exit={completed.returncode} duration_ms={duration}")
    return completed.returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
