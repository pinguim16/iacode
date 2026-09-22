#!/usr/bin/env python3
"""Run the mandatory delivery gates and record one Green Keeper rework cycle.

This is the evidence harness for the Test Rework / Green Keeper role defined in
``.iacode/agents/test-rework-greenkeeper.md``. The tool executes the gates, records every
invocation in the checkpoint ledger, and appends the cycle to ``REWORK-LOG.jsonl``. It never
edits code, never weakens a check, and never reports green on a red gate: repairing the cause is
the agent's responsibility, and proving the result is this tool's.

``GREEN_KEEPER_GATE`` is ``PASS`` only when every *mandatory* gate executed and is green, no
failure remains, and no rework item is left unresolved. A real external blocker yields
``BLOCKED_EXTERNAL``, which maps to a ``BLOCKED`` checkpoint, never to ``PASS``.

The mandatory set is closed
---------------------------
The M0 audit of ``SETUP-00-CP-0006`` ran ``--gates ""`` and obtained ``GREEN_KEEPER_GATE=PASS``
with no gate executed, no evidence, and a genuinely failing test in the tree. The cause was that
the tool asked its caller which gates were mandatory. It no longer does. The mandatory set comes
from ``.iacode/policies/quality-gates.json``; ``--gates`` may only *add* to a run, and an empty or
partial value changes nothing. Every cycle records the mandatory set it was measured against.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from ledger_common import (
    LedgerError,
    append_command_record,
    build_command_record,
    canonical_hash_path,
    find_root,
    git_snapshot,
    load_json,
    resolve_latest,
    runtime_label,
    scope_fingerprint,
    use_utf8_stdout,
    utc_now,
    validate_schema,
    write_json,
)
from policies import gate_definitions, mandatory_gates


def _refresh_declared_hashes(root: Path, checkpoint: Path) -> None:
    """Re-derive the declared inventory hashes before validating the checkpoint.

    Running a gate appends to the checkpoint's own append-only evidence, so its recorded hashes are
    stale the instant a cycle starts. This re-derives hashes for paths the author already declared;
    it never adds or removes a declaration, so an undeclared change still fails validation.
    """
    from finalize_checkpoint import _refresh_inventory_hashes

    state_path = checkpoint / "STATE.json"
    files_path = checkpoint / "FILES.json"
    if not (state_path.is_file() and files_path.is_file()):
        return
    state = load_json(state_path)
    write_json(files_path, _refresh_inventory_hashes(root, checkpoint, state, load_json(files_path)))


def _run_gate(root: Path, checkpoint: Path, name: str, definition: dict[str, Any]) -> tuple[str, int, str]:
    if name == "checkpointValidation":
        _refresh_declared_hashes(root, checkpoint)
    argv = [str(item) for item in definition["command"]]
    purpose = str(definition["purpose"])
    executable = list(argv)
    if executable[0] == "python":
        executable[0] = sys.executable
    started = time.monotonic()
    completed = subprocess.run(
        executable, cwd=root, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    duration = int((time.monotonic() - started) * 1000)
    snapshot = git_snapshot(root)
    inputs = [item for item in argv[1:] if (root / item).is_file() or (root / item).is_dir()]
    record = build_command_record(
        root,
        command=" ".join(argv),
        arguments=argv[1:],
        purpose=purpose,
        working_directory=str(root),
        runtime=runtime_label("python"),
        inputs=inputs,
        inputs_digest=[
            {"path": item,
             "hash": canonical_hash_path(root / item) if (root / item).is_file() else "ABSENT"}
            for item in inputs
        ],
        result="COMPLETED",
        result_code="OK",
        exit_code=completed.returncode,
        duration_ms=duration,
        operation="green-keeper-gate",
        phase=name,
        repository_state={
            "branch": snapshot["branch"],
            "head": snapshot["head"],
            "dirty": snapshot["dirty"],
            "detached": snapshot["detached"],
        },
    )
    identifier = append_command_record(checkpoint / "COMMANDS.jsonl", record)
    return identifier, completed.returncode, completed.stdout


def _next_cycle(log_path: Path) -> int:
    highest = 0
    if log_path.is_file():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                highest = max(highest, int(json.loads(line).get("cycle", 0)))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
    return highest + 1


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--gates", default="",
                        help="extra gates to run in addition to the canonical mandatory set; "
                             "this argument can never remove a mandatory gate")
    parser.add_argument("--trigger", default="scheduled delivery gate run",
                        help="what caused this cycle")
    parser.add_argument("--root-cause", default=None, help="root cause repaired before this cycle")
    parser.add_argument("--files-changed", default="", help="comma-separated paths repaired")
    parser.add_argument("--external-blocker", default=None,
                        help="a real external blocker that cannot be repaired in the repository")
    parser.add_argument("--note", default=None)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    definitions = gate_definitions(root)
    required = list(mandatory_gates(root))
    if not required:
        print("QUALITY_GATE_POLICY_INVALID")
        print("- the canonical policy declares no mandatory gate; a delivery cannot be measured")
        return 3

    extra = [name.strip() for name in args.gates.split(",") if name.strip()]
    unknown = [name for name in extra if name not in definitions]
    if unknown:
        parser.error("unknown gate(s): " + ", ".join(unknown))

    # The mandatory set always runs first and in policy order. Anything the caller adds runs after.
    names = required + [name for name in extra if name not in required]

    executed: list[str] = []
    failures: list[str] = []
    gate_results: list[dict[str, Any]] = []
    for name in names:
        identifier, code, output = _run_gate(root, checkpoint, name, definitions[name])
        executed.append(identifier)
        gate_results.append({
            "gate": name,
            "commandId": identifier,
            "exitCode": code,
            "mandatory": name in required,
        })
        status = "GREEN" if code == 0 else "RED"
        print(f"[{name}] {status} exit={code} ledger={identifier}")
        if code != 0:
            failures.append(name)
            if not args.quiet:
                sys.stdout.write(output)

    if failures:
        result = "BLOCKED_EXTERNAL" if args.external_blocker else "STILL_RED"
    else:
        result = "GREEN"

    entry: dict[str, Any] = {
        "cycle": _next_cycle(checkpoint / "REWORK-LOG.jsonl"),
        "timestamp": utc_now(),
        "trigger": args.trigger,
        "failedGate": failures[0] if failures else None,
        "failureEvidence": executed if failures else [],
        "rootCauseSummary": args.root_cause,
        "filesChanged": [item.strip() for item in args.files_changed.split(",") if item.strip()],
        "commandsExecuted": executed,
        "requiredGates": required,
        "gateResults": gate_results,
        "scopeFingerprint": scope_fingerprint(root),
        "result": result,
        "remainingFailures": len(failures),
    }
    if args.external_blocker:
        entry["externalBlocker"] = args.external_blocker
    if args.note:
        entry["notes"] = args.note

    schema_path = root / ".iacode" / "schemas" / "rework-log.schema.json"
    if schema_path.is_file():
        errors = validate_schema(entry, load_json(schema_path))
        if errors:
            print("REWORK_LOG_INVALID")
            for error in errors:
                print(f"- {error}")
            return 3

    with (checkpoint / "REWORK-LOG.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    gate = "PASS" if result == "GREEN" else "FAIL"
    print(f"GREEN_KEEPER_GATE={gate} cycle={entry['cycle']} result={result} "
          f"required={','.join(required)} "
          f"remainingFailures={entry['remainingFailures']} evidence={','.join(executed)}")
    if result == "GREEN":
        return 0
    return 2 if result == "BLOCKED_EXTERNAL" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(3)
