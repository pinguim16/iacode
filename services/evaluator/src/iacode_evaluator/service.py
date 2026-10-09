"""Stable internal use cases over quality planning and durable facts.

The HTTP and Temporal adapters call this service; callers never receive the store, a runner
implementation, an object-store client or a way to author a verdict.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from iacode_contracts.quality import (
    QUALITY_TERMINAL_RUN_STATES,
    QualityEvidence,
    QualityFinding,
    QualityPlan,
    QualityResult,
    QualityVerdict,
)

from iacode_evaluator.errors import QualityError
from iacode_evaluator.planner import build_plan
from iacode_evaluator.projects import ProjectProfile, detect_project
from iacode_evaluator.store import EventRecord, RunRecord


@dataclass(frozen=True)
class PlannedProfile:
    profile: ProjectProfile
    plan: QualityPlan


@dataclass(frozen=True)
class QualityRunView:
    run: RunRecord
    plan: QualityPlan
    results: tuple[QualityResult, ...]
    findings: tuple[QualityFinding, ...]
    evidence: tuple[QualityEvidence, ...]
    verdict: QualityVerdict | None
    events: tuple[EventRecord, ...]


class QualityService:
    def __init__(self, *, registry: Any, store: Any) -> None:
        self.registry = registry
        self.store = store

    async def create_profile_and_plan(
        self,
        *,
        snapshot_id: str,
        snapshot_digest: str,
        project_files: Mapping[str, str | bytes],
        configuration: dict[str, Any] | None,
        owner_run_id: str | None,
    ) -> PlannedProfile:
        profile = detect_project(project_files)
        plan = build_plan(
            snapshot_id=snapshot_id,
            snapshot_digest=snapshot_digest,
            project=profile,
            registry=self.registry,
            configuration=configuration,
        )
        recorded = await self.store.create_plan(plan, owner_run_id=owner_run_id)
        return PlannedProfile(profile=profile, plan=recorded.plan)

    async def start_run(
        self,
        *,
        plan_id: str,
        owner_run_id: str | None,
        idempotency_key: str,
    ) -> RunRecord:
        return await self.store.create_run(
            plan_id=plan_id,
            owner_run_id=owner_run_id,
            idempotency_key=idempotency_key,
        )

    async def get_run(self, run_id: str) -> QualityRunView:
        run = await self.store.run(run_id)
        plan = await self.store.plan_for_run(run_id)
        if run is None or plan is None:
            raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
        results = await self.store.results_for_run(run_id)
        return QualityRunView(
            run=run,
            plan=plan.plan,
            results=results,
            findings=tuple(item for result in results for item in result.findings),
            evidence=tuple(item for result in results for item in result.evidence),
            verdict=await self.store.verdict_for_run(run_id),
            events=tuple(await self.store.events(run_id, limit=500)),
        )

    async def request_cancel(
        self, run_id: str, *, request_id: str, reason: str = "cancel requested"
    ) -> RunRecord:
        run = await self.store.run(run_id)
        if run is None:
            raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
        if run.state in QUALITY_TERMINAL_RUN_STATES or run.state == "CANCELLING":
            return run
        target = "CANCELLED" if run.state in {"CREATED", "PLANNED"} else "CANCELLING"
        return await self.store.transition(
            run_id,
            state=target,
            event_type="CANCELLATION_REQUESTED",
            dedupe_key=f"cancel:{request_id}",
            payload={"reason": reason},
            reason=reason if target == "CANCELLED" else None,
        )

    async def request_reproduction(
        self,
        run_id: str,
        *,
        idempotency_key: str,
    ) -> RunRecord:
        original = await self.store.run(run_id)
        plan = await self.store.plan_for_run(run_id)
        if original is None or plan is None:
            raise QualityError("RUN_NOT_FOUND", "the quality run does not exist")
        if original.state not in QUALITY_TERMINAL_RUN_STATES:
            raise QualityError(
                "REPRODUCTION_SOURCE_ACTIVE", "only a terminal quality run can be reproduced"
            )
        reproduced = await self.store.create_run(
            plan_id=plan.plan.planId,
            owner_run_id=original.owner_run_id,
            idempotency_key=idempotency_key,
            reproduction_of_run_id=run_id,
        )
        await self.store.append_event(
            run_id,
            event_type="REPRODUCTION_REQUESTED",
            dedupe_key=f"reproduction:{idempotency_key}",
            payload={"reproducedRunId": reproduced.run_id},
        )
        return reproduced
