"""The rules the router applies to a candidate, separated from the act of choosing one.

Keeping them here rather than inside :mod:`iacode_model_gateway.routing.router` is what makes each
one testable on its own: "would this model be rejected, and what would the reason be" is a question
answered by a pure function over a descriptor, with no catalog, no clock and no HTTP client in sight.

Two rules are worth reading twice.

**Unknown is refused by default.** A model that has never declared support for a required capability
is not a model that supports it. The policy can be configured to allow a specific capability
through — a locally-hosted runtime whose ``/models`` answer carries nothing is the case that needs
it — but the allowance is per capability, explicit, and visible in the repository.

**A reasoning effort is never dropped.** If a caller asked for one and the model does not declare
the level, the candidate is rejected. Sending the request without the field would return an answer
that looks fine and is not what was asked for, which is the worst of the three options: refuse,
route elsewhere, or silently do something else.
"""

from __future__ import annotations

from dataclasses import dataclass

from iacode_model_gateway.config import RoutePolicy
from iacode_model_gateway.contracts import (
    Capability,
    CapabilityState,
    GatewayRequest,
    ModelDescriptor,
    ReasoningEffort,
)
from iacode_model_gateway.errors import GatewayError

__all__ = ["CandidateVerdict", "evaluate_candidate", "may_fall_back"]


@dataclass(frozen=True)
class CandidateVerdict:
    """Whether a candidate may serve a request, and the short reason when it may not."""

    usable: bool
    reason: str = ""


def evaluate_candidate(request: GatewayRequest, model: ModelDescriptor,
                       policy: RoutePolicy) -> CandidateVerdict:
    """Decide whether one catalog entry can serve one request."""
    if not model.active:
        return CandidateVerdict(False, "the model is inactive in the catalog")

    for capability in request.implied_capabilities:
        state = model.capability(capability)
        if state is CapabilityState.SUPPORTED:
            continue
        if state is CapabilityState.UNSUPPORTED:
            return CandidateVerdict(False, f"the model does not support {capability!s}")
        if not policy.unknown_capability.permits(capability):
            return CandidateVerdict(
                False,
                f"the model has never declared {capability!s} and the policy refuses an unknown "
                f"capability")

    if request.reasoning_effort is not None and model.reasoning_levels:
        if request.reasoning_effort not in model.reasoning_levels:
            declared = ", ".join(str(level) for level in model.reasoning_levels)
            return CandidateVerdict(
                False,
                f"the model declares reasoning levels {declared} and not "
                f"{request.reasoning_effort!s}")

    return CandidateVerdict(True)


def reasoning_is_expressible(effort: ReasoningEffort | None,
                             model: ModelDescriptor) -> bool:
    """Whether an effort can be sent to this model without being silently dropped.

    A model that declares no levels at all is a model we know nothing about, which
    :func:`evaluate_candidate` has already judged through the ``reasoning`` capability. This answers
    the narrower question the adapter asks.
    """
    if effort is None:
        return True
    if not model.reasoning_levels:
        return model.capability(Capability.REASONING) is CapabilityState.SUPPORTED
    return effort in model.reasoning_levels


def may_fall_back(error: GatewayError, remaining: int) -> tuple[bool, str]:
    """Whether the router should try a different candidate after this failure.

    Two conditions, and the second is not a detail: a fallback budget that could be exhausted by the
    errors themselves is how a chain becomes a loop.
    """
    if remaining <= 0:
        return False, "the fallback budget is exhausted"
    if not error.fallbackable:
        return False, (
            f"{error.error_type!s} would fail identically on another candidate")
    return True, f"{error.error_type!s} may be resolved by a different candidate"
