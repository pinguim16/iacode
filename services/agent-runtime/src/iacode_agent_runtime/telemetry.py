"""The runtime's instruments and its logging contract.

Two rules, and both are about what must *not* be here.

**No label carries content.** A Prometheus label becomes a time series, so a label whose value is a
task, a prompt, a response or a tool argument produces one series per run and takes the whole
metrics store down with it — and, worse, publishes the content to anyone who can read the endpoint.
:func:`_label` reduces every label to a bounded set of known values, and the suite asserts that no
instrument declares a label outside the permitted names.

**No log record carries the whole task.** The structured fields are identifiers and outcomes:
correlation, task, run, agent, agent run, stage, event type, model call and status. The task's text
is in the run's own row, where it belongs and where access to it is a deliberate act.

The instruments are created against a registry that is passed in, never the global default. A module
that registers on import cannot be instantiated twice, which makes it impossible to build two
applications in one interpreter — which is exactly what a test suite does.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from iacode_telemetry.logging import get_logger
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

__all__ = ["PERMITTED_LABELS", "AgentRuntimeMetrics", "runtime_log_fields"]

logger = get_logger(__name__)

#: Every label any instrument in this module may declare. Low cardinality by construction: a team
#: slug, a state, an agent slug, an error type and a stage name are all drawn from configuration or
#: from a closed vocabulary.
PERMITTED_LABELS = frozenset({"service", "team", "agent", "state", "error_type", "stage"})

#: Buckets for a run's duration. A run is seconds to minutes; anything past ten minutes is
#: interesting only as "long", which the last bucket says.
DURATION_BUCKETS = (0.5, 1, 2, 5, 10, 30, 60, 120, 300, 600)


def _label(value: Any, *, limit: int = 64) -> str:
    """A label value: short, non-empty and never content."""
    text = str(value or "unknown").strip() or "unknown"
    return text[:limit]


@dataclass
class AgentRuntimeMetrics:
    """The instruments the agent runtime publishes."""

    registry: CollectorRegistry
    service: str = "iacode-agent-runtime"

    def __post_init__(self) -> None:
        self.runs_total = Counter(
            "agent_runs_total", "Agent runs started, by team.",
            ["service", "team"], registry=self.registry)
        self.run_duration_seconds = Histogram(
            "agent_run_duration_seconds", "How long an agent run took, by terminal state.",
            ["service", "state"], buckets=DURATION_BUCKETS, registry=self.registry)
        self.turns_total = Counter(
            "agent_turns_total", "Agent turns executed, by agent.",
            ["service", "agent"], registry=self.registry)
        self.run_failures_total = Counter(
            "agent_run_failures_total", "Agent runs that failed, by classified error type.",
            ["service", "error_type"], registry=self.registry)
        self.waiting_for_tool = Gauge(
            "agent_runs_waiting_for_tool", "Agent runs currently paused on a tool request.",
            ["service"], registry=self.registry)
        self.budget_exhaustions_total = Counter(
            "agent_budget_exhaustions_total", "Runs stopped by a budget, by which limit.",
            ["service", "state"], registry=self.registry)
        self.cancellations_total = Counter(
            "agent_cancellations_total", "Agent runs cancelled.",
            ["service"], registry=self.registry)
        self.tool_requests_total = Counter(
            "agent_tool_requests_total", "Tool requests recorded. None of them was executed.",
            ["service", "agent"], registry=self.registry)

    # -- recording -------------------------------------------------------------------------------

    def run_started(self, team: str) -> None:
        self.runs_total.labels(service=self.service, team=_label(team)).inc()

    def turn_executed(self, agent: str) -> None:
        self.turns_total.labels(service=self.service, agent=_label(agent)).inc()

    def tool_requested(self, agent: str) -> None:
        self.tool_requests_total.labels(service=self.service, agent=_label(agent)).inc()

    def waiting(self, delta: int) -> None:
        self.waiting_for_tool.labels(service=self.service).inc(delta)

    def run_finished(self, state: str, seconds: float) -> None:
        self.run_duration_seconds.labels(
            service=self.service, state=_label(state)).observe(max(seconds, 0.0))

    def run_failed(self, error_type: str) -> None:
        self.run_failures_total.labels(
            service=self.service, error_type=_label(error_type)).inc()

    def budget_exhausted(self, limit: str) -> None:
        self.budget_exhaustions_total.labels(service=self.service, state=_label(limit)).inc()

    def cancelled(self) -> None:
        self.cancellations_total.labels(service=self.service).inc()


def runtime_log_fields(
    *,
    correlation_id: str | None = None,
    task_id: str | None = None,
    run_id: str | None = None,
    agent_id: str | None = None,
    agent_run_id: str | None = None,
    stage: str | None = None,
    event_type: str | None = None,
    model_call_id: str | None = None,
    status: str | None = None,
) -> dict[str, str]:
    """The structured fields a runtime log record carries.

    A field with no value is absent rather than null, the convention Gate 0 established: a key that
    is always null teaches readers to ignore it before it ever means anything. The task's text is
    deliberately not among the fields at all.
    """
    candidates = {
        "correlationId": correlation_id,
        "taskId": task_id,
        "runId": run_id,
        "agentId": agent_id,
        "agentRunId": agent_run_id,
        "stage": stage,
        "eventType": event_type,
        "modelCallId": model_call_id,
        "status": status,
    }
    return {key: str(value) for key, value in candidates.items() if value}
