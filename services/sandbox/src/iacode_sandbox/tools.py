"""The closed registry of executable tools, and how each one's arguments become a helper request.

A tool name is a key into :data:`REGISTRY` and into nothing else. It is never resolved to a module,
an executable, a path or a shell command: a name the registry does not hold is refused with
``UNKNOWN_TOOL``, and there is no fallback that hands an unknown name to ``shell.exec``.

Each tool validates its arguments strictly — a key it does not declare is refused, a value of the
wrong type is refused with its own reason — and builds the one helper request it maps to, with the
limits taken from the policy rather than from the request. A request may *lower* the timeout of a
command; it can never raise it, and it can never name a limit, a mount, an image or a network,
because no tool declares an argument for any of them.

Git operations are argument vectors built here from a closed set of verbs. ``push``, ``fetch``,
``pull``, ``clone``, ``remote``, ``reset``, ``clean``, ``rebase``, ``filter-repo`` and every other
verb this Gate does not offer have no tool, and a revision or path that looks like an option is
refused before it reaches ``git``.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from iacode_sandbox.paths import PathRejectedError, normalize_request_path
from iacode_sandbox.policy import ResourceProfile, SandboxPolicy

__all__ = ["ACCESS_LEVELS", "REGISTRY", "ToolRejectedError", "ToolSpec", "build_helper_request"]

#: What a tool needs from the workspace. A read-only policy grants only ``read``.
ACCESS_LEVELS = ("read", "write", "execute")

_REVISION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/^~@{}-]{0,127}$")


class ToolRejectedError(ValueError):
    """A request refused before anything ran. The code is what the agent receives."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ToolSpec:
    name: str
    access: str
    arguments: dict[str, type | tuple[type, ...]]
    required: tuple[str, ...]
    build: Callable[[dict[str, Any], SandboxPolicy, ResourceProfile], dict[str, Any]]


def _check(tool: str, arguments: Any, declared: dict[str, type | tuple[type, ...]],
           required: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise ToolRejectedError("ARGUMENTS_INVALID", f"{tool}: the arguments must be an object")
    unknown = sorted(set(arguments) - set(declared))
    if unknown:
        raise ToolRejectedError(
            "ARGUMENT_UNKNOWN",
            f"{tool} does not accept {', '.join(unknown)}; a request cannot add a "
            "setting a tool does not declare")
    for name in required:
        if name not in arguments:
            raise ToolRejectedError("ARGUMENT_MISSING", f"{tool} requires {name!r}")
    for name, value in arguments.items():
        expected = declared[name]
        # bool is an int in Python; a flag and a count are different things to a tool.
        accepted = expected if isinstance(expected, tuple) else (expected,)
        wrong = (not isinstance(value, expected)
                 or (isinstance(value, bool) and bool not in accepted))
        if wrong:
            raise ToolRejectedError("ARGUMENT_WRONG_TYPE",
                                    f"{tool}: {name!r} has the wrong type ({type(value).__name__})")
    return arguments


def _path(tool: str, value: Any) -> str:
    try:
        return str(normalize_request_path(value))
    except PathRejectedError as rejected:
        raise ToolRejectedError(rejected.code, f"{tool}: {rejected}") from None


def _bounded(tool: str, name: str, value: Any, low: int, high: int) -> int:
    if value < low or value > high:
        raise ToolRejectedError("ARGUMENT_OUT_OF_RANGE",
                                f"{tool}: {name!r} must be between {low} and {high}")
    return int(value)


def _output(profile: ResourceProfile, timeout: int) -> dict[str, Any]:
    return {"timeoutSeconds": timeout, "outputBytes": profile.output_bytes,
            "artifactBytes": profile.artifact_bytes}


# -- filesystem ---------------------------------------------------------------------------------


def _list(arguments, _policy, profile):
    return {"op": "fs.list", "path": _path("filesystem.list", arguments.get("path", ".")),
            "depth": _bounded("filesystem.list", "depth", arguments.get("depth", 1), 1, 4),
            "maxEntries": profile.list_entries}


def _read(arguments, _policy, profile):
    return {"op": "fs.read", "path": _path("filesystem.read", arguments["path"]),
            "maxBytes": profile.read_bytes}


def _write(arguments, _policy, profile):
    return {"op": "fs.write", "path": _path("filesystem.write", arguments["path"]),
            "content": arguments["content"],
            "createParents": bool(arguments.get("createParents", False)),
            "maxBytes": profile.write_bytes}


def _patch(arguments, _policy, profile):
    return {"op": "fs.patch", "patch": arguments["patch"], "maxBytes": profile.patch_bytes}


def _search(arguments, _policy, profile):
    return {"op": "fs.search", "pattern": arguments["pattern"],
            "regex": bool(arguments.get("regex", False)),
            "path": _path("filesystem.search", arguments.get("path", ".")),
            "maxResults": _bounded("filesystem.search", "maxResults",
                                   arguments.get("maxResults", profile.search_results), 1,
                                   profile.search_results),
            "maxSeconds": profile.search_seconds, "maxFileBytes": profile.search_file_bytes}


# -- shell ----------------------------------------------------------------------------------------


def _exec(arguments, policy, profile):
    environment = arguments.get("environment") or {}
    allowed = policy.request_environment_names
    for name, value in environment.items():
        if name not in allowed:
            raise ToolRejectedError("ENVIRONMENT_NOT_ALLOWED",
                                    f"shell.exec may not set {name!r}; the policy allows "
                                    + (", ".join(sorted(allowed)) or "no variable"))
        if not isinstance(value, str) or len(value) > policy.request_environment_max_length:
            raise ToolRejectedError(
                "ENVIRONMENT_VALUE_INVALID",
                f"shell.exec: the value of {name!r} must be a string of at most "
                f"{policy.request_environment_max_length} characters")
    command = arguments["command"]
    if not command.strip():
        raise ToolRejectedError("COMMAND_EMPTY", "shell.exec needs a non-empty command")
    timeout = _bounded("shell.exec", "timeoutSeconds",
                       arguments.get("timeoutSeconds", profile.command_timeout_seconds), 1,
                       profile.command_timeout_seconds)
    return {"op": "exec", "command": command, "cwd": _path("shell.exec", arguments.get("cwd", ".")),
            "environment": dict(environment), **_output(profile, timeout)}


# -- git ------------------------------------------------------------------------------------------


def _revision(tool: str, value: str) -> str:
    if not _REVISION.match(value):
        raise ToolRejectedError("GIT_REVISION_INVALID",
                                f"{tool}: {value!r} is not a revision this tool accepts")
    return value


def _git(argv: list[str], profile: ResourceProfile) -> dict[str, Any]:
    return {"op": "git", "argv": ["git", "-c", "core.pager=cat", "-c", "color.ui=false", *argv],
            **_output(profile, profile.git_timeout_seconds)}


def _git_status(_arguments, _policy, profile):
    return _git(["status", "--short", "--branch"], profile)


def _git_diff(arguments, _policy, profile):
    argv = ["diff", "--no-ext-diff"]
    if arguments.get("staged"):
        argv.append("--staged")
    if "path" in arguments:
        argv += ["--", _path("git.diff", arguments["path"])]
    return _git(argv, profile)


def _git_log(arguments, _policy, profile):
    count = _bounded("git.log", "maxCount", arguments.get("maxCount", 20), 1, 200)
    return _git(["log", f"--max-count={count}", "--format=%H %an %ad %s", "--date=iso-strict"],
                profile)


def _git_show(arguments, _policy, profile):
    revision = _revision("git.show", arguments.get("revision", "HEAD"))
    argv = ["show", "--no-ext-diff", revision]
    if "path" in arguments:
        argv += ["--", _path("git.show", arguments["path"])]
    return _git(argv, profile)


def _git_add(arguments, _policy, profile):
    paths = arguments["paths"]
    if not paths or not all(isinstance(item, str) for item in paths):
        raise ToolRejectedError("ARGUMENT_WRONG_TYPE",
                                "git.add: 'paths' is a non-empty list of paths")
    return _git(["add", "--", *[_path("git.add", item) for item in paths]], profile)


def _git_commit(arguments, _policy, profile):
    message = arguments["message"]
    if not message.strip() or len(message) > 4000:
        raise ToolRejectedError(
            "ARGUMENT_OUT_OF_RANGE",
            "git.commit: the message must be non-empty and at most 4000 characters")
    return _git(["commit", "--no-verify", "-m", message], profile)


REGISTRY: dict[str, ToolSpec] = {spec.name: spec for spec in (
    ToolSpec("filesystem.list", "read", {"path": str, "depth": int}, (), _list),
    ToolSpec("filesystem.read", "read", {"path": str}, ("path",), _read),
    ToolSpec("filesystem.search", "read",
             {"pattern": str, "path": str, "regex": bool, "maxResults": int}, ("pattern",),
             _search),
    ToolSpec("filesystem.write", "write",
             {"path": str, "content": str, "createParents": bool}, ("path", "content"), _write),
    ToolSpec("filesystem.apply_patch", "write", {"patch": str}, ("patch",), _patch),
    ToolSpec("shell.exec", "execute",
             {"command": str, "cwd": str, "environment": dict, "timeoutSeconds": int},
             ("command",), _exec),
    ToolSpec("git.status", "read", {}, (), _git_status),
    ToolSpec("git.diff", "read", {"staged": bool, "path": str}, (), _git_diff),
    ToolSpec("git.log", "read", {"maxCount": int}, (), _git_log),
    ToolSpec("git.show", "read", {"revision": str, "path": str}, (), _git_show),
    ToolSpec("git.add", "write", {"paths": list}, ("paths",), _git_add),
    ToolSpec("git.commit", "write", {"message": str}, ("message",), _git_commit),
)}


def build_helper_request(tool: str, arguments: Any, policy: SandboxPolicy) -> dict[str, Any]:
    """The helper request for ``tool``, or :class:`ToolRejectedError` saying why there is none."""
    spec = REGISTRY.get(tool)
    if spec is None:
        raise ToolRejectedError(
            "UNKNOWN_TOOL",
            f"{tool!r} is not a registered tool; a name the registry does not hold "
            "is never executed")
    if tool not in policy.tools:
        raise ToolRejectedError("TOOL_NOT_IN_POLICY",
                                f"the {policy.name!r} policy does not allow {tool!r}")
    if spec.access != "read" and policy.workspace_access != "read-write":
        raise ToolRejectedError(
            "WORKSPACE_READ_ONLY",
            f"the {policy.name!r} policy gives read-only access; {tool!r} needs "
            f"{spec.access}")
    checked = _check(tool, arguments, spec.arguments, spec.required)
    return spec.build(checked, policy, policy.resources)
