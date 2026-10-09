"""Read a bounded project manifest from an authorised immutable workspace snapshot."""

from __future__ import annotations

import asyncio
import hashlib
import io
import tarfile
import uuid
from pathlib import PurePosixPath
from typing import Any

from iacode_contracts.sandbox import WORKSPACE_SNAPSHOT_ARTIFACT_KIND

from iacode_evaluator.errors import QualityError

MAX_PROJECT_FILE_BYTES = 2 * 1024 * 1024
MAX_PROJECT_TOTAL_BYTES = 64 * 1024 * 1024


class SnapshotProjectReader:
    def __init__(self, session_factory: Any, client: Any) -> None:
        self.session_factory = session_factory
        self.client = client

    async def read(self, artifact_id: str, checksum: str) -> dict[str, str | bytes]:
        from iacode_persistence.models import Artifact

        try:
            identifier = uuid.UUID(artifact_id)
        except ValueError:
            raise QualityError("SNAPSHOT_ID_INVALID", "snapshotId must be a UUID") from None
        async with self.session_factory() as session:
            row = await session.get(Artifact, identifier)
        if row is None or row.kind != WORKSPACE_SNAPSHOT_ARTIFACT_KIND:
            raise QualityError(
                "SNAPSHOT_NOT_AUTHORISED", "the snapshot is not an authorised workspace artifact"
            )
        if checksum != row.checksum_sha256:
            raise QualityError(
                "SNAPSHOT_CHECKSUM_MISMATCH", "snapshotDigest differs from the stored artifact"
            )

        def download() -> bytes:
            response = self.client.get_object(row.storage_bucket, row.storage_key)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        archive_bytes = await asyncio.to_thread(download)
        if hashlib.sha256(archive_bytes).hexdigest() != checksum:
            raise QualityError("SNAPSHOT_CORRUPT", "the stored snapshot digest does not match")
        return await asyncio.to_thread(self._files, archive_bytes)

    @staticmethod
    def _files(archive_bytes: bytes) -> dict[str, str | bytes]:
        files: dict[str, str | bytes] = {}
        total = 0
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
            for member in archive.getmembers():
                path = PurePosixPath(member.name)
                if (
                    not member.isfile()
                    or path.is_absolute()
                    or ".." in path.parts
                    or member.size > MAX_PROJECT_FILE_BYTES
                ):
                    continue
                total += member.size
                if total > MAX_PROJECT_TOTAL_BYTES:
                    raise QualityError("SNAPSHOT_TOO_LARGE", "snapshot files exceed the read bound")
                source = archive.extractfile(member)
                if source is None:
                    continue
                content = source.read()
                try:
                    files[path.as_posix()] = content.decode("utf-8")
                except UnicodeDecodeError:
                    files[path.as_posix()] = content
        if not files:
            raise QualityError("SNAPSHOT_EMPTY", "the snapshot contains no bounded regular files")
        return files


__all__ = ["SnapshotProjectReader"]
