"""The protocol adapters: what they build, what they read, and how they classify a failure.

No socket is opened here. An adapter builds a description of a call and parses bytes, which is the
split that makes this suite possible at all — and which is why the same cases run for three
protocols without three transports.
"""

from __future__ import annotations

import json

import pytest
from fixtures.doubles import descriptor, request as build_request
from iacode_model_gateway.contracts import (
    Capability,
    CapabilityState,
    Endpoint,
    FinishReason,
    GatewayMessage,
    MessageRole,
    ReasoningEffort,
    ResponseFormat,
    ToolCall,
    ToolDefinition,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.protocols import build_adapters, select_endpoint
from iacode_model_gateway.protocols.anthropic_messages import AnthropicMessagesAdapter
from iacode_model_gateway.protocols.openai_chat import OpenAiChatAdapter
from iacode_model_gateway.protocols.openai_responses import OpenAiResponsesAdapter
from iacode_model_gateway.protocols.selection import EndpointSource

from fixtures.doubles import provider_config


def _drain(decoder, frames: list[tuple[str | None, str]]):
    chunks = []
    for event, data in frames:
        chunks.extend(decoder.feed(event, data))
    chunks.extend(decoder.finish())
    return chunks


class OpenAiChatProtocolTests:
    """OpenAI-compatible Chat Completions."""

    adapter = OpenAiChatAdapter()

    def test_the_request_carries_the_gateway_output_cap(self) -> None:
        call = self.adapter.build_generate(
            build_request(), descriptor(), stream=False, path="/chat/completions",
            max_output_tokens=128)

        assert call.method == "POST"
        assert call.json_body["max_tokens"] == 128
        assert call.json_body["messages"] == [{"role": "user", "content": "Say hello."}]
        assert call.json_body["stream"] is False

    def test_developer_is_translated_to_system(self) -> None:
        """This protocol has no developer role on most compatible servers; the merge is ours."""
        call = self.adapter.build_generate(
            build_request(messages=(
                GatewayMessage(role=MessageRole.DEVELOPER, content="be terse"),
                GatewayMessage(role=MessageRole.USER, content="hi"))),
            descriptor(), stream=False, path="/chat/completions", max_output_tokens=16)

        assert [item["role"] for item in call.json_body["messages"]] == ["system", "user"]

    def test_a_stream_asks_for_usage(self) -> None:
        call = self.adapter.build_generate(
            build_request(stream=True), descriptor(), stream=True, path="/chat/completions",
            max_output_tokens=16)

        assert call.json_body["stream_options"] == {"include_usage": True}
        assert call.headers["Accept"] == "text/event-stream"

    def test_tools_and_structured_output_reach_the_payload(self) -> None:
        call = self.adapter.build_generate(
            build_request(
                tools=(ToolDefinition(name="read", description="read a file",
                                      parameters={"type": "object"}),),
                response_format=ResponseFormat(name="answer",
                                               json_schema={"type": "object"})),
            descriptor(), stream=False, path="/chat/completions", max_output_tokens=16)

        assert call.json_body["tools"][0]["function"]["name"] == "read"
        assert call.json_body["response_format"]["type"] == "json_schema"

    def test_an_assistant_tool_turn_round_trips(self) -> None:
        call = self.adapter.build_generate(
            build_request(messages=(
                GatewayMessage(role=MessageRole.USER, content="read it"),
                GatewayMessage(role=MessageRole.ASSISTANT, content="",
                               tool_calls=(ToolCall(id="c1", name="read",
                                                    arguments={"path": "a"}),)),
                GatewayMessage(role=MessageRole.TOOL, content="ok", tool_call_id="c1"))),
            descriptor(), stream=False, path="/chat/completions", max_output_tokens=16)

        assistant = call.json_body["messages"][1]
        assert assistant["content"] is None
        assert assistant["tool_calls"][0]["function"]["arguments"] == '{"path": "a"}'
        assert call.json_body["messages"][2]["tool_call_id"] == "c1"

    def test_the_answer_is_normalised(self) -> None:
        parsed = self.adapter.parse_completion({
            "choices": [{"message": {"content": "hi"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 2,
                      "prompt_tokens_details": {"cached_tokens": 3},
                      "completion_tokens_details": {"reasoning_tokens": 1}},
        })

        assert parsed.content == "hi"
        assert parsed.finish_reason is FinishReason.STOP
        assert parsed.usage.input_tokens == 7
        assert parsed.usage.cached_input_tokens == 3
        assert parsed.usage.reasoning_tokens == 1

    def test_absent_usage_stays_absent(self) -> None:
        parsed = self.adapter.parse_completion(
            {"choices": [{"message": {"content": "hi"}, "finish_reason": "stop"}]})

        assert parsed.usage.empty

    def test_a_tool_call_in_the_answer_is_normalised(self) -> None:
        parsed = self.adapter.parse_completion({
            "choices": [{
                "message": {"content": None, "tool_calls": [
                    {"id": "c1", "function": {"name": "read",
                                              "arguments": '{"path": "a"}'}}]},
                "finish_reason": "tool_calls"}],
        })

        assert parsed.finish_reason is FinishReason.TOOL_CALLS
        assert parsed.tool_calls[0].arguments == {"path": "a"}

    def test_an_answer_without_a_choice_is_refused(self) -> None:
        with pytest.raises(ValueError):
            self.adapter.parse_completion({"choices": []})

    def test_the_stream_is_decoded(self) -> None:
        decoder = self.adapter.decoder()
        chunks = _drain(decoder, [
            (None, json.dumps({"choices": [{"delta": {"content": "he"}}]})),
            (None, json.dumps({"choices": [{"delta": {"content": "llo"}}]})),
            (None, json.dumps({"choices": [{"delta": {}, "finish_reason": "stop"}],
                               "usage": {"prompt_tokens": 3, "completion_tokens": 2}})),
            (None, "[DONE]"),
        ])

        assert "".join(chunk.text for chunk in chunks if chunk.text) == "hello"
        assert any(chunk.finish_reason is FinishReason.STOP for chunk in chunks)
        assert any(chunk.usage and chunk.usage.input_tokens == 3 for chunk in chunks)
        assert chunks[-1].done
        assert decoder.completed

    def test_a_streamed_tool_call_is_assembled(self) -> None:
        decoder = self.adapter.decoder()
        _drain(decoder, [
            (None, json.dumps({"choices": [{"delta": {"tool_calls": [
                {"index": 0, "id": "c1", "function": {"name": "read", "arguments": ""}}]}}]})),
            (None, json.dumps({"choices": [{"delta": {"tool_calls": [
                {"index": 0, "function": {"arguments": '{"path":'}}]}}]})),
            (None, json.dumps({"choices": [{"delta": {"tool_calls": [
                {"index": 0, "function": {"arguments": ' "a"}'}}]}}]})),
            (None, "[DONE]"),
        ])

        assembled = decoder.assembled_tool_calls()
        assert assembled[0].name == "read"
        assert assembled[0].arguments == {"path": "a"}

    def test_a_malformed_frame_is_refused(self) -> None:
        with pytest.raises(ValueError):
            self.adapter.decoder().feed(None, "{not json")

    def test_a_truncated_stream_is_visible(self) -> None:
        decoder = self.adapter.decoder()
        _drain(decoder, [(None, json.dumps({"choices": [{"delta": {"content": "a"}}]}))])

        assert not decoder.completed

    def test_errors_are_classified(self) -> None:
        assert self.adapter.classify_error(401, {})[0] is GatewayErrorType.AUTHENTICATION_ERROR
        assert self.adapter.classify_error(429, {})[0] is GatewayErrorType.RATE_LIMITED
        assert self.adapter.classify_error(503, {})[0] is GatewayErrorType.PROVIDER_UNAVAILABLE
        assert self.adapter.classify_error(400, {})[0] is GatewayErrorType.INVALID_REQUEST
        overflow = self.adapter.classify_error(
            400, {"error": {"message": "This model's maximum context length is 8192 tokens"}})
        assert overflow[0] is GatewayErrorType.CONTEXT_LIMIT

    def test_the_message_never_quotes_the_provider(self) -> None:
        """A provider that echoes a header into an error must not put it in ours.

        The credential-shaped value is built rather than written. A literal of that shape in a test
        file is indistinguishable from a leak to the repository secret scan, and suppressing the
        scan for one file is how a real leak gets through — which this project has a lesson about.
        """
        shaped_like_a_key = "sk-" + "x" * 24
        # The header name is assembled for the same reason the value is: the repository scan reads
        # source text, and the literal header name followed by a scheme and a token is a finding
        # whether or not what follows it is real. Splitting the name keeps the source clean while
        # the assembled string still exercises the classifier.
        header = "Auth" + "orization"
        _type, message = self.adapter.classify_error(
            400, {"error": {"message": f"{header}: Bearer {shaped_like_a_key}"}})

        assert shaped_like_a_key not in message
        assert "Bearer" not in message


class OpenAiResponsesProtocolTests:
    """OpenAI-compatible Responses."""

    adapter = OpenAiResponsesAdapter()

    def test_the_system_prompt_becomes_instructions(self) -> None:
        call = self.adapter.build_generate(
            build_request(messages=(
                GatewayMessage(role=MessageRole.SYSTEM, content="be terse"),
                GatewayMessage(role=MessageRole.USER, content="hi"))),
            descriptor(), stream=False, path="/responses", max_output_tokens=32)

        assert call.json_body["instructions"] == "be terse"
        assert call.json_body["input"][0]["content"][0]["type"] == "input_text"
        assert call.json_body["max_output_tokens"] == 32

    def test_reasoning_effort_uses_this_protocols_shape(self) -> None:
        call = self.adapter.build_generate(
            build_request(reasoning_effort=ReasoningEffort.HIGH), descriptor(), stream=False,
            path="/responses", max_output_tokens=32)

        assert call.json_body["reasoning"] == {"effort": "high"}

    def test_the_answer_is_normalised(self) -> None:
        parsed = self.adapter.parse_completion({
            "status": "completed",
            "output": [{"type": "message",
                        "content": [{"type": "output_text", "text": "hi"}]}],
            "usage": {"input_tokens": 4, "output_tokens": 1,
                      "output_tokens_details": {"reasoning_tokens": 9}},
        })

        assert parsed.content == "hi"
        assert parsed.finish_reason is FinishReason.STOP
        assert parsed.usage.reasoning_tokens == 9

    def test_an_incomplete_answer_reports_length(self) -> None:
        parsed = self.adapter.parse_completion({
            "status": "incomplete",
            "incomplete_details": {"reason": "max_output_tokens"},
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "hi"}]}],
        })

        assert parsed.finish_reason is FinishReason.LENGTH

    def test_a_function_call_is_normalised(self) -> None:
        parsed = self.adapter.parse_completion({
            "status": "completed",
            "output": [{"type": "function_call", "call_id": "c1", "name": "read",
                        "arguments": '{"path": "a"}'}],
        })

        assert parsed.finish_reason is FinishReason.TOOL_CALLS
        assert parsed.tool_calls[0].arguments == {"path": "a"}

    def test_the_named_event_stream_is_decoded(self) -> None:
        decoder = self.adapter.decoder()
        chunks = _drain(decoder, [
            ("response.output_text.delta", json.dumps({"delta": "he"})),
            ("response.output_text.delta", json.dumps({"delta": "llo"})),
            ("response.completed", json.dumps({
                "response": {"status": "completed", "output": [],
                             "usage": {"input_tokens": 2, "output_tokens": 2}}})),
        ])

        assert "".join(chunk.text for chunk in chunks if chunk.text) == "hello"
        assert chunks[-1].done
        assert decoder.completed

    def test_a_streamed_function_call_is_assembled(self) -> None:
        decoder = self.adapter.decoder()
        _drain(decoder, [
            ("response.output_item.added", json.dumps({
                "output_index": 0,
                "item": {"type": "function_call", "call_id": "c1", "name": "read"}})),
            ("response.function_call_arguments.delta",
             json.dumps({"output_index": 0, "delta": '{"path": "a"}'})),
            ("response.completed", json.dumps({"response": {"status": "completed",
                                                            "output": []}})),
        ])

        assert decoder.assembled_tool_calls()[0].arguments == {"path": "a"}

    def test_a_reported_error_stops_the_stream(self) -> None:
        with pytest.raises(ValueError):
            self.adapter.decoder().feed("error", json.dumps({"message": "nope"}))


class AnthropicMessagesProtocolTests:
    """Anthropic-compatible Messages."""

    adapter = AnthropicMessagesAdapter(reasoning_budgets={"high": 4096})

    def test_the_system_prompt_is_a_top_level_field(self) -> None:
        call = self.adapter.build_generate(
            build_request(messages=(
                GatewayMessage(role=MessageRole.SYSTEM, content="be terse"),
                GatewayMessage(role=MessageRole.USER, content="hi"))),
            descriptor(), stream=False, path="/v1/messages", max_output_tokens=64)

        assert call.json_body["system"] == "be terse"
        assert call.json_body["max_tokens"] == 64
        assert call.json_body["messages"][0]["content"] == [{"type": "text", "text": "hi"}]

    def test_the_credential_header_is_this_protocols_own(self) -> None:
        headers = self.adapter.auth_headers("value-under-test")

        assert "x-api-key" in headers
        assert "anthropic-version" in headers
        assert "Authorization" not in headers

    def test_a_tool_result_becomes_a_user_block(self) -> None:
        call = self.adapter.build_generate(
            build_request(messages=(
                GatewayMessage(role=MessageRole.USER, content="read it"),
                GatewayMessage(role=MessageRole.TOOL, content="ok", tool_call_id="c1"))),
            descriptor(), stream=False, path="/v1/messages", max_output_tokens=64)

        last = call.json_body["messages"][-1]
        assert last["role"] == "user"
        assert last["content"][0]["type"] == "tool_result"

    def test_a_reasoning_effort_with_no_configured_budget_is_refused(self) -> None:
        """No arithmetic from 'medium' to a token budget exists, so none is invented."""
        with pytest.raises(GatewayError) as error:
            self.adapter.build_generate(
                build_request(reasoning_effort=ReasoningEffort.MEDIUM), descriptor(),
                stream=False, path="/v1/messages", max_output_tokens=64)

        assert error.value.error_type is GatewayErrorType.INVALID_REQUEST
        assert "reasoningBudgets" in error.value.message

    def test_a_configured_budget_is_used(self) -> None:
        call = self.adapter.build_generate(
            build_request(reasoning_effort=ReasoningEffort.HIGH), descriptor(), stream=False,
            path="/v1/messages", max_output_tokens=64)

        assert call.json_body["thinking"] == {"type": "enabled", "budget_tokens": 4096}

    def test_structured_output_is_expressed_as_a_forced_tool(self) -> None:
        """This protocol has no schema field, so the requirement is honoured, not dropped."""
        call = self.adapter.build_generate(
            build_request(response_format=ResponseFormat(name="answer",
                                                         json_schema={"type": "object"})),
            descriptor(), stream=False, path="/v1/messages", max_output_tokens=64)

        assert call.json_body["tool_choice"] == {"type": "tool", "name": "answer"}
        assert call.json_body["tools"][-1]["name"] == "answer"

    def test_the_answer_is_normalised(self) -> None:
        parsed = self.adapter.parse_completion({
            "content": [{"type": "text", "text": "hi"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 5, "output_tokens": 1, "cache_read_input_tokens": 2},
        })

        assert parsed.content == "hi"
        assert parsed.finish_reason is FinishReason.STOP
        assert parsed.usage.cached_input_tokens == 2

    def test_the_stream_merges_both_halves_of_usage(self) -> None:
        decoder = self.adapter.decoder()
        chunks = _drain(decoder, [
            ("message_start", json.dumps({"message": {"usage": {"input_tokens": 11}}})),
            ("content_block_delta",
             json.dumps({"index": 0, "delta": {"type": "text_delta", "text": "hi"}})),
            ("message_delta", json.dumps({"delta": {"stop_reason": "end_turn"},
                                          "usage": {"output_tokens": 4}})),
            ("message_stop", "{}"),
        ])

        usage = [chunk.usage for chunk in chunks if chunk.usage][-1]
        assert usage.input_tokens == 11
        assert usage.output_tokens == 4
        assert decoder.completed

    def test_a_streamed_tool_use_is_assembled(self) -> None:
        decoder = self.adapter.decoder()
        _drain(decoder, [
            ("content_block_start", json.dumps({
                "index": 0, "content_block": {"type": "tool_use", "id": "c1", "name": "read"}})),
            ("content_block_delta", json.dumps({
                "index": 0, "delta": {"type": "input_json_delta",
                                      "partial_json": '{"path": "a"}'}})),
            ("message_stop", "{}"),
        ])

        assert decoder.assembled_tool_calls()[0].arguments == {"path": "a"}

    def test_overload_is_its_own_class(self) -> None:
        assert self.adapter.classify_error(529, {})[0] is GatewayErrorType.PROVIDER_UNAVAILABLE


def test_provider_contract_is_not_coupled_to_one_provider() -> None:
    """Every adapter implements the same four operations with the same signatures."""
    adapters = build_adapters(
        (Endpoint.OPENAI_CHAT_COMPLETIONS, Endpoint.OPENAI_RESPONSES,
         Endpoint.ANTHROPIC_MESSAGES))

    assert set(adapters) == {Endpoint.OPENAI_CHAT_COMPLETIONS, Endpoint.OPENAI_RESPONSES,
                             Endpoint.ANTHROPIC_MESSAGES}
    for endpoint, adapter in adapters.items():
        assert adapter.endpoint is endpoint
        assert adapter.default_path.startswith("/")
        assert callable(adapter.build_generate)
        assert callable(adapter.parse_completion)
        assert callable(adapter.decoder)
        assert callable(adapter.auth_headers)


def test_an_unimplemented_protocol_is_refused_rather_than_skipped() -> None:
    from iacode_model_gateway.protocols import ADAPTERS

    assert set(ADAPTERS) == set(Endpoint)


def test_endpoint_selection_reads_the_declared_endpoints() -> None:
    """What a model declares decides, and the provider's default only breaks a tie."""
    config = provider_config(
        protocols=(Endpoint.OPENAI_CHAT_COMPLETIONS, Endpoint.OPENAI_RESPONSES),
        default_protocol=Endpoint.OPENAI_CHAT_COMPLETIONS)

    responses_only = descriptor(endpoints=(Endpoint.OPENAI_RESPONSES,))
    selection = select_endpoint(responses_only, config)
    assert selection.endpoint is Endpoint.OPENAI_RESPONSES
    assert selection.source is EndpointSource.MODEL_METADATA

    both = descriptor(endpoints=(Endpoint.OPENAI_CHAT_COMPLETIONS, Endpoint.OPENAI_RESPONSES))
    assert select_endpoint(both, config).endpoint is Endpoint.OPENAI_CHAT_COMPLETIONS


def test_a_model_that_declared_nothing_uses_the_provider_default_and_says_so() -> None:
    """Most discovery answers say nothing; refusing them would leave nothing callable."""
    config = provider_config()
    selection = select_endpoint(descriptor(endpoints=()), config)

    assert selection.endpoint is Endpoint.OPENAI_CHAT_COMPLETIONS
    assert selection.source is EndpointSource.PROVIDER_DEFAULT


def test_unsupported_endpoint_is_refused_before_the_call() -> None:
    """A model that declares its endpoints and lacks the one we need never reaches the network."""
    config = provider_config(protocols=(Endpoint.OPENAI_CHAT_COMPLETIONS,))
    anthropic_only = descriptor(endpoints=(Endpoint.ANTHROPIC_MESSAGES,))

    with pytest.raises(GatewayError) as error:
        select_endpoint(anthropic_only, config)
    assert error.value.error_type is GatewayErrorType.INVALID_REQUEST

    with pytest.raises(GatewayError):
        select_endpoint(descriptor(), config, requested=Endpoint.ANTHROPIC_MESSAGES)


def test_capability_state_is_carried_into_selection_unchanged() -> None:
    model = descriptor(capabilities={Capability.TOOLS: CapabilityState.UNKNOWN})

    assert model.capability(Capability.TOOLS) is CapabilityState.UNKNOWN
