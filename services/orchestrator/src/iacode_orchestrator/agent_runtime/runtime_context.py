"""What the activities need, built once per worker process.

An activity is a module-level function — that is how the Temporal SDK registers one — so it cannot
take its dependencies as constructor arguments. The alternative to a process-level context is a
global session factory, a global gateway client and a global registry, each initialised by whichever
import happened first. One explicitly built, explicitly installed context is the smaller evil: it is
created by :func:`build_context`, installed by the worker at start-up, and read by
:func:`get_context`, which fails loudly rather than lazily constructing something out of ambient
configuration.

Note what is **not** here: no provider, no provider policy, no credential and no gateway
composition. The worker reaches a model by calling the Model Gateway's published HTTP contract, so
the only address it holds is the IACode API's own.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from iacode_agent_runtime.gateway_client import GatewayModelClient
from iacode_agent_runtime.limits import RuntimeLimits
from iacode_agent_runtime.persistence import SqlAgentRunStore
from iacode_agent_runtime.registry import AgentRegistry
from iacode_agent_runtime.telemetry import AgentRuntimeMetrics
from iacode_evaluator.policy import load_policy
from iacode_evaluator.service import QualityService
from iacode_evaluator.snapshots import SnapshotProjectReader
from iacode_evaluator.store import SqlQualityStore
from iacode_persistence.engine import create_engine, create_session_factory
from minio import Minio
from prometheus_client import CollectorRegistry
from sqlalchemy.ext.asyncio import AsyncEngine

from iacode_orchestrator.config import WorkerSettings

__all__ = ["RuntimeContext", "build_context", "get_context", "set_context"]


@dataclass
class RuntimeContext:
    """Everything one worker process owns on behalf of the agent runtime."""

    settings: WorkerSettings
    store: SqlAgentRunStore
    model_client: GatewayModelClient
    registry: AgentRegistry
    metrics: AgentRuntimeMetrics
    limits: RuntimeLimits
    prometheus: CollectorRegistry
    engine: AsyncEngine
    quality_store: SqlQualityStore
    quality_service: QualityService
    quality_snapshots: SnapshotProjectReader

    async def close(self) -> None:
        await self.engine.dispose()


_context: RuntimeContext | None = None


def build_context(
    settings: WorkerSettings, registry: CollectorRegistry | None = None
) -> RuntimeContext:
    """Compose the runtime for this process. No I/O happens here: every client connects lazily."""
    prometheus = registry if registry is not None else CollectorRegistry()
    engine = create_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        connect_timeout_seconds=settings.database_connect_timeout_seconds,
    )
    factory = create_session_factory(engine)
    quality_store = SqlQualityStore(factory)
    objects = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )
    return RuntimeContext(
        settings=settings,
        store=SqlAgentRunStore(factory),
        model_client=GatewayModelClient(
            base_url=settings.agent_runtime_gateway_url,
            max_output_tokens=settings.agent_runtime_max_output_tokens,
            timeout_seconds=settings.agent_runtime_request_timeout_seconds,
        ),
        registry=AgentRegistry(Path(settings.repository_root)),
        metrics=AgentRuntimeMetrics(prometheus, service="iacode-agent-runtime"),
        limits=RuntimeLimits(),
        prometheus=prometheus,
        engine=engine,
        quality_store=quality_store,
        quality_service=QualityService(
            registry=load_policy(
                Path(settings.repository_root) / ".iacode" / "policies" / "quality-policy.json"
            ),
            store=quality_store,
        ),
        quality_snapshots=SnapshotProjectReader(factory, objects),
    )


def set_context(context: RuntimeContext | None) -> None:
    global _context
    _context = context


def get_context() -> RuntimeContext:
    if _context is None:
        raise RuntimeError(
            "the agent runtime context is not installed; the worker installs it at start-up"
        )
    return _context
