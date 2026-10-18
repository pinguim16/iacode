"""Recover only the exact failed native fixture after current non-deleting lock inspection."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_native_file_lock import delete_access, owners, retained_target
from ledger_common import load_json, use_utf8_stdout, utc_now, write_json
from native_process import remove_owned_directory


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    destination = CHECKPOINT / "attempts/NATIVE-RETAINED-CLEANUP-0001.json"
    if destination.exists():
        raise ValueError("immutable cleanup receipt already exists; do not replay")
    inspection = load_json(CHECKPOINT / "attempts/NATIVE-LOCK-INSPECTION-0001.json")
    if not inspection.get("controlValid") or inspection.get("applicationsStopped") != 0:
        raise ValueError("actual read-only positive/released handle controls are required")
    target = retained_target()
    temporary = Path(tempfile.gettempdir()).resolve()
    directory = temporary / "iacode-native-editor-s0gh5exk"
    if (directory.resolve() != directory or directory.parent != temporary
            or directory.is_symlink() or directory.is_junction() or not directory.is_dir()
            or not target.is_relative_to(directory) or not target.is_file()):
        raise ValueError("exact retained native owner is absent or redirected")
    observed_owners, access = owners(target), delete_access(target)
    if observed_owners or not access["available"]:
        raise RuntimeError("retained file is still owned/locked; no process will be stopped")
    native_report = CHECKPOINT / "RED-TEAM-NATIVE.json"
    report_hash, log_hash = digest(native_report), digest(target)
    implementation_hash = digest(ROOT / "scripts/iacode/native_process.py")
    retries = remove_owned_directory(directory, temporary)
    removed = not directory.exists()
    if not removed or digest(native_report) != report_hash:
        raise RuntimeError("actual removal or unchanged original failure evidence was not observed")
    receipt = {"kind": "SCOPED_NATIVE_FIXTURE_RECOVERY_NOT_ACCEPTANCE", "observedAt": utc_now(),
               "originalFailureCommand": "cmd-0258", "target": str(directory),
               "validatedTemporaryParent": str(temporary), "originalReportSha256": report_hash,
               "originalLogSha256Only": log_hash, "originalLogBytesRetained": False,
               "cleanupImplementationSha256": implementation_hash,
               "currentOwners": observed_owners, "currentDeleteAccess": access,
               "removed": removed, "cleanupRetries": retries, "applicationsStopped": 0,
               "originalFailureRewritten": False, "result": "PASS"}
    write_json(destination, receipt)
    print(json.dumps(receipt))
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
