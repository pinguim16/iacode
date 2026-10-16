#!/usr/bin/env python3
"""Preserve actual v3 results without promoting them over later source corrections."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import LedgerError, load_json, utc_now, write_json

FILES = ("VERIFY.json", "FUNCTIONAL-SCENARIOS.json", "PUBLISHED-CLEAN-CLONE-REPORT.json",
         "COMPOSE-ISOLATION-AUDIT.json", "FULL-VERIFY-PROGRESS.json")
SUBJECT = "0b1fa85c46cf3ce0bcb13fd4792f389d97d71ea4"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest_path = CHECKPOINT / "VERIFICATION-ATTEMPT-ARCHIVE.json"
    manifest = load_json(manifest_path)
    attempts = list(manifest.get("additionalAttempts") or [])
    if any(item.get("subjectCommit") == SUBJECT for item in attempts):
        raise LedgerError("v3 was already preserved")
    for attempt in [manifest, *attempts]:
        for artifact in attempt["artifacts"]:
            if digest(CHECKPOINT / artifact["path"]) != artifact["sha256"]:
                raise LedgerError("a preserved predecessor artifact changed")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    verification = load_json(CHECKPOINT / "VERIFY.json")
    destination = CHECKPOINT / "attempts/published-v3"
    if (publication.get("publishedCommit") != SUBJECT
            or not publication.get("temporaryCloneRemoved")
            or verification.get("result") not in {"PASS", "FAIL"}
            or len(verification.get("stages", [])) != 42 or destination.exists()
            or not all((CHECKPOINT / name).is_file() for name in FILES)):
        raise LedgerError("only the completed, cleaned v3 subject may be archived")
    artifacts = []
    destination.mkdir(parents=True)
    for name in FILES:
        source, target = CHECKPOINT / name, destination / name
        expected = digest(source)
        source.rename(target)
        if digest(target) != expected:
            raise LedgerError("an archived verifier artifact changed bytes")
        artifacts.append({"path": target.relative_to(CHECKPOINT).as_posix(), "sha256": expected})
    attempts.append({"subjectCommit": SUBJECT, "archivedAt": utc_now(),
                     "verificationResult": verification["result"],
                     "publicationResult": publication["result"],
                     "eligibleForCurrentPromotion": False,
                     "qualification": "G4-INT-025 correction and tests were added later in the main "
                                      "checkout; v3 clone and driver remained unchanged.",
                     "artifacts": artifacts})
    manifest["additionalAttempts"] = attempts
    write_json(manifest_path, manifest)
    print(f"V3_VERIFICATION_PRESERVED artifacts={len(artifacts)} actual_result={verification['result']} promotion=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
