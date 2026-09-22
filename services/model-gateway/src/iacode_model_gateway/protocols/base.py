"""What a protocol adapter is, and what it is not allowed to know.

A protocol adapter translates between the gateway contract and one wire protocol. It knows request
shapes, response shapes, stream framing, authentication headers and error bodies. It knows nothing
about routing, retrying, circuits, catalogs or persistence: those are decided once, above, for every
protocol, and an adapter that retried on its own would produce a total attempt count nobody could
predict.

The split that makes this testable is that **an adapter never performs I/O**. It builds a
description of a call and parses the bytes that come back. One HTTP client, in
``providers/http_provider.py``, performs every request, and the adapter suite exercises request
building and response parsing without a socket.

Streaming is decoded by a small state machine per call rather than by a generator, because the same
decoder has to serve both the transport reading frames off a socket and a test feeding it a list of
recorded frames.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from iacode_model_gateway.contracts import (
    Endpoint,
    FinishReason,
    GatewayRequest,
    ModelDescriptor,
    ToolCall,
    ToolCallDelta,
    Usage,
)
from iacode_model_gateway.errors import GatewayErrorType

__all__ = [
    "HttpCall",
    "ParsedCompletion",
    "ProtocolAdapter",
    "RawModel",
    "StreamChunk",
    "StreamDecoder",
    "build_tool_call",
    "context_limit_hint",
]


@dataclass(frozen=True)
class HttpCall:
    """A request an adapter wants made, without the credential.

    The authorization header is added by the provider immediately before the call and is never part
    of this object, so a call description can be logged, compared in a test or written into a
    fixture without anything being redacted first.
    """

    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    json_body: dict[str, Any] | None = None
    query: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RawModel:
    """One model as a provider described it, before normalization."""

    model_id: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ParsedCompletion:
    """A non-streaming answer, already in the gateway's vocabulary."""

    content: str = ""
    tool_calls: tuple[ToolCall, ...] = ()
    finish_reason: FinishReason = FinishReason.UNKNOWN
    usage: Usage = field(default_factory=Usage)


@dataclass(frozen=True)
class StreamChunk:
    """One thing that happened on a stream.

    A chunk carries whichever of the four kinds of news it has. ``done`` marks the frame that ends
    the stream, which is not the same as the transport closing: a provider that stops sending
    without a terminal frame is a truncated stream, and the difference has to be visible.
    """

    text: str | None = None
    tool_call_delta: ToolCallDelta | None = None
    usage: Usage | None = None
    finish_reason: FinishReason | None = None
    done: bool = False


def build_tool_call(call_id: str, name: str, raw_arguments: str) -> ToolCall:
    """Normalize one tool call, including the case where the model emitted invalid JSON.

    A model producing unparseable arguments is ordinary, not exceptional. Throwing the call away
    would hide a real event from the caller, and inventing an empty argument object would hand a
    later Gate a call that looks executable and is not. The call is therefore returned, flagged, and
    the reason recorded.
    """
    text = raw_arguments or ""
    if not text.strip():
        return ToolCall(id=call_id, name=name, arguments={})
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as error:
        return ToolCall(
            id=call_id, name=name, arguments={}, arguments_valid=False,
            invalid_reason=f"arguments are not valid JSON: {error.msg} at position {error.pos}")
    if not isinstance(parsed, dict):
        return ToolCall(
            id=call_id, name=name, arguments={}, arguments_valid=False,
            invalid_reason=f"arguments must be a JSON object, found {type(parsed).__name__}")
    return ToolCall(id=call_id, name=name, arguments=parsed)


class StreamDecoder(ABC):
    """Turns raw stream frames into :class:`StreamChunk` values, statefully."""

    @abstractmethod
    def feed(self, event: str | None, data: str) -> list[StreamChunk]:
        """Decode one frame. ``event`` is the SSE event name when the protocol uses one."""

    def finish(self) -> list[StreamChunk]:
        """Anything the decoder was holding when the transport closed.

        The default is nothing. A protocol that assembles tool calls across frames overrides it so
        the assembled calls are not lost when the last frame carries no terminator.
        """
        return []

    @property
    def completed(self) -> bool:
        """Whether a terminal frame was seen, as opposed to the connection simply ending."""
        return getattr(self, "_completed", False)


class ProtocolAdapter(ABC):
    """One wire protocol, as a pure translation layer."""

    #: The protocol family this adapter implements.
    endpoint: Endpoint
    #: Where the generation endpoint lives, relative to the provider's base URL, by default.
    default_path: str
    #: Where model discovery lives by default.
    default_discovery_path: str = "/models"

    @abstractmethod
    def auth_headers(self, secret: str) -> dict[str, str]:
        """The headers that authenticate a call. The only place a credential is ever read."""

    @abstractmethod
    def build_generate(self, request: GatewayRequest, model: ModelDescriptor, *,
                       stream: bool, path: str, max_output_tokens: int) -> HttpCall:
        """Describe the generation call for this request and model."""

    @abstractmethod
    def parse_completion(self, payload: dict[str, Any]) -> ParsedCompletion:
        """Read a non-streaming answer."""

    @abstractmethod
    def decoder(self) -> StreamDecoder:
        """A fresh decoder for one streaming call."""

    def build_discovery(self, path: str) -> HttpCall:
        """Describe the model-discovery call. Most protocols share this shape."""
        return HttpCall(method="GET", path=path, headers={"Accept": "application/json"})

    def parse_models(self, payload: Any) -> list[RawModel]:
        """Read a discovery answer into raw model records.

        Two shapes are accepted because both are in the wild: ``{"data": [...]}`` and a bare list.
        A third, unrecognised shape is an error rather than an empty catalog — reporting "no models"
        for an answer we failed to understand would deactivate a provider's whole catalog.
        """
        entries: Any
        if isinstance(payload, dict):
            entries = payload.get("data", payload.get("models"))
        else:
            entries = payload
        if not isinstance(entries, list):
            raise ValueError(
                "the discovery answer is neither a list nor an object carrying 'data' or 'models'")
        models: list[RawModel] = []
        for entry in entries:
            if isinstance(entry, str):
                models.append(RawModel(model_id=entry, payload={"id": entry}))
                continue
            if not isinstance(entry, dict):
                raise ValueError("a discovery entry is neither a string nor an object")
            identifier = entry.get("id") or entry.get("name") or entry.get("model")
            if not isinstance(identifier, str) or not identifier.strip():
                raise ValueError("a discovery entry carries no usable model identifier")
            models.append(RawModel(model_id=identifier.strip(), payload=entry))
        return models

    def classify_error(self, status_code: int, payload: Any) -> tuple[GatewayErrorType, str]:
        """Map a failing HTTP answer onto the taxonomy.

        The shared mapping is by status code, which every HTTP provider agrees on. A protocol whose
        bodies carry a more precise type overrides this and refines the answer; none of them may
        return the provider's message verbatim, because a provider that echoes a request header into
        an error body would put an ``Authorization`` value into our exception text.
        """
        del payload  # The body is not trusted as message material; see the docstring.
        if status_code == 401:
            return (GatewayErrorType.AUTHENTICATION_ERROR,
                    "the provider rejected the credential")
        if status_code == 403:
            return (GatewayErrorType.AUTHORIZATION_ERROR,
                    "the provider refused the request for this credential")
        if status_code == 404:
            return (GatewayErrorType.MODEL_NOT_FOUND,
                    "the provider does not expose this model or endpoint")
        if status_code in (408, 504):
            return (GatewayErrorType.PROVIDER_TIMEOUT, "the provider timed out")
        if status_code == 429:
            return (GatewayErrorType.RATE_LIMITED, "the provider rate limited the request")
        if status_code in (413, 422):
            return (GatewayErrorType.INVALID_REQUEST, "the provider refused the request payload")
        if status_code == 400:
            return (GatewayErrorType.INVALID_REQUEST, "the provider refused the request")
        if status_code in (502, 503):
            return (GatewayErrorType.PROVIDER_UNAVAILABLE, "the provider is unavailable")
        if status_code >= 500:
            return (GatewayErrorType.TRANSIENT_PROVIDER_ERROR, "the provider failed")
        return (GatewayErrorType.PERMANENT_PROVIDER_ERROR,
                f"the provider answered {status_code}")


def context_limit_hint(payload: Any) -> bool:
    """Whether a refusal body is about the context window rather than about the payload.

    A context overflow arrives as a 400 exactly like a malformed request, and the two need opposite
    handling: one is worth routing elsewhere, the other is not. The check looks at the body's own
    vocabulary and is deliberately conservative — an unrecognised 400 stays an invalid request,
    because treating a malformed payload as a context problem would send it to a second model that
    refuses it identically.
    """
    if not isinstance(payload, dict):
        return False
    error = payload.get("error")
    haystack = " ".join(
        str(value) for value in (
            error.get("message") if isinstance(error, dict) else error,
            error.get("code") if isinstance(error, dict) else None,
            error.get("type") if isinstance(error, dict) else None,
            payload.get("message"),
        ) if value
    ).lower()
    if not haystack:
        return False
    markers = (
        "context length", "context_length", "context window", "maximum context",
        "too many tokens", "reduce the length", "prompt is too long", "input is too long",
    )
    return any(marker in haystack for marker in markers)
