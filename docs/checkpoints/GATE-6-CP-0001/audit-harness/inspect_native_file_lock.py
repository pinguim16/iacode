"""Inspect only the retained native failure; no application stop/restart or deletion API."""

from __future__ import annotations

import ast
import ctypes
import json
import os
import re
import sys
import tempfile
from ctypes import wintypes
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from ledger_common import load_json, use_utf8_stdout, utc_now, write_json
from native_process import owned_directory

# SDK layout and read-only list contract:
# https://learn.microsoft.com/en-us/windows/win32/api/restartmanager/nf-restartmanager-rmgetlist
# https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/RestartManager.h
class UniqueProcess(ctypes.Structure):
    _fields_ = [("pid", wintypes.DWORD), ("started", wintypes.FILETIME)]


class ProcessInfo(ctypes.Structure):
    _fields_ = [("process", UniqueProcess), ("application", wintypes.WCHAR * 256),
                ("service", wintypes.WCHAR * 64), ("kind", ctypes.c_int),
                ("status", wintypes.ULONG), ("session", wintypes.DWORD),
                ("restartable", wintypes.BOOL)]


def owners(path: Path) -> list[dict]:
    """Register one owned file, list PID/creation identities, end the advisory session."""
    api = ctypes.WinDLL("Rstrtmgr", use_last_error=True)
    signatures = {
        "RmStartSession": ([ctypes.POINTER(wintypes.DWORD), wintypes.DWORD, wintypes.LPWSTR], wintypes.DWORD),
        "RmRegisterResources": ([wintypes.DWORD, ctypes.c_uint, ctypes.POINTER(wintypes.LPCWSTR),
                                  ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p], wintypes.DWORD),
        "RmGetList": ([wintypes.DWORD, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint),
                        ctypes.POINTER(ProcessInfo), ctypes.POINTER(wintypes.DWORD)], wintypes.DWORD),
        "RmEndSession": ([wintypes.DWORD], wintypes.DWORD),
    }
    for name, (arguments, result) in signatures.items():
        function = getattr(api, name)
        function.argtypes, function.restype = arguments, result
    handle, key = wintypes.DWORD(), ctypes.create_unicode_buffer(33)
    code = api.RmStartSession(ctypes.byref(handle), 0, key)
    if code:
        raise ctypes.WinError(code)
    try:
        files = (wintypes.LPCWSTR * 1)(str(path))
        code = api.RmRegisterResources(handle, 1, files, 0, None, 0, None)
        if code:
            raise ctypes.WinError(code)
        size = 0
        for _ in range(4):
            needed, count, reasons = ctypes.c_uint(), ctypes.c_uint(size), wintypes.DWORD()
            buffer = (ProcessInfo * size)() if size else None
            code = api.RmGetList(handle, ctypes.byref(needed), ctypes.byref(count), buffer,
                                 ctypes.byref(reasons))
            if code == 234:
                if not 0 < needed.value <= 256:
                    raise RuntimeError("owner-list bound refused")
                size = needed.value
                continue
            if code:
                raise ctypes.WinError(code)
            return [{"pid": row.process.pid,
                     "creationFileTime": (row.process.started.dwHighDateTime << 32)
                                         | row.process.started.dwLowDateTime,
                     "application": row.application, "service": row.service,
                     "applicationType": row.kind} for row in (buffer or [])[:count.value]]
        raise RuntimeError("owner list changed beyond bounded inspection")
    finally:
        code = api.RmEndSession(handle)
        if code:
            raise ctypes.WinError(code)


def file_api():
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                               ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    api.CreateFileW.restype = wintypes.HANDLE
    api.CloseHandle.argtypes, api.CloseHandle.restype = [wintypes.HANDLE], wintypes.BOOL
    return api


def delete_access(path: Path) -> dict:
    # DELETE access only, OPEN_EXISTING, no delete-on-close flag: no content or path is removed.
    api = file_api()
    handle = api.CreateFileW(str(path), 0x10000, 7, None, 3, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        return {"available": False, "winerror": ctypes.get_last_error(), "deleted": False}
    if not api.CloseHandle(handle):
        raise ctypes.WinError(ctypes.get_last_error())
    return {"available": True, "winerror": None, "deleted": False}


def retained_target() -> Path:
    report = load_json(CHECKPOINT / "RED-TEAM-NATIVE.json")
    failure = report.get("failure", "")
    match = re.search(r": ('.*')$", failure)
    if report.get("result") != "FAIL" or "WinError 32" not in failure or not match:
        raise ValueError("the actual retained native sharing-lock failure is required")
    path = Path(ast.literal_eval(match.group(1)))
    temporary = Path(tempfile.gettempdir()).resolve()
    expected = temporary / "iacode-native-editor-s0gh5exk"
    if not path.resolve().is_relative_to(expected) or expected.parent != temporary:
        raise ValueError("retained observation is outside its exact created native owner")
    for part in (path, *path.parents):
        if part == temporary:
            break
        if part.is_symlink() or part.is_junction():
            raise ValueError("redirected retained file refused")
    return path.resolve()


def main() -> int:
    if os.name != "nt":
        raise RuntimeError("this actual Win32 diagnostic requires Windows")
    output = CHECKPOINT / "attempts/NATIVE-LOCK-INSPECTION-0001.json"
    if output.exists():
        raise ValueError("immutable diagnostic already exists; do not replay")
    with owned_directory("iacode-native-lock-inspection-") as control:
        path = control["path"] / "control.log"
        path.write_text("Owned handle inspection control.\n", encoding="utf-8")
        api = file_api()
        handle = api.CreateFileW(str(path), 0x80000000, 1, None, 3, 0x80, None)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            held, held_delete = owners(path), delete_access(path)
        finally:
            if not api.CloseHandle(handle):
                raise ctypes.WinError(ctypes.get_last_error())
        released, released_delete = owners(path), delete_access(path)
        valid = (any(row["pid"] == os.getpid() for row in held)
                 and all(row["pid"] != os.getpid() for row in released)
                 and held_delete["winerror"] == 32 and released_delete["available"])
        if not valid:
            raise RuntimeError("actual positive/released handle control is invalid")
    target = retained_target()
    current = {"path": str(target), "exists": target.is_file(), "owners": [], "deleteAccess": None}
    if target.is_file():
        current.update({"owners": owners(target), "deleteAccess": delete_access(target)})
    report = {"kind": "READ_ONLY_HANDLE_INSPECTION_NOT_GATE_ACCEPTANCE", "observedAt": utc_now(),
              "originalFailureCommand": "cmd-0258", "controlValid": valid,
              "controlOwnedDirectoryRemoved": control["removed"],
              "controlCleanupRetries": control["cleanupRetries"],
              "heldControl": held, "heldDeleteAccess": held_delete,
              "releasedControl": released, "releasedDeleteAccess": released_delete,
              "retainedFailureFile": current, "applicationsStopped": 0,
              "originalDirectoryDeleted": False, "result": "PASS"}
    write_json(output, report)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
