#!/usr/bin/env python3
"""Observe real live-state generation only for the exact published, unchanged source."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import (
    LedgerError, canonical_hash_path, load_json, scope_fingerprint, utc_now, use_utf8_stdout,
    write_json,
)

REMOTE = "https://github.com/pinguim16/iacode.git"


def git(root: Path, *arguments: str) -> str:
    result = subprocess.run(["git", *arguments], cwd=root, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", check=False)
    if result.returncode:
        raise LedgerError(f"program-state proof Git {arguments[0]} refused: exit {result.returncode}")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject-tag", required=True)
    args = parser.parse_args()
    destination = CHECKPOINT / "PROGRAM-STATE-LIVE-VALIDATION.json"
    if destination.exists():
        raise LedgerError("preserve the existing published live-state observation")
    fingerprint = scope_fingerprint(ROOT)
    subject = git(ROOT, "rev-parse", "HEAD")
    before = git(ROOT, "status", "--porcelain")
    historical = ROOT / "docs/program/PROGRAM-STATE.json"
    historical_hash = canonical_hash_path(historical)
    observations = []
    with tempfile.TemporaryDirectory(prefix="iacode-cp0010-program-state-proof-") as temporary:
        clone = Path(temporary) / "repository"
        git(Path(temporary), "clone", "--no-local", REMOTE, str(clone))
        git(clone, "checkout", "--detach", args.subject_tag)
        if (git(clone, "rev-parse", "HEAD") != subject
                or git(clone, "rev-parse", "origin/main") != subject
                or git(clone, "status", "--porcelain")
                or scope_fingerprint(clone) != fingerprint):
            raise LedgerError("current source is not the unchanged exact published subject")
        for arguments in (["--write"], []):
            result = subprocess.run(
                [sys.executable, "scripts/development-ledger/program_state.py", *arguments],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                check=False,
            )
            observations.append({"command": "python scripts/development-ledger/program_state.py"
                                 + (" --write" if arguments else ""),
                                 "exitCode": result.returncode, "stdout": result.stdout.strip()})
        state = load_json(ROOT / "var/program-state.json")
        after = git(ROOT, "status", "--porcelain")
        checks = {
            "actualCommandsPassed": all(item["exitCode"] == 0 for item in observations),
            "latestCheckpoint": state["checkpoint"] == CHECKPOINT.name,
            "exactLocalAndRemote": state["localCommit"] == state["remoteCommit"] == subject,
            "declaredStatus": state["status"] == load_json(CHECKPOINT / "STATE.json")["status"],
            "trackedStateUnchanged": before == after,
            "historicalObservationUnchanged": canonical_hash_path(historical) == historical_hash,
            "sourceUnchangedDuringProof": scope_fingerprint(ROOT) == fingerprint,
            "transportedSubjectUnchanged": not git(clone, "status", "--porcelain"),
        }
    checks["temporaryCloneRemoved"] = not Path(temporary).exists()
    report = {"schemaVersion": "1.0.0", "generatedAt": utc_now(),
              "kind": "INTERNAL_PUBLISHED_LIVE_STATE_PROOF_NOT_INDEPENDENT",
              "subjectCommit": subject, "subjectTag": args.subject_tag,
              "sourceFingerprint": fingerprint, "commands": observations,
              "observed": state, "checks": checks,
              "result": "PASS" if all(checks.values()) else "FAIL"}
    write_json(destination, report)
    print(f"PUBLISHED_PROGRAM_STATE={report['result']} checks={sum(checks.values())}/{len(checks)}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
