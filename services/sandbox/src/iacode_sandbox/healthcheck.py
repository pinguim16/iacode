"""Container healthcheck: the sandbox queue has a poller, and the engine answers.

"The process exists" is the lazy answer. This asks the two questions that matter: does Temporal see
a worker polling the sandbox queue, and does the container engine answer this service's client.
"""

from __future__ import annotations

import asyncio
import sys

from iacode_contracts.sandbox import SANDBOX_TASK_QUEUE
from temporalio.client import Client

from iacode_sandbox.backend import DockerBackend
from iacode_sandbox.config import get_sandbox_settings

TIMEOUT_SECONDS = 8.0


async def _check() -> tuple[bool, str]:
    from temporalio.api.enums.v1 import TaskQueueType
    from temporalio.api.taskqueue.v1 import TaskQueue
    from temporalio.api.workflowservice.v1 import DescribeTaskQueueRequest

    settings = get_sandbox_settings()
    client = await asyncio.wait_for(
        Client.connect(settings.temporal_target, namespace=settings.temporal_namespace),
        timeout=TIMEOUT_SECONDS)
    response = await asyncio.wait_for(
        client.workflow_service.describe_task_queue(DescribeTaskQueueRequest(
            namespace=settings.temporal_namespace, task_queue=TaskQueue(name=SANDBOX_TASK_QUEUE),
            task_queue_type=TaskQueueType.TASK_QUEUE_TYPE_ACTIVITY)),
        timeout=TIMEOUT_SECONDS)
    if not list(response.pollers):
        return False, f"no poller is registered on {SANDBOX_TASK_QUEUE!r}"
    managed = await asyncio.to_thread(DockerBackend().managed, settings.sandbox_owner)
    return True, f"sandbox queue polled; {len(managed)} managed container(s)"


def main() -> int:
    try:
        healthy, detail = asyncio.run(_check())
    except Exception as error:  # any failure is an unhealthy answer
        print(f"sandbox unhealthy: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(detail)
    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())
