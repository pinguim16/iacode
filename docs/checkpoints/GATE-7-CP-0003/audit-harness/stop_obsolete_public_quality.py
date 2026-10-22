"""Stop only the pinned obsolete quality producer; its existing Job drains its tree.

One historical process identity, never a name/prefix kill or a reusable PID action.
Refuse before any effect unless native creation time, executable, argv and parent match.
"""

import ctypes
import json
import subprocess
import sys
from ctypes import wintypes
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def main():
    if sys.argv[1:] != ["--execute"]:
        raise ValueError("Explicit execution switch required; no broad or inferred target")
    expected_start = datetime.fromisoformat("2026-10-22T00:11:48.795774+00:00")
    expected_parent_start = datetime.fromisoformat("2026-10-22T00:11:06.427410+00:00")
    executable = Path("C:/Program Files/Python313/python.exe")
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
        "8312bb282844dc5d6b5e3e3f7a96f3c77cdbdca9",
        "--tag",
        "iacode-subjects/GATE-7-CP-0003-runtime-v1",
    ]
    command = (
        "$rows = @(Get-CimInstance Win32_Process -Filter 'ProcessId ="
        " 51764'; Get-CimInstance Win32_Process -Filter 'ProcessId = "
        "43492'); $rows | ForEach-Object { [pscustomobject]@{ id=$_.P"
        "rocessId; parent=$_.ParentProcessId; created=$_.CreationDate"
        ".ToUniversalTime().ToString('o'); command=$_.CommandLine } }"
        " | ConvertTo-Json -Compress"
    )
    shell = (
        "C:/Users/cesar/.cache/codex-runtimes/codex-primary-runtime/d"
        "ependencies/native/powershell/pwsh.exe"
    )
    observed = subprocess.run(
        [shell, "-NoProfile", "-Command", command],
        cwd=ROOT,
        capture_output=True,
        timeout=20,
        check=True,
    )
    rows = {row["id"]: row for row in json.loads(observed.stdout)}
    target, parent = rows[51764], rows[43492]
    if (
        target["parent"] != 43492
        or parent["parent"] != 41388
        or target["command"] != subprocess.list2cmdline(expected)
        or parent["command"] != subprocess.list2cmdline(parent_expected)
        or abs((datetime.fromisoformat(target["created"]) - expected_start).total_seconds()) > 0.001
        or abs((datetime.fromisoformat(parent["created"]) - expected_parent_start).total_seconds())
        > 0.001
    ):
        raise ValueError("Pinned historical identity mismatch; no process signaled")
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
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x1001, False, 51764)
    if not handle:
        raise OSError(ctypes.get_last_error(), "Pinned producer handle unavailable; no effect")
    try:
        created, exited, privileged, user = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(
            handle,
            ctypes.byref(created),
            ctypes.byref(exited),
            ctypes.byref(privileged),
            ctypes.byref(user),
        ):
            raise OSError(ctypes.get_last_error(), "Native identity unavailable; no effect")
        ticks = (created.dwHighDateTime << 32) | created.dwLowDateTime
        started = datetime.fromtimestamp(ticks / 10000000 - 11644473600, UTC)
        length = wintypes.DWORD(32768)
        name = ctypes.create_unicode_buffer(length.value)
        if (
            abs((started - expected_start).total_seconds()) > 0.001
            or not kernel.QueryFullProcessImageNameW(handle, 0, name, ctypes.byref(length))
            or Path(name.value) != executable
        ):
            raise ValueError("Native pinned handle differs; no process signaled")
        if not kernel.TerminateProcess(handle, 20):
            raise OSError(ctypes.get_last_error(), "Pinned producer termination refused")
        print(
            json.dumps(
                {
                    "kind": "CONTROLLED_OBSOLETE_QUALITY_CANCELLATION_NOT_TEST_FAILURE_OR_PASS",
                    "producerId": 51764,
                    "producerCreatedAt": started.isoformat(),
                    "requestedExitCode": 20,
                    "nativePinnedIdentityMatched": True,
                    "exactProducerTerminationRequested": True,
                    "descendantCleanupOwner": "Existing run_owned Windows Job Object",
                    "applicationsOrDockerSignaled": False,
                }
            )
        )
    finally:
        if not kernel.CloseHandle(handle):
            raise OSError(ctypes.get_last_error(), "Native controller handle release failed")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
