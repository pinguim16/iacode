"""Immutable content-addressed quality evidence over the existing artifact store."""

from __future__ import annotations

import asyncio
import hashlib
import io
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from iacode_contracts.quality import QualityEvidence
from minio.error import S3Error

from iacode_evaluator.errors import QualityError

MAX_INLINE_SUMMARY_BYTES = 4096
REDACTION = re.compile(r"(?i)(api[_-]?key|password|secret|token)(\s*[:=]\s*)[^\s,;]+")
MISSING_OBJECT_CODES = frozenset({"NoSuchKey", "NoSuchObject"})


def _object_missing(error: Exception) -> bool:
    return isinstance(error, (KeyError, OSError)) or (
        isinstance(error, S3Error) and error.code in MISSING_OBJECT_CODES
    )


@dataclass(frozen=True)
class EvidenceRecord:
    contract: QualityEvidence
    bucket: str
    key: str
    run_id: str
    result_id: str | None = None


class EvidenceRepository(Protocol):
    async def by_digest(self, run_id: str, digest: str) -> EvidenceRecord | None: ...

    async def by_evidence_id(self, evidence_id: str) -> EvidenceRecord | None: ...

    async def record(self, record: EvidenceRecord) -> EvidenceRecord: ...


class MemoryEvidenceRepository:
    def __init__(self) -> None:
        self.records: dict[tuple[str, str], EvidenceRecord] = {}

    async def by_digest(self, run_id: str, digest: str) -> EvidenceRecord | None:
        return self.records.get((run_id, digest))

    async def by_evidence_id(self, evidence_id: str) -> EvidenceRecord | None:
        return next(
            (
                record
                for record in self.records.values()
                if record.contract.evidenceId == evidence_id
            ),
            None,
        )

    async def record(self, record: EvidenceRecord) -> EvidenceRecord:
        key = (record.run_id, record.contract.digest)
        existing = self.records.get(key)
        if existing is not None:
            if existing != record:
                raise QualityError(
                    "EVIDENCE_DIGEST_COLLISION",
                    "the evidence digest is already bound to different metadata",
                )
            return existing
        self.records[key] = record
        return record


class MemoryObjectStore:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], bytes] = {}

    def stat_object(self, bucket: str, key: str) -> object:
        if (bucket, key) not in self.objects:
            raise KeyError(key)
        return object()

    def put_object(
        self,
        bucket: str,
        key: str,
        data: io.BytesIO,
        length: int,
        **_options: Any,
    ) -> None:
        content = data.read()
        if len(content) != length:
            raise ValueError("object length differs from declared length")
        self.objects[(bucket, key)] = content

    def get_object(self, bucket: str, key: str) -> io.BytesIO:
        return io.BytesIO(self.objects[(bucket, key)])


def inline_summary(value: str, limit: int = MAX_INLINE_SUMMARY_BYTES) -> str:
    """Redact credential-shaped values and bound the exact UTF-8 representation."""
    redacted = REDACTION.sub(r"\1\2[REDACTED]", value)
    payload = redacted.encode("utf-8")
    if len(payload) <= limit:
        return redacted
    marker = b"\n[... full output stored as quality evidence ...]"
    kept = payload[: max(0, limit - len(marker))]
    while True:
        try:
            return (kept + marker).decode("utf-8")
        except UnicodeDecodeError:
            kept = kept[:-1]


class QualityEvidenceStore:
    def __init__(
        self,
        *,
        client: Any,
        bucket: str,
        repository: EvidenceRepository,
        now: Any = None,
    ) -> None:
        self.client = client
        self.bucket = bucket
        self.repository = repository
        self.now = now or (lambda: datetime.now(UTC))

    async def _read(self, key: str) -> bytes:
        def download() -> bytes:
            response = self.client.get_object(self.bucket, key)
            try:
                return response.read()
            finally:
                close = getattr(response, "close", None)
                if close:
                    close()
                release = getattr(response, "release_conn", None)
                if release:
                    release()

        try:
            return await asyncio.to_thread(download)
        except Exception as error:
            if _object_missing(error):
                raise QualityError(
                    "EVIDENCE_MISSING", "the evidence object does not exist"
                ) from error
            raise QualityError(
                "EVIDENCE_STORE_UNAVAILABLE", "the evidence object store could not be read"
            ) from error

    async def put(
        self,
        *,
        run_id: str,
        result_id: str | None,
        kind: str,
        content: bytes,
        media_type: str,
        producer: str,
        source_digests: tuple[str, ...] = (),
    ) -> QualityEvidence:
        digest = hashlib.sha256(content).hexdigest()
        existing = await self.repository.by_digest(run_id, digest)
        if existing is not None:
            if await self._read(existing.key) != content:
                raise QualityError(
                    "EVIDENCE_DIGEST_COLLISION", "existing evidence bytes differ for the digest"
                )
            if (
                existing.run_id != run_id
                or existing.result_id != result_id
                or existing.contract.kind != kind
                or existing.contract.mediaType != media_type
                or existing.contract.producer != producer
                or existing.contract.sourceDigests != source_digests
            ):
                raise QualityError(
                    "EVIDENCE_METADATA_CONFLICT",
                    "the evidence digest is already bound to different immutable metadata",
                )
            return existing.contract

        key = f"quality/evidence/{digest}"
        object_exists = False
        try:
            await asyncio.to_thread(self.client.stat_object, self.bucket, key)
            object_exists = True
        except Exception as error:
            if not _object_missing(error):
                raise QualityError(
                    "EVIDENCE_STORE_UNAVAILABLE", "the evidence object store could not be read"
                ) from error
        if object_exists:
            stored = await self._read(key)
            if stored != content:
                raise QualityError(
                    "EVIDENCE_DIGEST_COLLISION", "stored evidence bytes differ for the digest"
                )
        else:
            await asyncio.to_thread(
                self.client.put_object,
                self.bucket,
                key,
                io.BytesIO(content),
                len(content),
                content_type=media_type,
                metadata={"sha256": digest},
            )
        contract = QualityEvidence(
            evidenceId=str(uuid.uuid4()),
            kind=kind,
            artifactId=str(uuid.uuid4()),
            digest=digest,
            sizeBytes=len(content),
            mediaType=media_type,
            producer=producer,
            sourceDigests=source_digests,
            createdAt=self.now(),
        )
        record = EvidenceRecord(
            contract=contract,
            bucket=self.bucket,
            key=key,
            run_id=run_id,
            result_id=result_id,
        )
        return (await self.repository.record(record)).contract

    async def resolve(self, evidence: QualityEvidence) -> bool:
        record = await self.repository.by_evidence_id(evidence.evidenceId)
        if record is None or record.contract != evidence:
            return False
        try:
            content = await self._read(record.key)
        except QualityError:
            return False
        return (
            len(content) == evidence.sizeBytes
            and hashlib.sha256(content).hexdigest() == evidence.digest
        )


class SqlEvidenceRepository:
    """Atomic artifact-row and evidence-row persistence over the shared schema."""

    def __init__(self, session_factory: Any) -> None:
        self.session_factory = session_factory

    @staticmethod
    def _record(row: Any) -> EvidenceRecord:
        artifact = row.artifact
        contract = QualityEvidence(
            evidenceId=row.evidence_id,
            kind=row.kind,
            artifactId=str(row.artifact_id),
            digest=row.digest,
            sizeBytes=row.size_bytes,
            mediaType=row.media_type,
            producer=row.producer,
            sourceDigests=tuple(row.source_digests),
            createdAt=row.created_at,
            retentionClass=row.retention_class,
            storageAllowed=row.storage_allowed,
            ragAllowed=row.rag_allowed,
            trainingAllowed=row.training_allowed,
            distillationAllowed=row.distillation_allowed,
        )
        return EvidenceRecord(
            contract=contract,
            bucket=artifact.storage_bucket,
            key=artifact.storage_key,
            run_id=str(row.quality_run_id),
            result_id=row.result.result_id if row.result else None,
        )

    async def by_digest(self, run_id: str, digest: str) -> EvidenceRecord | None:
        from iacode_persistence.models import QualityEvidence as QualityEvidenceRow
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        statement = (
            select(QualityEvidenceRow)
            .options(
                selectinload(QualityEvidenceRow.artifact),
                selectinload(QualityEvidenceRow.result),
            )
            .where(
                QualityEvidenceRow.quality_run_id == uuid.UUID(run_id),
                QualityEvidenceRow.digest == digest,
            )
        )
        async with self.session_factory() as session:
            row = (await session.execute(statement)).scalars().first()
        return self._record(row) if row else None

    async def by_evidence_id(self, evidence_id: str) -> EvidenceRecord | None:
        from iacode_persistence.models import QualityEvidence as QualityEvidenceRow
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        statement = (
            select(QualityEvidenceRow)
            .options(
                selectinload(QualityEvidenceRow.artifact),
                selectinload(QualityEvidenceRow.result),
            )
            .where(QualityEvidenceRow.evidence_id == evidence_id)
        )
        async with self.session_factory() as session:
            row = (await session.execute(statement)).scalars().first()
        return self._record(row) if row else None

    async def record(self, record: EvidenceRecord) -> EvidenceRecord:
        from iacode_persistence.models import Artifact
        from iacode_persistence.models import QualityEvidence as QualityEvidenceRow
        from iacode_persistence.models import QualityResult as QualityResultRow
        from sqlalchemy import select
        from sqlalchemy.exc import IntegrityError

        contract = record.contract
        try:
            async with self.session_factory() as session, session.begin():
                artifact = (
                    (
                        await session.execute(
                            select(Artifact).where(
                                Artifact.storage_bucket == record.bucket,
                                Artifact.storage_key == record.key,
                            )
                        )
                    )
                    .scalars()
                    .first()
                )
                if artifact is None:
                    artifact = Artifact(
                        id=uuid.UUID(contract.artifactId),
                        task_run_id=None,
                        kind=f"quality.{contract.kind}",
                        storage_bucket=record.bucket,
                        storage_key=record.key,
                        content_type=contract.mediaType,
                        size_bytes=contract.sizeBytes,
                        checksum_sha256=contract.digest,
                    )
                    session.add(artifact)
                    await session.flush()
                elif (
                    artifact.checksum_sha256 != contract.digest
                    or artifact.size_bytes != contract.sizeBytes
                    or artifact.content_type != contract.mediaType
                ):
                    raise QualityError(
                        "EVIDENCE_METADATA_CONFLICT",
                        "the content-addressed artifact has conflicting metadata",
                    )
                stored_contract = contract.model_copy(update={"artifactId": str(artifact.id)})
                stored_record = EvidenceRecord(
                    contract=stored_contract,
                    bucket=record.bucket,
                    key=record.key,
                    run_id=record.run_id,
                    result_id=record.result_id,
                )
                result_row_id = None
                if record.result_id:
                    result_row = (
                        (
                            await session.execute(
                                select(QualityResultRow).where(
                                    QualityResultRow.quality_run_id == uuid.UUID(record.run_id),
                                    QualityResultRow.result_id == record.result_id,
                                )
                            )
                        )
                        .scalars()
                        .first()
                    )
                    if result_row is None:
                        raise QualityError(
                            "EVIDENCE_RESULT_NOT_FOUND",
                            "the evidence result does not belong to the quality run",
                        )
                    result_row_id = result_row.id
                session.add(
                    QualityEvidenceRow(
                        id=uuid.UUID(stored_contract.evidenceId),
                        created_at=stored_contract.createdAt,
                        quality_run_id=uuid.UUID(record.run_id),
                        quality_result_id=result_row_id,
                        artifact_id=artifact.id,
                        evidence_id=stored_contract.evidenceId,
                        kind=stored_contract.kind,
                        digest=stored_contract.digest,
                        size_bytes=stored_contract.sizeBytes,
                        media_type=stored_contract.mediaType,
                        producer=stored_contract.producer,
                        source_digests=list(stored_contract.sourceDigests),
                        retention_class=stored_contract.retentionClass,
                        storage_allowed=stored_contract.storageAllowed,
                        rag_allowed=stored_contract.ragAllowed,
                        training_allowed=stored_contract.trainingAllowed,
                        distillation_allowed=stored_contract.distillationAllowed,
                    )
                )
        except IntegrityError:
            existing = await self.by_digest(record.run_id, contract.digest)
            if existing is None or not self._same_metadata(existing, record):
                raise QualityError(
                    "EVIDENCE_METADATA_CONFLICT", "evidence persistence rejected conflicting data"
                ) from None
            return existing
        return stored_record

    @staticmethod
    def _same_metadata(left: EvidenceRecord, right: EvidenceRecord) -> bool:
        return (
            left.run_id == right.run_id
            and left.result_id == right.result_id
            and left.bucket == right.bucket
            and left.key == right.key
            and left.contract.kind == right.contract.kind
            and left.contract.digest == right.contract.digest
            and left.contract.sizeBytes == right.contract.sizeBytes
            and left.contract.mediaType == right.contract.mediaType
            and left.contract.producer == right.contract.producer
            and left.contract.sourceDigests == right.contract.sourceDigests
            and left.contract.retentionClass == right.contract.retentionClass
            and left.contract.storageAllowed == right.contract.storageAllowed
            and left.contract.ragAllowed == right.contract.ragAllowed
            and left.contract.trainingAllowed == right.contract.trainingAllowed
            and left.contract.distillationAllowed == right.contract.distillationAllowed
        )
