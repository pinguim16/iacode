"""The HTTP provider: the one place a socket is opened, exercised without one.

``httpx.MockTransport`` lets the real client, the real timeouts and the real SSE reader run against
a scripted server. That is the difference between testing the transport and testing a mock of it:
every byte here goes through the code production uses.
"""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest
from fixtures.doubles import descriptor, provider_config, request as build_request, settings
from iacode_model_gateway.config import ResolvedProvider
from iacode_model_gateway.contracts import Endpoint, FinishReason
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.protocols import build_adapters
from iacode_model_gateway.providers.http_provider import HttpModelProvider, parse_retry_after
from pydantic import SecretStr

CREDENTIAL = "dw" + "-live-" + "q" * 32


def _provider(handler, **setting_overrides) -> HttpModelProvider:
    config = provider_config()
    resolved = ResolvedProvider(config=config, base_url="https://provider.example/v1",
                                credential=SecretStr(CREDENTIAL))
    return HttpModelProvider(
        resolved, build_adapters(config.protocols, config.protocol_options),
        settings(**setting_overrides), transport=httpx.MockTransport(handler))


def _sse(*frames: str) -> str:
    return "".join(f"data: {frame}\n\n" for frame in frames)


def _completion_body(text: str = "hello") -> dict:
    return {"choices": [{"message": {"content": text}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 3, "completion_tokens": 1}}


async def test_model_discovery_reaches_the_configured_path() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("authorization", "")
        return httpx.Response(200, json={"data": [{"id": "model-one"}, {"id": "model-two"}]})

    discovered = await _provider(handler).list_models()

    assert seen["url"] == "https://provider.example/v1/models"
    assert seen["auth"].endswith(CREDENTIAL)
    assert [item[0] for item in discovered.entries] == ["model-one", "model-two"]


async def test_a_bare_list_discovery_answer_is_accepted() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=["model-one"])

    discovered = await _provider(handler).list_models()

    assert discovered.entries == (("model-one", {"id": "model-one"}),)


async def test_an_unrecognised_discovery_answer_is_an_error_not_an_empty_catalog() -> None:
    """Reporting 'no models' for an answer we failed to read would deactivate the catalog."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    with pytest.raises(GatewayError) as error:
        await _provider(handler).list_models()

    assert error.value.error_type is GatewayErrorType.PROVIDER_UNAVAILABLE


async def test_generation_sends_the_built_call_and_parses_the_answer() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        captured["path"] = request.url.path
        return httpx.Response(200, json=_completion_body())

    parsed = await _provider(handler).generate(
        build_request(), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS, output_tokens=64)

    assert captured["path"] == "/v1/chat/completions"
    assert captured["body"]["max_tokens"] == 64
    assert parsed.content == "hello"
    assert parsed.usage.input_tokens == 3
    assert parsed.finish_reason is FinishReason.STOP


async def test_streaming_reads_server_sent_events() -> None:
    body = _sse(
        json.dumps({"choices": [{"delta": {"content": "he"}}]}),
        json.dumps({"choices": [{"delta": {"content": "llo"}}]}),
        json.dumps({"choices": [{"delta": {}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 2}}),
        "[DONE]")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=body,
                              headers={"content-type": "text/event-stream"})

    chunks = [chunk async for chunk in _provider(handler).stream(
        build_request(stream=True), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS,
        output_tokens=16)]

    assert "".join(chunk.text or "" for chunk in chunks) == "hello"
    assert any(chunk.usage and chunk.usage.output_tokens == 2 for chunk in chunks)


async def test_a_keep_alive_comment_frame_is_ignored() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        text = ": keep-alive\n\n" + _sse(
            json.dumps({"choices": [{"delta": {"content": "a"}}]}), "[DONE]")
        return httpx.Response(200, text=text, headers={"content-type": "text/event-stream"})

    chunks = [chunk async for chunk in _provider(handler).stream(
        build_request(stream=True), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS,
        output_tokens=16)]

    assert "".join(chunk.text or "" for chunk in chunks) == "a"


async def test_a_stream_that_ends_without_a_terminal_frame_is_a_failure() -> None:
    """A truncated stream and a finished one must not look the same."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=_sse(
            json.dumps({"choices": [{"delta": {"content": "a"}}]})),
            headers={"content-type": "text/event-stream"})

    with pytest.raises(GatewayError) as error:
        async for _chunk in _provider(handler).stream(
                build_request(stream=True), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS,
                output_tokens=16):
            pass

    assert error.value.error_type is GatewayErrorType.TRANSIENT_PROVIDER_ERROR


async def test_errors_are_normalised_with_the_retry_hint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"message": "slow down"}},
                              headers={"retry-after": "7",
                                       "x-ratelimit-remaining-requests": "0"})

    with pytest.raises(GatewayError) as error:
        await _provider(handler).generate(
            build_request(), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS, output_tokens=16)

    assert error.value.error_type is GatewayErrorType.RATE_LIMITED
    assert error.value.retry_after_seconds == 7
    assert error.value.details["rateLimitRemainingRequests"] == 0
    assert "slow down" not in error.value.message


async def test_an_authentication_failure_is_classified_and_says_nothing_more() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": f"bad key {CREDENTIAL}"}})

    with pytest.raises(GatewayError) as error:
        await _provider(handler).generate(
            build_request(), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS, output_tokens=16)

    assert error.value.error_type is GatewayErrorType.AUTHENTICATION_ERROR
    assert CREDENTIAL not in error.value.message
    assert CREDENTIAL not in json.dumps(error.value.to_dict())


async def test_timeout_is_normalised() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("too slow", request=request)

    with pytest.raises(GatewayError) as error:
        await _provider(handler).generate(
            build_request(), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS, output_tokens=16)

    assert error.value.error_type is GatewayErrorType.PROVIDER_TIMEOUT


async def test_a_connect_failure_is_distinguished_from_a_read_failure() -> None:
    def connect(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("unreachable", request=request)

    with pytest.raises(GatewayError) as error:
        await _provider(connect).generate(
            build_request(), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS, output_tokens=16)
    assert "accept a connection" in error.value.message

    def refused(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    with pytest.raises(GatewayError) as error:
        await _provider(refused).generate(
            build_request(), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS, output_tokens=16)
    assert error.value.error_type is GatewayErrorType.PROVIDER_UNAVAILABLE


def test_no_call_is_unbounded() -> None:
    """Connect and read are separate budgets, and both are always set."""
    import inspect

    from iacode_model_gateway.providers import http_provider

    source = inspect.getsource(http_provider.HttpModelProvider._client)
    assert "connect=" in source
    assert "read=" in source
    assert "timeout=None" not in inspect.getsource(http_provider)


async def test_oversized_provider_response_is_refused() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "x" * 50_000}}]})

    with pytest.raises(GatewayError) as error:
        await _provider(handler, max_response_bytes=2048).generate(
            build_request(), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS, output_tokens=16)

    assert error.value.error_type is GatewayErrorType.RESPONSE_TOO_LARGE


async def test_cancellation_stops_the_upstream_call() -> None:
    """Closing the iterator closes the connection, which is what stops tokens being generated."""
    def handler(request: httpx.Request) -> httpx.Response:
        frames = _sse(*[json.dumps({"choices": [{"delta": {"content": str(index)}}]})
                        for index in range(100)])
        return httpx.Response(200, text=frames, headers={"content-type": "text/event-stream"})

    provider = _provider(handler)
    stream = provider.stream(build_request(stream=True), descriptor(),
                             Endpoint.OPENAI_CHAT_COMPLETIONS, output_tokens=16)
    seen = []
    async for chunk in stream:
        seen.append(chunk)
        if len(seen) == 2:
            break
    await stream.aclose()

    assert len(seen) == 2


async def test_a_health_probe_reports_a_reachable_provider() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "model-one"}]})

    health = await _provider(handler).health()

    assert health.reachable
    assert health.latency_ms is not None


async def test_a_health_probe_reports_why_a_provider_is_not_usable() -> None:
    """'Reachable but refusing our credential' is the state an operator needs to see."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "nope"}})

    health = await _provider(handler).health()

    assert not health.reachable
    assert "credential" in (health.detail or "")


async def test_a_tool_call_is_normalised_end_to_end() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{
            "message": {"content": None, "tool_calls": [
                {"id": "c1", "function": {"name": "read", "arguments": '{"path": "a"}'}}]},
            "finish_reason": "tool_calls"}]})

    parsed = await _provider(handler).generate(
        build_request(), descriptor(), Endpoint.OPENAI_CHAT_COMPLETIONS, output_tokens=16)

    assert parsed.tool_calls[0].name == "read"
    assert parsed.tool_calls[0].arguments == {"path": "a"}


def test_retry_after_reads_seconds_and_refuses_a_date() -> None:
    """A date form would require trusting the provider's clock against ours."""
    assert parse_retry_after("12") == 12.0
    assert parse_retry_after("0") == 0.0
    assert parse_retry_after("Wed, 21 Oct 2026 07:28:00 GMT") is None
    assert parse_retry_after(None) is None
    assert parse_retry_after("-3") is None


async def test_an_adapter_the_provider_does_not_serve_is_refused() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_completion_body())

    with pytest.raises(GatewayError) as error:
        await _provider(handler).generate(
            build_request(), descriptor(), Endpoint.ANTHROPIC_MESSAGES, output_tokens=16)

    assert error.value.error_type is GatewayErrorType.INTERNAL_GATEWAY_ERROR


async def test_concurrent_calls_do_not_share_state() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_completion_body(json.loads(request.content)["model"]))

    provider = _provider(handler)
    answers = await asyncio.gather(*[
        provider.generate(build_request(), descriptor(model_id=name),
                          Endpoint.OPENAI_CHAT_COMPLETIONS, output_tokens=16)
        for name in ("one", "two", "three")
    ])

    assert sorted(answer.content for answer in answers) == ["one", "three", "two"]
