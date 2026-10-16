"""Consent-bound, secret-scanned ingress to the existing immutable snapshot contract."""

from __future__ import annotations

import asyncio
import gzip
import hashlib
import io
import tarfile
import unicodedata
import uuid
from pathlib import PurePosixPath
from typing import Any

from iacode_common.secret_scanning import find_secret_kinds
from iacode_contracts.desktop import PROTOCOL, DesktopError
from iacode_contracts.sandbox import WORKSPACE_SNAPSHOT_ARTIFACT_KIND
from iacode_persistence.models import Artifact
from sqlalchemy.dialects.postgresql import insert


def excluded(part: str) -> bool:
    name = part.casefold()
    return (
        name in PROTOCOL["excludedDirectories"]
        or name in PROTOCOL["excludedNames"]
        or name.startswith(".env")
        or any(name.endswith(suffix) for suffix in PROTOCOL["excludedSuffixes"])
    )


def safe_path(name: str) -> bool:
    path = PurePosixPath(name)
    if (
        not name
        or len(name.encode("utf-8")) > 240
        or path.is_absolute()
        or not path.parts
        or path.as_posix() != name
        or any(char in name for char in '\\:<>"|?*')
        or unicodedata.normalize("NFC", name) != name
        or any(unicodedata.category(char) in {"Cc", "Cf", "Cs"} for char in name)
    ):
        return False
    reserved = {
        "con",
        "prn",
        "aux",
        "nul",
        *(f"com{i}" for i in range(1, 10)),
        *(f"lpt{i}" for i in range(1, 10)),
    }
    return all(
        part not in {".", ".."}
        and part[-1:] not in {".", " "}
        and not excluded(part)
        and part.split(".")[0].casefold() not in reserved
        for part in path.parts
    )


def snapshot_bytes(files: list[dict[str, str]], expected_digest: str) -> tuple[bytes, str]:
    if not 1 <= len(files) <= PROTOCOL["maxFiles"]:
        raise DesktopError(
            "SNAPSHOT_FILE_COUNT_INVALID", "snapshot file count is outside its bound"
        )
    names: set[str] = set()
    inventory = hashlib.sha256()
    entries: list[tuple[str, bytes]] = []
    total = 0
    for item in sorted(files, key=lambda row: row["path"].encode("utf-8")):
        name = item["path"]
        if not safe_path(name) or name.casefold() in names:
            raise DesktopError(
                "SNAPSHOT_PATH_REFUSED", "snapshot contains an unsafe or ambiguous path"
            )
        names.add(name.casefold())
        content = item["content"].encode("utf-8")
        total += len(content)
        if len(content) > PROTOCOL["maxFileBytes"] or total > PROTOCOL["maxSnapshotBytes"]:
            raise DesktopError("SNAPSHOT_TOO_LARGE", "snapshot exceeds its decoded byte bound")
        # Both exact content and its path are scanned before building, looking up or writing an
        # artifact. There is no desktop false-positive exemption or runtime caller allowance.
        try:
            findings = find_secret_kinds(item["content"]) + find_secret_kinds(name)
        except Exception as error:
            raise DesktopError(
                "SNAPSHOT_SCAN_UNAVAILABLE", "snapshot secret scan failed closed"
            ) from error
        if findings:
            raise DesktopError(
                "SNAPSHOT_SECRET_REFUSED", "snapshot contains prohibited sensitive content"
            )
        inventory.update(
            name.encode("utf-8")
            + b"\0"
            + str(len(content)).encode("ascii")
            + b":"
            + hashlib.sha256(content).hexdigest().encode("ascii")
            + b"\n"
        )
        entries.append((name, content))
    manifest_digest = inventory.hexdigest()
    if manifest_digest != expected_digest:
        raise DesktopError(
            "SNAPSHOT_CONSENT_MISMATCH", "snapshot differs from the approved inventory"
        )
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, content in entries:
            info = tarfile.TarInfo(name)
            info.size = len(content)
            info.mode = 0o644
            info.mtime = 0
            archive.addfile(info, io.BytesIO(content))
    data = gzip.compress(buffer.getvalue(), mtime=0)
    return data, manifest_digest


async def store_snapshot(resources: Any, arguments: dict) -> dict:
    data, manifest_digest = await asyncio.to_thread(
        snapshot_bytes, arguments["files"], arguments["manifestDigest"]
    )
    digest = hashlib.sha256(data).hexdigest()
    identifier = uuid.uuid5(uuid.NAMESPACE_URL, f"iacode:desktop:snapshot:v1:{digest}")
    key = f"sandbox/snapshots/desktop/{digest}.tar.gz"
    # The content-addressed object is written before its pointer is committed. A storage/DB
    # failure cannot authorize a partial snapshot; retrying the same content recovers the same ID.
    await asyncio.to_thread(
        resources.minio.put_object,
        resources.settings.minio_bucket,
        key,
        io.BytesIO(data),
        len(data),
        content_type="application/gzip",
    )
    async with resources.session_factory() as session, session.begin():
        await session.execute(
            insert(Artifact)
            .values(
                id=identifier,
                kind=WORKSPACE_SNAPSHOT_ARTIFACT_KIND,
                storage_bucket=resources.settings.minio_bucket,
                storage_key=key,
                content_type="application/gzip",
                size_bytes=len(data),
                checksum_sha256=digest,
                metadata_={
                    "source": "desktop",
                    "manifestDigest": manifest_digest,
                    "trainingAllowed": False,
                },
            )
            .on_conflict_do_nothing(index_elements=[Artifact.id])
        )
        row = await session.get(Artifact, identifier)
        if (
            row is None
            or row.checksum_sha256 != digest
            or row.storage_key != key
            or row.kind != WORKSPACE_SNAPSHOT_ARTIFACT_KIND
        ):
            raise DesktopError("SNAPSHOT_IDENTITY_CONFLICT", "snapshot identity cannot be reused")
    return {
        "snapshotId": str(identifier),
        "snapshotDigest": digest,
        "manifestDigest": manifest_digest,
        "sizeBytes": len(data),
        "fileCount": len(arguments["files"]),
        "trainingAllowed": False,
    }


async def authorize_snapshot(resources: Any, identifier: str, digest: str | None = None) -> None:
    async with resources.session_factory() as session:
        row = await session.get(Artifact, uuid.UUID(identifier))
    if (
        row is None
        or row.kind != WORKSPACE_SNAPSHOT_ARTIFACT_KIND
        or row.metadata_.get("source") != "desktop"
        or row.metadata_.get("trainingAllowed") is not False
    ):
        raise DesktopError("SNAPSHOT_NOT_AUTHORISED", "a consented desktop snapshot is required")
    if digest is not None and digest != row.checksum_sha256:
        raise DesktopError(
            "SNAPSHOT_DIGEST_MISMATCH", "snapshot digest differs from its stored identity"
        )
    # The existing reader re-hashes the actual object before use; ingestion cannot substitute a
    # UUID that exists but names unrelated or tampered bytes.
    await resources.quality.snapshots.read(identifier, row.checksum_sha256)
