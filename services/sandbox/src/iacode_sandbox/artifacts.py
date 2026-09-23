"""Where what did not fit inline goes: the Foundation's object store, not a new one.

A tool result is shown to a model, and a model's context is not a log file. A command that printed
four megabytes returns its first ``outputBytes`` inline, says it was truncated, and names an
artifact holding the rest. The artifact is an object in the bucket the Foundation already runs
(``IACODE_MINIO_BUCKET``) and a row in the ``artifacts`` table Gate 0 created for exactly this — no
second storage, no second metadata table.
"""

from __future__ import annotations

import hashlib
import io
from typing import Any, Protocol

from iacode_sandbox.contracts import ArtifactReference

__all__ = ["ArtifactSink", "MemoryArtifactSink", "MinioArtifactSink"]


class ArtifactSink(Protocol):
    async def put(self, *, run_id: str, tool_request_id: str, name: str, content: bytes,
                  kind: str, content_type: str = "text/plain; charset=utf-8"
                  ) -> ArtifactReference: ...


def _key(run_id: str, tool_request_id: str, name: str) -> str:
    return f"sandbox/{run_id}/{tool_request_id}/{name}"


class MemoryArtifactSink:
    """The sink the service's suite runs with: it keeps the bytes and records the row."""

    def __init__(self, store: Any, bucket: str = "iacode-artifacts") -> None:
        self.store = store
        self.bucket = bucket
        self.objects: dict[str, bytes] = {}

    async def put(self, *, run_id: str, tool_request_id: str, name: str, content: bytes,
                  kind: str, content_type: str = "text/plain; charset=utf-8"
                  ) -> ArtifactReference:
        key = _key(run_id, tool_request_id, name)
        self.objects[key] = content
        digest = hashlib.sha256(content).hexdigest()
        identifier = await self.store.record_artifact(
            run_id=run_id, kind=kind, bucket=self.bucket, key=key, content_type=content_type,
            size_bytes=len(content), sha256=digest)
        return ArtifactReference(artifact_id=identifier, kind=kind, bucket=self.bucket, key=key,
                                 size_bytes=len(content), sha256=digest,
                                 content_type=content_type)


class MinioArtifactSink:
    """Objects in the Foundation's MinIO bucket, rows in ``artifacts``."""

    def __init__(self, client: Any, bucket: str, store: Any) -> None:
        self.client = client
        self.bucket = bucket
        self.store = store

    async def put(self, *, run_id: str, tool_request_id: str, name: str, content: bytes,
                  kind: str, content_type: str = "text/plain; charset=utf-8"
                  ) -> ArtifactReference:
        import asyncio

        key = _key(run_id, tool_request_id, name)
        digest = hashlib.sha256(content).hexdigest()
        await asyncio.to_thread(self.client.put_object, self.bucket, key, io.BytesIO(content),
                                len(content), content_type=content_type,
                                metadata={"sha256": digest})
        identifier = await self.store.record_artifact(
            run_id=run_id, kind=kind, bucket=self.bucket, key=key, content_type=content_type,
            size_bytes=len(content), sha256=digest)
        return ArtifactReference(artifact_id=identifier, kind=kind, bucket=self.bucket, key=key,
                                 size_bytes=len(content), sha256=digest,
                                 content_type=content_type)
