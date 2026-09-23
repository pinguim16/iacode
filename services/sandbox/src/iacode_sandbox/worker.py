"""The sandbox service process: a Temporal worker on the sandbox queue, and a sweeper.

The orchestrator's workflow reaches the sandbox through two activities on
:data:`~iacode_contracts.sandbox.SANDBOX_TASK_QUEUE` and through nothing else: there is no HTTP
surface, no published port and no shell. This process is the only one in the stack that holds the
container engine's socket, and it hands that socket to no sandbox.

At start it reconciles the store with the engine (`SandboxService.reconcile`), because a restart
must not trust memory; while it runs it sweeps expired sessions on a fixed interval, a bounded
number at a time.

    python -m iacode_sandbox.worker
"""

from __future__ import annotations

import asyncio
import contextlib
import signal
import sys
from pathlib import Path
from typing import Any

from iacode_contracts.sandbox import (
    SANDBOX_EXECUTE_ACTIVITY,
    SANDBOX_RELEASE_ACTIVITY,
    SANDBOX_TASK_QUEUE,
)
from iacode_telemetry.logging import configure_logging, get_logger
from temporalio import activity
from temporalio.client import Client
from temporalio.worker import Worker

from iacode_sandbox.config import SandboxSettings, get_sandbox_settings

__all__ = ["ACTIVITIES", "execute_tool", "release_run", "run", "set_service"]

logger = get_logger(__name__)

_SERVICE: Any = None


def set_service(service: Any) -> None:
    """Install the service the activities use. An activity cannot be handed its dependencies."""
    global _SERVICE
    _SERVICE = service


def _service() -> Any:
    if _SERVICE is None:
        raise RuntimeError("the sandbox service has not been installed in this process")
    return _SERVICE


@activity.defn(name=SANDBOX_EXECUTE_ACTIVITY)
async def execute_tool(payload: dict[str, Any]) -> dict[str, Any]:
    """Execute one tool request in the run's sandbox and return the result as data."""
    result = await _service().execute(payload, heartbeat=activity.heartbeat)
    return result.to_dict()


@activity.defn(name=SANDBOX_RELEASE_ACTIVITY)
async def release_run(payload: dict[str, Any]) -> dict[str, Any]:
    """End every session of a run that has reached its end."""
    released = await _service().release_run(str(payload["runId"]))
    return {"runId": str(payload["runId"]), "released": released}


ACTIVITIES = [execute_tool, release_run]


def build_service(settings: SandboxSettings):
    """Compose the service from the stack this process can reach."""
    from iacode_persistence.engine import create_engine, create_session_factory
    from prometheus_client import CollectorRegistry

    from iacode_sandbox.artifacts import MinioArtifactSink
    from iacode_sandbox.backend import DockerBackend
    from iacode_sandbox.config import minio_client
    from iacode_sandbox.policy import load_policy_registry
    from iacode_sandbox.service import SandboxService
    from iacode_sandbox.snapshots import SnapshotReader
    from iacode_sandbox.store import SqlSandboxStore
    from iacode_sandbox.telemetry import SandboxMetrics

    engine = create_engine(settings.database_url, pool_size=settings.database_pool_size,
                           max_overflow=settings.database_max_overflow,
                           connect_timeout_seconds=settings.database_connect_timeout_seconds)
    factory = create_session_factory(engine)
    store = SqlSandboxStore(factory)
    client = minio_client(settings)
    registry = CollectorRegistry()
    service = SandboxService(
        root=Path(settings.repository_root),
        policies=load_policy_registry(Path(settings.repository_root)),
        backend=DockerBackend(), store=store,
        artifacts=MinioArtifactSink(client, settings.minio_bucket, store),
        metrics=SandboxMetrics(registry), snapshot_reader=SnapshotReader(factory, client),
        owner=settings.sandbox_owner)
    return service, engine, registry


async def _connect(settings: SandboxSettings) -> Client:
    deadline = asyncio.get_running_loop().time() + settings.worker_connect_timeout_seconds
    last_error: Exception | None = None
    while asyncio.get_running_loop().time() < deadline:
        try:
            return await Client.connect(settings.temporal_target,
                                        namespace=settings.temporal_namespace)
        except Exception as error:  # retried until the deadline, then raised
            last_error = error
            logger.warning("temporal not reachable yet; retrying",
                           extra={"target": settings.temporal_target})
            await asyncio.sleep(3)
    raise RuntimeError(f"could not connect to Temporal at {settings.temporal_target}"
                       ) from last_error


async def _sweep_forever(service: Any, settings: SandboxSettings, stop: asyncio.Event) -> None:
    while not stop.is_set():
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=settings.sandbox_sweep_interval_seconds)
        if stop.is_set():
            return
        try:
            expired = await service.sweep(limit=settings.sandbox_sweep_batch)
            if expired:
                logger.info("expired sandbox sessions swept", extra={"count": len(expired)})
        except Exception as error:  # a failed sweep is logged and retried later
            logger.error("sandbox sweep failed", exc_info=error)


async def run(settings: SandboxSettings | None = None) -> int:
    from prometheus_client import start_http_server

    settings = settings or get_sandbox_settings()
    configure_logging(service=settings.service_name, level=settings.log_level,
                      version=settings.version)
    service, engine, registry = build_service(settings)
    set_service(service)
    start_http_server(settings.sandbox_metrics_port, registry=registry)

    report = await service.reconcile()
    logger.info("sandbox sessions reconciled",
                extra={key: len(value) for key, value in report.items()})

    client = await _connect(settings)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for received in (getattr(signal, "SIGTERM", None), getattr(signal, "SIGINT", None)):
        if received is not None:
            with contextlib.suppress(NotImplementedError):
                loop.add_signal_handler(received, stop.set)

    worker = Worker(client, task_queue=SANDBOX_TASK_QUEUE, activities=ACTIVITIES,
                    identity=settings.identity, max_concurrent_activities=8)
    sweeper = asyncio.create_task(_sweep_forever(service, settings, stop))
    logger.info("sandbox service started", extra={"taskQueue": SANDBOX_TASK_QUEUE})
    try:
        async with worker:
            await stop.wait()
    finally:
        stop.set()
        await sweeper
        set_service(None)
        await engine.dispose()
    logger.info("sandbox service stopped")
    return 0


def main() -> int:
    try:
        return asyncio.run(run())
    except KeyboardInterrupt:
        return 0
    except Exception as error:  # the process exits non-zero with the reason logged
        configure_logging(service="iacode-sandbox")
        get_logger(__name__).error("sandbox service failed to start", exc_info=error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
