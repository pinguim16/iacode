"""The Agent Runtime's error taxonomy.

A run that fails has to say *what kind* of failure it was, because the answer decides what happens
next: a budget exhaustion is the run working as configured, an invalid agent output is a model
problem, and a gateway error is somebody else's outage. Collapsing them into one "the run failed"
would make every one of those look like the same incident.

The taxonomy maps the gateway's own classification without hiding where a failure came from.
`iacode_model_gateway.errors.GatewayErrorType` already distinguishes authentication, rate limiting,
timeouts and an open circuit; the runtime does not re-classify them, it records
:data:`AgentRuntimeErrorType.GATEWAY_ERROR` and keeps the gateway's type beside it. Re-deriving a
provider's failure from a string would be a second classifier that can disagree with the first.

Nothing here carries a provider's raw message. `details` is a small dictionary of facts a caller
may branch on, and the message is ours.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

__all__ = [
    "AgentRuntimeError",
    "AgentRuntimeErrorType",
    "BudgetExceededError",
    "InvalidAgentOutputError",
    "InvalidStateTransitionError",
    "RunCancelledError",
    "ToolResultInvalidError",
]


class AgentRuntimeErrorType(StrEnum):
    """Why a run stopped, in the runtime's vocabulary."""

    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_AGENT_OUTPUT = "INVALID_AGENT_OUTPUT"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    CONTEXT_OVERFLOW = "CONTEXT_OVERFLOW"
    GATEWAY_ERROR = "GATEWAY_ERROR"
    TOOL_RESULT_INVALID = "TOOL_RESULT_INVALID"
    TOOL_NOT_PERMITTED = "TOOL_NOT_PERMITTED"
    TOOL_WAIT_TIMEOUT = "TOOL_WAIT_TIMEOUT"
    RUN_DEADLINE_EXCEEDED = "RUN_DEADLINE_EXCEEDED"
    RUN_CANCELLED = "RUN_CANCELLED"
    INVALID_STATE_TRANSITION = "INVALID_STATE_TRANSITION"
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    TEAM_NOT_FOUND = "TEAM_NOT_FOUND"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
    WORKFLOW_ERROR = "WORKFLOW_ERROR"
    INTERNAL_AGENT_RUNTIME_ERROR = "INTERNAL_AGENT_RUNTIME_ERROR"


class AgentRuntimeError(Exception):
    """A classified runtime failure.

    ``message`` is safe to show a caller: it says what went wrong in our words and carries no
    traceback, no provider body and no credential. ``details`` holds the few facts worth branching
    on — a limit that was reached, the stage that failed — and nothing else.
    """

    def __init__(
        self,
        error_type: AgentRuntimeErrorType,
        message: str,
        *,
        stage: str | None = None,
        details: dict[str, Any] | None = None,
        upstream_type: str | None = None,
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.stage = stage
        self.details = dict(details or {})
        #: The gateway's own classification, when the failure came from there. Kept rather than
        #: translated, so the origin of a failure survives the boundary.
        self.upstream_type = upstream_type

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "errorType": str(self.error_type),
            "message": self.message,
        }
        if self.stage:
            payload["stage"] = self.stage
        if self.upstream_type:
            payload["upstreamType"] = self.upstream_type
        if self.details:
            payload["details"] = dict(self.details)
        return payload

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return f"AgentRuntimeError({self.error_type}, {self.message!r})"


class InvalidAgentOutputError(AgentRuntimeError):
    """The agent answered with something that is not a valid envelope."""

    def __init__(self, message: str, *, stage: str | None = None,
                 details: dict[str, Any] | None = None) -> None:
        super().__init__(AgentRuntimeErrorType.INVALID_AGENT_OUTPUT, message,
                         stage=stage, details=details)


class BudgetExceededError(AgentRuntimeError):
    """The run reached a limit it was created with."""

    def __init__(self, message: str, *, stage: str | None = None,
                 details: dict[str, Any] | None = None) -> None:
        super().__init__(AgentRuntimeErrorType.BUDGET_EXCEEDED, message,
                         stage=stage, details=details)


class InvalidStateTransitionError(AgentRuntimeError):
    """Something asked the run to move somewhere the state machine does not allow."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(AgentRuntimeErrorType.INVALID_STATE_TRANSITION, message, details=details)


class ToolResultInvalidError(AgentRuntimeError):
    """A tool result was refused: wrong run, unknown request, or a run that is already finished."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(AgentRuntimeErrorType.TOOL_RESULT_INVALID, message, details=details)


class RunCancelledError(AgentRuntimeError):
    """The run was cancelled. Terminal, and not a defect."""

    def __init__(self, message: str = "the run was cancelled", *,
                 stage: str | None = None) -> None:
        super().__init__(AgentRuntimeErrorType.RUN_CANCELLED, message, stage=stage)
