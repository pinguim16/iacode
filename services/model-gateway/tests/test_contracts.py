"""The gateway contract: what it validates, what it refuses, and what it never carries."""

from __future__ import annotations

import pytest
from fixtures.doubles import descriptor, request as build_request
from iacode_model_gateway.contracts import (
    CONTRACT_VERSION,
    Capability,
    Endpoint,
    FinishReason,
    GatewayMessage,
    GatewayRequest,
    GatewayResponse,
    MessageRole,
    ModelRef,
    ResponseFormat,
    RouteDecision,
    RouteReason,
    StreamEvent,
    StreamEventType,
    ToolCall,
    ToolCallDelta,
    ToolDefinition,
    Usage,
)
from iacode_model_gateway.protocols.base import build_tool_call
from pydantic import ValidationError


def test_contract_version_is_declared() -> None:
    """A consumer can detect an incompatible change instead of discovering it by crashing."""
    assert CONTRACT_VERSION
    answer = GatewayResponse(
        request_id="req", ref=ModelRef(provider_id="alpha", model_id="model-one"),
        endpoint=Endpoint.OPENAI_CHAT_COMPLETIONS, latency_ms=1.0,
        route=RouteDecision(reason=RouteReason.DEFAULT_MODEL))

    assert answer.contract_version == CONTRACT_VERSION


def test_request_is_validated_when_it_is_built() -> None:
    """Every refusal happens at construction, not at the provider."""
    with pytest.raises(ValidationError):
        GatewayRequest(request_id="req", messages=())

    with pytest.raises(ValidationError):
        build_request(route="fast", model="alpha:model-one")

    with pytest.raises(ValidationError):
        build_request(model="model-one")  # unqualified: two providers could expose it

    with pytest.raises(ValidationError):
        build_request(tools=(ToolDefinition(name="same"), ToolDefinition(name="same")))

    with pytest.raises(ValidationError):
        build_request(temperature=9.0)


def test_message_roles_are_provider_independent() -> None:
    """The five roles exist in the contract whether or not a given provider has them."""
    assert {str(role) for role in MessageRole} == {
        "system", "developer", "user", "assistant", "tool"}

    with pytest.raises(ValidationError):
        GatewayMessage(role=MessageRole.TOOL, content="result")  # no call answered

    with pytest.raises(ValidationError):
        GatewayMessage(role=MessageRole.USER, content="",
                       tool_calls=(ToolCall(id="1", name="t"),))

    answered = GatewayMessage(role=MessageRole.TOOL, content="42", tool_call_id="call-1")
    assert answered.tool_call_id == "call-1"


def test_response_never_exposes_the_raw_provider_payload() -> None:
    """No field of the response can carry a provider's own JSON."""
    answer = GatewayResponse(
        request_id="req", ref=ModelRef(provider_id="alpha", model_id="model-one"),
        endpoint=Endpoint.OPENAI_CHAT_COMPLETIONS, latency_ms=1.0,
        route=RouteDecision(reason=RouteReason.DEFAULT_MODEL))
    fields = set(type(answer).model_fields)

    assert not fields & {"raw", "raw_response", "provider_payload", "body", "original"}
    with pytest.raises(ValidationError):
        GatewayResponse(
            request_id="req", ref=ModelRef(provider_id="alpha", model_id="model-one"),
            endpoint=Endpoint.OPENAI_CHAT_COMPLETIONS, latency_ms=-1.0,
            route=RouteDecision(reason=RouteReason.DEFAULT_MODEL))


def test_gateway_normalises_a_tool_call_without_executing_it() -> None:
    """A tool call is a record of a request, not an invocation."""
    call = build_tool_call("call-1", "read_file", '{"path": "README.md"}')

    assert call.arguments == {"path": "README.md"}
    assert call.arguments_valid
    # Nothing in the contract can run anything: there is no callable and no handler field.
    assert not any(callable(getattr(call, name, None)) and not name.startswith(("model_", "_"))
                   for name in type(call).model_fields)


def test_invalid_tool_arguments_produce_a_normalised_error() -> None:
    """Broken JSON from a model is an ordinary event, recorded rather than thrown away."""
    broken = build_tool_call("call-2", "read_file", '{"path": "READ')

    assert not broken.arguments_valid
    assert "not valid JSON" in (broken.invalid_reason or "")
    assert broken.arguments == {}

    not_an_object = build_tool_call("call-3", "read_file", "[1, 2, 3]")
    assert not not_an_object.arguments_valid
    assert "must be a JSON object" in (not_an_object.invalid_reason or "")

    with pytest.raises(ValidationError):
        ToolCall(id="x", name="y", arguments_valid=False)  # a refusal must say why


def test_implied_capabilities_are_derived_from_the_request() -> None:
    """A caller that supplies tools needs a model that accepts them, declared or not."""
    plain = build_request()
    assert plain.implied_capabilities == ()

    rich = build_request(
        stream=True,
        tools=(ToolDefinition(name="read"),),
        response_format=ResponseFormat(name="answer", json_schema={"type": "object"}))

    assert set(rich.implied_capabilities) == {
        Capability.STREAMING, Capability.TOOLS, Capability.STRUCTURED_OUTPUT}


def test_usage_derives_a_total_only_when_both_halves_exist() -> None:
    """A total derived from one half is a different number wearing the same name."""
    assert Usage(input_tokens=10, output_tokens=5).total_tokens == 15
    assert Usage(input_tokens=10).total_tokens is None
    assert Usage().empty
    assert not Usage(reasoning_tokens=3).empty


def test_structured_output_requires_a_schema() -> None:
    with pytest.raises(ValidationError):
        ResponseFormat(name="answer", json_schema={})
    with pytest.raises(ValidationError):
        ResponseFormat(name="answer", json_schema={"type": "array"})


def test_model_reference_identity_is_the_pair() -> None:
    """Two providers exposing the same identifier are two models."""
    first = ModelRef(provider_id="alpha", model_id="shared")
    second = ModelRef(provider_id="beta", model_id="shared")

    assert first.qualified != second.qualified
    assert ModelRef.parse("alpha:shared") == first
    with pytest.raises(ValueError):
        ModelRef.parse("shared")


def test_capability_is_unknown_until_something_says_otherwise() -> None:
    model = descriptor(capabilities={})

    assert str(model.capability(Capability.TOOLS)) == "UNKNOWN"
    assert str(model.provenance(Capability.TOOLS)) == "UNKNOWN"


def test_stream_event_renders_one_server_sent_event_frame() -> None:
    event = StreamEvent(type=StreamEventType.TEXT_DELTA, request_id="req", sequence=3,
                        text="hello")
    frame = event.to_sse()

    assert frame.startswith("event: text_delta\ndata: ")
    assert frame.endswith("\n\n")
    assert '"text":"hello"' in frame.replace(", ", ",").replace('": ', '":')


def test_a_tool_call_fragment_is_not_a_tool_call() -> None:
    """A half-arrived call cannot be emitted as though it were complete."""
    fragment = ToolCallDelta(index=0, id="call-1", name="read", arguments_fragment='{"pa')

    assert not isinstance(fragment, ToolCall)
    assert fragment.arguments_fragment == '{"pa'


def test_finish_reasons_are_our_vocabulary() -> None:
    assert {str(item) for item in FinishReason} >= {
        "STOP", "LENGTH", "TOOL_CALLS", "CONTENT_FILTER", "ERROR", "CANCELLED", "UNKNOWN"}
