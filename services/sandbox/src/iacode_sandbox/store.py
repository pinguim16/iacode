"""Where the sandbox keeps what it must not forget: its sessions and its executions.

The service's memory is never the source of truth. A session is a row here and a container on the
engine, and after a restart the service rebuilds its view from both (`service.reconcile`). An
execution is written once, when it ends, to ``tool_calls`` — keyed by the tool request it
answers, so a retried activity finds the recorded outcome instead of running the tool again.

:class:`SandboxStore` is the port. :class:`SqlSandboxStore` is the implementation the service runs
with, over the shared schema in ``packages/persistence``. :class:`MemorySandboxStore` is the
implementation the service's own suite runs with, where there is no database; it enforces the same
rules — one active session per run, one execution per request — so a test that passes against it is
testing the service, not a store that forgives what the real one refuses.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from typing import Any, Protocol

from iacode_contracts.sandbox import SANDBOX_ACTIVE_SESSION_STATES

__all__ = [
    "ExecutionRecord",
    "MemorySandboxStore",
    "SandboxStore",
    "SessionRecord",
    "SqlSandboxStore",
    "StoreConflictError",
]


class StoreConflictError(RuntimeError):
    """A write the store's own rules refuse, such as a second active session for one run."""


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    run_id: str
    state: str
    policy: str
    image: str
    image_fingerprint: str
    container_name: str
    network_profile: str
    workspace_source: dict[str, Any]
    resource_limits: dict[str, Any]
    expires_at: datetime
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    failure_reason: str | None = None
    active_tool_request_id: str | None = None
    created_at: datetime | None = None

    @property
    def active(self) -> bool:
        return self.state in SANDBOX_ACTIVE_SESSION_STATES


@dataclass(frozen=True)
class ExecutionRecord:
    tool_request_id: str
    agent_run_id: str
    session_id: str | None
    tool: str
    status: str
    exit_code: int | None
    duration_ms: int
    timed_out: bool
    truncated: bool
    error_code: str | None
    summary: str
    artifact_ids: tuple[str, ...] = ()
    result: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None


class SandboxStore(Protocol):
    async def active_session_for_run(self, run_id: str) -> SessionRecord | None: ...
    async def session(self, session_id: str) -> SessionRecord | None: ...
    async def sessions(self, *, active_only: bool = False) -> list[SessionRecord]: ...
    async def create_session(self, record: SessionRecord) -> SessionRecord: ...
    async def update_session(self, session_id: str, **fields: Any) -> SessionRecord: ...
    async def execution(self, tool_request_id: str) -> ExecutionRecord | None: ...
    async def record_execution(self, record: ExecutionRecord) -> ExecutionRecord: ...
    async def record_artifact(self, *, run_id: str, kind: str, bucket: str, key: str,
                              content_type: str, size_bytes: int, sha256: str) -> str: ...


def _now() -> datetime:
    return datetime.now(UTC)


class MemorySandboxStore:
    """The store the service's suite runs with. Same rules as the database, no database."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}
        self._executions: dict[str, ExecutionRecord] = {}
        self.artifacts: list[dict[str, Any]] = []

    async def active_session_for_run(self, run_id: str) -> SessionRecord | None:
        return next((item for item in self._sessions.values()
                     if item.run_id == run_id and item.active), None)

    async def session(self, session_id: str) -> SessionRecord | None:
        return self._sessions.get(session_id)

    async def sessions(self, *, active_only: bool = False) -> list[SessionRecord]:
        return [item for item in self._sessions.values() if item.active or not active_only]

    async def create_session(self, record: SessionRecord) -> SessionRecord:
        if record.active and await self.active_session_for_run(record.run_id):
            raise StoreConflictError(f"run {record.run_id} already has an active sandbox session")
        stored = replace(record, created_at=record.created_at or _now())
        self._sessions[record.session_id] = stored
        return stored

    async def update_session(self, session_id: str, **fields: Any) -> SessionRecord:
        stored = replace(self._sessions[session_id], **fields)
        self._sessions[session_id] = stored
        return stored

    async def execution(self, tool_request_id: str) -> ExecutionRecord | None:
        return self._executions.get(tool_request_id)

    async def record_execution(self, record: ExecutionRecord) -> ExecutionRecord:
        if record.tool_request_id in self._executions:
            return self._executions[record.tool_request_id]
        stored = replace(record, created_at=_now())
        self._executions[record.tool_request_id] = stored
        return stored

    async def record_artifact(self, *, run_id: str, kind: str, bucket: str, key: str,
                              content_type: str, size_bytes: int, sha256: str) -> str:
        identifier = str(uuid.uuid4())
        self.artifacts.append({"id": identifier, "runId": run_id, "kind": kind, "bucket": bucket,
                               "key": key, "contentType": content_type, "sizeBytes": size_bytes,
                               "sha256": sha256})
        return identifier


class SqlSandboxStore:
    """The store over the shared schema. The rules live in the database's own constraints."""

    def __init__(self, session_factory: Any) -> None:
        self.session_factory = session_factory

    @staticmethod
    def _record(row: Any) -> SessionRecord:
        return SessionRecord(
            session_id=str(row.id), run_id=str(row.task_run_id), state=row.state,
            policy=row.policy, image=row.image, image_fingerprint=row.image_fingerprint,
            container_name=row.container_name, network_profile=row.network_profile,
            workspace_source=dict(row.workspace_source or {}),
            resource_limits=dict(row.resource_limits or {}), expires_at=row.expires_at,
            started_at=row.started_at, stopped_at=row.stopped_at,
            failure_reason=row.failure_reason,
            active_tool_request_id=(str(row.active_tool_request_id)
                                    if row.active_tool_request_id else None),
            created_at=row.created_at)

    async def active_session_for_run(self, run_id: str) -> SessionRecord | None:
        from iacode_persistence.models import SandboxSession
        from sqlalchemy import select

        async with self.session_factory() as session:
            row = (await session.execute(
                select(SandboxSession).where(
                    SandboxSession.task_run_id == uuid.UUID(run_id),
                    SandboxSession.state.in_(SANDBOX_ACTIVE_SESSION_STATES)))).scalars().first()
        return self._record(row) if row else None

    async def session(self, session_id: str) -> SessionRecord | None:
        from iacode_persistence.models import SandboxSession

        async with self.session_factory() as session:
            row = await session.get(SandboxSession, uuid.UUID(session_id))
        return self._record(row) if row else None

    async def sessions(self, *, active_only: bool = False) -> list[SessionRecord]:
        from iacode_persistence.models import SandboxSession
        from sqlalchemy import select

        statement = select(SandboxSession).order_by(SandboxSession.created_at)
        if active_only:
            statement = statement.where(SandboxSession.state.in_(SANDBOX_ACTIVE_SESSION_STATES))
        async with self.session_factory() as session:
            rows = (await session.execute(statement)).scalars().all()
        return [self._record(row) for row in rows]

    async def create_session(self, record: SessionRecord) -> SessionRecord:
        from iacode_persistence.models import SandboxSession
        from sqlalchemy.exc import IntegrityError

        row = SandboxSession(
            id=uuid.UUID(record.session_id), task_run_id=uuid.UUID(record.run_id),
            state=record.state, policy=record.policy, image=record.image,
            image_fingerprint=record.image_fingerprint, container_name=record.container_name,
            network_profile=record.network_profile, workspace_source=record.workspace_source,
            resource_limits=record.resource_limits, expires_at=record.expires_at)
        try:
            async with self.session_factory() as session, session.begin():
                session.add(row)
        except IntegrityError as error:
            raise StoreConflictError(f"the sandbox session for run {record.run_id} could not be "
                                     f"created: {error.orig}") from None
        return await self.session(record.session_id)  # type: ignore[return-value]

    async def update_session(self, session_id: str, **fields: Any) -> SessionRecord:
        from iacode_persistence.models import SandboxSession

        async with self.session_factory() as session, session.begin():
            row = await session.get(SandboxSession, uuid.UUID(session_id), with_for_update=True)
            for key, value in fields.items():
                if key == "active_tool_request_id":
                    value = uuid.UUID(value) if value else None
                setattr(row, key, value)
            row.version = (row.version or 1) + 1
        return await self.session(session_id)  # type: ignore[return-value]

    async def execution(self, tool_request_id: str) -> ExecutionRecord | None:
        from iacode_persistence.models import ToolCall
        from sqlalchemy import select

        async with self.session_factory() as session:
            row = (await session.execute(select(ToolCall).where(
                ToolCall.tool_request_id == uuid.UUID(tool_request_id)))).scalars().first()
        if row is None:
            return None
        return ExecutionRecord(
            tool_request_id=tool_request_id, agent_run_id=str(row.agent_run_id),
            session_id=str(row.sandbox_session_id) if row.sandbox_session_id else None,
            tool=row.tool_name, status=row.status, exit_code=row.exit_code,
            duration_ms=int(row.latency_ms or 0), timed_out=row.timed_out,
            truncated=row.truncated, error_code=row.error_code, summary=row.summary or "",
            artifact_ids=tuple(row.artifact_ids or ()), created_at=row.created_at)

    async def record_execution(self, record: ExecutionRecord) -> ExecutionRecord:
        from iacode_persistence.models import ToolCall
        from sqlalchemy.exc import IntegrityError

        row = ToolCall(
            agent_run_id=uuid.UUID(record.agent_run_id), tool_name=record.tool,
            succeeded=record.status == "SUCCEEDED", latency_ms=record.duration_ms,
            error_code=record.error_code, tool_request_id=uuid.UUID(record.tool_request_id),
            sandbox_session_id=uuid.UUID(record.session_id) if record.session_id else None,
            status=record.status, exit_code=record.exit_code, timed_out=record.timed_out,
            truncated=record.truncated, summary=record.summary[:240],
            artifact_ids=list(record.artifact_ids))
        try:
            async with self.session_factory() as session, session.begin():
                session.add(row)
        except IntegrityError:
            # The same request recorded twice: the first record is the record.
            existing = await self.execution(record.tool_request_id)
            if existing is None:
                raise
            return existing
        return await self.execution(record.tool_request_id)  # type: ignore[return-value]

    async def record_artifact(self, *, run_id: str, kind: str, bucket: str, key: str,
                              content_type: str, size_bytes: int, sha256: str) -> str:
        from iacode_persistence.models import Artifact

        row = Artifact(task_run_id=uuid.UUID(run_id), kind=kind, storage_bucket=bucket,
                       storage_key=key, content_type=content_type, size_bytes=size_bytes,
                       checksum_sha256=sha256)
        async with self.session_factory() as session, session.begin():
            session.add(row)
            await session.flush()
            identifier = str(row.id)
        return identifier
