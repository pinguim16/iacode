"""The OpenAI-compatible Responses protocol.

A second shape of the same idea, with three differences that matter to a gateway:

* the conversation is ``input`` items with typed content parts rather than flat ``messages``;
* the system prompt is a top-level ``instructions`` field rather than a message;
* the stream is made of **named** events (``response.output_text.delta``) rather than a single
  unnamed frame type, so the decoder switches on the event name and not on the payload's shape.

The adapter exists because the catalog is allowed to say that a model speaks this protocol and not
the other one. `docs/GATE-1-CHECKLIST.md` row 4.5 forbids assuming every model accepts
``/chat/completions``; an adapter that only knew one protocol would make that assumption unavoidable.
"""

from __future__ import annotations

import json
from typing import Any

from iacode_model_gateway.contracts import (
    Endpoint,
    FinishReason,
    GatewayRequest,
    MessageRole,
    ModelDescriptor,
    ToolCall,
    ToolCallDelta,
    Usage,
)
from iacode_model_gateway.errors import GatewayErrorType
from iacode_model_gateway.protocols.base import (
    HttpCall,
    ParsedCompletion,
    ProtocolAdapter,
    StreamChunk,
    StreamDecoder,
    build_tool_call,
    context_limit_hint,
)

__all__ = ["OpenAiResponsesAdapter", "OpenAiResponsesStreamDecoder"]

_INCOMPLETE_REASONS: dict[str, FinishReason] = {
    "max_output_tokens": FinishReason.LENGTH,
    "content_filter": FinishReason.CONTENT_FILTER,
}


def _usage(payload: Any) -> Usage:
    if not isinstance(payload, dict):
        return Usage()
    input_details = payload.get("input_tokens_details")
    output_details = payload.get("output_tokens_details")
    return Usage(
        input_tokens=_non_negative(payload.get("input_tokens")),
        output_tokens=_non_negative(payload.get("output_tokens")),
        total_tokens=_non_negative(payload.get("total_tokens")),
        cached_input_tokens=_non_negative(
            input_details.get("cached_tokens") if isinstance(input_details, dict) else None),
        reasoning_tokens=_non_negative(
            output_details.get("reasoning_tokens") if isinstance(output_details, dict) else None),
    )


def _non_negative(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = int(value)
    return number if number >= 0 else None


def _finish_reason(payload: dict[str, Any]) -> FinishReason:
    status = payload.get("status")
    if status == "completed":
        output = payload.get("output")
        if isinstance(output, list) and any(
                isinstance(item, dict) and item.get("type") == "function_call" for item in output):
            return FinishReason.TOOL_CALLS
        return FinishReason.STOP
    if status == "incomplete":
        details = payload.get("incomplete_details")
        reason = details.get("reason") if isinstance(details, dict) else None
        return _INCOMPLETE_REASONS.get(str(reason), FinishReason.UNKNOWN)
    if status in ("failed", "cancelled"):
        return FinishReason.ERROR if status == "failed" else FinishReason.CANCELLED
    return FinishReason.UNKNOWN


class OpenAiResponsesStreamDecoder(StreamDecoder):
    """Decode a named-event Responses stream."""

    def __init__(self) -> None:
        self._tool_calls: dict[int, dict[str, str]] = {}
        self._completed = False

    @property
    def completed(self) -> bool:
        return self._completed

    def feed(self, event: str | None, data: str) -> list[StreamChunk]:
        body = data.strip()
        if not body or body == "[DONE]":
            return []
        try:
            frame = json.loads(body)
        except json.JSONDecodeError as error:
            raise ValueError(f"a stream frame is not valid JSON: {error.msg}") from error
        if not isinstance(frame, dict):
            raise ValueError("a stream frame must be an object")

        # The event name is on the frame as well as on the SSE envelope. Reading it from the body
        # when the envelope has none keeps the decoder usable against a transport that drops it.
        name = event or frame.get("type")
        if not isinstance(name, str):
            return []

        if name == "response.output_text.delta":
            delta = frame.get("delta")
            return [StreamChunk(text=delta)] if isinstance(delta, str) and delta else []
        if name == "response.output_item.added":
            return self._item_added(frame)
        if name == "response.function_call_arguments.delta":
            return self._arguments_delta(frame)
        if name in ("response.completed", "response.incomplete", "response.failed"):
            self._completed = True
            response = frame.get("response")
            response = response if isinstance(response, dict) else {}
            chunks: list[StreamChunk] = []
            usage = _usage(response.get("usage"))
            if not usage.empty:
                chunks.append(StreamChunk(usage=usage))
            chunks.append(StreamChunk(finish_reason=_finish_reason(response), done=True))
            return chunks
        if name == "error":
            raise ValueError("the provider reported an error on the stream")
        return []

    def _item_added(self, frame: dict[str, Any]) -> list[StreamChunk]:
        item = frame.get("item")
        if not isinstance(item, dict) or item.get("type") != "function_call":
            return []
        index = frame.get("output_index")
        index = int(index) if isinstance(index, int) else len(self._tool_calls)
        state = self._tool_calls.setdefault(index, {"arguments": ""})
        identifier = item.get("call_id") or item.get("id")
        if isinstance(identifier, str) and identifier:
            state["id"] = identifier
        name = item.get("name")
        if isinstance(name, str) and name:
            state["name"] = name
        return [StreamChunk(tool_call_delta=ToolCallDelta(
            index=index, id=state.get("id"), name=state.get("name"), arguments_fragment=""))]

    def _arguments_delta(self, frame: dict[str, Any]) -> list[StreamChunk]:
        index = frame.get("output_index")
        index = int(index) if isinstance(index, int) else 0
        piece = frame.get("delta")
        if not isinstance(piece, str) or not piece:
            return []
        state = self._tool_calls.setdefault(index, {"arguments": ""})
        state["arguments"] = state.get("arguments", "") + piece
        return [StreamChunk(tool_call_delta=ToolCallDelta(
            index=index, id=state.get("id"), name=state.get("name"), arguments_fragment=piece))]

    def assembled_tool_calls(self) -> tuple[ToolCall, ...]:
        return tuple(
            build_tool_call(state.get("id") or f"call_{index}", state.get("name") or "",
                            state.get("arguments", ""))
            for index, state in sorted(self._tool_calls.items())
            if state.get("name")
        )


class OpenAiResponsesAdapter(ProtocolAdapter):
    """Translate the gateway contract to and from the Responses protocol."""

    endpoint = Endpoint.OPENAI_RESPONSES
    default_path = "/responses"
    default_discovery_path = "/models"

    def auth_headers(self, secret: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {secret}"}

    def build_generate(self, request: GatewayRequest, model: ModelDescriptor, *,
                       stream: bool, path: str, max_output_tokens: int) -> HttpCall:
        instructions: list[str] = []
        items: list[dict[str, Any]] = []
        for message in request.messages:
            if message.role in (MessageRole.SYSTEM, MessageRole.DEVELOPER):
                # ``instructions`` is where this protocol puts steering text. Sending it as an input
                # item works on some servers and is ignored by others, which is worse than either.
                instructions.append(message.content)
                continue
            if message.role is MessageRole.TOOL:
                items.append({"type": "function_call_output",
                              "call_id": message.tool_call_id,
                              "output": message.content})
                continue
            part = "output_text" if message.role is MessageRole.ASSISTANT else "input_text"
            if message.content:
                items.append({"role": str(message.role),
                              "content": [{"type": part, "text": message.content}]})
            for call in message.tool_calls:
                items.append({"type": "function_call", "call_id": call.id, "name": call.name,
                              "arguments": json.dumps(call.arguments, ensure_ascii=False)})

        body: dict[str, Any] = {
            "model": model.ref.model_id,
            "input": items,
            "stream": stream,
            "max_output_tokens": max_output_tokens,
        }
        if instructions:
            body["instructions"] = "\n\n".join(text for text in instructions if text)
        if request.temperature is not None:
            body["temperature"] = request.temperature
        if request.top_p is not None:
            body["top_p"] = request.top_p
        if request.reasoning_effort is not None:
            body["reasoning"] = {"effort": str(request.reasoning_effort)}
        if request.tools:
            body["tools"] = [
                {"type": "function", "name": tool.name, "description": tool.description,
                 "parameters": tool.parameters or {"type": "object", "properties": {}}}
                for tool in request.tools
            ]
        if request.response_format is not None:
            body["text"] = {"format": {
                "type": "json_schema",
                "name": request.response_format.name,
                "schema": request.response_format.json_schema,
                "strict": request.response_format.strict,
            }}
        return HttpCall(
            method="POST", path=path,
            headers={"Accept": "text/event-stream" if stream else "application/json",
                     "Content-Type": "application/json"},
            json_body=body)

    def parse_completion(self, payload: dict[str, Any]) -> ParsedCompletion:
        output = payload.get("output")
        if not isinstance(output, list):
            raise ValueError("the answer carries no output")
        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []
        for index, item in enumerate(output):
            if not isinstance(item, dict):
                continue
            kind = item.get("type")
            if kind == "message":
                for part in item.get("content") or []:
                    if isinstance(part, dict) and part.get("type") == "output_text":
                        value = part.get("text")
                        if isinstance(value, str):
                            text_parts.append(value)
            elif kind == "function_call":
                name = item.get("name")
                if not isinstance(name, str) or not name:
                    continue
                arguments = item.get("arguments")
                tool_calls.append(build_tool_call(
                    str(item.get("call_id") or item.get("id") or f"call_{index}"), name,
                    arguments if isinstance(arguments, str) else ""))
        return ParsedCompletion(
            content="".join(text_parts),
            tool_calls=tuple(tool_calls),
            finish_reason=_finish_reason(payload),
            usage=_usage(payload.get("usage")),
        )

    def decoder(self) -> StreamDecoder:
        return OpenAiResponsesStreamDecoder()

    def classify_error(self, status_code: int, payload: Any) -> tuple[GatewayErrorType, str]:
        if status_code == 400 and context_limit_hint(payload):
            return (GatewayErrorType.CONTEXT_LIMIT,
                    "the request exceeds the model's context window")
        return super().classify_error(status_code, payload)
