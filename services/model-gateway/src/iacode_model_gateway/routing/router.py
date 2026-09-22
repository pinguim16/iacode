"""Choosing which model to call, deterministically.

The router answers one question — *given this request, this catalog and this policy, which candidates
may serve it and in what order* — and it answers it the same way every time. There is no learning
here, no score and no measured preference, because this project has measured nothing yet.
`docs/GATE-1-CHECKLIST.md` row 7.8 forbids inventing one: a hardcoded "model X is better at coding"
is a claim, and a claim with no evaluation behind it is worse than no claim, because it gets acted
on.

The order is fixed and each step is visible in the result:

1. an **explicit model** is honoured or refused — never replaced, because a caller that names a
   model and silently gets another one has been lied to;
2. a **route alias** expands to its configured candidates, in the configured order;
3. otherwise the **configured default** is used;
4. with none of the three, the request fails with a clear error rather than with an arbitrary pick.

Then the candidates are filtered — disabled provider, inactive model, missing capability, window too
small — and truncated to one plus the configured fallback budget, so the chain is bounded by
construction rather than by a loop guard.

What the caller gets back is a plan and an explanation: the reason, how many candidates were
considered, and why the rejected ones were rejected. That explanation is short and structured. It is
not a narrative, and it is never a model's reasoning.
"""

from __future__ import annotations

from dataclasses import dataclass

from iacode_model_gateway.config import GatewaySettings, ProviderConfig, RoutePolicy
from iacode_model_gateway.contracts import (
    GatewayRequest,
    ModelDescriptor,
    ModelRef,
    RouteReason,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.routing.context import estimate_request_tokens, fits_context
from iacode_model_gateway.routing.policy import evaluate_candidate

__all__ = ["Candidate", "RoutePlan", "Router"]

#: How many rejection reasons the explanation carries. An explanation that grows with the catalog
#: stops being read, and the count of considered candidates is already recorded separately.
MAX_REJECTIONS_EXPLAINED = 8


@dataclass(frozen=True)
class Candidate:
    """One model the router is willing to call, with the provider that serves it."""

    model: ModelDescriptor
    provider: ProviderConfig

    @property
    def ref(self) -> ModelRef:
        return self.model.ref


@dataclass(frozen=True)
class RoutePlan:
    """The ordered candidates and the explanation of how they were chosen."""

    reason: RouteReason
    candidates: tuple[Candidate, ...]
    considered: int
    rejected: tuple[str, ...]
    route: str | None = None
    output_tokens: int = 0


class Router:
    """Deterministic candidate selection over a catalog."""

    def __init__(self, policy: RoutePolicy, settings: GatewaySettings) -> None:
        self._policy = policy
        self._settings = settings

    def plan(self, request: GatewayRequest, models: list[ModelDescriptor],
             providers: dict[str, ProviderConfig], *, output_tokens: int) -> RoutePlan:
        """Produce the ordered candidate list for a request, or refuse with a classified error."""
        by_ref = {model.ref.qualified: model for model in models}
        reason, route, wanted = self._intended(request)

        pool: list[Candidate] = []
        seen: set[str] = set()
        for wanted_ref in wanted:
            for candidate in self._expand(wanted_ref, by_ref, providers):
                if candidate.ref.qualified in seen:
                    continue
                seen.add(candidate.ref.qualified)
                pool.append(candidate)

        if not pool:
            raise GatewayError(
                GatewayErrorType.NO_CANDIDATE,
                self._nothing_matched_message(reason, route, wanted),
                details={"reason": str(reason), "route": route,
                         "requested": list(wanted)})

        estimate = estimate_request_tokens(request)
        usable: list[Candidate] = []
        rejected: list[str] = []
        for candidate in pool:
            verdict = evaluate_candidate(request, candidate.model, self._policy)
            if not verdict.usable:
                rejected.append(f"{candidate.ref.qualified}: {verdict.reason}")
                continue
            fits, why = fits_context(estimate, candidate.model, output_tokens)
            if not fits:
                rejected.append(f"{candidate.ref.qualified}: {why}")
                continue
            usable.append(candidate)

        if not usable:
            raise GatewayError(
                GatewayErrorType.NO_CANDIDATE,
                "no candidate satisfies the request: "
                + "; ".join(rejected[:MAX_REJECTIONS_EXPLAINED]),
                details={"reason": str(reason), "route": route,
                         "considered": len(pool),
                         "rejected": rejected[:MAX_REJECTIONS_EXPLAINED],
                         "inputTokenEstimate": estimate.tokens,
                         "estimateIsExact": estimate.exact})

        if reason is RouteReason.EXPLICIT_MODEL:
            # An explicit model is honoured, not widened. Falling back from it would be exactly the
            # silent replacement row 7.2 forbids.
            chosen = usable[:1]
        else:
            chosen = usable[:1 + self._settings.max_fallbacks]

        return RoutePlan(
            reason=reason,
            candidates=tuple(chosen),
            considered=len(pool),
            rejected=tuple(rejected[:MAX_REJECTIONS_EXPLAINED]),
            route=route,
            output_tokens=output_tokens,
        )

    # -- intent ---------------------------------------------------------------------------------

    def _intended(self, request: GatewayRequest) -> tuple[RouteReason, str | None, tuple[str, ...]]:
        """What the request asked for, before the catalog is consulted."""
        if request.model:
            return RouteReason.EXPLICIT_MODEL, None, (request.model,)

        if request.route:
            alias = self._policy.alias(request.route)
            if alias is None:
                raise GatewayError(
                    GatewayErrorType.INVALID_REQUEST,
                    f"route {request.route!r} is not configured; the configured routes are "
                    + (", ".join(item.alias for item in self._policy.aliases) or "none"),
                    details={"route": request.route})
            if alias.candidates:
                return RouteReason.ROUTE_ALIAS, alias.alias, alias.candidates
            if self._settings.default_model:
                # A configured alias with no candidates is a name for "whatever the default is".
                # That is a deliberate state, not an oversight: shipping candidates for it would be
                # this project asserting a preference it has not measured.
                return RouteReason.DEFAULT_MODEL, alias.alias, (self._settings.default_model,)
            raise GatewayError(
                GatewayErrorType.NO_CANDIDATE,
                f"route {request.route!r} has no configured candidate and no default model is "
                f"configured; set IACODE_GATEWAY_DEFAULT_MODEL or give the route a candidate",
                details={"route": request.route})

        if self._settings.default_model:
            return RouteReason.DEFAULT_MODEL, None, (self._settings.default_model,)

        raise GatewayError(
            GatewayErrorType.NO_CANDIDATE,
            "the request names no model and no route, and no default model is configured; set "
            "IACODE_GATEWAY_DEFAULT_MODEL rather than letting the gateway choose one",
            details={"setting": "IACODE_GATEWAY_DEFAULT_MODEL"})

    def _expand(self, reference: str, by_ref: dict[str, ModelDescriptor],
                providers: dict[str, ProviderConfig]) -> list[Candidate]:
        """Turn one configured reference into the catalog entries it names.

        A qualified ``provider:model`` names one entry. A bare identifier names every provider that
        exposes it, ordered by configured provider priority — which is how a route survives one
        provider being disabled without anybody editing the route.
        """
        if ":" in reference:
            model = by_ref.get(reference)
            if model is None:
                return []
            provider = providers.get(model.ref.provider_id)
            if provider is None or not provider.enabled:
                return []
            return [Candidate(model=model, provider=provider)]

        matches: list[Candidate] = []
        for model in by_ref.values():
            if model.ref.model_id != reference:
                continue
            provider = providers.get(model.ref.provider_id)
            if provider is None or not provider.enabled:
                continue
            matches.append(Candidate(model=model, provider=provider))
        # Higher priority first, then by identifier so two providers with the same priority always
        # produce the same order: a router whose answer depended on dictionary iteration would be
        # deterministic only by accident.
        matches.sort(key=lambda item: (-item.provider.priority, item.ref.qualified))
        return matches

    @staticmethod
    def _nothing_matched_message(reason: RouteReason, route: str | None,
                                 wanted: tuple[str, ...]) -> str:
        named = ", ".join(wanted)
        if reason is RouteReason.EXPLICIT_MODEL:
            return (f"model {named} is not in the catalog, or its provider is disabled; it is not "
                    f"replaced by another model because the request named it explicitly")
        if reason is RouteReason.ROUTE_ALIAS:
            return (f"route {route!r} names {named}, and none of them is in the catalog with an "
                    f"enabled provider")
        return (f"the default model {named} is not in the catalog with an enabled provider; "
                f"synchronise the catalog or correct IACODE_GATEWAY_DEFAULT_MODEL")
