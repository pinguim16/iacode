"""Preserve the completed failed v4 attempt byte-for-byte before a fresh immutable producer."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from ledger_common import load_json, use_utf8_stdout, utc_now, write_json
from verify import build_stages

SUBJECT = "01ffb159a852a60731459f38353c846c8e7a0bc8"
NAMES = ("VERIFY.json", "PUBLISHED-CLEAN-CLONE-REPORT.json", "FUNCTIONAL-SCENARIOS.json",
         "COMPOSE-ISOLATION-AUDIT.json", "PRODUCER-REPORTS.json", "FULL-VERIFY-PROGRESS.json")


def main() -> int:
    manifest_path = CHECKPOINT / "attempts/RUNTIME-V4-ARCHIVE.json"
    destinations = {name: CHECKPOINT / "attempts" / ("RUNTIME-V4-" + name) for name in NAMES}
    if manifest_path.exists() or any(path.exists() for path in destinations.values()):
        raise ValueError("the failed attempt archive is immutable; never overwrite or replay it")
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    producer = load_json(CHECKPOINT / "PRODUCER-REPORTS.json")
    expected = [stage.name for stage in build_stages(False)]
    if (verification.get("result") != "FAIL" or verification.get("fast") is not False
            or [row["name"] for row in verification["stages"]] != expected
            or publication.get("publishedCommit") != SUBJECT
            or publication.get("result") != "FAIL"
            or publication.get("stageDenominator") != len(expected)
            or producer.get("subjectCommit") != SUBJECT):
        raise ValueError("only the actual complete failed v4 subject may be archived")
    observations = []
    for name in NAMES:
        source, destination = CHECKPOINT / name, destinations[name]
        if (source.is_symlink() or source.resolve().parent != CHECKPOINT.resolve()
                or destination.parent.is_symlink() or destination.parent.is_junction()
                or not destination.resolve().is_relative_to(CHECKPOINT.resolve())):
            raise ValueError("refusing redirected or escaping observation paths")
        content = source.read_bytes()
        with destination.open("xb") as output:
            output.write(content)
        if destination.read_bytes() != content:
            raise ValueError("failed-attempt archive byte equality failed")
        observations.append({"source": name, "archive": destination.relative_to(CHECKPOINT).as_posix(),
            "sizeBytes": len(content), "sha256": hashlib.sha256(content).hexdigest(),
            "exactSourceBytesPreserved": True})
    # Only this redundant primary projection is removed, after its verified immutable copy.
    # Original safe producer files remain untouched under the UUID manifest.
    verifier_path = CHECKPOINT / "VERIFY.json"
    if (verifier_path.is_symlink() or verifier_path.resolve().parent != CHECKPOINT.resolve()
            or verifier_path.read_bytes() != destinations["VERIFY.json"].read_bytes()):
        raise ValueError("primary projection changed; no removal allowed")
    verifier_path.unlink()
    write_json(manifest_path, {"kind": "FAILED_COMPLETE_ATTEMPT_ARCHIVE_NOT_ACCEPTANCE",
        "archivedAt": utc_now(), "subjectCommit": SUBJECT, "command": "cmd-0208",
        "stageDenominator": len(expected), "stagesPassed": publication["stagesPassed"],
        "stagesFailed": publication["stagesFailed"], "originalProducerManifest": producer["manifest"],
        "copiedObservations": observations, "primaryVerifierProjectionRemovedAfterVerifiedCopy": True,
        "originalProducerFilesChanged": False, "gateVerdictIssued": False})
    print("FAILED_COMPLETE_V4_ARCHIVED exactCopies=" + str(len(observations)) + " result=FAIL")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
