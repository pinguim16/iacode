"""Durable execution, against the real Temporal and the real worker.

A connection proves Temporal is reachable. Only executing a workflow proves the durable-execution
path works, because the activity runs in a different process and its result travels back through
Temporal's history.

The worker is the one the Compose stack started, so what is verified is the deployment rather than
an in-process worker a test spun up for itself.
"""

from __future__ import annotations

import uuid

import pytest
from iacode_api.workflows.client import TemporalGateway
from temporalio.client import Client

from tests.conftest import stack_is_configured, stack_settings

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not stack_is_configured(),
                       reason="the Foundation stack is not configured for this process"),
]

# The task queue the worker polls. The API deliberately does not carry this setting — it starts no
# workflow in Gate 0 — so the test reads it the same way the worker does.
TASK_QUEUE = "iacode-foundation"
SMOKE_WORKFLOW = "IACodeFoundationSmoke"
EXECUTION_TIMEOUT_SECONDS = 60.0


async def _client() -> Client:
    settings = stack_settings()
    return await Client.connect(settings.temporal_target, namespace=settings.temporal_namespace)


async def test_worker_registers_the_smoke_workflow() -> None:
    """Temporal itself reports a poller on our queue.

    "The worker process is running" is the wrong question: a worker whose connection has dropped is
    still a running process. Asking Temporal is what makes this observable.
    """
    import os

    from temporalio.api.enums.v1 import TaskQueueType
    from temporalio.api.taskqueue.v1 import TaskQueue
    from temporalio.api.workflowservice.v1 import DescribeTaskQueueRequest

    queue = os.environ.get("IACODE_TEMPORAL_TASK_QUEUE", TASK_QUEUE)
    client = await _client()
    response = await client.workflow_service.describe_task_queue(
        DescribeTaskQueueRequest(
            namespace=client.namespace,
            task_queue=TaskQueue(name=queue),
            task_queue_type=TaskQueueType.TASK_QUEUE_TYPE_WORKFLOW,
        )
    )

    pollers = list(response.pollers)
    assert pollers, f"no worker polls {queue!r}"
    assert any("iacode-worker" in poller.identity for poller in pollers), \
        f"pollers are {[poller.identity for poller in pollers]}"


async def test_smoke_workflow_executes_end_to_end() -> None:
    """The whole path: start a workflow, the worker runs the activity, the result comes back."""
    import os

    queue = os.environ.get("IACODE_TEMPORAL_TASK_QUEUE", TASK_QUEUE)
    client = await _client()

    result = await client.execute_workflow(
        SMOKE_WORKFLOW,
        {"message": "integration-smoke", "requestedBy": "pytest"},
        id=f"iacode-integration-smoke-{uuid.uuid4()}",
        task_queue=queue,
        result_type=dict,
    )

    assert result["message"] == "integration-smoke"
    assert result["requestedBy"] == "pytest"
    # The activity reports facts only the worker process can know. A constant would pass a check
    # that proves nothing.
    assert result["workerIdentity"], "the activity did not report where it ran"
    assert result["executedAt"].endswith("Z")
    assert result["workflowId"].startswith("iacode-integration-smoke-")


async def test_the_workflow_result_is_recorded_in_history() -> None:
    """Durable means the run is inspectable afterwards, not only that it returned."""
    import os

    queue = os.environ.get("IACODE_TEMPORAL_TASK_QUEUE", TASK_QUEUE)
    client = await _client()
    workflow_id = f"iacode-integration-history-{uuid.uuid4()}"

    handle = await client.start_workflow(
        SMOKE_WORKFLOW,
        {"message": "history", "requestedBy": "pytest"},
        id=workflow_id,
        task_queue=queue,
        result_type=dict,
    )
    await handle.result()

    description = await client.get_workflow_handle(workflow_id).describe()
    assert description.status is not None
    assert description.status.name == "COMPLETED"


async def test_temporal_readiness_fails_against_an_unknown_namespace() -> None:
    """Readiness describes the *configured* namespace, so a typo is caught before the first start.

    A probe that only opened a connection would report a misconfigured namespace as healthy, and
    the failure would surface on the first workflow instead.
    """
    settings = stack_settings().model_copy(
        update={"temporal_namespace": "a-namespace-that-does-not-exist"})
    gateway = TemporalGateway(settings)
    try:
        with pytest.raises(Exception):  # noqa: B017 - any failure is the point
            await gateway.ping()
    finally:
        await gateway.close()
