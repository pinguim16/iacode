"""The run event log: a closed vocabulary, a dedupe key, and payloads that carry facts."""

from __future__ import annotations

import pytest
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.events import EVENT_TYPES, RunEvent, event_type, safe_payload
from iacode_agent_runtime.limits import RuntimeLimits
from iacode_contracts.agent_runtime import RUN_EVENT_TYPES


def test_event_vocabulary_covers_the_declared_moments() -> None:
    """Run creation and start, agent start and completion, the model call, the tool, the end."""
    for required in (
        "RUN_CREATED", "RUN_STARTED", "AGENT_STARTED", "MODEL_CALL_STARTED",
        "MODEL_CALL_COMPLETED", "TOOL_REQUESTED", "TOOL_RESULT_RECEIVED", "AGENT_COMPLETED",
        "RUN_COMPLETED", "RUN_FAILED", "RUN_CANCELLED",
    ):
        assert required in EVENT_TYPES
    assert set(EVENT_TYPES) == set(RUN_EVENT_TYPES)


def test_the_vocabulary_is_closed() -> None:
    with pytest.raises(AgentRuntimeError) as raised:
        event_type("RUN_ALMOST_FINISHED")
    assert raised.value.error_type is AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR


def test_an_event_must_carry_a_dedupe_key() -> None:
    """Without it a retried activity grows the history a second copy of the same moment."""
    with pytest.raises(AgentRuntimeError):
        RunEvent(run_id="run-1", type="RUN_STARTED", dedupe_key="")


FORBIDDEN_PAYLOAD_KEYS = (
    "reasoning", "chain_of_thought", "chainOfThought", "thoughts", "prompt", "messages",
    "completion", "raw_output", "transcript", "api_key", "secret", "authorization",
)


def test_event_payload_carries_no_private_reasoning() -> None:
    """Refused rather than truncated: a truncated prompt is still a prompt.

    Written as a loop rather than as a parametrisation: the TESTS denominator is derived
    statically from the source, and a runtime expansion cannot be counted that way.
    """
    for key in FORBIDDEN_PAYLOAD_KEYS:
        with pytest.raises(AgentRuntimeError) as raised:
            safe_payload({key: "something"})
        assert raised.value.error_type is AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR, key


def test_a_forbidden_key_is_refused_at_any_depth() -> None:
    with pytest.raises(AgentRuntimeError):
        safe_payload({"outer": {"inner": {"reasoning": "x"}}})


def test_a_payload_keeps_the_facts_it_is_allowed_to_carry() -> None:
    payload = safe_payload({
        "turn": 2, "repairAttempt": False, "latencyMs": 12.5, "tool": "repo.read",
        "rejected": ["a", "b"], "nested": {"provider": "double"}, "missing": None})
    assert payload["turn"] == 2
    assert payload["repairAttempt"] is False
    assert payload["latencyMs"] == 12.5
    assert payload["rejected"] == ["a", "b"]
    assert payload["nested"] == {"provider": "double"}
    assert payload["missing"] is None


def test_a_long_string_in_a_payload_is_truncated_rather_than_stored_whole() -> None:
    payload = safe_payload({"note": "x" * 5000})
    assert len(payload["note"]) <= 512


def test_oversized_event_payload_is_refused() -> None:
    with pytest.raises(AgentRuntimeError) as raised:
        safe_payload({f"key{index}": "y" * 400 for index in range(200)},
                     RuntimeLimits(max_event_payload_bytes=1024))
    assert raised.value.error_type is AgentRuntimeErrorType.PAYLOAD_TOO_LARGE


def test_an_event_renders_what_a_consumer_reads() -> None:
    event = RunEvent(run_id="run-1", type="AGENT_STARTED", dedupe_key="agent-started-0",
                     stage="plan", agent_run_id="agent-1", payload={"agent": "planner"},
                     sequence=4)
    rendered = event.to_dict()
    assert rendered["runId"] == "run-1"
    assert rendered["sequence"] == 4
    assert rendered["stage"] == "plan"
    assert rendered["payload"] == {"agent": "planner"}
