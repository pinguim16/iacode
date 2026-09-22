"""Composing the agent runtime for this process.

Everything expensive is built once, at start-up: the registry that reads the declared profiles, the
store over the shared schema, and the service that turns a creation request into a frozen plan. A
request then costs a few attribute reads.

The registry caches by the modification times of the definition files, so an operator who edits a
profile sees the change on the next run without restarting the API — the same reasoning the
gateway's provider policy follows.

Note what is absent. There is no model client here and no provider anything: the API does not run a
turn. It creates the run, hands the frozen plan to Temporal and answers questions about it; the
worker executes, and the worker reaches a model through the gateway like any other caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from iacode_agent_runtime.budgets import Budget
from iacode_agent_runtime.limits import RuntimeLimits
from iacode_agent_runtime.persistence import SqlAgentRunStore
from iacode_agent_runtime.registry import AgentRegistry
from iacode_agent_runtime.service import AgentRuntimeService

from iacode_api.config import Settings

__all__ = ["AgentRuntimeRuntime", "build_agent_runtime"]


@dataclass
class AgentRuntimeRuntime:
    """Everything the API owns on behalf of the agent runtime."""

    service: AgentRuntimeService
    registry: AgentRegistry
    store: SqlAgentRunStore
    task_queue: str
    execution_timeout_seconds: int
    event_poll_seconds: float


def build_agent_runtime(settings: Settings, session_factory) -> AgentRuntimeRuntime:
    """Read the declared profiles, wire the store and build the service.

    Written out field by field rather than by copying a prefix, so a key added on one side without
    the other is a name error here instead of a setting that silently keeps its default.
    """
    registry = AgentRegistry(Path(settings.repository_root))
    store = SqlAgentRunStore(session_factory)
    budget = Budget(
        max_turns=settings.agent_runtime_max_turns,
        max_model_calls=settings.agent_runtime_max_model_calls,
        max_duration_seconds=settings.agent_runtime_max_duration_seconds,
        tool_wait_timeout_seconds=settings.agent_runtime_tool_wait_timeout_seconds,
    )
    limits = RuntimeLimits(max_task_bytes=settings.agent_runtime_max_task_bytes)
    return AgentRuntimeRuntime(
        service=AgentRuntimeService(
            session_factory=session_factory,
            registry=registry,
            store=store,
            default_budget=budget,
            limits=limits,
        ),
        registry=registry,
        store=store,
        task_queue=settings.agent_runtime_task_queue,
        # A run's wall-clock deadline plus its tool wait: Temporal must not terminate a workflow
        # that is legitimately paused waiting for a tool result, because the run's own timeout is
        # what should end it — with a recorded state and a recorded event.
        execution_timeout_seconds=(settings.agent_runtime_max_duration_seconds
                                   + settings.agent_runtime_tool_wait_timeout_seconds),
        event_poll_seconds=settings.agent_runtime_event_stream_poll_seconds,
    )
