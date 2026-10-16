#!/usr/bin/env python3
"""Append the completed red v2 artifacts without replacing the preserved v1 manifest."""

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
SUBJECT = "4c53e4f788adc24e1b9cd9f581a7dc0d0f3c1340"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest_path = CHECKPOINT / "VERIFICATION-ATTEMPT-ARCHIVE.json"
    manifest = load_json(manifest_path)
    if manifest.get("additionalAttempts"):
        raise LedgerError("preserve the existing additional-attempt manifest")
    for artifact in manifest["artifacts"]:
        if digest(CHECKPOINT / artifact["path"]) != artifact["sha256"]:
            raise LedgerError("the preserved v1 evidence changed")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    verification = load_json(CHECKPOINT / "VERIFY.json")
    destination = CHECKPOINT / "attempts/published-v2"
    if (publication.get("publishedCommit") != SUBJECT or publication.get("result") != "FAIL"
            or not publication.get("temporaryCloneRemoved")
            or verification.get("result") != "FAIL" or len(verification.get("stages", [])) != 42
            or destination.exists() or not all((CHECKPOINT / name).is_file() for name in FILES)):
        raise LedgerError("only the completed red v2 subject may be archived")
    artifacts = []
    destination.mkdir(parents=True)
    for name in FILES:
        source, target = CHECKPOINT / name, destination / name
        expected = digest(source)
        source.rename(target)
        if digest(target) != expected:
            raise LedgerError("an archived verifier artifact changed bytes")
        artifacts.append({"path": target.relative_to(CHECKPOINT).as_posix(), "sha256": expected})
    manifest["additionalAttempts"] = [{"subjectCommit": SUBJECT, "archivedAt": utc_now(),
                                      "verificationResult": "FAIL", "artifacts": artifacts}]
    write_json(manifest_path, manifest)
    print(f"V2_VERIFICATION_PRESERVED artifacts={len(artifacts)} result=FAIL retained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
