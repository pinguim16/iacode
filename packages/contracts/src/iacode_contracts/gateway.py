"""The HTTP shapes of the Model Gateway API.

They live in the contracts package for the same reason the Foundation shapes do: more than one
consumer needs them. The frontend reads them today; the agent runtime of a later Gate will speak
them too, and neither should have to import the web application to learn what an inference answer
looks like.

These are *not* the gateway's internal contracts. ``iacode_model_gateway.contracts`` is what the
gateway and its adapters speak, in Python, with tuples and enums; this is what goes over the wire,
in the camel-case convention the Foundation endpoints already use and the browser already reads. The
translation is one function in each direction, in the route module, which is the only place that
knows both.

Nothing here carries a credential, a provider address or a raw provider payload. A caller chooses a
model or a route by name; where that model lives and how it is authenticated is administrative
configuration the API never echoes.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolDefinitionPayload(BaseModel):
    """A tool the caller is willing for the model to ask for."""

    name: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=4096)
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema of the arguments.")


class ToolCallPayload(BaseModel):
    """A tool invocation the model asked for. The gateway normalises it and executes nothing."""

    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    argumentsValid: bool = True
    invalidReason: str | None = None


class ToolCallDeltaPayload(BaseModel):
    """A fragment of a tool call, as it arrives on a stream."""

    index: int
    id: str | None = None
    name: str | None = None
    argumentsFragment: str = ""


class MessagePayload(BaseModel):
    """One turn of the conversation."""

    role: str = Field(description="system, developer, user, assistant or tool.")
    content: str = ""
    name: str | None = None
    toolCallId: str | None = Field(
        default=None, description="Set on a tool message: which call it answers.")


class ResponseFormatPayload(BaseModel):
    """A structured-output request. A schema is required; 'give me JSON' is not a contract."""

    name: str = Field(min_length=1, max_length=128)
    jsonSchema: dict[str, Any]
    strict: bool = True


class InferenceRequest(BaseModel):
    """What a caller asks the gateway to do.

    There is deliberately no field for a provider address, an API key or a header. An address a
    request can supply is an address an attacker can supply, and a gateway that forwarded a caller's
    credential would be a credential proxy.
    """

    model_config = ConfigDict(protected_namespaces=())

    messages: list[MessagePayload] = Field(min_length=1)
    model: str | None = Field(
        default=None, description="An explicit 'provider:model' reference.")
    route: str | None = Field(
        default=None, description="A configured route alias. Mutually exclusive with 'model'.")
    requiredCapabilities: list[str] = Field(default_factory=list)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    topP: float | None = Field(default=None, gt=0.0, le=1.0)
    maxOutputTokens: int | None = Field(default=None, ge=1)
    reasoningEffort: str | None = Field(default=None, description="low, medium, high or max.")
    tools: list[ToolDefinitionPayload] = Field(default_factory=list)
    responseFormat: ResponseFormatPayload | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class UsagePayload(BaseModel):
    """What the call consumed, as far as the provider reported it.

    Every field is optional and absent when the provider said nothing. A zero here would be a
    measurement, which is a different claim from silence.
    """

    inputTokens: int | None = None
    outputTokens: int | None = None
    totalTokens: int | None = None
    cachedInputTokens: int | None = None
    reasoningTokens: int | None = None


class RouteAttemptPayload(BaseModel):
    """One candidate the router tried, and what happened to it."""

    model_config = ConfigDict(protected_namespaces=())

    provider: str
    model: str
    endpoint: str | None = None
    attempt: int
    outcome: str
    errorType: str | None = None
    retries: int = 0
    latencyMs: float | None = None


class RouteDecisionPayload(BaseModel):
    """Why the gateway called what it called. A decision summary, never a model's reasoning."""

    reason: str
    route: str | None = None
    considered: int = 0
    rejected: list[str] = Field(default_factory=list)
    chain: list[RouteAttemptPayload] = Field(default_factory=list)
    fallbackCount: int = 0


class InferenceResponse(BaseModel):
    """The normalised answer."""

    model_config = ConfigDict(protected_namespaces=())

    contractVersion: str
    requestId: str
    provider: str
    model: str
    endpoint: str
    content: str = ""
    toolCalls: list[ToolCallPayload] = Field(default_factory=list)
    finishReason: str
    usage: UsagePayload
    latencyMs: float
    route: RouteDecisionPayload
    cost: float | None = Field(
        default=None,
        description="Absent unless pricing is configured. Zero would mean the call was free.")


class StreamEventPayload(BaseModel):
    """One event of a normalised stream, as it is carried by Server-Sent Events."""

    model_config = ConfigDict(protected_namespaces=())

    type: str
    requestId: str
    sequence: int
    text: str | None = None
    toolCallDelta: ToolCallDeltaPayload | None = None
    usage: UsagePayload | None = None
    finishReason: str | None = None
    provider: str | None = None
    model: str | None = None
    endpoint: str | None = None
    route: RouteDecisionPayload | None = None
    error: dict[str, Any] | None = None
    latencyMs: float | None = None


class CapabilityPayload(BaseModel):
    """What is known about one capability of one model, and on whose authority."""

    state: str = Field(description="SUPPORTED, UNSUPPORTED or UNKNOWN.")
    provenance: str = Field(
        description="PROVIDER_METADATA, MANUAL_CONFIGURATION, OBSERVED or UNKNOWN.")


class ModelSummary(BaseModel):
    """A model as the catalog knows it. Every unknown stays unknown."""

    model_config = ConfigDict(protected_namespaces=())

    provider: str
    model: str
    displayName: str
    family: str | None = None
    contextWindow: int | None = None
    maxOutputTokens: int | None = None
    supportedEndpoints: list[str] = Field(default_factory=list)
    capabilities: dict[str, CapabilityPayload] = Field(default_factory=dict)
    reasoningLevels: list[str] = Field(default_factory=list)
    active: bool = True
    syncedAt: str | None = None


class ModelListResponse(BaseModel):
    """The catalog, after whatever filters the caller asked for."""

    total: int
    models: list[ModelSummary]


class ProviderSummary(BaseModel):
    """A provider's safe metadata.

    There is no credential, no address and no header here, and there is no field that could carry
    one. ``credentialConfigured`` says whether the environment variable is set — which an operator
    needs — without saying anything about its value.
    """

    provider: str
    displayName: str
    adapter: str
    enabled: bool
    protocols: list[str] = Field(default_factory=list)
    credentialConfigured: bool = False
    credentialVariable: str = Field(
        description="The NAME of the environment variable that carries the credential.")
    addressConfigured: bool = False
    addressVariable: str = Field(
        description="The NAME of the environment variable that carries the address.")
    healthy: bool | None = None
    lastHealthCheck: str | None = None
    lastSync: str | None = None
    modelCount: int = 0
    detail: str | None = None


class ProviderListResponse(BaseModel):
    total: int
    providers: list[ProviderSummary]


class SyncOutcomePayload(BaseModel):
    """What one provider's synchronisation changed."""

    provider: str
    added: int = 0
    updated: int = 0
    deactivated: int = 0
    unchanged: int = 0
    errors: list[str] = Field(default_factory=list)


class SyncResponse(BaseModel):
    outcomes: list[SyncOutcomePayload]


class SyncRequest(BaseModel):
    provider: str | None = Field(
        default=None, description="Synchronise one provider; omit for every enabled provider.")


class GatewayHealthResponse(BaseModel):
    """Whether the gateway can work, and whether each provider is reachable.

    The two are separate answers. An unreachable provider does not make the gateway unhealthy, and
    it certainly does not make the process unhealthy: `/health` is about this process and answers
    without touching anything external.
    """

    status: str = Field(description="READY when at least one provider is usable, else DEGRADED.")
    contractVersion: str
    providers: list[ProviderSummary]
    circuits: dict[str, str] = Field(default_factory=dict)
    catalogSize: int = 0
    defaultModel: str | None = None
    routes: list[str] = Field(default_factory=list)
