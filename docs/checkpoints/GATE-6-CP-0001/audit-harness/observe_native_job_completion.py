"""Read only exact owned job members across termination; diagnostic, never acceptance."""

from __future__ import annotations

import ctypes
import hashlib
import json
import subprocess
import sys
from ctypes import wintypes
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from ledger_common import find_secrets, use_utf8_stdout, utc_now, write_json
import native_editor
import native_process


class Members(ctypes.Structure):
    _fields_ = [("assigned", wintypes.DWORD), ("listed", wintypes.DWORD),
                ("identifiers", ctypes.c_size_t * 4096)]


def child(sequence: int) -> int:
    stem = f"NATIVE-JOB-COMPLETION-{sequence:04d}"
    destination = CHECKPOINT / "attempts" / (stem + ".json")
    raw_destination = CHECKPOINT / "attempts" / (stem + "-PRODUCER.json")
    producer = ROOT / "var" / (stem.lower() + ".json")
    if any(path.exists() for path in (destination, raw_destination, producer)):
        raise ValueError("immutable job observation exists; do not replay")
    original = native_process.WindowsJob.close
    records, opened = [], []
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    for name, arguments, result in (
        ("OpenProcess", [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
        ("IsProcessInJob", [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)], wintypes.BOOL),
        ("WaitForSingleObject", [wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
        ("CloseHandle", [wintypes.HANDLE], wintypes.BOOL),
    ):
        getattr(api, name).argtypes, getattr(api, name).restype = arguments, result

    def observe(job):
        members = Members()
        if not job.api.QueryInformationJobObject(job.handle, 3, ctypes.byref(members),
                                                  ctypes.sizeof(members), None):
            raise ctypes.WinError(ctypes.get_last_error())
        record = {"observedAt": utc_now(), "assignedBefore": members.assigned,
                  "listedBefore": members.listed, "members": []}
        for pid in members.identifiers[:members.listed]:
            handle = api.OpenProcess(0x100000 | 0x1000, False, pid)
            if not handle:
                record["members"].append({"pid": pid, "openError": ctypes.get_last_error()})
                continue
            opened.append(handle)
            contained = wintypes.BOOL()
            if not api.IsProcessInJob(handle, job.handle, ctypes.byref(contained)):
                raise ctypes.WinError(ctypes.get_last_error())
            row = {"pid": pid, "ownedMembershipObserved": bool(contained.value),
                   "waitBefore": api.WaitForSingleObject(handle, 0), "handle": handle}
            record["members"].append(row)
        result = original(job)
        record["originalCloseResult"] = result
        for row in record["members"]:
            if "handle" in row:
                row["waitImmediatelyAfterOriginalClose"] = api.WaitForSingleObject(row["handle"], 0)
        records.append(record)
        return result

    native_process.WindowsJob.close = observe
    try:
        sys.argv = ["native_editor.py", "--report", str(producer)]
        native_exit = native_editor.main()
    finally:
        native_process.WindowsJob.close = original
        for record in records:
            for row in record["members"]:
                handle = row.pop("handle", None)
                if handle is not None:
                    row["waitAfterNativeReport"] = api.WaitForSingleObject(handle, 0)
        for handle in opened:
            if not api.CloseHandle(handle):
                raise ctypes.WinError(ctypes.get_last_error())
    raw = producer.read_bytes()
    if find_secrets(raw.decode("utf-8", "strict")):
        raise RuntimeError("unsafe native producer refused")
    with raw_destination.open("xb") as output:
        output.write(raw)
    document = json.loads(raw)
    mismatch = any(row.get("ownedMembershipObserved") and row.get("waitImmediatelyAfterOriginalClose") == 258
                   for record in records for row in record["members"])
    report = {"kind": "ACTUAL_JOB_COMPLETION_OBSERVATION_NOT_ACCEPTANCE", "observedAt": utc_now(),
              "nativeExitCode": native_exit, "nativeResult": document.get("result"),
              "directoryCleanup": document.get("directoryCleanup"), "jobObservations": records,
              "zeroAccountingWithUnsignaledOwnedMemberObserved": mismatch,
              "externalProcessesStopped": 0, "gateVerdictIssued": False,
              "producerArchive": raw_destination.relative_to(ROOT).as_posix(),
              "producerSha256": hashlib.sha256(raw).hexdigest()}
    write_json(destination, report)
    print(json.dumps(report), flush=True)
    return 0 if mismatch else 1


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--child":
        return child(int(sys.argv[2]))
    for sequence in (1, 2):
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child", str(sequence)],
                                   cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        path = CHECKPOINT / "attempts" / f"NATIVE-JOB-COMPLETION-{sequence:04d}.json"
        if not path.is_file():
            print(json.dumps({"childExitCode": completed.returncode, "diagnosticPresent": False,
                              "outputTail": (completed.stdout + completed.stderr)[-2000:]}))
            return 1
        report = json.loads(path.read_bytes())
        print(json.dumps(report), flush=True)
        if report["zeroAccountingWithUnsignaledOwnedMemberObserved"]:
            return 0
        if report["nativeExitCode"]:
            return 1
    print("JOB_COMPLETION_DIAGNOSIS=NOT_REPRODUCED; no repair or Gate verdict inferred")
    return 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
