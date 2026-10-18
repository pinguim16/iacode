"""Actual Win32 held-file deadline and two fresh native hosts; never whole-Gate acceptance."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_native_file_lock import file_api
from ledger_common import find_secrets, scope_fingerprint, use_utf8_stdout, utc_now, write_json
from native_process import owned_directory, remove_owned_directory


def main() -> int:
    if os.name != "nt":
        raise RuntimeError("actual Win32 lock/native proof requires Windows")
    archive = CHECKPOINT / "attempts"
    control_path = archive / "NATIVE-DEADLINE-CONTROL-0001.json"
    if control_path.exists():
        raise ValueError("immutable actual deadline proof already exists; do not replay")
    handle = None
    error = None
    facts = None
    still_present = False
    api = file_api()
    try:
        with owned_directory("iacode-gate6-native-deadline-") as facts:
            path = facts["path"] / "held.log"
            path.write_text("Owned Win32 sharing-lock deadline control.\n", encoding="utf-8")
            handle = api.CreateFileW(str(path), 0x80000000, 1, None, 3, 0x80, None)
            if handle == ctypes.c_void_p(-1).value:
                handle = None
                raise ctypes.WinError(ctypes.get_last_error())
    except PermissionError as observed:
        error = observed
        still_present = bool(facts and facts["path"].is_dir())
    finally:
        if handle is not None and not api.CloseHandle(handle):
            raise ctypes.WinError(ctypes.get_last_error())
    valid = bool(error and getattr(error, "winerror", None) == 32 and facts
                 and still_present and not facts["removed"]
                 and facts["cleanupRetries"] >= 1
                 and facts["cleanupAttempts"] == facts["cleanupRetries"] + 1
                 and facts["cleanupElapsedSeconds"] >= 10
                 and facts["cleanupFailure"]["winerror"] == 32)
    if facts and facts["path"].exists():
        remove_owned_directory(facts["path"], Path(tempfile.gettempdir()).resolve())
    removed = bool(facts and not facts["path"].exists())
    control = {"kind": "ACTUAL_WIN32_DEADLINE_CONTROL_NOT_NATIVE_ACCEPTANCE", "observedAt": utc_now(),
               "expectedFailureRetained": valid, "originalErrorType": type(error).__name__,
               "observed": {key: value for key, value in (facts or {}).items() if key != "path"},
               "ownedFixtureRemovedAfterOwnHandleClosed": removed, "applicationsStopped": 0,
               "result": "PASS" if valid and removed else "FAIL"}
    write_json(control_path, control)
    print(json.dumps(control), flush=True)
    if control["result"] != "PASS":
        return 1
    fingerprint = scope_fingerprint(ROOT)
    for sequence in (1, 2):
        stem = f"NATIVE-CLEANUP-LIVE-{sequence:04d}"
        producer_path = ROOT / "var" / (stem.lower() + ".json")
        destination, receipt_path = archive / (stem + ".json"), archive / (stem + "-RECEIPT.json")
        if destination.exists() or receipt_path.exists() or producer_path.exists():
            raise ValueError("immutable native proof output already exists; do not overwrite")
        completed = subprocess.run([sys.executable, "scripts/iacode/native_editor.py", "--report",
                                    producer_path.relative_to(ROOT).as_posix()], cwd=ROOT,
                                   capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        receipt = {"kind": "LOCAL_ACTUAL_NATIVE_PROOF_NOT_GATE_ACCEPTANCE", "observedAt": utc_now(),
                   "sourceFingerprint": fingerprint, "exitCode": completed.returncode, "result": "FAIL"}
        if producer_path.is_file() and not producer_path.is_symlink():
            raw = producer_path.read_bytes()
            receipt.update({"producerBytes": len(raw), "producerSha256": hashlib.sha256(raw).hexdigest()})
            unsafe = find_secrets(raw.decode("utf-8", "strict"))
            receipt["unsafeOccurrences"] = len(unsafe)
            if not unsafe:
                with destination.open("xb") as output:
                    output.write(raw)
                native = json.loads(raw)
                receipt.update({"producerArchive": destination.relative_to(ROOT).as_posix(),
                                "nativeResult": native.get("result"), "runs": len(native.get("runs", [])),
                                "ownedTemporaryDirectoryRemoved": native.get("ownedTemporaryDirectoryRemoved"),
                                "directoryCleanup": native.get("directoryCleanup"), "failure": native.get("failure")})
                if (completed.returncode == 0 and native.get("result") == "PASS"
                        and native.get("ownedTemporaryDirectoryRemoved") is True
                        and len(native.get("runs", [])) == 2
                        and all(run.get("result") == "PASS" and
                                run.get("processCleanup", {}).get("remainingAfterCleanup") == 0
                                for run in native["runs"])
                        and scope_fingerprint(ROOT) == fingerprint):
                    receipt["result"] = "PASS"
        write_json(receipt_path, receipt)
        print(json.dumps(receipt), flush=True)
        if receipt["result"] != "PASS":
            return 1
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
