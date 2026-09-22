"""The run event log: what a run records about itself.

The vocabulary is closed and comes from `iacode_contracts.agent_runtime`. A log whose event types
grow by accident is a log nothing can query, and the database carries the same list as a ``CHECK``
constraint, derived from the same tuple.

Two properties matter more than the list itself.

**An event is an occurrence, not a row.** :attr:`RunEvent.dedupe_key` identifies the moment — this
run, this stage, this turn, this kind — so an activity that Temporal executes twice appends the
event once. Without it the history of a run would depend on how many times the infrastructure
retried, which is not history.

**A payload carries facts, not narration.** :func:`safe_payload` drops anything that is not a
small scalar and refuses a key that looks like a place reasoning or a prompt would end up. The
Development Contract forbids storing private chain-of-thought, and a free-form JSON column is
exactly where it would arrive if nothing checked.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from iacode_contracts.agent_runtime import RUN_EVENT_TYPES

from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.limits import RuntimeLimits, enforce_size

__all__ = ["EVENT_TYPES", "RunEvent", "event_type", "safe_payload"]

EVENT_TYPES: frozenset[str] = frozenset(RUN_EVENT_TYPES)

#: Keys a payload may not carry, whatever their value. They are the names under which a transcript,
#: a prompt or a model's deliberation would be written if somebody added it without thinking.
FORBIDDEN_PAYLOAD_KEYS = frozenset({
    "reasoning", "thoughts", "thought", "chainofthought", "chain_of_thought", "deliberation",
    "prompt", "prompts", "messages", "completion", "rawoutput", "raw_output", "transcript",
    "apikey", "api_key", "secret", "token", "credential", "authorization",
})

#: The longest a string value inside a payload may be. A payload is a handful of facts; a value
#: longer than this is content that belongs in the run's own result column, not in the history.
MAX_PAYLOAD_VALUE = 512


def event_type(value: str) -> str:
    """Return a known event type, or refuse."""
    if value not in EVENT_TYPES:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR,
            f"{value!r} is not an event type this runtime declares",
            details={"eventType": value, "known": sorted(EVENT_TYPES)})
    return value


def safe_payload(payload: dict[str, Any] | None,
                 limits: RuntimeLimits | None = None) -> dict[str, Any]:
    """Reduce a payload to the facts it is allowed to carry.

    Refusing rather than truncating for a forbidden key is deliberate: a truncated prompt is still
    a prompt, and a caller that tried to record one has a defect worth surfacing.
    """
    limits = limits or RuntimeLimits()
    result: dict[str, Any] = {}
    for key, value in (payload or {}).items():
        normalised = str(key)
        if normalised.lower().replace("-", "").replace("_", "") in FORBIDDEN_PAYLOAD_KEYS:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR,
                f"an event payload may not carry {normalised!r}",
                details={"key": normalised})
        if value is None or isinstance(value, (bool, int, float)):
            result[normalised] = value
        elif isinstance(value, str):
            result[normalised] = value[:MAX_PAYLOAD_VALUE]
        elif isinstance(value, (list, tuple)):
            result[normalised] = [
                item[:MAX_PAYLOAD_VALUE] if isinstance(item, str) else item
                for item in value
                if item is None or isinstance(item, (bool, int, float, str))
            ]
        elif isinstance(value, dict):
            result[normalised] = safe_payload(value, limits)
        else:
            result[normalised] = str(value)[:MAX_PAYLOAD_VALUE]
    enforce_size(result, limits.max_event_payload_bytes, what="the event payload")
    return result


@dataclass(frozen=True)
class RunEvent:
    """One moment of a run, ready to be appended."""

    run_id: str
    type: str
    dedupe_key: str
    stage: str | None = None
    agent_run_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    sequence: int | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        event_type(self.type)
        if not self.dedupe_key:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR,
                "an event must carry a dedupe key; without one a retried activity duplicates it",
                details={"eventType": self.type})

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "sequence": self.sequence,
            "type": self.type,
            "stage": self.stage,
            "agentRunId": self.agent_run_id,
            "payload": dict(self.payload),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
