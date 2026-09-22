"""Container healthcheck for the worker.

A worker has no HTTP surface, so the tempting healthcheck is "the process exists". That answers the
wrong question: a worker whose connection to Temporal has dropped is still a running process, and
Compose would keep reporting it healthy while no workflow task was being picked up.

This asks Temporal instead. ``DescribeTaskQueue`` returns the pollers currently registered on the
queue, so the check passes only when Temporal itself can see this worker polling. That is the
observable fact the healthcheck is supposed to establish.

Run as a module so the container command is stable:

    python -m iacode_orchestrator.healthcheck
"""

from __future__ import annotations

import asyncio
import sys

from temporalio.client import Client

from iacode_orchestrator.config import get_worker_settings

TIMEOUT_SECONDS = 8.0


async def _check() -> tuple[bool, str]:
    settings = get_worker_settings()
    client = await asyncio.wait_for(
        Client.connect(settings.temporal_target, namespace=settings.namespace),
        timeout=TIMEOUT_SECONDS,
    )
    from temporalio.api.enums.v1 import TaskQueueType
    from temporalio.api.taskqueue.v1 import TaskQueue
    from temporalio.api.workflowservice.v1 import DescribeTaskQueueRequest

    response = await asyncio.wait_for(
        client.workflow_service.describe_task_queue(
            DescribeTaskQueueRequest(
                namespace=settings.namespace,
                task_queue=TaskQueue(name=settings.task_queue),
                task_queue_type=TaskQueueType.TASK_QUEUE_TYPE_WORKFLOW,
            )
        ),
        timeout=TIMEOUT_SECONDS,
    )
    pollers = list(response.pollers)
    if not pollers:
        return False, f"no poller is registered on task queue {settings.task_queue!r}"
    identities = ", ".join(sorted({poller.identity for poller in pollers}))
    return True, f"{len(pollers)} poller(s) on {settings.task_queue}: {identities}"


def main() -> int:
    try:
        healthy, detail = asyncio.run(_check())
    except Exception as error:
        print(f"worker unhealthy: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(detail)
    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())
