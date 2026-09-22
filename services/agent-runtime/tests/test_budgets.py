"""Budgets: what a run may spend, what it has spent, and what cannot be enforced."""

from __future__ import annotations

import pytest
from iacode_agent_runtime.budgets import Budget, BudgetLedger
from iacode_agent_runtime.errors import (
    AgentRuntimeError,
    AgentRuntimeErrorType,
    BudgetExceededError,
)


class BudgetContractTests:
    """Every run carries a turn limit, a call limit and a wall-clock deadline."""

    def test_a_default_budget_bounds_all_three(self) -> None:
        budget = Budget()
        assert budget.max_turns >= 1
        assert budget.max_model_calls >= 1
        assert budget.max_duration_seconds >= 1
        assert budget.tool_wait_timeout_seconds >= 1

    def test_a_budget_round_trips_through_its_dictionary(self) -> None:
        budget = Budget(max_turns=3, max_model_calls=5, max_duration_seconds=60,
                        tool_wait_timeout_seconds=30, max_total_tokens=1000)
        assert Budget.from_dict(budget.to_dict()) == budget

    def test_overrides_are_validated_by_the_same_rules(self) -> None:
        assert Budget().with_overrides(max_turns=2).max_turns == 2
        with pytest.raises(AgentRuntimeError):
            Budget().with_overrides(max_turns=0)

    def test_an_override_of_none_keeps_the_default(self) -> None:
        default = Budget()
        assert default.with_overrides(max_turns=None, max_model_calls=None) == default

    def test_the_token_budget_is_optional(self) -> None:
        assert Budget().max_total_tokens is None


ABSURD_BUDGETS = (
    ("max_turns", 0),
    ("max_turns", -1),
    ("max_turns", 1_000_000),
    ("max_model_calls", 0),
    ("max_model_calls", 10_000),
    ("max_duration_seconds", 0),
    ("max_duration_seconds", 10 ** 9),
    ("tool_wait_timeout_seconds", 0),
    ("max_total_tokens", 0),
)


def test_absurd_budget_is_refused() -> None:
    """A run configured with a million turns is an unbounded run with a number in front of it.

    Written as a loop rather than as a parametrisation: the TESTS denominator is derived
    statically from the source, and a runtime expansion cannot be counted that way.
    """
    for field, value in ABSURD_BUDGETS:
        with pytest.raises(AgentRuntimeError) as raised:
            Budget(**{field: value})
        assert raised.value.error_type is AgentRuntimeErrorType.INVALID_REQUEST, field
        assert raised.value.details["setting"] == field


def test_a_boolean_is_not_a_turn_count() -> None:
    """``True`` is an ``int`` in Python, and a budget of ``True`` turns is not a budget."""
    with pytest.raises(AgentRuntimeError):
        Budget(max_turns=True)


def test_every_gateway_call_counts() -> None:
    """Including a repair. A repair outside the budget makes one turn cost two invisibly."""
    ledger = BudgetLedger(budget=Budget(max_turns=4, max_model_calls=3))
    ledger.start_model_call()
    ledger.start_model_call(repair=True)
    assert ledger.model_calls_used == 2
    assert ledger.repair_calls == 1

    ledger.start_model_call()
    with pytest.raises(BudgetExceededError) as raised:
        ledger.start_model_call()
    assert raised.value.details["limit"] == "maxModelCalls"


def test_the_turn_limit_stops_the_loop() -> None:
    ledger = BudgetLedger(budget=Budget(max_turns=2, max_model_calls=9))
    ledger.start_turn()
    ledger.start_turn()
    with pytest.raises(BudgetExceededError) as raised:
        ledger.start_turn()
    assert raised.value.details["limit"] == "maxTurns"


def test_consumption_is_charged_before_the_thing_it_pays_for() -> None:
    """A ledger charged afterwards lets a run make the call it could not afford."""
    ledger = BudgetLedger(budget=Budget(max_turns=1, max_model_calls=1))
    ledger.start_model_call()
    assert ledger.model_calls_used == 1
    assert ledger.exhausted


def test_token_budget_is_unenforceable_without_usage() -> None:
    """``None`` is not zero. A provider that reported nothing has told us nothing."""
    ledger = BudgetLedger(budget=Budget(max_total_tokens=100))
    ledger.record_usage(None)

    assert ledger.tokens_enforceable is False
    assert ledger.tokens_used == 0
    assert ledger.to_dict()["tokensUsed"] is None
    assert ledger.unusable_usage_reasons

    # And it stays unenforceable: a later call that does report usage cannot retroactively make
    # the budget meaningful, because the missing call's tokens are still unknown.
    ledger.record_usage(1_000_000)
    assert ledger.tokens_enforceable is False


def test_a_token_budget_is_enforced_when_usage_exists() -> None:
    ledger = BudgetLedger(budget=Budget(max_total_tokens=100))
    ledger.record_usage(60)
    with pytest.raises(BudgetExceededError) as raised:
        ledger.record_usage(60)
    assert raised.value.details["limit"] == "maxTotalTokens"


def test_a_ledger_round_trips_so_a_restart_resumes_it() -> None:
    budget = Budget(max_turns=5, max_model_calls=7)
    ledger = BudgetLedger(budget=budget, turns_used=2, model_calls_used=3, tokens_used=40,
                          repair_calls=1)
    restored = BudgetLedger.from_dict(budget, ledger.to_dict())
    assert restored.turns_used == 2
    assert restored.model_calls_used == 3
    assert restored.repair_calls == 1
