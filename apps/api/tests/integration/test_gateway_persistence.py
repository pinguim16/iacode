"""The gateway's persistence, against the real PostgreSQL from the Compose stack.

Two things are proved here that no unit test can prove: that the migration this Gate adds applies to
a database created by the previous Gate, and that the SQLAlchemy stores behave the way the gateway's
ports say they do — atomically, deactivating rather than deleting, and without a column anywhere
that could hold a prompt.
"""

from __future__ import annotations

import subprocess
import sys
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

import pytest
from iacode_api.db import engine as db_engine
from iacode_api.gateway.store import SqlCatalogStore, SqlModelCallStore
from iacode_model_gateway.config import load_provider_configs
from iacode_model_gateway.contracts import (
    Capability,
    CapabilityProvenance,
    CapabilityState,
    Endpoint,
    ModelDescriptor,
    ModelRef,
)
from iacode_model_gateway.ports import ModelCallRecord, ProviderRecord
from iacode_persistence.models import Model, ModelCall, Provider
from sqlalchemy import create_engine, delete, select, text

from tests.conftest import stack_is_configured, stack_settings

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not stack_is_configured(),
                       reason="the Foundation stack is not configured for this process"),
]

APPLICATION_ROOT = Path(__file__).resolve().parents[2]


def _sync_url(async_url: str) -> str:
    return async_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)


def _administrative_url(async_url: str) -> str:
    base, _, _database = _sync_url(async_url).rpartition("/")
    return f"{base}/postgres"


def _alembic(database_url: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    import os

    environment = dict(os.environ)
    environment["IACODE_DATABASE_URL"] = database_url
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=str(APPLICATION_ROOT), env=environment, text=True,
        encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


class _DisposableDatabase:
    """A database created for one test and dropped afterwards, whatever the test does."""

    def __init__(self) -> None:
        settings = stack_settings()
        self.name = f"iacode_gateway_{uuid.uuid4().hex[:12]}"
        self._admin = _administrative_url(settings.database_url)
        base, _, _ = settings.database_url.rpartition("/")
        self.url = f"{base}/{self.name}"

    def __enter__(self) -> _DisposableDatabase:
        engine = create_engine(self._admin, isolation_level="AUTOCOMMIT", future=True)
        with engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{self.name}"'))
        engine.dispose()
        return self

    def __exit__(self, *_exception: object) -> None:
        engine = create_engine(self._admin, isolation_level="AUTOCOMMIT", future=True)
        with engine.connect() as connection:
            connection.execute(text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = :name"),
                {"name": self.name})
            connection.execute(text(f'DROP DATABASE IF EXISTS "{self.name}"'))
        engine.dispose()

    def columns(self, table: str) -> set[str]:
        engine = create_engine(_sync_url(self.url), future=True)
        try:
            with engine.connect() as connection:
                rows = connection.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'public' AND table_name = :table"), {"table": table})
                return {row[0] for row in rows}
        finally:
            engine.dispose()


def _descriptor(model_id: str, *, active: bool = True,
                context_window: int | None = 128000) -> ModelDescriptor:
    return ModelDescriptor(
        ref=ModelRef(provider_id="devworld", model_id=model_id),
        display_name=model_id.upper(),
        family="acme",
        context_window=context_window,
        max_output_tokens=4096,
        supported_endpoints=(Endpoint.OPENAI_CHAT_COMPLETIONS,),
        capabilities={Capability.STREAMING: CapabilityState.SUPPORTED,
                      Capability.TOOLS: CapabilityState.UNKNOWN},
        capability_provenance={
            Capability.STREAMING: CapabilityProvenance.PROVIDER_METADATA},
        active=active,
        raw_metadata={"id": model_id},
        synced_at=datetime(2026, 9, 22, tzinfo=UTC),
    )


def test_a_previous_gate_database_upgrades() -> None:
    """The upgrade path a running installation takes, not only the fresh one."""
    with _DisposableDatabase() as database:
        assert _alembic(database.url, "upgrade", "0001_foundation").returncode == 0
        before = database.columns("models")
        assert "supports_tools" in before
        assert "capabilities" not in before

        result = _alembic(database.url, "upgrade", "head")

        assert result.returncode == 0, result.stdout
        after = database.columns("models")
        assert {"capabilities", "capability_provenance", "supported_endpoints", "active",
                "raw_metadata", "synced_at", "family", "max_output_tokens"} <= after
        assert "supports_tools" not in after
        assert "enabled" not in after
        assert {"adapter", "healthy", "last_health_check", "last_sync", "model_count",
                "detail"} <= database.columns("providers")
        assert {"request_id", "provider_id", "endpoint", "route", "status", "started_at",
                "finished_at", "cost", "retry_count", "fallback_count", "correlation_id",
                "request_fingerprint", "reasoning_tokens"} <= database.columns("model_calls")


def test_the_upgrade_carries_forward_what_the_booleans_said() -> None:
    """An operator's statement survives the column that used to hold it."""
    with _DisposableDatabase() as database:
        assert _alembic(database.url, "upgrade", "0001_foundation").returncode == 0
        engine = create_engine(_sync_url(database.url), isolation_level="AUTOCOMMIT", future=True)
        with engine.connect() as connection:
            connection.execute(text(
                "INSERT INTO providers (id, slug, name, kind, enabled) "
                "VALUES (gen_random_uuid(), 'devworld', 'DevWorld', 'http-api', true)"))
            connection.execute(text(
                "INSERT INTO models (id, provider_id, slug, display_name, supports_tools, "
                "enabled) SELECT gen_random_uuid(), id, 'model-one', 'Model One', true, true "
                "FROM providers WHERE slug = 'devworld'"))
        engine.dispose()

        assert _alembic(database.url, "upgrade", "head").returncode == 0

        engine = create_engine(_sync_url(database.url), future=True)
        try:
            with engine.connect() as connection:
                row = connection.execute(text(
                    "SELECT capabilities, capability_provenance, active FROM models")).first()
        finally:
            engine.dispose()

        assert row[0]["tools"] == "SUPPORTED"
        assert row[1]["tools"] == "MANUAL_CONFIGURATION"
        assert row[2] is True


def test_the_gateway_migration_is_reversible() -> None:
    with _DisposableDatabase() as database:
        assert _alembic(database.url, "upgrade", "head").returncode == 0

        result = _alembic(database.url, "downgrade", "0001_foundation")

        assert result.returncode == 0, result.stdout
        restored = database.columns("models")
        assert "supports_tools" in restored
        assert "capabilities" not in restored


def test_no_table_stores_a_prompt() -> None:
    """The shape of the schema is the control, not the discipline of the code above it."""
    with _DisposableDatabase() as database:
        assert _alembic(database.url, "upgrade", "head").returncode == 0

        for table in ("model_calls", "models", "providers"):
            names = database.columns(table)
            assert not names & {"prompt", "messages", "completion", "response", "content",
                                "reasoning", "api_key", "credential", "token", "secret"}


class _Scope:
    """One test's private corner of the stack's own database, and what it must take back out."""

    def __init__(self, factory) -> None:
        self.factory = factory
        self.provider = f"devworld-{uuid.uuid4().hex[:8]}"
        self.request_ids: list[str] = []

    def request_id(self, name: str) -> str:
        """A request identifier unique to this run, registered for removal."""
        identifier = f"{name}-{self.provider}"
        self.request_ids.append(identifier)
        return identifier


@asynccontextmanager
async def _scope() -> AsyncIterator[_Scope]:
    """Run against the stack's real database and leave it exactly as it was found.

    The store tests cannot use `_DisposableDatabase`: what they prove is that the stores work
    against the schema the running installation actually has. That makes cleanup part of the test
    rather than tidiness. A fixture left behind is a model sitting in the operational catalog that
    a route could resolve to, and a `model_calls` row per run accumulates for ever in the table the
    operator reads to find out what the gateway spent.
    """
    settings = stack_settings()
    engine = db_engine.create_engine(settings)
    scope = _Scope(db_engine.create_session_factory(engine))
    try:
        yield scope
    finally:
        try:
            async with scope.factory() as session:
                if scope.request_ids:
                    await session.execute(
                        delete(ModelCall).where(ModelCall.request_id.in_(scope.request_ids)))
                row = (await session.execute(
                    select(Provider).where(Provider.slug == scope.provider))).scalars().first()
                if row is not None:
                    await session.execute(delete(Model).where(Model.provider_id == row.id))
                    await session.execute(delete(Provider).where(Provider.id == row.id))
                await session.commit()
        finally:
            await engine.dispose()


async def test_the_catalog_store_round_trips_a_descriptor() -> None:
    async with _scope() as scope:
        store = SqlCatalogStore(scope.factory)
        await store.upsert_provider(ProviderRecord(
            provider_id=scope.provider, display_name="DevWorld", adapter="openai-compatible",
            enabled=True, healthy=True, last_health_check=datetime.now(UTC),
            last_sync=datetime.now(UTC), model_count=1, detail=None))

        descriptor = _descriptor("model-one").model_copy(
            update={"ref": ModelRef(provider_id=scope.provider, model_id="model-one")})
        outcome = await store.replace_provider_models(scope.provider, [descriptor])

        assert outcome.added == 1
        stored = await store.list_models(provider_id=scope.provider)
        assert stored[0].display_name == "MODEL-ONE"
        assert stored[0].context_window == 128000
        assert stored[0].capability(Capability.STREAMING) is CapabilityState.SUPPORTED
        assert stored[0].capability(Capability.TOOLS) is CapabilityState.UNKNOWN
        assert stored[0].supported_endpoints == (Endpoint.OPENAI_CHAT_COMPLETIONS,)
        assert stored[0].synced_at is not None


async def test_synchronisation_is_idempotent_and_deactivates_rather_than_deletes() -> None:
    async with _scope() as scope:
        store = SqlCatalogStore(scope.factory)
        first = _descriptor("keep").model_copy(
            update={"ref": ModelRef(provider_id=scope.provider, model_id="keep")})
        second = _descriptor("drop").model_copy(
            update={"ref": ModelRef(provider_id=scope.provider, model_id="drop")})

        await store.replace_provider_models(scope.provider, [first, second])
        again = await store.replace_provider_models(scope.provider, [first, second])
        assert again.unchanged == 2
        assert again.added == 0

        after = await store.replace_provider_models(scope.provider, [first])

        assert after.deactivated == 1
        everything = {model.ref.model_id: model
                      for model in await store.list_models(provider_id=scope.provider)}
        assert set(everything) == {"keep", "drop"}
        assert not everything["drop"].active
        assert [model.ref.model_id for model
                in await store.list_models(provider_id=scope.provider, active=True)] == ["keep"]


async def test_model_call_persistence_records_the_operational_metadata() -> None:
    async with _scope() as scope:
        catalog = SqlCatalogStore(scope.factory)
        calls = SqlModelCallStore(scope.factory)
        descriptor = _descriptor("model-one").model_copy(
            update={"ref": ModelRef(provider_id=scope.provider, model_id="model-one")})
        await catalog.replace_provider_models(scope.provider, [descriptor])
        request_id = scope.request_id("req-metadata")

        started = datetime.now(UTC)
        await calls.record(ModelCallRecord(
            request_id=request_id, provider_id=scope.provider, model_id="model-one",
            endpoint="openai-chat-completions", route="default", purpose="DEFAULT_MODEL",
            status="SUCCEEDED", succeeded=True, started_at=started, finished_at=started,
            latency_ms=42, input_tokens=11, output_tokens=3, cached_input_tokens=1,
            reasoning_tokens=2, cost=None, error_type=None, retry_count=0, fallback_count=0,
            correlation_id="correlation-under-test", request_fingerprint="a" * 64))

        async with scope.factory() as session:
            row = (await session.execute(
                select(ModelCall).where(ModelCall.request_id == request_id))).scalars().first()

        assert row is not None
        assert row.status == "SUCCEEDED"
        assert row.latency_ms == 42
        assert row.input_tokens == 11
        assert row.reasoning_tokens == 2
        assert row.cost is None
        assert row.correlation_id == "correlation-under-test"
        assert row.model_id is not None
        assert row.provider_id is not None


async def test_a_call_against_a_model_the_catalog_lost_is_still_recorded() -> None:
    """Losing the record of a call that cost money is worse than losing the link to a row."""
    async with _scope() as scope:
        calls = SqlModelCallStore(scope.factory)
        request_id = scope.request_id("req-orphan")

        started = datetime.now(UTC)
        await calls.record(ModelCallRecord(
            request_id=request_id, provider_id="a-provider-that-was-never-stored",
            model_id="a-model-that-was-never-stored", endpoint="openai-chat-completions",
            route=None, purpose="EXPLICIT_MODEL", status="FAILED", succeeded=False,
            started_at=started, finished_at=started, error_type="MODEL_NOT_FOUND"))

        async with scope.factory() as session:
            row = (await session.execute(
                select(ModelCall).where(ModelCall.request_id == request_id))).scalars().first()

        assert row is not None
        assert row.model_id is None
        assert row.provider_id is None
        assert row.error_code == "MODEL_NOT_FOUND"


async def test_the_operational_catalog_holds_only_providers_the_policy_declares() -> None:
    """The control over the defect this test was written for: a fixture left in the real catalog.

    Every provider row is created either by the catalog synchroniser, from
    `.iacode/policies/providers.json`, or by a test writing through the same store. A slug the
    policy does not declare is therefore residue, and residue in this table is a model an operator
    can see in the catalog and a router could resolve to. Asserting the invariant is cheaper than
    trusting each test to clean up after itself.
    """
    settings = stack_settings()
    declared = {config.provider_id
                for config in load_provider_configs(Path(settings.gateway_policy_dir))}
    engine = db_engine.create_engine(settings)
    try:
        factory = db_engine.create_session_factory(engine)
        async with factory() as session:
            slugs = set((await session.execute(select(Provider.slug))).scalars().all())
    finally:
        await engine.dispose()

    assert slugs <= declared, f"undeclared providers in the operational catalog: {slugs - declared}"
