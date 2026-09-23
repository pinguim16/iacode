"""The one path resolver of the sandbox.

Every filesystem tool, every working directory and every Git path an agent names goes through
:func:`resolve_workspace_path`, and nothing else in the sandbox turns a string from a model into a
path. Path safety repeated in five functions is five chances for one of them to forget a case; this
module is the only place the cases are written.

It runs in two places and is the same file in both. The controller calls
:func:`normalize_request_path` to refuse an obviously hostile path before it spends a container
round trip on it. The helper inside the sandbox image calls :func:`resolve_workspace_path`, which
adds the check only the sandbox can make — where a symbolic link *actually* points — because the
links live in the sandbox's filesystem and the controller never sees them. The image build copies
this file; `SandboxImageProfileTests` asserts the copy is this file.

The property it protects is stated once: **no path this module returns lies outside the
workspace**, whether the request spelled the escape with ``..``, an absolute path, a Windows drive,
a UNC prefix, a backslash, a null byte, a normalisation trick or a symbolic link pointing outside.

Standard library only: this module runs inside the sandbox image, which carries no dependency.
"""

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath

__all__ = [
    "MAX_PATH_LENGTH",
    "WORKSPACE_ROOT",
    "PathRejectedError",
    "normalize_request_path",
    "resolve_workspace_path",
]

#: Where the workspace is mounted inside every sandbox.
WORKSPACE_ROOT = PurePosixPath("/workspace")

#: A path longer than this is refused before it is parsed.
MAX_PATH_LENGTH = 1024

_DRIVE = re.compile(r"^[A-Za-z]:")


class PathRejectedError(ValueError):
    """A requested path the workspace cannot honour, with a code the caller can report."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def normalize_request_path(requested: object, *, allow_root: bool = True) -> PurePosixPath:
    """The workspace-relative path a request names, checked lexically.

    Returns a relative path (``.`` for the workspace itself). Refuses, with a distinct code each:

    - a value that is not a non-empty string, or is longer than :data:`MAX_PATH_LENGTH`;
    - a null byte or any other control character;
    - a backslash, which is how a Windows path and a UNC path are spelled;
    - a Windows drive (``C:``) and a UNC or double-slash prefix (``//host``);
    - an absolute path outside the workspace;
    - a ``..`` that climbs above the workspace, however it is spelled.
    """
    if not isinstance(requested, str) or not requested.strip():
        raise PathRejectedError("PATH_EMPTY", "a path must be a non-empty string")
    if len(requested) > MAX_PATH_LENGTH:
        raise PathRejectedError("PATH_TOO_LONG",
                                f"a path may not exceed {MAX_PATH_LENGTH} characters")
    if "\x00" in requested:
        raise PathRejectedError("PATH_NULL_BYTE", "a path may not contain a null byte")
    if any(ord(character) < 32 or ord(character) == 127 for character in requested):
        raise PathRejectedError("PATH_CONTROL_CHARACTER",
                                "a path may not contain a control character")
    if "\\" in requested:
        raise PathRejectedError("PATH_BACKSLASH",
                                "a path uses '/' as its separator; a backslash is how a Windows or "
                                "UNC path escapes a workspace")
    if _DRIVE.match(requested):
        raise PathRejectedError("PATH_DRIVE", "a Windows drive is not a workspace path")
    if requested.startswith("//"):
        raise PathRejectedError("PATH_UNC", "a UNC or double-slash prefix is not a workspace path")

    candidate = PurePosixPath(requested)
    if candidate.is_absolute():
        try:
            candidate = candidate.relative_to(WORKSPACE_ROOT)
        except ValueError:
            raise PathRejectedError("PATH_ABSOLUTE_OUTSIDE",
                                    f"the absolute path {requested!r} is outside {WORKSPACE_ROOT}"
                                    ) from None

    parts: list[str] = []
    for part in candidate.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                raise PathRejectedError("PATH_ESCAPE",
                                        f"{requested!r} climbs above the workspace")
            parts.pop()
            continue
        parts.append(part)
    if not parts and not allow_root:
        raise PathRejectedError("PATH_IS_WORKSPACE", "the workspace itself is not a file")
    return PurePosixPath(*parts) if parts else PurePosixPath(".")


def _contained(root: str, candidate: str) -> bool:
    return candidate == root or candidate.startswith(root.rstrip("/") + "/")


def resolve_workspace_path(root: str | os.PathLike[str], requested: object, *,
                           allow_root: bool = True, for_write: bool = False) -> Path:
    """The real path inside ``root`` that ``requested`` names, or :class:`PathRejectedError`.

    After the lexical check, the path is resolved the way the kernel will resolve it —
    ``os.path.realpath`` follows every symbolic link, including one in a parent directory — and
    the result must still be inside the real workspace. A link inside the workspace that points
    outside it is therefore refused for reading and for writing alike, and so is a link to ``/``,
    to ``/proc`` or to another directory of the image.

    ``for_write`` additionally requires the parent directory to resolve inside the workspace, so a
    file is never created through a linked directory. A write replaces the final name atomically
    (the caller renames a temporary file over it), which replaces a link rather than following it.
    """
    relative = normalize_request_path(requested, allow_root=allow_root)
    real_root = os.path.realpath(os.fspath(root))
    candidate = os.path.join(real_root, *relative.parts) if relative.parts != (".",) else real_root
    resolved = os.path.realpath(candidate)
    if not _contained(real_root, resolved):
        raise PathRejectedError(
            "PATH_SYMLINK_ESCAPE",
            f"{requested!r} resolves outside the workspace through a symbolic link")
    if for_write:
        parent = os.path.realpath(os.path.dirname(candidate))
        if not _contained(real_root, parent):
            raise PathRejectedError(
                "PATH_SYMLINK_ESCAPE",
                f"the directory of {requested!r} resolves outside the workspace")
        if os.path.islink(candidate) and not _contained(real_root, os.path.realpath(candidate)):
            raise PathRejectedError("PATH_SYMLINK_ESCAPE",
                                    f"{requested!r} is a link that points outside the workspace")
    return Path(resolved) if not for_write else Path(candidate)
