"""The turn loop: what a run actually does, with every side effect behind a port.

The engine is the whole behaviour of a run — stages in order, turns inside a stage, budgets, the
repair attempt, the tool pause, the events and the final result — and it performs **no I/O of its
own**. Everything that touches the world goes through :class:`Effects`, whose methods correspond
one-to-one with Temporal activities.

That shape is not decoration. Temporal workflow code has to be deterministic: it is replayed from
history, so a call to the clock, to a random generator or to a database inside it produces a
different answer on replay and corrupts the run. Putting the loop here, with the effects injected,
means the same code that the workflow drives can be driven by a deterministic double in the suite —
so the logic is tested without Temporal, and the workflow contains no logic to get wrong.

Three rules the loop enforces, and each is a row of `docs/GATE-2-CHECKLIST.md`:

**Charge before you spend.** The ledger is debited before the call it pays for. A budget checked
afterwards lets a run make the call it could not afford and then discover it.

**One repair, then stop.** An invalid envelope buys exactly one corrective call, which counts
against the budget like any other. A second invalid answer fails the run. There is no loop, and
there is no third attempt hiding behind a different name.

**A tool request is persisted, and then nothing happens.** The run moves to ``WAITING_FOR_TOOL``
and waits. The tool name is never resolved, never looked up and never executed — Gate 3 owns
execution, and this Gate owns the pause.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from typing import Any, Protocol, runtime_checkable

from iacode_agent_runtime.budgets import BudgetLedger
from iacode_agent_runtime.context import assemble
from iacode_agent_runtime.contracts import (
    ModelCallOutcome,
    RunPlan,
    StagePlan,
    ToolResult,
    TurnRequest,
)
from iacode_agent_runtime.errors import (
    AgentRuntimeError,
    AgentRuntimeErrorType,
    InvalidAgentOutputError,
    RunCancelledError,
)
from iacode_agent_runtime.events import RunEvent, safe_payload
from iacode_agent_runtime.limits import RuntimeLimits, enforce_size
from iacode_agent_runtime.ports import StageCompletion
from iacode_agent_runtime.protocol import EnvelopeKind, parse_envelope, repair_instruction
from iacode_agent_runtime.states import RunState

__all__ = ["AgentRunEngine", "Effects", "RunOutcome"]


@runtime_checkable
class Effects(Protocol):
    """Everything the loop needs the world to do for it.

    Each method is one Temporal activity in the worker and one method of a deterministic double in
    the suite. Nothing else in this module reaches outside.
    """

    async def new_id(self) -> str:
        """A fresh identifier. An effect because a workflow may not generate one itself."""

    async def record_event(self, event: RunEvent) -> None: ...

    async def set_state(self, state: str, **fields: Any) -> None: ...

    async def start_stage(self, stage: StagePlan) -> str:
        """Open the agent run for a stage and return its identifier."""

    async def finish_stage(self, agent_run_id: str, completion: StageCompletion) -> None: ...

    async def call_model(self, request: TurnRequest) -> ModelCallOutcome: ...

    async def attach_model_call(self, agent_run_id: str,
                                gateway_request_id: str) -> str | None: ...

    async def create_tool_request(self, tool_request_id: str, agent_run_id: str, name: str,
                                  arguments: dict[str, Any]) -> None: ...

    async def wait_for_tool(self, tool_request_id: str,
                            timeout_seconds: int) -> ToolResult | None:
        """Wait for the answer, or return ``None`` when the wait times out."""

    def cancelled(self) -> bool:
        """Whether a cancellation has been requested. Read, never awaited: the loop checks it
        between steps and a coroutine there would be a scheduling point that changes replay."""


@dataclass
class RunOutcome:
    """What the whole run produced."""

    state: str
    result: str = ""
    result_summary: str = ""
    error_type: str | None = None
    error_summary: str | None = None
    failed_stage: str | None = None
    stages_executed: int = 0
    turns: int = 0
    model_calls: int = 0
    tools_requested: int = 0
    tools_resolved: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "result": self.result,
            "resultSummary": self.result_summary,
            "errorType": self.error_type,
            "errorSummary": self.error_summary,
            "failedStage": self.failed_stage,
            "agentsExecuted": self.stages_executed,
            "turns": self.turns,
            "modelCalls": self.model_calls,
            "toolsRequested": self.tools_requested,
            "toolsResolved": self.tools_resolved,
        }


def _render_tool_result(result: ToolResult) -> str:
    """How a tool result is shown to the agent: as labelled data, never as an instruction."""
    body: dict[str, Any] = {"status": result.status, "output": result.output}
    if result.error:
        body["error"] = result.error
    return json.dumps(body, ensure_ascii=False, sort_keys=True)[:8000]


@dataclass
class AgentRunEngine:
    """One run, from start to terminal state."""

    plan: RunPlan
    effects: Effects
    ledger: BudgetLedger
    limits: RuntimeLimits = field(default_factory=RuntimeLimits)

    _tools_requested: int = 0
    _tools_resolved: int = 0
    _stages_done: int = 0

    # -- the run ---------------------------------------------------------------------------------

    async def execute(self) -> RunOutcome:
        artifacts: dict[str, str] = {}
        stage: StagePlan | None = None
        try:
            await self.effects.set_state(str(RunState.RUNNING), started=True)
            await self._event("RUN_STARTED", "run-started", payload={
                "team": self.plan.team, "teamVersion": self.plan.team_version,
                "stages": len(self.plan.stages)})

            for stage in self.plan.stages:
                self._guard_cancellation(stage.name)
                output = await self._run_stage(stage, artifacts)
                artifacts[stage.output_name] = output
                self._stages_done += 1

            final = artifacts.get(
                self.plan.stages[-1].output_name if self.plan.stages else "", "")
            outcome = self._outcome(str(RunState.SUCCEEDED), result=final)
            # The terminal event is written before the terminal state, never after. They are two
            # commits, and whoever reads between them sees one of the two without the other; the
            # only safe half to see first is the event. A reader that waits for a terminal state
            # and then reads the log — the live smoke, the SSE stream opened on a finished run —
            # otherwise finds a SUCCEEDED run whose log never says so. G2-F-010.
            await self._event("RUN_COMPLETED", "run-completed", payload={
                "agentsExecuted": outcome.stages_executed, "turns": outcome.turns,
                "modelCalls": outcome.model_calls})
            await self.effects.set_state(
                str(RunState.SUCCEEDED), result=final,
                result_summary=_summarise(final),
                budget_used=self.ledger.to_dict(), finished=True)
            return outcome

        except RunCancelledError as cancelled:
            return await self._terminate(
                str(RunState.CANCELLED), cancelled, "RUN_CANCELLED", "run-cancelled",
                stage.name if stage else None)
        except AgentRuntimeError as error:
            return await self._terminate(
                str(RunState.FAILED), error, "RUN_FAILED", "run-failed",
                error.stage or (stage.name if stage else None))

    async def _terminate(self, state: str, error: AgentRuntimeError, event: str, key: str,
                         stage_name: str | None) -> RunOutcome:
        outcome = self._outcome(state, error=error, failed_stage=stage_name)
        # Event first, then state, for the reason the success path gives. G2-F-010.
        await self._event(event, key, stage=stage_name, payload={
            "errorType": str(error.error_type), "message": error.message})
        await self.effects.set_state(
            state, error_type=str(error.error_type), error_summary=error.message,
            failed_stage=stage_name, budget_used=self.ledger.to_dict(), finished=True)
        return outcome

    # -- one stage -------------------------------------------------------------------------------

    async def _run_stage(self, stage: StagePlan, artifacts: dict[str, str]) -> str:
        agent_run_id = await self.effects.start_stage(stage)
        await self._event("AGENT_STARTED", f"agent-started-{stage.index}", stage=stage.name,
                          agent_run_id=agent_run_id, payload={
                              "agent": stage.agent, "profileVersion": stage.profile_version,
                              "promptTemplateVersion": stage.prompt_template_version,
                              "promptTemplateHash": stage.prompt_template_hash,
                              "stageIndex": stage.index})

        stage_turns = 0
        stage_calls = 0
        tool_results: list[tuple[str, str]] = []
        transcript: list[tuple[str, str]] = []
        selected = tuple(
            (name, artifacts[name]) for name in stage.inputs
            if name != "task" and name in artifacts)

        try:
            while True:
                self._guard_cancellation(stage.name)
                if stage_turns >= stage.max_turns:
                    raise AgentRuntimeError(
                        AgentRuntimeErrorType.BUDGET_EXCEEDED,
                        f"stage {stage.name!r} reached its limit of {stage.max_turns} turns",
                        stage=stage.name,
                        details={"limit": "stageMaxTurns", "value": stage.max_turns})
                self.ledger.start_turn(stage=stage.name)
                stage_turns += 1

                context = assemble(
                    role_instructions=stage.role_instructions,
                    task=self.plan.task,
                    artifacts=selected,
                    tool_results=tuple(tool_results),
                    transcript=tuple(transcript),
                    tool_names=stage.allowed_actions,
                    limits=self.limits,
                )
                request = TurnRequest(
                    run_id=self.plan.run_id,
                    stage_index=stage.index,
                    turn=stage_turns,
                    instructions=context.instruction_text,
                    data=context.data_text,
                    route=self.plan.route or stage.default_route,
                    model=self.plan.model,
                    allowed_actions=stage.allowed_actions,
                    structured_output=True,
                )
                envelope, calls = await self._turn(stage, agent_run_id, request)
                stage_calls += len(calls)

                if envelope.kind is EnvelopeKind.TOOL_REQUEST:
                    assert envelope.tool is not None
                    result = await self._tool_pause(stage, agent_run_id, envelope.tool)
                    tool_results.append((result[0], result[1]))
                    continue

                if envelope.kind is EnvelopeKind.MESSAGE:
                    transcript.append((stage.agent, envelope.content))
                    continue

                enforce_size(envelope.content, self.limits.max_agent_output_bytes,
                             what=f"the output of stage {stage.name!r}")
                await self.effects.finish_stage(agent_run_id, StageCompletion(
                    state=str(RunState.SUCCEEDED),
                    output=envelope.content,
                    output_summary=envelope.summary or _summarise(envelope.content),
                    turns=stage_turns,
                    model_calls=stage_calls,
                ))
                await self._event("AGENT_COMPLETED", f"agent-completed-{stage.index}",
                                  stage=stage.name, agent_run_id=agent_run_id, payload={
                                      "agent": stage.agent, "turns": stage_turns,
                                      "modelCalls": stage_calls,
                                      "outputName": stage.output_name,
                                      "summary": envelope.summary or _summarise(
                                          envelope.content)})
                return envelope.content

        except AgentRuntimeError as error:
            await self.effects.finish_stage(agent_run_id, StageCompletion(
                state=str(RunState.CANCELLED if isinstance(error, RunCancelledError)
                          else RunState.FAILED),
                turns=stage_turns,
                model_calls=stage_calls,
                error_type=str(error.error_type),
                error_summary=error.message,
            ))
            raise replace_stage(error, stage.name) from None

    # -- one turn --------------------------------------------------------------------------------

    async def _turn(self, stage: StagePlan, agent_run_id: str, request: TurnRequest):
        """One model call, its parse, and at most one repair."""
        calls: list[ModelCallOutcome] = []
        outcome = await self._call(stage, agent_run_id, request, calls)
        try:
            return parse_envelope(outcome.text), calls
        except InvalidAgentOutputError as first:
            await self._event("RUN_NOTE", f"repair-{stage.index}-{request.turn}",
                              stage=stage.name, agent_run_id=agent_run_id, payload={
                                  "note": "invalid agent output; one repair attempt follows",
                                  "reason": first.message, "repairAttempt": True})
            repair = replace(
                request,
                instructions=request.instructions + "\n\n" + repair_instruction(
                    first.message, tool_names=request.allowed_actions),
                repair_of=f"{stage.index}:{request.turn}",
                structured_output=request.structured_output,
            )
            repaired = await self._call(stage, agent_run_id, repair, calls, repair=True)
            try:
                return parse_envelope(repaired.text), calls
            except InvalidAgentOutputError as second:
                raise AgentRuntimeError(
                    AgentRuntimeErrorType.INVALID_AGENT_OUTPUT,
                    f"the agent answered with an invalid envelope twice: {second.message}",
                    stage=stage.name,
                    details={"repairAttempted": True}) from None

    async def _call(self, stage: StagePlan, agent_run_id: str, request: TurnRequest,
                    calls: list[ModelCallOutcome], *, repair: bool = False) -> ModelCallOutcome:
        self._guard_cancellation(stage.name)
        # Charged before the call, so a run can never make the call it cannot afford. The repair
        # counts exactly like any other call: hiding it outside the budget would make one turn cost
        # two without the budget noticing.
        self.ledger.start_model_call(stage=stage.name, repair=repair)
        await self._event("MODEL_CALL_STARTED", f"call-{stage.index}-{request.turn}-{len(calls)}",
                          stage=stage.name, agent_run_id=agent_run_id, payload={
                              "turn": request.turn, "repairAttempt": repair,
                              "route": request.route, "model": request.model})
        outcome = await self.effects.call_model(request)
        model_call_id = await self.effects.attach_model_call(
            agent_run_id, outcome.gateway_request_id)
        outcome = replace(outcome, model_call_id=model_call_id)
        calls.append(outcome)
        self.ledger.record_usage(outcome.total_tokens, stage=stage.name)
        await self._event("MODEL_CALL_COMPLETED",
                          f"call-done-{stage.index}-{request.turn}-{len(calls)}",
                          stage=stage.name, agent_run_id=agent_run_id,
                          payload={k: v for k, v in outcome.to_dict().items() if k != "text"})
        return outcome

    # -- the tool pause ---------------------------------------------------------------------------

    async def _tool_pause(self, stage: StagePlan, agent_run_id: str, tool) -> tuple[str, str]:
        """Persist the request, pause the run, and wait. Nothing here executes anything.

        The tool name is a string that is stored and compared against the profile's permitted set.
        It is never resolved to a path, an executable, a shell command or an import.
        """
        if not stage.allowed_actions or tool.name not in stage.allowed_actions:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.TOOL_NOT_PERMITTED,
                f"agent {stage.agent!r} requested {tool.name!r}, which its profile does not permit",
                stage=stage.name,
                details={"requested": tool.name,
                         "permitted": list(stage.allowed_actions)})
        enforce_size(tool.arguments, self.limits.max_tool_arguments_bytes,
                     what=f"the arguments of tool {tool.name!r}")

        tool_request_id = await self.effects.new_id()
        await self.effects.create_tool_request(
            tool_request_id, agent_run_id, tool.name, dict(tool.arguments))
        self._tools_requested += 1
        await self._event("TOOL_REQUESTED", f"tool-requested-{tool_request_id}",
                          stage=stage.name, agent_run_id=agent_run_id, payload={
                              "toolRequestId": tool_request_id, "tool": tool.name,
                              "argumentCount": len(tool.arguments)})
        await self.effects.set_state(str(RunState.WAITING_FOR_TOOL), current_stage=stage.name)

        result = await self.effects.wait_for_tool(
            tool_request_id, self.plan.budget.tool_wait_timeout_seconds)
        if result is None:
            if self.effects.cancelled():
                raise RunCancelledError(stage=stage.name)
            raise AgentRuntimeError(
                AgentRuntimeErrorType.TOOL_WAIT_TIMEOUT,
                f"no result arrived for tool {tool.name!r} within "
                f"{self.plan.budget.tool_wait_timeout_seconds}s",
                stage=stage.name,
                details={"toolRequestId": tool_request_id, "tool": tool.name})

        enforce_size(result.output, self.limits.max_tool_result_bytes,
                     what=f"the result of tool {tool.name!r}")
        self._tools_resolved += 1
        await self.effects.set_state(str(RunState.RUNNING), current_stage=stage.name)
        await self._event("TOOL_RESULT_RECEIVED", f"tool-result-{tool_request_id}",
                          stage=stage.name, agent_run_id=agent_run_id, payload={
                              "toolRequestId": tool_request_id, "tool": tool.name,
                              "status": result.status})
        return tool_request_id, _render_tool_result(result)

    # -- helpers ----------------------------------------------------------------------------------

    def _guard_cancellation(self, stage_name: str | None) -> None:
        if self.effects.cancelled():
            raise RunCancelledError(stage=stage_name)

    async def _event(self, event_type: str, key: str, *, stage: str | None = None,
                     agent_run_id: str | None = None,
                     payload: dict[str, Any] | None = None) -> None:
        await self.effects.record_event(RunEvent(
            run_id=self.plan.run_id,
            type=event_type,
            dedupe_key=key,
            stage=stage,
            agent_run_id=agent_run_id,
            payload=safe_payload(payload, self.limits),
        ))

    def _outcome(self, state: str, *, result: str = "",
                 error: AgentRuntimeError | None = None,
                 failed_stage: str | None = None) -> RunOutcome:
        return RunOutcome(
            state=state,
            result=result,
            result_summary=_summarise(result) if result else "",
            error_type=str(error.error_type) if error else None,
            error_summary=error.message if error else None,
            failed_stage=failed_stage,
            stages_executed=self._stages_done,
            turns=self.ledger.turns_used,
            model_calls=self.ledger.model_calls_used,
            tools_requested=self._tools_requested,
            tools_resolved=self._tools_resolved,
        )


def replace_stage(error: AgentRuntimeError, stage: str | None) -> AgentRuntimeError:
    """The same failure, with the stage it happened in recorded on it."""
    if error.stage or stage is None:
        return error
    error.stage = stage
    return error


def _summarise(text: str, limit: int = 240) -> str:
    """A short, verifiable statement of what a run or a stage produced.

    The first line, truncated. It is a pointer to the result, not a description of how the result
    was reached: the Development Contract forbids storing private reasoning, and a "summary" that
    narrated the model's deliberation would be exactly that under another name.
    """
    first = (text or "").strip().splitlines()
    if not first:
        return ""
    value = first[0].strip()
    return value if len(value) <= limit else value[: limit - 1] + "…"
