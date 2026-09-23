"""GATE 3 against the real database: a run's workspace source, and what the sandbox executed for it.

A run may start from an authorised workspace snapshot, named by its artifact identifier and never by
a path; anything that is not a snapshot artifact is refused before the run exists. And the run's
detail shows what the sandbox recorded in ``tool_calls`` — the tool, how it ended, where and how
long — and never the output.

Every row a case writes is removed again, whatever the case does (`LSN-0039`).
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.persistence import SqlAgentRunStore
from iacode_agent_runtime.registry import AgentRegistry
from iacode_agent_runtime.service import AgentRuntimeService
from iacode_api.db import engine as db_engine
from iacode_contracts.agent_runtime import CreateAgentRunRequest
from iacode_contracts.sandbox import WORKSPACE_SNAPSHOT_ARTIFACT_KIND
from iacode_persistence.models import (
    Agent,
    AgentRun,
    Artifact,
    SandboxSession,
    Task,
    TaskRun,
    ToolCall,
    ToolRequest,
)
from sqlalchemy import delete, select

from tests.conftest import stack_is_configured, stack_settings

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not stack_is_configured(),
                       reason="the Foundation stack is not configured for this process"),
]

REPOSITORY_ROOT = Path("/app")


@pytest.fixture
async def session_factory() -> AsyncIterator:
    engine = db_engine.create_engine(stack_settings())
    try:
        yield db_engine.create_session_factory(engine)
    finally:
        await engine.dispose()


@pytest.fixture
async def service(session_factory) -> AsyncIterator[AgentRuntimeService]:
    """The real service; every run and artifact it creates is deleted afterwards."""
    created = AgentRuntimeService(session_factory=session_factory,
                                  registry=AgentRegistry(REPOSITORY_ROOT),
                                  store=SqlAgentRunStore(session_factory))
    created.cleanup = {"runs": [], "artifacts": []}  # type: ignore[attr-defined]
    try:
        yield created
    finally:
        async with session_factory() as session, session.begin():
            for run_id in created.cleanup["runs"]:  # type: ignore[attr-defined]
                row = await session.get(TaskRun, uuid.UUID(run_id))
                if row is not None:
                    await session.execute(delete(Task).where(Task.id == row.task_id))
            for artifact_id in created.cleanup["artifacts"]:  # type: ignore[attr-defined]
                await session.execute(delete(Artifact).where(Artifact.id == artifact_id))


async def artifact(session_factory, service, kind: str) -> str:
    async with session_factory() as session, session.begin():
        row = Artifact(kind=kind, storage_bucket="iacode-artifacts",
                       storage_key=f"itest/{uuid.uuid4().hex}.tar.gz",
                       content_type="application/gzip", size_bytes=10,
                       checksum_sha256="a" * 64)
        session.add(row)
        await session.flush()
        identifier = row.id
    service.cleanup["artifacts"].append(identifier)
    return str(identifier)


async def create(service, **fields):
    plan, created = await service.create_run(CreateAgentRunRequest(task="Fix the bug.", **fields))
    service.cleanup["runs"].append(created.runId)
    return plan, created


async def test_a_coding_run_names_an_authorised_snapshot(session_factory, service) -> None:
    snapshot = await artifact(session_factory, service, WORKSPACE_SNAPSHOT_ARTIFACT_KIND)
    plan, created = await create(service, team="coding", workspaceSnapshot=snapshot)

    assert plan.workspace == {"kind": "snapshot", "artifactId": snapshot, "checksum": "a" * 64}
    assert [stage.sandbox_policy for stage in plan.stages] == [None, "developer", "reviewer"]
    async with session_factory() as session:
        row = await session.get(TaskRun, uuid.UUID(created.runId))
    assert row.workspace == plan.workspace


async def test_a_coding_run_without_a_snapshot_gets_an_empty_workspace(session_factory,
                                                                      service) -> None:
    plan, _created = await create(service, team="coding")
    assert plan.workspace == {"kind": "empty"}


async def test_a_run_that_executes_no_tool_has_no_workspace(session_factory, service) -> None:
    plan, _created = await create(service, team="single-agent")
    assert plan.workspace == {}
    assert all(stage.sandbox_policy is None for stage in plan.stages)


async def test_anything_but_a_snapshot_artifact_is_refused(session_factory, service) -> None:
    other = await artifact(session_factory, service, "sandbox.stdout")
    for reference in (other, str(uuid.uuid4()), "not-a-uuid-but-36-characters-long-xx"):
        with pytest.raises(AgentRuntimeError) as refused:
            await create(service, team="coding", workspaceSnapshot=reference)
        assert refused.value.error_type is AgentRuntimeErrorType.INVALID_REQUEST


async def test_a_snapshot_for_a_team_without_tools_is_refused(session_factory, service) -> None:
    snapshot = await artifact(session_factory, service, WORKSPACE_SNAPSHOT_ARTIFACT_KIND)
    with pytest.raises(AgentRuntimeError, match="executes no tool"):
        await create(service, team="single-agent", workspaceSnapshot=snapshot)


async def test_the_detail_shows_what_the_sandbox_executed_and_not_its_output(session_factory,
                                                                              service) -> None:
    _plan, created = await create(service, team="coding")
    run_id = uuid.UUID(created.runId)
    async with session_factory() as session, session.begin():
        agent = (await session.execute(
            select(Agent).where(Agent.slug == "developer"))).scalars().one()
        agent_run = AgentRun(task_run_id=run_id, agent_id=agent.id, status="RUNNING",
                             stage_index=1, stage_name="develop", agent_slug="developer")
        session.add(agent_run)
        await session.flush()
        request = ToolRequest(task_run_id=run_id, agent_run_id=agent_run.id,
                              tool_name="shell.exec", arguments={"command": "SECRET-COMMAND"},
                              status="RESOLVED")
        sandbox = SandboxSession(
            task_run_id=run_id, state="STOPPED", policy="developer", image="i:t",
            image_fingerprint="f" * 64, container_name=f"iacode-sbx-{uuid.uuid4().hex}",
            network_profile="none", expires_at=datetime.now(UTC) + timedelta(hours=1))
        session.add_all([request, sandbox])
        await session.flush()
        session.add(ToolCall(agent_run_id=agent_run.id, tool_name="shell.exec", succeeded=True,
                             latency_ms=412, tool_request_id=request.id,
                             sandbox_session_id=sandbox.id, status="SUCCEEDED", exit_code=0,
                             summary="succeeded, exit 0"))

    detail = await service.detail(created.runId)

    assert len(detail.toolExecutions) == 1
    execution = detail.toolExecutions[0]
    assert (execution.tool, execution.status, execution.exitCode) == ("shell.exec", "SUCCEEDED", 0)
    assert execution.durationMs == 412
    assert execution.sandboxSession == str(sandbox.id).replace("-", "")[:12]
    assert "SECRET-COMMAND" not in execution.model_dump_json()
