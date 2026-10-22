"""Read native identities of only this publication's launchers; never signal a process."""

from __future__ import annotations

import base64
import ctypes
import hashlib
import json
from ctypes import wintypes
from datetime import UTC, datetime, timedelta
from pathlib import Path


class ProcessEntry(ctypes.Structure):
    _fields_ = [
        ("size", wintypes.DWORD),
        ("usage", wintypes.DWORD),
        ("pid", wintypes.DWORD),
        ("heap", ctypes.c_size_t),
        ("module", wintypes.DWORD),
        ("threads", wintypes.DWORD),
        ("parent", wintypes.DWORD),
        ("priority", wintypes.LONG),
        ("flags", wintypes.DWORD),
        ("name", wintypes.WCHAR * 260),
    ]


class UnicodeString(ctypes.Structure):
    _fields_ = [
        ("length", wintypes.USHORT),
        ("maximum", wintypes.USHORT),
        ("buffer", ctypes.c_void_p),
    ]


def main():
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    ntdll = ctypes.WinDLL("ntdll")
    declarations = {
        "CreateToolhelp32Snapshot": ([wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
        "Process32FirstW": ([wintypes.HANDLE, ctypes.POINTER(ProcessEntry)], wintypes.BOOL),
        "Process32NextW": ([wintypes.HANDLE, ctypes.POINTER(ProcessEntry)], wintypes.BOOL),
        "OpenProcess": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
        "GetProcessTimes": (
            [wintypes.HANDLE, *[ctypes.POINTER(wintypes.FILETIME)] * 4],
            wintypes.BOOL,
        ),
        "QueryFullProcessImageNameW": (
            [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)],
            wintypes.BOOL,
        ),
        "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
    }
    for name, (arguments, result) in declarations.items():
        function = getattr(kernel, name)
        function.argtypes, function.restype = arguments, result
    query = ntdll.NtQueryInformationProcess
    query.argtypes = [
        wintypes.HANDLE,
        wintypes.ULONG,
        ctypes.c_void_p,
        wintypes.ULONG,
        ctypes.POINTER(wintypes.ULONG),
    ]
    query.restype = wintypes.LONG
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    matches, refused, process_tree = [], [], []
    try:
        entry = ProcessEntry()
        entry.size = ctypes.sizeof(entry)
        available = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while available:
            process_tree.append({"pid": entry.pid, "parentPid": entry.parent, "name": entry.name})
            if entry.name.lower() in {"python.exe", "powershell.exe", "pwsh.exe"}:
                handle = kernel.OpenProcess(0x1000, False, entry.pid)
                if handle:
                    try:
                        buffer = ctypes.create_string_buffer(1024 * 1024)
                        returned = wintypes.ULONG()
                        status = query(handle, 60, buffer, len(buffer), ctypes.byref(returned))
                        if status < 0:
                            refused.append({"pid": entry.pid, "reason": "COMMAND_QUERY_REFUSED"})
                        else:
                            value = UnicodeString.from_buffer(buffer)
                            start, end = (
                                ctypes.addressof(buffer),
                                ctypes.addressof(buffer) + len(buffer),
                            )
                            if (
                                value.length % 2
                                or value.length > value.maximum
                                or not start <= value.buffer <= value.buffer + value.length <= end
                            ):
                                raise ValueError("Native returned command buffer bounds invalid")
                            command = ctypes.wstring_at(value.buffer, value.length // 2)
                            inspected = command
                            # Native shell invocations can carry an encoded command. Decode only
                            # a bounded shell argument for matching; never print private bodies.
                            tokens = command.split()
                            for index, token in enumerate(tokens[:-1]):
                                if token.lower() in {"-encodedcommand", "-enc", "-e"}:
                                    try:
                                        inspected += "\n" + base64.b64decode(
                                            tokens[index + 1], validate=True
                                        ).decode("utf-16-le")
                                    except (ValueError, UnicodeError):
                                        refused.append(
                                            {"pid": entry.pid, "reason": "ENCODING_REFUSED"}
                                        )
                            if "publish_progress.py" in inspected and "runtime-v5" in inspected:
                                times = [wintypes.FILETIME() for _ in range(4)]
                                if not kernel.GetProcessTimes(
                                    handle, *[ctypes.byref(item) for item in times]
                                ):
                                    raise ctypes.WinError(ctypes.get_last_error())
                                ticks = times[0].dwLowDateTime | times[0].dwHighDateTime << 32
                                executable = ctypes.create_unicode_buffer(32768)
                                length = wintypes.DWORD(len(executable))
                                if not kernel.QueryFullProcessImageNameW(
                                    handle, 0, executable, ctypes.byref(length)
                                ):
                                    raise ctypes.WinError(ctypes.get_last_error())
                                matches.append(
                                    {
                                        "pid": entry.pid,
                                        "parentPid": entry.parent,
                                        "creationFileTime": ticks,
                                        "creationUtc": (
                                            datetime(1601, 1, 1, tzinfo=UTC)
                                            + timedelta(microseconds=ticks // 10)
                                        ).isoformat(),
                                        "executable": executable.value,
                                        "commandSha256": hashlib.sha256(
                                            command.encode()
                                        ).hexdigest(),
                                        "role": (
                                            "PUBLICATION_LAUNCHER"
                                            if "--execute" in inspected
                                            and "--runtime-tag" in inspected
                                            and "Get-CimInstance" not in inspected
                                            else "READ_ONLY_QUERY"
                                            if "Get-CimInstance" in inspected
                                            else "AMBIGUOUS_REFUSE_SIGNAL"
                                        ),
                                        "literalPublicationAndTagMatched": True,
                                    }
                                )
                    finally:
                        kernel.CloseHandle(handle)
                else:
                    refused.append({"pid": entry.pid, "reason": "READ_HANDLE_REFUSED"})
            available = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    for row in matches:
        descendants = {row["pid"]}
        while True:
            observed = descendants | {
                item["pid"] for item in process_tree if item["parentPid"] in descendants
            }
            if observed == descendants:
                break
            descendants = observed
        row["observedDescendants"] = [
            item for item in process_tree if item["pid"] in descendants - {row["pid"]}
        ]
    print(
        json.dumps(
            {
                "kind": "READ_ONLY_NATIVE_LAUNCHER_IDENTITIES_NOT_TERMINATION_AUTHORITY",
                "matches": matches,
                "refused": refused,
                "processesSignaled": 0,
                "historicalTaskProcessEntries": [
                    item for item in process_tree if item["pid"] in {46028, 50960, 34724, 46808}
                ],
                "source": str(Path(__file__).resolve()),
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
