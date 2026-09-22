"""Request limits.

These are guard rails against an accident, not a quota system. `docs/GATE-1-CHECKLIST.md` row 8.10
asks for bounds that stop a mistake — a loop that appended to a message list, a tool schema built
from a database dump, an output cap someone typed an extra zero into — from becoming an expensive
provider call. Anything shaped like per-tenant accounting belongs to a Gate that has tenants.

Every limit is checked **before** the request leaves the process. A bound enforced by the provider's
rejection is not a bound; it is a way of finding out after paying for the round trip.
"""

from __future__ import annotations

import json

from iacode_model_gateway.config import GatewaySettings
from iacode_model_gateway.contracts import GatewayRequest
from iacode_model_gateway.errors import GatewayError, GatewayErrorType

__all__ = ["effective_output_tokens", "enforce_limits", "request_size_bytes"]


def request_size_bytes(request: GatewayRequest) -> int:
    """How large the request's content is, measured as the bytes it would serialise to.

    Measuring the serialised form rather than counting characters is what makes the limit mean the
    same thing for an English prompt and for one with an alphabet that costs three bytes a
    character.
    """
    payload = {
        "messages": [
            {"role": str(message.role), "content": message.content,
             "tool_calls": [call.model_dump(mode="json") for call in message.tool_calls]}
            for message in request.messages
        ],
        "tools": [tool.model_dump(mode="json") for tool in request.tools],
        "response_format": (request.response_format.model_dump(mode="json")
                            if request.response_format else None),
    }
    return len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def enforce_limits(request: GatewayRequest, settings: GatewaySettings) -> None:
    """Refuse a request that exceeds a configured bound, naming which one."""
    if len(request.messages) > settings.max_messages:
        raise GatewayError(
            GatewayErrorType.INVALID_REQUEST,
            f"the request carries {len(request.messages)} messages, above the configured limit of "
            f"{settings.max_messages}",
            details={"limit": "messages", "value": len(request.messages),
                     "maximum": settings.max_messages})

    if len(request.tools) > settings.max_tools:
        raise GatewayError(
            GatewayErrorType.INVALID_REQUEST,
            f"the request declares {len(request.tools)} tools, above the configured limit of "
            f"{settings.max_tools}",
            details={"limit": "tools", "value": len(request.tools),
                     "maximum": settings.max_tools})

    if request.max_output_tokens is not None \
            and request.max_output_tokens > settings.max_output_tokens:
        raise GatewayError(
            GatewayErrorType.INVALID_REQUEST,
            f"the request asks for {request.max_output_tokens} output tokens, above the configured "
            f"limit of {settings.max_output_tokens}",
            details={"limit": "maxOutputTokens", "value": request.max_output_tokens,
                     "maximum": settings.max_output_tokens})

    size = request_size_bytes(request)
    if size > settings.max_request_bytes:
        raise GatewayError(
            GatewayErrorType.INVALID_REQUEST,
            f"the request payload is {size} bytes, above the configured limit of "
            f"{settings.max_request_bytes}",
            details={"limit": "requestBytes", "value": size,
                     "maximum": settings.max_request_bytes})


def effective_output_tokens(request: GatewayRequest, settings: GatewaySettings,
                            model_limit: int | None) -> int:
    """The output cap to send, which is the smallest of the three that exist.

    A cap is mandatory for one of the protocols and strongly advisable for the others, so there is
    always a number. The model's own limit wins over the gateway's when it is smaller, because
    asking a model for more than it can produce is a request it refuses rather than truncates.
    """
    candidates = [settings.max_output_tokens]
    if request.max_output_tokens is not None:
        candidates.append(request.max_output_tokens)
    if model_limit is not None:
        candidates.append(model_limit)
    return max(min(candidates), 1)
