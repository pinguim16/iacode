"""The only path to a model: the Model Gateway's published HTTP contract."""

from __future__ import annotations

import json

import httpx
import pytest
from iacode_agent_runtime.contracts import TurnRequest
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.gateway_client import (
    GatewayModelClient,
    structured_output_supported,
)

ANSWER = {
    "contractVersion": "1.0.0",
    "requestId": "req-1",
    "provider": "devworld",
    "model": "some-model",
    "endpoint": "openai-chat-completions",
    "content": '{"kind": "FINAL", "content": "ok"}',
    "finishReason": "STOP",
    "usage": {"inputTokens": 10, "outputTokens": 4, "totalTokens": 14},
    "latencyMs": 42.0,
    "route": {"reason": "DEFAULT_MODEL", "route": None, "considered": 1, "rejected": [],
              "chain": [], "fallbackCount": 0},
    "cost": None,
}


def turn(**overrides) -> TurnRequest:
    values = {
        "run_id": "run-1", "stage_index": 0, "turn": 1,
        "instructions": "system instructions", "data": "<task>do the thing</task>",
        "route": None, "model": None, "allowed_actions": (), "structured_output": False,
        "repair_of": None,
    }
    values.update(overrides)
    return TurnRequest(**values)


def client_for(handler, **kwargs) -> GatewayModelClient:
    return GatewayModelClient(base_url="http://api.invalid",
                              transport=httpx.MockTransport(handler), **kwargs)


async def test_a_turn_is_one_call_to_the_gateway_endpoint() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=ANSWER)

    outcome = await client_for(handler).complete(turn())

    assert len(seen) == 1
    assert seen[0].url.path == "/api/v1/gateway/infer"
    assert outcome.gateway_request_id == "req-1"
    assert outcome.provider == "devworld"
    assert outcome.total_tokens == 14
    assert outcome.cost is None and outcome.cost_known is False


async def test_the_two_channels_become_the_two_messages() -> None:
    """The task never reaches the system message. That property is what this client guarantees."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json=ANSWER)

    await client_for(handler).complete(turn())

    roles = [message["role"] for message in captured["messages"]]
    assert roles == ["system", "user"]
    assert captured["messages"][0]["content"] == "system instructions"
    assert "do the thing" in captured["messages"][1]["content"]
    assert "do the thing" not in captured["messages"][0]["content"]


async def test_the_request_carries_no_credential_and_no_address() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json=ANSWER)

    await client_for(handler).complete(turn(model="devworld:some-model"))

    body = json.dumps(captured).lower()
    for forbidden in ("api_key", "apikey", "authorization", "base_url", "baseurl", "bearer"):
        assert forbidden not in body


async def test_route_and_model_are_mutually_exclusive_on_the_wire() -> None:
    """The gateway's contract refuses both; the client sends the model when there is one."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json=ANSWER)

    await client_for(handler).complete(turn(route="balanced", model="devworld:x"))
    assert captured.get("model") == "devworld:x"
    assert captured.get("route") is None


async def test_a_refusal_keeps_the_gateway_classification() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(409, json={
            "code": "NO_CANDIDATE",
            "message": "no candidate can serve the request",
            "correlationId": "c-1",
            "details": {"reason": "capability", "considered": 3, "hidden": "not public"}})

    with pytest.raises(AgentRuntimeError) as raised:
        await client_for(handler).complete(turn())

    error = raised.value
    assert error.error_type is AgentRuntimeErrorType.GATEWAY_ERROR
    assert error.upstream_type == "NO_CANDIDATE"
    assert error.details["considered"] == 3
    assert "hidden" not in error.details


async def test_an_unreachable_gateway_is_a_classified_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(AgentRuntimeError) as raised:
        await client_for(handler).complete(turn())
    assert raised.value.upstream_type == "GATEWAY_UNREACHABLE"


async def test_a_malformed_answer_is_a_classified_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"<html>not json</html>")

    with pytest.raises(AgentRuntimeError) as raised:
        await client_for(handler).complete(turn())
    assert raised.value.upstream_type == "GATEWAY_MALFORMED_RESPONSE"


def test_runtime_never_declares_a_capability() -> None:
    """An unknown capability is not support, and a route is not a model."""
    catalog = [
        {"provider": "devworld", "model": "known",
         "capabilities": {"structured-output": {"state": "SUPPORTED",
                                                "provenance": "PROVIDER_METADATA"}}},
        {"provider": "devworld", "model": "silent",
         "capabilities": {"structured-output": {"state": "UNKNOWN", "provenance": "UNKNOWN"}}},
        {"provider": "devworld", "model": "refuses",
         "capabilities": {"structured-output": {"state": "UNSUPPORTED",
                                                "provenance": "PROVIDER_METADATA"}}},
    ]
    assert structured_output_supported(catalog, "devworld:known") is True
    assert structured_output_supported(catalog, "devworld:silent") is False
    assert structured_output_supported(catalog, "devworld:refuses") is False
    assert structured_output_supported(catalog, "devworld:absent") is False
    assert structured_output_supported(catalog, None) is False
    assert structured_output_supported(catalog, "bare-identifier") is False


async def test_structured_output_is_used_only_when_the_capability_is_known() -> None:
    requests: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/gateway/models":
            return httpx.Response(200, json={"total": 1, "models": [
                {"provider": "devworld", "model": "known",
                 "capabilities": {"structured-output": {"state": "SUPPORTED",
                                                        "provenance": "PROVIDER_METADATA"}}}]})
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=ANSWER)

    client = client_for(handler)
    await client.complete(turn(model="devworld:known", structured_output=True))
    assert requests[-1]["responseFormat"]["name"] == "iacode_agent_envelope"

    await client.complete(turn(model="devworld:unknown", structured_output=True))
    assert "responseFormat" not in requests[-1]

    await client.complete(turn(route="balanced", structured_output=True))
    assert "responseFormat" not in requests[-1], "a route is not a model"


async def test_a_catalog_that_cannot_be_read_means_no_structured_output() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/gateway/models":
            return httpx.Response(503, json={"code": "DEPENDENCY_UNAVAILABLE",
                                             "message": "catalog unavailable"})
        return httpx.Response(200, json=ANSWER)

    captured: list[dict] = []

    def capturing(request: httpx.Request) -> httpx.Response:
        response = handler(request)
        if request.url.path.endswith("/infer"):
            captured.append(json.loads(request.content))
        return response

    await client_for(capturing).complete(turn(model="devworld:known", structured_output=True))
    assert "responseFormat" not in captured[0]


def test_runtime_does_not_reimplement_gateway_resilience() -> None:
    """Retries, circuits, fallbacks and provider selection belong to Gate 1 and stay there."""
    import inspect

    from iacode_agent_runtime import engine, gateway_client

    for module in (gateway_client, engine):
        source = inspect.getsource(module).lower()
        for forbidden in ("circuitbreaker", "circuit_breaker", "retry_policy", "backoff",
                          "fallback_chain", "max_attempts"):
            assert forbidden not in source, f"{module.__name__} reimplements {forbidden}"
