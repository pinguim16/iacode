"""Serialize actual process exits around an unsealed Gate7 progress publication.

Invoke directly, never through record_command: the staged scan records itself through that tool
and the canonical finalizer self-records. A durable success record is not a child exit signal.
This neither seals a checkpoint nor changes any requirement, promotion rule or audit verdict.
"""

from __future__ import annotations

import argparse
import json
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


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from ledger_common import find_secrets, use_utf8_stdout

    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--message", required=True)
    options = parser.parse_args()
    state = json.loads((CHECKPOINT / "STATE.json").read_bytes())
    if state["gate"] != "GATE-7" or state["status"] != "IN_PROGRESS":
        raise ValueError("only unsealed implementing Gate7 progress may be published")
    message = options.message
    if not message.strip() or len(message) > 120 or any(ord(char) < 32 for char in message):
        raise ValueError("one bounded nonempty commit subject is required")
    if find_secrets(message):
        raise ValueError("protected commit subject refused")
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
    python = sys.executable
    ledger = "scripts/development-ledger/"
    steps = [
        ("stage-declared-inputs", ["git", "add", "--", *paths]),
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
        ("stage-finalized-content", ["git", "add", "--", *paths]),
        ("commit", ["git", "commit", "-m", message]),
        ("committed-validation", [python, ledger + "validate_checkpoint.py"]),
        ("normal-push", ["git", "push", "origin", branch]),
    ]
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
