"""Structured output: refused where it cannot be honoured, configured where it can."""

from __future__ import annotations

import pytest
from fixtures.doubles import (
    InMemoryCatalogStore,
    ScriptedProvider,
    build_gateway,
    completion,
    descriptor,
    provider_config,
    request as build_request,
    route_policy,
    settings as build_settings,
)
from iacode_model_gateway.contracts import (
    Capability,
    CapabilityState,
    ResponseFormat,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.protocols.anthropic_messages import AnthropicMessagesAdapter
from iacode_model_gateway.protocols.openai_chat import OpenAiChatAdapter
from iacode_model_gateway.protocols.openai_responses import OpenAiResponsesAdapter
from iacode_model_gateway.routing.router import Router

SCHEMA = {"type": "object", "properties": {"answer": {"type": "string"}},
          "required": ["answer"]}


def _format() -> ResponseFormat:
    return ResponseFormat(name="answer", json_schema=SCHEMA)


def _plan(models):
    """Route a structured-output request over the given catalog, or raise the refusal."""
    return Router(route_policy(), build_settings()).plan(
        build_request(response_format=_format()), models,
        {"alpha": provider_config()}, output_tokens=16)


def test_structured_output_requires_a_capable_candidate() -> None:
    """A model that does not support it is refused rather than sent the request and told to cope."""
    with pytest.raises(GatewayError) as error:
        _plan([descriptor(capabilities={
            Capability.STRUCTURED_OUTPUT: CapabilityState.UNSUPPORTED})])

    assert error.value.error_type is GatewayErrorType.NO_CANDIDATE
    assert "structured-output" in error.value.message


def test_an_unknown_structured_output_capability_is_refused_by_default() -> None:
    """Never having declared it is not the same as supporting it."""
    with pytest.raises(GatewayError) as error:
        _plan([descriptor(capabilities={})])

    assert "never declared" in error.value.message


def test_a_capable_candidate_is_selected() -> None:
    plan = _plan([descriptor(capabilities={
        Capability.STRUCTURED_OUTPUT: CapabilityState.SUPPORTED})])

    assert plan.candidates[0].ref.qualified == "alpha:model-one"


async def test_a_capable_candidate_receives_the_configuration() -> None:
    store = InMemoryCatalogStore()
    store.seed(descriptor(
        capabilities={Capability.STRUCTURED_OUTPUT: CapabilityState.SUPPORTED}))
    provider = ScriptedProvider("alpha", completions=[completion('{"answer": "yes"}')])
    gateway = build_gateway(catalog=store, factory=lambda config: provider,
                            policy=route_policy())

    answer = await gateway.infer(build_request(response_format=_format()))

    assert answer.content == '{"answer": "yes"}'
    assert provider.calls[0]["kind"] == "generate"


def test_the_chat_completions_adapter_sends_a_json_schema() -> None:
    call = OpenAiChatAdapter().build_generate(
        build_request(response_format=_format()), descriptor(), stream=False,
        path="/chat/completions", max_output_tokens=16)

    body = call.json_body["response_format"]
    assert body["type"] == "json_schema"
    assert body["json_schema"]["schema"] == SCHEMA
    assert body["json_schema"]["strict"] is True


def test_the_responses_adapter_sends_a_text_format() -> None:
    call = OpenAiResponsesAdapter().build_generate(
        build_request(response_format=_format()), descriptor(), stream=False,
        path="/responses", max_output_tokens=16)

    assert call.json_body["text"]["format"]["schema"] == SCHEMA


def test_the_messages_adapter_forces_a_tool_rather_than_dropping_the_requirement() -> None:
    """This protocol has no schema field; silently ignoring the request would be the worst option."""
    call = AnthropicMessagesAdapter().build_generate(
        build_request(response_format=_format()), descriptor(), stream=False,
        path="/v1/messages", max_output_tokens=16)

    assert call.json_body["tool_choice"]["name"] == "answer"
    assert call.json_body["tools"][-1]["input_schema"] == SCHEMA


def test_a_schema_is_mandatory() -> None:
    """'Give me JSON' is a formatting preference no provider guarantees."""
    with pytest.raises(ValueError):
        ResponseFormat(name="answer", json_schema={})
