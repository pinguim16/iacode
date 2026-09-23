"""The sandbox's instruments and its logging contract.

The same two rules the agent runtime follows, for the same reasons.

**No label carries content.** A label is a time series, so a label holding a command, a path or a
file's text would publish it and multiply the series without bound. Every label here is a tool name
from the closed registry, a policy name from the canonical policy, a status from the closed
vocabulary or a reason code — and :data:`PERMITTED_LABELS` is the complete list, asserted by the
suite.

**No log record carries a tool's output, a secret or the host's environment.** The fields are the
identifiers that let a reader find the execution — run, agent, sandbox, tool — and how it ended. The
output is in the tool result and the artifact store, where access to it is a deliberate act.

Instruments are created against a registry that is passed in, never the global default.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from iacode_telemetry.logging import get_logger
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

__all__ = ["METRIC_NAMES", "PERMITTED_LABELS", "SandboxMetrics", "sandbox_log_fields"]

logger = get_logger(__name__)

#: Every label any instrument in this module may declare.
PERMITTED_LABELS = frozenset({"service", "tool", "policy", "status", "reason", "outcome"})

#: The instruments the Gate requires, by name.
METRIC_NAMES = (
    "sandbox_sessions_total",
    "sandbox_active_sessions",
    "sandbox_tool_executions_total",
    "sandbox_tool_duration_seconds",
    "sandbox_tool_failures_total",
    "sandbox_timeouts_total",
    "sandbox_policy_rejections_total",
)

DURATION_BUCKETS = (0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60, 120, 300)


def _label(value: Any, *, limit: int = 64) -> str:
    text = str(value or "unknown").strip() or "unknown"
    return text[:limit]


@dataclass
class SandboxMetrics:
    registry: CollectorRegistry
    service: str = "iacode-sandbox"

    def __post_init__(self) -> None:
        self.sessions_total = Counter(
            "sandbox_sessions_total", "Sandbox sessions created, by policy and outcome.",
            ["service", "policy", "outcome"], registry=self.registry)
        self.active_sessions = Gauge(
            "sandbox_active_sessions", "Sandbox sessions currently holding a container.",
            ["service"], registry=self.registry)
        self.tool_executions_total = Counter(
            "sandbox_tool_executions_total", "Tool executions, by tool and status.",
            ["service", "tool", "status"], registry=self.registry)
        self.tool_duration_seconds = Histogram(
            "sandbox_tool_duration_seconds", "How long a tool execution took, by tool.",
            ["service", "tool"], buckets=DURATION_BUCKETS, registry=self.registry)
        self.tool_failures_total = Counter(
            "sandbox_tool_failures_total", "Tool executions that did not succeed, by reason.",
            ["service", "tool", "reason"], registry=self.registry)
        self.timeouts_total = Counter(
            "sandbox_timeouts_total", "Tool executions stopped by their timeout, by tool.",
            ["service", "tool"], registry=self.registry)
        self.policy_rejections_total = Counter(
            "sandbox_policy_rejections_total", "Requests refused before execution, by reason.",
            ["service", "reason"], registry=self.registry)

    def session_created(self, policy: str, outcome: str) -> None:
        self.sessions_total.labels(service=self.service, policy=_label(policy),
                                   outcome=_label(outcome)).inc()

    def set_active_sessions(self, count: int) -> None:
        self.active_sessions.labels(service=self.service).set(max(count, 0))

    def execution(self, tool: str, status: str, seconds: float, reason: str | None) -> None:
        tool_label = _label(tool)
        self.tool_executions_total.labels(service=self.service, tool=tool_label,
                                          status=_label(status)).inc()
        self.tool_duration_seconds.labels(service=self.service,
                                          tool=tool_label).observe(max(seconds, 0.0))
        if status != "SUCCEEDED":
            self.tool_failures_total.labels(service=self.service, tool=tool_label,
                                            reason=_label(reason or status)).inc()
        if status == "TIMED_OUT":
            self.timeouts_total.labels(service=self.service, tool=tool_label).inc()

    def rejected(self, reason: str) -> None:
        self.policy_rejections_total.labels(service=self.service, reason=_label(reason)).inc()


def sandbox_log_fields(*, run_id: str | None = None, agent_id: str | None = None,
                       agent_run_id: str | None = None, sandbox_id: str | None = None,
                       tool: str | None = None, status: str | None = None,
                       duration_ms: int | None = None, reason: str | None = None
                       ) -> dict[str, str]:
    """The fields a sandbox log record carries. Absent when empty; never output, never a secret."""
    candidates = {
        "runId": run_id, "agentId": agent_id, "agentRunId": agent_run_id,
        "sandboxId": sandbox_id, "toolName": tool, "status": status,
        "durationMs": duration_ms, "reason": reason,
    }
    return {key: str(value) for key, value in candidates.items()
            if value is not None and value != ""}
