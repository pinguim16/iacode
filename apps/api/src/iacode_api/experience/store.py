"""Atomic SQL facts, uniqueness-backed replay and bounded finite retention."""

from __future__ import annotations

import uuid
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any

from iacode_common.identifiers import uuid7
from iacode_contracts.experience import CaptureExperience, ExperienceDocument
from iacode_experience.domain import ExperienceError, ExperiencePolicy, StoredExperience, digest
from iacode_persistence.models import Experience, ExperienceEvent
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


def stored(row: Experience, *, replay: bool = False) -> StoredExperience:
    return StoredExperience(
        experience_id=str(row.id),
        project_id=str(row.project_id),
        source_run_id=str(row.source_run_id),
        request_digest=row.request_digest or "",
        content_digest=row.content_digest or "",
        body=row.body,
        state=row.state,
        created_at=row.created_at,
        expires_at=row.expires_at or row.created_at,
        storage_allowed=row.storage_allowed,
        reuse_allowed=(row.rag_allowed, row.training_allowed, row.distillation_allowed),
        schema_version=row.schema_version,
        replay=replay,
        envelope_valid=(
            row.schema_version == 1
            and row.kind == "observable-engineering"
            and row.source_type == "task-run"
            and row.ownership == "UNVERIFIED"
            and row.license == "UNKNOWN"
            and row.metadata_ == {}
            and row.source_finished_at is not None
            and row.expires_at is not None
            and row.request_key is not None
            and row.request_digest is not None
            and (row.state != "ACTIVE" or row.summary == row.body.get("trajectorySummary"))
        ),
    )


class SqlExperienceStore:
    def __init__(self, session_factory: Any, policy: ExperiencePolicy) -> None:
        self.sessions = session_factory
        self.policy = policy

    async def by_request(self, project_id: str, request_id: str) -> StoredExperience | None:
        async with self.sessions() as session:
            row = await session.scalar(
                select(Experience).where(
                    Experience.project_id == uuid.UUID(project_id),
                    Experience.request_key == uuid.UUID(request_id),
                )
            )
            return stored(row, replay=True) if row else None

    async def get(self, project_id: str, experience_id: str) -> StoredExperience:
        async with self.sessions() as session:
            row = await session.scalar(
                select(Experience).where(
                    Experience.project_id == uuid.UUID(project_id),
                    Experience.id == uuid.UUID(experience_id),
                )
            )
            if row is None:
                raise ExperienceError("EXPERIENCE_NOT_FOUND")
            return stored(row)

    async def capture(
        self,
        project_id: str,
        request: CaptureExperience,
        document: ExperienceDocument,
        now: datetime,
        expires_at: datetime,
    ) -> StoredExperience:
        body = document.model_dump(mode="json")
        request_hash = digest(request.model_dump(mode="json"))
        row = Experience(
            id=uuid7(),
            created_at=now,
            updated_at=now,
            project_id=uuid.UUID(project_id),
            source_run_id=uuid.UUID(request.taskRunId),
            task_run_id=uuid.UUID(request.taskRunId),
            schema_version=1,
            state="ACTIVE",
            request_key=uuid.UUID(request.idempotencyKey),
            request_digest=request_hash,
            content_digest=digest(body),
            body=body,
            kind="observable-engineering",
            summary=document.trajectorySummary,
            source_type="task-run",
            ownership="UNVERIFIED",
            license="UNKNOWN",
            storage_allowed=True,
            rag_allowed=False,
            training_allowed=False,
            distillation_allowed=False,
            expires_at=expires_at,
            source_finished_at=document.task.finishedAt,
            metadata_={},
        )
        try:
            async with self.sessions() as session, session.begin():
                session.add(row)
                await session.flush()  # parent first: no relationship flush ordering assumption
                session.add(ExperienceEvent(experience_id=row.id, kind="CAPTURED", created_at=now))
                await session.flush()
                result = stored(row)
            return result
        except IntegrityError as error:
            if getattr(error.orig, "sqlstate", None) != "23505":
                raise ExperienceError("EXPERIENCE_DEPENDENCY_UNAVAILABLE") from error
            existing = await self.by_request(project_id, request.idempotencyKey)
            if existing is not None and existing.request_digest == request_hash:
                return replace(existing, replay=True)
            raise ExperienceError("REQUEST_CONFLICT" if existing else "SOURCE_CONFLICT") from error
        except SQLAlchemyError as error:
            raise ExperienceError("EXPERIENCE_DEPENDENCY_UNAVAILABLE") from error

    async def page(
        self, project_id: str, after: str | None, limit: int, now: datetime
    ) -> list[StoredExperience]:
        if not 1 <= limit <= self.policy.maxPageSize:
            raise ExperienceError("PAGE_LIMIT_INVALID")
        query = (
            select(Experience)
            .where(
                Experience.project_id == uuid.UUID(project_id),
                Experience.schema_version == 1,
                Experience.state == "ACTIVE",
                Experience.storage_allowed.is_(True),
                Experience.expires_at > now,
            )
            .order_by(Experience.id)
            .limit(limit)
        )
        if after is not None:
            query = query.where(Experience.id > uuid.UUID(after))
        async with self.sessions() as session:
            return [stored(row) for row in (await session.scalars(query)).all()]

    @staticmethod
    def _purge(session: Any, row: Experience, state: str, now: datetime) -> None:
        row.state = state
        row.body = {}
        row.summary = ""
        row.storage_allowed = False
        row.rag_allowed = row.training_allowed = row.distillation_allowed = False
        row.purged_at = now
        row.version += 1
        session.add(ExperienceEvent(experience_id=row.id, kind=state, created_at=now))

    async def withdraw(
        self, project_id: str, experience_id: str, now: datetime | None = None
    ) -> StoredExperience:
        now = now or datetime.now(UTC)
        async with self.sessions() as session, session.begin():
            row = await session.scalar(
                select(Experience)
                .where(
                    Experience.project_id == uuid.UUID(project_id),
                    Experience.id == uuid.UUID(experience_id),
                )
                .with_for_update()
            )
            if row is None:
                raise ExperienceError("EXPERIENCE_NOT_FOUND")
            if row.schema_version != 1:
                raise ExperienceError("LEGACY_QUARANTINED")
            if row.state == "ACTIVE":
                self._purge(session, row, "EXPIRED" if now >= row.expires_at else "DELETED", now)
                await session.flush()
            return stored(row)

    async def sweep(self, now: datetime | None = None) -> dict[str, int]:
        now = now or datetime.now(UTC)
        async with self.sessions() as session, session.begin():
            rows = (
                await session.scalars(
                    select(Experience)
                    .where(
                        Experience.schema_version == 1,
                        Experience.state == "ACTIVE",
                        Experience.expires_at <= now,
                    )
                    .order_by(Experience.expires_at, Experience.id)
                    .limit(self.policy.batchSize)
                    .with_for_update(skip_locked=True)
                )
            ).all()
            for row in rows:
                self._purge(session, row, "EXPIRED", now)
            await session.flush()
            obsolete = (
                await session.scalars(
                    select(Experience.id)
                    .where(
                        Experience.schema_version == 1,
                        Experience.state.in_(("DELETED", "EXPIRED")),
                        Experience.purged_at
                        <= now - timedelta(seconds=self.policy.tombstoneRetentionSeconds),
                        Experience.source_finished_at
                        <= now - timedelta(seconds=self.policy.captureMaxAgeSeconds),
                    )
                    .order_by(Experience.id)
                    .limit(self.policy.batchSize)
                    .with_for_update(skip_locked=True)
                )
            ).all()
            if obsolete:
                await session.execute(delete(Experience).where(Experience.id.in_(obsolete)))
            return {"purged": len(rows), "tombstonesCollected": len(obsolete)}
