"""Dependency lifecycle.

Everything the API holds open is created here, stored on ``app.state`` and released here. There is
no module-level client and no lazily-initialised global: `docs/GATE-0-CHECKLIST.md` row 3.3 asks for
an explicit lifecycle, and ambient globals are what make a second application instance in the same
interpreter — a test suite — share a connection pool with the first.

**Startup does no I/O.** Every client here connects lazily. That is what lets the API start while
PostgreSQL is still initialising and report ``NOT_READY`` until it is, instead of crash-looping. An
API that refuses to start without its database turns a ten-second dependency delay into a restart
storm, and readiness exists precisely so it does not have to.

**Shutdown releases everything, even when part of it fails.** Each release is attempted and its
failure logged, so one client that cannot close does not strand the three after it.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI
from iacode_telemetry.logging import get_logger
from minio import Minio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from iacode_api.agent_runtime.runtime import AgentRuntimeRuntime, build_agent_runtime
from iacode_api.cache import client as cache_client
from iacode_api.config import Settings
from iacode_api.db import engine as db_engine
from iacode_api.gateway.runtime import GatewayRuntime, build_runtime
from iacode_api.observability.metrics import Metrics
from iacode_api.storage import client as storage_client
from iacode_api.workflows.client import TemporalGateway

logger = get_logger(__name__)


@dataclass
class Resources:
    """Everything one application instance owns."""

    settings: Settings
    metrics: Metrics
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    redis: Redis
    minio: Minio
    temporal: TemporalGateway
    gateway: GatewayRuntime
    agent_runtime: AgentRuntimeRuntime


def build_resources(settings: Settings, metrics: Metrics) -> Resources:
    """Construct every client without performing any I/O."""
    engine = db_engine.create_engine(settings)
    session_factory = db_engine.create_session_factory(engine)
    return Resources(
        settings=settings,
        metrics=metrics,
        engine=engine,
        session_factory=session_factory,
        redis=cache_client.create_client(settings),
        minio=storage_client.create_client(settings),
        temporal=TemporalGateway(settings),
        # Reading the provider policy here rather than on first use means a missing or malformed
        # policy file stops the process at start-up, where it is one clear failure, instead of
        # turning every inference request into a confusing "no candidate".
        gateway=build_runtime(settings, session_factory, metrics.registry),
        # The declared agent and team profiles are read here for the same reason the provider
        # policy is: a malformed definition stops the process at start-up, where it is one
        # clear failure, instead of turning every run creation into a confusing refusal.
        agent_runtime=build_agent_runtime(settings, session_factory),
    )


async def release_resources(resources: Resources) -> list[str]:
    """Release every client, returning the names of the ones that failed to close."""
    failures: list[str] = []

    async def attempt(name: str, action: Any) -> None:
        try:
            await action
        except Exception as error:
            failures.append(name)
            logger.error("failed to release %s during shutdown", name, exc_info=error)

    await attempt("temporal", resources.temporal.close())
    await attempt("redis", cache_client.close(resources.redis))
    await attempt("database", resources.engine.dispose())
    # The MinIO SDK holds an urllib3 pool and exposes no close in this version; letting the object
    # go is the whole release. Saying so beats a no-op call that reads like cleanup.
    return failures


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Own the resources for exactly as long as the application is serving."""
    settings: Settings = app.state.settings
    resources = build_resources(settings, app.state.metrics)
    app.state.resources = resources
    logger.info(
        "api started",
        extra={"environment": settings.environment, "version": settings.version},
    )
    try:
        yield
    finally:
        failures = await release_resources(resources)
        app.state.resources = None
        logger.info("api stopped", extra={"releaseFailures": failures})
