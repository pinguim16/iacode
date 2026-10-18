"""Actual atomic PostgreSQL projection/index persistence with project-bound bounded reads."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any

from iacode_common.identifiers import uuid7
from iacode_contracts.knowledge import IngestKnowledge, KnowledgeDocument, KnowledgePolicy
from iacode_knowledge.domain import (
    INVALID_SOURCE_CODES,
    KnowledgeError,
    StoredKnowledge,
    canonical,
    decode,
    digest,
    index_fingerprint,
)
from iacode_persistence.models import KnowledgeDocument as Document
from iacode_persistence.models import KnowledgeEvent as Event
from iacode_persistence.models import KnowledgeIndexEntry as IndexEntry
from iacode_persistence.models import Project
from sqlalchemy import Text, case, cast, delete, func, literal, select
from sqlalchemy.dialects.postgresql import JSONB, array
from sqlalchemy.orm import load_only


class SqlKnowledgeStore:
    def __init__(
        self, sessions: Any, policy: KnowledgePolicy, known_credentials: tuple[str, ...]
    ) -> None:
        self.sessions = sessions
        self.policy = policy
        self.known_credentials = known_credentials

    @staticmethod
    def _source_condition(project: str, source: str) -> tuple:
        return Document.project_id == uuid.UUID(project), Document.source_id == uuid.UUID(source)

    async def _project(self, session: Any, project: str) -> None:
        if await session.scalar(select(Project.id).where(Project.id == uuid.UUID(project))) is None:
            raise KnowledgeError("PROJECT_NOT_FOUND")

    @staticmethod
    async def _lock(session: Any, project: str) -> None:
        # Project serialization also enforces the active-source capacity under concurrent inserts.
        key = int.from_bytes(
            hashlib.sha256(project.encode("ascii")).digest()[:8], "big", signed=True
        )
        await session.execute(select(func.pg_advisory_xact_lock(key)))

    def _selection(self) -> Any:
        # JSONB's text rendering adds structural spaces. The SQL receiver admits the bounded
        # worst-case expansion; canonical validation below still enforces the original byte bound.
        within = func.octet_length(cast(Document.body, Text)) <= self.policy.maxBodyBytes * 2
        return select(
            Document.id,
            Document.project_id,
            Document.source_kind,
            Document.source_id,
            Document.revision,
            Document.source_digest,
            Document.grant_digest,
            Document.policy_digest,
            Document.request_digest,
            Document.content_digest,
            Document.state,
            Document.created_at,
            Document.expires_at,
            Document.retention_ceiling,
            Document.purged_at,
            Document.source_created_at,
            case((within, Document.body), else_=literal({}, type_=JSONB)).label("body"),
            within.label("within_limit"),
        )

    @staticmethod
    def _stored(row: Any) -> StoredKnowledge:
        if row is None:
            raise KnowledgeError("KNOWLEDGE_NOT_FOUND")
        if not row.within_limit:
            raise KnowledgeError("STORED_LIMIT_EXCEEDED")
        return StoredKnowledge(
            document_id=str(row.id),
            project_id=str(row.project_id),
            source_kind=row.source_kind,
            source_id=str(row.source_id),
            revision=row.revision,
            source_digest=row.source_digest,
            grant_digest=row.grant_digest,
            policy_digest=row.policy_digest,
            request_digest=row.request_digest,
            content_digest=row.content_digest,
            state=row.state,
            created_at=row.created_at,
            expires_at=row.expires_at,
            retention_ceiling=row.retention_ceiling,
            purged_at=row.purged_at,
            source_created_at=row.source_created_at,
            body=row.body,
        )

    async def get(self, project: str, document: str) -> StoredKnowledge:
        async with self.sessions() as session:
            row = (
                await session.execute(
                    self._selection().where(
                        Document.project_id == uuid.UUID(project),
                        Document.id == uuid.UUID(document),
                    )
                )
            ).one_or_none()
            return self._stored(row)

    async def inventory(self, project: str, now: datetime) -> list[StoredKnowledge]:
        async with self.sessions() as session:
            await self._project(session, project)
            rows = (
                await session.execute(
                    self._selection()
                    .where(
                        Document.project_id == uuid.UUID(project),
                        Document.state == "ACTIVE",
                        Document.expires_at > now,
                    )
                    .order_by(Document.id)
                    .limit(self.policy.maxSources + 1)
                )
            ).all()
            if len(rows) > self.policy.maxSources:
                raise KnowledgeError("INDEX_CAPACITY_EXCEEDED")
            return [self._stored(row) for row in rows]

    async def index_rows(
        self, project: str, document: str
    ) -> tuple[tuple[int, str, tuple[str, ...]], ...]:
        async with self.sessions() as session:
            allowed = select(Document.id).where(
                Document.id == uuid.UUID(document), Document.project_id == uuid.UUID(project)
            )
            audit = await session.scalar(
                select(func.count())
                .select_from(Event)
                .where(Event.document_id.in_(allowed), Event.kind == "INDEXED")
            )
            if audit != 1:
                raise KnowledgeError("INDEX_CORRUPT")
            within = func.octet_length(cast(IndexEntry.tokens, Text)) <= 300000
            rows = (
                await session.execute(
                    select(
                        IndexEntry.ordinal,
                        IndexEntry.digest,
                        case((within, IndexEntry.tokens), else_=literal(None, type_=JSONB)).label(
                            "tokens"
                        ),
                    )
                    .where(IndexEntry.document_id.in_(allowed))
                    .order_by(IndexEntry.ordinal)
                    .limit(self.policy.maxChunks + 1)
                )
            ).all()
            if len(rows) > self.policy.maxChunks or any(
                not isinstance(row.tokens, list)
                or len(row.tokens) > self.policy.maxChunkTokens
                or any(
                    not isinstance(value, str) or len(value) > self.policy.maxTokenChars
                    for value in row.tokens
                )
                for row in rows
            ):
                raise KnowledgeError("INDEX_CORRUPT")
            return tuple((row.ordinal, row.digest, tuple(row.tokens)) for row in rows)

    async def publish(
        self, request: IngestKnowledge, document: KnowledgeDocument, now: datetime
    ) -> StoredKnowledge:
        body = canonical(document.model_dump(mode="json"))
        document = decode(body, KnowledgeDocument, self.policy.maxBodyBytes, self.known_credentials)
        source = document.provenance
        project = document.projectId
        if (request.sourceKind, request.sourceId, request.revision) != (
            source.sourceKind,
            source.sourceId,
            source.revision,
        ):
            raise KnowledgeError("SOURCE_SCOPE_MISMATCH")
        request_digest = digest(request.model_dump(mode="json"))
        material = digest(
            {
                "projectId": project,
                "sourceKind": source.sourceKind,
                "sourceId": source.sourceId,
                "revision": source.revision,
                "sourceDigest": source.sourceDigest,
                "grantDigest": source.grantDigest,
                "policyDigest": document.policyDigest,
            }
        )
        identifier = uuid7()
        async with self.sessions() as session, session.begin():
            await self._project(session, project)
            await self._lock(session, project)
            existing = (
                await session.execute(
                    select(
                        Document.id,
                        Document.request_digest,
                        Document.material_digest,
                        Document.state,
                        Document.expires_at,
                    ).where(
                        Document.project_id == uuid.UUID(project),
                        Document.request_key == uuid.UUID(request.idempotencyKey),
                    )
                )
            ).one_or_none()
            if existing is not None:
                if (
                    existing.request_digest != request_digest
                    or existing.material_digest != material
                ):
                    raise KnowledgeError("REQUEST_CONFLICT")
                if existing.state != "ACTIVE" or existing.expires_at <= now:
                    raise KnowledgeError("KNOWLEDGE_UNAVAILABLE")
                row = (
                    await session.execute(self._selection().where(Document.id == existing.id))
                ).one()
                return replace(self._stored(row), replay=True)
            history = (
                await session.execute(
                    select(
                        Document.state,
                        Document.source_digest,
                        Document.expires_at,
                        Document.retention_ceiling,
                        Document.material_digest,
                    )
                    .where(
                        *self._source_condition(project, source.sourceId),
                        Document.revision == source.revision,
                    )
                    .order_by(Document.created_at, Document.id)
                    .limit(self.policy.maxSources + 1)
                )
            ).all()
            if len(history) > self.policy.maxSources:
                raise KnowledgeError("INDEX_CAPACITY_EXCEEDED")
            if any(row.source_digest != source.sourceDigest for row in history):
                raise KnowledgeError("SOURCE_REVISION_CONFLICT")
            if any(row.state in {"DELETED", "EXPIRED"} or row.expires_at <= now for row in history):
                raise KnowledgeError("KNOWLEDGE_UNAVAILABLE")
            if any(row.material_digest == material for row in history):
                raise KnowledgeError("SOURCE_REVISION_CONFLICT")
            active = (
                await session.scalars(
                    select(Document)
                    .where(
                        *self._source_condition(project, source.sourceId),
                        Document.state == "ACTIVE",
                    )
                    .options(
                        load_only(Document.id, Document.state, Document.version, raiseload=True)
                    )
                    .limit(self.policy.maxSources + 1)
                    .with_for_update()
                )
            ).all()
            if len(active) > self.policy.maxSources:
                raise KnowledgeError("INDEX_CAPACITY_EXCEEDED")
            if not active:
                count = await session.scalar(
                    select(func.count())
                    .select_from(Document)
                    .where(Document.project_id == uuid.UUID(project), Document.state == "ACTIVE")
                )
                if count >= self.policy.maxSources:
                    raise KnowledgeError("INDEX_CAPACITY_EXCEEDED")
            expiry = min(
                now + timedelta(seconds=document.retentionSeconds), source.grant.validUntil
            )
            ceiling = min([expiry, *(row.retention_ceiling for row in history)])
            expiry = min(expiry, ceiling)
            if expiry <= now:
                raise KnowledgeError("KNOWLEDGE_UNAVAILABLE")
            for row in active:
                await self._terminate(session, row, "INVALIDATED", now)
            session.add(
                Document(
                    id=identifier,
                    project_id=uuid.UUID(project),
                    source_kind=source.sourceKind,
                    source_id=uuid.UUID(source.sourceId),
                    revision=source.revision,
                    source_digest=source.sourceDigest,
                    grant_digest=source.grantDigest,
                    policy_digest=document.policyDigest,
                    material_digest=material,
                    request_key=uuid.UUID(request.idempotencyKey),
                    request_digest=request_digest,
                    content_digest=hashlib.sha256(body).hexdigest(),
                    state="ACTIVE",
                    body=document.model_dump(mode="json"),
                    source_created_at=source.artifactCreatedAt,
                    created_at=now,
                    updated_at=now,
                    expires_at=expiry,
                    retention_ceiling=ceiling,
                    checked_at=now,
                    metadata_={},
                )
            )
            await session.flush()
            session.add_all(
                [
                    IndexEntry(
                        document_id=identifier,
                        ordinal=chunk.ordinal,
                        digest=chunk.digest,
                        tokens=list(chunk.tokens),
                        created_at=now,
                    )
                    for chunk in document.chunks
                ]
            )
            session.add(Event(document_id=identifier, kind="INDEXED", created_at=now))
            await session.flush()
            stored = self._stored(
                (await session.execute(self._selection().where(Document.id == identifier))).one()
            )
        return stored

    @staticmethod
    async def _terminate(session: Any, row: Document, state: str, now: datetime) -> None:
        if row.state != "ACTIVE":
            return
        session.add(Event(document_id=row.id, kind=state, created_at=now))
        await session.flush()
        row.state = state
        row.body = {}
        row.purged_at = now
        row.checked_at = now
        row.updated_at = now
        row.version += 1
        await session.flush()
        await session.execute(delete(IndexEntry).where(IndexEntry.document_id == row.id))

    async def candidates(
        self, project: str, query: tuple[str, ...], policy_digest: str, now: datetime
    ) -> list[tuple[str, int]]:
        async with self.sessions() as session:
            await self._project(session, project)
            stale = await session.scalar(
                select(Document.id)
                .where(
                    Document.project_id == uuid.UUID(project),
                    Document.state == "ACTIVE",
                    Document.expires_at > now,
                    Document.policy_digest != policy_digest,
                )
                .limit(1)
            )
            if stale is not None:
                raise KnowledgeError("INDEX_STALE")
            rows = (
                await session.execute(
                    select(IndexEntry.document_id, IndexEntry.ordinal)
                    .join(Document, Document.id == IndexEntry.document_id)
                    .where(
                        Document.project_id == uuid.UUID(project),
                        Document.state == "ACTIVE",
                        Document.expires_at > now,
                        IndexEntry.tokens.has_any(array(list(query), type_=Text)),
                    )
                    .order_by(IndexEntry.document_id, IndexEntry.ordinal)
                    .limit(self.policy.maxCandidates + 1)
                )
            ).all()
            if len(rows) > self.policy.maxCandidates:
                raise KnowledgeError("INDEX_CAPACITY_EXCEEDED")
            return [(str(row.document_id), row.ordinal) for row in rows]

    async def page(
        self, project: str, after: str | None, limit: int, now: datetime
    ) -> list[StoredKnowledge]:
        if limit < 1 or limit > self.policy.maxPageSize:
            raise KnowledgeError("PAGE_LIMIT_INVALID")
        async with self.sessions() as session:
            await self._project(session, project)
            statement = self._selection().where(
                Document.project_id == uuid.UUID(project),
                Document.state == "ACTIVE",
                Document.expires_at > now,
            )
            if after is not None:
                statement = statement.where(Document.id > uuid.UUID(after))
            rows = (await session.execute(statement.order_by(Document.id).limit(limit))).all()
            return [self._stored(row) for row in rows]

    async def withdraw(
        self, project: str, document: str, now: datetime | None = None
    ) -> StoredKnowledge:
        now = now or datetime.now(UTC)
        async with self.sessions() as session, session.begin():
            await self._lock(session, project)
            row = await session.scalar(
                select(Document)
                .where(
                    Document.project_id == uuid.UUID(project), Document.id == uuid.UUID(document)
                )
                .options(load_only(Document.id, Document.state, Document.version, raiseload=True))
                .with_for_update()
            )
            if row is None:
                raise KnowledgeError("KNOWLEDGE_NOT_FOUND")
            await self._terminate(session, row, "DELETED", now)
            result = (await session.execute(self._selection().where(Document.id == row.id))).one()
            return self._stored(result)

    async def sweep(self, sources: Any, now: datetime | None = None) -> dict[str, int]:
        now = now or datetime.now(UTC)
        purged = 0
        async with self.sessions() as session, session.begin():
            rows = (
                await session.scalars(
                    select(Document)
                    .where(Document.state == "ACTIVE")
                    .options(
                        load_only(
                            Document.id,
                            Document.state,
                            Document.expires_at,
                            Document.project_id,
                            Document.source_kind,
                            Document.source_id,
                            Document.revision,
                            Document.source_digest,
                            Document.grant_digest,
                            Document.policy_digest,
                            Document.checked_at,
                            Document.version,
                            raiseload=True,
                        )
                    )
                    .order_by(Document.checked_at, Document.id)
                    .limit(self.policy.batchSize)
                    .with_for_update(skip_locked=True)
                )
            ).all()
            for row in rows:
                state = "EXPIRED" if row.expires_at <= now else None
                if state is None:
                    try:
                        source = await sources.load(
                            str(row.project_id),
                            row.source_kind,
                            str(row.source_id),
                            row.revision,
                            now,
                            capture=False,
                        )
                        if (
                            source.entry.sourceDigest,
                            source.entry.grantDigest,
                            index_fingerprint(self.policy),
                        ) != (row.source_digest, row.grant_digest, row.policy_digest):
                            state = "INVALIDATED"
                    except KnowledgeError as error:
                        if error.code not in INVALID_SOURCE_CODES:
                            raise
                        state = "INVALIDATED"
                if state is not None:
                    await self._terminate(session, row, state, now)
                    purged += 1
                else:
                    row.checked_at = now
                    row.updated_at = now
                    row.version += 1
            old = (
                await session.scalars(
                    select(Document.id)
                    .where(
                        Document.state != "ACTIVE",
                        Document.purged_at
                        <= now - timedelta(seconds=self.policy.tombstoneRetentionSeconds),
                        Document.source_created_at
                        < now - timedelta(seconds=self.policy.sourceCaptureMaxAgeSeconds),
                    )
                    .order_by(Document.id)
                    .limit(self.policy.batchSize)
                    .with_for_update(skip_locked=True)
                )
            ).all()
            if old:
                await session.execute(delete(Document).where(Document.id.in_(old)))
        return {"checked": len(rows), "purged": purged, "tombstonesRemoved": len(old)}
