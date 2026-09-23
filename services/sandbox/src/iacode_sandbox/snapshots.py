"""Authorised workspace snapshots: the only way content from outside reaches a sandbox.

A sandbox is never given the host's filesystem. What a run works on is a **snapshot**: a tar archive
of a directory an operator chose, stored as an object in the Foundation's bucket with a row in
``artifacts`` of kind ``sandbox.workspace-snapshot`` and its SHA-256. A run names the snapshot's
artifact identifier; the service reads the object, checks the digest, and hands the archive to the
helper, which extracts it with the standard library's ``data`` filter after refusing links, devices,
absolute names and escapes itself.

So the development tree an operator works in is never the tree an agent works in. The agent gets a
copy, in a container, and nothing it does to the copy reaches the original.

    python -m iacode_sandbox.snapshots create --source /input --name synthetic-calculator

The command runs inside the sandbox service's image, where the database and the bucket are
reachable, with the source directory mounted read-only by ``scripts/iacode/sandbox_snapshot.py``.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import io
import json
import os
import sys
import tarfile
import uuid
from pathlib import Path
from typing import Any

from iacode_contracts.sandbox import WORKSPACE_SNAPSHOT_ARTIFACT_KIND

__all__ = ["SnapshotError", "SnapshotReader", "build_snapshot"]

#: Directories never copied into a snapshot: version-control internals, caches and dependencies.
EXCLUDED_DIRECTORIES = frozenset({".git", "__pycache__", "node_modules", ".venv", "venv",
                                  ".pytest_cache", ".ruff_cache", ".mypy_cache"})

#: The largest snapshot the tool builds. A workspace is a tmpfs of a few hundred megabytes.
MAX_SNAPSHOT_BYTES = 64 * 1024 * 1024


class SnapshotError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def build_snapshot(source: Path, *, max_bytes: int = MAX_SNAPSHOT_BYTES) -> bytes:
    """A deterministic gzip tar of ``source``'s regular files. Links and special files refused."""
    if not source.is_dir():
        raise SnapshotError("SNAPSHOT_SOURCE_INVALID", f"{source} is not a directory")
    buffer = io.BytesIO()
    total = 0
    with tarfile.open(fileobj=buffer, mode="w:gz", format=tarfile.PAX_FORMAT) as archive:
        for current, directories, files in os.walk(source, followlinks=False):
            directories[:] = sorted(item for item in directories
                                    if item not in EXCLUDED_DIRECTORIES)
            for name in sorted(files):
                path = Path(current) / name
                relative = path.relative_to(source).as_posix()
                if path.is_symlink():
                    raise SnapshotError("SNAPSHOT_SOURCE_UNSAFE",
                                        f"{relative} is a link; a snapshot carries regular files")
                if not path.is_file():
                    continue
                total += path.stat().st_size
                if total > max_bytes:
                    raise SnapshotError("SNAPSHOT_TOO_LARGE",
                                        f"the source exceeds {max_bytes} bytes")
                info = tarfile.TarInfo(relative)
                content = path.read_bytes()
                info.size = len(content)
                info.mode = 0o644
                info.mtime = 0
                archive.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


class SnapshotReader:
    """Reads a snapshot back, refusing anything that is not an intact authorised snapshot."""

    def __init__(self, session_factory: Any, client: Any) -> None:
        self.session_factory = session_factory
        self.client = client

    async def read(self, artifact_id: str, checksum: str | None = None) -> bytes:
        from iacode_persistence.models import Artifact

        async with self.session_factory() as session:
            row = await session.get(Artifact, uuid.UUID(artifact_id))
        if row is None or row.kind != WORKSPACE_SNAPSHOT_ARTIFACT_KIND:
            raise SnapshotError("SNAPSHOT_NOT_AUTHORISED",
                                f"{artifact_id} is not an authorised workspace snapshot")
        if checksum and checksum != row.checksum_sha256:
            raise SnapshotError("SNAPSHOT_CHECKSUM_MISMATCH",
                                "the run names a different digest than the snapshot carries")

        def download() -> bytes:
            response = self.client.get_object(row.storage_bucket, row.storage_key)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        data = await asyncio.to_thread(download)
        if hashlib.sha256(data).hexdigest() != row.checksum_sha256:
            raise SnapshotError("SNAPSHOT_CORRUPT",
                                "the stored snapshot does not match its recorded digest")
        return data


async def _create(source: Path, name: str) -> dict[str, Any]:
    from iacode_persistence.engine import create_engine, create_session_factory
    from iacode_persistence.models import Artifact

    from iacode_sandbox.config import get_sandbox_settings, minio_client

    settings = get_sandbox_settings()
    data = build_snapshot(source)
    digest = hashlib.sha256(data).hexdigest()
    key = f"sandbox/snapshots/{digest[:16]}-{name}.tar.gz"
    client = minio_client(settings)
    await asyncio.to_thread(client.put_object, settings.minio_bucket, key, io.BytesIO(data),
                            len(data), content_type="application/gzip",
                            metadata={"sha256": digest})
    engine = create_engine(settings.database_url)
    factory = create_session_factory(engine)
    try:
        async with factory() as session, session.begin():
            row = Artifact(kind=WORKSPACE_SNAPSHOT_ARTIFACT_KIND,
                           storage_bucket=settings.minio_bucket, storage_key=key,
                           content_type="application/gzip", size_bytes=len(data),
                           checksum_sha256=digest, metadata_={"name": name})
            existing = None
            from sqlalchemy import select

            existing = (await session.execute(
                select(Artifact).where(Artifact.storage_key == key))).scalars().first()
            if existing is None:
                session.add(row)
                await session.flush()
                identifier = str(row.id)
            else:
                identifier = str(existing.id)
    finally:
        await engine.dispose()
    return {"artifactId": identifier, "sha256": digest, "sizeBytes": len(data), "key": key}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create", help="archive a directory as an authorised snapshot")
    create.add_argument("--source", type=Path, required=True)
    create.add_argument("--name", required=True)
    arguments = parser.parse_args(argv)
    try:
        result = asyncio.run(_create(arguments.source, arguments.name))
    except SnapshotError as error:
        print(json.dumps({"error": error.code, "detail": str(error)}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
