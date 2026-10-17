"""Allowlisted observations of actual runtime/quality facts; no provider invocation.

Text from goals, answers, event payloads, arguments, summaries and catalog raw metadata is never
projected. Source objects are bounded and rehashed, not trusted because a row says PASS.
"""

from __future__ import annotations

import asyncio
import hashlib
import uuid
from datetime import datetime
from typing import Any

from iacode_contracts.experience import CaptureExperience, ExperienceDocument, ExperienceTask
from iacode_contracts.quality import QUALITY_TERMINAL_RUN_STATES
from iacode_contracts.sandbox import WORKSPACE_SNAPSHOT_ARTIFACT_KIND
from iacode_evaluator.canonical import digest as quality_digest
from iacode_evaluator.evidence import SqlEvidenceRepository
from iacode_evaluator.verdict import derive_verdict, verdict_digest
from iacode_experience.domain import (
    ExperienceError,
    ExperiencePolicy,
    canonical,
    digest,
    require_safe,
    validate_document,
)
from iacode_persistence.models import (
    AgentRun,
    Artifact,
    Model,
    ModelCall,
    Provider,
    RunEvent,
    Task,
    TaskRun,
    ToolCall,
    ToolRequest,
)
from iacode_persistence.models import QualityPlan as QualityPlanRow
from iacode_persistence.models import QualityResult as QualityResultRow
from iacode_persistence.models import QualityRun as QualityRunRow
from iacode_persistence.models import QualityVerdict as QualityVerdictRow
from sqlalchemy import Text, cast, func, select
from sqlalchemy.orm import load_only


def _time(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _id(value: uuid.UUID | None) -> str | None:
    return str(value) if value is not None else None


class SqlExperienceSources:
    def __init__(
        self,
        session_factory: Any,
        client: Any,
        quality_store: Any,
        policy: ExperiencePolicy,
        known_credentials: tuple[str, ...],
    ) -> None:
        self.sessions = session_factory
        self.client = client
        self.quality = quality_store
        self.policy = policy
        self.credentials = known_credentials
        self.evidence = SqlEvidenceRepository(session_factory)

    async def _object(self, artifact: Artifact, *, maximum: int, scan: bool) -> bytes:
        if not 0 <= artifact.size_bytes <= maximum:
            raise ExperienceError("SOURCE_OBJECT_LIMIT_EXCEEDED")

        def read() -> bytes:
            response = self.client.get_object(artifact.storage_bucket, artifact.storage_key)
            try:
                # Bound the actual transfer even if a row/remote object was tampered with.
                return response.read(artifact.size_bytes + 1)
            finally:
                response.close()
                response.release_conn()

        try:
            raw = await asyncio.to_thread(read)
        except Exception as error:
            raise ExperienceError("SOURCE_OBJECT_UNAVAILABLE") from error
        if (
            len(raw) != artifact.size_bytes
            or hashlib.sha256(raw).hexdigest() != artifact.checksum_sha256
        ):
            raise ExperienceError("SOURCE_OBJECT_CORRUPT")
        if scan:
            require_safe(raw, self.credentials)
        return raw

    async def _bounded(self, session: Any, statement: Any) -> list:
        rows = (await session.execute(statement.limit(self.policy.maxFacts + 1))).all()
        if len(rows) > self.policy.maxFacts:
            raise ExperienceError("SOURCE_FACT_LIMIT_EXCEEDED")
        return rows

    async def _bound_json(self, session: Any, column: Any, condition: Any) -> None:
        # Bound the actual structured bytes in SQL, before a driver materializes them in memory.
        size = await session.scalar(
            select(func.sum(func.octet_length(cast(column, Text)))).where(condition)
        )
        if (size or 0) > self.policy.maxBodyBytes:
            raise ExperienceError("SOURCE_FACT_LIMIT_EXCEEDED")

    async def _artifact(self, session: Any, identifier: uuid.UUID) -> Artifact | None:
        return await session.get(
            Artifact,
            identifier,
            options=[
                load_only(
                    Artifact.id,
                    Artifact.kind,
                    Artifact.storage_bucket,
                    Artifact.storage_key,
                    Artifact.size_bytes,
                    Artifact.checksum_sha256,
                    raiseload=True,
                )
            ],
        )

    async def _quality(
        self, project_id: str, request: CaptureExperience, files: dict
    ) -> tuple[dict | None, dict, list[dict]]:
        if request.qualityRunId is None:
            return None, {"checks": [], "caseCount": None}, []
        # Bound corrupt source bodies/cardinality in SQL before any typed store loads them.
        quality_id = uuid.UUID(request.qualityRunId)
        async with self.sessions() as session:
            for model, condition in (
                (
                    QualityPlanRow,
                    QualityPlanRow.id
                    == select(QualityRunRow.quality_plan_id)
                    .where(QualityRunRow.id == quality_id)
                    .scalar_subquery(),
                ),
                (QualityVerdictRow, QualityVerdictRow.quality_run_id == quality_id),
                (QualityResultRow, QualityResultRow.quality_run_id == quality_id),
            ):
                count, size = (
                    await session.execute(
                        select(func.count(), func.sum(func.octet_length(cast(model.content, Text))))
                        .select_from(model)
                        .where(condition)
                    )
                ).one()
                if count > self.policy.maxFacts or (size or 0) > 4 * 1024 * 1024:
                    raise ExperienceError("SOURCE_FACT_LIMIT_EXCEEDED")
        run = await self.quality.run(request.qualityRunId)
        if run is None or run.state not in QUALITY_TERMINAL_RUN_STATES or run.finished_at is None:
            raise ExperienceError("QUALITY_SOURCE_NOT_TERMINAL")
        plan_record = await self.quality.plan_for_run(request.qualityRunId)
        verdict = await self.quality.verdict_for_run(request.qualityRunId)
        if plan_record is None or verdict is None:
            raise ExperienceError("QUALITY_SOURCE_INCOMPLETE")
        plan = plan_record.plan
        if (
            run.owner_run_id not in (None, request.taskRunId)
            or plan_record.owner_run_id not in (None, request.taskRunId)
            or plan.snapshotId != files["snapshotId"]
            or plan.snapshotDigest != files["digest"]
        ):
            raise ExperienceError("QUALITY_SOURCE_MISMATCH")
        expected_plan = quality_digest(
            {
                "contractVersion": plan.contractVersion,
                "snapshotId": plan.snapshotId,
                "snapshotDigest": plan.snapshotDigest,
                "projectProfile": plan.projectProfile,
                "projectProfileDigest": plan.projectProfileDigest,
                "policyDigest": plan.policy.digest,
                "checks": [check.model_dump(mode="json") for check in plan.checks],
            }
        )
        if expected_plan != plan.planId or len(plan.checks) > self.policy.maxFacts:
            raise ExperienceError("QUALITY_PLAN_CORRUPT")
        results = await self.quality.results_for_run(request.qualityRunId)
        if len(results) > self.policy.maxFacts:
            raise ExperienceError("SOURCE_FACT_LIMIT_EXCEEDED")
        resolved: set[str] = set()
        provenance: list[dict] = []
        evidence_count = 0
        for result in results:
            for evidence in result.evidence:
                evidence_count += 1
                if evidence_count > self.policy.maxFacts:
                    raise ExperienceError("SOURCE_FACT_LIMIT_EXCEEDED")
                record = await self.evidence.by_evidence_id(evidence.evidenceId)
                if (
                    record is None
                    or record.contract != evidence
                    or record.run_id != request.qualityRunId
                    or not evidence.storageAllowed
                ):
                    raise ExperienceError("SOURCE_PERMISSION_REFUSED")
                async with self.sessions() as session:
                    artifact = await self._artifact(session, uuid.UUID(evidence.artifactId))
                if artifact is None or artifact.checksum_sha256 != evidence.digest:
                    raise ExperienceError("QUALITY_EVIDENCE_CORRUPT")
                await self._object(artifact, maximum=4 * 1024 * 1024, scan=True)
                resolved.add(evidence.digest)
                if not any(item["sourceId"] == evidence.artifactId for item in provenance):
                    provenance.append(
                        {
                            "sourceType": "quality-evidence",
                            "sourceId": evidence.artifactId,
                            "digest": evidence.digest,
                            "storageAllowed": True,
                        }
                    )
        derived = derive_verdict(
            run_id=request.qualityRunId,
            plan=plan,
            results=results,
            resolved_evidence_digests=resolved,
            derived_at=verdict.derivedAt,
            cancel_requested=run.cancel_requested,
        )
        if verdict_digest(verdict) != verdict.digest or derived != verdict:
            raise ExperienceError("QUALITY_VERDICT_CORRUPT")
        if (run.state == "SUCCEEDED") != (verdict.verdict == "PASS"):
            raise ExperienceError("QUALITY_VERDICT_CORRUPT")
        by_check = {result.checkId: result for result in results}
        tests = {
            "checks": [
                {
                    "checkId": check.checkId,
                    "kind": check.kind,
                    "runner": check.runner,
                    "status": by_check[check.checkId].status if check.checkId in by_check else None,
                    "resultDigest": quality_digest(by_check[check.checkId].model_dump(mode="json"))
                    if check.checkId in by_check
                    else None,
                    "caseCount": None,
                }
                for check in plan.checks
            ],
            "caseCount": None,
        }
        return (
            {
                "runId": request.qualityRunId,
                "planDigest": plan.planId,
                "verdict": verdict.verdict,
                "verdictDigest": verdict.digest,
                "resultDigests": list(verdict.resultDigests),
                "evidenceDigests": list(verdict.evidenceDigests),
            },
            tests,
            provenance,
        )

    async def observe(
        self, project_id: str, request: CaptureExperience, now: datetime
    ) -> ExperienceDocument:
        async with self.sessions() as session:
            source = (
                await session.execute(
                    select(TaskRun, Task.project_id)
                    .options(
                        load_only(
                            TaskRun.id,
                            TaskRun.task_id,
                            TaskRun.status,
                            TaskRun.attempt,
                            TaskRun.started_at,
                            TaskRun.finished_at,
                            raiseload=True,
                        )
                    )
                    .join(Task)
                    .where(
                        TaskRun.id == uuid.UUID(request.taskRunId),
                        Task.project_id == uuid.UUID(project_id),
                    )
                )
            ).first()
            if source is None:
                raise ExperienceError("SOURCE_NOT_FOUND")
            run = source[0]
            if run.status not in ("SUCCEEDED", "FAILED", "CANCELLED") or run.finished_at is None:
                raise ExperienceError("SOURCE_NOT_TERMINAL")
            await self._bound_json(session, TaskRun.workspace, TaskRun.id == run.id)
            workspace_kind, snapshot_id, snapshot_checksum = (
                await session.execute(
                    select(
                        TaskRun.workspace["kind"].as_string(),
                        TaskRun.workspace["artifactId"].as_string(),
                        TaskRun.workspace["checksum"].as_string(),
                    ).where(TaskRun.id == run.id)
                )
            ).one()
            agents = await self._bounded(
                session,
                select(AgentRun)
                .options(
                    load_only(
                        AgentRun.id,
                        AgentRun.stage_index,
                        AgentRun.status,
                        AgentRun.started_at,
                        AgentRun.finished_at,
                        raiseload=True,
                    )
                )
                .where(AgentRun.task_run_id == run.id)
                .order_by(AgentRun.stage_index, AgentRun.id),
            )
            events = await self._bounded(
                session,
                select(RunEvent)
                .options(
                    load_only(
                        RunEvent.id,
                        RunEvent.sequence,
                        RunEvent.event_type,
                        RunEvent.created_at,
                        raiseload=True,
                    )
                )
                .where(RunEvent.task_run_id == run.id)
                .order_by(RunEvent.sequence),
            )
            calls = await self._bounded(
                session,
                select(ModelCall, Provider.slug, Model.slug)
                .options(load_only(ModelCall.id, raiseload=True))
                .join(AgentRun, ModelCall.agent_run_id == AgentRun.id)
                .outerjoin(Provider, ModelCall.provider_id == Provider.id)
                .outerjoin(Model, ModelCall.model_id == Model.id)
                .where(AgentRun.task_run_id == run.id)
                .order_by(ModelCall.id),
            )
            tools = await self._bounded(
                session,
                select(ToolCall)
                .options(
                    load_only(
                        ToolCall.id,
                        ToolCall.tool_request_id,
                        ToolCall.sandbox_session_id,
                        ToolCall.tool_name,
                        ToolCall.status,
                        ToolCall.succeeded,
                        ToolCall.exit_code,
                        ToolCall.latency_ms,
                        raiseload=True,
                    )
                )
                .join(AgentRun)
                .where(AgentRun.task_run_id == run.id)
                .order_by(ToolCall.id),
            )
            command_scope = (ToolRequest.task_run_id == run.id) & (
                ToolRequest.tool_name == "shell.exec"
            )
            await self._bound_json(session, ToolRequest.arguments, command_scope)
            commands = await self._bounded(
                session,
                select(ToolRequest)
                .options(
                    load_only(
                        ToolRequest.id, ToolRequest.tool_name, ToolRequest.arguments, raiseload=True
                    )
                )
                .where(ToolRequest.task_run_id == run.id, ToolRequest.tool_name == "shell.exec")
                .order_by(ToolRequest.id),
            )
            files = {"snapshotId": None, "digest": None, "sizeBytes": None, "fileCount": None}
            if workspace_kind == "snapshot":
                snapshot = await self._artifact(session, uuid.UUID(str(snapshot_id)))
                if (
                    snapshot is None
                    or snapshot.kind != WORKSPACE_SNAPSHOT_ARTIFACT_KIND
                    or snapshot.checksum_sha256 != snapshot_checksum
                ):
                    raise ExperienceError("SNAPSHOT_SOURCE_MISMATCH")
                permission_type, permission = (
                    await session.execute(
                        select(
                            func.jsonb_typeof(Artifact.metadata_["storageAllowed"]),
                            Artifact.metadata_["storageAllowed"].as_string(),
                        ).where(Artifact.id == snapshot.id)
                    )
                ).one()
                if permission_type is not None and (
                    permission_type != "boolean" or permission != "true"
                ):
                    raise ExperienceError("SOURCE_PERMISSION_REFUSED")
                await self._object(snapshot, maximum=64 * 1024 * 1024, scan=False)
                files = {
                    "snapshotId": str(snapshot.id),
                    "digest": snapshot.checksum_sha256,
                    "sizeBytes": snapshot.size_bytes,
                    "fileCount": None,
                }
            quality, tests, provenance = await self._quality(project_id, request, files)
            if files["snapshotId"] is not None:
                provenance.insert(
                    0,
                    {
                        "sourceType": "workspace-snapshot",
                        "sourceId": files["snapshotId"],
                        "digest": files["digest"],
                        "storageAllowed": True,
                    },
                )
            task = {
                "projectId": project_id,
                "taskId": str(run.task_id),
                "runId": str(run.id),
                "status": run.status,
                "attempt": run.attempt,
                "startedAt": _time(run.started_at),
                "finishedAt": _time(run.finished_at),
            }
            body = {
                "task": task,
                "environment": {},
                "provider": [{"callId": str(c.id), "provider": p} for c, p, _ in calls],
                "model": [{"callId": str(c.id), "model": m} for c, _, m in calls],
                "trajectorySummary": f"{run.status}; agents={len(agents)}; "
                f"modelCalls={len(calls)}; "
                f"tools={len(tools)}; quality={quality['verdict'] if quality else 'UNKNOWN'}",
                "actions": [
                    {
                        "sequence": e.sequence,
                        "event": e.event_type,
                        "createdAt": _time(e.created_at),
                    }
                    for (e,) in events
                ],
                "toolCalls": [
                    {
                        "callId": str(t.id),
                        "requestId": _id(t.tool_request_id),
                        "sessionId": _id(t.sandbox_session_id),
                        "tool": t.tool_name,
                        "status": t.status,
                        "succeeded": t.succeeded,
                        "exitCode": t.exit_code,
                        "durationMs": t.latency_ms,
                    }
                    for (t,) in tools
                ],
                "commands": [
                    {
                        "requestId": str(c.id),
                        "tool": c.tool_name,
                        "argumentsDigest": digest(c.arguments),
                    }
                    for (c,) in commands
                ],
                "files": files,
                "attempts": [
                    {
                        "agentRunId": str(a.id),
                        "stageIndex": a.stage_index,
                        "status": a.status,
                        "startedAt": _time(a.started_at),
                        "finishedAt": _time(a.finished_at),
                    }
                    for (a,) in agents
                ],
                "failures": (
                    [{"sourceId": str(run.id), "outcome": run.status}]
                    if run.status != "SUCCEEDED"
                    else []
                )
                + [
                    {"sourceId": str(a.id), "outcome": a.status}
                    for (a,) in agents
                    if a.status in ("FAILED", "CANCELLED")
                ],
                "corrections": [],
                "tests": tests,
                "quality": quality,
                "finalResult": {
                    "taskStatus": run.status,
                    "qualityVerdict": quality["verdict"] if quality else None,
                },
                "trainingEligibility": {},
            }
            normalized_task = ExperienceTask.model_validate_json(canonical(task)).model_dump(
                mode="json"
            )
            body["provenance"] = [
                {
                    "sourceType": "task-run",
                    "sourceId": str(run.id),
                    "digest": digest(normalized_task),
                    "storageAllowed": True,
                },
                *provenance,
            ]
        return validate_document(body, self.policy, self.credentials)

    async def verify(self, document: ExperienceDocument) -> None:
        request = CaptureExperience(
            taskRunId=document.task.runId,
            qualityRunId=document.quality.runId if document.quality else None,
            storageConsent=True,
            idempotencyKey=document.task.runId,
        )
        observed = await self.observe(document.task.projectId, request, document.task.finishedAt)
        fields = (
            "task",
            "files",
            "quality",
            "tests",
            "actions",
            "toolCalls",
            "commands",
            "attempts",
            "failures",
            "finalResult",
        )
        if any(getattr(observed, key) != getattr(document, key) for key in fields):
            raise ExperienceError("SOURCE_FACTS_CHANGED")
        # Catalog labels are observations at capture time, not mutable configuration authority.
        if tuple(x.callId for x in observed.provider) != tuple(x.callId for x in document.provider):
            raise ExperienceError("SOURCE_FACTS_CHANGED")

    async def candidates(self, run_id: str) -> dict:
        async with self.sessions() as session:
            source = (
                await session.execute(
                    select(TaskRun, Task.project_id)
                    .options(
                        load_only(TaskRun.id, TaskRun.status, TaskRun.finished_at, raiseload=True)
                    )
                    .join(Task)
                    .where(TaskRun.id == uuid.UUID(run_id))
                )
            ).first()
        if source is None:
            raise ExperienceError("SOURCE_NOT_FOUND")
        run, project = source
        return {
            "projectId": str(project),
            "taskRunId": str(run.id),
            "state": run.status,
            "finishedAt": _time(run.finished_at),
            "storageConsentRequired": True,
            "reuseAllowed": False,
        }
