"""Health means every dependency and both required Temporal pollers answer."""

from __future__ import annotations

import asyncio
import sys

from iacode_contracts.quality import QUALITY_TASK_QUEUE
from iacode_contracts.sandbox import SANDBOX_TASK_QUEUE
from temporalio.client import Client

from iacode_evaluator.config import get_evaluator_settings, minio_client

TIMEOUT_SECONDS = 8.0


async def _poller(client: Client, namespace: str, queue: str, queue_type: object) -> None:
    from temporalio.api.taskqueue.v1 import TaskQueue
    from temporalio.api.workflowservice.v1 import DescribeTaskQueueRequest

    response = await asyncio.wait_for(
        client.workflow_service.describe_task_queue(
            DescribeTaskQueueRequest(
                namespace=namespace,
                task_queue=TaskQueue(name=queue),
                task_queue_type=queue_type,
            )
        ),
        timeout=TIMEOUT_SECONDS,
    )
    if not list(response.pollers):
        raise RuntimeError(f"no poller is registered on {queue!r}")


async def _check() -> str:
    from iacode_persistence.engine import create_engine, ping
    from temporalio.api.enums.v1 import TaskQueueType

    settings = get_evaluator_settings()
    client = await asyncio.wait_for(
        Client.connect(settings.temporal_target, namespace=settings.temporal_namespace),
        timeout=TIMEOUT_SECONDS,
    )
    await _poller(
        client,
        settings.temporal_namespace,
        QUALITY_TASK_QUEUE,
        TaskQueueType.TASK_QUEUE_TYPE_WORKFLOW,
    )
    await _poller(
        client,
        settings.temporal_namespace,
        SANDBOX_TASK_QUEUE,
        TaskQueueType.TASK_QUEUE_TYPE_ACTIVITY,
    )
    engine = create_engine(
        settings.database_url,
        pool_size=1,
        max_overflow=0,
        connect_timeout_seconds=settings.database_connect_timeout_seconds,
    )
    try:
        await asyncio.wait_for(ping(engine), timeout=TIMEOUT_SECONDS)
    finally:
        await engine.dispose()
    objects = minio_client(settings)
    exists = await asyncio.wait_for(
        asyncio.to_thread(objects.bucket_exists, settings.minio_bucket), timeout=TIMEOUT_SECONDS
    )
    if not exists:
        raise RuntimeError(f"artifact bucket {settings.minio_bucket!r} does not exist")
    return "quality and sandbox pollers, PostgreSQL, and artifact storage are ready"


def main() -> int:
    try:
        detail = asyncio.run(_check())
    except Exception as error:
        print(f"evaluator unhealthy: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(detail)
    return 0


if __name__ == "__main__":
    sys.exit(main())
