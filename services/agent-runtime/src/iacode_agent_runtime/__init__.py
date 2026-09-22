"""The IACode Agent Runtime.

The brain that coordinates. It receives a task, creates a durable run, selects a team of agents,
assembles context, calls the Model Gateway — and only the Model Gateway — executes the agents in
order, records every state change and every event, survives a restart, enforces budgets, can be
cancelled and produces a result.

**It executes nothing.** When an agent asks for a tool, the request is persisted, the run moves to
``WAITING_FOR_TOOL`` and it waits. There is no shell here, no filesystem mutation, no Git, no
container and no browser, and an automated boundary control in the suite proves it rather than
trusting this sentence. Execution belongs to `GATE 3 — SANDBOX`:

```text
Agent Runtime -> ToolRequest -> WAITING_FOR_TOOL -> [Gate 3] -> ToolResult -> Agent Runtime resumes
```

The package is provider-neutral and application-neutral. It declares ports for persistence, for the
model and for the clock; the API process and the Temporal worker supply them. Nothing here imports
FastAPI, and nothing here imports a provider adapter.
"""

from iacode_agent_runtime.contracts import RunPlan, StagePlan, ToolRequest, ToolResult
from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType
from iacode_agent_runtime.protocol import ENVELOPE_VERSION, AgentEnvelope, EnvelopeKind
from iacode_agent_runtime.states import RunState

__all__ = [
    "ENVELOPE_VERSION",
    "AgentEnvelope",
    "AgentRuntimeError",
    "AgentRuntimeErrorType",
    "EnvelopeKind",
    "RunPlan",
    "RunState",
    "StagePlan",
    "ToolRequest",
    "ToolResult",
]
