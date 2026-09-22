"""Turning a provider's description of a model into the catalog's description of it.

The single rule this module exists to hold: **a capability is recorded only when the provider said
something about it.** Everything else is ``UNKNOWN``, and ``UNKNOWN`` survives all the way to the
router, which has a policy for it.

Two tempting shortcuts are refused explicitly.

*Defaulting to false.* A provider that lists a model with nothing but an identifier — which is what
most ``/models`` answers are — has not told us that the model cannot use tools. Recording
``UNSUPPORTED`` would be the catalog inventing a fact, and the router would then quietly exclude
every model the provider happens to describe tersely.

*Reading the name.* ``…-vision-…`` in an identifier is a naming convention, not metadata. The
project has a lesson about controls that decide behaviour from a literal, and a capability derived
from a substring is the same defect with a friendlier face. :class:`CapabilityProvenance` has no
member for it, so the code cannot express the claim even if someone wanted to.

The recognized keys below are a union of the shapes seen across OpenAI-compatible providers and
aggregators. An unrecognized key is not an error: it is kept verbatim in ``raw_metadata``, where a
later Gate can read it without this function having to guess at its meaning today.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from iacode_model_gateway.contracts import (
    Capability,
    CapabilityProvenance,
    CapabilityState,
    Endpoint,
    ModelDescriptor,
    ModelRef,
    ReasoningEffort,
)

__all__ = ["CapabilityOverride", "normalise_model", "normalise_models"]

# Where a context window may be declared.
_CONTEXT_KEYS = ("context_window", "context_length", "max_context_tokens", "max_input_tokens",
                 "context_size")
# Where an output cap may be declared.
_OUTPUT_KEYS = ("max_output_tokens", "max_completion_tokens", "max_tokens", "output_token_limit")
# Where a human-readable name may be declared.
_NAME_KEYS = ("display_name", "name", "label")
# Where a family may be declared.
_FAMILY_KEYS = ("family", "owned_by", "organization", "vendor", "publisher")
# Where the protocol families may be declared.
_ENDPOINT_KEYS = ("supported_endpoints", "endpoints", "supported_protocols", "protocols")
# Where a flat list of supported parameters or features may be declared.
_FEATURE_LIST_KEYS = ("supported_parameters", "supported_features", "features", "capabilities")
# Where reasoning levels may be declared.
_REASONING_LEVEL_KEYS = ("supported_reasoning_efforts", "reasoning_efforts", "reasoning_levels")

# Tokens that, inside a declared feature list, name one of our capabilities. A provider that lists
# its features is making a statement; matching it is reading that statement, not guessing.
_FEATURE_TOKENS: dict[Capability, tuple[str, ...]] = {
    Capability.TOOLS: ("tools", "tool_use", "tool_choice", "function_calling", "functions"),
    Capability.VISION: ("vision", "image_input", "images", "multimodal_input"),
    Capability.STRUCTURED_OUTPUT: ("structured_outputs", "structured_output", "response_format",
                                   "json_schema"),
    Capability.STREAMING: ("stream", "streaming"),
    Capability.REASONING: ("reasoning", "reasoning_effort", "thinking", "include_reasoning"),
}

# Boolean keys that state one capability directly.
_BOOLEAN_KEYS: dict[Capability, tuple[str, ...]] = {
    Capability.TOOLS: ("supports_tools", "tool_use", "function_calling", "supports_functions"),
    Capability.VISION: ("supports_vision", "vision", "multimodal"),
    Capability.STRUCTURED_OUTPUT: ("supports_structured_output", "structured_output",
                                   "json_schema", "supports_response_schema"),
    Capability.STREAMING: ("supports_streaming", "streaming", "stream"),
    Capability.REASONING: ("supports_reasoning", "reasoning", "thinking"),
}

_ENDPOINT_ALIASES: dict[str, Endpoint] = {
    "openai-chat-completions": Endpoint.OPENAI_CHAT_COMPLETIONS,
    "chat.completions": Endpoint.OPENAI_CHAT_COMPLETIONS,
    "chat_completions": Endpoint.OPENAI_CHAT_COMPLETIONS,
    "chat": Endpoint.OPENAI_CHAT_COMPLETIONS,
    "/chat/completions": Endpoint.OPENAI_CHAT_COMPLETIONS,
    "/v1/chat/completions": Endpoint.OPENAI_CHAT_COMPLETIONS,
    "openai-responses": Endpoint.OPENAI_RESPONSES,
    "responses": Endpoint.OPENAI_RESPONSES,
    "/responses": Endpoint.OPENAI_RESPONSES,
    "/v1/responses": Endpoint.OPENAI_RESPONSES,
    "anthropic-messages": Endpoint.ANTHROPIC_MESSAGES,
    "messages": Endpoint.ANTHROPIC_MESSAGES,
    "/v1/messages": Endpoint.ANTHROPIC_MESSAGES,
}


class CapabilityOverride:
    """A capability an administrator states about a model the provider is silent about.

    It exists so a locally-hosted runtime whose ``/models`` answer carries nothing can still be
    routed to, without the normalizer inventing anything. The provenance of such a statement is
    ``MANUAL_CONFIGURATION``, which is visible in the catalog and in the API, so nobody mistakes an
    administrator's claim for the provider's.
    """

    def __init__(self, model_id: str, capabilities: dict[Capability, CapabilityState]) -> None:
        self.model_id = model_id
        self.capabilities = dict(capabilities)


def _first(payload: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = int(value)
    return number if number > 0 else None


def _nested(payload: dict[str, Any]) -> dict[str, Any]:
    """A flattened view of the one-level-deep objects providers nest metadata in.

    ``architecture``, ``top_provider`` and ``limits`` are the common ones. Flattening is preferred
    to naming each path, because the alternative is one lookup chain per provider shape, and that is
    exactly the provider-specific knowledge this layer exists to keep out of the code above it.
    """
    flat: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, dict):
            for inner_key, inner_value in value.items():
                flat.setdefault(inner_key, inner_value)
        flat.setdefault(key, value)
    return flat


def _endpoints(payload: dict[str, Any]) -> tuple[Endpoint, ...]:
    declared = _first(payload, _ENDPOINT_KEYS)
    if isinstance(declared, str):
        declared = [declared]
    if not isinstance(declared, list):
        return ()
    found: list[Endpoint] = []
    for item in declared:
        if not isinstance(item, str):
            continue
        endpoint = _ENDPOINT_ALIASES.get(item.strip().lower())
        if endpoint is not None and endpoint not in found:
            found.append(endpoint)
    return tuple(found)


def _feature_tokens(payload: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    for key in _FEATURE_LIST_KEYS:
        value = payload.get(key)
        if isinstance(value, list):
            tokens |= {str(item).strip().lower() for item in value if isinstance(item, str)}
        elif isinstance(value, dict):
            tokens |= {str(name).strip().lower() for name, flag in value.items() if flag is True}
    modalities = payload.get("input_modalities") or payload.get("modalities")
    if isinstance(modalities, list):
        tokens |= {str(item).strip().lower() for item in modalities if isinstance(item, str)}
    return tokens


def _capabilities(payload: dict[str, Any]) -> tuple[dict[Capability, CapabilityState],
                                                    dict[Capability, CapabilityProvenance]]:
    states: dict[Capability, CapabilityState] = {}
    provenance: dict[Capability, CapabilityProvenance] = {}
    tokens = _feature_tokens(payload)

    for capability, keys in _BOOLEAN_KEYS.items():
        for key in keys:
            value = payload.get(key)
            if isinstance(value, bool):
                states[capability] = (CapabilityState.SUPPORTED if value
                                      else CapabilityState.UNSUPPORTED)
                provenance[capability] = CapabilityProvenance.PROVIDER_METADATA
                break

    if tokens:
        for capability, names in _FEATURE_TOKENS.items():
            if capability in states:
                continue
            if any(name in tokens for name in names):
                states[capability] = CapabilityState.SUPPORTED
                provenance[capability] = CapabilityProvenance.PROVIDER_METADATA
        if Capability.VISION not in states and "image" in tokens:
            states[Capability.VISION] = CapabilityState.SUPPORTED
            provenance[Capability.VISION] = CapabilityProvenance.PROVIDER_METADATA

    # A declared feature list is a *complete* statement of what the model supports, so a capability
    # absent from it is unsupported rather than unknown. A boolean map is not: it states only what
    # it names.
    if any(isinstance(payload.get(key), list) for key in _FEATURE_LIST_KEYS):
        for capability in Capability:
            if capability not in states:
                states[capability] = CapabilityState.UNSUPPORTED
                provenance[capability] = CapabilityProvenance.PROVIDER_METADATA

    return states, provenance


def _reasoning_levels(payload: dict[str, Any]) -> tuple[ReasoningEffort, ...]:
    declared = _first(payload, _REASONING_LEVEL_KEYS)
    if not isinstance(declared, list):
        return ()
    levels: list[ReasoningEffort] = []
    for item in declared:
        if not isinstance(item, str):
            continue
        try:
            effort = ReasoningEffort(item.strip().lower())
        except ValueError:
            continue
        if effort not in levels:
            levels.append(effort)
    return tuple(levels)


def _active(payload: dict[str, Any]) -> bool:
    """Whether the provider says the model is usable right now.

    Absent means usable: the model is in the discovery answer, which is the provider stating that it
    exists. Only an explicit negative deactivates it.
    """
    for key in ("active", "available", "enabled"):
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    status = payload.get("status")
    if isinstance(status, str):
        return status.strip().lower() in ("", "active", "available", "ready", "ok", "live")
    return True


def normalise_model(provider_id: str, model_id: str, payload: dict[str, Any], *,
                    synced_at: datetime,
                    overrides: dict[str, dict[Capability, CapabilityState]] | None = None,
                    provider_capabilities: dict[Capability, CapabilityState] | None = None,
                    provider_endpoints: tuple[Endpoint, ...] = (),
                    provider_reasoning_levels: tuple[ReasoningEffort, ...] = ()
                    ) -> ModelDescriptor:
    """Normalize one provider model record.

    ``provider_capabilities``, ``provider_endpoints`` and ``provider_reasoning_levels`` are the
    administrator's statements about the provider as a whole — "everything this endpoint serves
    streams", which is a property of the protocol rather than a guess about a model. They apply only
    where the model itself said nothing, they never overrule the provider's own metadata, and they
    are recorded with ``MANUAL_CONFIGURATION`` provenance so the two sources stay distinguishable in
    the catalog and in the API. A per-model ``override`` is the same kind of statement, narrower,
    and it is applied last because it is the most specific.
    """
    flat = _nested(payload)
    states, provenance = _capabilities(flat)

    for capability, state in (provider_capabilities or {}).items():
        if states.get(capability, CapabilityState.UNKNOWN) is not CapabilityState.UNKNOWN:
            continue
        states[capability] = state
        provenance[capability] = CapabilityProvenance.MANUAL_CONFIGURATION

    for capability, state in (overrides or {}).get(model_id, {}).items():
        states[capability] = state
        provenance[capability] = CapabilityProvenance.MANUAL_CONFIGURATION

    endpoints = _endpoints(flat) or provider_endpoints
    levels = _reasoning_levels(flat) or provider_reasoning_levels

    display = _first(flat, _NAME_KEYS)
    family = _first(flat, _FAMILY_KEYS)

    return ModelDescriptor(
        ref=ModelRef(provider_id=provider_id, model_id=model_id),
        display_name=str(display).strip() if isinstance(display, str) and display.strip()
        else model_id,
        family=str(family).strip() if isinstance(family, str) and family.strip() else None,
        context_window=_positive_int(_first(flat, _CONTEXT_KEYS)),
        max_output_tokens=_positive_int(_first(flat, _OUTPUT_KEYS)),
        supported_endpoints=endpoints,
        capabilities=states,
        capability_provenance=provenance,
        reasoning_levels=levels,
        active=_active(flat),
        raw_metadata=dict(payload),
        synced_at=synced_at,
    )


def normalise_models(provider_id: str, raw: Iterable[tuple[str, dict[str, Any]]], *,
                     synced_at: datetime,
                     overrides: dict[str, dict[Capability, CapabilityState]] | None = None,
                     provider_capabilities: dict[Capability, CapabilityState] | None = None,
                     provider_endpoints: tuple[Endpoint, ...] = (),
                     provider_reasoning_levels: tuple[ReasoningEffort, ...] = ()
                     ) -> list[ModelDescriptor]:
    """Normalize a whole discovery answer, refusing a duplicate identifier.

    A provider that lists one identifier twice has produced an answer we cannot apply: the second
    record would silently overwrite the first, and which of the two survived would depend on
    iteration order. Refusing is what keeps the previous catalog in place instead.
    """
    seen: set[str] = set()
    models: list[ModelDescriptor] = []
    for model_id, payload in raw:
        if model_id in seen:
            raise ValueError(
                f"the discovery answer lists {model_id!r} more than once; applying it would make "
                f"the surviving record depend on iteration order")
        seen.add(model_id)
        models.append(normalise_model(
            provider_id, model_id, payload, synced_at=synced_at, overrides=overrides,
            provider_capabilities=provider_capabilities,
            provider_endpoints=provider_endpoints,
            provider_reasoning_levels=provider_reasoning_levels))
    return models
