"""Read-only Restart Manager diagnosis of two exact failed owned native profiles."""

import ctypes
import json
from ctypes import wintypes
from pathlib import Path


class UniqueProcess(ctypes.Structure):
    _fields_ = [("pid", wintypes.DWORD), ("started", wintypes.FILETIME)]


class ProcessInfo(ctypes.Structure):
    _fields_ = [("process", UniqueProcess), ("name", wintypes.WCHAR * 256),
                ("service", wintypes.WCHAR * 64), ("type", ctypes.c_int),
                ("status", wintypes.ULONG), ("session", wintypes.DWORD),
                ("restartable", wintypes.BOOL)]


def main():
    api = ctypes.WinDLL("rstrtmgr", use_last_error=True)
    handle = wintypes.DWORD()
    key = ctypes.create_unicode_buffer(33)
    if api.RmStartSession(ctypes.byref(handle), 0, key):
        raise RuntimeError("Restart Manager session unavailable")
    try:
        paths = [str(Path("C:/Users/cesar/AppData/Local/Temp") / relative) for relative in (
            "iacode-native-editor-2hzp2ekf/package/profile/Dictionaries/en-US-10-1.bdic",
            "iacode-native-editor-aorj2q1p/untrusted/profile/Dictionaries/en-US-10-1.bdic")]
        files = (wintypes.LPCWSTR * len(paths))(*paths)
        error = api.RmRegisterResources(handle, len(paths), files, 0, None, 0, None)
        if error:
            raise OSError(error, "owned dictionary registration failed")
        required, count, reason = wintypes.UINT(), wintypes.UINT(), wintypes.DWORD()
        error = api.RmGetList(handle, ctypes.byref(required), ctypes.byref(count), None, ctypes.byref(reason))
        if error not in (0, 234):
            raise OSError(error, "lock enumeration failed")
        count.value = required.value
        processes = (ProcessInfo * count.value)()
        error = api.RmGetList(handle, ctypes.byref(required), ctypes.byref(count), processes, ctypes.byref(reason))
        if error:
            raise OSError(error, "lock enumeration changed")
        print(json.dumps({"ownedFiles": paths, "lockingProcesses": [
            {"pid": row.process.pid, "name": row.name, "service": row.service}
            for row in processes[:count.value]]}))
    finally:
        api.RmEndSession(handle)


if __name__ == "__main__":
    main()
