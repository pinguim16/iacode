"""Contain only an owned Windows acceptance process tree in a kill-on-close Job Object."""

from __future__ import annotations

import ctypes
import shutil
import tempfile
import time
from contextlib import contextmanager
from ctypes import wintypes
from pathlib import Path


def remove_owned_directory(directory: Path, temporary_root: Path) -> int:
    """Bounded sharing-lock retry, never a skipped cleanup or an unvalidated broad target."""
    expected = temporary_root.resolve() / directory.name
    if (
        not directory.name.startswith("iacode-")
        or directory.is_symlink()
        or directory.is_junction()
        or directory.resolve() != expected
        or expected.parent != temporary_root.resolve()
    ):
        raise ValueError("refusing an unowned or redirected temporary directory")
    deadline = time.monotonic() + 10
    retries = 0
    while directory.exists():
        try:
            shutil.rmtree(directory)
        except PermissionError as error:
            if getattr(error, "winerror", None) not in (5, 32) or time.monotonic() >= deadline:
                raise
            retries += 1
            time.sleep(0.1)
    return retries


@contextmanager
def owned_directory(prefix: str):
    if not prefix.startswith("iacode-") or any(char in prefix for char in "/\\"):
        raise ValueError("owned temporary prefix required")
    temporary_root = Path(tempfile.gettempdir()).resolve()
    directory = Path(tempfile.mkdtemp(prefix=prefix, dir=temporary_root))
    facts = {"path": directory, "cleanupRetries": None, "removed": False}
    try:
        yield facts
    finally:
        facts["cleanupRetries"] = remove_owned_directory(directory, temporary_root)
        facts["removed"] = not directory.exists()


class BasicLimits(ctypes.Structure):
    _fields_ = [
        ("process_time", ctypes.c_int64),
        ("job_time", ctypes.c_int64),
        ("flags", wintypes.DWORD),
        ("minimum", ctypes.c_size_t),
        ("maximum", ctypes.c_size_t),
        ("active_limit", wintypes.DWORD),
        ("affinity", ctypes.c_size_t),
        ("priority", wintypes.DWORD),
        ("scheduling", wintypes.DWORD),
    ]


class IoCounters(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_uint64)
        for name in (
            "read_ops",
            "write_ops",
            "other_ops",
            "read_bytes",
            "write_bytes",
            "other_bytes",
        )
    ]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("basic", BasicLimits),
        ("io", IoCounters),
        ("process_memory", ctypes.c_size_t),
        ("job_memory", ctypes.c_size_t),
        ("peak_process", ctypes.c_size_t),
        ("peak_job", ctypes.c_size_t),
    ]


class Accounting(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_int64) for name in ("user", "kernel", "period_user", "period_kernel")
    ] + [(name, wintypes.DWORD) for name in ("faults", "total", "active", "terminated")]


class ThreadEntry(ctypes.Structure):
    _fields_ = [
        ("size", wintypes.DWORD),
        ("usage", wintypes.DWORD),
        ("thread", wintypes.DWORD),
        ("owner", wintypes.DWORD),
        ("base", wintypes.LONG),
        ("delta", wintypes.LONG),
        ("flags", wintypes.DWORD),
    ]


class WindowsJob:
    def __init__(self) -> None:
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
            "SetInformationJobObject": (
                [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD],
                wintypes.BOOL,
            ),
            "QueryInformationJobObject": (
                [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p],
                wintypes.BOOL,
            ),
            "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
            "TerminateJobObject": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            "CreateToolhelp32Snapshot": ([wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
            "Thread32First": ([wintypes.HANDLE, ctypes.POINTER(ThreadEntry)], wintypes.BOOL),
            "Thread32Next": ([wintypes.HANDLE, ctypes.POINTER(ThreadEntry)], wintypes.BOOL),
            "OpenThread": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            "ResumeThread": ([wintypes.HANDLE], wintypes.DWORD),
            "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.api, name)
            function.argtypes, function.restype = arguments, result
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = ExtendedLimits()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE.
        if not self.api.SetInformationJobObject(
            self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
        ):
            self.api.CloseHandle(self.handle)
            raise ctypes.WinError(ctypes.get_last_error())
        self.attached = False

    def attach_and_resume(self, process) -> None:
        if not self.api.AssignProcessToJobObject(
            self.handle, wintypes.HANDLE(int(process._handle))
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        self.attached = True
        snapshot = self.api.CreateToolhelp32Snapshot(4, 0)  # TH32CS_SNAPTHREAD.
        if snapshot == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            entry = ThreadEntry()
            entry.size = ctypes.sizeof(entry)
            available = self.api.Thread32First(snapshot, ctypes.byref(entry))
            while available:
                if entry.owner == process.pid:
                    thread = self.api.OpenThread(2, False, entry.thread)  # THREAD_SUSPEND_RESUME.
                    if not thread:
                        raise ctypes.WinError(ctypes.get_last_error())
                    try:
                        if self.api.ResumeThread(thread) == 0xFFFFFFFF:
                            raise ctypes.WinError(ctypes.get_last_error())
                    finally:
                        self.api.CloseHandle(thread)
                    return
                available = self.api.Thread32Next(snapshot, ctypes.byref(entry))
            raise RuntimeError("the suspended owned process primary thread was not found")
        finally:
            self.api.CloseHandle(snapshot)

    def active(self) -> int:
        result = Accounting()
        if not self.api.QueryInformationJobObject(
            self.handle, 1, ctypes.byref(result), ctypes.sizeof(result), None
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return result.active

    def close(self) -> dict:
        try:
            before = self.active()
            if not self.api.TerminateJobObject(self.handle, 1):
                raise ctypes.WinError(ctypes.get_last_error())
            deadline = time.monotonic() + 10
            while self.active():
                if time.monotonic() >= deadline:
                    raise RuntimeError("owned native process job did not drain")
                time.sleep(0.05)
            return {"jobOwned": True, "remainingBeforeCleanup": before, "remainingAfterCleanup": 0}
        finally:
            self.api.CloseHandle(self.handle)
