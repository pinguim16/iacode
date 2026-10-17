"""Gate 6 wire facts, not a transcript or a caller-owned verdict.

All payload objects are closed. Unknown observations use null; absence never means PASS.
The HTTP boundary additionally enforces byte limits and unambiguous JSON before validation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

Identity = Annotated[str, Field(pattern=r"^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$")]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Code = Annotated[str, Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._:+-]{0,127}$")]
TaskState = Literal["SUCCEEDED", "FAILED", "CANCELLED"]


class ExperienceModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, strict=True, json_schema_serialization_defaults_required=True
    )

    @field_validator(
        "storageAllowed",
        "ragAllowed",
        "trainingAllowed",
        "distillationAllowed",
        "eligible",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def exact_permission_booleans(cls, value: object) -> object:
        if type(value) is not bool:
            raise ValueError("permission fields require exact booleans")
        return value


class CaptureExperience(ExperienceModel):
    taskRunId: Identity
    qualityRunId: Identity | None = None
    storageConsent: Literal[True]
    idempotencyKey: Identity
    retentionSeconds: int | None = Field(default=None, ge=1, le=7776000)

    @field_validator("storageConsent", mode="before")
    @classmethod
    def consent_is_boolean(cls, value: object) -> object:
        if value is not True:
            raise ValueError("explicit boolean storage consent is required")
        return value


class ExperienceTask(ExperienceModel):
    projectId: Identity
    taskId: Identity
    runId: Identity
    status: TaskState
    attempt: int = Field(ge=1, le=1000000)
    startedAt: AwareDatetime | None
    finishedAt: AwareDatetime

    @model_validator(mode="after")
    def ordered_time(self) -> ExperienceTask:
        if self.startedAt is not None and self.finishedAt < self.startedAt:
            raise ValueError("finish must not precede start")
        return self


class ExperienceEnvironment(ExperienceModel):
    source: Literal["persisted-runtime-facts"] = "persisted-runtime-facts"
    hostDetails: None = None
    limit: Literal["No host configuration, source content or environment values copied."] = (
        "No host configuration, source content or environment values copied."
    )


class ObservedProvider(ExperienceModel):
    callId: Identity
    provider: Code | None


class ObservedModel(ExperienceModel):
    callId: Identity
    model: Annotated[str, Field(min_length=1, max_length=256)] | None


class ExperienceAction(ExperienceModel):
    sequence: int = Field(ge=1)
    event: Code
    createdAt: AwareDatetime


class ExperienceTool(ExperienceModel):
    callId: Identity
    requestId: Identity | None
    sessionId: Identity | None
    tool: Code
    status: Code | None
    succeeded: bool | None
    exitCode: int | None
    durationMs: int | None = Field(ge=0)


class ExperienceCommand(ExperienceModel):
    requestId: Identity
    tool: Code
    argumentsDigest: Digest
    representation: Literal["digest-only; no command or arguments copied"] = (
        "digest-only; no command or arguments copied"
    )


class ExperienceFiles(ExperienceModel):
    snapshotId: Identity | None
    digest: Digest | None
    sizeBytes: int | None = Field(ge=0, le=67108864)
    fileCount: int | None = Field(ge=0, le=10000)

    @model_validator(mode="after")
    def coherent_reference(self) -> ExperienceFiles:
        if (self.snapshotId is None) != (self.digest is None):
            raise ValueError("snapshot identity and digest must be present together")
        return self


class ExperienceAttempt(ExperienceModel):
    agentRunId: Identity
    stageIndex: int = Field(ge=0)
    status: Code
    startedAt: AwareDatetime | None
    finishedAt: AwareDatetime | None


class ExperienceFailure(ExperienceModel):
    sourceId: Identity
    outcome: Code
    detail: None = None


class ExperienceCorrection(ExperienceModel):
    # No current source column proves a correction. The domain currently emits an empty tuple.
    sourceId: Identity
    evidenceDigest: Digest


class ExperienceTestCheck(ExperienceModel):
    checkId: Code
    kind: Code
    runner: Code
    status: Code | None
    resultDigest: Digest | None
    caseCount: None = None


class ExperienceTests(ExperienceModel):
    checks: tuple[ExperienceTestCheck, ...] = Field(max_length=1000)
    caseCount: None = None


class ExperienceQuality(ExperienceModel):
    runId: Identity
    planDigest: Digest
    verdict: Literal["PASS", "FAIL"]
    verdictDigest: Digest
    resultDigests: tuple[Digest, ...] = Field(max_length=1000)
    evidenceDigests: tuple[Digest, ...] = Field(max_length=1000)


class ExperienceResult(ExperienceModel):
    taskStatus: TaskState
    qualityVerdict: Literal["PASS", "FAIL"] | None


class ExperienceProvenance(ExperienceModel):
    sourceType: Literal["task-run", "workspace-snapshot", "quality-evidence"]
    sourceId: Identity
    digest: Digest
    ownership: Literal["UNVERIFIED"] = "UNVERIFIED"
    license: Literal["UNKNOWN"] = "UNKNOWN"
    storageAllowed: Literal[True]
    ragAllowed: Literal[False] = False
    trainingAllowed: Literal[False] = False
    distillationAllowed: Literal[False] = False
    notes: Literal["Observable facts/references only; unknown rights deny reuse."] = (
        "Observable facts/references only; unknown rights deny reuse."
    )
    evidence: Literal[
        "Explicit storage consent; operational observation is not a reuse license."
    ] = "Explicit storage consent; operational observation is not a reuse license."


class ExperienceEligibility(ExperienceModel):
    eligible: Literal[False] = False
    evidence: Literal["No verified ownership/license or positive reuse grant."] = (
        "No verified ownership/license or positive reuse grant."
    )


class ExperienceDocument(ExperienceModel):
    schemaVersion: Literal["1.0.0"] = "1.0.0"
    task: ExperienceTask
    environment: ExperienceEnvironment
    provider: tuple[ObservedProvider, ...] = Field(max_length=1000)
    model: tuple[ObservedModel, ...] = Field(max_length=1000)
    effort: None = None
    repository: None = None
    baseCommit: None = None
    trajectorySummary: str = Field(min_length=1, max_length=256)
    actions: tuple[ExperienceAction, ...] = Field(max_length=1000)
    toolCalls: tuple[ExperienceTool, ...] = Field(max_length=1000)
    commands: tuple[ExperienceCommand, ...] = Field(max_length=1000)
    files: ExperienceFiles
    attempts: tuple[ExperienceAttempt, ...] = Field(max_length=1000)
    failures: tuple[ExperienceFailure, ...] = Field(max_length=1000)
    corrections: tuple[ExperienceCorrection, ...] = Field(max_length=0)
    tests: ExperienceTests
    quality: ExperienceQuality | None
    humanReview: None = None
    agentReview: None = None
    finalResult: ExperienceResult
    provenance: tuple[ExperienceProvenance, ...] = Field(min_length=1, max_length=1002)
    trainingEligibility: ExperienceEligibility

    @model_validator(mode="after")
    def coherent_facts(self) -> ExperienceDocument:
        if self.finalResult.taskStatus != self.task.status:
            raise ValueError("result must describe the source task")
        verdict = self.quality.verdict if self.quality else None
        if self.finalResult.qualityVerdict != verdict:
            raise ValueError("quality observation must match the actual verdict")
        expected_summary = (
            f"{self.task.status}; agents={len(self.attempts)}; modelCalls={len(self.provider)}; "
            f"tools={len(self.toolCalls)}; quality={verdict or 'UNKNOWN'}"
        )
        if self.trajectorySummary != expected_summary:
            raise ValueError("trajectory summary must be derived from observable facts")
        if tuple(x.callId for x in self.provider) != tuple(x.callId for x in self.model):
            raise ValueError("provider and model observations must describe the same calls")
        for collection, key in (
            (self.actions, "sequence"),
            (self.attempts, "agentRunId"),
            (self.toolCalls, "callId"),
            (self.provider, "callId"),
        ):
            keys = [getattr(item, key) for item in collection]
            if len(keys) != len(set(keys)):
                raise ValueError("duplicate observed fact")
        if self.provenance[0].sourceId != self.task.runId:
            raise ValueError("provenance must start with the original task run")
        if self.provenance[0].sourceType != "task-run":
            raise ValueError("the first provenance entry must identify the task")
        source_ids = [item.sourceId for item in self.provenance]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("duplicate provenance source")
        evidence_digests = {
            item.digest for item in self.provenance[1:] if item.sourceType == "quality-evidence"
        }
        if evidence_digests != (set(self.quality.evidenceDigests) if self.quality else set()):
            raise ValueError("quality evidence and provenance must agree")
        snapshots = [
            item for item in self.provenance[1:] if item.sourceType == "workspace-snapshot"
        ]
        if self.files.snapshotId is None:
            if snapshots:
                raise ValueError("unobserved snapshot cannot appear in provenance")
        elif len(snapshots) != 1 or (snapshots[0].sourceId, snapshots[0].digest) != (
            self.files.snapshotId,
            self.files.digest,
        ):
            raise ValueError("snapshot reference and provenance must agree")
        if any(item.sourceType == "task-run" for item in self.provenance[1:]):
            raise ValueError("only one original task source is permitted")
        return self


class ExperienceSummary(ExperienceModel):
    experienceId: Identity
    projectId: Identity
    sourceRunId: Identity
    contentDigest: Digest
    createdAt: datetime
    expiresAt: datetime
    state: Literal["ACTIVE", "EXPIRED", "DELETED"]
