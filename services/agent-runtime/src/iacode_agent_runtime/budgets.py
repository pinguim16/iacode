"""What a run may spend, and the ledger that tracks it.

Four limits, and they exist for different reasons.

``max_turns``            stops an agent loop. This one is not optional and cannot be waived: a
                         runtime that can execute an unbounded number of turns will eventually
                         execute an unbounded number of turns.
``max_model_calls``      stops the spend. Every call to the gateway counts, **including a repair
                         call**, because a repair that did not count would be a way to make one
                         turn cost two without the budget noticing.
``max_duration_seconds`` stops a run that is alive but going nowhere.
``max_total_tokens``     optional, and enforceable only when the provider reports usage.

The last one is the interesting one. Gate 1 established that a provider which reports no usage has
told us nothing, and inventing a token count to enforce a budget against would be inventing the
evidence for the decision. So the ledger records ``tokens_enforceable = False`` the first time a
call comes back without usage, keeps counting turns and calls, and says plainly that the token
budget cannot be enforced — rather than silently not enforcing it.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from iacode_agent_runtime.errors import (
    AgentRuntimeError,
    AgentRuntimeErrorType,
    BudgetExceededError,
)

__all__ = ["Budget", "BudgetLedger"]

#: Ceilings on the limits themselves. A run configured with a million turns is not a configured run,
#: it is an unbounded one with a number in front of it.
MAX_TURNS_CEILING = 100
MAX_MODEL_CALLS_CEILING = 200
MAX_DURATION_CEILING_SECONDS = 86_400
MAX_TOOL_WAIT_CEILING_SECONDS = 86_400


@dataclass(frozen=True)
class Budget:
    """The limits a run was created with. Frozen: widening it mid-run is a new run's decision."""

    max_turns: int = 8
    max_model_calls: int = 12
    max_duration_seconds: int = 900
    tool_wait_timeout_seconds: int = 3600
    max_total_tokens: int | None = None

    def __post_init__(self) -> None:
        self._positive("max_turns", self.max_turns, MAX_TURNS_CEILING)
        self._positive("max_model_calls", self.max_model_calls, MAX_MODEL_CALLS_CEILING)
        self._positive("max_duration_seconds", self.max_duration_seconds,
                       MAX_DURATION_CEILING_SECONDS)
        self._positive("tool_wait_timeout_seconds", self.tool_wait_timeout_seconds,
                       MAX_TOOL_WAIT_CEILING_SECONDS)
        if self.max_total_tokens is not None:
            self._positive("max_total_tokens", self.max_total_tokens, 100_000_000)

    @staticmethod
    def _positive(name: str, value: Any, ceiling: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INVALID_REQUEST,
                f"{name} must be a whole number of at least 1",
                details={"setting": name, "value": value})
        if value > ceiling:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INVALID_REQUEST,
                f"{name} is {value}, above the permitted maximum of {ceiling}",
                details={"setting": name, "value": value, "maximum": ceiling})

    def to_dict(self) -> dict[str, Any]:
        return {
            "maxTurns": self.max_turns,
            "maxModelCalls": self.max_model_calls,
            "maxDurationSeconds": self.max_duration_seconds,
            "toolWaitTimeoutSeconds": self.tool_wait_timeout_seconds,
            "maxTotalTokens": self.max_total_tokens,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> Budget:
        payload = payload or {}
        defaults = cls()
        return cls(
            max_turns=int(payload.get("maxTurns", defaults.max_turns)),
            max_model_calls=int(payload.get("maxModelCalls", defaults.max_model_calls)),
            max_duration_seconds=int(
                payload.get("maxDurationSeconds", defaults.max_duration_seconds)),
            tool_wait_timeout_seconds=int(
                payload.get("toolWaitTimeoutSeconds", defaults.tool_wait_timeout_seconds)),
            max_total_tokens=(
                int(payload["maxTotalTokens"])
                if payload.get("maxTotalTokens") is not None else None),
        )

    def with_overrides(self, **overrides: int | None) -> Budget:
        """A copy with the caller's stated limits applied, validated by the same rules."""
        stated = {key: value for key, value in overrides.items() if value is not None}
        return replace(self, **stated) if stated else self


@dataclass
class BudgetLedger:
    """What a run has spent so far, and whether it may spend more.

    Consumption is recorded **before** the thing it pays for happens. A ledger that charged after
    the call would let a run make its last call and then discover it could not afford it, which is
    the same as not having a budget.
    """

    budget: Budget
    turns_used: int = 0
    model_calls_used: int = 0
    tokens_used: int = 0
    tokens_enforceable: bool = True
    repair_calls: int = 0
    unusable_usage_reasons: list[str] = field(default_factory=list)

    # -- consumption ---------------------------------------------------------------------------

    def start_turn(self, *, stage: str | None = None) -> None:
        if self.turns_used >= self.budget.max_turns:
            raise BudgetExceededError(
                f"the run reached its limit of {self.budget.max_turns} turns",
                stage=stage,
                details={"limit": "maxTurns", "value": self.budget.max_turns})
        self.turns_used += 1

    def start_model_call(self, *, stage: str | None = None, repair: bool = False) -> None:
        if self.model_calls_used >= self.budget.max_model_calls:
            raise BudgetExceededError(
                f"the run reached its limit of {self.budget.max_model_calls} model calls",
                stage=stage,
                details={"limit": "maxModelCalls", "value": self.budget.max_model_calls,
                         "repairAttempt": repair})
        self.model_calls_used += 1
        if repair:
            self.repair_calls += 1

    def record_usage(self, total_tokens: int | None, *, stage: str | None = None) -> None:
        """Add what a call consumed, or record that it cannot be known.

        ``None`` is not zero. A provider that reported no usage has told us nothing, so the token
        budget becomes unenforceable and says so, instead of being enforced against a number the
        runtime made up.
        """
        if total_tokens is None:
            if self.tokens_enforceable and self.budget.max_total_tokens is not None:
                self.unusable_usage_reasons.append(
                    "the provider reported no usage for at least one call")
            self.tokens_enforceable = False
            return
        self.tokens_used += int(total_tokens)
        if (self.budget.max_total_tokens is not None
                and self.tokens_enforceable
                and self.tokens_used > self.budget.max_total_tokens):
            raise BudgetExceededError(
                f"the run consumed {self.tokens_used} tokens, above its limit of "
                f"{self.budget.max_total_tokens}",
                stage=stage,
                details={"limit": "maxTotalTokens", "value": self.budget.max_total_tokens,
                         "used": self.tokens_used})

    # -- reporting ------------------------------------------------------------------------------

    @property
    def exhausted(self) -> bool:
        """Whether the run has nothing left to spend on another turn."""
        return (self.turns_used >= self.budget.max_turns
                or self.model_calls_used >= self.budget.max_model_calls)

    def to_dict(self) -> dict[str, Any]:
        return {
            "turnsUsed": self.turns_used,
            "modelCallsUsed": self.model_calls_used,
            "tokensUsed": self.tokens_used if self.tokens_enforceable else None,
            "tokensEnforceable": self.tokens_enforceable,
            "repairCalls": self.repair_calls,
            "unusableUsageReasons": list(dict.fromkeys(self.unusable_usage_reasons)),
        }

    @classmethod
    def from_dict(cls, budget: Budget, payload: dict[str, Any] | None) -> BudgetLedger:
        payload = payload or {}
        return cls(
            budget=budget,
            turns_used=int(payload.get("turnsUsed", 0)),
            model_calls_used=int(payload.get("modelCallsUsed", 0)),
            tokens_used=int(payload.get("tokensUsed") or 0),
            tokens_enforceable=bool(payload.get("tokensEnforceable", True)),
            repair_calls=int(payload.get("repairCalls", 0)),
            unusable_usage_reasons=list(payload.get("unusableUsageReasons") or []),
        )
