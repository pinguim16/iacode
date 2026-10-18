"""Read-only curated admission and the owning storage-only experience permission boundary."""

from __future__ import annotations

import asyncio
import hashlib
import os
import stat
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from iacode_contracts.knowledge import CuratedArtifact, KnowledgePolicy, SourceGrant, SourceRegistry
from iacode_experience.domain import ExperienceError
from iacode_knowledge.domain import (
    AdmittedSource,
    KnowledgeError,
    decode,
    validate_grant,
    validate_source,
)


def read_confined(root: Path, relative: str, maximum: int) -> bytes:
    """Open bounded regular files only; paths are deployment data, never HTTP-provided paths."""
    if "\\" in relative or "\x00" in relative or ":" in relative:
        raise KnowledgeError("SOURCE_PATH_REFUSED")
    parts = tuple(relative.split("/"))
    if (
        not parts
        or PurePosixPath(relative).is_absolute()
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise KnowledgeError("SOURCE_PATH_REFUSED")
    try:
        if root.is_symlink() or root.is_junction() or str(root.drive).startswith("\\"):
            raise KnowledgeError("SOURCE_PATH_REFUSED")
        if any(parent.is_symlink() or parent.is_junction() for parent in root.parents):
            raise KnowledgeError("SOURCE_PATH_REFUSED")
        canonical_root = root.resolve(strict=True)
        cursor = root
        for part in parts:
            cursor = cursor / part
            if cursor.is_symlink() or cursor.is_junction():
                raise KnowledgeError("SOURCE_PATH_REFUSED")
        resolved = cursor.resolve(strict=True)
        if not resolved.is_relative_to(canonical_root) or resolved == canonical_root:
            raise KnowledgeError("SOURCE_PATH_REFUSED")
        before = cursor.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise KnowledgeError("SOURCE_PATH_REFUSED")
        if before.st_size > maximum:
            raise KnowledgeError("SOURCE_LIMIT_EXCEEDED")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        flags |= getattr(os, "O_BINARY", 0) | getattr(os, "O_NOINHERIT", 0)
        descriptor = os.open(cursor, flags)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (
                before.st_dev,
                before.st_ino,
            ):
                raise KnowledgeError("SOURCE_CHANGED")
            raw = stream.read(maximum + 1)
            after = os.fstat(stream.fileno())
        final = cursor.lstat()

        def identity(value: os.stat_result) -> tuple[int, int, int, int]:
            return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns

        if identity(before) != identity(after) or identity(after) != identity(final):
            raise KnowledgeError("SOURCE_CHANGED")
        if len(raw) > maximum:
            raise KnowledgeError("SOURCE_LIMIT_EXCEEDED")
        return raw
    except KnowledgeError:
        raise
    except FileNotFoundError as error:
        raise KnowledgeError("SOURCE_OBJECT_UNAVAILABLE") from error
    except OSError as error:
        raise KnowledgeError("SOURCE_STORE_UNAVAILABLE") from error


class CurrentKnowledgeSources:
    def __init__(
        self,
        root: Path,
        policy: KnowledgePolicy,
        experience: Any,
        known_credentials: tuple[str, ...],
    ) -> None:
        self.root = root
        self.policy = policy
        self.experience = experience
        self.known_credentials = known_credentials

    def _load_curated(
        self, project: str, source: str, revision: str, now: datetime, *, capture: bool
    ) -> AdmittedSource:
        registry_raw = read_confined(self.root, "registry.json", self.policy.maxRegistryBytes)
        registry = decode(
            registry_raw, SourceRegistry, self.policy.maxRegistryBytes, self.known_credentials
        )
        if len(registry.sources) > self.policy.maxSources:
            raise KnowledgeError("SOURCE_LIMIT_EXCEEDED")
        entries = [
            entry
            for entry in registry.sources
            if entry.projectId == project and entry.sourceId == source
        ]
        if not entries:
            raise KnowledgeError("SOURCE_NOT_FOUND")
        entry = entries[0]
        if entry.revision != revision:
            raise KnowledgeError("SOURCE_CHANGED")
        if not entry.grantPath.startswith("grants/") or not entry.artifactPath.startswith(
            "artifacts/"
        ):
            raise KnowledgeError("SOURCE_PATH_REFUSED")
        if not entry.grantPath.endswith(".json") or not entry.artifactPath.endswith(".json"):
            raise KnowledgeError("SOURCE_PATH_REFUSED")
        grant_raw = read_confined(self.root, entry.grantPath, self.policy.maxRegistryBytes)
        if hashlib.sha256(grant_raw).hexdigest() != entry.grantDigest:
            raise KnowledgeError("SOURCE_CHANGED")
        grant = decode(grant_raw, SourceGrant, self.policy.maxRegistryBytes, self.known_credentials)
        # Permission is checked before the source's content is even read into this adapter.
        validate_grant(entry, grant, project, self.policy, now)
        artifact_raw = read_confined(self.root, entry.artifactPath, self.policy.maxSourceBytes)
        if hashlib.sha256(artifact_raw).hexdigest() != entry.sourceDigest:
            raise KnowledgeError("SOURCE_CHANGED")
        artifact = decode(
            artifact_raw, CuratedArtifact, self.policy.maxSourceBytes, self.known_credentials
        )
        admitted = AdmittedSource(entry, artifact, grant)
        validate_source(admitted, project, self.policy, now, capture=capture)
        if read_confined(self.root, "registry.json", self.policy.maxRegistryBytes) != registry_raw:
            raise KnowledgeError("SOURCE_CHANGED")
        # Re-read exact content-addressed inputs, refusing a mixed observation during publication.
        if (
            read_confined(self.root, entry.grantPath, self.policy.maxRegistryBytes) != grant_raw
            or read_confined(self.root, entry.artifactPath, self.policy.maxSourceBytes)
            != artifact_raw
        ):
            raise KnowledgeError("SOURCE_CHANGED")
        return admitted

    async def load(
        self, project: str, kind: str, source: str, revision: str, now: datetime, *, capture: bool
    ) -> AdmittedSource:
        if kind == "curated":
            return await asyncio.to_thread(
                self._load_curated, project, source, revision, now, capture=capture
            )
        if kind != "experience":
            raise KnowledgeError("SOURCE_KIND_UNSUPPORTED")
        try:
            stored = await self.experience.store.get(project, source)
            document = await self.experience.service.deliver(stored, now)
        except ExperienceError as error:
            raise KnowledgeError("EXPERIENCE_SOURCE_UNAVAILABLE") from error
        if revision != stored.content_digest:
            raise KnowledgeError("SOURCE_CHANGED")
        if any(not row.ragAllowed or not row.storageAllowed for row in document.provenance):
            raise KnowledgeError("REUSE_PERMISSION_DENIED")
        # Current Gate6 contracts have no rights-qualified positive representation. A future
        # source schema needs its own explicit adapter; no grant or body is fabricated here.
        raise KnowledgeError("SOURCE_FORMAT_UNSUPPORTED")
