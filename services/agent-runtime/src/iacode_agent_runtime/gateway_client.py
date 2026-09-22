"""The only path from the agent runtime to a model: the Model Gateway's own API.

This module is the whole of the runtime's relationship with inference. It sends one
:class:`~iacode_contracts.gateway.InferenceRequest` to the gateway endpoint and turns the answer
into a :class:`~iacode_agent_runtime.contracts.ModelCallOutcome`. That is all it does.

**It speaks the gateway's published contract, not a provider's.** The runtime does not import
``iacode_model_gateway`` at all: it imports the shared wire shapes in ``iacode_contracts.gateway``
and talks to the boundary over HTTP. That makes "the agent runtime never reaches a provider" a
property of the dependency graph rather than a promise — there is no provider adapter, no provider
client and no credential anywhere in this package to misuse, and a boundary scan in the suite
asserts it.

What it deliberately does **not** do:

- choose a provider, name one, or hold an address or a credential;
- retry a call the gateway has already retried;
- open a circuit, close one, or consult one;
- fall back to a second model;
- decide whether a model can serve a request.

Every one of those is a Gate 1 contract with its own tests. A second implementation here would be a
second answer that can disagree with the first, which is the failure class the engineering memory
already records.

**Structured output is used only where it is known to exist.** The catalog records a capability as
``SUPPORTED``, ``UNSUPPORTED`` or ``UNKNOWN``, and at the time of this Gate the configured provider
publishes nothing, so every capability is ``UNKNOWN``. The runtime therefore asks for a JSON object
in the prompt and validates it locally, and turns on the provider's native structured output only
for an explicitly named model the catalog says has it. Nothing here asserts a capability on a
model's behalf.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from iacode_contracts.gateway import InferenceRequest, MessagePayload, ResponseFormatPayload

from iacode_agent_runtime.contracts import ModelCallOutcome, TurnRequest
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.protocol import envelope_schema

__all__ = ["GatewayModelClient", "structured_output_supported"]

INFER_PATH = "/api/v1/gateway/infer"
MODELS_PATH = "/api/v1/gateway/models"

#: How long a catalog answer is reused before it is read again. Short enough that a catalog
#: synchronisation is picked up within a run, long enough that a multi-turn stage does not ask once
#: per turn. The client runs inside an activity, never inside workflow code, so reading a clock
#: here is not a determinism problem.
CATALOG_TTL_SECONDS = 60.0


def structured_output_supported(models: list[dict[str, Any]], model: str | None) -> bool:
    """Whether native structured output is *known* to be available for this request.

    ``True`` only for an explicitly named ``provider:model`` whose catalog entry says
    ``SUPPORTED``. An unknown capability answers ``False``, and so does a request that names a route
    rather than a model — a route resolves to a candidate list, and a capability that holds for the
    first candidate does not hold for the second.
    """
    if not model or ":" not in model:
        return False
    provider, _, identifier = model.partition(":")
    for entry in models:
        if entry.get("provider") != provider or entry.get("model") != identifier:
            continue
        capability = (entry.get("capabilities") or {}).get("structured-output") or {}
        return str(capability.get("state")) == "SUPPORTED"
    return False


@dataclass
class GatewayModelClient:
    """A :class:`~iacode_agent_runtime.ports.ModelClient` over the Model Gateway's HTTP API."""

    base_url: str
    max_output_tokens: int | None = None
    temperature: float | None = None
    timeout_seconds: float = 300.0
    purpose: str = "agent-turn"
    transport: httpx.AsyncBaseTransport | None = None

    _catalog: list[dict[str, Any]] = field(default_factory=list, init=False)
    _catalog_read_at: float = field(default=0.0, init=False)

    async def complete(self, request: TurnRequest) -> ModelCallOutcome:
        structured = request.structured_output and await self._structured(request.model)
        payload = InferenceRequest(
            messages=[
                # Two channels, and the separation is the point. What the runtime and the role
                # require goes in the system message; everything the run is *about* — the task, an
                # earlier stage's artifact, a tool result — goes in the user message inside
                # labelled blocks. A task concatenated into the system message would be
                # indistinguishable from an instruction, to the model and to a reader.
                MessagePayload(role="system", content=request.instructions),
                MessagePayload(role="user", content=request.data),
            ],
            model=request.model,
            route=None if request.model else request.route,
            temperature=self.temperature,
            maxOutputTokens=self.max_output_tokens,
            responseFormat=(
                ResponseFormatPayload(name="iacode_agent_envelope", jsonSchema=envelope_schema(),
                                      strict=True)
                if structured else None),
            metadata={"purpose": self.purpose, "runId": request.run_id,
                      "stage": str(request.stage_index), "turn": str(request.turn)},
        )
        body = await self._post(INFER_PATH, payload.model_dump(mode="json", exclude_none=True))
        usage = body.get("usage") or {}
        route = body.get("route") or {}
        return ModelCallOutcome(
            text=body.get("content") or "",
            model_call_id=None,
            gateway_request_id=str(body.get("requestId") or ""),
            provider=str(body.get("provider") or ""),
            model=str(body.get("model") or ""),
            endpoint=str(body.get("endpoint") or ""),
            route_reason=str(route.get("reason") or ""),
            finish_reason=str(body.get("finishReason") or ""),
            latency_ms=float(body.get("latencyMs") or 0.0),
            total_tokens=usage.get("totalTokens"),
            input_tokens=usage.get("inputTokens"),
            output_tokens=usage.get("outputTokens"),
            cost=body.get("cost"),
            cost_known=body.get("cost") is not None,
            repair_attempt=request.repair_of is not None,
        )

    # -- internals ---------------------------------------------------------------------------------

    async def _structured(self, model: str | None) -> bool:
        if not model:
            return False
        now = time.monotonic()
        if not self._catalog or now - self._catalog_read_at > CATALOG_TTL_SECONDS:
            try:
                body = await self._get(MODELS_PATH)
            except AgentRuntimeError:
                # A catalog the runtime could not read is a catalog that has told it nothing, which
                # is exactly the state in which native structured output must not be requested.
                return False
            self._catalog = list(body.get("models") or [])
            self._catalog_read_at = now
        return structured_output_supported(self._catalog, model)

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with self._client() as client:
            try:
                response = await client.post(path, json=payload)
            except httpx.HTTPError as error:
                raise self._unreachable(error) from error
            return self._read(response, path)

    async def _get(self, path: str) -> dict[str, Any]:
        async with self._client() as client:
            try:
                response = await client.get(path)
            except httpx.HTTPError as error:
                raise self._unreachable(error) from error
            return self._read(response, path)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url.rstrip("/"),
            timeout=httpx.Timeout(self.timeout_seconds),
            transport=self.transport,
            headers={"Accept": "application/json"},
        )

    @staticmethod
    def _unreachable(error: Exception) -> AgentRuntimeError:
        return AgentRuntimeError(
            AgentRuntimeErrorType.GATEWAY_ERROR,
            "the model gateway could not be reached",
            details={"reason": type(error).__name__},
            upstream_type="GATEWAY_UNREACHABLE")

    @staticmethod
    def _read(response: httpx.Response, path: str) -> dict[str, Any]:
        if response.status_code >= 400:
            try:
                body = response.json()
            except ValueError:
                body = {}
            # The gateway's own classification is kept rather than re-derived: it already
            # distinguishes an authentication failure from a rate limit from an open circuit, and a
            # second classifier here would be one that can disagree with the first.
            code = str(body.get("code") or f"HTTP_{response.status_code}")
            message = str(body.get("message") or "the model gateway refused the call")
            raise AgentRuntimeError(
                AgentRuntimeErrorType.GATEWAY_ERROR,
                f"the model gateway refused the call: {message}",
                details={"status": response.status_code,
                         **{key: value for key, value in (body.get("details") or {}).items()
                            if key in ("route", "routeReason", "reason", "considered", "limit")}},
                upstream_type=code)
        try:
            body = response.json()
        except ValueError as error:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.GATEWAY_ERROR,
                f"the model gateway answered {path} with something that is not JSON",
                upstream_type="GATEWAY_MALFORMED_RESPONSE") from error
        if not isinstance(body, dict):
            raise AgentRuntimeError(
                AgentRuntimeErrorType.GATEWAY_ERROR,
                f"the model gateway answered {path} with a non-object body",
                upstream_type="GATEWAY_MALFORMED_RESPONSE")
        return body
