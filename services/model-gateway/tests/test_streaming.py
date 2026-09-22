"""Streaming: the envelope, and the rule that two models can never write one answer."""

from __future__ import annotations

import pytest
from fixtures.doubles import (
    InMemoryCatalogStore,
    InMemoryModelCallStore,
    ScriptedProvider,
    build_gateway,
    descriptor,
    failure,
    provider_config,
    request as build_request,
    route_policy,
)
from iacode_model_gateway.config import RouteAlias
from iacode_model_gateway.contracts import (
    FinishReason,
    StreamEventType,
    ToolCallDelta,
    Usage,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.protocols.base import StreamChunk


def _text(*parts: str) -> list[StreamChunk]:
    return [StreamChunk(text=part) for part in parts]


def _finished(*parts: str, usage: Usage | None = None) -> list[StreamChunk]:
    chunks = _text(*parts)
    if usage is not None:
        chunks.append(StreamChunk(usage=usage))
    chunks.append(StreamChunk(finish_reason=FinishReason.STOP, done=True))
    return chunks


async def _collect(gateway, request=None):
    return [event async for event in gateway.stream(request or build_request(stream=True))]


class StreamEnvelopeTests:
    """Every event kind, in the order a consumer can rely on."""

    async def test_a_normal_stream_starts_delivers_and_ends(self) -> None:
        provider = ScriptedProvider("alpha", streams=[_finished(
            "he", "llo", usage=Usage(input_tokens=3, output_tokens=2))])
        gateway = build_gateway(factory=lambda config: provider)

        events = await _collect(gateway)

        kinds = [str(event.type) for event in events]
        assert kinds[0] == "start"
        assert kinds[-1] == "end"
        assert "".join(event.text or "" for event in events) == "hello"
        assert events[-1].finish_reason is FinishReason.STOP
        assert events[-1].usage.output_tokens == 2

    async def test_sequence_numbers_are_dense_and_ordered(self) -> None:
        provider = ScriptedProvider("alpha", streams=[_finished("a", "b")])
        gateway = build_gateway(factory=lambda config: provider)

        events = await _collect(gateway)

        assert [event.sequence for event in events] == list(range(len(events)))

    async def test_the_start_event_names_the_model_and_the_route(self) -> None:
        provider = ScriptedProvider("alpha", streams=[_finished("a")])
        gateway = build_gateway(factory=lambda config: provider)

        first = (await _collect(gateway))[0]

        assert first.type is StreamEventType.START
        assert first.ref.qualified == "alpha:model-one"
        assert first.route is not None

    async def test_an_empty_stream_still_ends(self) -> None:
        """A model that produced nothing is an answer, not a hang."""
        provider = ScriptedProvider(
            "alpha", streams=[[StreamChunk(finish_reason=FinishReason.STOP, done=True)]])
        gateway = build_gateway(factory=lambda config: provider)

        events = await _collect(gateway)

        assert [str(event.type) for event in events] == ["start", "end"]
        assert not any(event.text for event in events)

    async def test_usage_arrives_before_the_end(self) -> None:
        provider = ScriptedProvider("alpha", streams=[_finished(
            "a", usage=Usage(input_tokens=1, output_tokens=1))])
        gateway = build_gateway(factory=lambda config: provider)

        events = await _collect(gateway)
        kinds = [str(event.type) for event in events]

        assert kinds.index("usage") < kinds.index("end")

    async def test_a_tool_call_delta_is_its_own_event(self) -> None:
        provider = ScriptedProvider("alpha", streams=[[
            StreamChunk(tool_call_delta=ToolCallDelta(index=0, id="c1", name="read",
                                                      arguments_fragment='{"p"')),
            StreamChunk(finish_reason=FinishReason.TOOL_CALLS, done=True),
        ]])
        gateway = build_gateway(factory=lambda config: provider)

        events = await _collect(gateway)
        deltas = [event for event in events if event.type is StreamEventType.TOOL_CALL_DELTA]

        assert deltas[0].tool_call_delta.name == "read"
        assert deltas[0].tool_call_delta.arguments_fragment == '{"p"'


async def test_streaming_uses_the_same_router() -> None:
    """One routing decision, one policy, one set of candidates — not a parallel architecture."""
    store = InMemoryCatalogStore()
    store.seed(descriptor(model_id="model-one", active=False))
    provider = ScriptedProvider("alpha", streams=[_finished("a")])
    gateway = build_gateway(catalog=store, factory=lambda config: provider)

    with pytest.raises(GatewayError) as error:
        await _collect(gateway)

    assert error.value.error_type is GatewayErrorType.NO_CANDIDATE
    assert provider.calls == []


async def test_provider_failure_before_the_first_delta_falls_back() -> None:
    store = InMemoryCatalogStore()
    store.seed(descriptor(model_id="first"), descriptor(model_id="second"))
    first = ScriptedProvider("alpha", streams=[[failure(GatewayErrorType.PROVIDER_UNAVAILABLE)]])
    second = ScriptedProvider("beta", streams=[_finished("recovered")])
    providers = {"alpha": provider_config("alpha"), "beta": provider_config("beta")}
    store.seed(descriptor("beta", "second"))
    gateway = build_gateway(
        providers=providers, catalog=store,
        factory=lambda config: first if config.provider_id == "alpha" else second,
        policy=route_policy(RouteAlias(alias="pair",
                                       candidates=("alpha:first", "beta:second"))),
        max_attempts=1)

    events = await _collect(gateway, build_request(stream=True, route="pair"))

    assert "".join(event.text or "" for event in events) == "recovered"
    assert events[0].ref.qualified == "beta:second"


async def test_no_fallback_after_the_first_delivered_content() -> None:
    """The consumer holds one model's output; a second model may not continue it."""
    store = InMemoryCatalogStore()
    store.seed(descriptor(model_id="first"))
    store.seed(descriptor("beta", "second"))
    first = ScriptedProvider("alpha", streams=[
        _text("partial") + [failure(GatewayErrorType.PROVIDER_UNAVAILABLE)]])
    second = ScriptedProvider("beta", streams=[_finished("should not be reached")])
    gateway = build_gateway(
        providers={"alpha": provider_config("alpha"), "beta": provider_config("beta")},
        catalog=store,
        factory=lambda config: first if config.provider_id == "alpha" else second,
        policy=route_policy(RouteAlias(alias="pair",
                                       candidates=("alpha:first", "beta:second"))),
        max_attempts=1)

    events = await _collect(gateway, build_request(stream=True, route="pair"))

    assert "".join(event.text or "" for event in events) == "partial"
    assert events[-1].type is StreamEventType.ERROR
    assert second.calls == []


async def test_no_two_models_are_concatenated_in_one_stream() -> None:
    """The property stated directly: every delivered token came from one model."""
    store = InMemoryCatalogStore()
    store.seed(descriptor(model_id="first"))
    store.seed(descriptor("beta", "second"))
    first = ScriptedProvider("alpha", streams=[
        _text("alpha-one ", "alpha-two ") + [failure(GatewayErrorType.TRANSIENT_PROVIDER_ERROR)]])
    second = ScriptedProvider("beta", streams=[_finished("beta-one")])
    gateway = build_gateway(
        providers={"alpha": provider_config("alpha"), "beta": provider_config("beta")},
        catalog=store,
        factory=lambda config: first if config.provider_id == "alpha" else second,
        policy=route_policy(RouteAlias(alias="pair",
                                       candidates=("alpha:first", "beta:second"))),
        max_attempts=1)

    events = await _collect(gateway, build_request(stream=True, route="pair"))
    text = "".join(event.text or "" for event in events)
    models = {event.ref.qualified for event in events if event.ref is not None}

    assert "beta-one" not in text
    assert models == {"alpha:first"}


async def test_failure_after_content_ends_with_an_error_event() -> None:
    provider = ScriptedProvider("alpha", streams=[
        _text("some") + [failure(GatewayErrorType.TRANSIENT_PROVIDER_ERROR)]])
    gateway = build_gateway(factory=lambda config: provider, max_attempts=1)

    events = await _collect(gateway)

    assert events[-1].type is StreamEventType.ERROR
    assert events[-1].finish_reason is FinishReason.ERROR
    assert events[-1].error["errorType"] == "TRANSIENT_PROVIDER_ERROR"
    assert "already been delivered" in events[-1].error["details"]["fallbackStopped"]


async def test_a_retry_is_allowed_only_before_anything_was_delivered() -> None:
    store = InMemoryCatalogStore()
    store.seed(descriptor())
    retried = ScriptedProvider("alpha", streams=[
        [failure(GatewayErrorType.PROVIDER_TIMEOUT)],
        _finished("recovered")])
    gateway = build_gateway(catalog=store, factory=lambda config: retried, max_attempts=2)

    events = await _collect(gateway)
    assert "".join(event.text or "" for event in events) == "recovered"

    after_output = ScriptedProvider("alpha", streams=[
        _text("partial") + [failure(GatewayErrorType.PROVIDER_TIMEOUT)],
        _finished("never")])
    second = build_gateway(catalog=store, factory=lambda config: after_output, max_attempts=2)

    events = await _collect(second)
    assert "".join(event.text or "" for event in events) == "partial"
    assert len(after_output.streams) == 1  # the second script was never consumed


async def test_consumer_cancellation_stops_the_upstream_call() -> None:
    """A consumer that stops reading must stop the provider generating."""
    provider = ScriptedProvider("alpha", streams=[_finished("a", "b", "c", "d")])
    gateway = build_gateway(factory=lambda config: provider)

    generator = gateway.stream(build_request(stream=True))
    seen = []
    async for event in generator:
        seen.append(event)
        if len(seen) >= 2:
            break
    await generator.aclose()

    assert provider.cancelled
    assert len(seen) == 2


async def test_a_truncated_stream_is_recorded_as_a_failure() -> None:
    store = InMemoryCatalogStore()
    store.seed(descriptor())
    calls = InMemoryModelCallStore()
    provider = ScriptedProvider("alpha", streams=[
        _text("a") + [failure(GatewayErrorType.TRANSIENT_PROVIDER_ERROR)]])
    gateway = build_gateway(catalog=store, calls=calls, factory=lambda config: provider,
                            max_attempts=1)

    await _collect(gateway)

    assert calls.calls[-1].status == "FAILED"
    assert calls.calls[-1].error_type == "TRANSIENT_PROVIDER_ERROR"
