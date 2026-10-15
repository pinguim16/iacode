"""Durable workflow adapters, telemetry, configuration, and cancellation semantics."""

from __future__ import annotations

import asyncio
import inspect
from datetime import UTC, datetime
from types import SimpleNamespace

import iacode_evaluator.workflow as workflow_module
import pytest
from iacode_contracts.quality import QualityCheck, QualityPlan, QualityPolicy
from iacode_evaluator.activities import derive_run_verdict, record_execution, set_runtime
from iacode_evaluator.config import EvaluatorSettings
from iacode_evaluator.evidence import (
    MemoryEvidenceRepository,
    MemoryObjectStore,
    QualityEvidenceStore,
)
from iacode_evaluator.store import MemoryQualityStore
from iacode_evaluator.telemetry import METRIC_NAMES, PERMITTED_LABELS, QualityMetrics
from iacode_evaluator.workflow import (
    QualityRunWorkflow,
    enforce_accepted_cancellation,
    failed_sandbox_execution,
)
from prometheus_client import CollectorRegistry, generate_latest
from temporalio.exceptions import ActivityError
from temporalio.exceptions import CancelledError as TemporalCancelledError

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
    @pytest.mark.asyncio
    async def test_durable_cancellation_at_activity_completion_finishes_without_a_signal(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        await self._assert_cancellation_boundary(monkeypatch, "activity")

    @pytest.mark.asyncio
    async def test_durable_cancellation_during_result_write_finishes_without_a_signal(
        self, monkeypatch
    ):
        await self._assert_cancellation_boundary(monkeypatch, "result")

    @pytest.mark.asyncio
    async def test_durable_cancellation_during_verdict_write_finishes_without_a_signal(
        self, monkeypatch
    ):
        await self._assert_cancellation_boundary(monkeypatch, "verdict")

    @pytest.mark.asyncio
    async def test_cancellation_after_verdict_commit_is_not_accepted(self, monkeypatch):
        await self._assert_cancellation_boundary(monkeypatch, "after_verdict")

    @pytest.mark.asyncio
    async def test_workflow_without_cancellation_completes_successfully(self, monkeypatch):
        await self._assert_cancellation_boundary(monkeypatch, "none")

    @pytest.mark.asyncio
    async def test_unrelated_activity_failure_is_not_hidden_as_cancellation(self, monkeypatch):
        await self._assert_cancellation_boundary(monkeypatch, "unrelated_error")

    @pytest.mark.asyncio
    async def test_completed_check_joins_cancelled_durable_read_without_cancelling_run(
        self, monkeypatch,
    ):
        await self._assert_cancellation_boundary(monkeypatch, "watcher_read_cancelled")

    @pytest.mark.asyncio
    async def test_unrelated_watcher_failure_is_not_hidden_by_join_cleanup(self, monkeypatch):
        await self._assert_cancellation_boundary(monkeypatch, "watcher_unrelated_error")

    @pytest.mark.asyncio
    async def test_precompleted_watcher_cancellation_is_not_claimed_as_own_cleanup(
        self, monkeypatch,
    ):
        await self._assert_cancellation_boundary(monkeypatch, "watcher_cancelled_before_cleanup")

    async def _assert_cancellation_boundary(
        self, monkeypatch: pytest.MonkeyPatch, cancel_at: str
    ) -> None:
        from iacode_contracts.sandbox import SANDBOX_EXECUTION_KEY, SANDBOX_RELEASE_ACTIVITY
        from iacode_evaluator import activities
        from iacode_evaluator.errors import QualityError

        store = MemoryQualityStore(now=lambda: NOW)
        await store.create_plan(_plan())
        run = await store.create_run(plan_id=SHA, owner_run_id=None, idempotency_key="race")

        async def accept_cancellation():
            await store.transition(
                run.run_id, state="CANCELLING", event_type="CANCELLATION_REQUESTED",
                dedupe_key="race-cancel", payload={"reason": "operator"},
            )

        original_result = store.record_result
        original_verdict = store.record_verdict
        injected = False
        watcher_task = None
        watcher_read_started = asyncio.Event()

        async def record_result(*args, **kwargs):
            if cancel_at == "result":
                await accept_cancellation()
            if cancel_at == "unrelated_error":
                raise QualityError("UNRELATED_STORE_FAILURE", "not a cancellation")
            return await original_result(*args, **kwargs)

        async def record_verdict(verdict):
            nonlocal injected
            if cancel_at == "verdict" and not injected:
                injected = True
                await accept_cancellation()
            recorded = await original_verdict(verdict)
            if cancel_at == "after_verdict":
                with pytest.raises(QualityError) as refusal:
                    await accept_cancellation()
                assert refusal.value.code == "CANCELLATION_WINDOW_CLOSED"
            return recorded

        store.record_result = record_result
        store.record_verdict = record_verdict
        runtime = SimpleNamespace(
            store=store,
            evidence=QualityEvidenceStore(
                client=MemoryObjectStore(), bucket="artifacts",
                repository=MemoryEvidenceRepository(), now=lambda: NOW,
            ),
            metrics=QualityMetrics(CollectorRegistry()),
        )
        calls = {
            activities.READ_PLAN_ACTIVITY: activities.read_plan,
            activities.READ_RUN_ACTIVITY: activities.read_run,
            activities.TRANSITION_ACTIVITY: activities.transition_run,
            activities.RECORD_EXECUTION_ACTIVITY: activities.record_execution,
            activities.DERIVE_VERDICT_ACTIVITY: activities.derive_run_verdict,
        }

        async def execute(name, payload, **_kwargs):
            if name == SANDBOX_RELEASE_ACTIVITY:
                return {"released": 0}
            if (name == activities.READ_RUN_ACTIVITY
                    and asyncio.current_task() is watcher_task):
                watcher_read_started.set()
                if cancel_at == "watcher_cancelled_before_cleanup":
                    raise ActivityError(
                        "polling read ended before cleanup",
                        scheduled_event_id=1, started_event_id=2,
                        identity="evaluator-test", activity_type=name,
                        activity_id="watcher-read", retry_state=None,
                    ) from TemporalCancelledError("not requested by the owner's join")
                try:
                    await asyncio.Future()
                except asyncio.CancelledError:
                    cause = (TemporalCancelledError("polling read cancelled by its owner")
                             if cancel_at == "watcher_read_cancelled"
                             else QualityError("UNRELATED_READ_FAILURE", "unrelated watcher read"))
                    raise ActivityError(
                        "polling read ended", scheduled_event_id=1, started_event_id=2,
                        identity="evaluator-test", activity_type=name,
                        activity_id="watcher-read", retry_state=None,
                    ) from cause
            try:
                return await calls[name](payload)
            except QualityError as error:
                raise ActivityError(
                    str(error), scheduled_event_id=1, started_event_id=2,
                    identity="evaluator-test", activity_type=name,
                    activity_id="race-activity", retry_state=None,
                ) from error

        class CompletedActivity:
            def cancel(self):
                pass

            def __await__(self):
                async def complete():
                    if cancel_at.startswith("watcher_"):
                        await watcher_read_started.wait()
                    if cancel_at == "activity":
                        await accept_cancellation()
                    return {SANDBOX_EXECUTION_KEY: {
                        "status": "SUCCEEDED", "exitCode": 0, "durationMs": 1,
                    }}
                return complete().__await__()

        monkeypatch.setattr(workflow_module.workflow, "execute_activity", execute)
        monkeypatch.setattr(
            workflow_module.workflow, "start_activity", lambda *_a, **_k: CompletedActivity()
        )
        monkeypatch.setattr(workflow_module.workflow, "now", lambda: NOW)
        if cancel_at.startswith("watcher_"):
            original_watch = QualityRunWorkflow._watch_durable_cancellation

            async def watch(instance):
                nonlocal watcher_task
                watcher_task = asyncio.current_task()
                return await original_watch(instance)

            async def immediate_sleep(_delay):
                await asyncio.sleep(0)

            monkeypatch.setattr(QualityRunWorkflow, "_watch_durable_cancellation", watch)
            monkeypatch.setattr(workflow_module.workflow, "sleep", immediate_sleep)
        set_runtime(runtime)
        try:
            if cancel_at in {
                "unrelated_error", "watcher_unrelated_error", "watcher_cancelled_before_cleanup",
            }:
                message = ("polling read ended" if cancel_at.startswith("watcher_")
                           else "not a cancellation")
                with pytest.raises(ActivityError, match=message) as raised:
                    await QualityRunWorkflow().run({"runId": run.run_id})
                if cancel_at == "watcher_cancelled_before_cleanup":
                    assert isinstance(raised.value.cause, TemporalCancelledError)
                else:
                    assert isinstance(raised.value.cause, QualityError)
                    assert raised.value.cause.code == (
                        "UNRELATED_READ_FAILURE" if cancel_at == "watcher_unrelated_error"
                        else "UNRELATED_STORE_FAILURE"
                    )
                assert (await store.run(run.run_id)).state == "RUNNING"
                assert await store.verdict_for_run(run.run_id) is None
                return
            outcome = await QualityRunWorkflow().run({"runId": run.run_id})
        finally:
            set_runtime(None)
            await asyncio.sleep(0)

        expected_state = ("SUCCEEDED" if cancel_at in {
            "none", "after_verdict", "watcher_read_cancelled",
        } else "CANCELLED")
        expected_verdict = "PASS" if expected_state == "SUCCEEDED" else "FAIL"
        assert outcome["state"] == expected_state
        assert outcome["verdict"] == expected_verdict
        assert (await store.run(run.run_id)).state == expected_state
        assert (await store.verdict_for_run(run.run_id)).verdict == expected_verdict

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

    def test_accepted_cancellation_wins_over_a_racing_success_response(self) -> None:
        succeeded = {"status": "SUCCEEDED", "exitCode": 0, "durationMs": 12}

        execution = enforce_accepted_cancellation(succeeded, cancel_requested=True)

        assert execution["status"] == "CANCELLED"
        assert execution["errorCode"] == "QUALITY_CANCELLED"
        assert enforce_accepted_cancellation(succeeded, cancel_requested=False) is succeeded

    def test_cancellation_is_rechecked_after_dispatch_before_activity_start(self) -> None:
        source = inspect.getsource(QualityRunWorkflow._run_plan)
        dispatch = source.index('"CHECK_DISPATCHED"')
        durable_read = source.index("durable = await self._read_run()", dispatch)
        boundary = source.index("if self.cancel_requested", dispatch)
        activity = source.index("workflow.start_activity", dispatch)

        assert dispatch < durable_read < boundary < activity

    @pytest.mark.asyncio
    async def test_durable_read_completion_after_handle_clear_keeps_cancellation_authoritative(
        self, monkeypatch,
    ):
        instance = QualityRunWorkflow()
        instance.run_id = "read-completion-race"
        instance._sandbox_activity = SimpleNamespace(cancel=lambda: None)

        async def immediate_sleep(_delay):
            return None

        async def complete_after_handle_clear():
            instance._sandbox_activity = None
            return {"state": "CANCELLING"}

        monkeypatch.setattr(workflow_module.workflow, "sleep", immediate_sleep)
        instance._read_run = complete_after_handle_clear
        await instance._watch_durable_cancellation()
        assert instance.cancel_requested is True
        assert instance._sandbox_activity is None

    @pytest.mark.asyncio
    async def test_durable_cancelling_state_stops_an_active_sandbox_activity(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        instance = QualityRunWorkflow()
        instance.run_id = "quality-run-1"

        class ActivityHandle:
            cancelled = False

            def cancel(self) -> None:
                self.cancelled = True

        activity = ActivityHandle()
        instance._sandbox_activity = activity

        async def immediate_sleep(_delay: object) -> None:
            return None

        async def read_cancelling_run() -> dict[str, str]:
            instance.state = "CANCELLING"
            return {"state": "CANCELLING"}

        monkeypatch.setattr(workflow_module.workflow, "sleep", immediate_sleep)
        instance._read_run = read_cancelling_run  # type: ignore[method-assign]

        await instance._watch_durable_cancellation()

        assert instance.cancel_requested is True
        assert activity.cancelled is True

    @pytest.mark.asyncio
    async def test_a_signal_flag_set_before_handle_assignment_still_cancels_the_activity(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        instance = QualityRunWorkflow()
        instance.cancel_requested = True

        class ActivityHandle:
            cancelled = False

            def cancel(self) -> None:
                self.cancelled = True

        activity = ActivityHandle()
        instance._sandbox_activity = activity

        async def must_not_sleep(_delay: object) -> None:
            raise AssertionError("an already accepted cancellation must not wait for polling")

        monkeypatch.setattr(workflow_module.workflow, "sleep", must_not_sleep)

        await instance._watch_durable_cancellation()

        assert activity.cancelled is True

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

    @pytest.mark.asyncio
    async def test_secret_bearing_execution_is_contained_and_derives_fail(self) -> None:
        store = MemoryQualityStore(now=lambda: NOW)
        await store.create_plan(_plan())
        run = await store.create_run(plan_id=SHA, owner_run_id=None, idempotency_key="run-secret")
        for state, event in (("PLANNED", "PLANNED"), ("QUEUED", "QUEUED"), ("RUNNING", "STARTED")):
            await store.transition(
                run.run_id,
                state=state,
                event_type=event,
                dedupe_key=f"secret:{state}",
                payload={},
            )
        objects = MemoryObjectStore()
        repository = MemoryEvidenceRepository()
        evidence = QualityEvidenceStore(
            client=objects,
            bucket="artifacts",
            repository=repository,
            now=lambda: NOW,
        )
        set_runtime(
            SimpleNamespace(
                store=store,
                evidence=evidence,
                metrics=QualityMetrics(CollectorRegistry()),
            )
        )
        marker = "gh" + "p_" + "c" * 20
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
                        "output": {"stdout": marker},
                    },
                }
            )
            verdict = await derive_run_verdict(
                {"runId": run.run_id, "derivedAt": NOW.isoformat()}
            )
        finally:
            set_runtime(None)

        assert result["status"] == "ERROR"
        assert result["exitCode"] is None
        assert result["evidence"] == []
        assert result["findings"] == []
        assert result["summary"] == "quality evidence was rejected before persistence"
        assert verdict["verdict"] == "FAIL"
        assert repository.records == {}
        assert objects.objects == {}
        assert marker not in str(result)
        assert marker not in str(verdict)


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
