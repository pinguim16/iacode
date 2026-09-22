"""The run state machine.

Seven states and one transition table, both derived from `iacode_contracts.agent_runtime` so that
the API, the workflow, the database constraint and the browser all describe the same lifecycle. A
transition written as an ``if`` inside the code that performs it is a transition no test can
enumerate; a table can be walked, and :func:`forbidden_transitions` walks it to produce exactly the
moves that must fail.

Two properties this module exists to guarantee.

**An impossible transition raises.** It does not log, it does not coerce and it does not silently
win. `docs/GATE-2-CHECKLIST.md` row 4.3 asks for a refusal, because a runtime that accepts
``SUCCEEDED -> RUNNING`` can be made to resurrect a finished run by replaying one message.

**A terminal state is terminal.** ``SUCCEEDED``, ``FAILED`` and ``CANCELLED`` have no outgoing
edges at all, so a late tool result, a redelivered signal or a retried activity cannot restart a run
that is over. Another attempt is another run.
"""

from __future__ import annotations

from enum import StrEnum

from iacode_contracts.agent_runtime import (
    AGENT_RUN_STATES,
    ALLOWED_RUN_TRANSITIONS,
    TERMINAL_RUN_STATES,
)

from iacode_agent_runtime.errors import InvalidStateTransitionError

__all__ = [
    "TERMINAL_STATES",
    "RunState",
    "allowed_transitions",
    "assert_transition",
    "can_transition",
    "forbidden_transitions",
    "is_terminal",
]


#: The states, built from the shared tuple rather than typed a second time. Building the enum this
#: way means a value added to the contract is a value this enum has, and one removed is a name error
#: here, rather than a silent divergence that only the database constraint would notice.
RunState = StrEnum("RunState", {state: state for state in AGENT_RUN_STATES})

TERMINAL_STATES: frozenset[str] = frozenset(TERMINAL_RUN_STATES)


def allowed_transitions() -> dict[str, tuple[str, ...]]:
    """The transition table, as data."""
    return {state: tuple(targets) for state, targets in ALLOWED_RUN_TRANSITIONS.items()}


def is_terminal(state: str | RunState) -> bool:
    return str(state) in TERMINAL_STATES


def can_transition(current: str | RunState, target: str | RunState) -> bool:
    """Whether the table permits the move. A state it does not know cannot move anywhere."""
    return str(target) in ALLOWED_RUN_TRANSITIONS.get(str(current), ())


def assert_transition(current: str | RunState, target: str | RunState) -> RunState:
    """Apply a transition or refuse it.

    Returning the target rather than ``None`` is deliberate: the caller assigns what this function
    returns, so there is no path where a caller forgets to check and assigns anyway.
    """
    if str(current) not in ALLOWED_RUN_TRANSITIONS:
        raise InvalidStateTransitionError(
            f"{current!s} is not a state this runtime knows",
            details={"from": str(current), "to": str(target)})
    if str(target) not in ALLOWED_RUN_TRANSITIONS:
        raise InvalidStateTransitionError(
            f"{target!s} is not a state this runtime knows",
            details={"from": str(current), "to": str(target)})
    if not can_transition(current, target):
        detail = "a terminal run never runs again" if is_terminal(current) else "not permitted"
        raise InvalidStateTransitionError(
            f"{current!s} -> {target!s} is refused: {detail}",
            details={"from": str(current), "to": str(target)})
    return RunState(str(target))


def forbidden_transitions() -> tuple[tuple[str, str], ...]:
    """Every move the table does not allow, derived rather than listed.

    The adversarial suite walks this instead of naming a handful of examples, so a transition added
    to the table is covered the moment it exists and one removed stops being asserted.
    """
    return tuple(
        (source, target)
        for source in AGENT_RUN_STATES
        for target in AGENT_RUN_STATES
        if target not in ALLOWED_RUN_TRANSITIONS.get(source, ())
    )
