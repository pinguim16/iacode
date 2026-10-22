"""One pinned superseded quality producer; its existing Job owns descendant cleanup."""

import ctypes
import json
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import use_utf8_stdout, utc_now, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    if sys.argv[1:] != ["--execute"]:
        raise ValueError("One explicit historical operation only")
    executable = Path("C:/Program Files/Python313/python.exe")
    target_start = datetime.fromisoformat("2026-10-22T03:31:59.332905+00:00")
    parent_start = datetime.fromisoformat("2026-10-22T03:31:23.272258+00:00")
    expected = [
        str(executable),
        "scripts/development-ledger/green_keeper.py",
        "--trigger",
        "Current complete corrective assurance from an exact public transported subject",
        "--root-cause",
        "M2 literal invocation/cleanup evidence and measured adapter/UTF-8 guard corrections",
    ]
    parent_expected = [
        str(executable),
        "docs/checkpoints/GATE-7-CP-0003/audit-harness/run_published_green_keeper.py",
        "--commit",
        "477ec86f09c5e03ad328cf40a3725855b3526bad",
        "--tag",
        "iacode-subjects/GATE-7-CP-0003-runtime-v2",
    ]
    query = (
        "@(Get-CimInstance Win32_Process -Filter 'ProcessId=38840';Ge"
        "t-CimInstance Win32_Process -Filter 'ProcessId=9340')|ForEac"
        "h-Object{[pscustomobject]@{id=$_.ProcessId;parent=$_.ParentP"
        "rocessId;created=$_.CreationDate.ToUniversalTime().ToString("
        "'o');command=$_.CommandLine}}|ConvertTo-Json -Compress"
    )
    shell = (
        "C:/Users/cesar/.cache/codex-runtimes/codex-primary-runtime/d"
        "ependencies/native/powershell/pwsh.exe"
    )
    result = subprocess.run(
        [shell, "-NoProfile", "-Command", query],
        cwd=ROOT,
        capture_output=True,
        timeout=20,
        check=True,
    )
    rows = {row["id"]: row for row in json.loads(result.stdout)}
    target, parent = rows[38840], rows[9340]
    if (
        target["parent"] != 9340
        or parent["parent"] != 39032
        or target["command"] != subprocess.list2cmdline(expected)
        or parent["command"] != subprocess.list2cmdline(parent_expected)
        or datetime.fromisoformat(target["created"]) != target_start
        or datetime.fromisoformat(parent["created"]) != parent_start
    ):
        raise ValueError("Historical native producer/parent mismatch; no signal")
    output = CHECKPOINT / "published-green-keeper/run-0002/CONTROLLED-CANCELLATION.json"
    if output.exists():
        raise ValueError("Do not repeat this historical cancellation")
    fact = {
        "recordedAt": utc_now(),
        "kind": "CONTROLLED_SUPERSEDED_CYCLE_NOT_TEST_VERDICT",
        "reason": (
            "PRE-PUSH-LINT-001: runtime-v2 was published before current w"
            "hole lint; repair publication preconditions and run fresh co"
            "mplete assurance."
        ),
        "subjectCommit": "477ec86f09c5e03ad328cf40a3725855b3526bad",
        "producerId": 38840,
        "producerCreatedAt": target_start.isoformat(),
        "requestedExitCode": 20,
        "dockerEngineSignaled": False,
        "preexistingApplicationsSignaled": False,
        "descendantCleanupOwner": (
            "Existing run_owned Windows Job; actual wrapper completion remains required"
        ),
    }
    write_json(output, fact)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *[ctypes.POINTER(wintypes.FILETIME)] * 4]
    kernel.GetProcessTimes.restype = wintypes.BOOL
    kernel.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.TerminateProcess.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x101001, False, 38840)
    if not handle:
        raise OSError(ctypes.get_last_error(), "Pinned producer handle unavailable")
    try:
        times = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *[ctypes.byref(value) for value in times]):
            raise OSError(ctypes.get_last_error(), "Pinned creation time unavailable")
        ticks = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
        delta = target_start - datetime(1601, 1, 1, tzinfo=UTC)
        expected_us = (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds
        length = wintypes.DWORD(32768)
        name = ctypes.create_unicode_buffer(length.value)
        if (
            ticks // 10 != expected_us
            or not kernel.QueryFullProcessImageNameW(handle, 0, name, ctypes.byref(length))
            or Path(name.value) != executable
        ):
            raise ValueError("Native pinned handle mismatch; no signal")
        if (
            not kernel.TerminateProcess(handle, 20)
            or kernel.WaitForSingleObject(handle, 10000) != 0
        ):
            raise OSError(ctypes.get_last_error(), "Pinned producer exit not observed")
    finally:
        if not kernel.CloseHandle(handle):
            raise OSError(ctypes.get_last_error(), "Pinned controller release failed")
    deadline = time.monotonic() + 40
    purpose = (
        "Execute-all-canonical-mandatory-quality-gates-from-exact-pub"
        "lic-runtime-v2-with-original-observations"
    )
    while time.monotonic() < deadline:
        records = [
            json.loads(line)
            for line in (CHECKPOINT / "COMMANDS.jsonl").read_bytes().splitlines()
            if line
        ]
        if any(row.get("purpose") == purpose for row in records):
            break
        time.sleep(0.2)
    else:
        raise ValueError("Actual wrapper recorder exit not observed")
    fact.update(exactNativeIdentityMatched=True, exactProducerExitObserved=True)
    write_json(output, fact)
    print(
        json.dumps(
            {
                "kind": fact["kind"],
                "exactProducerExitObserved": True,
                "nativePinnedIdentityMatched": True,
                "dockerEngineSignaled": False,
                "preexistingApplicationsSignaled": False,
                "requestedExitCode": 20,
            }
        )
    )
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
