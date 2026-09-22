"""The Anthropic-compatible Messages protocol.

Structurally different from the OpenAI shapes in four ways the adapter has to absorb:

* the system prompt is a top-level ``system`` field, and there is no system *role*;
* content is always a list of typed blocks, even for a single string;
* a tool result is a ``tool_result`` block inside a **user** turn, not a message with its own role;
* ``max_tokens`` is mandatory, so the gateway's own output cap is what fills it.

**Reasoning effort is not guessed.** This protocol expresses deliberation as a token budget, not as
a level, and there is no correct arithmetic from "high" to a number. Inventing one would be this
project asserting a mapping it has never measured, so the budget comes from provider configuration
and a request that asks for an effort the configuration does not map is refused with a message that
says which key is missing. `docs/GATE-1-CHECKLIST.md` row 7.6 asks for a validated level or an
explicit error; a silently dropped ``thinking`` block would be neither.
"""

from __future__ import annotations

from typing import Any

from iacode_model_gateway.contracts import (
    Endpoint,
    FinishReason,
    GatewayRequest,
    MessageRole,
    ModelDescriptor,
    ReasoningEffort,
    ToolCall,
    ToolCallDelta,
    Usage,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.protocols.base import (
    HttpCall,
    ParsedCompletion,
    ProtocolAdapter,
    StreamChunk,
    StreamDecoder,
    build_tool_call,
    context_limit_hint,
)

__all__ = ["AnthropicMessagesAdapter", "AnthropicMessagesStreamDecoder"]

DEFAULT_VERSION = "2023-06-01"

_STOP_REASONS: dict[str, FinishReason] = {
    "end_turn": FinishReason.STOP,
    "stop_sequence": FinishReason.STOP,
    "max_tokens": FinishReason.LENGTH,
    "tool_use": FinishReason.TOOL_CALLS,
    "refusal": FinishReason.CONTENT_FILTER,
}


def _non_negative(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = int(value)
    return number if number >= 0 else None


def _usage(payload: Any) -> Usage:
    if not isinstance(payload, dict):
        return Usage()
    return Usage(
        input_tokens=_non_negative(payload.get("input_tokens")),
        output_tokens=_non_negative(payload.get("output_tokens")),
        cached_input_tokens=_non_negative(payload.get("cache_read_input_tokens")),
    )


def _merge_usage(first: Usage, second: Usage) -> Usage:
    """Combine the two halves this protocol reports at different moments.

    ``message_start`` carries the input tokens and ``message_delta`` the output tokens. Taking only
    the second would report a call that consumed no input.
    """
    return Usage(
        input_tokens=second.input_tokens if second.input_tokens is not None else first.input_tokens,
        output_tokens=(second.output_tokens if second.output_tokens is not None
                       else first.output_tokens),
        cached_input_tokens=(second.cached_input_tokens if second.cached_input_tokens is not None
                             else first.cached_input_tokens),
        reasoning_tokens=(second.reasoning_tokens if second.reasoning_tokens is not None
                          else first.reasoning_tokens),
    )


class AnthropicMessagesStreamDecoder(StreamDecoder):
    """Decode the named-event Messages stream."""

    def __init__(self) -> None:
        self._blocks: dict[int, dict[str, str]] = {}
        self._usage = Usage()
        self._completed = False

    @property
    def completed(self) -> bool:
        return self._completed

    def feed(self, event: str | None, data: str) -> list[StreamChunk]:
        import json

        body = data.strip()
        if not body:
            return []
        try:
            frame = json.loads(body)
        except json.JSONDecodeError as error:
            raise ValueError(f"a stream frame is not valid JSON: {error.msg}") from error
        if not isinstance(frame, dict):
            raise ValueError("a stream frame must be an object")
        name = event or frame.get("type")
        if not isinstance(name, str):
            return []

        if name == "message_start":
            message = frame.get("message")
            if isinstance(message, dict):
                self._usage = _merge_usage(self._usage, _usage(message.get("usage")))
            return []
        if name == "content_block_start":
            return self._block_start(frame)
        if name == "content_block_delta":
            return self._block_delta(frame)
        if name == "message_delta":
            self._usage = _merge_usage(self._usage, _usage(frame.get("usage")))
            delta = frame.get("delta")
            reason = delta.get("stop_reason") if isinstance(delta, dict) else None
            chunks = [StreamChunk(usage=self._usage)] if not self._usage.empty else []
            if isinstance(reason, str):
                chunks.append(StreamChunk(
                    finish_reason=_STOP_REASONS.get(reason, FinishReason.UNKNOWN)))
            return chunks
        if name == "message_stop":
            self._completed = True
            return [StreamChunk(done=True)]
        if name == "error":
            raise ValueError("the provider reported an error on the stream")
        return []

    def _block_start(self, frame: dict[str, Any]) -> list[StreamChunk]:
        index = frame.get("index")
        index = int(index) if isinstance(index, int) else len(self._blocks)
        block = frame.get("content_block")
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            return []
        state = self._blocks.setdefault(index, {"arguments": ""})
        identifier = block.get("id")
        if isinstance(identifier, str) and identifier:
            state["id"] = identifier
        name = block.get("name")
        if isinstance(name, str) and name:
            state["name"] = name
        return [StreamChunk(tool_call_delta=ToolCallDelta(
            index=index, id=state.get("id"), name=state.get("name"), arguments_fragment=""))]

    def _block_delta(self, frame: dict[str, Any]) -> list[StreamChunk]:
        index = frame.get("index")
        index = int(index) if isinstance(index, int) else 0
        delta = frame.get("delta")
        if not isinstance(delta, dict):
            return []
        kind = delta.get("type")
        if kind == "text_delta":
            text = delta.get("text")
            return [StreamChunk(text=text)] if isinstance(text, str) and text else []
        if kind == "input_json_delta":
            piece = delta.get("partial_json")
            if not isinstance(piece, str) or not piece:
                return []
            state = self._blocks.setdefault(index, {"arguments": ""})
            state["arguments"] = state.get("arguments", "") + piece
            return [StreamChunk(tool_call_delta=ToolCallDelta(
                index=index, id=state.get("id"), name=state.get("name"),
                arguments_fragment=piece))]
        return []

    def assembled_tool_calls(self) -> tuple[ToolCall, ...]:
        return tuple(
            build_tool_call(state.get("id") or f"call_{index}", state.get("name") or "",
                            state.get("arguments", ""))
            for index, state in sorted(self._blocks.items())
            if state.get("name")
        )


class AnthropicMessagesAdapter(ProtocolAdapter):
    """Translate the gateway contract to and from the Messages protocol."""

    endpoint = Endpoint.ANTHROPIC_MESSAGES
    default_path = "/v1/messages"
    default_discovery_path = "/v1/models"

    def __init__(self, *, version: str = DEFAULT_VERSION,
                 reasoning_budgets: dict[str, int] | None = None) -> None:
        self.version = version or DEFAULT_VERSION
        self.reasoning_budgets = dict(reasoning_budgets or {})

    def auth_headers(self, secret: str) -> dict[str, str]:
        return {"x-api-key": secret, "anthropic-version": self.version}

    def build_generate(self, request: GatewayRequest, model: ModelDescriptor, *,
                       stream: bool, path: str, max_output_tokens: int) -> HttpCall:
        system: list[str] = []
        messages: list[dict[str, Any]] = []
        for message in request.messages:
            if message.role in (MessageRole.SYSTEM, MessageRole.DEVELOPER):
                system.append(message.content)
                continue
            if message.role is MessageRole.TOOL:
                messages.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": message.tool_call_id,
                     "content": message.content}]})
                continue
            blocks: list[dict[str, Any]] = []
            if message.content:
                blocks.append({"type": "text", "text": message.content})
            for call in message.tool_calls:
                blocks.append({"type": "tool_use", "id": call.id, "name": call.name,
                               "input": call.arguments})
            if blocks:
                messages.append({"role": str(message.role), "content": blocks})

        body: dict[str, Any] = {
            "model": model.ref.model_id,
            "messages": messages,
            "max_tokens": max_output_tokens,
            "stream": stream,
        }
        if system:
            body["system"] = "\n\n".join(text for text in system if text)
        if request.temperature is not None:
            body["temperature"] = request.temperature
        if request.top_p is not None:
            body["top_p"] = request.top_p
        if request.reasoning_effort is not None:
            body["thinking"] = {"type": "enabled",
                                "budget_tokens": self._budget(request.reasoning_effort)}
        if request.tools:
            body["tools"] = [
                {"name": tool.name, "description": tool.description,
                 "input_schema": tool.parameters or {"type": "object", "properties": {}}}
                for tool in request.tools
            ]
        if request.response_format is not None:
            # This protocol has no schema-enforcing field. Silently dropping the requirement would
            # return unvalidated prose to a caller that asked for a structured answer, so the model
            # is given the schema as a tool it must use — the documented way to get a typed result
            # here — and the caller still receives a tool call rather than a fabricated guarantee.
            body["tools"] = list(body.get("tools") or []) + [{
                "name": request.response_format.name,
                "description": "Return the answer through this tool, matching the schema exactly.",
                "input_schema": request.response_format.json_schema,
            }]
            body["tool_choice"] = {"type": "tool", "name": request.response_format.name}

        return HttpCall(
            method="POST", path=path,
            headers={"Accept": "text/event-stream" if stream else "application/json",
                     "Content-Type": "application/json"},
            json_body=body)

    def _budget(self, effort: ReasoningEffort) -> int:
        budget = self.reasoning_budgets.get(str(effort))
        if not isinstance(budget, int) or budget <= 0:
            raise GatewayError(
                GatewayErrorType.INVALID_REQUEST,
                f"this provider maps no thinking budget to reasoning effort {effort!s}; configure "
                f"protocolOptions.reasoningBudgets.{effort!s} or send no reasoning effort")
        return budget

    def parse_completion(self, payload: dict[str, Any]) -> ParsedCompletion:
        import json

        blocks = payload.get("content")
        if not isinstance(blocks, list):
            raise ValueError("the answer carries no content")
        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []
        for index, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                value = block.get("text")
                if isinstance(value, str):
                    text_parts.append(value)
            elif block.get("type") == "tool_use":
                name = block.get("name")
                if not isinstance(name, str) or not name:
                    continue
                arguments = block.get("input")
                tool_calls.append(build_tool_call(
                    str(block.get("id") or f"call_{index}"), name,
                    json.dumps(arguments, ensure_ascii=False) if isinstance(arguments, dict)
                    else ""))
        stop_reason = payload.get("stop_reason")
        return ParsedCompletion(
            content="".join(text_parts),
            tool_calls=tuple(tool_calls),
            finish_reason=_STOP_REASONS.get(str(stop_reason), FinishReason.UNKNOWN),
            usage=_usage(payload.get("usage")),
        )

    def decoder(self) -> StreamDecoder:
        return AnthropicMessagesStreamDecoder()

    def classify_error(self, status_code: int, payload: Any) -> tuple[GatewayErrorType, str]:
        if status_code == 400 and context_limit_hint(payload):
            return (GatewayErrorType.CONTEXT_LIMIT,
                    "the request exceeds the model's context window")
        if status_code == 529:
            return (GatewayErrorType.PROVIDER_UNAVAILABLE, "the provider is overloaded")
        return super().classify_error(status_code, payload)
