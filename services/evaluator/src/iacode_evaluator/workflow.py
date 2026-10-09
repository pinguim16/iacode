"""Replay-safe Temporal workflow for one frozen quality plan."""

from __future__ import annotations

import asyncio
import math
from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError
from temporalio.workflow import ActivityCancellationType

with workflow.unsafe.imports_passed_through():
    from iacode_contracts.quality import (
        QUALITY_CANCEL_SIGNAL,
        QUALITY_REPRODUCE_SIGNAL,
        QUALITY_RUN_WORKFLOW,
        QUALITY_TASK_QUEUE,
        QUALITY_TERMINAL_RUN_STATES,
        QualityPlan,
    )
    from iacode_contracts.sandbox import (
        SANDBOX_EXECUTE_ACTIVITY,
        SANDBOX_EXECUTION_KEY,
        SANDBOX_RELEASE_ACTIVITY,
        SANDBOX_TASK_QUEUE,
    )

    from iacode_evaluator.activities import (
        DERIVE_VERDICT_ACTIVITY,
        READ_PLAN_ACTIVITY,
        READ_RUN_ACTIVITY,
        RECORD_EXECUTION_ACTIVITY,
        TRANSITION_ACTIVITY,
    )
    from iacode_evaluator.executor import quality_tool_request_id, sandbox_request

STORE_TIMEOUT = timedelta(seconds=30)
SANDBOX_HEARTBEAT_TIMEOUT = timedelta(seconds=120)
ACTIVITY_RETRY = RetryPolicy(maximum_attempts=5)


def failed_sandbox_execution(error: ActivityError, *, cancel_requested: bool) -> dict[str, Any]:
    """Normalize Temporal's activity failure without losing an acknowledged cancellation.

    With ``WAIT_CANCELLATION_COMPLETED`` Temporal reports the cancelled activity through
    ``ActivityError`` after the sandbox has acknowledged cleanup. The workflow signal is the
    authoritative reason in that branch; treating it as a generic error would make the store
    correctly reject the non-cancellation callback while the run remains CANCELLING forever.
    """
    if cancel_requested:
        return {
            "status": "CANCELLED",
            "errorCode": "QUALITY_CANCELLED",
            "error": "the quality check was cancelled and sandbox cleanup acknowledged",
            "durationMs": 0,
        }
    return {
        "status": "ERROR",
        "errorCode": "SANDBOX_ACTIVITY_FAILED",
        "error": f"the sandbox activity failed: {type(error).__name__}",
        "durationMs": 0,
    }


@workflow.defn(name=QUALITY_RUN_WORKFLOW)
class QualityRunWorkflow:
    def __init__(self) -> None:
        self.run_id = ""
        self.state = "CREATED"
        self.current_check: str | None = None
        self.cancel_requested = False
        self.reproduction_requested = False
        self._sandbox_activity: Any = None

    @workflow.signal(name=QUALITY_CANCEL_SIGNAL)
    async def cancel(self, _reason: str = "cancel requested") -> None:
        self.cancel_requested = True
        if self._sandbox_activity is not None:
            self._sandbox_activity.cancel()

    @workflow.signal(name=QUALITY_REPRODUCE_SIGNAL)
    async def reproduce(self) -> None:
        self.reproduction_requested = True

    @workflow.query
    def status(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "state": self.state,
            "currentCheck": self.current_check,
            "cancelRequested": self.cancel_requested,
            "reproductionRequested": self.reproduction_requested,
        }

    async def _transition(
        self,
        state: str,
        event_type: str,
        dedupe_key: str,
        payload: dict[str, Any],
        reason: str | None = None,
    ) -> None:
        body: dict[str, Any] = {
            "runId": self.run_id,
            "state": state,
            "eventType": event_type,
            "dedupeKey": dedupe_key,
            "payload": payload,
        }
        if reason is not None:
            body["reason"] = reason
        result = await workflow.execute_activity(
            TRANSITION_ACTIVITY,
            body,
            task_queue=QUALITY_TASK_QUEUE,
            start_to_close_timeout=STORE_TIMEOUT,
            retry_policy=ACTIVITY_RETRY,
        )
        self.state = str(result["state"])

    async def _read_run(self) -> dict[str, Any]:
        result = await workflow.execute_activity(
            READ_RUN_ACTIVITY,
            {"runId": self.run_id},
            task_queue=QUALITY_TASK_QUEUE,
            start_to_close_timeout=STORE_TIMEOUT,
            retry_policy=ACTIVITY_RETRY,
        )
        self.state = str(result["state"])
        return result

    async def _read_plan(self) -> QualityPlan:
        result = await workflow.execute_activity(
            READ_PLAN_ACTIVITY,
            {"runId": self.run_id},
            task_queue=QUALITY_TASK_QUEUE,
            start_to_close_timeout=STORE_TIMEOUT,
            retry_policy=ACTIVITY_RETRY,
        )
        return QualityPlan.model_validate(result)

    async def _record(self, check_id: str, execution: dict[str, Any]) -> dict[str, Any]:
        return await workflow.execute_activity(
            RECORD_EXECUTION_ACTIVITY,
            {
                "runId": self.run_id,
                "checkId": check_id,
                "execution": execution,
                "finishedAt": workflow.now().isoformat(),
            },
            task_queue=QUALITY_TASK_QUEUE,
            start_to_close_timeout=STORE_TIMEOUT,
            retry_policy=ACTIVITY_RETRY,
        )

    async def _verdict(self) -> dict[str, Any]:
        return await workflow.execute_activity(
            DERIVE_VERDICT_ACTIVITY,
            {"runId": self.run_id, "derivedAt": workflow.now().isoformat()},
            task_queue=QUALITY_TASK_QUEUE,
            start_to_close_timeout=STORE_TIMEOUT,
            retry_policy=ACTIVITY_RETRY,
        )

    async def _release(self, reason: str) -> None:
        released = await workflow.execute_activity(
            SANDBOX_RELEASE_ACTIVITY,
            {"runId": self.run_id},
            task_queue=SANDBOX_TASK_QUEUE,
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=ACTIVITY_RETRY,
        )
        await self._transition(
            self.state,
            "SANDBOX_RELEASED",
            f"workflow:sandbox-released:{reason}",
            {"released": int(released.get("released") or 0)},
        )

    async def _finish_cancelled(self, plan: QualityPlan) -> dict[str, Any]:
        if self.state not in {"CANCELLING", "CANCELLED"}:
            await self._transition(
                "CANCELLING",
                "CANCELLATION_REQUESTED",
                "workflow:cancellation-requested",
                {"reason": "workflow cancellation signal"},
            )
        if self.state == "CANCELLED":
            return {"runId": self.run_id, "state": self.state, "verdict": "FAIL"}
        await self._release("cancellation")
        verdict = await self._verdict()
        await self._transition(
            "CANCELLED",
            "COMPLETED",
            "workflow:cancelled",
            {"verdict": verdict["verdict"]},
            reason="quality run cancelled after sandbox cleanup",
        )
        return {"runId": self.run_id, "state": self.state, "verdict": verdict["verdict"]}

    @workflow.run
    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.run_id = str(payload["runId"])
        plan = await self._read_plan()
        started = workflow.now()
        await self._read_run()
        if self.state in QUALITY_TERMINAL_RUN_STATES:
            return {"runId": self.run_id, "state": self.state, "verdict": "FAIL"}
        if self.state == "CANCELLING":
            self.cancel_requested = True
            return await self._finish_cancelled(plan)
        await self._transition("PLANNED", "PLANNED", "workflow:planned", {"planId": plan.planId})
        if self.state in QUALITY_TERMINAL_RUN_STATES:
            return {"runId": self.run_id, "state": self.state, "verdict": "FAIL"}
        if self.cancel_requested:
            return await self._finish_cancelled(plan)
        await self._transition("QUEUED", "QUEUED", "workflow:queued", {})
        await self._transition("RUNNING", "STARTED", "workflow:started", {})

        deadline_hit = False
        for check in plan.checks:
            if not check.applicable:
                continue
            if self.cancel_requested:
                return await self._finish_cancelled(plan)
            self.current_check = check.checkId
            await self._transition(
                "RUNNING",
                "CHECK_DISPATCHED",
                f"workflow:dispatch:{check.checkId}",
                {"checkId": check.checkId, "kind": check.kind},
            )
            elapsed = (workflow.now() - started).total_seconds()
            remaining = plan.policy.maxRunSeconds - elapsed
            if remaining <= 0:
                execution = {
                    "status": "TIMED_OUT",
                    "errorCode": "QUALITY_RUN_DEADLINE_EXCEEDED",
                    "error": "the policy-owned quality run deadline expired",
                    "durationMs": 0,
                    "timedOut": True,
                }
                await self._record(check.checkId, execution)
                deadline_hit = True
                break
            timeout = max(1, min(check.timeoutSeconds, math.ceil(remaining)))
            request = sandbox_request(
                run_id=self.run_id,
                tool_request_id=quality_tool_request_id(self.run_id, check.checkId),
                plan=plan,
                check=check,
            )
            self._sandbox_activity = workflow.start_activity(
                SANDBOX_EXECUTE_ACTIVITY,
                request,
                task_queue=SANDBOX_TASK_QUEUE,
                start_to_close_timeout=timedelta(seconds=timeout + 30),
                heartbeat_timeout=SANDBOX_HEARTBEAT_TIMEOUT,
                cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
                retry_policy=RetryPolicy(maximum_attempts=1),
            )
            try:
                response = await self._sandbox_activity
                execution = dict(response[SANDBOX_EXECUTION_KEY])
            except asyncio.CancelledError:
                execution = {
                    "status": "CANCELLED",
                    "errorCode": "QUALITY_CANCELLED",
                    "error": "the quality check was cancelled and sandbox cleanup acknowledged",
                    "durationMs": 0,
                }
            except ActivityError as error:
                execution = failed_sandbox_execution(error, cancel_requested=self.cancel_requested)
            finally:
                self._sandbox_activity = None
            await self._record(check.checkId, execution)
            if self.cancel_requested or execution["status"] == "CANCELLED":
                return await self._finish_cancelled(plan)
            await self._release(check.checkId)
            if execution["status"] == "TIMED_OUT":
                deadline_hit = True

        self.current_check = None
        verdict = await self._verdict()
        await self._release("final")
        if deadline_hit:
            terminal = "TIMED_OUT"
            reason = "one or more policy-owned quality deadlines expired"
        elif verdict["verdict"] == "PASS":
            terminal = "SUCCEEDED"
            reason = "derived quality verdict PASS"
        else:
            terminal = "FAILED"
            reason = "derived quality verdict FAIL"
        await self._transition(
            terminal,
            "COMPLETED",
            "workflow:completed",
            {"verdict": verdict["verdict"]},
            reason=reason,
        )
        return {"runId": self.run_id, "state": self.state, "verdict": verdict["verdict"]}


__all__ = ["QualityRunWorkflow", "failed_sandbox_execution"]
