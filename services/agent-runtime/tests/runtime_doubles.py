"""Deterministic doubles: a model that answers from a script, and effects that remember.

Two objects, and both exist so the engine can be exercised without a provider, without a database
and without Temporal.

:class:`ScriptedModel` answers each call with the next entry of a script. A script entry is either
the text the model "produced" or an exception to raise, so an invalid envelope, a gateway failure
and a well-behaved agent are all expressed the same way. It records every request it received,
which is how a test asserts what was *in* a prompt rather than only what came out of one.

:class:`RecordingEffects` is the engine's world. It keeps the states, the events, the stages and
the tool requests in memory, applies the same state machine the real store applies, and exposes
what happened as plain lists. A double that accepted any transition would let the engine's tests
pass while the real store refused the same sequence, so it asks
:func:`~iacode_agent_runtime.states.assert_transition` exactly as the SQL store does.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from iacode_agent_runtime.contracts import (
    ModelCallOutcome,
    RunPlan,
    StagePlan,
    ToolResult,
    TurnRequest,
)
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.events import RunEvent
from iacode_agent_runtime.ports import StageCompletion
from iacode_agent_runtime.protocol import ENVELOPE_VERSION
from iacode_agent_runtime.states import assert_transition

__all__ = [
    "RecordingEffects",
    "ScriptedModel",
    "envelope",
    "plan_for",
    "repository_root",
    "stage",
    "tool_envelope",
]


def envelope(kind: str = "FINAL", content: str = "done", summary: str = "") -> str:
    """One valid envelope, rendered as a model would emit it."""
    import json

    body: dict[str, Any] = {"version": ENVELOPE_VERSION, "kind": kind, "content": content}
    if summary:
        body["summary"] = summary
    return json.dumps(body)


def tool_envelope(name: str, **arguments: Any) -> str:
    """A tool request envelope. Nothing that reads it will execute anything."""
    import json

    return json.dumps({
        "version": ENVELOPE_VERSION,
        "kind": "TOOL_REQUEST",
        "tool": {"name": name, "arguments": arguments},
    })


def stage(index: int = 0, name: str = "answer", agent: str = "generalist", *,
          inputs: tuple[str, ...] = ("task",), output_name: str = "answer",
          max_turns: int = 4, allowed_actions: tuple[str, ...] = ()) -> StagePlan:
    return StagePlan(
        index=index,
        name=name,
        agent=agent,
        agent_name=agent.title(),
        role_instructions=f"# Role: {agent}\n\nAnswer the task.",
        inputs=inputs,
        output_name=output_name,
        max_turns=max_turns,
        allowed_actions=allowed_actions,
        profile_version="1.0.0",
        prompt_template=f"agents/prompts/{agent}.v1.md",
        prompt_template_version="v1",
        prompt_template_hash="0" * 64,
    )


def plan_for(*stages: StagePlan, task: str = "Say IACODE_AGENT_OK.", run_id: str = "run-1",
             budget=None, route: str | None = None, model: str | None = None) -> RunPlan:
    from iacode_agent_runtime.budgets import Budget

    return RunPlan(
        run_id=run_id,
        task_id="task-1",
        task=task,
        team="test-team",
        team_version="1.0.0",
        stages=stages or (stage(),),
        budget=budget or Budget(),
        route=route,
        model=model,
    )


@dataclass
class ScriptedModel:
    """A model that answers from a script and remembers every request."""

    script: list[Any] = field(default_factory=list)
    requests: list[TurnRequest] = field(default_factory=list)
    default: str | None = None
    provider: str = "double"
    model: str = "scripted"
    total_tokens: int | None = 12

    async def complete(self, request: TurnRequest) -> ModelCallOutcome:
        self.requests.append(request)
        if self.script:
            answer = self.script.pop(0)
        elif self.default is not None:
            answer = self.default
        else:
            raise AssertionError(
                "the scripted model ran out of answers; the engine asked for a turn the test did "
                "not expect")
        if isinstance(answer, BaseException):
            raise answer
        if callable(answer):
            answer = answer(request)
        return ModelCallOutcome(
            text=str(answer),
            model_call_id=None,
            gateway_request_id=f"gwr-{len(self.requests)}",
            provider=self.provider,
            model=self.model,
            endpoint="openai-chat-completions",
            route_reason="DEFAULT_MODEL",
            finish_reason="STOP",
            latency_ms=1.0,
            total_tokens=self.total_tokens,
            input_tokens=None if self.total_tokens is None else self.total_tokens // 2,
            output_tokens=None if self.total_tokens is None else self.total_tokens // 2,
            cost=None,
            cost_known=False,
            repair_attempt=request.repair_of is not None,
        )

    @property
    def calls(self) -> int:
        return len(self.requests)


@dataclass
class RecordingEffects:
    """The engine's world, in memory, enforcing the same state machine the real store does."""

    model: ScriptedModel
    state: str = "QUEUED"
    states: list[str] = field(default_factory=list)
    events: list[RunEvent] = field(default_factory=list)
    stages_started: list[StagePlan] = field(default_factory=list)
    completions: list[tuple[str, StageCompletion]] = field(default_factory=list)
    tool_requests: list[dict[str, Any]] = field(default_factory=list)
    tool_answers: dict[str, ToolResult] = field(default_factory=dict)
    attached: list[tuple[str, str]] = field(default_factory=list)
    cancel: bool = False
    cancel_after_events: int | None = None
    tool_wait_returns_none: bool = False
    waits: list[tuple[str, int]] = field(default_factory=list)
    #: The event types the log held at each state change: which of the two a reader sees first.
    log_at_state: list[tuple[str, tuple[str, ...]]] = field(default_factory=list)
    _identifiers: int = 0
    _sequence: int = 0

    # -- effects ---------------------------------------------------------------------------------

    async def new_id(self) -> str:
        self._identifiers += 1
        return f"tool-request-{self._identifiers}"

    async def record_event(self, event: RunEvent) -> None:
        if any(existing.dedupe_key == event.dedupe_key for existing in self.events):
            return
        self._sequence += 1
        object.__setattr__(event, "sequence", self._sequence)
        self.events.append(event)
        if (self.cancel_after_events is not None
                and len(self.events) >= self.cancel_after_events):
            self.cancel = True

    async def set_state(self, state: str, **fields: Any) -> None:
        self.log_at_state.append((state, tuple(self.event_types())))
        if state != self.state:
            assert_transition(self.state, state)
            self.state = state
        self.states.append(state)

    async def start_stage(self, stage_plan: StagePlan) -> str:
        self.stages_started.append(stage_plan)
        return f"agent-run-{stage_plan.index}"

    async def finish_stage(self, agent_run_id: str, completion: StageCompletion) -> None:
        self.completions.append((agent_run_id, completion))

    async def call_model(self, request: TurnRequest) -> ModelCallOutcome:
        if self.cancel:
            raise AssertionError("the engine called a model after cancellation was requested")
        return await self.model.complete(request)

    async def attach_model_call(self, agent_run_id: str,
                                gateway_request_id: str) -> str | None:
        self.attached.append((agent_run_id, gateway_request_id))
        return f"model-call-{len(self.attached)}"

    async def create_tool_request(self, tool_request_id: str, agent_run_id: str, name: str,
                                  arguments: dict[str, Any]) -> None:
        self.tool_requests.append({
            "toolRequestId": tool_request_id, "agentRunId": agent_run_id,
            "name": name, "arguments": dict(arguments)})

    async def wait_for_tool(self, tool_request_id: str,
                            timeout_seconds: int) -> ToolResult | None:
        self.waits.append((tool_request_id, timeout_seconds))
        if self.tool_wait_returns_none or self.cancel:
            return None
        answer = self.tool_answers.get(tool_request_id)
        if answer is None:
            raise AssertionError(
                f"the engine waited on {tool_request_id} and the test scripted no answer")
        return answer

    def cancelled(self) -> bool:
        return self.cancel

    # -- reading ---------------------------------------------------------------------------------

    def event_types(self) -> list[str]:
        return [event.type for event in self.events]

    def events_of(self, event_type: str) -> list[RunEvent]:
        return [event for event in self.events if event.type == event_type]


def gateway_failure(message: str = "the provider is unavailable") -> AgentRuntimeError:
    """A gateway failure shaped exactly as the real client raises one."""
    return AgentRuntimeError(
        AgentRuntimeErrorType.GATEWAY_ERROR, message, upstream_type="PROVIDER_UNAVAILABLE")


def repository_root() -> Path:
    """Where ``agents/`` lives, found by looking rather than by being told.

    In a checkout the definitions are at the repository root; in the API image they are at ``/app``,
    beside the suite. Walking up until the directory appears makes one helper serve both, which is
    better than a constant that is correct in one of the two places the suite runs.
    """
    for candidate in (Path(__file__).resolve(), *Path(__file__).resolve().parents):
        if (candidate / "agents" / "profiles").is_dir():
            return candidate
    raise AssertionError("no agents/profiles directory was found above the suite")
