"""The MinIO object-storage client.

Gate 0 proves that object storage exists, that the bucket the later Gates will write into is there,
and that a real object survives a write, a read and a delete. The Artifact Service belongs to a
later Gate; this module is the connection and nothing more.

The MinIO SDK is synchronous. Calling it directly from a coroutine would block the event loop for
the duration of a network round trip, so every call here goes through :func:`asyncio.to_thread`.
That is the honest adaptation: pretending the SDK is async by wrapping it in a coroutine that still
blocks is how an event loop stalls under load with no obvious cause.
"""

from __future__ import annotations

import asyncio
import io

from minio import Minio

from iacode_api.config import Settings


def create_client(settings: Settings) -> Minio:
    """Build the client. It performs no I/O, so a down MinIO does not prevent startup."""
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key.get_secret_value(),
        secret_key=settings.minio_secret_key.get_secret_value(),
        secure=settings.minio_secure,
    )


async def ping(client: Minio, bucket: str) -> None:
    """Prove object storage answers *and* that the bucket exists.

    Checking the bucket rather than merely listing buckets is deliberate: a MinIO that is up but
    whose bootstrap never ran cannot store an artifact, and readiness is about accepting work.
    """
    exists = await asyncio.to_thread(client.bucket_exists, bucket)
    if not exists:
        raise RuntimeError(f"object storage bucket {bucket!r} does not exist")


async def ensure_bucket(client: Minio, bucket: str) -> bool:
    """Create the bucket when it is missing. Returns whether this call created it.

    Idempotent by construction: the existence check and the creation are separate calls, and a
    concurrent creation surfaces as ``BucketAlreadyOwnedByYou``, which is treated as success
    because the post-condition the caller wants is satisfied either way.
    """
    from minio.error import S3Error

    if await asyncio.to_thread(client.bucket_exists, bucket):
        return False
    try:
        await asyncio.to_thread(client.make_bucket, bucket)
    except S3Error as error:
        if error.code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            return False
        raise
    return True


async def put_object(client: Minio, bucket: str, key: str, data: bytes,
                     content_type: str = "application/octet-stream") -> None:
    await asyncio.to_thread(
        client.put_object, bucket, key, io.BytesIO(data), len(data), content_type)


async def get_object(client: Minio, bucket: str, key: str) -> bytes:
    def _read() -> bytes:
        response = client.get_object(bucket, key)
        try:
            return response.read()
        finally:
            # Both are required: ``close`` ends the stream and ``release_conn`` returns the socket
            # to urllib3's pool. Skipping the second leaks a connection per read.
            response.close()
            response.release_conn()

    return await asyncio.to_thread(_read)


async def remove_object(client: Minio, bucket: str, key: str) -> None:
    await asyncio.to_thread(client.remove_object, bucket, key)
