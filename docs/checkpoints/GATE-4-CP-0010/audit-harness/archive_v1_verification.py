#!/usr/bin/env python3
"""Preserve every completed red v1 verifier artifact byte-for-byte before a replacement."""

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
SUBJECT = "33c3f42c0d5faf112c3e037a55006dd750c4bfe1"


def main() -> int:
    report = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    verification = load_json(CHECKPOINT / "VERIFY.json")
    destination = CHECKPOINT / "attempts/published-v1"
    if (report.get("publishedCommit") != SUBJECT or report.get("result") != "FAIL"
            or not report.get("temporaryCloneRemoved") or verification.get("result") != "FAIL"
            or len(verification.get("stages", [])) != 42 or destination.exists()
            or not all((CHECKPOINT / name).is_file() for name in FILES)):
        raise LedgerError("only the completed red v1 subject may be archived by this harness")
    manifest = []
    destination.mkdir(parents=True)
    for name in FILES:
        source, target = CHECKPOINT / name, destination / name
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        source.rename(target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise LedgerError("an archived verifier artifact changed bytes")
        manifest.append({"path": target.relative_to(CHECKPOINT).as_posix(), "sha256": digest})
    write_json(CHECKPOINT / "VERIFICATION-ATTEMPT-ARCHIVE.json", {
        "schemaVersion": "1.0.0", "generatedAt": utc_now(), "subjectCommit": SUBJECT,
        "result": "PASS", "meaning": "red verification preserved, not an approval",
        "artifacts": manifest,
    })
    print(f"V1_VERIFICATION_PRESERVED artifacts={len(manifest)} result=FAIL retained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
