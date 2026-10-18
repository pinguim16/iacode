"""Retain exact completed v5 assurance and failed Red Team bytes before fresh rework."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets, load_json, use_utf8_stdout, utc_now, write_json

SUBJECT = "950421fc5554a7e654ffd6096898b07a679d9923"
NAMES = (
    "VERIFY.json", "PUBLISHED-CLEAN-CLONE-REPORT.json", "FUNCTIONAL-SCENARIOS.json",
    "COMPOSE-ISOLATION-AUDIT.json", "PRODUCER-REPORTS.json", "FULL-VERIFY-PROGRESS.json",
    "FUNCTIONAL-ACCEPTANCE.json", "FUNCTIONAL-ACCEPTANCE-VALIDATION.json",
    "COMPLETENESS-REPORT.json", "COMPLETENESS-REPORT.md", "M2-INTERNAL-RED-TEAM.json",
    "M2-INHERITED-RED-TEAM.json", "RED-TEAM-NATIVE.json", "RED-TEAM-DESKTOP.json",
    "RED-TEAM-EXPERIENCE.json", "RED-TEAM-EXECUTIONS.json", "RED-TEAM-REPORT.md",
)
RETIRED_PROJECTIONS = (
    "VERIFY.json", "FUNCTIONAL-ACCEPTANCE.json", "FUNCTIONAL-ACCEPTANCE-VALIDATION.json",
    "M2-INTERNAL-RED-TEAM.json", "COMPLETENESS-REPORT.json", "COMPLETENESS-REPORT.md",
)


def main() -> int:
    manifest_path = CHECKPOINT / "attempts/RUNTIME-V5-ASSURANCE-ARCHIVE.json"
    if manifest_path.exists():
        raise ValueError("immutable v5 archive exists; do not replay")
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    attacks = load_json(CHECKPOINT / "M2-INTERNAL-RED-TEAM.json")
    native = load_json(CHECKPOINT / "RED-TEAM-NATIVE.json")
    if (publication.get("publishedCommit") != SUBJECT or verification.get("result") != "PASS"
            or verification.get("fast") is not False or len(verification.get("stages", [])) != 47
            or any(row.get("result") != "PASS" for row in verification["stages"])
            or attacks.get("result") != "RED_TEAM_FAIL" or native.get("result") != "FAIL"):
        raise ValueError("the exact completed v5 PASS and failed fresh native/Red Team are required")
    sources = [(CHECKPOINT / name, "RUNTIME-V5-ASSURANCE-" + name) for name in NAMES]
    sources.extend((ROOT / "var" / name, "RUNTIME-V5-RAW-" + name)
                   for name in ("gate5-red-team-native.json", "gate5-red-team-desktop.json"))
    payloads = []
    for source, name in sources:
        destination = CHECKPOINT / "attempts" / name
        if source.is_symlink() or not source.is_file() or destination.exists():
            raise ValueError("archive source absent/redirected or immutable destination exists")
        raw = source.read_bytes()
        if find_secrets(raw.decode("utf-8", "strict")):
            raise ValueError("unsafe original bytes refused before archival")
        payloads.append((source, destination, raw))
    rows = []
    for source, destination, raw in payloads:
        with destination.open("xb") as output:
            output.write(raw)
        if destination.read_bytes() != raw or source.read_bytes() != raw:
            raise RuntimeError("byte-exact archive verification failed")
        rows.append({"source": source.relative_to(ROOT).as_posix(),
                     "archive": destination.relative_to(ROOT).as_posix(), "bytes": len(raw),
                     "sha256": hashlib.sha256(raw).hexdigest(), "byteEqual": True})
    # Only the six redundant, verified checkpoint-local projections are retired.
    # Original UUID producers, raw scenario results and failure history are untouched.
    for name in RETIRED_PROJECTIONS:
        source = CHECKPOINT / name
        raw = next(raw for path, _, raw in payloads if path == source)
        if source.parent != CHECKPOINT or source.is_symlink() or source.read_bytes() != raw:
            raise ValueError("changed or redirected projection refused before retirement")
        source.unlink()
    report = {"kind": "EXACT_HISTORICAL_V5_ASSURANCE_ARCHIVE_NOT_CURRENT_ACCEPTANCE",
              "observedAt": utc_now(), "subjectCommit": SUBJECT, "records": rows,
              "completedFullCommand": "cmd-0232", "failedRedTeamCommand": "cmd-0258",
              "retiredRedundantProjections": list(RETIRED_PROJECTIONS),
              "originalProducerHistoryChanged": False, "result": "PASS"}
    write_json(manifest_path, report)
    print(json.dumps({"archiveResult": "PASS", "records": len(rows),
                      "retiredRedundantProjections": list(RETIRED_PROJECTIONS)}))
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
