"""The protocol adapters and the factory that builds them from provider configuration.

A provider declares which protocols it serves and, optionally, non-secret options for them. This
module turns that declaration into adapter instances. Adding a protocol means adding a module and
one entry in :data:`ADAPTERS`; nothing above this package learns a new name.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from iacode_model_gateway.contracts import Endpoint
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.protocols.anthropic_messages import AnthropicMessagesAdapter
from iacode_model_gateway.protocols.base import (
    HttpCall,
    ParsedCompletion,
    ProtocolAdapter,
    RawModel,
    StreamChunk,
    StreamDecoder,
)
from iacode_model_gateway.protocols.openai_chat import OpenAiChatAdapter
from iacode_model_gateway.protocols.openai_responses import OpenAiResponsesAdapter
from iacode_model_gateway.protocols.selection import (
    EndpointSelection,
    EndpointSource,
    select_endpoint,
)

__all__ = [
    "ADAPTERS",
    "AnthropicMessagesAdapter",
    "EndpointSelection",
    "EndpointSource",
    "HttpCall",
    "OpenAiChatAdapter",
    "OpenAiResponsesAdapter",
    "ParsedCompletion",
    "ProtocolAdapter",
    "RawModel",
    "StreamChunk",
    "StreamDecoder",
    "build_adapters",
    "select_endpoint",
]


def _anthropic(options: dict[str, Any]) -> ProtocolAdapter:
    from iacode_model_gateway.protocols.anthropic_messages import DEFAULT_VERSION

    budgets = options.get("reasoningBudgets") or {}
    version = str(options.get("anthropicVersion") or "").strip() or DEFAULT_VERSION
    return AnthropicMessagesAdapter(
        version=version,
        reasoning_budgets={str(key): int(value) for key, value in budgets.items()
                           if isinstance(value, int) and not isinstance(value, bool)},
    )


#: Every protocol the gateway can speak, by the family it implements.
ADAPTERS: dict[Endpoint, Callable[[dict[str, Any]], ProtocolAdapter]] = {
    Endpoint.OPENAI_CHAT_COMPLETIONS: lambda _options: OpenAiChatAdapter(),
    Endpoint.OPENAI_RESPONSES: lambda _options: OpenAiResponsesAdapter(),
    Endpoint.ANTHROPIC_MESSAGES: _anthropic,
}


def build_adapters(protocols: tuple[Endpoint, ...],
                   options: dict[str, Any] | None = None) -> dict[Endpoint, ProtocolAdapter]:
    """Instantiate the adapters a provider declares.

    An unknown protocol is refused rather than skipped: a provider configured for a family we do not
    implement would otherwise appear to work until a request happened to need it.
    """
    settings = dict(options or {})
    adapters: dict[Endpoint, ProtocolAdapter] = {}
    for endpoint in protocols:
        factory = ADAPTERS.get(endpoint)
        if factory is None:
            raise GatewayError(
                GatewayErrorType.INTERNAL_GATEWAY_ERROR,
                f"no adapter implements the {endpoint!s} protocol")
        adapters[endpoint] = factory(settings)
    return adapters
