"""The ports the agent runtime needs from the outside, declared by the runtime.

The dependency points inward. The application composes a runtime and hands it a store and a model
client; the runtime knows nothing about SQLAlchemy, nothing about FastAPI and nothing about
Temporal. If the arrow pointed the other way, ``iacode_agent_runtime`` would import the web
application, and the worker — which has no web application — could not use it.

The model client is a port for a second reason. It is the **only** way to reach a model, and having
it as a named interface is what makes "the runtime never talks to a provider" something a test can
assert rather than something a reviewer has to notice. The real implementation wraps the Gate 1
gateway; the suite's implementation is a deterministic double that answers from a script.

``Clock`` exists so a deadline test does not sleep. A test that waits fifteen minutes is a test that
gets deleted.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol, runtime_checkable

from iacode_contracts.agent_runtime import TOOL_EXECUTOR_EXTERNAL

from iacode_agent_runtime.contracts import (
    ModelCallOutcome,
    ToolRequest,
    ToolResult,
    TurnRequest,
)
from iacode_agent_runtime.events import RunEvent

__all__ = [
    "AgentRunRecord",
    "AgentRunStore",
    "Clock",
    "ModelClient",
    "RealClock",
    "RunRecord",
    "StageCompletion",
]


@dataclass(frozen=True)
class RunRecord:
    """A run as the store keeps it."""

    run_id: str
    task_id: str
    state: str
    team: str
    task: str
    workflow_id: str | None = None
    current_stage: str | None = None
    cancel_requested: bool = False
    budget: dict[str, Any] = field(default_factory=dict)
    budget_used: dict[str, Any] = field(default_factory=dict)
    result: str | None = None
    error_type: str | None = None
    created_at: datetime | None = None


@dataclass(frozen=True)
class AgentRunRecord:
    """One stage's execution as the store keeps it."""

    agent_run_id: str
    run_id: str
    stage_index: int
    stage_name: str
    agent: str
    state: str


@dataclass(frozen=True)
class StageCompletion:
    """What a finished stage recorded. No private reasoning; a short summary and the output."""

    state: str
    output: str = ""
    output_summary: str = ""
    turns: int = 0
    model_calls: int = 0
    error_type: str | None = None
    error_summary: str | None = None


@runtime_checkable
class AgentRunStore(Protocol):
    """Where a run, its stages, its events and its tool interactions live."""

    async def load_run(self, run_id: str) -> RunRecord | None:
        """The run, or ``None`` when no such run exists."""

    async def set_run_state(
        self,
        run_id: str,
        state: str,
        *,
        current_stage: str | None = None,
        budget_used: dict[str, Any] | None = None,
        result: str | None = None,
        result_summary: str | None = None,
        error_type: str | None = None,
        error_summary: str | None = None,
        failed_stage: str | None = None,
        workflow_id: str | None = None,
        started: bool = False,
        finished: bool = False,
    ) -> str:
        """Apply a state transition, refusing one the state machine does not allow.

        Returns the state the run now holds. The store performs the check rather than trusting the
        caller, because the caller is sometimes a retried activity that believes stale state.
        """

    async def append_event(self, event: RunEvent) -> RunEvent:
        """Append one event and return it with the sequence the store assigned.

        Idempotent on ``dedupe_key``: appending the same occurrence twice returns the first event
        and creates nothing.
        """

    async def read_events(self, run_id: str, *, after: int = 0,
                          limit: int = 500) -> list[RunEvent]:
        """Events of a run after a cursor, in sequence order."""

    async def start_stage(self, run_id: str, *, stage_index: int, stage_name: str,
                          agent: str, profile_version: str, prompt_template_version: str,
                          prompt_template_hash: str, output_name: str) -> AgentRunRecord:
        """Create or reopen the agent run for one stage. Idempotent per (run, stage index)."""

    async def finish_stage(self, agent_run_id: str, completion: StageCompletion) -> None:
        """Record what a stage produced."""

    async def create_tool_request(self, run_id: str, *, agent_run_id: str | None, name: str,
                                  arguments: dict[str, Any], tool_request_id: str,
                                  executor: str = TOOL_EXECUTOR_EXTERNAL) -> ToolRequest:
        """Persist a tool request with the executor that owns it. Idempotent on the identifier
        the caller supplies; the executor is written once and never changed."""

    async def pending_tool_request(self, run_id: str) -> ToolRequest | None:
        """The request this run is waiting on, if any."""

    async def resolve_tool_request(self, run_id: str, result: ToolResult, *,
                                   origin: str) -> ToolResult:
        """Record the answer to a tool request, delivered by ``origin``.

        Refuses a request that belongs to another run, does not exist, or is no longer pending,
        and a result whose ``origin`` is not the executor that owns the request; is idempotent
        when the owning executor delivers the same result twice. ``origin`` is supplied by the
        caller's own code path - the API passes ``EXTERNAL``, the workflow's internal activity
        passes ``SANDBOX`` - and never read from the result.
        """

    async def attach_model_call(self, agent_run_id: str, gateway_request_id: str) -> str | None:
        """Attribute the gateway's own record of a call to the agent run that caused it.

        The gateway owns ``model_calls``: it writes what the call cost and how long it took, and it
        is the authoritative source of that usage. The runtime adds the link and reads the totals
        back from there rather than keeping a second count of its own.
        """


@runtime_checkable
class ModelClient(Protocol):
    """The only way the runtime reaches a model."""

    async def complete(self, request: TurnRequest) -> ModelCallOutcome:
        """Run one turn and return what the model produced, normalised."""


@runtime_checkable
class Clock(Protocol):
    """Time, as an injectable dependency."""

    def now(self) -> datetime: ...

    def monotonic(self) -> float: ...

    async def sleep(self, seconds: float) -> None: ...


class RealClock:
    """The clock a running process uses."""

    def now(self) -> datetime:
        return datetime.now(UTC)

    def monotonic(self) -> float:
        return time.monotonic()

    async def sleep(self, seconds: float) -> None:
        await asyncio.sleep(seconds)
