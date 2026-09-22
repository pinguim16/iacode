"""Routing: which candidates, in what order, and why the rest were refused."""

from __future__ import annotations

import pytest
from fixtures.doubles import (
    InMemoryCatalogStore,
    ScriptedProvider,
    build_gateway,
    completion,
    descriptor,
    provider_config,
    request as build_request,
    route_policy,
    settings as build_settings,
)
from iacode_model_gateway.config import RouteAlias
from iacode_model_gateway.contracts import (
    Capability,
    CapabilityState,
    Endpoint,
    GatewayMessage,
    MessageRole,
    ReasoningEffort,
    RouteReason,
    ToolDefinition,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.routing.context import (
    SAFETY_MARGIN,
    estimate_request_tokens,
    fits_context,
)
from iacode_model_gateway.routing.router import Router


def _router(policy=None, **overrides):
    return Router(policy or route_policy(), build_settings(**overrides))


def _plan(router, request, models, providers=None, output_tokens: int = 16):
    return router.plan(request, models, providers or {"alpha": provider_config()},
                       output_tokens=output_tokens)


def test_router_is_deterministic() -> None:
    """The same inputs produce the same plan, including the order."""
    router = _router(route_policy(RouteAlias(alias="wide", candidates=("model-one",))))
    models = [descriptor(model_id="model-one"), descriptor("beta", "model-one")]
    providers = {"alpha": provider_config("alpha", priority=50),
                 "beta": provider_config("beta", priority=90)}

    first = _plan(router, build_request(route="wide"), models, providers)
    second = _plan(router, build_request(route="wide"), list(reversed(models)), providers)

    assert [item.ref.qualified for item in first.candidates] == ["beta:model-one",
                                                                 "alpha:model-one"]
    assert [item.ref.qualified for item in first.candidates] == \
        [item.ref.qualified for item in second.candidates]


def test_explicit_model_is_honoured_or_refused() -> None:
    """Named explicitly means used or refused, never quietly replaced."""
    router = _router()
    models = [descriptor(model_id="model-one"), descriptor(model_id="model-two")]

    plan = _plan(router, build_request(model="alpha:model-two"), models)
    assert [item.ref.model_id for item in plan.candidates] == ["model-two"]
    assert plan.reason is RouteReason.EXPLICIT_MODEL

    with pytest.raises(GatewayError) as error:
        _plan(router, build_request(model="alpha:absent"), models)
    assert error.value.error_type is GatewayErrorType.NO_CANDIDATE
    assert "not replaced" in error.value.message


def test_the_default_model_is_used_when_nothing_is_named() -> None:
    router = _router()
    plan = _plan(router, build_request(), [descriptor()])

    assert plan.reason is RouteReason.DEFAULT_MODEL
    assert plan.candidates[0].ref.qualified == "alpha:model-one"


def test_missing_default_model_is_an_explicit_error() -> None:
    """An arbitrary choice would spend tokens on a model nobody authorised."""
    router = _router(default_model=None)

    with pytest.raises(GatewayError) as error:
        _plan(router, build_request(), [descriptor()])

    assert error.value.error_type is GatewayErrorType.NO_CANDIDATE
    assert "IACODE_GATEWAY_DEFAULT_MODEL" in error.value.message


def test_an_unconfigured_route_is_refused_by_name() -> None:
    router = _router(route_policy(RouteAlias(alias="fast")))

    with pytest.raises(GatewayError) as error:
        _plan(router, build_request(route="nonsense"), [descriptor()])

    assert error.value.error_type is GatewayErrorType.INVALID_REQUEST
    assert "fast" in error.value.message


def test_an_alias_with_no_candidate_falls_back_to_the_default() -> None:
    """Shipping candidates for an alias would assert a preference nobody measured."""
    router = _router(route_policy(RouteAlias(alias="coding")))
    plan = _plan(router, build_request(route="coding"), [descriptor()])

    assert plan.reason is RouteReason.DEFAULT_MODEL
    assert plan.route == "coding"


def test_an_alias_with_no_candidate_and_no_default_fails_clearly() -> None:
    router = _router(route_policy(RouteAlias(alias="coding")), default_model=None)

    with pytest.raises(GatewayError) as error:
        _plan(router, build_request(route="coding"), [descriptor()])

    assert "coding" in error.value.message


def test_route_aliases_come_from_configuration() -> None:
    """The router knows no alias the policy did not give it."""
    empty = _router(route_policy())

    with pytest.raises(GatewayError):
        _plan(empty, build_request(route="deep"), [descriptor()])

    configured = _router(route_policy(RouteAlias(alias="deep",
                                                 candidates=("alpha:model-two",))))
    plan = _plan(configured, build_request(route="deep"),
                 [descriptor(model_id="model-two")])
    assert plan.reason is RouteReason.ROUTE_ALIAS


def test_capability_filtering_removes_a_model_that_cannot_serve() -> None:
    router = _router()
    models = [descriptor(model_id="model-one",
                         capabilities={Capability.TOOLS: CapabilityState.UNSUPPORTED}),
              descriptor(model_id="model-two",
                         capabilities={Capability.TOOLS: CapabilityState.SUPPORTED})]

    plan = _plan(router,
                 build_request(model="alpha:model-two", tools=(ToolDefinition(name="read"),)),
                 models)
    assert plan.candidates[0].ref.model_id == "model-two"

    with pytest.raises(GatewayError) as error:
        _plan(router,
              build_request(model="alpha:model-one", tools=(ToolDefinition(name="read"),)),
              models)
    assert "does not support tools" in error.value.message


def test_unknown_capability_is_rejected_by_default() -> None:
    """Sending anyway would spend quota to learn what the catalog already said it did not know."""
    router = _router()
    silent = descriptor(model_id="model-one", capabilities={})

    with pytest.raises(GatewayError) as error:
        _plan(router, build_request(tools=(ToolDefinition(name="read"),)), [silent])
    assert "never declared" in error.value.message

    permissive = _router(route_policy(allow_unknown=(Capability.TOOLS,)))
    plan = _plan(permissive, build_request(tools=(ToolDefinition(name="read"),)), [silent])
    assert plan.candidates[0].ref.model_id == "model-one"


def test_disabled_provider_and_inactive_model_are_excluded() -> None:
    router = _router()
    models = [descriptor(model_id="model-one", active=False)]

    with pytest.raises(GatewayError):
        _plan(router, build_request(), models)

    with pytest.raises(GatewayError):
        _plan(router, build_request(), [descriptor()],
              {"alpha": provider_config(enabled=False)})


def test_incompatible_reasoning_effort_is_not_sent_silently() -> None:
    """Dropping the field would answer a different question from the one that was asked."""
    router = _router()
    model = descriptor(model_id="model-one",
                       capabilities={Capability.REASONING: CapabilityState.SUPPORTED},
                       reasoning_levels=(ReasoningEffort.LOW,))

    with pytest.raises(GatewayError) as error:
        _plan(router, build_request(reasoning_effort=ReasoningEffort.HIGH), [model])
    assert "reasoning levels low" in error.value.message

    plan = _plan(router, build_request(reasoning_effort=ReasoningEffort.LOW), [model])
    assert plan.candidates


def test_route_explanation_is_structured_and_short() -> None:
    router = _router()
    models = [descriptor(model_id="model-one"),
              descriptor(model_id="model-two", active=False)]

    plan = _plan(router, build_request(), models)

    assert plan.reason in set(RouteReason)
    assert plan.considered == 1
    assert len(plan.rejected) <= 8
    assert all(isinstance(item, str) and len(item) < 300 for item in plan.rejected)


def test_routing_reads_normalised_fields_only() -> None:
    """A decision that depended on the raw payload would depend on a provider's release notes."""
    router = _router()
    misleading = descriptor(model_id="model-one",
                            capabilities={Capability.TOOLS: CapabilityState.UNSUPPORTED})
    misleading = misleading.model_copy(update={"raw_metadata": {"supports_tools": True}})

    with pytest.raises(GatewayError):
        _plan(router, build_request(tools=(ToolDefinition(name="read"),)), [misleading])


def test_the_fallback_chain_is_truncated_to_the_configured_budget() -> None:
    router = _router(route_policy(RouteAlias(
        alias="wide",
        candidates=("alpha:model-one", "alpha:model-two", "alpha:model-three",
                    "alpha:model-four"))), max_fallbacks=1)
    models = [descriptor(model_id=name) for name in
              ("model-one", "model-two", "model-three", "model-four")]

    plan = _plan(router, build_request(route="wide"), models)

    assert len(plan.candidates) == 2


class ContextWindowTests:
    """The preflight, and the fact that it is an estimate."""

    def test_an_estimate_says_it_is_an_estimate(self) -> None:
        estimate = estimate_request_tokens(build_request())

        assert not estimate.exact
        assert "heuristic" in estimate.method
        assert estimate.tokens > 0

    def test_a_model_with_no_declared_window_is_not_filtered_out(self) -> None:
        fits, why = fits_context(estimate_request_tokens(build_request()),
                                 descriptor(context_window=None), 100)

        assert fits
        assert "no context window" in why

    def test_a_request_larger_than_the_window_is_refused(self) -> None:
        big = build_request(messages=(
            GatewayMessage(role=MessageRole.USER, content="x" * 40_000),))

        fits, why = fits_context(estimate_request_tokens(big), descriptor(context_window=1000),
                                 100)

        assert not fits
        assert "exceed" in why

    def test_the_output_cap_counts_against_the_window(self) -> None:
        estimate = estimate_request_tokens(build_request())
        window = descriptor(context_window=1000)

        assert fits_context(estimate, window, 100)[0]
        assert not fits_context(estimate, window, 1000)[0]

    def test_the_margin_is_applied_rather_than_assumed(self) -> None:
        assert 0 < SAFETY_MARGIN < 1

    def test_the_router_rejects_a_candidate_whose_window_is_too_small(self) -> None:
        router = _router()
        big = build_request(model="alpha:small",
                            messages=(GatewayMessage(role=MessageRole.USER,
                                                     content="x" * 40_000),))

        with pytest.raises(GatewayError) as error:
            _plan(router, big, [descriptor(model_id="small", context_window=1000)])

        assert "token window" in error.value.message


async def test_the_output_cap_is_tightened_to_the_chosen_models_limit() -> None:
    """Asking a model for more than it can produce is a refusal, not a truncation."""
    store = InMemoryCatalogStore()
    store.seed(descriptor(max_output_tokens=32))
    provider = ScriptedProvider("alpha", completions=[completion()])
    gateway = build_gateway(catalog=store, factory=lambda config: provider,
                            max_output_tokens=256)

    await gateway.infer(build_request())

    assert provider.calls[0]["outputTokens"] == 32


def test_no_model_quality_claim_is_hardcoded() -> None:
    """No score, no benchmark, no 'better at' anywhere in the gateway source."""
    import re
    from pathlib import Path

    import iacode_model_gateway

    source_root = Path(iacode_model_gateway.__file__).resolve().parent
    claim = re.compile(
        r"(?i)\b(better than|best for|outperforms|score\s*[:=]\s*[0-9]|quality\s*[:=]\s*[0-9]"
        r"|rank(?:ing)?\s*[:=]\s*[0-9]|benchmark\s*[:=])")
    offenders = []
    for path in sorted(source_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for match in claim.finditer(path.read_text(encoding="utf-8")):
            offenders.append(f"{path.name}: {match.group(0)}")

    assert offenders == [], offenders
