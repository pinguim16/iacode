"""The IACode Model Gateway contract.

This module is the boundary. Everything above it — the API, the future agent runtime, the
orchestrator, the frontend — speaks only these types. Everything below it — the protocol adapters —
translates them into whatever a particular provider wants and translates the answer back.

Three rules shape the whole file.

**A capability is a tri-state.** ``SUPPORTED``, ``UNSUPPORTED`` and ``UNKNOWN`` are three different
facts, and collapsing the third into the second is the mistake that makes a gateway confident about
a model it has never been told anything about. A provider that lists a model without saying whether
it streams has told us nothing, and routing has to be able to see that.

**Nothing here is a provider's own shape.** There is no field that exists because one vendor has it.
``finish_reason`` is our vocabulary, ``usage`` is our vocabulary, and a tool call is our record of a
request the model made — not the JSON that carried it.

**Absent is not zero and not false.** A token count the provider did not report is ``None``. A cost
we cannot compute is ``None``. Writing ``0`` there would state that the call was free, which is a
different claim and usually a wrong one.

The contract carries an explicit version. A consumer that has to discover an incompatible change by
crashing is a consumer that will discover it in production.
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

__all__ = [
    "CONTRACT_VERSION",
    "Capability",
    "CapabilityProvenance",
    "CapabilityState",
    "Endpoint",
    "FinishReason",
    "GatewayMessage",
    "GatewayRequest",
    "GatewayResponse",
    "MessageRole",
    "ModelDescriptor",
    "ModelRef",
    "ReasoningEffort",
    "ResponseFormat",
    "RouteAttempt",
    "RouteDecision",
    "RouteReason",
    "StreamEvent",
    "StreamEventType",
    "TokenEstimate",
    "ToolCall",
    "ToolCallDelta",
    "ToolDefinition",
    "Usage",
]

#: The version of this contract. It changes when a consumer would have to change with it.
CONTRACT_VERSION = "1.0.0"


class MessageRole(StrEnum):
    """Who produced a message.

    ``DEVELOPER`` is carried separately from ``SYSTEM`` because the two mean different things to a
    model family that distinguishes them, and an adapter that has to merge them can do so knowingly.
    Merging at the contract level would throw the distinction away before any adapter could use it.
    """

    SYSTEM = "system"
    DEVELOPER = "developer"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class FinishReason(StrEnum):
    """Why generation stopped, in our vocabulary rather than a provider's."""

    STOP = "STOP"
    LENGTH = "LENGTH"
    TOOL_CALLS = "TOOL_CALLS"
    CONTENT_FILTER = "CONTENT_FILTER"
    ERROR = "ERROR"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"


class Endpoint(StrEnum):
    """A wire protocol a provider may expose.

    These are protocol families, not URLs. Which path a family lives at is provider configuration;
    which family a model accepts is catalog metadata.
    """

    OPENAI_CHAT_COMPLETIONS = "openai-chat-completions"
    OPENAI_RESPONSES = "openai-responses"
    ANTHROPIC_MESSAGES = "anthropic-messages"


class Capability(StrEnum):
    """A capability routing is allowed to require of a model."""

    STREAMING = "streaming"
    TOOLS = "tools"
    VISION = "vision"
    STRUCTURED_OUTPUT = "structured-output"
    REASONING = "reasoning"


class CapabilityState(StrEnum):
    """Whether a model supports a capability, does not, or has never told us.

    ``UNKNOWN`` is a first-class answer. The routing policy decides what to do with it; the catalog
    never decides on the policy's behalf by guessing.
    """

    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


class CapabilityProvenance(StrEnum):
    """Where a capability statement came from.

    A capability with no provenance is an opinion. ``INFERRED_FROM_NAME`` is deliberately absent:
    "the identifier contains 'vision', therefore it sees" is a guess dressed as metadata, and the
    catalog refuses to record it.
    """

    PROVIDER_METADATA = "PROVIDER_METADATA"
    MANUAL_CONFIGURATION = "MANUAL_CONFIGURATION"
    OBSERVED = "OBSERVED"
    UNKNOWN = "UNKNOWN"


class ReasoningEffort(StrEnum):
    """How much deliberation a request asks for, when the model exposes the control at all."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAX = "max"


class RouteReason(StrEnum):
    """Why the router chose what it chose. Short, structured, and auditable.

    This is a decision summary, not a chain of thought. `docs/GATE-1-CHECKLIST.md` row 7.9 asks for
    something a human can verify against the catalog and the policy; a narrative would be neither
    verifiable nor ours to store.
    """

    EXPLICIT_MODEL = "EXPLICIT_MODEL"
    DEFAULT_MODEL = "DEFAULT_MODEL"
    ROUTE_ALIAS = "ROUTE_ALIAS"
    CAPABILITY_FILTER = "CAPABILITY_FILTER"
    CONTEXT_FILTER = "CONTEXT_FILTER"
    PROVIDER_PRIORITY = "PROVIDER_PRIORITY"
    FALLBACK = "FALLBACK"


class ToolDefinition(BaseModel):
    """A tool the caller is willing for the model to ask for.

    The gateway passes it to the provider and normalizes any request that comes back. It never
    executes anything: deciding whether a tool call may run is Gate 2's contract and running it is
    Gate 3's sandbox.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=4096)
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema of the arguments, as the caller declared it.")


class ToolCall(BaseModel):
    """A tool invocation the model asked for, normalized.

    ``arguments`` is the parsed object. ``arguments_valid`` records whether parsing succeeded: a
    model that emits malformed JSON is a real and frequent event, and a contract that could only
    represent well-formed calls would force the adapter to either throw the call away or invent one.
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1, max_length=256)
    name: str = Field(min_length=1, max_length=128)
    arguments: dict[str, Any] = Field(default_factory=dict)
    arguments_valid: bool = True
    invalid_reason: str | None = None

    @model_validator(mode="after")
    def _invalid_calls_explain_themselves(self) -> ToolCall:
        if not self.arguments_valid and not self.invalid_reason:
            raise ValueError("an invalid tool call must record why it is invalid")
        return self


class ToolCallDelta(BaseModel):
    """A fragment of a tool call, as it arrives on a stream.

    Providers stream tool calls in pieces: an index and an identifier first, then the name, then the
    arguments a few characters at a time. A fragment is therefore *not* a :class:`ToolCall` — its
    arguments are usually not parseable JSON yet — and giving it its own type is what stops a
    half-arrived call from being emitted as though it were complete. The assembled calls arrive on
    the ``END`` event, once there is something whole to assemble.
    """

    model_config = ConfigDict(frozen=True)

    index: int = Field(ge=0)
    id: str | None = None
    name: str | None = None
    arguments_fragment: str = ""


class GatewayMessage(BaseModel):
    """One turn of the conversation, in roles no provider owns."""

    model_config = ConfigDict(frozen=True)

    role: MessageRole
    content: str = ""
    name: str | None = Field(default=None, max_length=128)
    tool_call_id: str | None = Field(
        default=None, max_length=256,
        description="Set on a TOOL message: which call this message answers.")
    tool_calls: tuple[ToolCall, ...] = ()

    @model_validator(mode="after")
    def _tool_messages_answer_a_call(self) -> GatewayMessage:
        if self.role is MessageRole.TOOL and not self.tool_call_id:
            raise ValueError("a tool message must name the tool call it answers")
        if self.role is not MessageRole.ASSISTANT and self.tool_calls:
            raise ValueError("only an assistant message may carry tool calls")
        if self.role is not MessageRole.TOOL and not self.content and not self.tool_calls:
            raise ValueError(f"a {self.role} message must carry content")
        return self


class ResponseFormat(BaseModel):
    """A structured-output request.

    A schema is required. "Give me JSON" without a schema is a formatting preference that every
    provider spells differently and none of them guarantees, and the router would have no capability
    to check it against.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=128)
    json_schema: dict[str, Any]
    strict: bool = True

    @field_validator("json_schema")
    @classmethod
    def _schema_is_an_object(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("a structured output request must carry a JSON Schema")
        if value.get("type") not in (None, "object"):
            raise ValueError("the top level of a response schema must be an object")
        return value


class ModelRef(BaseModel):
    """How a model is named without ambiguity.

    Two providers may expose the same identifier. ``openai/gpt-x`` from provider A and from provider
    B are different models with different prices, different availability and different behaviour, so
    identity is the pair and never the bare identifier.
    """

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    provider_id: str = Field(min_length=1, max_length=128)
    model_id: str = Field(min_length=1, max_length=256)

    @property
    def qualified(self) -> str:
        return f"{self.provider_id}:{self.model_id}"

    @classmethod
    def parse(cls, value: str) -> ModelRef:
        """Read ``provider:model``; a bare identifier is refused rather than guessed at."""
        provider, separator, model = value.partition(":")
        if not separator or not provider or not model:
            raise ValueError(
                "a model reference is 'provider:model'; a bare model identifier is ambiguous "
                "because two providers may expose the same one")
        return cls(provider_id=provider, model_id=model)


class ModelDescriptor(BaseModel):
    """One model as the catalog knows it, after normalization.

    Every field a provider did not supply is ``None`` or ``UNKNOWN``. Nothing here is defaulted into
    a confident value, because the router reads this object to decide what a model can do.
    """

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    ref: ModelRef
    display_name: str
    family: str | None = None
    context_window: int | None = Field(default=None, ge=1)
    max_output_tokens: int | None = Field(default=None, ge=1)
    supported_endpoints: tuple[Endpoint, ...] = ()
    capabilities: dict[Capability, CapabilityState] = Field(default_factory=dict)
    capability_provenance: dict[Capability, CapabilityProvenance] = Field(default_factory=dict)
    reasoning_levels: tuple[ReasoningEffort, ...] = ()
    active: bool = True
    raw_metadata: dict[str, Any] = Field(default_factory=dict)
    synced_at: datetime | None = None

    def capability(self, capability: Capability) -> CapabilityState:
        """What we know about one capability, which may be that we know nothing."""
        return self.capabilities.get(capability, CapabilityState.UNKNOWN)

    def provenance(self, capability: Capability) -> CapabilityProvenance:
        return self.capability_provenance.get(capability, CapabilityProvenance.UNKNOWN)

    def supports_endpoint(self, endpoint: Endpoint) -> bool:
        return endpoint in self.supported_endpoints


class TokenEstimate(BaseModel):
    """A token count, and whether it is a measurement or an estimate.

    The distinction is the whole point. A provider that returns usage has counted; a preflight that
    divides characters by four has guessed. Reporting the guess as a count is how a context-window
    check becomes a superstition.
    """

    model_config = ConfigDict(frozen=True)

    tokens: int = Field(ge=0)
    exact: bool
    method: str = Field(
        description="How the number was obtained, for example 'provider-usage' or 'heuristic'.")


class Usage(BaseModel):
    """What a call consumed, as far as the provider reported it.

    Every field is optional and stays ``None`` when the provider said nothing. ``total_tokens`` is
    reported when the provider reports it and derived only when both halves are present, because a
    total derived from one half is a different number wearing the same name.
    """

    model_config = ConfigDict(frozen=True)

    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    cached_input_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _derive_total_only_when_both_halves_exist(self) -> Usage:
        if self.total_tokens is None and self.input_tokens is not None \
                and self.output_tokens is not None:
            object.__setattr__(self, "total_tokens", self.input_tokens + self.output_tokens)
        return self

    @property
    def empty(self) -> bool:
        return all(value is None for value in self.model_dump().values())


class RouteAttempt(BaseModel):
    """One candidate the router tried, and what happened to it."""

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    ref: ModelRef
    endpoint: Endpoint | None = None
    attempt: int = Field(ge=1)
    outcome: str = Field(description="SUCCEEDED, FAILED or SKIPPED.")
    error_type: str | None = None
    retries: int = Field(default=0, ge=0)
    latency_ms: float | None = Field(default=None, ge=0)


class RouteDecision(BaseModel):
    """Why the gateway called what it called, in a form an operator can check.

    ``considered`` is a count rather than a list of everything in the catalog: an explanation that
    grows with the catalog stops being read.
    """

    model_config = ConfigDict(frozen=True)

    reason: RouteReason
    route: str | None = None
    considered: int = Field(default=0, ge=0)
    rejected: tuple[str, ...] = ()
    chain: tuple[RouteAttempt, ...] = ()

    @property
    def fallback_count(self) -> int:
        """How many times the gateway moved on to a different candidate."""
        return max(len(self.chain) - 1, 0)


class GatewayRequest(BaseModel):
    """One inference request, in the only shape the gateway accepts.

    There is deliberately no field for a base URL, an API key, a header or an organization: an
    address that a request can supply is an address an attacker can supply, and a gateway that
    forwards a caller's credential is a credential proxy. Both come from administrative
    configuration and from nowhere else.
    """

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    request_id: str = Field(min_length=1, max_length=128)
    messages: tuple[GatewayMessage, ...]
    route: str | None = Field(
        default=None, max_length=64,
        description="A configured route alias. Mutually exclusive with an explicit model.")
    model: str | None = Field(
        default=None, max_length=384,
        description="An explicit 'provider:model' reference, when the caller has chosen.")
    required_capabilities: tuple[Capability, ...] = ()
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, gt=0.0, le=1.0)
    max_output_tokens: int | None = Field(default=None, ge=1)
    reasoning_effort: ReasoningEffort | None = None
    stream: bool = False
    tools: tuple[ToolDefinition, ...] = ()
    response_format: ResponseFormat | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("messages")
    @classmethod
    def _at_least_one_message(cls, value: tuple[GatewayMessage, ...]) -> tuple[GatewayMessage, ...]:
        if not value:
            raise ValueError("a request must carry at least one message")
        return value

    @field_validator("tools")
    @classmethod
    def _tool_names_are_unique(cls, value: tuple[ToolDefinition, ...]
                               ) -> tuple[ToolDefinition, ...]:
        names = [tool.name for tool in value]
        if len(names) != len(set(names)):
            raise ValueError("two tools share a name; the model could not tell them apart")
        return value

    @model_validator(mode="after")
    def _route_and_model_are_exclusive(self) -> GatewayRequest:
        if self.route and self.model:
            raise ValueError(
                "a request names a route or a model, never both; two routing intents in one "
                "request have no defined precedence")
        if self.model:
            ModelRef.parse(self.model)
        return self

    @property
    def implied_capabilities(self) -> tuple[Capability, ...]:
        """What the request needs whether or not the caller thought to ask for it.

        A caller that supplies tools needs a model that accepts tools. Making them declare it twice
        would mean that forgetting the declaration sends the request to a model that cannot serve
        it — the failure arriving from the provider instead of from the router.
        """
        implied = set(self.required_capabilities)
        if self.stream:
            implied.add(Capability.STREAMING)
        if self.tools:
            implied.add(Capability.TOOLS)
        if self.response_format is not None:
            implied.add(Capability.STRUCTURED_OUTPUT)
        if self.reasoning_effort is not None:
            implied.add(Capability.REASONING)
        return tuple(sorted(implied, key=str))


class GatewayResponse(BaseModel):
    """The answer, normalized.

    The provider's own payload is not here. It is available to the adapter that produced this
    object and to nothing above it: a consumer that reads a raw field is a consumer coupled to one
    provider's release notes.
    """

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    contract_version: str = CONTRACT_VERSION
    request_id: str
    ref: ModelRef
    endpoint: Endpoint
    content: str = ""
    tool_calls: tuple[ToolCall, ...] = ()
    finish_reason: FinishReason = FinishReason.UNKNOWN
    usage: Usage = Field(default_factory=Usage)
    latency_ms: float = Field(ge=0)
    route: RouteDecision
    cost: float | None = Field(
        default=None,
        description="Absent unless pricing is configured. Zero would mean the call was free.")
    metadata: dict[str, str] = Field(default_factory=dict)


class StreamEventType(StrEnum):
    """The kinds of event a normalized stream can carry."""

    START = "start"
    TEXT_DELTA = "text_delta"
    TOOL_CALL_DELTA = "tool_call_delta"
    USAGE = "usage"
    END = "end"
    ERROR = "error"


class StreamEvent(BaseModel):
    """One event of a normalized stream.

    A single envelope rather than six classes: this crosses an HTTP boundary as Server-Sent Events,
    and a union that has to be re-discriminated on the other side is a union that will be
    re-discriminated wrongly.
    """

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    type: StreamEventType
    request_id: str
    sequence: int = Field(ge=0)
    text: str | None = None
    tool_call_delta: ToolCallDelta | None = None
    tool_calls: tuple[ToolCall, ...] = ()
    usage: Usage | None = None
    finish_reason: FinishReason | None = None
    ref: ModelRef | None = None
    endpoint: Endpoint | None = None
    route: RouteDecision | None = None
    error: dict[str, Any] | None = None
    latency_ms: float | None = Field(default=None, ge=0)

    def to_sse(self) -> str:
        """Render the event as one Server-Sent Event frame.

        The event name is on the frame as well as inside the payload. A browser subscribing to a
        named event should not have to parse the body to find out which event it received.
        """
        body = json.dumps(self.model_dump(mode="json", exclude_none=True), ensure_ascii=False)
        return f"event: {self.type}\ndata: {body}\n\n"
