"""The Foundation smoke workflow.

This is the smallest workflow that proves the durable execution path works end to end: the API can
reach Temporal, the worker is polling the task queue, an activity executes in the worker process,
and the result travels back to the caller through Temporal's history.

It is **not** the beginning of agent orchestration. There is no branching, no retry policy worth
the name, no signal, no child workflow and no tool call, because
`docs/GATE-0-CHECKLIST.md` row 8.5 puts all of that in Gate 2. When that Gate arrives it will add
workflows beside this one; this one stays exactly as small as it is, because its job is to answer
"is durable execution working" during an incident, and a smoke check that grows features stops
being able to answer that.

The activity returns real data — the worker's identity and the instant it ran — rather than a
constant. A smoke check that returns a hardcoded string passes when the worker is answering from
cache, from a replay or from nothing at all.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, timedelta

from temporalio import activity, workflow

SMOKE_WORKFLOW_NAME = "IACodeFoundationSmoke"
SMOKE_ACTIVITY_NAME = "iacode_foundation_echo"


@dataclass
class SmokeInput:
    """What the caller asks the workflow to echo, and who asked."""

    message: str
    requestedBy: str = "unknown"


@dataclass
class SmokeResult:
    """What the activity observed while running inside the worker."""

    message: str
    requestedBy: str
    workerIdentity: str
    executedAt: str
    workflowId: str


@activity.defn(name=SMOKE_ACTIVITY_NAME)
async def echo(payload: SmokeInput) -> SmokeResult:
    """Run inside the worker and report facts only the worker can know."""
    from datetime import datetime

    info = activity.info()
    return SmokeResult(
        message=payload.message,
        requestedBy=payload.requestedBy,
        workerIdentity=info.workflow_namespace + "/" + info.task_queue,
        executedAt=datetime.now(UTC).isoformat(timespec="milliseconds").replace(
            "+00:00", "Z"),
        workflowId=info.workflow_id,
    )


@workflow.defn(name=SMOKE_WORKFLOW_NAME)
class SmokeWorkflow:
    """Execute the echo activity once and return its result."""

    @workflow.run
    async def run(self, payload: SmokeInput) -> SmokeResult:
        # A short timeout on purpose: this workflow exists to fail fast when the worker is not
        # there. A generous timeout would turn "the worker is down" into "the smoke check is slow".
        return await workflow.execute_activity(
            echo,
            payload,
            start_to_close_timeout=timedelta(seconds=10),
            schedule_to_close_timeout=timedelta(seconds=30),
        )
