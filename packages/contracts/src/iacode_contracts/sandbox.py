"""The shared vocabulary and the HTTP shapes of the Sandbox.

The sandbox is operated by one process and consulted by three: the orchestrator worker dispatches a
tool request to it, the API reads what it executed, and the database constrains what it records.
Every name two of them must agree on is written here once, for the reason
`docs/GATE-2-CHECKLIST.md` row 3.5 gave for the run states: a name written twice is a name that
drifts, and the drift surfaces as a request sent to a queue nobody polls or a row the database
refuses.

Nothing here carries a command's output, a file's content or a credential. The views describe what
ran, how long it took and how it ended; the output belongs to the agent that asked for it and to the
artifact store.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "SANDBOX_ACTIVE_SESSION_STATES",
    "SANDBOX_AGENT_RESULT_KEY",
    "SANDBOX_AGENT_RESULT_MAX_BYTES",
    "SANDBOX_CONTRACT_VERSION",
    "SANDBOX_EXECUTE_ACTIVITY",
    "SANDBOX_EXECUTION_KEY",
    "SANDBOX_RELEASE_ACTIVITY",
    "SANDBOX_SESSION_STATES",
    "SANDBOX_TASK_QUEUE",
    "TOOL_EXECUTION_STATUSES",
    "WORKSPACE_SNAPSHOT_ARTIFACT_KIND",
    "ToolExecutionView",
]

#: The version of the execution contract the worker and the sandbox exchange. A request carrying
#: another version is refused rather than interpreted.
SANDBOX_CONTRACT_VERSION = "1.0.0"

#: The Temporal task queue the sandbox service polls. It is a contract constant rather than a
#: setting: the workflow that dispatches to it cannot read configuration (replay has to be
#: deterministic), so the only way both sides agree is for the name to exist once.
SANDBOX_TASK_QUEUE = "iacode-sandbox"

#: The two activities the sandbox registers on that queue.
SANDBOX_EXECUTE_ACTIVITY = "iacode_sandbox_execute_tool"
SANDBOX_RELEASE_ACTIVITY = "iacode_sandbox_release_run"

#: The two keys of what the execute activity returns: the tool result the workflow persists and
#: hands back to the agent, and the whole execution record. They are written here once because the
#: producer and the consumer live in two processes that share nothing else: the first version had
#: the sandbox return the execution record alone while the workflow read the tool result, and no
#: test that ran either side against a double could see it.
SANDBOX_AGENT_RESULT_KEY = "agentResult"
SANDBOX_EXECUTION_KEY = "execution"

#: A sandbox session's lifecycle. ``CREATED`` is a row with no container yet; ``STARTING`` is a
#: container being created and its workspace provisioned; ``READY`` is idle and usable; ``RUNNING``
#: is executing one tool; ``STOPPING`` is being removed; ``STOPPED``, ``FAILED`` and ``EXPIRED`` are
#: terminal.
SANDBOX_SESSION_STATES: tuple[str, ...] = (
    "CREATED", "STARTING", "READY", "RUNNING", "STOPPING", "STOPPED", "FAILED", "EXPIRED",
)

#: The states in which a session owns a container that may still be doing something.
SANDBOX_ACTIVE_SESSION_STATES: tuple[str, ...] = ("CREATED", "STARTING", "READY", "RUNNING",
                                                  "STOPPING")

#: How one execution ended, as the sandbox records it. The first four are the agent runtime's own
#: tool result statuses; ``CANCELLED`` and ``INTERRUPTED`` exist only on the execution record,
#: because a cancelled run and an execution whose outcome was lost produce no result for an agent.
TOOL_EXECUTION_STATUSES: tuple[str, ...] = (
    "SUCCEEDED", "FAILED", "DENIED", "TIMED_OUT", "CANCELLED", "INTERRUPTED",
)

#: The largest tool result output the sandbox hands to an agent, measured as the agent runtime
#: measures every payload: the UTF-8 length of the canonical JSON rendering. A bound on the raw
#: bytes a tool produced is not enough, because JSON escapes a control character into six bytes and
#: a 128 KiB file of them renders as 768 KiB. The sandbox shortens a result to fit this, explicitly,
#: and the runtime's own ``max_tool_result_bytes`` must not be smaller, or a result the sandbox
#: considered deliverable would fail the run that asked for it.
SANDBOX_AGENT_RESULT_MAX_BYTES = 160 * 1024

#: The artifact kind of an authorised workspace snapshot. A run may be provisioned only from an
#: artifact of this kind.
WORKSPACE_SNAPSHOT_ARTIFACT_KIND = "sandbox.workspace-snapshot"


class ToolExecutionView(BaseModel):
    """One executed tool, as the operational page shows it: what, how it ended, where, how long."""

    model_config = ConfigDict(extra="forbid")

    toolRequestId: str
    tool: str
    status: str = Field(description="One of " + ", ".join(TOOL_EXECUTION_STATUSES))
    durationMs: int | None = None
    sandboxSession: str | None = Field(
        default=None, description="The first twelve characters of the sandbox session identifier.")
    exitCode: int | None = Field(
        default=None, description="Present only when a process was started.")
    timedOut: bool = False
    truncated: bool = False
    errorCode: str | None = None
    summary: str = Field(default="", max_length=240)
    createdAt: str
