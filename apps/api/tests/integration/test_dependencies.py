"""Integration with the real services, not with imitations of them.

`docs/DEVELOPMENT-CONTRACT.md` forbids proving an integration with a mock when the real service
exists in the test stack. Every test here therefore talks to the PostgreSQL, Redis, MinIO and
Temporal containers the Compose file starts, and each one is skipped with a reason rather than
passing quietly when the stack is absent.

They run inside the API image on the Compose network, so the addresses come from the container's
own environment — the same values the running API uses.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from iacode_api.cache import client as cache_client
from iacode_api.db import engine as db_engine
from iacode_api.db.models import Project, Task
from iacode_api.storage import client as storage_client
from iacode_api.workflows.client import TemporalGateway
from sqlalchemy import select, text

from tests.conftest import stack_is_configured, stack_settings

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not stack_is_configured(),
                       reason="the Foundation stack is not configured for this process"),
]


async def test_database_round_trip() -> None:
    """Write through the ORM, read it back, and clean up. Proves the schema is really there."""
    settings = stack_settings()
    engine = db_engine.create_engine(settings)
    factory = db_engine.create_session_factory(engine)
    slug = f"integration-{uuid.uuid4().hex[:12]}"
    try:
        async with db_engine.session_scope(factory) as session:
            project = Project(slug=slug, name="Integration project")
            session.add(project)
            await session.flush()
            session.add(Task(project_id=project.id, title="Integration task"))

        async with db_engine.session_scope(factory) as session:
            stored = (await session.execute(
                select(Project).where(Project.slug == slug))).scalar_one()
            assert stored.name == "Integration project"
            # Defaults the database applies, not values Python set.
            assert stored.version == 1
            assert stored.metadata_ == {}
            assert stored.created_at is not None
            tasks = (await session.execute(
                select(Task).where(Task.project_id == stored.id))).scalars().all()
            assert [task.status for task in tasks] == ["PENDING"]

        async with db_engine.session_scope(factory) as session:
            stored = (await session.execute(
                select(Project).where(Project.slug == slug))).scalar_one()
            await session.delete(stored)
    finally:
        await engine.dispose()


async def test_identifiers_are_time_ordered_in_the_database() -> None:
    """UUIDv7 keys must sort by creation time, which is the reason the strategy was chosen."""
    settings = stack_settings()
    engine = db_engine.create_engine(settings)
    factory = db_engine.create_session_factory(engine)
    prefix = f"ordering-{uuid.uuid4().hex[:8]}"
    try:
        async with db_engine.session_scope(factory) as session:
            for index in range(5):
                session.add(Project(slug=f"{prefix}-{index}", name=f"Ordering {index}"))

        async with db_engine.session_scope(factory) as session:
            rows = (await session.execute(
                select(Project.slug).where(Project.slug.like(f"{prefix}-%")).order_by(Project.id)
            )).scalars().all()
            assert rows == [f"{prefix}-{index}" for index in range(5)]

        async with db_engine.session_scope(factory) as session:
            for slug in rows:
                stored = (await session.execute(
                    select(Project).where(Project.slug == slug))).scalar_one()
                await session.delete(stored)
    finally:
        await engine.dispose()


async def test_the_schema_matches_the_declared_model() -> None:
    """Every declared table exists. A migration that ran but created nothing would pass a ping."""
    settings = stack_settings()
    engine = db_engine.create_engine(settings)
    try:
        async with engine.connect() as connection:
            rows = await connection.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            present = {row[0] for row in rows}
    finally:
        await engine.dispose()

    expected = {
        "projects", "repositories", "tasks", "task_runs", "agents", "agent_runs",
        "providers", "models", "model_calls", "tool_calls", "artifacts", "experiences",
    }
    assert expected <= present, f"missing tables: {sorted(expected - present)}"
    assert "alembic_version" in present


async def test_pgvector_extension_is_available() -> None:
    """Prepared for Gate 7 and verified now, so the preparation is a fact rather than a plan."""
    settings = stack_settings()
    engine = db_engine.create_engine(settings)
    try:
        async with engine.connect() as connection:
            row = (await connection.execute(
                text("SELECT extversion FROM pg_extension WHERE extname = 'vector'"))).first()
    finally:
        await engine.dispose()

    assert row is not None, "the vector extension was not created by the migration"


async def test_a_failed_statement_does_not_poison_the_pooled_connection() -> None:
    """Without the rollback in ``session_scope`` the *next* request fails, not this one."""
    settings = stack_settings()
    engine = db_engine.create_engine(settings)
    factory = db_engine.create_session_factory(engine)
    try:
        with pytest.raises(Exception):  # noqa: B017 - any driver error proves the point
            async with db_engine.session_scope(factory) as session:
                await session.execute(text("SELECT * FROM a_table_that_does_not_exist"))

        async with db_engine.session_scope(factory) as session:
            assert (await session.execute(text("SELECT 1"))).scalar_one() == 1
    finally:
        await engine.dispose()


async def test_redis_round_trip() -> None:
    settings = stack_settings()
    client = cache_client.create_client(settings)
    key = f"iacode:integration:{uuid.uuid4().hex}"
    try:
        await cache_client.ping(client)
        await client.set(key, "stored", ex=60)
        assert await client.get(key) == "stored"
        assert await client.delete(key) == 1
        assert await client.get(key) is None
    finally:
        await cache_client.close(client)


async def test_object_storage_round_trip() -> None:
    settings = stack_settings()
    client = storage_client.create_client(settings)
    bucket = settings.minio_bucket
    key = f"integration/{uuid.uuid4().hex}.txt"
    payload = b"iacode foundation object"

    await storage_client.ping(client, bucket)
    await storage_client.put_object(client, bucket, key, payload, "text/plain")
    assert await storage_client.get_object(client, bucket, key) == payload
    await storage_client.remove_object(client, bucket, key)

    from minio.error import S3Error

    with pytest.raises(S3Error):
        await storage_client.get_object(client, bucket, key)


async def test_bucket_bootstrap_is_idempotent() -> None:
    """The stack's bootstrap already ran, so a second call must create nothing and not fail."""
    settings = stack_settings()
    client = storage_client.create_client(settings)

    created = await storage_client.ensure_bucket(client, settings.minio_bucket)

    assert created is False


async def test_temporal_connectivity() -> None:
    settings = stack_settings()
    gateway = TemporalGateway(settings)
    try:
        await gateway.ping()
    finally:
        await gateway.close()


async def test_readiness_is_ready_against_the_running_stack(live_client: TestClient) -> None:
    """The positive path of the readiness contract, executed against the real dependencies."""
    response = live_client.get("/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "READY"
    assert {item["name"] for item in body["dependencies"]} == {
        "postgres", "redis", "minio", "temporal"}
    assert all(item["status"] == "UP" for item in body["dependencies"])
    assert all(item["latencyMs"] is not None for item in body["dependencies"])
