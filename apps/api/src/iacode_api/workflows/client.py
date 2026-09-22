"""The Temporal client.

The API is a Temporal *client*: it connects, and from Gate 2 onwards it will start workflows. The
worker that executes them is a separate process, ``services/orchestrator``, because a worker inside
the API would tie workflow execution to the request-serving process's lifetime and scaling.

Connecting is not done at startup. ``Client.connect`` performs a real handshake, so a Temporal that
is still starting would either block the API's startup or crash it — and a liveness probe that
depends on a workflow engine is exactly what `docs/GATE-0-CHECKLIST.md` row 3.4 forbids. The client
is therefore connected on demand and cached, and readiness is what reports the connection's state.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

from temporalio.client import Client
from temporalio.exceptions import WorkflowAlreadyStartedError
from temporalio.service import RPCError

from iacode_api.config import Settings


class TemporalGateway:
    """A lazily connected, shared Temporal client.

    The lock matters: without it, the first burst of concurrent readiness probes each opens its own
    connection, and all but one are then discarded without being closed.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Client | None = None
        self._lock = asyncio.Lock()

    async def connect(self) -> Client:
        if self._client is not None:
            return self._client
        async with self._lock:
            if self._client is None:
                self._client = await asyncio.wait_for(
                    Client.connect(
                        self._settings.temporal_target,
                        namespace=self._settings.temporal_namespace,
                    ),
                    timeout=self._settings.readiness_timeout_seconds,
                )
        return self._client

    async def ping(self) -> None:
        """Prove Temporal answers, by asking the service rather than by owning a client object.

        A cached client object is not evidence: it survives the server going away. Describing the
        namespace is a real round trip to the frontend service, which is what readiness needs, and
        it fails when the namespace the configuration names does not exist -- a misconfiguration
        that would otherwise only appear on the first workflow start.
        """
        client = await self.connect()
        await asyncio.wait_for(
            client.workflow_service.describe_namespace(
                _describe_namespace_request(self._settings.temporal_namespace)),
            timeout=self._settings.readiness_timeout_seconds,
        )

    # --- Gate 2: starting and steering an agent run -------------------------------------------

    async def start_agent_run(self, *, workflow: str, workflow_id: str,
                              payload: dict[str, Any], task_queue: str,
                              execution_timeout_seconds: int) -> str:
        """Start the durable run, or adopt the one already running under this identifier.

        The workflow identifier is derived from the run identifier, so starting the same run twice
        is refused by Temporal itself. That is a second idempotency layer under the one the
        database provides, and it is the one that holds when two API processes race.
        """
        client = await self.connect()
        try:
            handle = await client.start_workflow(
                workflow,
                payload,
                id=workflow_id,
                task_queue=task_queue,
                execution_timeout=timedelta(seconds=execution_timeout_seconds),
            )
            return handle.id
        except WorkflowAlreadyStartedError:
            return workflow_id

    async def signal_agent_run(self, *, workflow_id: str, signal: str,
                               payload: Any = None) -> bool:
        """Deliver a signal, answering whether there was a running workflow to receive it.

        ``False`` rather than an exception when the workflow has already finished: a tool result
        arriving after a run ended is a case the API answers with a refusal of its own, and a
        transport error here would obscure it.
        """
        client = await self.connect()
        handle = client.get_workflow_handle(workflow_id)
        try:
            if payload is None:
                await handle.signal(signal)
            else:
                await handle.signal(signal, payload)
            return True
        except RPCError:
            return False

    async def close(self) -> None:
        """Drop the cached client.

        The SDK exposes no explicit close: ``ServiceClient`` owns a Rust-backed connection that is
        released when the object is dropped. Dropping the reference here is therefore the whole
        release, and saying so is better than calling a method that does not exist — an earlier
        version of this file called ``service_client.close()`` and the worker healthcheck failed
        with ``AttributeError`` rather than with anything about Temporal.
        """
        self._client = None


def _describe_namespace_request(namespace: str):
    from temporalio.api.workflowservice.v1 import DescribeNamespaceRequest

    return DescribeNamespaceRequest(namespace=namespace)
