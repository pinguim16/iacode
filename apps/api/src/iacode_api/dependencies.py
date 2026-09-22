"""FastAPI dependency providers.

Every provider reads from ``request.app.state``. Nothing is imported from module scope, because a
module-level client is process state that two application instances would share, and a test that
builds its own application would then be talking to the previous one's connection pool.

The readiness probe list is built here too: it is the one place that knows both which clients exist
and which of them readiness depends on.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from minio import Minio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from iacode_api.cache import client as cache_client
from iacode_api.config import Settings
from iacode_api.db import engine as db_engine
from iacode_api.lifespan import Resources
from iacode_api.observability.metrics import Metrics
from iacode_api.readiness import DependencyProbe
from iacode_api.storage import client as storage_client


def get_resources(request: Request) -> Resources:
    resources = getattr(request.app.state, "resources", None)
    if resources is None:
        # Reachable only if a request is served outside the lifespan, which means the application
        # was built wrongly. Failing loudly beats a ``NoneType`` error three frames deeper.
        raise RuntimeError("application resources are not initialised")
    return resources


def get_settings(request: Request) -> Settings:
    return get_resources(request).settings


def get_metrics(request: Request) -> Metrics:
    return get_resources(request).metrics


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """A request-scoped unit of work, committed on success and rolled back on failure."""
    resources = get_resources(request)
    async with db_engine.session_scope(resources.session_factory) as session:
        yield session


def get_redis(request: Request) -> Redis:
    return get_resources(request).redis


def get_minio(request: Request) -> Minio:
    return get_resources(request).minio


def build_probes(resources: Resources) -> list[DependencyProbe]:
    """The dependencies readiness is allowed to depend on.

    All four are mandatory. The API's job from Gate 2 onwards is to accept a task, persist it,
    cache state, store artifacts and start a workflow; it cannot do that without any one of them,
    so declaring one optional would make readiness a claim rather than a measurement.
    """
    settings = resources.settings
    return [
        DependencyProbe(
            name="postgres",
            probe=lambda: db_engine.ping(resources.engine),
            mandatory=True,
        ),
        DependencyProbe(
            name="redis",
            probe=lambda: cache_client.ping(resources.redis),
            mandatory=True,
        ),
        DependencyProbe(
            name="minio",
            probe=lambda: storage_client.ping(resources.minio, settings.minio_bucket),
            mandatory=True,
        ),
        DependencyProbe(
            name="temporal",
            probe=resources.temporal.ping,
            mandatory=True,
        ),
    ]


ResourcesDep = Annotated[Resources, Depends(get_resources)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
