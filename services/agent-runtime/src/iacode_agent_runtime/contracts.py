"""The data the runtime passes around: the plan of a run, and what happens while it executes.

The central object is :class:`RunPlan`. It is the **frozen** description of what a run will do,
resolved once when the run is created and carried into the durable workflow from there. Resolving
the team, the profiles and the prompt hashes at creation time is what makes a run reproducible: an
operator who edits a profile while a run is in flight changes the next run, not the one that is
already going. A workflow that re-read the registry on every turn would silently change behaviour
mid-run, and the event log would not show why.

Everything here is a plain frozen dataclass with explicit ``to_dict``/``from_dict`` pairs, because
these objects cross a Temporal boundary. Serialisation is part of the contract, not an
implementation detail of whichever library happens to be in the worker image.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from iacode_contracts.agent_runtime import TOOL_REQUEST_STATUSES, TOOL_RESULT_STATUSES

from iacode_agent_runtime.budgets import Budget
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType

__all__ = [
    "ModelCallOutcome",
    "RunPlan",
    "StagePlan",
    "ToolRequest",
    "ToolResult",
    "TurnRequest",
    "TurnResult",
]


@dataclass(frozen=True)
class StagePlan:
    """One stage, with everything resolved: the profile, its version and its prompt."""

    index: int
    name: str
    agent: str
    agent_name: str
    role_instructions: str
    inputs: tuple[str, ...]
    output_name: str
    max_turns: int
    allowed_actions: tuple[str, ...]
    profile_version: str
    prompt_template: str
    prompt_template_version: str
    prompt_template_hash: str
    default_route: str | None = None
    #: The canonical sandbox policy this stage's tool requests execute under, frozen from the
    #: agent's profile when the run is created. ``None`` means the stage's tools are answered from
    #: outside, as in Gate 2; the runtime reads nothing else out of it.
    sandbox_policy: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "name": self.name,
            "agent": self.agent,
            "agentName": self.agent_name,
            "roleInstructions": self.role_instructions,
            "inputs": list(self.inputs),
            "outputName": self.output_name,
            "maxTurns": self.max_turns,
            "allowedActions": list(self.allowed_actions),
            "profileVersion": self.profile_version,
            "promptTemplate": self.prompt_template,
            "promptTemplateVersion": self.prompt_template_version,
            "promptTemplateHash": self.prompt_template_hash,
            "defaultRoute": self.default_route,
            "sandboxPolicy": self.sandbox_policy,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> StagePlan:
        return cls(
            index=int(payload["index"]),
            name=str(payload["name"]),
            agent=str(payload["agent"]),
            agent_name=str(payload.get("agentName") or payload["agent"]),
            role_instructions=str(payload["roleInstructions"]),
            inputs=tuple(str(item) for item in payload.get("inputs") or ()),
            output_name=str(payload["outputName"]),
            max_turns=int(payload["maxTurns"]),
            allowed_actions=tuple(str(item) for item in payload.get("allowedActions") or ()),
            profile_version=str(payload["profileVersion"]),
            prompt_template=str(payload["promptTemplate"]),
            prompt_template_version=str(payload["promptTemplateVersion"]),
            prompt_template_hash=str(payload["promptTemplateHash"]),
            default_route=payload.get("defaultRoute"),
            sandbox_policy=payload.get("sandboxPolicy"),
        )


@dataclass(frozen=True)
class RunPlan:
    """Everything a run needs, frozen at creation.

    ``route`` and ``model`` are passed through to the gateway untouched. The runtime does not parse
    them, does not look up a provider and does not decide whether a model can serve the request:
    that is the gateway's contract, and duplicating the check here would be a second answer to a
    question that already has one.
    """

    run_id: str
    task_id: str
    task: str
    team: str
    team_version: str
    stages: tuple[StagePlan, ...]
    budget: Budget
    route: str | None = None
    model: str | None = None
    correlation_id: str | None = None
    title: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    #: Where the run's sandbox workspace comes from: ``{"kind": "empty"}`` or an authorised
    #: snapshot, ``{"kind": "snapshot", "artifactId": ..., "checksum": ...}``. Opaque here; the
    #: sandbox validates it.
    workspace: dict[str, str] = field(default_factory=dict)

    def stage(self, index: int) -> StagePlan:
        for stage in self.stages:
            if stage.index == index:
                return stage
        raise AgentRuntimeError(
            AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR,
            f"the plan has no stage {index}",
            details={"stage": index})

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "taskId": self.task_id,
            "task": self.task,
            "team": self.team,
            "teamVersion": self.team_version,
            "stages": [stage.to_dict() for stage in self.stages],
            "budget": self.budget.to_dict(),
            "route": self.route,
            "model": self.model,
            "correlationId": self.correlation_id,
            "title": self.title,
            "metadata": dict(self.metadata),
            "workspace": dict(self.workspace),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RunPlan:
        return cls(
            run_id=str(payload["runId"]),
            task_id=str(payload["taskId"]),
            task=str(payload["task"]),
            team=str(payload["team"]),
            team_version=str(payload["teamVersion"]),
            stages=tuple(StagePlan.from_dict(item) for item in payload.get("stages") or ()),
            budget=Budget.from_dict(payload.get("budget")),
            route=payload.get("route"),
            model=payload.get("model"),
            correlation_id=payload.get("correlationId"),
            title=payload.get("title"),
            metadata=dict(payload.get("metadata") or {}),
            workspace={str(key): str(value)
                       for key, value in (payload.get("workspace") or {}).items()},
        )


@dataclass(frozen=True)
class ToolRequest:
    """A tool an agent asked for. **Persisted and waited on; never executed by the runtime.**"""

    tool_request_id: str
    run_id: str
    agent_run_id: str | None
    name: str
    arguments: dict[str, Any]
    status: str = "PENDING"
    created_at: datetime | None = None
    resolved_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.status not in TOOL_REQUEST_STATUSES:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.INTERNAL_AGENT_RUNTIME_ERROR,
                f"{self.status!r} is not a tool request status",
                details={"status": self.status})

    def to_dict(self) -> dict[str, Any]:
        return {
            "toolRequestId": self.tool_request_id,
            "runId": self.run_id,
            "agentRunId": self.agent_run_id,
            "name": self.name,
            "arguments": dict(self.arguments),
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "resolvedAt": self.resolved_at.isoformat() if self.resolved_at else None,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ToolRequest:
        return cls(
            tool_request_id=str(payload["toolRequestId"]),
            run_id=str(payload["runId"]),
            agent_run_id=payload.get("agentRunId"),
            name=str(payload["name"]),
            arguments=dict(payload.get("arguments") or {}),
            status=str(payload.get("status") or "PENDING"),
        )


@dataclass(frozen=True)
class ToolResult:
    """The answer to a tool request, as this Gate receives it.

    ``output`` is opaque. The runtime stores it, labels it and hands it back to the agent as data;
    it reads nothing out of it and acts on nothing in it.
    """

    tool_request_id: str
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in TOOL_RESULT_STATUSES:
            raise AgentRuntimeError(
                AgentRuntimeErrorType.TOOL_RESULT_INVALID,
                f"{self.status!r} is not a tool result status; expected one of "
                + ", ".join(TOOL_RESULT_STATUSES),
                details={"status": self.status})

    @property
    def succeeded(self) -> bool:
        return self.status == "SUCCEEDED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "toolRequestId": self.tool_request_id,
            "status": self.status,
            "output": dict(self.output),
            "error": self.error,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ToolResult:
        return cls(
            tool_request_id=str(payload["toolRequestId"]),
            status=str(payload["status"]),
            output=dict(payload.get("output") or {}),
            error=payload.get("error"),
            metadata=dict(payload.get("metadata") or {}),
        )


@dataclass(frozen=True)
class ModelCallOutcome:
    """What one call to the gateway produced, in the runtime's terms.

    ``cost`` is ``None`` when the gateway does not know it, and ``cost_known`` says which of the two
    it is. Reporting an unknown cost as zero would state that the call was free, which is a
    different claim and usually a wrong one — the rule Gate 1 established and this Gate inherits.
    """

    text: str
    model_call_id: str | None
    provider: str
    model: str
    endpoint: str
    route_reason: str
    finish_reason: str
    latency_ms: float
    gateway_request_id: str = ""
    total_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost: float | None = None
    cost_known: bool = False
    repair_attempt: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "modelCallId": self.model_call_id,
            "gatewayRequestId": self.gateway_request_id,
            "provider": self.provider,
            "model": self.model,
            "endpoint": self.endpoint,
            "routeReason": self.route_reason,
            "finishReason": self.finish_reason,
            "latencyMs": self.latency_ms,
            "totalTokens": self.total_tokens,
            "inputTokens": self.input_tokens,
            "outputTokens": self.output_tokens,
            "cost": self.cost,
            "costKnown": self.cost_known,
            "repairAttempt": self.repair_attempt,
        }


@dataclass(frozen=True)
class TurnRequest:
    """What the engine asks a model for: one turn of one stage."""

    run_id: str
    stage_index: int
    turn: int
    instructions: str
    data: str
    route: str | None
    model: str | None
    allowed_actions: tuple[str, ...]
    structured_output: bool = False
    repair_of: str | None = None


@dataclass(frozen=True)
class TurnResult:
    """What one turn produced, once the envelope has been parsed."""

    kind: str
    content: str = ""
    summary: str = ""
    tool_name: str | None = None
    tool_arguments: dict[str, Any] = field(default_factory=dict)
    calls: tuple[ModelCallOutcome, ...] = ()

    @property
    def model_call_ids(self) -> tuple[str, ...]:
        return tuple(call.model_call_id for call in self.calls if call.model_call_id)
