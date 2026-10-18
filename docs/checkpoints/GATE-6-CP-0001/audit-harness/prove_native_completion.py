"""Require two actual uninstrumented native proofs and retain every original producer."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets, scope_fingerprint, use_utf8_stdout, utc_now, write_json


def main() -> int:
    fingerprint = scope_fingerprint(ROOT)
    for sequence in (1, 2):
        stem = f"NATIVE-COMPLETION-PROOF-{sequence:04d}"
        producer = ROOT / "var" / (stem.lower() + ".json")
        destination = CHECKPOINT / "attempts" / (stem + ".json")
        receipt_path = CHECKPOINT / "attempts" / (stem + "-RECEIPT.json")
        if any(path.exists() for path in (producer, destination, receipt_path)):
            raise ValueError("immutable completion proof exists; do not replay")
        completed = subprocess.run([sys.executable, "scripts/iacode/native_editor.py", "--report",
                                    producer.relative_to(ROOT).as_posix()], cwd=ROOT,
                                   capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        receipt = {"kind": "LOCAL_ACTUAL_NATIVE_COMPLETION_NOT_GATE_ACCEPTANCE", "observedAt": utc_now(),
                   "sourceFingerprint": fingerprint, "exitCode": completed.returncode, "result": "FAIL"}
        if producer.is_file() and not producer.is_symlink():
            raw = producer.read_bytes()
            receipt.update({"producerBytes": len(raw), "producerSha256": hashlib.sha256(raw).hexdigest()})
            unsafe = find_secrets(raw.decode("utf-8", "strict"))
            receipt["unsafeOccurrences"] = len(unsafe)
            if not unsafe:
                with destination.open("xb") as output:
                    output.write(raw)
                native = json.loads(raw)
                cleanups = [cleanup for run in native.get("runs", []) for cleanup in
                            (run.get("processCleanup", {}), run.get("installation", {}).get("processCleanup", {}))]
                complete = bool(cleanups) and all(
                    row.get("jobOwned") is True and row.get("remainingAfterCleanup") == 0
                    and type(row.get("observedProcessCount")) is int
                    and row.get("observedProcessCount") == row.get("signaledProcessCount")
                    for row in cleanups)
                receipt.update({"producerArchive": destination.relative_to(ROOT).as_posix(),
                                "nativeResult": native.get("result"), "runs": len(native.get("runs", [])),
                                "ownedTemporaryDirectoryRemoved": native.get("ownedTemporaryDirectoryRemoved"),
                                "directoryCleanup": native.get("directoryCleanup"),
                                "allObservedOwnedMembersSignaled": complete, "failure": native.get("failure")})
                if (completed.returncode == 0 and native.get("result") == "PASS" and complete
                        and native.get("ownedTemporaryDirectoryRemoved") is True
                        and len(native.get("runs", [])) == 2
                        and all(row.get("result") == "PASS" for row in native["runs"])
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
