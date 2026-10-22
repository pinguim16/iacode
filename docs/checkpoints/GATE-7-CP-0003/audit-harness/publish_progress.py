"""Serialize actual process exits around an unsealed Gate7 progress publication.

Invoke directly, never through record_command: the staged scan records itself through that tool
and the canonical finalizer self-records. A durable success record is not a child exit signal.
This neither seals a checkpoint nor changes any requirement, promotion rule or audit verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def require_current_authored_quality():
    """Require the latest unchanged-rule observation for the whole derived helper scope."""
    from audit_runner_bridge import regular
    from authored_python_quality import authored_paths
    from ledger_common import find_secrets, load_json, scope_fingerprint

    candidates = sorted((CHECKPOINT / "quality-attempts/helper-quality").glob("run-*/RECEIPT.json"))
    if not candidates:
        raise ValueError("CURRENT_AUTHORED_QUALITY_MISSING")
    path = candidates[-1]
    regular(path, CHECKPOINT)
    proof = load_json(path)
    paths = authored_paths()
    hashes = {}
    for name in paths:
        regular(ROOT / name, ROOT)
        hashes[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    if (
        proof["mode"] != "check"
        or proof["result"] != "PASS"
        or proof["sourceUnchanged"] is not True
        or proof["sourceFingerprint"] != scope_fingerprint(ROOT)
        or proof["paths"] != paths
        or proof["hashesBefore"] != hashes
        or proof["hashesAfter"] != hashes
        or len(proof["executions"]) != 1
    ):
        raise ValueError("CURRENT_WHOLE_AUTHORED_QUALITY_REQUIRED")
    execution = proof["executions"][0]
    producer = execution["producer"]
    if (
        execution["step"] != "check"
        or producer["status"] != "COMPLETED"
        or type(producer["exitCode"]) is not int
        or producer["exitCode"] != 0
        or producer["arguments"][-(len(paths) + 2) :] != ["ruff", "check", *paths]
        or execution["cleanup"]["result"] != "PASS"
    ):
        raise ValueError("AUTHORED_PRODUCER_OR_CLEANUP_FAILED")
    for name in ("stdout", "stderr"):
        fact = producer[name]
        artifact = path.parent / ("check." + name + ".log")
        regular(artifact, CHECKPOINT)
        if (
            fact["refusal"] is not None
            or type(fact["bytes"]) is not int
            or not 0 <= fact["bytes"] <= 8 * 1024 * 1024
            or artifact.stat().st_size != fact["bytes"]
        ):
            raise ValueError("AUTHORED_STREAM_REFUSED")
        raw = artifact.read_bytes()
        if hashlib.sha256(raw).hexdigest() != fact["sha256"] or find_secrets(
            raw.decode("utf-8", errors="strict")
        ):
            raise ValueError("AUTHORED_ORIGINAL_STREAM_MISMATCH")
    return {"receipt": path.relative_to(CHECKPOINT).as_posix(), "paths": len(paths)}


def require_current_lint():
    """Accept only the latest actual canonical lint bound to current source and pre-push HEAD."""
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from audit_runner_bridge import regular
    from ledger_common import canonical_hash_path, find_secrets, load_json, scope_fingerprint
    from policies import gate_definitions

    candidates = sorted((CHECKPOINT / "quality-attempts/lint").glob("run-*.json"))
    if not candidates:
        raise ValueError("CURRENT_CANONICAL_LINT_MISSING")
    path = candidates[-1]
    regular(path, CHECKPOINT)
    if path.stat().st_size > 65536:
        raise ValueError("LINT_RECEIPT_SIZE")
    value = load_json(path)
    definition = gate_definitions(ROOT)["lint"]["command"]
    expected = [sys.executable, *definition[1:]]
    fingerprint = scope_fingerprint(ROOT)
    if (
        definition[0] != "python"
        or value["arguments"] != expected
        or type(value["exitCode"]) is not int
        or value["exitCode"] != 0
        or value["sourceUnchanged"] is not True
        or value["sourceFingerprint"] != fingerprint
        or set(value["streams"]) != {"stdout", "stderr"}
    ):
        raise ValueError("CURRENT_CANONICAL_LINT_REQUIRED")
    for fact in value["streams"].values():
        if (
            fact["refused"] is not False
            or type(fact["bytes"]) is not int
            or not 0 <= fact["bytes"] <= 8 * 1024 * 1024
            or type(fact["path"]) is not str
        ):
            raise ValueError("LINT_STREAM_OBSERVATION_REFUSED")
        artifact = ROOT / fact["path"]
        regular(artifact, CHECKPOINT)
        if artifact.stat().st_size != fact["bytes"]:
            raise ValueError("LINT_STREAM_SIZE_MISMATCH")
        raw = artifact.read_bytes()
        if hashlib.sha256(raw).hexdigest() != fact["sha256"] or find_secrets(
            raw.decode("utf-8", errors="strict")
        ):
            raise ValueError("LINT_ORIGINAL_STREAM_MISMATCH")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, check=True, text=True
    ).stdout.strip()
    regular(CHECKPOINT / "COMMANDS.jsonl", CHECKPOINT)
    rows = [
        json.loads(line)
        for line in (CHECKPOINT / "COMMANDS.jsonl").read_bytes().splitlines()
        if line
    ]
    wrapper = "docs/checkpoints/GATE-7-CP-0003/audit-harness/run_causal.py"
    relative = path.relative_to(CHECKPOINT).as_posix()
    finished = datetime.fromisoformat(value["finishedAt"].replace("Z", "+00:00"))
    started = datetime.fromisoformat(value["startedAt"].replace("Z", "+00:00"))
    matches = [
        row
        for row in rows
        if row.get("result") == "COMPLETED"
        and type(row.get("exitCode")) is int
        and row.get("exitCode") == 0
        and row.get("subjectCommit") == head
        and row.get("stdoutArtifact") == relative
        and row.get("arguments") == [wrapper, "--gate", "lint"]
        and any(
            item["path"] == wrapper and item["hash"] == canonical_hash_path(ROOT / wrapper)
            for item in row.get("inputsDigest", [])
        )
        and started <= finished <= datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
    ]
    if not matches:
        raise ValueError("CURRENT_PRE_PUBLICATION_LINT_BINDING_REQUIRED")
    return {
        "receipt": relative,
        "commandId": matches[-1]["id"],
        "sourceFingerprint": fingerprint,
        "subjectCommit": head,
    }


class StageFailedError(RuntimeError):
    def __init__(self, stage: str, code: int) -> None:
        super().__init__("serialized publication stage refused")
        self.stage = stage
        self.code = code


def run_sequence(stages: list[tuple[str, list[str]]], cwd: Path) -> list[dict]:
    observations = []
    for name, command in stages:
        # subprocess.run waits for the actual child, not an output/ledger success marker.
        process = subprocess.run(command, cwd=cwd, check=False)
        observations.append({"stage": name, "exitCode": process.returncode})
        if process.returncode != 0:
            raise StageFailedError(name, process.returncode)
    return observations


def stage_declared_paths(root: Path, declared: list[str]) -> None:
    """Use literal NUL stdin, not an unbounded Windows command line or a truncated inventory."""
    changed = set()
    for arguments in (
        ["diff", "--name-only", "-z", "HEAD"],
        ["ls-files", "--others", "--exclude-standard", "-z"],
    ):
        raw = subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True).stdout
        changed.update(part.decode("utf-8", errors="strict") for part in raw.split(b"\0") if part)
    if not changed or changed - set(declared):
        raise ValueError("every actual changed path must be explicitly declared before staging")
    data = b"".join(path.encode("utf-8") + b"\0" for path in sorted(changed))
    subprocess.run(
        ["git", "--literal-pathspecs", "add", "--pathspec-from-file=-", "--pathspec-file-nul"],
        cwd=root,
        input=data,
        check=True,
    )


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from ledger_common import find_secrets, use_utf8_stdout

    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--execute", action="store_true")
    action.add_argument("--stage-declared", action="store_true")
    action.add_argument("--check-current-lint", action="store_true")
    action.add_argument("--check-current-authored-quality", action="store_true")
    parser.add_argument("--message")
    parser.add_argument("--runtime-tag")
    options = parser.parse_args()
    if options.check_current_lint or options.check_current_authored_quality:
        try:
            proof = (
                require_current_lint()
                if options.check_current_lint
                else require_current_authored_quality()
            )
        except Exception as error:
            print(
                json.dumps(
                    {
                        "result": "FAIL",
                        "kind": (
                            "PRE_PUBLICATION_LINT_REFUSAL"
                            if options.check_current_lint
                            else "PRE_PUBLICATION_AUTHORED_QUALITY_REFUSAL"
                        ),
                        "errorType": type(error).__name__,
                        "publicationEffectsStarted": False,
                    }
                )
            )
            return 2
        print(
            json.dumps(
                {
                    "result": "PASS",
                    "kind": (
                        "CURRENT_CANONICAL_LINT_PRECONDITION"
                        if options.check_current_lint
                        else "CURRENT_WHOLE_AUTHORED_QUALITY_PRECONDITION"
                    ),
                    **proof,
                }
            )
        )
        return 0
    state = json.loads((CHECKPOINT / "STATE.json").read_bytes())
    if state["gate"] != "GATE-7" or state["status"] not in {"IN_PROGRESS", "BLOCKED"}:
        raise ValueError(
            "only unsealed implementing Gate7 progress or a truthful blocked handoff may be saved"
        )
    if state["status"] == "BLOCKED" and (not state["blockedBy"] or options.runtime_tag):
        raise ValueError(
            "a blocked handoff requires named blockers and cannot be a runtime subject publication"
        )
    message = options.message or ""
    if not options.stage_declared and (
        not message.strip() or len(message) > 120 or any(ord(char) < 32 for char in message)
    ):
        raise ValueError("one bounded nonempty commit subject is required")
    if find_secrets(message):
        raise ValueError("protected commit subject refused")
    if (
        options.runtime_tag is not None
        and re.fullmatch(
            r"iacode-subjects/GATE-7-CP-0003-runtime-v[1-9][0-9]*", options.runtime_tag
        )
        is None
    ):
        raise ValueError(
            "only a new explicitly named current immutable runtime subject tag is allowed"
        )
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    if not branch or branch != state["branch"]:
        raise ValueError("an attached matching implementing branch is required")
    tag = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/tags/iacode-checkpoints/" + CHECKPOINT.name],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if tag.returncode == 0:
        raise ValueError("never publish progress into a sealed checkpoint")
    inventory = json.loads((CHECKPOINT / "FILES.json").read_bytes())
    paths = [
        row["path"]
        for category in ("filesCreated", "filesModified", "filesDeleted")
        for row in inventory[category]
    ]
    if not paths or any(
        not (ROOT / path).resolve().is_relative_to(ROOT.resolve()) for path in paths
    ):
        raise ValueError("explicitly declared in-repository paths are required")
    if options.stage_declared:
        stage_declared_paths(ROOT, paths)
        return 0
    python = sys.executable
    ledger = "scripts/development-ledger/"
    steps = [
        (
            "current-lint-precondition",
            [
                python,
                ledger + "record_command.py",
                "--purpose",
                "Require-current-canonical-lint-before-any-progress-publication-effect",
                "--",
                "python",
                Path(__file__).resolve().relative_to(ROOT).as_posix(),
                "--check-current-lint",
            ],
        ),
        (
            "current-authored-quality-precondition",
            [
                python,
                ledger + "record_command.py",
                "--purpose",
                "Require-whole-current-authored-source-quality-before-publication",
                "--",
                "python",
                Path(__file__).resolve().relative_to(ROOT).as_posix(),
                "--check-current-authored-quality",
            ],
        ),
        ("stage-declared-inputs", [python, str(Path(__file__)), "--stage-declared"]),
        (
            "staged-scan",
            [
                python,
                ledger + "record_command.py",
                "--purpose",
                "Scan-declared-progress-before-actual-process-owned-publication",
                "--",
                "python",
                ledger + "secret_scan.py",
                "--staged",
            ],
        ),
        (
            "canonical-finalizer",
            [
                python,
                ledger + "finalize_checkpoint.py",
                "--status",
                state["status"],
                "--commit-ref",
                "HEAD",
            ],
        ),
        ("stage-finalized-content", [python, str(Path(__file__)), "--stage-declared"]),
        ("commit", ["git", "commit", "-m", message]),
        ("committed-validation", [python, ledger + "validate_checkpoint.py"]),
    ]
    if options.runtime_tag:
        steps.extend(
            [
                ("immutable-runtime-tag", ["git", "tag", options.runtime_tag]),
                (
                    "atomic-normal-push",
                    [
                        "git",
                        "push",
                        "--atomic",
                        "origin",
                        branch,
                        "refs/tags/" + options.runtime_tag,
                    ],
                ),
            ]
        )
    else:
        steps.append(("normal-push", ["git", "push", "origin", branch]))
    try:
        observations = run_sequence(steps, ROOT)
    except StageFailedError as error:
        print(
            json.dumps(
                {
                    "result": "FAIL",
                    "stage": error.stage,
                    "exitCode": error.code,
                    "historyRewritten": False,
                    "remainingStepsExecuted": False,
                }
            ),
            flush=True,
        )
        return error.code or 1
    print(
        json.dumps(
            {
                "result": "PASS",
                "kind": state["status"] + "_NOT_GATE_ACCEPTANCE",
                "actualProcessExits": observations,
                "checkpointSealed": False,
                "independentM2": "PENDING",
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
