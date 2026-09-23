"""Apply a unified diff to a workspace, entirely or not at all.

A patch from a model is a claim about the files it edits: this hunk sits here, surrounded by these
lines. When the claim is wrong the honest answer is an error naming the hunk, and the dangerous
answer is to apply the hunks that happened to match and drop the rest. This module parses every
file of the patch, applies every hunk to an in-memory copy, and only when all of them apply writes
anything — each file atomically, through a temporary file renamed over the original, and with the
files already written restored if a later one cannot be.

Every path the patch names goes through :func:`paths.resolve_workspace_path`; a patch cannot edit
what the resolver refuses. Standard library only: this runs inside the sandbox image.
"""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

try:  # the package in the controller, the flat copy inside the sandbox image
    from iacode_sandbox.paths import PathRejectedError, resolve_workspace_path
except ImportError:  # pragma: no cover - exercised inside the image
    from paths import PathRejectedError, resolve_workspace_path  # type: ignore[no-redef]

__all__ = ["FilePatch", "Hunk", "PatchRejectedError", "apply_patch", "parse_patch"]

_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
DEV_NULL = "/dev/null"


class PatchRejectedError(ValueError):
    """A patch that cannot be applied, and why. Nothing was written."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class Hunk:
    old_start: int
    old_count: int
    lines: list[str] = field(default_factory=list)


@dataclass
class FilePatch:
    old_path: str | None
    new_path: str | None
    hunks: list[Hunk] = field(default_factory=list)

    @property
    def target(self) -> str:
        return self.new_path or self.old_path or ""


def _strip_prefix(name: str) -> str | None:
    name = name.split("\t", 1)[0].strip()
    if name == DEV_NULL:
        return None
    if name.startswith(("a/", "b/")):
        return name[2:]
    return name


def parse_patch(text: str) -> list[FilePatch]:
    """Parse a unified diff, with or without ``diff --git`` headers."""
    if not isinstance(text, str) or not text.strip():
        raise PatchRejectedError("PATCH_EMPTY", "the patch is empty")
    lines = text.splitlines()
    files: list[FilePatch] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("--- "):
            if index + 1 >= len(lines) or not lines[index + 1].startswith("+++ "):
                raise PatchRejectedError("PATCH_MALFORMED",
                                         f"line {index + 1}: '---' without '+++'")
            current = FilePatch(_strip_prefix(line[4:]), _strip_prefix(lines[index + 1][4:]))
            if current.old_path is None and current.new_path is None:
                raise PatchRejectedError("PATCH_MALFORMED", "a file patch names no file")
            files.append(current)
            index += 2
            while index < len(lines) and lines[index].startswith("@@"):
                match = _HUNK.match(lines[index])
                if match is None:
                    raise PatchRejectedError("PATCH_MALFORMED",
                                             f"line {index + 1}: bad hunk header")
                hunk = Hunk(int(match.group(1)),
                            int(match.group(2)) if match.group(2) is not None else 1)
                index += 1
                while index < len(lines) and lines[index][:1] in (" ", "+", "-", "\\"):
                    if lines[index].startswith("--- ") and index + 1 < len(lines) \
                            and lines[index + 1].startswith("+++ "):
                        break
                    if not lines[index].startswith("\\"):
                        hunk.lines.append(lines[index])
                    index += 1
                if not hunk.lines:
                    raise PatchRejectedError("PATCH_MALFORMED", "a hunk carries no lines")
                current.hunks.append(hunk)
            if not current.hunks:
                raise PatchRejectedError("PATCH_MALFORMED", f"{current.target} has no hunk")
            continue
        index += 1
    if not files:
        raise PatchRejectedError("PATCH_MALFORMED", "the patch contains no file")
    return files


def _apply_hunks(original: list[str], patch: FilePatch) -> list[str]:
    result: list[str] = []
    cursor = 0
    for number, hunk in enumerate(patch.hunks, 1):
        expected = [line[1:] for line in hunk.lines if line[:1] in (" ", "-")]
        replacement = [line[1:] for line in hunk.lines if line[:1] in (" ", "+")]
        start = max(hunk.old_start - 1, 0) if hunk.old_count else hunk.old_start
        if original[start:start + len(expected)] != expected:
            raise PatchRejectedError(
                "PATCH_CONTEXT_MISMATCH",
                f"{patch.target}: hunk {number} does not match the file at line {hunk.old_start}; "
                "nothing was changed")
        if start < cursor:
            raise PatchRejectedError("PATCH_MALFORMED", f"{patch.target}: hunk {number} overlaps")
        result.extend(original[cursor:start])
        result.extend(replacement)
        cursor = start + len(expected)
    result.extend(original[cursor:])
    return result


def _atomic_write(path: Path, content: bytes) -> None:
    descriptor, temporary = tempfile.mkstemp(dir=str(path.parent), prefix=".iacode-patch-")
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def apply_patch(root: str, text: str, *, max_bytes: int) -> list[dict[str, object]]:
    """Apply every file of ``text`` under ``root``, or raise and change nothing."""
    if len(text.encode("utf-8")) > max_bytes:
        raise PatchRejectedError("PATCH_TOO_LARGE", f"the patch exceeds {max_bytes} bytes")
    planned: list[tuple[Path, bytes | None, str]] = []
    for patch in parse_patch(text):
        try:
            if patch.new_path is None:
                target = resolve_workspace_path(root, patch.old_path, allow_root=False,
                                                for_write=True)
            else:
                target = resolve_workspace_path(root, patch.new_path, allow_root=False,
                                                for_write=True)
        except PathRejectedError as rejected:
            raise PatchRejectedError(rejected.code, str(rejected)) from None
        if patch.old_path is None:
            if target.exists():
                raise PatchRejectedError("PATCH_TARGET_EXISTS",
                                         f"{patch.target} already exists; nothing was changed")
            original: list[str] = []
        else:
            if not target.is_file():
                raise PatchRejectedError("PATCH_TARGET_MISSING",
                                         f"{patch.target} does not exist; nothing was changed")
            try:
                original = target.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                raise PatchRejectedError("PATCH_BINARY_TARGET",
                                         f"{patch.target} is not UTF-8 text") from None
        updated = _apply_hunks(original, patch)
        if patch.new_path is None:
            if updated:
                raise PatchRejectedError("PATCH_MALFORMED",
                                         f"{patch.target}: a deletion must remove every line")
            planned.append((target, None, "deleted"))
        else:
            content = ("\n".join(updated) + ("\n" if updated else "")).encode("utf-8")
            planned.append((target, content, "created" if patch.old_path is None else "modified"))

    written: list[tuple[Path, bytes | None]] = []
    try:
        for target, content, _change in planned:
            previous = target.read_bytes() if target.exists() else None
            if content is None:
                target.unlink()
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                _atomic_write(target, content)
            written.append((target, previous))
    except OSError as error:
        for target, previous in reversed(written):
            if previous is None:
                if target.exists():
                    target.unlink()
            else:
                _atomic_write(target, previous)
        raise PatchRejectedError(
            "PATCH_WRITE_FAILED",
            f"the patch could not be written ({error.strerror}); every file was "
            "restored") from None
    real_root = os.path.realpath(root)
    return [{"path": os.path.relpath(str(target), real_root).replace(os.sep, "/"),
             "change": change} for target, _content, change in planned]
