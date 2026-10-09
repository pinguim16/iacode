"""Bounded, non-executing project profile detection."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from iacode_evaluator.canonical import digest
from iacode_evaluator.errors import QualityError

MAX_MANIFEST_BYTES = 256 * 1024
IGNORED_PARTS = frozenset(
    {
        ".git",
        ".gradle",
        ".mvn",
        ".venv",
        "build",
        "dist",
        "node_modules",
        "target",
        "vendor",
    }
)
STACK_MARKERS: dict[str, tuple[str, ...]] = {
    "angular": ("angular.json",),
    "typescript": ("tsconfig.json",),
    "node": ("package.json",),
    "python": ("pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Pipfile"),
    "maven": ("pom.xml",),
    "gradle": ("build.gradle", "build.gradle.kts", "gradlew"),
}
STACK_ORDER = ("python", "node", "typescript", "angular", "maven", "gradle")


@dataclass(frozen=True)
class ProjectProfile:
    profile_id: str
    stacks: tuple[str, ...]
    manifests: tuple[str, ...]
    confidence: str
    ambiguities: tuple[str, ...]
    configuration_source: str | None
    digest: str


def _safe_relative(value: str) -> str:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise QualityError("PROJECT_PATH_INVALID", f"project path is not relative: {value!r}")
    if any(part in IGNORED_PARTS for part in path.parts):
        raise QualityError(
            "PROJECT_PATH_IGNORED", f"generated or vendor path is not inspected: {value!r}"
        )
    return path.as_posix()


def detect_project(files: Mapping[str, bytes | str]) -> ProjectProfile:
    """Detect from a bounded snapshot inventory; never execute or import its content."""
    safe: dict[str, int] = {}
    for raw_path, content in files.items():
        try:
            path = _safe_relative(raw_path)
        except QualityError as error:
            if error.code == "PROJECT_PATH_IGNORED":
                continue
            raise
        size = len(content.encode("utf-8")) if isinstance(content, str) else len(content)
        if size > MAX_MANIFEST_BYTES:
            raise QualityError("PROJECT_MANIFEST_TOO_LARGE", f"{path!r} exceeds manifest limit")
        safe[path] = size

    basenames = {PurePosixPath(path).name: path for path in sorted(safe)}
    found = tuple(
        stack
        for stack in STACK_ORDER
        if any(marker in basenames for marker in STACK_MARKERS[stack])
    )
    manifests = tuple(
        sorted(
            {
                basenames[marker]
                for stack in found
                for marker in STACK_MARKERS[stack]
                if marker in basenames
            }
        )
    )
    if not found:
        confidence = "UNSUPPORTED"
        profile_id = "unsupported"
        ambiguities = ("no supported toolchain manifest was found",)
    else:
        confidence = "HIGH"
        profile_id = "+".join(found)
        ambiguities_list: list[str] = []
        if "maven" in found and "gradle" in found:
            confidence = "AMBIGUOUS"
            ambiguities_list.append("both Maven and Gradle manifests are present")
        ambiguities = tuple(ambiguities_list)
    configuration = basenames.get("iacode-quality.json")
    content = {
        "profile": profile_id,
        "stacks": found,
        "manifests": manifests,
        "confidence": confidence,
        "ambiguities": ambiguities,
        "configuration": configuration,
    }
    return ProjectProfile(
        profile_id, found, manifests, confidence, ambiguities, configuration, digest(content)
    )


def inventory_project(root: Path) -> dict[str, bytes]:
    """Read manifest candidates under ``root`` without following links outside it."""
    resolved_root = root.resolve(strict=True)
    inventory: dict[str, bytes] = {}
    markers = {item for values in STACK_MARKERS.values() for item in values} | {
        "iacode-quality.json",
    }
    for current, directories, filenames in os.walk(resolved_root, followlinks=False):
        current_path = Path(current)
        directories[:] = [
            name
            for name in directories
            if name not in IGNORED_PARTS and not (current_path / name).is_symlink()
        ]
        for name in filenames:
            if name not in markers:
                continue
            path = current_path / name
            if path.is_symlink():
                raise QualityError("PROJECT_SYMLINK_REFUSED", f"manifest is a symlink: {path}")
            resolved = path.resolve(strict=True)
            try:
                relative = resolved.relative_to(resolved_root).as_posix()
            except ValueError:
                raise QualityError(
                    "PROJECT_PATH_ESCAPE", f"manifest escapes project: {path}"
                ) from None
            data = resolved.read_bytes()
            if len(data) > MAX_MANIFEST_BYTES:
                raise QualityError("PROJECT_MANIFEST_TOO_LARGE", f"{relative!r} exceeds limit")
            inventory[relative] = data
    return inventory
