"""Serialize actual process exits around an unsealed Gate7 progress publication.

Invoke directly, never through record_command: the staged scan records itself through that tool
and the canonical finalizer self-records. A durable success record is not a child exit signal.
This neither seals a checkpoint nor changes any requirement, promotion rule or audit verdict.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


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
    parser.add_argument("--message")
    parser.add_argument("--runtime-tag")
    options = parser.parse_args()
    state = json.loads((CHECKPOINT / "STATE.json").read_bytes())
    if state["gate"] != "GATE-7" or state["status"] != "IN_PROGRESS":
        raise ValueError("only unsealed implementing Gate7 progress may be published")
    message = options.message or ""
    if not options.stage_declared and (
        not message.strip() or len(message) > 120 or any(ord(char) < 32 for char in message)
    ):
        raise ValueError("one bounded nonempty commit subject is required")
    if find_secrets(message):
        raise ValueError("protected commit subject refused")
    if options.runtime_tag is not None and re.fullmatch(
        r"iacode-subjects/GATE-7-CP-0003-runtime-v[1-9][0-9]*", options.runtime_tag
    ) is None:
        raise ValueError("only a new explicitly named current immutable runtime subject tag is allowed")
    branch = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, check=True, text=True
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
                "IN_PROGRESS",
                "--commit-ref",
                "HEAD",
            ],
        ),
        ("stage-finalized-content", [python, str(Path(__file__)), "--stage-declared"]),
        ("commit", ["git", "commit", "-m", message]),
        ("committed-validation", [python, ledger + "validate_checkpoint.py"]),
    ]
    if options.runtime_tag:
        steps.extend([
            ("immutable-runtime-tag", ["git", "tag", options.runtime_tag]),
            ("atomic-normal-push", ["git", "push", "--atomic", "origin", branch,
                                    "refs/tags/" + options.runtime_tag]),
        ])
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
                "kind": "IN_PROGRESS_NOT_GATE_ACCEPTANCE",
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
