"""Durable workflow adapters, telemetry, configuration, and cancellation semantics."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from iacode_contracts.quality import QualityCheck, QualityPlan, QualityPolicy
from iacode_evaluator.activities import record_execution, set_runtime
from iacode_evaluator.config import EvaluatorSettings
from iacode_evaluator.evidence import (
    MemoryEvidenceRepository,
    MemoryObjectStore,
    QualityEvidenceStore,
)
from iacode_evaluator.store import MemoryQualityStore
from iacode_evaluator.telemetry import METRIC_NAMES, PERMITTED_LABELS, QualityMetrics
from iacode_evaluator.workflow import QualityRunWorkflow, failed_sandbox_execution
from prometheus_client import CollectorRegistry, generate_latest
from temporalio.exceptions import ActivityError

NOW = datetime(2026, 10, 9, 18, tzinfo=UTC)
SHA = "a" * 64
OTHER_SHA = "b" * 64


def _plan() -> QualityPlan:
    return QualityPlan(
        planId=SHA,
        snapshotId="snapshot-1",
        snapshotDigest=OTHER_SHA,
        projectProfile="python",
        projectProfileDigest=SHA,
        policy=QualityPolicy(
            policyId="default",
            version="1.0.0",
            digest=OTHER_SHA,
            profile="python",
            mandatoryCheckKinds=("unit",),
            maxRunSeconds=60,
            maxCheckSeconds=30,
            maxOutputBytes=4096,
        ),
        checks=(
            QualityCheck(
                checkId="q001-unit",
                kind="unit",
                runner="python.unit",
                command=("python", "-m", "unittest"),
                applicabilityReason="required by the Python profile",
                timeoutSeconds=30,
            ),
        ),
        createdAt=NOW,
    )


class QualityWorkflowAdapterTests:
    def test_the_temporal_workflow_uses_the_shared_name(self) -> None:
        definition = getattr(QualityRunWorkflow, "__temporal_workflow_definition")
        assert definition.name == "IACodeQualityRun"

    def test_an_acknowledged_activity_cancellation_stays_a_cancellation(self) -> None:
        error = ActivityError(
            "cancelled",
            scheduled_event_id=1,
            started_event_id=2,
            identity="evaluator-test",
            activity_type="iacode_sandbox_execute_tool",
            activity_id="activity-1",
            retry_state=None,
        )
        cancelled = failed_sandbox_execution(error, cancel_requested=True)
        failed = failed_sandbox_execution(error, cancel_requested=False)

        assert cancelled["status"] == "CANCELLED"
        assert cancelled["errorCode"] == "QUALITY_CANCELLED"
        assert failed["status"] == "ERROR"
        assert failed["errorCode"] == "SANDBOX_ACTIVITY_FAILED"

    @pytest.mark.asyncio
    async def test_a_sandbox_answer_becomes_redacted_immutable_evidence(self) -> None:
        store = MemoryQualityStore(now=lambda: NOW)
        await store.create_plan(_plan())
        run = await store.create_run(plan_id=SHA, owner_run_id=None, idempotency_key="run-1")
        for state, event in (("PLANNED", "PLANNED"), ("QUEUED", "QUEUED"), ("RUNNING", "STARTED")):
            await store.transition(
                run.run_id,
                state=state,
                event_type=event,
                dedupe_key=f"state:{state}",
                payload={},
            )
        objects = MemoryObjectStore()
        evidence = QualityEvidenceStore(
            client=objects,
            bucket="artifacts",
            repository=MemoryEvidenceRepository(),
            now=lambda: NOW,
        )
        registry = CollectorRegistry()
        set_runtime(
            SimpleNamespace(store=store, evidence=evidence, metrics=QualityMetrics(registry))
        )
        try:
            result = await record_execution(
                {
                    "runId": run.run_id,
                    "checkId": "q001-unit",
                    "finishedAt": NOW.isoformat(),
                    "execution": {
                        "status": "SUCCEEDED",
                        "exitCode": 0,
                        "durationMs": 12,
                        "output": {"stdout": "to" + "ken=should-not-survive"},
                    },
                }
            )
        finally:
            set_runtime(None)
        assert result["status"] == "PASSED"
        content = next(iter(objects.objects.values())).decode("utf-8")
        assert "should-not-survive" not in content
        assert "[REDACTED]" in content


class QualityOperationsTests:
    def test_configuration_refuses_schemes_and_wrong_database_drivers(self) -> None:
        with pytest.raises(ValueError, match="host:port"):
            EvaluatorSettings(temporal_target="http://temporal:7233")
        with pytest.raises(ValueError, match=r"postgresql\+asyncpg"):
            EvaluatorSettings(database_url="postgresql://db/example")

    def test_metric_names_and_labels_are_closed_and_low_cardinality(self) -> None:
        registry = CollectorRegistry()
        metrics = QualityMetrics(registry)
        metrics.started()
        metrics.check("unit", "PASSED", 10)
        metrics.finding("HIGH", "unit")
        metrics.evidence()
        metrics.verdict("PASS")
        metrics.completed("SUCCEEDED")
        rendered = generate_latest(registry).decode("utf-8")
        assert all(
            name in rendered for name in METRIC_NAMES if name != "quality_runs_planned_total"
        )
        for collector in registry._collector_to_names:
            assert set(getattr(collector, "_labelnames", ())) <= PERMITTED_LABELS
        for forbidden in ("run_id", "artifact_id", "digest", "command", "output", "path"):
            assert forbidden not in PERMITTED_LABELS
