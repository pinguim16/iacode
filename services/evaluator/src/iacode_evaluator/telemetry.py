"""Low-cardinality metrics and bounded structured log fields for quality work."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

PERMITTED_LABELS = frozenset(
    {"service", "profile", "status", "check_kind", "severity", "category", "verdict"}
)
METRIC_NAMES = (
    "quality_runs_planned_total",
    "quality_active_runs",
    "quality_runs_completed_total",
    "quality_checks_total",
    "quality_check_duration_seconds",
    "quality_findings_total",
    "quality_evidence_writes_total",
    "quality_verdicts_total",
)
DURATION_BUCKETS = (0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60, 120, 300, 900, 1800)


def _label(value: Any, limit: int = 64) -> str:
    return (str(value or "unknown").strip() or "unknown")[:limit]


@dataclass
class QualityMetrics:
    registry: CollectorRegistry
    service: str = "iacode-evaluator"

    def __post_init__(self) -> None:
        self.runs_planned = Counter(
            "quality_runs_planned_total",
            "Frozen quality plans created by profile.",
            ["service", "profile"],
            registry=self.registry,
        )
        self.active_runs = Gauge(
            "quality_active_runs",
            "Quality runs whose workflow has started and not completed.",
            ["service"],
            registry=self.registry,
        )
        self.runs_completed = Counter(
            "quality_runs_completed_total",
            "Terminal quality runs by status.",
            ["service", "status"],
            registry=self.registry,
        )
        self.checks = Counter(
            "quality_checks_total",
            "Quality checks by closed kind and status.",
            ["service", "check_kind", "status"],
            registry=self.registry,
        )
        self.check_duration = Histogram(
            "quality_check_duration_seconds",
            "Quality check duration by closed kind and status.",
            ["service", "check_kind", "status"],
            buckets=DURATION_BUCKETS,
            registry=self.registry,
        )
        self.findings = Counter(
            "quality_findings_total",
            "Quality findings by bounded severity and category.",
            ["service", "severity", "category"],
            registry=self.registry,
        )
        self.evidence_writes = Counter(
            "quality_evidence_writes_total",
            "Immutable quality evidence references written.",
            ["service", "status"],
            registry=self.registry,
        )
        self.verdicts = Counter(
            "quality_verdicts_total",
            "Derived quality verdicts.",
            ["service", "verdict"],
            registry=self.registry,
        )

    def planned(self, profile: str) -> None:
        self.runs_planned.labels(service=self.service, profile=_label(profile)).inc()

    def started(self) -> None:
        self.active_runs.labels(service=self.service).inc()

    def completed(self, status: str) -> None:
        self.active_runs.labels(service=self.service).dec()
        self.runs_completed.labels(service=self.service, status=_label(status)).inc()

    def check(self, kind: str, status: str, duration_ms: int) -> None:
        labels = {"service": self.service, "check_kind": _label(kind), "status": _label(status)}
        self.checks.labels(**labels).inc()
        self.check_duration.labels(**labels).observe(max(duration_ms, 0) / 1000)

    def finding(self, severity: str, category: str) -> None:
        self.findings.labels(
            service=self.service, severity=_label(severity), category=_label(category)
        ).inc()

    def evidence(self, status: str = "stored") -> None:
        self.evidence_writes.labels(service=self.service, status=_label(status)).inc()

    def verdict(self, value: str) -> None:
        self.verdicts.labels(service=self.service, verdict=_label(value)).inc()


def quality_log_fields(
    *,
    correlation_id: str | None = None,
    run_id: str | None = None,
    plan_id: str | None = None,
    check_id: str | None = None,
    sandbox_id: str | None = None,
    status: str | None = None,
    duration_ms: int | None = None,
    reason: str | None = None,
) -> dict[str, str]:
    candidates = {
        "correlationId": correlation_id,
        "runId": run_id,
        "planId": plan_id,
        "checkId": check_id,
        "sandboxId": sandbox_id,
        "status": status,
        "durationMs": duration_ms,
        "reason": reason,
    }
    return {key: str(value) for key, value in candidates.items() if value not in (None, "")}


__all__ = ["METRIC_NAMES", "PERMITTED_LABELS", "QualityMetrics", "quality_log_fields"]
