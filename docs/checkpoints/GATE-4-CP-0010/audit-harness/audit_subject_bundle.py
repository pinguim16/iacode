#!/usr/bin/env python3
"""Internally audit the immutable published subject without modifying its checkpoint."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0009"
COMMIT = "ff2814f7d7bf06fa8a99858b958daf3f22197496"
REMOTE = "https://github.com/pinguim16/iacode.git"


def command(arguments: list[str], cwd: Path) -> str:
    completed = subprocess.run(arguments, cwd=cwd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    if completed.returncode:
        raise RuntimeError(f"subject audit command failed: {arguments[0]} exit={completed.returncode}")
    return completed.stdout.strip()


def main() -> int:
    output = CHECKPOINT / "SUBJECT-BUNDLE-AUDIT.json"
    if output.exists():
        raise RuntimeError("preserve the previous subject audit before another attempt")
    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="iacode-cp0010-subject-audit-") as directory:
        clone = Path(directory) / "repository"
        command(["git", "clone", "--no-local", REMOTE, str(clone)], Path(directory))
        command(["git", "checkout", "--detach", f"iacode-checkpoints/{SUBJECT}"], clone)
        observed = command(["git", "rev-parse", "HEAD"], clone)
        if observed != COMMIT:
            raise RuntimeError("published subject tag changed")
        checks["coldStartCheckpoint"] = "CHECKPOINT_VALID" in command(
            [sys.executable, "scripts/development-ledger/validate_checkpoint.py"], clone)
        checks["integrity"] = "INTEGRITY_VALID" in command(
            [sys.executable, "scripts/development-ledger/verify_integrity.py"], clone)
        sys.path.insert(0, str(clone / "scripts" / "development-ledger"))
        import review_bundle

        subject = clone / "docs" / "checkpoints" / SUBJECT
        declaration = json.loads((subject / "REVIEW-BUNDLE-VALIDATION.json").read_text(encoding="utf-8"))
        reconstruction = review_bundle.reconstruct_twice(clone, subject, declaration["subject"]["commit"])
        positive = review_bundle.verify_declaration(clone, subject, declaration, reconstruction)
        checks["declaredReconstruction"] = positive["result"] == "PASS"
        checks["byteIdentity"] = reconstruction.get("byteIdentical") is True
        checks["twoValidArchives"] = reconstruction.get("validationResults") == ["PASS", "PASS"]
        for field, value, expected in (
            ("sha256", "0" * 64, "sha256"),
            ("sizeBytes", declaration["sizeBytes"] + 1, "sizeBytes"),
        ):
            mutated = copy.deepcopy(declaration)
            mutated[field] = value
            refused = review_bundle.verify_declaration(clone, subject, mutated, reconstruction)
            checks[f"refusesMutated{field}"] = (
                refused["result"] == "FAIL" and any(expected in item for item in refused["findings"]))
        mutated = copy.deepcopy(declaration)
        mutated["payloadPolicy"]["excludedCheckpointFiles"].append("STATE.json")
        refused = review_bundle.verify_declaration(clone, subject, mutated, reconstruction)
        checks["refusesWiderExclusion"] = refused["result"] == "FAIL"
        checks["sealedSubjectUnchanged"] = not command(["git", "status", "--porcelain"], clone)
        report = {
            "schemaVersion": "1.0.0", "reviewKind": "SAME_SESSION_INTERNAL_REVIEW",
            "subjectCheckpoint": SUBJECT, "subjectCommit": observed,
            "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "declaration": {key: declaration[key] for key in ("sha256", "sizeBytes", "entries")},
            "reconstruction": reconstruction, "positiveControl": positive["result"],
            "checks": checks, "result": "PASS" if all(checks.values()) else "FAIL",
        }
    report["temporaryCloneRemoved"] = not Path(directory).exists()
    if not report["temporaryCloneRemoved"]:
        report["result"] = "FAIL"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"SUBJECT_BUNDLE_AUDIT={report['result']} checks={len(checks)}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
