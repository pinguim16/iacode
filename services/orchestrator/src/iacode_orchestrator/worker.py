"""The IACode Temporal worker.

A separate process from the API, deliberately. A worker embedded in the web application would tie
workflow execution to the request-serving process: restarting the API to deploy a route change
would interrupt running workflows, and a worker busy with activities would compete with request
handling for the same event loop.

The worker connects with a retry loop instead of failing fast. Temporal's ``auto-setup`` image
provisions its schema on first boot, which takes appreciably longer than the API takes to start, and
a worker that exits on the first refused connection turns that into a restart loop that looks like a
crash. Connecting is the one place where waiting is right: the API does the opposite, because it has
a readiness endpoint to report the wait through and the worker has nowhere to report it.

Shutdown is graceful. ``SIGTERM`` stops polling and lets in-flight activities finish before the
process exits, so ``docker compose stop`` does not abandon a running workflow task.
"""

from __future__ import annotations

import asyncio
import contextlib
import signal
import sys

from iacode_telemetry.logging import configure_logging, get_logger
from prometheus_client import start_http_server
from temporalio.client import Client
from temporalio.worker import Worker

from iacode_orchestrator.agent_runtime.activities import AGENT_RUNTIME_ACTIVITIES
from iacode_orchestrator.agent_runtime.runtime_context import build_context, set_context
from iacode_orchestrator.config import WorkerSettings, get_worker_settings
from iacode_orchestrator.runtime import get_runtime
from iacode_orchestrator.workflows.agent_run import AgentRunWorkflow
from iacode_orchestrator.workflows.smoke import SmokeWorkflow, echo

logger = get_logger(__name__)

CONNECT_RETRY_SECONDS = 3.0


async def connect(settings: WorkerSettings) -> Client:
    """Connect to Temporal, retrying until the deadline the configuration sets."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + settings.connect_timeout_seconds
    attempt = 0
    last_error: Exception | None = None
    while loop.time() < deadline:
        attempt += 1
        try:
            return await Client.connect(
                settings.temporal_target,
                namespace=settings.namespace,
                runtime=get_runtime(),
            )
        except Exception as error:
            last_error = error
            logger.warning(
                "temporal not reachable yet; retrying",
                extra={"attempt": attempt, "target": settings.temporal_target})
            await asyncio.sleep(CONNECT_RETRY_SECONDS)
    raise RuntimeError(
        f"could not connect to Temporal at {settings.temporal_target} within "
        f"{settings.connect_timeout_seconds:g}s") from last_error


async def run(settings: WorkerSettings | None = None) -> int:
    settings = settings or get_worker_settings()
    configure_logging(
        service=settings.service_name, level=settings.log_level, version=settings.version)

    client = await connect(settings)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    # Named rather than looked up. The agent runtime boundary resolves no name at runtime — a
    # tool name least of all — and a repository-wide control enforces that, so this module does
    # not get an exception for the convenience of a loop over two strings.
    for received in (signal.SIGTERM if hasattr(signal, "SIGTERM") else None,
                     signal.SIGINT if hasattr(signal, "SIGINT") else None):
        if received is None:
            continue
        with contextlib.suppress(NotImplementedError):
            # Windows has no signal handlers on the proactor loop. The worker runs in Linux
            # containers, so the suppression is about not crashing during a local developer run.
            loop.add_signal_handler(received, stop.set)

    # Gate 2 adds the agent runtime. It is composed once per process and installed where the
    # activities can read it, because an activity is a module-level function and cannot be handed
    # its dependencies any other way.
    context = build_context(settings)
    set_context(context)
    start_http_server(settings.agent_runtime_metrics_port, registry=context.prometheus)

    foundation = Worker(
        client,
        task_queue=settings.task_queue,
        workflows=[SmokeWorkflow],
        activities=[echo],
        identity=settings.identity,
    )
    # A queue of its own for agent runs. A long run waiting on a tool holds a workflow task slot,
    # and sharing one queue would let a paused run starve the Foundation smoke check — which is the
    # thing an operator reaches for when they want to know whether durable execution works at all.
    agent_runtime = Worker(
        client,
        task_queue=settings.agent_runtime_task_queue,
        workflows=[AgentRunWorkflow],
        activities=AGENT_RUNTIME_ACTIVITIES,
        identity=settings.identity,
    )
    logger.info(
        "worker started",
        extra={"taskQueue": settings.task_queue,
               "agentRuntimeTaskQueue": settings.agent_runtime_task_queue,
               "namespace": settings.namespace})

    try:
        async with foundation, agent_runtime:
            await stop.wait()
    finally:
        set_context(None)
        await context.close()

    # The SDK exposes no explicit close; the connection is released when the client is dropped.
    logger.info("worker stopped")
    return 0


def main() -> int:
    try:
        return asyncio.run(run())
    except KeyboardInterrupt:
        return 0
    except Exception as error:
        configure_logging(service="iacode-worker")
        get_logger(__name__).error("worker failed to start", exc_info=error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
