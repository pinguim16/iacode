"""Recover only the second retained failed native owner after current read-only lock checks."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_native_file_lock import delete_access, owners
from ledger_common import load_json, use_utf8_stdout, utc_now, write_json
from native_process import remove_owned_directory


def main() -> int:
    receipt_path = CHECKPOINT / "attempts/NATIVE-RETAINED-CLEANUP-0002.json"
    if receipt_path.exists():
        raise ValueError("immutable second cleanup receipt exists; do not replay")
    report_path = CHECKPOINT / "attempts/NATIVE-CLEANUP-LIVE-0001.json"
    original = report_path.read_bytes()
    report = json.loads(original)
    match = re.search(r": ('.*')$", report.get("failure", ""))
    if report.get("result") != "FAIL" or not match or report.get("directoryCleanup", {}).get("cleanupFailure", {}).get("winerror") != 32:
        raise ValueError("the exact retained deadline failure is required")
    target = Path(ast.literal_eval(match.group(1))).resolve()
    temporary = Path(tempfile.gettempdir()).resolve()
    directory = temporary / "iacode-native-editor-vu7u7fpg"
    if directory.resolve() != directory or directory.parent != temporary or not directory.is_dir() or not target.is_relative_to(directory):
        raise ValueError("exact second retained fixture is absent or outside temporary parent")
    for part in (target, *target.parents):
        if part == temporary:
            break
        if part.is_symlink() or part.is_junction():
            raise ValueError("redirected retained fixture refused")
    control = load_json(CHECKPOINT / "attempts/NATIVE-LOCK-INSPECTION-0001.json")
    if not control["controlValid"] or not target.is_file():
        raise ValueError("positive/released actual handle controls and retained file are required")
    current, access = owners(target), delete_access(target)
    if current or not access["available"]:
        raise RuntimeError("the exact failed file is still held; no process will be stopped")
    log_digest = hashlib.sha256(target.read_bytes()).hexdigest()
    facts = {}
    retries = remove_owned_directory(directory, temporary, observation=facts)
    if directory.exists() or report_path.read_bytes() != original:
        raise RuntimeError("actual removal or unchanged original failure was not observed")
    receipt = {"kind": "SCOPED_NATIVE_FIXTURE_RECOVERY_NOT_ACCEPTANCE", "observedAt": utc_now(),
               "originalFailureCommand": "cmd-0269", "target": str(directory),
               "validatedTemporaryParent": str(temporary), "originalReportSha256": hashlib.sha256(original).hexdigest(),
               "originalLogSha256Only": log_digest, "originalLogBytesRetained": False,
               "currentOwners": current, "currentDeleteAccess": access, "cleanupObservation": facts,
               "removed": True, "cleanupRetries": retries, "applicationsStopped": 0,
               "originalFailureRewritten": False, "result": "PASS"}
    write_json(receipt_path, receipt)
    print(json.dumps(receipt), flush=True)
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
