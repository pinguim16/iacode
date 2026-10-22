"""One historical CLI-plugin drain; never a reusable PID/name or engine operation."""

import ctypes
import json
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import UTC, datetime
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import use_utf8_stdout


def main():
    if sys.argv[1:] != ["--execute"]:
        raise ValueError("One explicit historical operation only")
    expected_start = datetime.fromisoformat("2026-10-22T03:04:58.502079+00:00")
    executable = Path("C:/Program Files/Docker/cli-plugins/docker-buildx.exe")
    builder = "iacode-m2cp3-61bb7b6040b746f89d25f24580762b3c"
    expected_argv = [str(executable), "buildx", "inspect", builder, "--bootstrap"]
    query = "$p=Get-CimInstance Win32_Process -Filter 'ProcessId=35632'; if($null -eq $p){throw 'Historical target absent'}; [pscustomobject]@{id=$p.ProcessId;parent=$p.ParentProcessId;created=$p.CreationDate.ToUniversalTime().ToString('o');command=$p.CommandLine}|ConvertTo-Json -Compress"
    shell = "C:/Users/cesar/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe"
    result = subprocess.run([shell, "-NoProfile", "-Command", query], cwd=ROOT,
                            capture_output=True, timeout=20, check=True)
    row = json.loads(result.stdout)
    if (row["id"] != 35632 or row["parent"] != 43800
            or row["command"] != subprocess.list2cmdline(expected_argv)
            or datetime.fromisoformat(row["created"]) != expected_start):
        raise ValueError("Historical plugin identity mismatch; no signal")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *[ctypes.POINTER(wintypes.FILETIME)] * 4]
    kernel.GetProcessTimes.restype = wintypes.BOOL
    kernel.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                                ctypes.POINTER(wintypes.DWORD)]
    kernel.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.TerminateProcess.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x101001, False, 35632)
    if not handle:
        raise OSError(ctypes.get_last_error(), "Historical native handle unavailable")
    try:
        times = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *[ctypes.byref(value) for value in times]):
            raise OSError(ctypes.get_last_error(), "Native creation identity unavailable")
        ticks = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
        delta = expected_start - datetime(1601, 1, 1, tzinfo=UTC)
        expected_microseconds = (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds
        length = wintypes.DWORD(32768)
        name = ctypes.create_unicode_buffer(length.value)
        if (ticks // 10 != expected_microseconds
                or not kernel.QueryFullProcessImageNameW(handle, 0, name, ctypes.byref(length))
                or Path(name.value) != executable):
            raise ValueError("Pinned native identity mismatch; no signal")
        if not kernel.TerminateProcess(handle, 20):
            raise OSError(ctypes.get_last_error(), "Exact CLI helper termination refused")
        if kernel.WaitForSingleObject(handle, 10000) != 0:
            raise ValueError("Exact helper exit was not observed")
    finally:
        if not kernel.CloseHandle(handle):
            raise OSError(ctypes.get_last_error(), "Controller handle release failed")
    # Serialize ledger completion with the old parent before our enclosing recorder appends.
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        rows = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_bytes().splitlines() if line]
        if any(value.get("purpose") == "Start-only-the-new-exact-private-builder-and-preserve-its-actual-producer-streams"
               for value in rows):
            break
        time.sleep(.2)
    else:
        raise ValueError("Old parent recorder completion not observed")
    print(json.dumps({"kind": "PINNED_OWNED_CLI_DRAIN_NOT_ACCEPTANCE", "pluginId": 35632,
        "createdAt": expected_start.isoformat(), "exactNativeIdentityMatched": True,
        "exactPluginExitObserved": True, "dockerEngineSignaled": False,
        "preexistingApplicationsSignaled": False, "requestedExitCode": 20}))
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
