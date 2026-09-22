"""The run state machine.

The transition table is data, so these walk it rather than naming a handful of examples. A
transition added to the contract is covered the moment it exists, and one removed stops being
asserted — which is the difference between a test of the rule and a test of today's rule.
"""

from __future__ import annotations

import pytest
from iacode_agent_runtime.errors import InvalidStateTransitionError
from iacode_agent_runtime.states import (
    TERMINAL_STATES,
    RunState,
    allowed_transitions,
    assert_transition,
    can_transition,
    forbidden_transitions,
    is_terminal,
)
from iacode_contracts.agent_runtime import (
    AGENT_RUN_STATES,
    ALLOWED_RUN_TRANSITIONS,
    TERMINAL_RUN_STATES,
)


def test_declared_states_are_exactly_the_contract() -> None:
    """No state exists that the shared vocabulary does not name, and none is missing."""
    assert tuple(str(state) for state in RunState) == AGENT_RUN_STATES
    assert set(TERMINAL_STATES) == set(TERMINAL_RUN_STATES)
    assert set(allowed_transitions()) == set(AGENT_RUN_STATES)


def test_state_machine_has_one_definition() -> None:
    """The enum, the table and the database vocabulary come from the same tuple.

    `docs/GATE-2-CHECKLIST.md` row 4.7. A second list somewhere is a second list that grows a value
    the first one does not have.
    """
    from iacode_persistence.models import RUN_STATUSES

    assert allowed_transitions() == {
        state: tuple(targets) for state, targets in ALLOWED_RUN_TRANSITIONS.items()}
    assert set(AGENT_RUN_STATES).issubset(set(RUN_STATUSES))


class RunStateMachineTests:
    """Every permitted move is applied and every other move is refused."""

    def test_every_permitted_transition_is_applied(self) -> None:
        moves = 0
        for source, targets in allowed_transitions().items():
            for target in targets:
                assert can_transition(source, target)
                assert assert_transition(source, target) == RunState(target)
                moves += 1
        assert moves >= 12, "the table describes fewer transitions than the lifecycle needs"

    def test_every_forbidden_transition_is_refused(self) -> None:
        refused = 0
        for source, target in forbidden_transitions():
            assert not can_transition(source, target)
            with pytest.raises(InvalidStateTransitionError):
                assert_transition(source, target)
            refused += 1
        assert refused > 0, "the derivation produced no forbidden transition to check"

    def test_the_happy_path_is_reachable(self) -> None:
        """A positive control: the lifecycle a successful run actually walks."""
        state = RunState.CREATED
        for target in (RunState.QUEUED, RunState.RUNNING, RunState.WAITING_FOR_TOOL,
                       RunState.RUNNING, RunState.SUCCEEDED):
            state = assert_transition(state, target)
        assert state is RunState.SUCCEEDED


def test_impossible_transition_is_refused() -> None:
    """The one the engineering memory cares about: a finished run being restarted."""
    with pytest.raises(InvalidStateTransitionError) as raised:
        assert_transition(RunState.SUCCEEDED, RunState.RUNNING)
    assert "terminal" in str(raised.value)


def test_terminal_state_never_transitions() -> None:
    for state in TERMINAL_RUN_STATES:
        assert is_terminal(state)
        assert allowed_transitions()[state] == ()
        for target in AGENT_RUN_STATES:
            assert not can_transition(state, target)


def test_an_unknown_state_moves_nowhere() -> None:
    with pytest.raises(InvalidStateTransitionError):
        assert_transition("SLEEPING", RunState.RUNNING)
    with pytest.raises(InvalidStateTransitionError):
        assert_transition(RunState.RUNNING, "SLEEPING")
