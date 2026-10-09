"""Quality Engine process: Temporal worker plus Prometheus endpoint."""

from __future__ import annotations

import asyncio
import contextlib
import signal
import sys

from iacode_contracts.quality import QUALITY_TASK_QUEUE
from iacode_telemetry.logging import configure_logging, get_logger
from prometheus_client import start_http_server
from temporalio.client import Client
from temporalio.worker import Worker

from iacode_evaluator.activities import ACTIVITIES, set_runtime
from iacode_evaluator.config import EvaluatorSettings, get_evaluator_settings
from iacode_evaluator.runtime import build_runtime
from iacode_evaluator.workflow import QualityRunWorkflow

logger = get_logger(__name__)


async def _connect(settings: EvaluatorSettings) -> Client:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + settings.worker_connect_timeout_seconds
    last_error: Exception | None = None
    while loop.time() < deadline:
        try:
            return await Client.connect(
                settings.temporal_target, namespace=settings.temporal_namespace
            )
        except Exception as error:
            last_error = error
            logger.warning(
                "temporal not reachable yet; retrying", extra={"target": settings.temporal_target}
            )
            await asyncio.sleep(3)
    raise RuntimeError(
        f"could not connect to Temporal at {settings.temporal_target}"
    ) from last_error


async def run(settings: EvaluatorSettings | None = None) -> int:
    settings = settings or get_evaluator_settings()
    if settings.quality_task_queue != QUALITY_TASK_QUEUE:
        raise RuntimeError(
            f"quality task queue must be the shared contract value {QUALITY_TASK_QUEUE!r}"
        )
    configure_logging(
        service=settings.service_name, level=settings.log_level, version=settings.version
    )
    runtime = build_runtime(settings)
    set_runtime(runtime)
    start_http_server(settings.quality_metrics_port, registry=runtime.registry)
    client = await _connect(settings)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for received in (getattr(signal, "SIGTERM", None), getattr(signal, "SIGINT", None)):
        if received is not None:
            with contextlib.suppress(NotImplementedError):
                loop.add_signal_handler(received, stop.set)
    worker = Worker(
        client,
        task_queue=QUALITY_TASK_QUEUE,
        workflows=[QualityRunWorkflow],
        activities=ACTIVITIES,
        identity=settings.identity,
        max_concurrent_activities=8,
    )
    logger.info("quality worker started", extra={"taskQueue": QUALITY_TASK_QUEUE})
    try:
        async with worker:
            await stop.wait()
    finally:
        set_runtime(None)
        await runtime.close()
    logger.info("quality worker stopped")
    return 0


def main() -> int:
    try:
        return asyncio.run(run())
    except KeyboardInterrupt:
        return 0
    except Exception as error:
        configure_logging(service="iacode-evaluator")
        get_logger(__name__).error("quality worker failed to start", exc_info=error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
