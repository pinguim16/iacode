"""The contracts that cross a boundary: the plan, the tool request, the tool result, the limits."""

from __future__ import annotations

import dataclasses

import pytest
from iacode_agent_runtime.budgets import Budget
from iacode_agent_runtime.contracts import (
    ModelCallOutcome,
    RunPlan,
    ToolRequest,
    ToolResult,
)
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.limits import RuntimeLimits, enforce_size, payload_size
from iacode_contracts.agent_runtime import TOOL_REQUEST_STATUSES, TOOL_RESULT_STATUSES
from runtime_doubles import plan_for, stage


class ToolRequestContractTests:
    """Identity, run, agent, name, arguments, creation time and a declared status."""

    def test_a_request_carries_the_declared_fields(self) -> None:
        request = ToolRequest(
            tool_request_id="tr-1", run_id="run-1", agent_run_id="ar-1",
            name="repo.read", arguments={"path": "README.md"})
        rendered = request.to_dict()
        assert set(rendered) >= {
            "toolRequestId", "runId", "agentRunId", "name", "arguments", "status", "createdAt"}
        assert rendered["status"] == "PENDING"

    def test_the_status_vocabulary_is_closed(self) -> None:
        assert TOOL_REQUEST_STATUSES == ("PENDING", "RESOLVED", "REJECTED", "CANCELLED")
        with pytest.raises(AgentRuntimeError):
            ToolRequest(tool_request_id="tr-1", run_id="run-1", agent_run_id=None,
                        name="x", arguments={}, status="RUNNING")

    def test_a_request_round_trips(self) -> None:
        request = ToolRequest(tool_request_id="tr-1", run_id="run-1", agent_run_id=None,
                              name="repo.read", arguments={"path": "a"})
        again = ToolRequest.from_dict(request.to_dict())
        assert again.name == "repo.read"
        assert again.arguments == {"path": "a"}


class ToolResultContractTests:
    """The request it answers, a status, an output, an error and metadata."""

    def test_a_result_carries_the_declared_fields(self) -> None:
        result = ToolResult(tool_request_id="tr-1", status="SUCCEEDED",
                            output={"stdout": "ok"}, metadata={"by": "fixture"})
        rendered = result.to_dict()
        assert set(rendered) == {"toolRequestId", "status", "output", "error", "metadata"}
        assert result.succeeded

    def test_the_status_vocabulary_is_closed(self) -> None:
        assert TOOL_RESULT_STATUSES == ("SUCCEEDED", "FAILED", "DENIED", "TIMED_OUT")
        with pytest.raises(AgentRuntimeError) as raised:
            ToolResult(tool_request_id="tr-1", status="OK")
        assert raised.value.error_type is AgentRuntimeErrorType.TOOL_RESULT_INVALID

    def test_a_failed_result_is_not_a_success(self) -> None:
        assert not ToolResult(tool_request_id="tr-1", status="DENIED").succeeded

    def test_a_result_round_trips(self) -> None:
        result = ToolResult(tool_request_id="tr-1", status="FAILED", error="no such path")
        assert ToolResult.from_dict(result.to_dict()).error == "no such path"


def test_workflow_plan_is_frozen_at_creation() -> None:
    """The plan a workflow carries cannot be edited, so a profile change cannot reach a live run."""
    plan = plan_for(stage())
    # `FrozenInstanceError`, named rather than caught blind: a blind assertion passes when the
    # attribute does not exist either, which is the opposite of what this asserts.
    with pytest.raises(dataclasses.FrozenInstanceError):
        plan.task = "something else"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        plan.stages[0].role_instructions = "be evil"  # type: ignore[misc]


def test_a_plan_round_trips_across_the_workflow_boundary() -> None:
    plan = plan_for(stage(0, "plan", "planner", output_name="plan"),
                    stage(1, "review", "reviewer", inputs=("task", "plan"),
                          output_name="review"),
                    budget=Budget(max_turns=3, max_model_calls=4), route="balanced")
    restored = RunPlan.from_dict(plan.to_dict())
    assert restored.to_dict() == plan.to_dict()
    assert restored.stage(1).agent == "reviewer"
    assert restored.route == "balanced"


def test_a_plan_refuses_a_stage_it_does_not_have() -> None:
    with pytest.raises(AgentRuntimeError):
        plan_for(stage()).stage(9)


def test_route_and_model_override_are_passed_through() -> None:
    """The runtime carries them; the gateway decides. Nothing here parses provider metadata."""
    plan = plan_for(stage(), route=None, model="devworld:some-model")
    assert plan.model == "devworld:some-model"
    assert RunPlan.from_dict(plan.to_dict()).model == "devworld:some-model"


def test_unknown_cost_is_unknown_not_zero() -> None:
    outcome = ModelCallOutcome(
        text="x", model_call_id=None, provider="double", model="m", endpoint="e",
        route_reason="DEFAULT_MODEL", finish_reason="STOP", latency_ms=1.0)
    assert outcome.cost is None
    assert outcome.cost_known is False
    assert outcome.to_dict()["cost"] is None


def test_identifiers_use_the_existing_strategy() -> None:
    """One generator, the repository's own, rather than a second format for this Gate."""
    import uuid

    from iacode_agent_runtime.persistence import new_identifier

    value = uuid.UUID(new_identifier())
    assert value.version == 7


class PayloadLimitTests:
    """Tool arguments, agent output, tool results and events are all bounded."""

    def test_every_limit_is_positive(self) -> None:
        limits = RuntimeLimits()
        for name in ("max_task_bytes", "max_agent_output_bytes", "max_tool_arguments_bytes",
                     "max_tool_result_bytes", "max_event_payload_bytes", "max_context_bytes"):
            assert getattr(limits, name) > 0

    def test_a_limit_of_zero_is_refused(self) -> None:
        with pytest.raises(AgentRuntimeError):
            RuntimeLimits(max_task_bytes=0)

    def test_size_is_measured_the_same_way_everywhere(self) -> None:
        assert payload_size("abc") == 3
        assert payload_size("é") == 2
        assert payload_size({"a": 1}) == len('{"a": 1}')

    def test_an_oversized_payload_is_refused_and_not_echoed(self) -> None:
        with pytest.raises(AgentRuntimeError) as raised:
            enforce_size("secret-value-" + "x" * 100, 16, what="the tool result")
        assert raised.value.error_type is AgentRuntimeErrorType.PAYLOAD_TOO_LARGE
        assert "secret-value" not in raised.value.message
        assert raised.value.details["limit"] == 16

    def test_a_payload_within_the_limit_passes(self) -> None:
        enforce_size({"a": "b"}, 1024, what="the tool arguments")


class SandboxPlanContractTests:
    """GATE 3: a stage carries the sandbox policy its tools run under, and a run its workspace."""

    def test_the_sandbox_policy_and_the_workspace_round_trip(self) -> None:
        sandboxed = dataclasses.replace(stage(allowed_actions=("filesystem.read",)),
                                        sandbox_policy="developer")
        plan = dataclasses.replace(
            plan_for(sandboxed),
            workspace={"kind": "snapshot", "artifactId": "a1", "checksum": "0" * 64})
        restored = RunPlan.from_dict(plan.to_dict())
        assert restored.stage(0).sandbox_policy == "developer"
        assert restored.workspace == {"kind": "snapshot", "artifactId": "a1",
                                      "checksum": "0" * 64}

    def test_a_gate_two_plan_still_reads_as_one(self) -> None:
        """A plan serialised before GATE 3 has neither field and keeps Gate 2's meaning."""
        payload = plan_for(stage()).to_dict()
        payload.pop("workspace")
        for item in payload["stages"]:
            item.pop("sandboxPolicy")
        restored = RunPlan.from_dict(payload)
        assert restored.stage(0).sandbox_policy is None
        assert restored.workspace == {}
