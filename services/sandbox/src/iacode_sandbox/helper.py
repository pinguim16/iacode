"""The program that runs inside a sandbox and does what a tool asks.

The controller never touches a workspace. It sends one JSON request to this program over ``docker
exec`` and reads one JSON response back; everything that reads, writes, searches, patches, runs or
commits happens here, inside the container, as the sandbox's unprivileged user, on a filesystem
whose only writable places are the workspace and ``/tmp``.

That arrangement is the defence in depth of the Gate. Even a path resolver with a bug could only
reach this container's own filesystem — a read-only image and two small in-memory mounts — because
the host is not mounted here at all.

Three rules shape the process handling, and they are the rules the Gate's red team attacks:

- **A command's whole process tree ends with it.** The command runs in a new session; on timeout the
  session's process group is killed, and afterwards every process in the container other than the
  init process and this helper is killed too, so a child that escaped into its own session with
  ``setsid`` or a double fork does not survive the command that started it.
- **Output is bounded while it is read.** Each stream keeps at most ``artifactBytes`` and counts the
  rest; nothing buffers without a limit.
- **Nothing is inherited.** A command's environment is built from the request's allowlisted
  variables, never from this process's environment.

Standard library only, and runnable from a flat directory: the image copies this file,
``paths.py`` and ``patching.py`` to ``/opt/iacode`` and runs ``python3 -I`` on it.
"""

from __future__ import annotations

import base64
import contextlib
import io
import json
import os
import re
import signal
import subprocess
import sys
import tarfile
import threading
import time
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # the flat copy inside the image
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from patching import PatchRejectedError, apply_patch  # type: ignore[no-redef]
    from paths import PathRejectedError, resolve_workspace_path  # type: ignore[no-redef]
else:
    from iacode_sandbox.patching import PatchRejectedError, apply_patch
    from iacode_sandbox.paths import PathRejectedError, resolve_workspace_path

WORKSPACE = os.environ.get("IACODE_SANDBOX_WORKSPACE", "/workspace")
GIT_CONFIG = os.environ.get("IACODE_SANDBOX_GIT_CONFIG", "/opt/iacode/gitconfig")

#: The environment every command starts from. Nothing else of this process's environment reaches
#: a command: a variable the request does not name and the policy does not allow does not exist.
BASE_ENVIRONMENT = {
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "HOME": "/tmp",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "PYTHONDONTWRITEBYTECODE": "1",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": GIT_CONFIG,
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_ALLOW_PROTOCOL": "file",
}


class HelperError(Exception):
    """A request this helper refuses, with the code reported to the controller."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


# -- process handling -----------------------------------------------------------------------------


class _BoundedReader(threading.Thread):
    """Drain one pipe to the end, keeping at most ``limit`` bytes and counting all of them."""

    def __init__(self, stream: Any, limit: int) -> None:
        super().__init__(daemon=True)
        self.stream = stream
        self.limit = limit
        self.kept = bytearray()
        self.total = 0

    def run(self) -> None:
        while True:
            chunk = self.stream.read(65536)
            if not chunk:
                return
            self.total += len(chunk)
            room = self.limit - len(self.kept)
            if room > 0:
                self.kept.extend(chunk[:room])


def _processes() -> list[dict[str, Any]]:
    """Every process visible in this container's PID namespace."""
    found = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/stat", encoding="utf-8", errors="replace") as handle:
                stat = handle.read()
            with open(f"/proc/{entry}/cmdline", "rb") as handle:
                command = handle.read().replace(b"\x00", b" ").decode("utf-8", "replace").strip()
        except OSError:
            continue
        closing = stat.rfind(")")
        fields = stat[closing + 2:].split()
        found.append({"pid": int(entry), "ppid": int(fields[1]) if len(fields) > 1 else 0,
                      "state": fields[0] if fields else "?", "command": command[:200]})
    return found


#: How long the sweep may take before it gives up on a process table it cannot empty, and how much
#: of that the freezing may use. Freezing has its own, shorter budget: a process blocked inside the
#: kernel (state ``D``, a fork waiting on the process limit) cannot stop until it returns, and a
#: freeze that waited for it would spend the whole sweep and leave no time to kill anything.
SWEEP_SECONDS = 15.0
FREEZE_SECONDS = 3.0


def _pids() -> set[int]:
    """The process identifiers in this PID namespace, from the directory listing alone."""
    return {int(entry) for entry in os.listdir("/proc") if entry.isdigit()}


def _state(pid: int) -> str:
    """A process's state letter, from ``stat`` alone, or ``""`` when it has gone.

    Never ``cmdline``: reading another process's command line takes that process's memory lock,
    which a process in the middle of a fork holds, so a sweep that read it would wait on exactly
    the processes it has to kill.
    """
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8", errors="replace") as handle:
            stat = handle.read()
    except OSError:
        return ""
    fields = stat[stat.rfind(")") + 2:].split()
    return fields[0] if fields else ""


def kill_everything_else(deadline_seconds: float = SWEEP_SECONDS,
                         freeze_seconds: float = FREEZE_SECONDS) -> int:
    """Kill every process except the init process and this helper. Returns how many.

    Freeze first, then kill. A loop of ``SIGKILL`` loses to a fork bomb that detached from the
    command it came from: while the sweep walks the process table, every survivor forks into the
    slots the sweep just freed, and the table stays full — the sandbox then cannot start the next
    command at all. A stopped process cannot fork, so every process is sent ``SIGSTOP`` until a
    listing shows no process the previous rounds had not already stopped; a process blocked in the
    kernel is killed on its way out by the ``SIGKILL`` that follows.
    """
    keep = {1, os.getpid()}
    started = time.monotonic()
    freeze_deadline = started + min(freeze_seconds, deadline_seconds)
    deadline = started + deadline_seconds
    frozen: set[int] = set()
    while time.monotonic() < freeze_deadline:
        current = _pids() - keep
        if current <= frozen:
            break
        for pid in current:
            with contextlib.suppress(OSError):
                os.kill(pid, signal.SIGSTOP)
        frozen |= current
    killed = 0
    while time.monotonic() < deadline:
        targets = [pid for pid in _pids() - keep if _state(pid) not in ("", "Z")]
        if not targets:
            break
        for pid in targets:
            try:
                os.kill(pid, signal.SIGKILL)
                killed += 1
            except OSError:
                pass
        time.sleep(0.02)
    return killed


def run_process(argv: list[str], *, cwd: str, environment: dict[str, str], timeout: float,
                inline_bytes: int, artifact_bytes: int, stdin: bytes | None = None
                ) -> dict[str, Any]:
    """Run one process to completion or to its timeout, and leave nothing behind."""
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            argv, cwd=cwd, env=environment, stdin=subprocess.PIPE if stdin else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    except FileNotFoundError:
        return {"started": False, "exitCode": None, "stdout": "", "stderr": "",
                "durationMs": int((time.monotonic() - started) * 1000), "timedOut": False,
                "truncated": False, "stdoutBytes": 0, "stderrBytes": 0, "orphansKilled": 0,
                "errorCode": "EXECUTABLE_NOT_FOUND",
                "error": f"{argv[0]!r} does not exist in the sandbox image"}
    except OSError as error:
        return {"started": False, "exitCode": None, "stdout": "", "stderr": "",
                "durationMs": int((time.monotonic() - started) * 1000), "timedOut": False,
                "truncated": False, "stdoutBytes": 0, "stderrBytes": 0, "orphansKilled": 0,
                "errorCode": "PROCESS_NOT_STARTED", "error": f"the process could not start: "
                                                             f"{error.strerror}"}
    readers = [_BoundedReader(process.stdout, artifact_bytes),
               _BoundedReader(process.stderr, artifact_bytes)]
    for reader in readers:
        reader.start()
    if stdin:
        with contextlib.suppress(OSError):
            process.stdin.write(stdin)
            process.stdin.close()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        with contextlib.suppress(OSError):
            os.killpg(process.pid, signal.SIGKILL)
        process.wait()
    # Whatever the command left running — in its own group or escaped into another session —
    # ends now, so the pipes close and nothing outlives the command that started it.
    orphans = kill_everything_else()
    for reader in readers:
        reader.join(timeout=5)
    stdout, stderr = readers
    truncated = stdout.total > inline_bytes or stderr.total > inline_bytes
    result = {
        "started": True,
        "exitCode": None if timed_out else process.returncode,
        "stdout": bytes(stdout.kept[:inline_bytes]).decode("utf-8", "replace"),
        "stderr": bytes(stderr.kept[:inline_bytes]).decode("utf-8", "replace"),
        "durationMs": int((time.monotonic() - started) * 1000),
        "timedOut": timed_out,
        "truncated": truncated,
        "stdoutBytes": stdout.total,
        "stderrBytes": stderr.total,
        "orphansKilled": orphans,
    }
    if truncated:
        result["stdoutFull"] = base64.b64encode(bytes(stdout.kept)).decode("ascii")
        result["stderrFull"] = base64.b64encode(bytes(stderr.kept)).decode("ascii")
    if timed_out:
        result["errorCode"] = "COMMAND_TIMED_OUT"
        result["error"] = f"the command exceeded its timeout of {timeout:g}s and was killed"
    return result


def _environment(extra: dict[str, str] | None) -> dict[str, str]:
    environment = dict(BASE_ENVIRONMENT)
    for key, value in (extra or {}).items():
        environment[str(key)] = str(value)
    return environment


# -- operations ---------------------------------------------------------------------------------


def _resolve(requested: Any, **options: Any) -> Path:
    try:
        return resolve_workspace_path(WORKSPACE, requested, **options)
    except PathRejectedError as rejected:
        raise HelperError(rejected.code, str(rejected)) from None


def _relative(path: Path) -> str:
    root = os.path.realpath(WORKSPACE)
    value = os.path.relpath(os.path.realpath(str(path)) if path.exists() else str(path), root)
    return "." if value == "." else value.replace(os.sep, "/")


def op_list(request: dict[str, Any]) -> dict[str, Any]:
    base = _resolve(request.get("path") or ".")
    if not base.is_dir():
        raise HelperError("PATH_NOT_A_DIRECTORY", f"{request.get('path')!r} is not a directory")
    depth = int(request.get("depth") or 1)
    limit = int(request["maxEntries"])
    entries: list[dict[str, Any]] = []
    truncated = False
    base_depth = len(base.parts)
    for current, directories, files in os.walk(base, followlinks=False):
        directories[:] = sorted(item for item in directories if item != ".git")
        level = len(Path(current).parts) - base_depth
        if level >= depth:
            directories[:] = []
        for name in sorted(directories) + sorted(files):
            path = Path(current) / name
            if len(entries) >= limit:
                truncated = True
                break
            kind = "link" if path.is_symlink() else "directory" if path.is_dir() else "file"
            entry = {"path": os.path.relpath(str(path), os.path.realpath(WORKSPACE))
                     .replace(os.sep, "/"), "type": kind}
            if kind == "file":
                entry["size"] = path.stat().st_size
            entries.append(entry)
        if truncated:
            break
    return {"entries": entries, "truncated": truncated}


def op_read(request: dict[str, Any]) -> dict[str, Any]:
    path = _resolve(request.get("path"), allow_root=False)
    if not path.is_file():
        raise HelperError("FILE_NOT_FOUND", f"{request.get('path')!r} is not a file")
    limit = int(request["maxBytes"])
    size = path.stat().st_size
    if size > limit:
        raise HelperError("FILE_TOO_LARGE",
                          f"{request.get('path')!r} is {size} bytes; the limit is {limit}")
    content = path.read_bytes()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HelperError("FILE_NOT_UTF8",
                          f"{request.get('path')!r} is not UTF-8 text; binary content is not "
                          "returned inline") from None
    return {"path": _relative(path), "content": text, "size": size}


def op_write(request: dict[str, Any]) -> dict[str, Any]:
    content = request.get("content")
    if not isinstance(content, str):
        raise HelperError("CONTENT_NOT_TEXT", "the content to write must be a string")
    encoded = content.encode("utf-8")
    if len(encoded) > int(request["maxBytes"]):
        raise HelperError("CONTENT_TOO_LARGE",
                          f"the content is {len(encoded)} bytes; "
                          f"the limit is {request['maxBytes']}")
    path = _resolve(request.get("path"), allow_root=False, for_write=True)
    if path.is_dir():
        raise HelperError("PATH_IS_A_DIRECTORY", f"{request.get('path')!r} is a directory")
    if not path.parent.exists():
        if not request.get("createParents"):
            raise HelperError("PARENT_NOT_FOUND",
                              f"the directory of {request.get('path')!r} does not exist")
        path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".iacode-write-{os.getpid()}-{time.monotonic_ns()}"
    try:
        with open(temporary, "wb") as handle:
            handle.write(encoded)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"path": _relative(path), "size": len(encoded)}


def op_patch(request: dict[str, Any]) -> dict[str, Any]:
    try:
        changed = apply_patch(WORKSPACE, request.get("patch"), max_bytes=int(request["maxBytes"]))
    except PatchRejectedError as rejected:
        raise HelperError(rejected.code, str(rejected)) from None
    return {"files": changed}


def op_search(request: dict[str, Any]) -> dict[str, Any]:
    pattern_text = request.get("pattern")
    if not isinstance(pattern_text, str) or not pattern_text:
        raise HelperError("PATTERN_EMPTY", "a search needs a non-empty pattern")
    try:
        pattern = re.compile(pattern_text if request.get("regex") else re.escape(pattern_text))
    except re.error as error:
        raise HelperError("PATTERN_INVALID",
                          f"the pattern is not a valid expression: {error}") from None
    base = _resolve(request.get("path") or ".")
    limit = int(request["maxResults"])
    deadline = time.monotonic() + float(request["maxSeconds"])
    max_file = int(request["maxFileBytes"])
    matches: list[dict[str, Any]] = []
    truncated = False
    timed_out = False

    def candidates():
        if base.is_file():
            yield base
            return
        for current, directories, files in os.walk(base, followlinks=False):
            directories[:] = sorted(item for item in directories if item != ".git")
            for name in sorted(files):
                yield Path(current) / name

    for path in candidates():
        if time.monotonic() > deadline:
            timed_out = True
            break
        if path.is_symlink() or not path.is_file() or path.stat().st_size > max_file:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, 1):
            if pattern.search(line):
                if len(matches) >= limit:
                    truncated = True
                    break
                matches.append({"path": os.path.relpath(str(path), os.path.realpath(WORKSPACE))
                                .replace(os.sep, "/"), "line": number, "text": line[:300]})
        if truncated:
            break
    return {"matches": matches, "truncated": truncated, "timedOut": timed_out}


def op_exec(request: dict[str, Any]) -> dict[str, Any]:
    cwd = _resolve(request.get("cwd") or ".")
    if not cwd.is_dir():
        raise HelperError("CWD_NOT_A_DIRECTORY", f"{request.get('cwd')!r} is not a directory")
    command = request.get("command")
    if not isinstance(command, str) or not command.strip():
        raise HelperError("COMMAND_EMPTY", "shell.exec needs a non-empty command")
    # The shell is deliberate and bounded: this *is* the sandbox, and shell.exec is the tool whose
    # contract is "run this with a shell". The string never reaches a shell anywhere else.
    return run_process(["/bin/sh", "-c", command], cwd=str(cwd),
                       environment=_environment(request.get("environment")),
                       timeout=float(request["timeoutSeconds"]),
                       inline_bytes=int(request["outputBytes"]),
                       artifact_bytes=int(request["artifactBytes"]))


def op_git(request: dict[str, Any]) -> dict[str, Any]:
    argv = request.get("argv")
    if not isinstance(argv, list) or not argv or argv[0] != "git":
        raise HelperError("GIT_ARGV_INVALID", "a Git operation is an argument vector for git")
    return run_process([str(item) for item in argv], cwd=os.path.realpath(WORKSPACE),
                       environment=_environment(None),
                       timeout=float(request["timeoutSeconds"]),
                       inline_bytes=int(request["outputBytes"]),
                       artifact_bytes=int(request["artifactBytes"]))


def _safe_members(archive: tarfile.TarFile, limit: int) -> list[tarfile.TarInfo]:
    total = 0
    members = []
    for member in archive.getmembers():
        if member.isdev() or member.isfifo():
            raise HelperError("SNAPSHOT_UNSAFE", f"{member.name!r} is a device or a fifo")
        if member.issym() or member.islnk():
            raise HelperError("SNAPSHOT_UNSAFE", f"{member.name!r} is a link; snapshots carry "
                                                 "regular files only")
        try:
            resolve_workspace_path(WORKSPACE, member.name, allow_root=True)
        except PathRejectedError as rejected:
            raise HelperError("SNAPSHOT_UNSAFE", f"{member.name!r}: {rejected}") from None
        total += member.size
        if total > limit:
            raise HelperError("SNAPSHOT_TOO_LARGE", f"the snapshot exceeds {limit} bytes")
        members.append(member)
    return members


def op_workspace_init(request: dict[str, Any]) -> dict[str, Any]:
    root = os.path.realpath(WORKSPACE)
    if any(os.scandir(root)):
        raise HelperError("WORKSPACE_NOT_EMPTY", "a workspace is provisioned once")
    files = 0
    payload = request.get("snapshot")
    if payload:
        data = base64.b64decode(payload)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            members = _safe_members(archive, int(request["maxBytes"]))
            # The "data" filter refuses absolute names, escapes, links out and special files a
            # second time, in the library that does the writing.
            archive.extractall(root, members=members, filter="data")
            files = sum(1 for member in members if member.isfile())
    git_environment = _environment(None)
    steps = []
    if not os.path.isdir(os.path.join(root, ".git")):
        steps = [["git", "init", "-q", "-b", "main"], ["git", "add", "-A"],
                 ["git", "commit", "-q", "--allow-empty", "-m", "Workspace snapshot"]]
    for argv in steps:
        outcome = run_process(argv, cwd=root, environment=git_environment, timeout=60,
                              inline_bytes=4096, artifact_bytes=4096)
        if outcome.get("exitCode") != 0:
            raise HelperError("WORKSPACE_GIT_INIT_FAILED",
                              f"{' '.join(argv[:2])} failed: {outcome.get('stderr', '')[:300]}")
    return {"files": files}


def op_ps(_request: dict[str, Any]) -> dict[str, Any]:
    own = os.getpid()
    return {"processes": [item for item in _processes() if item["pid"] != own]}


def op_kill_all(_request: dict[str, Any]) -> dict[str, Any]:
    return {"killed": kill_everything_else()}


OPERATIONS = {
    "fs.list": op_list,
    "fs.read": op_read,
    "fs.write": op_write,
    "fs.patch": op_patch,
    "fs.search": op_search,
    "exec": op_exec,
    "git": op_git,
    "workspace.init": op_workspace_init,
    "ps": op_ps,
    "kill-all": op_kill_all,
}


def handle(request: dict[str, Any]) -> dict[str, Any]:
    operation = OPERATIONS.get(str(request.get("op")))
    if operation is None:
        return {"ok": False, "errorCode": "OPERATION_UNKNOWN",
                "error": f"{request.get('op')!r} is not an operation of this helper"}
    try:
        return {"ok": True, "result": operation(request)}
    except HelperError as error:
        return {"ok": False, "errorCode": error.code, "error": str(error)}
    except OSError as error:
        return {"ok": False, "errorCode": "FILESYSTEM_ERROR",
                "error": f"{error.strerror or error}"}


def run_init() -> int:
    """PID 1 of a sandbox: reap every orphan, and do nothing else.

    A sandbox has no long-running program of its own; every tool arrives through ``docker exec``.
    Its first process therefore only has to be a correct init: it reaps whatever is re-parented to
    it, so an orphan never lingers as a zombie against the process limit, and it exits when the
    engine asks the container to stop. Because it is PID 1, a signal sent from inside the sandbox
    cannot kill it, and because it is the only process that is neither a tool nor a helper,
    "every process but PID 1 and this helper" is exactly the set a tool may leave behind.
    """

    def reap(_signum: int, _frame: Any) -> None:
        while True:
            try:
                pid, _status = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                return
            if pid == 0:
                return

    signal.signal(signal.SIGCHLD, reap)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    while True:
        signal.pause()


def main() -> int:
    if sys.argv[1:] == ["--init"]:
        return run_init()
    try:
        request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        response = {"ok": False, "errorCode": "REQUEST_INVALID", "error": str(error)[:300]}
    else:
        response = handle(request if isinstance(request, dict) else {})
    sys.stdout.write(json.dumps(response, ensure_ascii=False))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
