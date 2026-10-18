"""Preserve original v6 observations as raw data, not relocated active Markdown/Python."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, use_utf8_stdout, utc_now, write_json


def main() -> int:
    destination = CHECKPOINT / "attempts/RUNTIME-V6-RAW-CATALOG.json"
    if destination.exists():
        raise ValueError("raw catalog already exists; never replay relocation")
    original = CHECKPOINT / "attempts/RUNTIME-V6-FINALIZATION-ARCHIVE.json"
    raw_manifest = original.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest["result"] != "PASS" or len(manifest["records"]) != 30:
        raise ValueError("the original complete immutable manifest is required")
    records = []
    for row in manifest["records"]:
        source = ROOT / row["archive"]
        target = source.with_name(source.name + ".raw") if source.suffix in {".md", ".py"} else source
        if (source.parent.resolve() != (CHECKPOINT / "attempts").resolve() or source.is_symlink()
                or not source.is_file() or (target != source and target.exists())):
            raise ValueError("unexpected archive target; no broad relocation allowed")
        raw = source.read_bytes()
        if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("original observation bytes changed")
        records.append((row, source, target, raw))
    current = []
    for row, source, target, raw in records:
        if target != source:
            source.rename(target)
        if target.read_bytes() != raw:
            raise ValueError("raw relocation altered bytes")
        current.append({**row, "originalArchive": row["archive"], "archive": target.relative_to(ROOT).as_posix()})
    if original.read_bytes() != raw_manifest:
        raise ValueError("original immutable manifest changed")
    write_json(destination, {"kind": "BYTE_EXACT_RAW_OBSERVATION_CATALOG_NOT_ACTIVE_DOCUMENTATION",
        "generatedAt": utc_now(), "originalManifest": original.relative_to(ROOT).as_posix(),
        "originalManifestSha256": hashlib.sha256(raw_manifest).hexdigest(),
        "originalPublishedCommit": "cf125cb03deff658df2922c7b74aed4b530e1b17",
        "records": current, "originalManifestRewritten": False, "originalObservationBytesChanged": False,
        "result": "PASS"})
    progress = load_json(CHECKPOINT / "FULL-VERIFY-PROGRESS.json")
    clone = Path(progress["clone"])
    if progress["subjectCommit"] != "cf125cb03deff658df2922c7b74aed4b530e1b17" or clone.exists():
        raise ValueError("actual interrupted v7 clone must already be gone; no deletion is retried")
    owned = {}
    for kind, command in (
        ("containers", ["docker", "ps", "-a", "--filter", "label=com.docker.compose.project=iacode-verify-eb2b2e1fcd9d", "--format", "{{.ID}}"]),
        ("volumes", ["docker", "volume", "ls", "--filter", "label=com.docker.compose.project=iacode-verify-eb2b2e1fcd9d", "--format", "{{.Name}}"]),
        ("networks", ["docker", "network", "ls", "--filter", "label=com.docker.compose.project=iacode-verify-eb2b2e1fcd9d", "--format", "{{.ID}}"]),
    ):
        owned[kind] = subprocess.check_output(command, timeout=10).decode().splitlines()
        if owned[kind]:
            raise ValueError("owned interruption resources remain; no broad cleanup permitted")
    write_json(CHECKPOINT / "attempts/FULL-VERIFY-INTERRUPTED-0004.json", {
        "kind": "INTENTIONALLY_INTERRUPTED_INCOMPLETE_VERIFICATION_NOT_PASS", "observedAt": utc_now(),
        "subjectCommit": progress["subjectCommit"], "progress": progress,
        "verificationResult": "NOT_COMPLETED", "gateVerdictIssued": False,
        "originalFullCommand": "cmd-0374", "interruptionCommand": "cmd-0373",
        "diagnosticCommand": "cmd-0376", "diagnosticResult": "FAIL", "completedStages": 0,
        "temporaryCloneRemoved": True, "ownedResourcesAfter": owned,
        "terminationLimit": "taskkill returned nonzero and the interruption helper failed before its receipt. Later exact PID observations were absent; original full recorder exited1. Do not infer a successful termination call or replay old PIDs. No before/after shared-project claim exists for this incomplete attempt.",
        "reason": "Original archived Markdown relative links were treated as active documentation; current raw catalog preserves exact bytes and original published locators without weakening active-document validation."})
    print(f"V6_RAW_CATALOG=PASS records={len(current)} original_bytes_changed=false v7_incomplete_no_owned_residue=true")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
