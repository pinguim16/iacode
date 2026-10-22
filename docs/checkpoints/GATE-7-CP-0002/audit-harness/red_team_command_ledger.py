"""Independent positive-control and mutation attack for new_checkpoint command evidence."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


REMOTE = "https://github.com/pinguim16/iacode.git"
TAG = "refs/tags/iacode-checkpoints/GATE-7-CP-0001"
COMMIT = "823cf164c6931dab7f957c92721ded7a916655bd"
MARKER = "M2-RED-TEAM-PHASE-7f7db23f"


def _run(argv: list[str], cwd: Path, env: dict[str, str]) -> dict[str, Any]:
    started = time.monotonic()
    result = subprocess.run(
        argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    return {
        "arguments": argv,
        "workingDirectory": str(cwd),
        "durationMs": int((time.monotonic() - started) * 1000),
        "exitCode": result.returncode,
        "stdout": result.stdout.decode("utf-8", errors="replace")[-32768:],
        "stderr": result.stderr.decode("utf-8", errors="replace")[-32768:],
    }


def _load_validator(repository: Path) -> Any:
    module_root = repository / "scripts" / "development-ledger"
    sys.path.insert(0, str(module_root))
    path = module_root / "validate_checkpoint.py"
    spec = importlib.util.spec_from_file_location("m2_red_team_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _case(owner_root: Path, name: str, phase: str | None, env: dict[str, str]) -> dict[str, Any]:
    repository = owner_root / name / "repository"
    repository.parent.mkdir(parents=True)
    steps = []
    steps.append(_run([
        "git", "-c", "core.longpaths=true", "-c", "http.sslBackend=openssl",
        "-c", "credential.helper=", "clone", "--quiet", "--no-local", REMOTE,
        str(repository),
    ], owner_root, env))
    if steps[-1]["exitCode"] == 0:
        steps.append(_run(["git", "checkout", "--quiet", "--detach", TAG], repository, env))
    if any(step["exitCode"] != 0 for step in steps):
        return {"name": name, "steps": steps, "result": "HARNESS_FAIL"}
    head = _run(["git", "rev-parse", "HEAD"], repository, env)
    steps.append(head)
    invocation = [
        sys.executable,
        "scripts/development-ledger/new_checkpoint.py",
        "--gate", "GATE-7",
        "--status", "IN_PROGRESS",
    ]
    if phase is not None:
        invocation.extend(["--phase", phase])
    creation = _run(invocation, repository, env)
    steps.append(creation)
    checkpoint = repository / "docs" / "checkpoints" / "GATE-7-CP-0002"
    state = json.loads((checkpoint / "STATE.json").read_text(encoding="utf-8"))
    command = json.loads((checkpoint / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()[0])
    validator = _load_validator(repository)
    validation_errors: list[str] = []
    validator._validate_command_reproducibility(repository, command, 1, validation_errors)
    recorded_arguments = command.get("arguments")
    invoked_arguments = invocation[1:]
    exact_arguments = recorded_arguments == invoked_arguments
    phase_recognized = state.get("phase") == (phase if phase is not None else "GATE-7")
    return {
        "name": name,
        "repository": str(repository),
        "head": head["stdout"].strip(),
        "steps": steps,
        "phaseSupplied": phase,
        "statePhase": state.get("phase"),
        "phaseRecognizedByProducer": phase_recognized,
        "invokedArguments": invoked_arguments,
        "recordedCommand": command.get("command"),
        "recordedArguments": recorded_arguments,
        "recordedArgumentsExact": exact_arguments,
        "canonicalReproducibilityValidatorErrors": validation_errors,
        "canonicalReproducibilityValidatorAccepted": not validation_errors,
        "result": "OBSERVED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    owner_root = args.owner_root.resolve()
    if owner_root.exists():
        raise RuntimeError(f"exclusive owner root already exists: {owner_root}")
    owner_root.mkdir(parents=True)
    env = os.environ.copy()
    env.update({
        "GIT_TERMINAL_PROMPT": "0",
        "GCM_INTERACTIVE": "Never",
        "GIT_CONFIG_COUNT": "3",
        "GIT_CONFIG_KEY_0": "core.longpaths",
        "GIT_CONFIG_VALUE_0": "true",
        "GIT_CONFIG_KEY_1": "http.sslBackend",
        "GIT_CONFIG_VALUE_1": "openssl",
        "GIT_CONFIG_KEY_2": "credential.helper",
        "GIT_CONFIG_VALUE_2": "",
    })

    baseline = _case(owner_root, "baseline", None, env)
    attack = _case(owner_root, "phase-mutation", MARKER, env)
    baseline_valid = (
        baseline.get("head") == COMMIT
        and baseline.get("phaseRecognizedByProducer") is True
        and baseline.get("recordedArgumentsExact") is True
        and baseline.get("canonicalReproducibilityValidatorAccepted") is True
    )
    premise_valid = (
        attack.get("head") == COMMIT
        and attack.get("phaseRecognizedByProducer") is True
        and MARKER in attack.get("invokedArguments", [])
    )
    escaped = (
        premise_valid
        and attack.get("recordedArgumentsExact") is False
        and MARKER not in attack.get("recordedArguments", [])
        and attack.get("canonicalReproducibilityValidatorAccepted") is True
    )
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "M2_INDEPENDENT_RED_TEAM_COMMAND_LEDGER",
        "subjectCommit": COMMIT,
        "ownerRoot": str(owner_root),
        "retained": True,
        "baselineControl": {
            "status": "VALID" if baseline_valid else "INVALID",
            "case": baseline,
        },
        "attacks": [{
            "id": "M2-RT-01",
            "target": "new_checkpoint.py literal invocation evidence",
            "mutation": "Supply a consumed optional --phase marker.",
            "premise": "STATE.phase must equal the unique marker, proving the option was consumed.",
            "expected": "cmd-0001.command and arguments contain the supplied option and marker; replay preserves phase.",
            "observed": "The state carries the marker, the record omits it, and the canonical reproducibility validator reports no error.",
            "premiseValid": premise_valid,
            "case": attack,
            "result": "ESCAPED" if escaped else "DEFENDED",
        }],
        "attacksExecuted": 1,
        "attacksDefended": 0 if escaped else 1,
        "escapes": 1 if escaped else 0,
        "result": "RED_TEAM_FAIL" if escaped or not baseline_valid else "RED_TEAM_PASS",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"M2_LEDGER_RED_TEAM={report['result']} baseline={report['baselineControl']['status']} "
        f"premise_valid={premise_valid} escapes={report['escapes']}"
    )
    return 1 if report["result"] != "RED_TEAM_PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
