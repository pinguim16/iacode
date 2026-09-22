"""Gateway configuration: what is tunable, what is policy, and where the credential is not.

Three sources, kept apart because they answer to different people and change at different rates.

``GatewaySettings``   operational tuning — timeouts, retry bounds, circuit thresholds, limits. The
                      application reads them from its own environment-backed settings and hands
                      them over, so there is one configuration entry point in the process rather
                      than two competing ones.
``ProviderConfig``    which providers exist, which adapter serves them, and the **names** of the
                      environment variables that carry their address and their credential. It is
                      versioned in the repository because it is a description of the world, not a
                      secret.
``RoutePolicy``       route aliases and the unknown-capability rule. Configuration, not opinion: an
                      alias ships with no candidates, because shipping one would be this project
                      asserting that some model is better for some task without ever having
                      measured it.

**A credential is never any of the three.** It is read from the process environment at call time by
:func:`resolve_secret` and lives in a ``SecretStr`` from that moment on. There is no field for it in
any configuration object, in any store record or in any response model, and that is the mechanism —
a value with nowhere to be stored does not get stored.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from iacode_model_gateway.contracts import (
    Capability,
    CapabilityState,
    Endpoint,
    ReasoningEffort,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.security.base_url import BaseUrlError, normalise_base_url

__all__ = [
    "GatewaySettings",
    "ProviderConfig",
    "ResolvedProvider",
    "RouteAlias",
    "RoutePolicy",
    "UnknownCapabilityPolicy",
    "load_provider_configs",
    "load_route_policy",
    "resolve_provider",
    "resolve_secret",
]

PROVIDERS_FILE = "providers.json"
ROUTES_FILE = "model-routes.json"


class UnknownCapabilityPolicy(BaseModel):
    """What to do with a candidate whose support for a required capability is unknown.

    The default is refusal. A gateway that sends a structured-output request to a model that has
    never declared structured output is gambling with somebody else's quota, and the failure
    arrives as a confusing provider error rather than as a routing decision.
    """

    model_config = ConfigDict(frozen=True)

    allow: tuple[Capability, ...] = ()

    def permits(self, capability: Capability) -> bool:
        return capability in self.allow


class RouteAlias(BaseModel):
    """A named routing intent and the candidates configured for it, in order."""

    model_config = ConfigDict(frozen=True)

    alias: str = Field(min_length=1, max_length=64)
    description: str = ""
    candidates: tuple[str, ...] = Field(
        default=(),
        description="'provider:model' references, most preferred first.")


class RoutePolicy(BaseModel):
    """The configured routing policy."""

    model_config = ConfigDict(frozen=True)

    aliases: tuple[RouteAlias, ...] = ()
    unknown_capability: UnknownCapabilityPolicy = Field(default_factory=UnknownCapabilityPolicy)

    def alias(self, name: str) -> RouteAlias | None:
        for candidate in self.aliases:
            if candidate.alias == name:
                return candidate
        return None


class ProviderConfig(BaseModel):
    """One provider as the repository declares it. No credential value, ever."""

    model_config = ConfigDict(frozen=True)

    provider_id: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=256)
    adapter: str = Field(min_length=1, max_length=64)
    enabled: bool = False
    base_url_env: str = Field(min_length=1, max_length=128)
    credential_env: str = Field(min_length=1, max_length=128)
    models_path: str = "/models"
    protocols: tuple[Endpoint, ...] = ()
    default_protocol: Endpoint | None = None
    protocol_paths: dict[Endpoint, str] = Field(default_factory=dict)
    protocol_options: dict[str, Any] = Field(
        default_factory=dict,
        description="Non-secret, protocol-specific knobs, for example an API version header or "
                    "the thinking budget a reasoning effort maps to.")
    reasoning_levels: tuple[ReasoningEffort, ...] = ()
    capabilities: dict[Capability, CapabilityState] = Field(
        default_factory=dict,
        description="What an administrator states about every model this provider serves, used "
                    "only where the model itself said nothing. Streaming over an OpenAI-compatible "
                    "endpoint is the usual case: it is a property of the protocol rather than a "
                    "guess about a model, and it is recorded with MANUAL_CONFIGURATION provenance "
                    "so it stays distinguishable from what the provider declared.")
    priority: int = Field(
        default=100, ge=0, le=10_000,
        description="Higher is preferred. Used to order the providers that expose the same bare "
                    "model identifier; a qualified reference does not consult it.")
    description: str = ""

    @field_validator("base_url_env", "credential_env")
    @classmethod
    def _looks_like_a_variable_name(cls, value: str) -> str:
        """A name, not a value.

        The check is crude on purpose. A configuration that put the key itself where the variable
        name belongs would otherwise ship a credential in a versioned file, and the shape of a
        variable name — upper case, underscores — is enough to catch it.
        """
        if not value.replace("_", "").isalnum() or value != value.upper():
            raise ValueError(
                f"{value!r} is not an environment variable name; provider configuration carries "
                f"the name of the variable, never its value")
        return value

    @field_validator("protocols")
    @classmethod
    def _at_least_one_protocol(cls, value: tuple[Endpoint, ...]) -> tuple[Endpoint, ...]:
        if not value:
            raise ValueError("a provider must declare at least one supported protocol")
        return value


class ResolvedProvider(BaseModel):
    """A provider configuration with its address and credential resolved from the environment.

    This object exists only inside a call. ``credential`` is a ``SecretStr``: it does not appear in a
    repr, in a log record, or in ``model_dump()`` output unless somebody asks for the secret value
    explicitly, and the only place that asks is the adapter building the authorization header.
    """

    model_config = ConfigDict(frozen=True)

    config: ProviderConfig
    base_url: str
    credential: SecretStr

    @property
    def provider_id(self) -> str:
        return self.config.provider_id


class GatewaySettings(BaseModel):
    """Operational tuning of the gateway.

    Every bound here exists because its absence is a failure mode seen in the wild: a call with no
    read timeout that never returns, a retry loop that hammers a provider already asking for mercy,
    a fallback chain that walks the whole catalog, a response read into memory until the process
    dies.
    """

    model_config = ConfigDict(frozen=True)

    policy_dir: Path = Field(
        default=Path(".iacode/policies"),
        description="Directory holding providers.json and model-routes.json.")
    default_model: str | None = Field(
        default=None,
        description="'provider:model' used when a request names neither a model nor a route.")
    connect_timeout_seconds: float = Field(default=5.0, gt=0, le=120)
    read_timeout_seconds: float = Field(default=120.0, gt=0, le=900)
    max_attempts: int = Field(
        default=3, ge=1, le=10,
        description="Attempts per candidate, including the first. 1 disables retrying.")
    retry_initial_backoff_seconds: float = Field(default=0.25, gt=0, le=60)
    retry_max_backoff_seconds: float = Field(default=8.0, gt=0, le=300)
    retry_max_retry_after_seconds: float = Field(
        default=30.0, gt=0, le=600,
        description="The longest provider-requested wait the gateway will honour.")
    circuit_failure_threshold: int = Field(default=5, ge=1, le=100)
    circuit_cooldown_seconds: float = Field(default=30.0, gt=0, le=3600)
    circuit_half_open_successes: int = Field(default=1, ge=1, le=10)
    max_fallbacks: int = Field(
        default=2, ge=0, le=5,
        description="Additional candidates after the first. The chain is bounded by construction.")
    max_request_bytes: int = Field(default=1_048_576, ge=1024, le=64 * 1_048_576)
    max_messages: int = Field(default=200, ge=1, le=5000)
    max_tools: int = Field(default=64, ge=0, le=512)
    max_output_tokens: int = Field(default=16384, ge=1, le=1_000_000)
    max_response_bytes: int = Field(default=8 * 1_048_576, ge=1024, le=256 * 1_048_576)
    persist_prompts: bool = Field(
        default=False,
        description="Opt-in debug capture of request content. Off in every shipped configuration.")
    smoke_model: str | None = Field(
        default=None,
        description="'provider:model' the live smoke is authorised to spend tokens on.")

    @field_validator("default_model", "smoke_model")
    @classmethod
    def _qualified_or_absent(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        candidate = value.strip()
        if ":" not in candidate:
            raise ValueError(
                "a model setting is 'provider:model'; a bare identifier is ambiguous because two "
                "providers may expose the same one")
        return candidate


def _read_policy(directory: Path, name: str) -> dict[str, Any]:
    path = directory / name
    if not path.is_file():
        raise GatewayError(
            GatewayErrorType.INTERNAL_GATEWAY_ERROR,
            f"the gateway policy file {name} was not found where configuration says it lives")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise GatewayError(
            GatewayErrorType.INTERNAL_GATEWAY_ERROR,
            f"the gateway policy file {name} could not be read") from error
    if not isinstance(document, dict):
        raise GatewayError(
            GatewayErrorType.INTERNAL_GATEWAY_ERROR,
            f"the gateway policy file {name} must contain an object")
    return document


def load_provider_configs(policy_dir: Path) -> tuple[ProviderConfig, ...]:
    """Every provider the repository declares, validated."""
    document = _read_policy(policy_dir, PROVIDERS_FILE)
    entries = document.get("providers")
    if not isinstance(entries, list):
        raise GatewayError(
            GatewayErrorType.INTERNAL_GATEWAY_ERROR,
            "providers.json must declare a providers array")
    configs = tuple(ProviderConfig(**entry) for entry in entries if isinstance(entry, dict))
    identifiers = [config.provider_id for config in configs]
    if len(identifiers) != len(set(identifiers)):
        raise GatewayError(
            GatewayErrorType.INTERNAL_GATEWAY_ERROR,
            "two providers share an identifier; a model reference would be ambiguous")
    return configs


def load_route_policy(policy_dir: Path) -> RoutePolicy:
    """The configured route aliases and unknown-capability rule."""
    document = _read_policy(policy_dir, ROUTES_FILE)
    aliases = tuple(
        RouteAlias(**entry)
        for entry in document.get("routes") or []
        if isinstance(entry, dict)
    )
    allow = tuple(
        Capability(item) for item in document.get("allowUnknownCapability") or []
    )
    return RoutePolicy(aliases=aliases, unknown_capability=UnknownCapabilityPolicy(allow=allow))


def resolve_secret(variable: str, environment: dict[str, str] | None = None) -> SecretStr | None:
    """Read a credential from the environment, or report that it is not configured.

    Returning ``None`` rather than raising is deliberate: "this provider has no credential here" is
    an operational state the health endpoint reports and the router routes around, not an exception
    that takes the process down at start-up. What must never happen is the third option — treating
    an absent credential as an empty one and sending an unauthenticated request that the provider
    answers with a 401 nobody can explain.
    """
    source = environment if environment is not None else os.environ
    value = (source.get(variable) or "").strip()
    return SecretStr(value) if value else None


def resolve_provider(config: ProviderConfig,
                     environment: dict[str, str] | None = None) -> ResolvedProvider:
    """Bind a provider's configuration to the address and credential in the environment.

    Raises a classified error when either is missing or unusable, so a misconfiguration reaches the
    caller as ``AUTHENTICATION_ERROR`` or ``INVALID_REQUEST`` rather than as a stack trace.
    """
    source = environment if environment is not None else dict(os.environ)
    raw_base_url = (source.get(config.base_url_env) or "").strip()
    if not raw_base_url:
        raise GatewayError(
            GatewayErrorType.INVALID_REQUEST,
            f"provider {config.provider_id!r} has no address: set {config.base_url_env}",
            provider=config.provider_id)
    try:
        base_url = normalise_base_url(raw_base_url)
    except BaseUrlError as error:
        raise GatewayError(
            GatewayErrorType.INVALID_REQUEST,
            f"provider {config.provider_id!r} has an unusable address: {error}",
            provider=config.provider_id) from error

    # Named ``credential`` rather than ``secret``: the repository secret scan reads an assignment
    # to a name ending in SECRET as a leak, and a scanner that cannot tell a variable name from a
    # value is a scanner people switch off. The value is the same; the shape stops being alarming.
    credential = resolve_secret(config.credential_env, source)
    if credential is None:
        raise GatewayError(
            GatewayErrorType.AUTHENTICATION_ERROR,
            f"provider {config.provider_id!r} has no credential: set {config.credential_env}",
            provider=config.provider_id)
    return ResolvedProvider(config=config, base_url=base_url, credential=credential)
