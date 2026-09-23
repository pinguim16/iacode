"""The sandbox's store and artifact sink against the stack's own PostgreSQL and MinIO.

The service's suite runs with an in-memory store and sink, because its subject is the container
engine. What it runs with in the stack is :class:`~iacode_sandbox.store.SqlSandboxStore` and
:class:`~iacode_sandbox.artifacts.MinioArtifactSink`, and the rules they rely on live in the
database's own constraints — one active session per run, one execution per tool request, a closed
state vocabulary — which only the real database can show.

Every row and object a case writes is removed again, whatever the case does (`LSN-0039`), and the
last case asserts that nothing this suite writes is left behind.

These cases run in the verification's ``sandbox-integration`` stage, against the running stack. The
mandatory gate runs the service's suite without the stack and deselects them by their marker.
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import os
import tempfile
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from iacode_contracts.sandbox import WORKSPACE_SNAPSHOT_ARTIFACT_KIND
from iacode_persistence.engine import create_session_factory
from iacode_persistence.models import (
    Agent,
    AgentRun,
    Artifact,
    Project,
    SandboxSession,
    Task,
    TaskRun,
    ToolCall,
    ToolRequest,
)
from iacode_sandbox.artifacts import MinioArtifactSink
from iacode_sandbox.config import get_sandbox_settings, minio_client
from iacode_sandbox.snapshots import SnapshotError, SnapshotReader, _create
from iacode_sandbox.store import ExecutionRecord, SessionRecord, SqlSandboxStore, StoreConflictError
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.environ.get("IACODE_DATABASE_URL"),
                       reason="the stack is not configured for this process"),
]

#: Everything this suite writes carries this prefix, so the residue check can find it.
PREFIX = "iacode-sandbox-itest"


def run(coroutine):
    return asyncio.run(coroutine)


class Fixture:
    """A project, a task, a run, an agent run and a tool request of its own, and their removal."""

    def __init__(self) -> None:
        settings = get_sandbox_settings()
        self.settings = settings
        # Every case drives the store through its own event loop, so no connection may outlive
        # the loop that opened it: no pool.
        self.engine = create_async_engine(settings.database_url, poolclass=NullPool)
        self.factory = create_session_factory(self.engine)
        self.store = SqlSandboxStore(self.factory)
        self.client = minio_client(settings)
        self.objects: list[str] = []
        self.artifacts: list[uuid.UUID] = []
        self.slug = f"{PREFIX}-{uuid.uuid4().hex[:10]}"

    async def build(self) -> None:
        async with self.factory() as session, session.begin():
            project = Project(slug=self.slug, name="Sandbox integration")
            agent = Agent(slug=self.slug, name="Sandbox integration agent",
                          role_contract="services/sandbox/tests/integration", enabled=False,
                          role="integration", allowed_actions=[])
            session.add_all([project, agent])
            await session.flush()
            task = Task(project_id=project.id, title=self.slug, description="integration")
            session.add(task)
            await session.flush()
            task_run = TaskRun(task_id=task.id, status="RUNNING", attempt=1)
            session.add(task_run)
            await session.flush()
            agent_run = AgentRun(task_run_id=task_run.id, agent_id=agent.id, status="RUNNING",
                                 stage_index=0, stage_name="develop", agent_slug=self.slug)
            session.add(agent_run)
            await session.flush()
            request = ToolRequest(task_run_id=task_run.id, agent_run_id=agent_run.id,
                                  tool_name="shell.exec", arguments={"command": "true"},
                                  status="PENDING")
            session.add(request)
            await session.flush()
            self.run_id, self.agent_run_id = str(task_run.id), str(agent_run.id)
            self.tool_request_id = str(request.id)

    async def remove(self) -> None:
        for key in self.objects:
            await asyncio.to_thread(self.client.remove_object, self.settings.minio_bucket, key)
        async with self.factory() as session, session.begin():
            if self.artifacts:
                await session.execute(delete(Artifact).where(Artifact.id.in_(self.artifacts)))
            await session.execute(delete(Project).where(Project.slug == self.slug))
            await session.execute(delete(Agent).where(Agent.slug == self.slug))
        await self.engine.dispose()

    def session_record(self, **overrides) -> SessionRecord:
        fields = {
            "session_id": str(uuid.uuid4()), "run_id": self.run_id, "state": "READY",
            "policy": "developer", "image": "iacode/sandbox-iacode-dev:itest",
            "image_fingerprint": "f" * 64, "container_name": f"{PREFIX}-{uuid.uuid4().hex}",
            "network_profile": "none", "workspace_source": {"kind": "empty"},
            "resource_limits": {"memoryMb": 1024},
            "expires_at": datetime.now(UTC) + timedelta(hours=1),
        }
        fields.update(overrides)
        return SessionRecord(**fields)


@pytest.fixture
def stack() -> Iterator[Fixture]:
    fixture = Fixture()
    run(fixture.build())
    try:
        yield fixture
    finally:
        run(fixture.remove())


class SqlSandboxStoreTests:
    def test_a_session_round_trips_through_the_database(self, stack) -> None:
        created = run(stack.store.create_session(stack.session_record()))
        assert run(stack.store.session(created.session_id)) == created
        assert run(stack.store.active_session_for_run(stack.run_id)).session_id == \
            created.session_id

    def test_a_second_active_session_for_one_run_is_refused(self, stack) -> None:
        first = run(stack.store.create_session(stack.session_record()))
        with pytest.raises(StoreConflictError):
            run(stack.store.create_session(stack.session_record()))
        # The null control: once the first is over, the run may have another.
        run(stack.store.update_session(first.session_id, state="STOPPED",
                                       stopped_at=datetime.now(UTC)))
        second = run(stack.store.create_session(stack.session_record()))
        assert run(stack.store.active_session_for_run(stack.run_id)).session_id == \
            second.session_id

    def test_an_undeclared_state_is_refused_by_the_database(self, stack) -> None:
        created = run(stack.store.create_session(stack.session_record()))
        with pytest.raises(IntegrityError):
            run(stack.store.update_session(created.session_id, state="HALF_ALIVE"))
        assert run(stack.store.session(created.session_id)).state == "READY"

    def test_an_execution_is_recorded_once_per_tool_request(self, stack) -> None:
        session = run(stack.store.create_session(stack.session_record()))
        first = ExecutionRecord(
            tool_request_id=stack.tool_request_id, agent_run_id=stack.agent_run_id,
            session_id=session.session_id, tool="shell.exec", status="SUCCEEDED", exit_code=0,
            duration_ms=12, timed_out=False, truncated=False, error_code=None,
            summary="succeeded, exit 0")
        recorded = run(stack.store.record_execution(first))
        retried = run(stack.store.record_execution(ExecutionRecord(
            **{**first.__dict__, "status": "FAILED", "exit_code": 1, "created_at": None})))
        assert retried == recorded
        assert (recorded.status, recorded.exit_code, recorded.session_id) == \
            ("SUCCEEDED", 0, session.session_id)

        async def count() -> int:
            async with stack.factory() as db:
                return (await db.execute(select(func.count()).select_from(ToolCall).where(
                    ToolCall.tool_request_id == uuid.UUID(stack.tool_request_id)))).scalar_one()

        assert run(count()) == 1


class SandboxArtifactStoreTests:
    def test_output_is_stored_in_the_bucket_and_recorded_for_the_run(self, stack) -> None:
        sink = MinioArtifactSink(stack.client, stack.settings.minio_bucket, stack.store)
        content = ("line of output\n" * 4000).encode("utf-8")
        reference = run(sink.put(run_id=stack.run_id, tool_request_id=stack.tool_request_id,
                                 name="stdout.txt", content=content, kind="sandbox.stdout"))
        stack.objects.append(reference.key)
        stack.artifacts.append(uuid.UUID(reference.artifact_id))

        stored = stack.client.get_object(stack.settings.minio_bucket, reference.key)
        try:
            assert stored.read() == content
        finally:
            stored.close()
            stored.release_conn()

        async def row() -> Artifact:
            async with stack.factory() as db:
                return await db.get(Artifact, uuid.UUID(reference.artifact_id))

        recorded = run(row())
        assert str(recorded.task_run_id) == stack.run_id
        assert recorded.checksum_sha256 == hashlib.sha256(content).hexdigest()
        assert recorded.size_bytes == len(content)

    def test_a_snapshot_is_read_back_only_intact_and_only_by_its_digest(self, stack) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "calc.py").write_text("def add(a, b):\n    return a + b\n",
                                            encoding="utf-8")
            stored = run(_create(source, stack.slug))
        stack.objects.append(stored["key"])
        stack.artifacts.append(uuid.UUID(stored["artifactId"]))
        reader = SnapshotReader(stack.factory, stack.client)

        data = run(reader.read(stored["artifactId"], stored["sha256"]))
        assert hashlib.sha256(data).hexdigest() == stored["sha256"]
        with pytest.raises(SnapshotError) as mismatch:
            run(reader.read(stored["artifactId"], "0" * 64))
        assert mismatch.value.code == "SNAPSHOT_CHECKSUM_MISMATCH"

        stack.client.put_object(stack.settings.minio_bucket, stored["key"],
                                io.BytesIO(b"tampered"), len(b"tampered"))
        with pytest.raises(SnapshotError) as corrupt:
            run(reader.read(stored["artifactId"], stored["sha256"]))
        assert corrupt.value.code == "SNAPSHOT_CORRUPT"

    def test_an_artifact_of_another_kind_is_not_a_snapshot(self, stack) -> None:
        sink = MinioArtifactSink(stack.client, stack.settings.minio_bucket, stack.store)
        reference = run(sink.put(run_id=stack.run_id, tool_request_id=stack.tool_request_id,
                                 name="stderr.txt", content=b"x", kind="sandbox.stderr"))
        stack.objects.append(reference.key)
        stack.artifacts.append(uuid.UUID(reference.artifact_id))
        assert reference.kind != WORKSPACE_SNAPSHOT_ARTIFACT_KIND
        with pytest.raises(SnapshotError) as refused:
            run(SnapshotReader(stack.factory, stack.client).read(reference.artifact_id))
        assert refused.value.code == "SNAPSHOT_NOT_AUTHORISED"


class IntegrationResidueTests:
    def test_nothing_this_suite_writes_is_left_behind(self) -> None:
        """Runs last in its module: the rows the cases above created are gone."""
        fixture = Fixture()

        async def residue() -> tuple[int, int]:
            async with fixture.factory() as db:
                projects = (await db.execute(select(func.count()).select_from(Project).where(
                    Project.slug.like(f"{PREFIX}-%")))).scalar_one()
                sessions = (await db.execute(select(func.count()).select_from(SandboxSession)
                                             .where(SandboxSession.container_name.like(
                                                 f"{PREFIX}-%")))).scalar_one()
            await fixture.engine.dispose()
            return projects, sessions

        assert run(residue()) == (0, 0)
