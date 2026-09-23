"""The shared vocabulary and the HTTP shapes of the Agent Runtime.

Two different things live here, and they live together because both are promises to a consumer the
producer does not control.

**The vocabulary.** The run states, the state transitions, the tool request statuses and the event
types are named once, in this package, and every other component derives from these tuples: the
runtime's own :class:`~iacode_agent_runtime.states.RunState`, the ``CHECK`` constraint the database
carries, the API's responses and the browser's rendering. `docs/GATE-2-CHECKLIST.md` row 3.5 asks
for exactly that, because the engineering memory records what happens when a classification is
written down twice — one copy grows a value the other does not have, and the disagreement surfaces
as a constraint violation in production rather than as a failing test.

**The wire shapes.** What crosses the HTTP boundary, in the camel-case convention the Foundation
and the gateway endpoints already use.

Nothing here carries a credential, a provider address, a raw prompt or a model's private reasoning.
A caller names a team and a task; where a model lives and how it is authenticated is administrative
configuration the API never echoes.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from iacode_contracts.sandbox import ToolExecutionView

__all__ = [
    "AGENT_RUN_STATES",
    "AGENT_RUN_WORKFLOW",
    "ALLOWED_RUN_TRANSITIONS",
    "CANCEL_SIGNAL",
    "RUN_EVENT_TYPES",
    "TERMINAL_RUN_STATES",
    "TOOL_EXECUTOR_EXTERNAL",
    "TOOL_EXECUTOR_SANDBOX",
    "TOOL_REQUEST_EXECUTORS",
    "TOOL_REQUEST_STATUSES",
    "TOOL_RESULT_SIGNAL",
    "TOOL_RESULT_STATUSES",
    "AgentProfileSummary",
    "AgentRunCreated",
    "AgentRunDetail",
    "AgentRunListResponse",
    "AgentRunStageView",
    "AgentRunSummaryView",
    "BudgetView",
    "CreateAgentRunRequest",
    "RunEventPage",
    "RunEventPayload",
    "TeamProfileSummary",
    "TeamStageSummary",
    "ToolRequestView",
    "ToolResultSubmission",
]

# ---------------------------------------------------------------------------------------------
# The vocabulary
# ---------------------------------------------------------------------------------------------

#: The durable workflow that executes a run, and the two signals that steer it. They are named here
#: rather than in the worker because two processes have to agree on them: the API starts and signals
#: the workflow, the worker registers and receives it. A name written down twice is a name that
#: eventually differs by a character, and the failure would be a signal that silently goes nowhere.
AGENT_RUN_WORKFLOW = "IACodeAgentRun"
TOOL_RESULT_SIGNAL = "tool_result"
CANCEL_SIGNAL = "cancel"

#: Every state a run may be in. Seven, and deliberately not more: a lifecycle with twenty states
#: describes a system nobody has built yet, and each extra state is a transition table entry that
#: nothing exercises.
AGENT_RUN_STATES: tuple[str, ...] = (
    "CREATED",
    "QUEUED",
    "RUNNING",
    "WAITING_FOR_TOOL",
    "SUCCEEDED",
    "FAILED",
    "CANCELLED",
)

#: A run that reaches one of these is finished. Another attempt is another run.
TERMINAL_RUN_STATES: tuple[str, ...] = ("SUCCEEDED", "FAILED", "CANCELLED")

#: Which state may follow which. The table is data so that one implementation can read it and one
#: test can enumerate it; a transition written as an ``if`` in the code that performs it is a
#: transition no test can find.
ALLOWED_RUN_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "CREATED": ("QUEUED", "CANCELLED", "FAILED"),
    "QUEUED": ("RUNNING", "CANCELLED", "FAILED"),
    "RUNNING": ("WAITING_FOR_TOOL", "SUCCEEDED", "FAILED", "CANCELLED"),
    "WAITING_FOR_TOOL": ("RUNNING", "FAILED", "CANCELLED"),
    "SUCCEEDED": (),
    "FAILED": (),
    "CANCELLED": (),
}

#: What can happen to a tool request. ``PENDING`` until something answers it; ``RESOLVED`` when a
#: result arrives; ``REJECTED`` when the result is refused; ``CANCELLED`` when the run ends first.
TOOL_REQUEST_STATUSES: tuple[str, ...] = ("PENDING", "RESOLVED", "REJECTED", "CANCELLED")

#: Who answers a tool request. Recorded when the request is created, from the stage that made
#: it, and never taken from a result. ``SANDBOX``: the stage has a sandbox policy, the sandbox
#: executes the request and only its result - delivered by the workflow's internal activity -
#: may resolve it. ``EXTERNAL``: the stage has no sandbox policy and its result arrives through
#: the API's tool-result endpoint. `M1-F-002`: without this, the endpoint accepted a result for
#: a request the sandbox was executing, and the agent received it instead of the sandbox's.
TOOL_EXECUTOR_EXTERNAL = "EXTERNAL"
TOOL_EXECUTOR_SANDBOX = "SANDBOX"
TOOL_REQUEST_EXECUTORS: tuple[str, ...] = (TOOL_EXECUTOR_EXTERNAL, TOOL_EXECUTOR_SANDBOX)

#: What a tool result says happened. Gate 2 never produces one of these itself — it accepts one
#: from whatever is authorised to execute, which in this Gate is a test fixture or the internal
#: development simulator, and from Gate 3 onwards is the sandbox.
TOOL_RESULT_STATUSES: tuple[str, ...] = ("SUCCEEDED", "FAILED", "DENIED", "TIMED_OUT")

#: Every event a run can record. The list is closed: an event type that is not here cannot be
#: appended, because a log whose vocabulary grows by accident is a log nothing can query.
RUN_EVENT_TYPES: tuple[str, ...] = (
    "RUN_CREATED",
    "RUN_STARTED",
    "AGENT_STARTED",
    "MODEL_CALL_STARTED",
    "MODEL_CALL_COMPLETED",
    "TOOL_REQUESTED",
    "TOOL_RESULT_RECEIVED",
    "AGENT_COMPLETED",
    "RUN_COMPLETED",
    "RUN_FAILED",
    "RUN_CANCELLED",
    "RUN_NOTE",
)


# ---------------------------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------------------------


class BudgetView(BaseModel):
    """What a run may spend, and what it has spent.

    ``maxTotalTokens`` is optional and ``tokensEnforceable`` says whether it can be enforced at all.
    A provider that reports no usage makes a token budget unenforceable, and saying so is different
    from silently not enforcing it — `docs/GATE-2-CHECKLIST.md` row 11.2.
    """

    maxTurns: int = Field(ge=1, le=100)
    maxModelCalls: int = Field(ge=1, le=200)
    maxDurationSeconds: int = Field(ge=1, le=86400)
    toolWaitTimeoutSeconds: int = Field(ge=1, le=86400)
    maxTotalTokens: int | None = Field(default=None, ge=1)
    turnsUsed: int = Field(default=0, ge=0)
    modelCallsUsed: int = Field(default=0, ge=0)
    tokensUsed: int | None = Field(default=None, ge=0)
    tokensEnforceable: bool = True


class CreateAgentRunRequest(BaseModel):
    """What a caller supplies to start a run.

    There is deliberately no field for a provider address, an API key, a header or an organisation.
    An address a request can supply is an address an attacker can supply, and a runtime that
    forwarded a caller's credential would be a credential proxy. Both come from administrative
    configuration and from nowhere else — the same rule the gateway's request contract states.
    """

    model_config = ConfigDict(extra="forbid")

    task: str = Field(min_length=1, description="What IACode is being asked to do.")
    title: str | None = Field(default=None, max_length=512)
    team: str = Field(default="single-agent", min_length=1, max_length=128)
    route: str | None = Field(default=None, max_length=64)
    model: str | None = Field(
        default=None, max_length=384,
        description="An explicit 'provider:model' reference. The gateway decides whether it can "
                    "serve the request; the runtime does not inspect provider metadata.")
    maxTurns: int | None = Field(default=None, ge=1, le=100)
    maxModelCalls: int | None = Field(default=None, ge=1, le=200)
    maxDurationSeconds: int | None = Field(default=None, ge=1, le=86400)
    maxTotalTokens: int | None = Field(default=None, ge=1)
    toolWaitTimeoutSeconds: int | None = Field(default=None, ge=1, le=86400)
    idempotencyKey: str | None = Field(default=None, min_length=1, max_length=128)
    metadata: dict[str, str] = Field(default_factory=dict)
    workspaceSnapshot: str | None = Field(
        default=None, min_length=36, max_length=36,
        description="The identifier of an authorised workspace snapshot artifact the run's sandbox "
                    "is provisioned from. Never a path: a run cannot name a directory of the host.")


class ToolResultSubmission(BaseModel):
    """The answer to a tool request.

    Gate 2 accepts it; it never produces it by executing anything. ``output`` is an opaque object
    to this Gate: the runtime hands it back to the agent as a labelled artifact and reads nothing
    out of it.
    """

    model_config = ConfigDict(extra="forbid")

    toolRequestId: str = Field(min_length=1, max_length=64)
    status: str = Field(description="One of " + ", ".join(TOOL_RESULT_STATUSES))
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = Field(default=None, max_length=4096)
    metadata: dict[str, str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------------------------


class AgentRunCreated(BaseModel):
    """The immediate answer to a creation request.

    It carries an identifier and a state, not a result. A run can take minutes, and an endpoint that
    held the HTTP request open until it finished would be a timeout waiting to happen.
    """

    runId: str
    taskId: str
    state: str
    team: str
    createdAt: str
    idempotentReplay: bool = Field(
        default=False,
        description="True when this answer is the run an earlier request with the same "
                    "idempotency key already created.")


class AgentRunStageView(BaseModel):
    """One stage of a team, as it executed."""

    index: int
    name: str
    agent: str
    agentRunId: str | None = None
    state: str
    profileVersion: str | None = None
    promptTemplateVersion: str | None = None
    promptTemplateHash: str | None = None
    turns: int = 0
    modelCalls: int = 0
    outputName: str | None = None
    outputSummary: str | None = None
    startedAt: str | None = None
    finishedAt: str | None = None


class ToolRequestView(BaseModel):
    """A tool the run asked for and is waiting on. Nothing here executes it."""

    toolRequestId: str
    agentRunId: str | None = None
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: str
    createdAt: str
    resolvedAt: str | None = None
    resultStatus: str | None = None


class AgentRunSummaryView(BaseModel):
    """The operational summary of a finished or running run. No private reasoning."""

    agentsExecuted: int = 0
    turns: int = 0
    modelCalls: int = 0
    toolsRequested: int = 0
    toolsResolved: int = 0
    durationSeconds: float | None = None
    finalState: str | None = None
    totalTokens: int | None = None
    cost: float | None = Field(
        default=None,
        description="Absent when the gateway does not know it. Zero would state the run was free.")
    costKnown: bool = False


class AgentRunDetail(BaseModel):
    """Everything an operator can see about one run."""

    runId: str
    taskId: str
    title: str | None = None
    task: str
    team: str
    teamVersion: str | None = None
    state: str
    route: str | None = None
    model: str | None = None
    currentStage: str | None = None
    createdAt: str
    startedAt: str | None = None
    finishedAt: str | None = None
    workflowId: str | None = None
    budget: BudgetView
    stages: list[AgentRunStageView] = Field(default_factory=list)
    pendingToolRequest: ToolRequestView | None = None
    toolRequests: list[ToolRequestView] = Field(default_factory=list)
    toolExecutions: list[ToolExecutionView] = Field(
        default_factory=list,
        description="What the sandbox executed for this run: the tool, how it ended, how long it "
                    "took and which sandbox ran it. Never the output.")
    result: str | None = None
    resultSummary: str | None = None
    errorType: str | None = None
    errorSummary: str | None = None
    failedStage: str | None = None
    correlationId: str | None = None
    summary: AgentRunSummaryView = Field(default_factory=AgentRunSummaryView)
    trainingAllowed: bool = Field(
        default=False,
        description="Always false in this Gate. Rights default to denial and nothing here grants "
                    "them.")


class AgentRunListResponse(BaseModel):
    total: int
    runs: list[AgentRunDetail] = Field(default_factory=list)


class RunEventPayload(BaseModel):
    """One recorded event of a run.

    ``sequence`` is assigned by the store and is monotonic per run, so a consumer can resume from a
    cursor and two consumers agree on the order.
    """

    runId: str
    sequence: int = Field(ge=1)
    type: str
    createdAt: str
    agentRunId: str | None = None
    stage: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class RunEventPage(BaseModel):
    runId: str
    total: int
    nextCursor: int
    events: list[RunEventPayload] = Field(default_factory=list)


class AgentProfileSummary(BaseModel):
    """A declared agent role, as the registry knows it."""

    agent: str
    name: str
    role: str
    description: str
    version: str
    defaultRoute: str | None = None
    maxTurns: int
    allowedActions: list[str] = Field(default_factory=list)
    promptTemplate: str
    promptTemplateVersion: str
    promptTemplateHash: str
    enabled: bool
    sandboxPolicy: str | None = Field(
        default=None, description="The sandbox policy this role's tools execute under, if any.")


class TeamStageSummary(BaseModel):
    index: int
    name: str
    agent: str
    inputs: list[str] = Field(default_factory=list)
    outputName: str


class TeamProfileSummary(BaseModel):
    """A declared team. Configuration, never an inference."""

    team: str
    name: str
    description: str
    version: str
    enabled: bool
    stages: list[TeamStageSummary] = Field(default_factory=list)
