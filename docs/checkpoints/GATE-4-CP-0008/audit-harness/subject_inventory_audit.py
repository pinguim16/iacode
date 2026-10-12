#!/usr/bin/env python3
"""Read every tracked CP0007 artifact and audit identity, hashes and command transport."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0007"
COMMIT = "e21d30fde473f302d0f8f60b59acf008fa52e250"
TAG = f"iacode-checkpoints/{SUBJECT}"
REMOTE = "https://github.com/pinguim16/iacode.git"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def run(arguments: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        arguments, cwd=cwd, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    return {"exitCode": completed.returncode, "output": completed.stdout.strip()}


def git(cwd: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=cwd, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    return completed.stdout.strip()


def parse_file(path: Path) -> dict[str, Any]:
    content = path.read_bytes()
    result: dict[str, Any] = {
        "path": path.as_posix(),
        "sizeBytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "readComplete": True,
        "parse": "NOT_APPLICABLE",
    }
    if path.suffix == ".json":
        json.loads(content.decode("utf-8"))
        result["parse"] = "JSON_VALID"
    elif path.suffix == ".jsonl":
        lines = [line for line in content.decode("utf-8").splitlines() if line.strip()]
        for line in lines:
            json.loads(line)
        result["parse"] = f"JSONL_VALID:{len(lines)}"
    elif path.suffix in {".md", ".txt", ".py"}:
        content.decode("utf-8")
        result["parse"] = "UTF8_VALID"
    return result


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="iacode-g4-cp0008-inventory-") as temporary:
        parent = Path(temporary)
        clone = parent / "repository"
        clone_result = run(["git", "clone", "--quiet", "--no-local", REMOTE, str(clone)], parent)
        checkout = run(["git", "checkout", "--quiet", "--detach", TAG], clone)
        head = git(clone, "rev-parse", "HEAD")
        remote_main = git(clone, "rev-parse", "origin/main")
        tag_commit = git(clone, "rev-parse", f"{TAG}^{{commit}}")
        tree = git(clone, "rev-parse", "HEAD^{tree}")
        validate = run([sys.executable, "scripts/development-ledger/validate_checkpoint.py"], clone)
        integrity = run([sys.executable, "scripts/development-ledger/verify_integrity.py"], clone)
        fsck = run(["git", "fsck", "--full", "--strict"], clone)
        tracked = [
            line for line in git(clone, "ls-tree", "-r", "--name-only", "HEAD", f"docs/checkpoints/{SUBJECT}").splitlines()
            if line
        ]
        files = []
        for relative in tracked:
            item = parse_file(clone / relative)
            item["path"] = relative
            files.append(item)
        commands = [
            json.loads(line)
            for line in (clone / "docs" / "checkpoints" / SUBJECT / "COMMANDS.jsonl")
            .read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        sys.path.insert(0, str(clone / "scripts" / "development-ledger"))
        from ledger_common import command_input_transport_error  # type: ignore[import-not-found]

        completed_inputs = [
            {
                "commandId": command.get("id"),
                "path": reference,
                "transportError": command_input_transport_error(clone, str(reference)),
            }
            for command in commands
            if command.get("result") == "COMPLETED"
            for reference in command.get("inputs") or []
        ]
        bad_inputs = [item for item in completed_inputs if item["transportError"] is not None]
        refused = [
            command for command in commands
            if command.get("result") == "PRECONDITION_REJECTED"
            and command.get("resultCode") == "E_NONTRANSPORT_INPUT"
        ]
        chain = json.loads((clone / ".iacode" / "anchors" / "checkpoint-chain.json").read_text(encoding="utf-8"))
        anchors = chain.get("anchors") or []
        subject_anchor = next((item for item in anchors if item.get("checkpointId") == SUBJECT), None)
        checks = {
            "clone": clone_result["exitCode"] == 0 and checkout["exitCode"] == 0,
            "identity": head == remote_main == tag_commit == COMMIT,
            "checkpointValidation": validate["exitCode"] == 0 and "CHECKPOINT_VALID" in validate["output"],
            "integrity": integrity["exitCode"] == 0 and "INTEGRITY_VALID" in integrity["output"],
            "gitObjectIntegrity": fsck["exitCode"] == 0,
            "completeRead": bool(files) and len(files) == len(tracked) and all(item["readComplete"] for item in files),
            "structuredParse": all(not str(item["parse"]).startswith("INVALID") for item in files),
            "completedCommandInputsPortable": not bad_inputs,
            "transportRefusalPreserved": bool(refused),
            "pendingAnchorDerived": subject_anchor is None,
        }
        report = {
            "schemaVersion": "1.0.0",
            "artifact": "PUBLISHED-SUBJECT-INVENTORY-AUDIT",
            "checkpoint": CHECKPOINT.name,
            "subjectCheckpoint": SUBJECT,
            "subjectCommit": COMMIT,
            "subjectTree": tree,
            "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "identity": {"head": head, "originMain": remote_main, "tagCommit": tag_commit},
            "trackedCheckpointFileCount": len(tracked),
            "trackedCheckpointFiles": files,
            "commandCount": len(commands),
            "completedInputCount": len(completed_inputs),
            "nonTransportableCompletedInputs": bad_inputs,
            "recordedTransportRefusals": [item.get("id") for item in refused],
            "anchorStateAtSubject": (
                "PENDING_SUCCESSOR_ANCHOR" if subject_anchor is None else "ANCHORED"
            ),
            "anchorCountAtSubject": len(anchors),
            "validation": validate,
            "integrity": integrity,
            "gitFsck": fsck,
            "checks": checks,
            "result": "PASS" if all(checks.values()) else "FAIL",
        }
        arguments.report.resolve().write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n",
        )
    print(
        f"SUBJECT_INVENTORY_AUDIT={report['result']} files={len(files)} "
        f"commands={len(commands)} inputs={len(completed_inputs)} anchor=PENDING_SUCCESSOR_ANCHOR"
    )
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
