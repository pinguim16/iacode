"""The OpenAI-compatible Chat Completions protocol.

The most widely implemented shape there is: OpenAI itself, most aggregators, vLLM, llama.cpp's
server, Ollama's compatibility layer. That is why it is the gateway's first adapter and why it is
written to the *common* subset rather than to any one implementation's latest additions.

Two translation decisions are worth stating, because both lose information and both do so knowingly:

**``developer`` becomes ``system``.** The contract keeps the two roles apart so a protocol that
distinguishes them can use the distinction. Chat Completions, as most servers implement it, does
not: sending ``role: "developer"`` to a compatible server that has not adopted it is answered with a
400. Merging here is a translation the adapter is responsible for, and it is done in one place
rather than by asking every caller to know which servers have caught up.

**``max_tokens``, not ``max_completion_tokens``.** The newer name is correct for OpenAI's own
current API and is rejected by a large part of the compatible ecosystem. The older one is still
accepted by both. Where a provider needs the newer spelling, the Responses adapter is the right
destination for that request.
"""

from __future__ import annotations

import json
from typing import Any

from iacode_model_gateway.contracts import (
    Endpoint,
    FinishReason,
    GatewayMessage,
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

__all__ = ["OpenAiChatAdapter", "OpenAiChatStreamDecoder"]

_ROLES: dict[MessageRole, str] = {
    MessageRole.SYSTEM: "system",
    MessageRole.DEVELOPER: "system",
    MessageRole.USER: "user",
    MessageRole.ASSISTANT: "assistant",
    MessageRole.TOOL: "tool",
}

_FINISH_REASONS: dict[str, FinishReason] = {
    "stop": FinishReason.STOP,
    "length": FinishReason.LENGTH,
    "max_tokens": FinishReason.LENGTH,
    "tool_calls": FinishReason.TOOL_CALLS,
    "function_call": FinishReason.TOOL_CALLS,
    "content_filter": FinishReason.CONTENT_FILTER,
}

#: The frame that terminates an OpenAI-compatible stream.
DONE = "[DONE]"


def _finish_reason(value: Any) -> FinishReason:
    if not isinstance(value, str):
        return FinishReason.UNKNOWN
    return _FINISH_REASONS.get(value.strip().lower(), FinishReason.UNKNOWN)


def _usage(payload: Any) -> Usage:
    """Read usage without inventing any of it.

    A provider that omits the block has told us nothing, and every field stays absent. A provider
    that reports only prompt tokens gets exactly that recorded.
    """
    if not isinstance(payload, dict):
        return Usage()
    details = payload.get("prompt_tokens_details")
    completion_details = payload.get("completion_tokens_details")
    return Usage(
        input_tokens=_non_negative(payload.get("prompt_tokens")),
        output_tokens=_non_negative(payload.get("completion_tokens")),
        total_tokens=_non_negative(payload.get("total_tokens")),
        cached_input_tokens=_non_negative(
            details.get("cached_tokens") if isinstance(details, dict) else None),
        reasoning_tokens=_non_negative(
            completion_details.get("reasoning_tokens")
            if isinstance(completion_details, dict) else None),
    )


def _non_negative(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = int(value)
    return number if number >= 0 else None


def _message_payload(message: GatewayMessage) -> dict[str, Any]:
    payload: dict[str, Any] = {"role": _ROLES[message.role], "content": message.content}
    if message.name:
        payload["name"] = message.name
    if message.role is MessageRole.TOOL:
        payload["tool_call_id"] = message.tool_call_id
    if message.tool_calls:
        payload["tool_calls"] = [
            {
                "id": call.id,
                "type": "function",
                "function": {"name": call.name,
                             "arguments": json.dumps(call.arguments, ensure_ascii=False)},
            }
            for call in message.tool_calls
        ]
        # An assistant turn that only requested tools carries no text, and some servers refuse an
        # empty string alongside tool calls while accepting a null.
        if not message.content:
            payload["content"] = None
    return payload


class OpenAiChatStreamDecoder(StreamDecoder):
    """Assembles an OpenAI-compatible stream into gateway chunks.

    Tool calls arrive in fragments keyed by index: the first fragment carries the identifier and the
    name, the rest carry slices of the argument string. The decoder emits each fragment as a delta
    so a consumer can show progress, and keeps the accumulation so the assembled calls can be
    delivered once, complete, when the stream ends.
    """

    def __init__(self) -> None:
        self._tool_calls: dict[int, dict[str, str]] = {}
        self._completed = False
        self._emitted_final = False

    def feed(self, event: str | None, data: str) -> list[StreamChunk]:
        del event  # This protocol carries everything on unnamed ``data:`` frames.
        payload = data.strip()
        if not payload:
            return []
        if payload == DONE:
            self._completed = True
            return self._final_chunks(done=True)

        try:
            frame = json.loads(payload)
        except json.JSONDecodeError as error:
            raise ValueError(f"a stream frame is not valid JSON: {error.msg}") from error
        if not isinstance(frame, dict):
            raise ValueError("a stream frame must be an object")

        chunks: list[StreamChunk] = []
        usage = frame.get("usage")
        if isinstance(usage, dict):
            chunks.append(StreamChunk(usage=_usage(usage)))

        choices = frame.get("choices")
        if not isinstance(choices, list):
            return chunks
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            delta = choice.get("delta")
            if isinstance(delta, dict):
                text = delta.get("content")
                if isinstance(text, str) and text:
                    chunks.append(StreamChunk(text=text))
                chunks.extend(self._tool_fragments(delta.get("tool_calls")))
            reason = choice.get("finish_reason")
            if isinstance(reason, str) and reason:
                chunks.append(StreamChunk(finish_reason=_finish_reason(reason)))
        return chunks

    def finish(self) -> list[StreamChunk]:
        """Deliver the assembled tool calls when the transport closed without a terminal frame."""
        return self._final_chunks(done=False)

    @property
    def completed(self) -> bool:
        return self._completed

    def _final_chunks(self, *, done: bool) -> list[StreamChunk]:
        if self._emitted_final:
            return [StreamChunk(done=True)] if done else []
        self._emitted_final = True
        return [StreamChunk(done=done)]

    def assembled_tool_calls(self) -> tuple[ToolCall, ...]:
        """The complete tool calls, in the order the provider indexed them."""
        return tuple(
            build_tool_call(
                state.get("id") or f"call_{index}",
                state.get("name") or "",
                state.get("arguments", ""))
            for index, state in sorted(self._tool_calls.items())
            if state.get("name")
        )

    def _tool_fragments(self, fragments: Any) -> list[StreamChunk]:
        if not isinstance(fragments, list):
            return []
        chunks: list[StreamChunk] = []
        for fragment in fragments:
            if not isinstance(fragment, dict):
                continue
            index = fragment.get("index")
            index = int(index) if isinstance(index, int) else len(self._tool_calls)
            state = self._tool_calls.setdefault(index, {"arguments": ""})
            identifier = fragment.get("id")
            if isinstance(identifier, str) and identifier:
                state["id"] = identifier
            function = fragment.get("function")
            name = None
            argument_fragment = ""
            if isinstance(function, dict):
                name = function.get("name")
                if isinstance(name, str) and name:
                    state["name"] = name
                piece = function.get("arguments")
                if isinstance(piece, str) and piece:
                    state["arguments"] = state.get("arguments", "") + piece
                    argument_fragment = piece
            chunks.append(StreamChunk(tool_call_delta=ToolCallDelta(
                index=index,
                id=state.get("id"),
                name=state.get("name"),
                arguments_fragment=argument_fragment,
            )))
        return chunks


class OpenAiChatAdapter(ProtocolAdapter):
    """Translate the gateway contract to and from OpenAI-compatible Chat Completions."""

    endpoint = Endpoint.OPENAI_CHAT_COMPLETIONS
    default_path = "/chat/completions"
    default_discovery_path = "/models"

    def auth_headers(self, secret: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {secret}"}

    def build_generate(self, request: GatewayRequest, model: ModelDescriptor, *,
                       stream: bool, path: str, max_output_tokens: int) -> HttpCall:
        body: dict[str, Any] = {
            "model": model.ref.model_id,
            "messages": [_message_payload(message) for message in request.messages],
            "stream": stream,
            "max_tokens": max_output_tokens,
        }
        if request.temperature is not None:
            body["temperature"] = request.temperature
        if request.top_p is not None:
            body["top_p"] = request.top_p
        if request.reasoning_effort is not None:
            body["reasoning_effort"] = str(request.reasoning_effort)
        if request.tools:
            body["tools"] = [
                {"type": "function",
                 "function": {"name": tool.name, "description": tool.description,
                              "parameters": tool.parameters or {"type": "object",
                                                                "properties": {}}}}
                for tool in request.tools
            ]
        if request.response_format is not None:
            body["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": request.response_format.name,
                    "schema": request.response_format.json_schema,
                    "strict": request.response_format.strict,
                },
            }
        if stream:
            # Without this a compatible server ends the stream with no usage block at all, and the
            # call is recorded with unknown token counts even though the provider knew them.
            body["stream_options"] = {"include_usage": True}
        return HttpCall(
            method="POST", path=path,
            headers={"Accept": "text/event-stream" if stream else "application/json",
                     "Content-Type": "application/json"},
            json_body=body)

    def parse_completion(self, payload: dict[str, Any]) -> ParsedCompletion:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("the answer carries no choice")
        first = choices[0]
        if not isinstance(first, dict):
            raise ValueError("the first choice is not an object")
        message = first.get("message")
        message = message if isinstance(message, dict) else {}
        content = message.get("content")
        tool_calls: list[ToolCall] = []
        raw_calls = message.get("tool_calls")
        if isinstance(raw_calls, list):
            for index, raw in enumerate(raw_calls):
                if not isinstance(raw, dict):
                    continue
                function = raw.get("function")
                function = function if isinstance(function, dict) else {}
                name = function.get("name")
                if not isinstance(name, str) or not name:
                    continue
                tool_calls.append(build_tool_call(
                    str(raw.get("id") or f"call_{index}"), name,
                    function.get("arguments") if isinstance(function.get("arguments"), str) else ""))
        return ParsedCompletion(
            content=content if isinstance(content, str) else "",
            tool_calls=tuple(tool_calls),
            finish_reason=_finish_reason(first.get("finish_reason")),
            usage=_usage(payload.get("usage")),
        )

    def decoder(self) -> StreamDecoder:
        return OpenAiChatStreamDecoder()

    def classify_error(self, status_code: int, payload: Any) -> tuple[GatewayErrorType, str]:
        """Refine the shared status mapping where this protocol's body says more.

        A context overflow and a malformed payload are both 400, and they need opposite handling:
        one is worth sending elsewhere, the other is not. The body's own vocabulary is the only
        thing that separates them.
        """
        if status_code == 400 and context_limit_hint(payload):
            return (GatewayErrorType.CONTEXT_LIMIT,
                    "the request exceeds the model's context window")
        if status_code == 404 and isinstance(payload, dict):
            error = payload.get("error")
            code = error.get("code") if isinstance(error, dict) else None
            if isinstance(code, str) and "model" in code.lower():
                return (GatewayErrorType.MODEL_NOT_FOUND, "the provider does not expose this model")
        return super().classify_error(status_code, payload)
