"""The gateway error taxonomy.

Every failure a provider can produce arrives in a different shape: an HTTP status, a JSON body with
a vendor-specific ``type``, a transport exception, a timeout, a cancelled task. The consumer of the
gateway must not have to know any of them. This module is the single vocabulary they all map onto,
and the mapping happens in the adapter layer, never above it.

The taxonomy exists to answer three operational questions, and every member is here because one of
them needs it:

*Is it worth trying again?*      ``RATE_LIMITED``, ``PROVIDER_TIMEOUT``, ``PROVIDER_UNAVAILABLE``
                                 and ``TRANSIENT_PROVIDER_ERROR`` may resolve on a retry.
                                 ``AUTHENTICATION_ERROR``, ``INVALID_REQUEST``, ``CONTEXT_LIMIT``
                                 and ``MODEL_NOT_FOUND`` never do, and retrying them burns quota
                                 while the caller waits for an answer that will not change.
*Would another model help?*      A provider being down is another candidate's opportunity. A
                                 malformed request is not: the second model refuses it exactly like
                                 the first, and the fallback only makes the failure slower.
*Whose fault is it?*             ``INTERNAL_GATEWAY_ERROR`` is ours. Everything else is a fact
                                 about the provider or about the request, and the distinction is
                                 what stops us from opening a circuit because of our own bug.

``retryable`` and ``fallbackable`` are properties of the *class*, declared once here, rather than
decisions rediscovered at each call site. A per-site decision is how a retry on an authentication
failure gets written: it looks reasonable in isolation.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

__all__ = [
    "GatewayError",
    "GatewayErrorType",
    "FALLBACKABLE_ERRORS",
    "RETRYABLE_ERRORS",
]


class GatewayErrorType(StrEnum):
    """The canonical failure classes of a model invocation."""

    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    INVALID_REQUEST = "INVALID_REQUEST"
    CONTEXT_LIMIT = "CONTEXT_LIMIT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    TRANSIENT_PROVIDER_ERROR = "TRANSIENT_PROVIDER_ERROR"
    PERMANENT_PROVIDER_ERROR = "PERMANENT_PROVIDER_ERROR"
    CIRCUIT_OPEN = "CIRCUIT_OPEN"
    CANCELLED = "CANCELLED"
    NO_CANDIDATE = "NO_CANDIDATE"
    RESPONSE_TOO_LARGE = "RESPONSE_TOO_LARGE"
    INTERNAL_GATEWAY_ERROR = "INTERNAL_GATEWAY_ERROR"


#: Classes where the same request, sent again to the same model, can legitimately succeed.
RETRYABLE_ERRORS: frozenset[GatewayErrorType] = frozenset({
    GatewayErrorType.RATE_LIMITED,
    GatewayErrorType.PROVIDER_TIMEOUT,
    GatewayErrorType.PROVIDER_UNAVAILABLE,
    GatewayErrorType.TRANSIENT_PROVIDER_ERROR,
})

#: Classes where a *different* candidate could answer. Deliberately wider than the retryable set
#: and deliberately not universal.
#:
#: ``AUTHENTICATION_ERROR`` is here because a credential is per provider: the key for provider A
#: being wrong says nothing about provider B, and a configured second provider is exactly the
#: situation fallback exists for. It is *not* in the retryable set, because re-sending to the same
#: provider with the same key cannot succeed.
#:
#: ``INVALID_REQUEST``, ``CONTEXT_LIMIT`` and ``MODEL_NOT_FOUND`` are absent. A malformed payload is
#: malformed everywhere; a prompt too long for a 128k window is not made shorter by sending it to a
#: second model — the context filter in the router is what handles that, before the call.
FALLBACKABLE_ERRORS: frozenset[GatewayErrorType] = frozenset({
    GatewayErrorType.AUTHENTICATION_ERROR,
    GatewayErrorType.AUTHORIZATION_ERROR,
    GatewayErrorType.RATE_LIMITED,
    GatewayErrorType.PROVIDER_UNAVAILABLE,
    GatewayErrorType.PROVIDER_TIMEOUT,
    GatewayErrorType.TRANSIENT_PROVIDER_ERROR,
    GatewayErrorType.PERMANENT_PROVIDER_ERROR,
    GatewayErrorType.CIRCUIT_OPEN,
})


class GatewayError(Exception):
    """A failure of a model invocation, already classified.

    ``message`` is safe to show a caller: it is written by the adapter from the class and from
    non-sensitive context, never from the provider's raw body, because a provider that echoes a
    request header back inside an error message would otherwise put an ``Authorization`` value into
    our exception text. ``details`` carries structured, non-sensitive context — a status code, a
    retry hint, a model identifier — and is what the API turns into a response body.
    """

    def __init__(
        self,
        error_type: GatewayErrorType,
        message: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        status_code: int | None = None,
        retry_after_seconds: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.provider = provider
        self.model = model
        self.status_code = status_code
        self.retry_after_seconds = retry_after_seconds
        self.details = dict(details or {})

    @property
    def retryable(self) -> bool:
        """Whether sending the same request to the same model again could succeed."""
        return self.error_type in RETRYABLE_ERRORS

    @property
    def fallbackable(self) -> bool:
        """Whether a different candidate could answer the request this one failed."""
        return self.error_type in FALLBACKABLE_ERRORS

    def to_dict(self) -> dict[str, Any]:
        """The classified failure as a payload, with nothing in it that could be a credential."""
        payload: dict[str, Any] = {"errorType": str(self.error_type), "message": self.message}
        if self.provider:
            payload["provider"] = self.provider
        if self.model:
            payload["model"] = self.model
        if self.status_code is not None:
            payload["statusCode"] = self.status_code
        if self.retry_after_seconds is not None:
            payload["retryAfterSeconds"] = self.retry_after_seconds
        if self.details:
            payload["details"] = dict(self.details)
        return payload

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"GatewayError({self.error_type}, {self.message!r})"
