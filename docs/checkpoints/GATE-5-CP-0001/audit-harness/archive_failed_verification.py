"""Preserve completed failed verification observations exactly before a corrective rerun."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from verify import build_stages  # noqa: E402
NAMES = (
    "VERIFY.json", "FUNCTIONAL-SCENARIOS.json", "PUBLISHED-CLEAN-CLONE-REPORT.json",
    "COMPOSE-ISOLATION-AUDIT.json", "FULL-VERIFY-PROGRESS.json",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", required=True, type=int)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--collector-failure-command")
    args = parser.parse_args()
    if args.attempt < 1:
        raise ValueError("positive attempt number required")
    verification = json.loads((CHECKPOINT / "VERIFY.json").read_text(encoding="utf-8"))
    progress = json.loads((CHECKPOINT / "FULL-VERIFY-PROGRESS.json").read_text(encoding="utf-8"))
    expected = [stage.name for stage in build_stages(False)]
    if (verification.get("result") != "FAIL" or verification.get("fast") is not False
            or [row["name"] for row in verification["stages"]] != expected
            or progress.get("subjectCommit") != args.expected_commit):
        raise ValueError("a complete failed exact-subject current verifier observation is required")
    published_path = CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json"
    collected = published_path.is_file()
    if collected:
        published = json.loads(published_path.read_text(encoding="utf-8"))
        if (published.get("publishedCommit") != args.expected_commit
                or published.get("result") != "FAIL"
                or not published.get("temporaryCloneRemoved")
                or published.get("exitCode") == 0):
            raise ValueError("the completed failed collector does not bind this exact subject")
    else:
        records = {row["id"]: row for row in (json.loads(line) for line in
                   (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
                   if line.strip())}
        record = records.get(args.collector_failure_command, {})
        if (record.get("exitCode") != 1 or record.get("subjectCommit") != args.expected_commit
                or "audit-harness/run_full_verification.py" not in record.get("command", "")
                or Path(progress["clone"]).parent.exists()
                or verification.get("isolation", {}).get("postRunCleanup") != "PASS"):
            raise ValueError("actual failed collector record and observed owned cleanup are required")
    attempts = CHECKPOINT / "attempts"
    prefix = f"FULL-VERIFY-RED-{args.attempt:04d}"
    manifest = attempts / f"{prefix}-MANIFEST.json"
    available = [name for name in NAMES if (CHECKPOINT / name).is_file()]
    if collected and len(available) != len(NAMES):
        raise ValueError("a completed collector must have produced every promised observation")
    destinations = {name: attempts / f"{prefix}-{name}" for name in available}
    if manifest.exists() or any(path.exists() for path in destinations.values()):
        raise ValueError("an immutable attempt archive already exists")
    observations = []
    attempts.mkdir(parents=True, exist_ok=True)
    for name, destination in destinations.items():
        original = CHECKPOINT / name
        before = original.read_bytes()
        shutil.copyfile(original, destination)
        if destination.read_bytes() != before:
            raise RuntimeError("archive byte equality failed: " + name)
        observations.append({
            "original": name, "archive": destination.relative_to(CHECKPOINT).as_posix(),
            "bytes": len(before), "sha256": hashlib.sha256(before).hexdigest(),
        })
    document = {
        "kind": "COMPLETED_FAILED_VERIFICATION_ARCHIVE",
        "subjectCommit": args.expected_commit, "archivedAt": datetime.now(UTC).isoformat(),
        "result": "FAIL", "verifierCompleted": True, "collectorCompleted": collected,
        "collectorFailureCommand": args.collector_failure_command,
        "unavailableCollectorArtifacts": [name for name in NAMES if name not in available],
        "stagesPassed": sum(row["result"] == "PASS" for row in verification["stages"]),
        "stageDenominator": len(expected),
        "cleanup": {"compose": verification["isolation"]["postRunCleanup"],
                    "temporaryDirectoryAbsentObserved": not Path(progress["clone"]).parent.exists()},
        "observations": observations, "sameSessionInternalEvidence": True,
    }
    manifest.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")
    # Each current file has an exact checked recoverable copy and an identifying manifest.
    # Retiring these paths allows the verifier's no-overwrite precondition to remain strict.
    for name in available:
        (CHECKPOINT / name).unlink()
    print(json.dumps(document, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
