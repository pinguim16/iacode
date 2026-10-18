"""Capture available safe raw native/desktop observations without retroactive byte claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets, load_json, scope_fingerprint, use_utf8_stdout, utc_now, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", choices=("v6", "v8"), required=True)
    parser.add_argument("--source-command", required=True)
    args = parser.parse_args()
    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise ValueError("only unsealed implementing evidence may be captured")
    historical = args.label == "v6"
    subject = ("1442b86d38be11aee5e2ff635e576be08e52997b" if historical else
               load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")["publishedCommit"])
    fingerprint = ("584eb6433e55f8a693315fa84c367c37de3c1c36747b08694888a01ca0c32f91"
                   if historical else scope_fingerprint(ROOT))
    commands = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    execution = next((row for row in commands if row["id"] == args.source_command), None)
    if (execution is None or execution.get("exitCode") != 0
            or execution.get("subjectCommit") != subject
            or "audit-harness/run_internal_red_team.py" not in execution["command"]):
        raise ValueError("the actual successful matching Red Team semantic observation is required")
    prefix = "RUNTIME-" + args.label.upper() + "-RED-TEAM-RAW-"
    manifest = CHECKPOINT / "attempts" / (prefix + "MANIFEST.json")
    if manifest.exists() or (CHECKPOINT / "attempts").is_symlink() or (CHECKPOINT / "attempts").is_junction():
        raise ValueError("immutable raw capture exists or archive owner is redirected")
    payloads = []
    for kind in ("native", "desktop"):
        source = ROOT / "var" / ("gate5-red-team-" + kind + ".json")
        projection = CHECKPOINT / (("attempts/RUNTIME-V6-FINALIZATION-" if historical else "")
                                   + "RED-TEAM-" + kind.upper() + ".json")
        destination = CHECKPOINT / "attempts" / (prefix + kind.upper() + ".json")
        if (source.is_symlink() or not source.is_file() or destination.exists()
                or not source.resolve().is_relative_to(ROOT.resolve())):
            raise ValueError("missing/redirected raw source or immutable destination already exists")
        raw = source.read_bytes()
        if find_secrets(raw.decode("utf-8", "strict")):
            raise ValueError("unsafe raw producer refused without recording its contents")
        observed = json.loads(raw)
        if (observed != load_json(projection) or observed.get("result") != "PASS"
                or observed.get("ownedTemporaryDirectoryRemoved") is not True
                or (kind == "desktop" and observed.get("sourceFingerprint") != fingerprint)):
            raise ValueError("available bytes do not match the expected successful semantic observation")
        payloads.append((source, projection, destination, raw))
    rows = []
    for source, projection, destination, raw in payloads:
        with destination.open("xb") as output:
            output.write(raw)
        if source.read_bytes() != raw or destination.read_bytes() != raw:
            raise ValueError("raw source changed during capture or archive byte equality failed")
        rows.append({"source": source.relative_to(ROOT).as_posix(),
            "semanticProjection": projection.relative_to(ROOT).as_posix(),
            "archive": destination.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(), "semanticIdentityMatches": True, "byteEqualAtCapture": True})
    write_json(manifest, {"kind": "AVAILABLE_RAW_PRODUCER_CAPTURE_NOT_GATE_ACCEPTANCE",
        "capturedAt": utc_now(), "label": args.label, "semanticObservationCommand": args.source_command,
        "semanticObservationSubject": subject, "semanticTargetFingerprint": fingerprint,
        "historicalBytesAtOriginalCommandNotAttested": historical,
        "limit": "This capture attests the available bytes at capturedAt. Semantic equality with an earlier projection never retroactively attests historical byte spelling.",
        "records": rows, "originalBytesRewritten": False, "gateVerdictIssued": False,
        "trainingAllowed": False, "ragAllowed": False, "distillationAllowed": False, "result": "PASS"})
    print(f"RAW_PRODUCERS_CAPTURED label={args.label} records={len(rows)} byte_equal=true no_gate_verdict=true")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
