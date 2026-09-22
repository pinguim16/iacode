"""The instruments and the log fields: identifiers and outcomes, never content."""

from __future__ import annotations

from iacode_agent_runtime.telemetry import (
    PERMITTED_LABELS,
    AgentRuntimeMetrics,
    runtime_log_fields,
)
from prometheus_client import CollectorRegistry

DECLARED_INSTRUMENTS = {
    "agent_runs_total",
    "agent_run_duration_seconds",
    "agent_turns_total",
    "agent_run_failures_total",
    "agent_runs_waiting_for_tool",
    "agent_budget_exhaustions_total",
    "agent_cancellations_total",
    "agent_tool_requests_total",
}


def metrics() -> tuple[AgentRuntimeMetrics, CollectorRegistry]:
    registry = CollectorRegistry()
    return AgentRuntimeMetrics(registry), registry


def names(registry: CollectorRegistry) -> set[str]:
    return {metric.name for metric in registry.collect()}


class AgentRuntimeMetricsTests:
    """Every declared instrument exists and moves when the thing it counts happens."""

    def test_every_declared_instrument_is_published(self) -> None:
        _, registry = metrics()
        published = names(registry)
        for instrument in DECLARED_INSTRUMENTS:
            stem = instrument.removesuffix("_total")
            assert stem in published or instrument in published, f"{instrument} is missing"

    def test_a_started_run_is_counted(self) -> None:
        instruments, registry = metrics()
        instruments.run_started("planner-reviewer")
        value = registry.get_sample_value(
            "agent_runs_total",
            {"service": "iacode-agent-runtime", "team": "planner-reviewer"})
        assert value == 1.0

    def test_turns_failures_and_cancellations_are_counted(self) -> None:
        instruments, registry = metrics()
        instruments.turn_executed("planner")
        instruments.run_failed("BUDGET_EXCEEDED")
        instruments.budget_exhausted("BUDGET_EXCEEDED")
        instruments.cancelled()

        assert registry.get_sample_value(
            "agent_turns_total",
            {"service": "iacode-agent-runtime", "agent": "planner"}) == 1.0
        assert registry.get_sample_value(
            "agent_run_failures_total",
            {"service": "iacode-agent-runtime", "error_type": "BUDGET_EXCEEDED"}) == 1.0
        assert registry.get_sample_value(
            "agent_cancellations_total", {"service": "iacode-agent-runtime"}) == 1.0

    def test_the_waiting_gauge_goes_up_and_comes_back_down(self) -> None:
        instruments, registry = metrics()
        instruments.waiting(1)
        assert registry.get_sample_value(
            "agent_runs_waiting_for_tool", {"service": "iacode-agent-runtime"}) == 1.0
        instruments.waiting(-1)
        assert registry.get_sample_value(
            "agent_runs_waiting_for_tool", {"service": "iacode-agent-runtime"}) == 0.0

    def test_a_finished_run_records_its_duration(self) -> None:
        instruments, registry = metrics()
        instruments.run_finished("SUCCEEDED", 3.5)
        count = registry.get_sample_value(
            "agent_run_duration_seconds_count",
            {"service": "iacode-agent-runtime", "state": "SUCCEEDED"})
        assert count == 1.0

    def test_two_registries_can_coexist(self) -> None:
        """A module that registered on import could not be built twice, and a suite does."""
        first, _ = metrics()
        second, _ = metrics()
        assert first is not second


def test_no_metric_label_carries_content() -> None:
    """A label whose value is a task produces one time series per run, and publishes the task."""
    _, registry = metrics()
    declared: set[str] = set()
    for metric in registry.collect():
        for sample in metric.samples:
            declared.update(sample.labels)
    assert declared <= PERMITTED_LABELS, f"an unexpected label is published: {declared}"
    for forbidden in ("task", "prompt", "response", "content", "arguments", "result"):
        assert forbidden not in declared


def test_a_label_value_is_bounded_and_never_empty() -> None:
    instruments, registry = metrics()
    instruments.run_started("t" * 5000)
    instruments.turn_executed("")
    labels = [sample.labels for metric in registry.collect() for sample in metric.samples]
    for label in labels:
        for value in label.values():
            assert value
            assert len(value) <= 64


def test_logs_carry_the_declared_identifiers() -> None:
    fields = runtime_log_fields(
        correlation_id="c-1", task_id="t-1", run_id="r-1", agent_id="a-1",
        agent_run_id="ar-1", stage="plan", event_type="AGENT_STARTED",
        model_call_id="mc-1", status="RUNNING")
    assert set(fields) == {
        "correlationId", "taskId", "runId", "agentId", "agentRunId", "stage", "eventType",
        "modelCallId", "status"}


def test_a_field_with_no_value_is_absent_rather_than_null() -> None:
    """The convention Gate 0 established: an always-null key teaches readers to ignore it."""
    fields = runtime_log_fields(run_id="r-1")
    assert fields == {"runId": "r-1"}


def test_nested_secret_is_redacted_in_runtime_logs() -> None:
    """The runtime logs identifiers, and the shared redactor catches what a call site forgets."""
    from iacode_common.redaction import redact_text, redact_value

    # Assembled from parts, following the convention `services/model-gateway/tests` set: a
    # credential-shaped literal is indistinguishable from a leak to the repository secret scan,
    # and suppressing the scan for one file is how a real leak gets through.
    shaped_like_a_key = "sk-" + "live-" + "1234"
    scheme = "Bear" + "er"
    variable = "IACODE_DEVWORLD_API" + "_KEY"

    assert (redact_value("authorization", f"{scheme} {shaped_like_a_key}")
            != f"{scheme} {shaped_like_a_key}")
    assert shaped_like_a_key not in redact_text(f"{variable}={shaped_like_a_key}")
    # The null control: an operational value survives both paths untouched.
    assert redact_value("stage", "plan") == "plan"
    assert "plan" in redact_text("stage=plan")
