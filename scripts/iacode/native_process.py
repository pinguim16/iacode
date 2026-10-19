"""Contain only an owned Windows acceptance process tree in a kill-on-close Job Object."""

from __future__ import annotations

import ctypes
import shutil
import tempfile
import time
from contextlib import contextmanager
from ctypes import wintypes
from pathlib import Path


def remove_owned_directory(
    directory: Path, temporary_root: Path, *, observation: dict | None = None
) -> int:
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
    started = time.monotonic()
    deadline = started + 10
    retries = 0
    attempts = 0
    first_lock = None
    failure = None
    try:
        while directory.exists():
            attempts += 1
            try:
                shutil.rmtree(directory)
            except PermissionError as error:
                now = time.monotonic()
                retryable = getattr(error, "winerror", None) in (5, 32)
                if retryable and first_lock is None:
                    first_lock = round(now - started, 6)
                if not retryable or now >= deadline:
                    raise
                retries += 1
                time.sleep(0.1)
    except Exception as error:
        failure = {
            "type": type(error).__name__,
            "errno": getattr(error, "errno", None),
            "winerror": getattr(error, "winerror", None),
            "filename": str(error.filename) if getattr(error, "filename", None) else None,
        }
        raise
    finally:
        if observation is not None:
            observation.update(
                {
                    "cleanupRetries": retries,
                    "cleanupAttempts": attempts,
                    "cleanupElapsedSeconds": round(time.monotonic() - started, 6),
                    "firstSharingLockAfterSeconds": first_lock,
                    "cleanupFailure": failure,
                    "removed": not directory.exists(),
                }
            )
    return retries


@contextmanager
def owned_directory(prefix: str):
    if not prefix.startswith("iacode-") or any(char in prefix for char in "/\\"):
        raise ValueError("owned temporary prefix required")
    temporary_root = Path(tempfile.gettempdir()).resolve()
    directory = Path(tempfile.mkdtemp(prefix=prefix, dir=temporary_root))
    facts = {
        "path": directory,
        "cleanupRetries": 0,
        "cleanupAttempts": 0,
        "cleanupElapsedSeconds": None,
        "firstSharingLockAfterSeconds": None,
        "cleanupFailure": None,
        "removed": False,
    }
    try:
        yield facts
    finally:
        try:
            facts["cleanupRetries"] = remove_owned_directory(
                directory, temporary_root, observation=facts
            )
        except Exception as error:
            if facts["cleanupFailure"] is None:
                facts["cleanupFailure"] = {
                    "type": type(error).__name__,
                    "errno": getattr(error, "errno", None),
                    "winerror": getattr(error, "winerror", None),
                }
            raise


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


class ProcessIdList(ctypes.Structure):
    _fields_ = [
        ("assigned", wintypes.DWORD),
        ("listed", wintypes.DWORD),
        ("identifiers", ctypes.c_size_t * 4096),
    ]


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


class NativeJobCleanupError(RuntimeError):
    """Closed cleanup facts survive propagation; arbitrary exception text does not."""

    def __init__(self, message: str, observation: dict) -> None:
        super().__init__(message)
        self.observation = dict(observation)


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
            "OpenProcess": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            "IsProcessInJob": (
                [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)],
                wintypes.BOOL,
            ),
            "WaitForSingleObject": ([wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
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

    def owned_member_handles(self) -> list[tuple[int, int]]:
        """Pin read/synchronization handles only after exact membership validation."""
        members = ProcessIdList()
        if not self.api.QueryInformationJobObject(
            self.handle, 3, ctypes.byref(members), ctypes.sizeof(members), None
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        if members.assigned != members.listed or members.listed > 4096:
            raise RuntimeError("owned native job member snapshot is incomplete")
        handles = []
        try:
            for identifier in members.identifiers[: members.listed]:
                handle = self.api.OpenProcess(0x101000, False, identifier)
                if not handle:
                    raise ctypes.WinError(ctypes.get_last_error())
                handles.append((identifier, handle))
                contained = wintypes.BOOL()
                if not self.api.IsProcessInJob(handle, self.handle, ctypes.byref(contained)):
                    raise ctypes.WinError(ctypes.get_last_error())
                if not contained.value:
                    raise RuntimeError("native process identity is no longer an owned job member")
        except Exception:
            for _, handle in handles:
                self.api.CloseHandle(handle)
            raise
        return handles

    def close(self) -> dict:
        handles = []
        pending = {}
        started = time.monotonic()
        deadline = started + 10
        grace_until = started + 1
        now = started
        before = active = None
        forced = False
        phase = "MEMBER_SNAPSHOT"
        try:
            before = self.active()
            handles = self.owned_member_handles()
            pending = dict(handles)
            phase = "NATURAL_DRAIN"
            while True:
                active = self.active()
                for identifier, handle in list(pending.items()):
                    status = self.api.WaitForSingleObject(handle, 0)
                    if status == 0:
                        del pending[identifier]
                    elif status == 0xFFFFFFFF:
                        raise ctypes.WinError(ctypes.get_last_error())
                    elif status != 258:
                        raise RuntimeError("unexpected owned process synchronization state")
                now = time.monotonic()
                if now >= deadline:
                    raise RuntimeError("owned native process job did not drain")
                if not active and not pending:
                    break
                if not forced and now >= grace_until:
                    phase = "FORCE_SNAPSHOT"
                    known = set(dict(handles))
                    for identifier, handle in self.owned_member_handles():
                        if identifier in known:
                            self.api.CloseHandle(handle)
                        else:
                            handles.append((identifier, handle))
                            pending[identifier] = handle
                    phase = "FORCED_DRAIN"
                    if not self.api.TerminateJobObject(self.handle, 1):
                        raise ctypes.WinError(ctypes.get_last_error())
                    forced = True
                time.sleep(0.05)
            return {
                "jobOwned": True,
                "remainingBeforeCleanup": before,
                "remainingAfterCleanup": 0,
                "observedProcessCount": len(handles),
                "signaledProcessCount": len(handles),
                "forcedTermination": forced,
                "naturalExitBudgetWithinOriginalDeadlineSeconds": 1,
            }
        except Exception as error:
            observation = {
                "result": "FAIL",
                "phase": phase,
                "totalDeadlineSeconds": 10,
                "naturalExitBudgetSeconds": 1,
                "forcedTermination": forced,
                "remainingBeforeCleanup": before,
                "remainingJobActive": active,
                "observedProcessCount": len(handles),
                "signaledProcessCount": len(handles) - len(pending),
                "pendingProcessCount": len(pending),
                "lastObservedElapsedSeconds": round(max(0, now - started), 6),
            }
            message = (
                "owned native process job did not drain"
                if now >= deadline
                else "owned native job cleanup failed"
            )
            raise NativeJobCleanupError(message, observation) from error
        finally:
            for _, handle in handles:
                self.api.CloseHandle(handle)
            self.api.CloseHandle(self.handle)
