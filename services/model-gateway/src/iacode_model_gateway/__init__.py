"""The IACode Model Gateway.

One boundary for model invocation. Everything above it speaks
:mod:`iacode_model_gateway.contracts` and nothing else; everything below it is a protocol adapter
that translates those contracts into one provider's wire format.

Nothing in this package knows the name of a commercial provider. A provider is an entry in
``.iacode/policies/providers.json`` naming an adapter, an address variable and a credential
variable, which is what lets a second provider be added by configuration rather than by code.

What the gateway deliberately does not do: it does not execute tools — it normalizes the request so
a later Gate can decide — it does not orchestrate agents, it does not retrieve, and it does not
train. Those are Gates 2, 3, 6 and 18.
"""

from iacode_model_gateway.contracts import (
    CONTRACT_VERSION,
    Capability,
    CapabilityProvenance,
    CapabilityState,
    Endpoint,
    FinishReason,
    GatewayMessage,
    GatewayRequest,
    GatewayResponse,
    MessageRole,
    ModelDescriptor,
    ModelRef,
    ReasoningEffort,
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
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.gateway import ModelGateway, default_provider_factory

__all__ = [
    "CONTRACT_VERSION",
    "Capability",
    "CapabilityProvenance",
    "CapabilityState",
    "Endpoint",
    "FinishReason",
    "GatewayError",
    "GatewayErrorType",
    "GatewayMessage",
    "GatewayRequest",
    "GatewayResponse",
    "MessageRole",
    "ModelDescriptor",
    "ModelGateway",
    "ModelRef",
    "ReasoningEffort",
    "ResponseFormat",
    "RouteDecision",
    "RouteReason",
    "StreamEvent",
    "StreamEventType",
    "ToolCall",
    "ToolCallDelta",
    "ToolDefinition",
    "Usage",
    "default_provider_factory",
]
