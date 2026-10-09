"""Versioned contracts shared by the Quality Engine's processes.

The contracts carry immutable facts and references, never a credential, host path, whole command
output, or caller-authored verdict. Unknown fields are refused so an apparent extension cannot be
silently ignored by an older consumer.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

QUALITY_CONTRACT_VERSION = "1.0.0"
QUALITY_CHECK_KINDS = (
    "build",
    "unit",
    "integration",
    "lint",
    "static",
    "dependency-security",
    "secret",
    "coverage",
    "migration",
    "diff-integrity",
)
QUALITY_RUN_STATES = (
    "CREATED",
    "PLANNED",
    "QUEUED",
    "RUNNING",
    "CANCELLING",
    "SUCCEEDED",
    "FAILED",
    "CANCELLED",
    "TIMED_OUT",
    "INVALID",
)
QUALITY_TERMINAL_RUN_STATES = ("SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT", "INVALID")
QUALITY_RESULT_STATUSES = (
    "PASSED",
    "FAILED",
    "DENIED",
    "TIMED_OUT",
    "CANCELLED",
    "ERROR",
    "NOT_APPLICABLE",
)
QUALITY_VERDICTS = ("PASS", "FAIL")
QUALITY_FINDING_SEVERITIES = ("INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL")
QUALITY_EVIDENCE_KINDS = (
    "stdout",
    "stderr",
    "report",
    "coverage",
    "dependency-scan",
    "secret-scan",
    "diff",
    "migration",
    "reproduction",
)
QUALITY_RESULT_ORIGIN = "EVALUATOR"
QUALITY_RUN_EVENT_TYPES = (
    "CREATED",
    "PLANNED",
    "QUEUED",
    "STARTED",
    "CHECK_DISPATCHED",
    "CHECK_RECORDED",
    "CANCELLATION_REQUESTED",
    "SANDBOX_RELEASED",
    "VERDICT_DERIVED",
    "COMPLETED",
    "REPRODUCTION_REQUESTED",
    "INVALIDATED",
)
QUALITY_TASK_QUEUE = "iacode-quality"
QUALITY_RUN_WORKFLOW = "IACodeQualityRun"
QUALITY_CANCEL_SIGNAL = "cancel_quality_run"
QUALITY_REPRODUCE_SIGNAL = "reproduce_quality_run"

SHA256_PATTERN = r"^[0-9a-f]{64}$"
IDENTIFIER_PATTERN = r"^[a-zA-Z0-9][a-zA-Z0-9._:+-]{0,127}$"


class QualityModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    contractVersion: Literal["1.0.0"] = QUALITY_CONTRACT_VERSION


class QualityEvidence(QualityModel):
    evidenceId: str = Field(pattern=IDENTIFIER_PATTERN)
    kind: str
    artifactId: str = Field(min_length=1, max_length=128)
    digest: str = Field(pattern=SHA256_PATTERN)
    sizeBytes: int = Field(ge=0, le=64 * 1024 * 1024)
    mediaType: str = Field(min_length=1, max_length=128)
    producer: str = Field(min_length=1, max_length=128)
    sourceDigests: tuple[str, ...] = ()
    createdAt: datetime
    retentionClass: str = Field(default="quality-evidence", min_length=1, max_length=64)
    storageAllowed: bool = True
    ragAllowed: bool = False
    trainingAllowed: bool = False
    distillationAllowed: bool = False

    @field_validator("kind")
    @classmethod
    def known_kind(cls, value: str) -> str:
        if value not in QUALITY_EVIDENCE_KINDS:
            raise ValueError(f"unknown quality evidence kind: {value}")
        return value

    @field_validator("sourceDigests")
    @classmethod
    def valid_source_digests(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if len(values) != len(set(values)):
            raise ValueError("sourceDigests contains a duplicate")
        if any(
            len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value)
            for value in values
        ):
            raise ValueError("each source digest must be a lowercase SHA-256")
        return values


class QualityFinding(QualityModel):
    findingId: str = Field(pattern=IDENTIFIER_PATTERN)
    checkId: str = Field(pattern=IDENTIFIER_PATTERN)
    severity: str
    category: str = Field(min_length=1, max_length=64)
    fingerprint: str = Field(pattern=SHA256_PATTERN)
    message: str = Field(min_length=1, max_length=2048)
    location: str | None = Field(default=None, max_length=512)
    evidenceIds: tuple[str, ...] = ()
    recurrenceCount: int = Field(default=1, ge=1)

    @field_validator("severity")
    @classmethod
    def known_severity(cls, value: str) -> str:
        if value not in QUALITY_FINDING_SEVERITIES:
            raise ValueError(f"unknown quality finding severity: {value}")
        return value


class QualityCheck(QualityModel):
    checkId: str = Field(pattern=IDENTIFIER_PATTERN)
    kind: str
    runner: str = Field(pattern=IDENTIFIER_PATTERN)
    command: tuple[str, ...] = Field(min_length=1, max_length=64)
    workingDirectory: str = Field(default=".", min_length=1, max_length=512)
    mandatory: bool = True
    applicable: bool = True
    applicabilityReason: str = Field(min_length=1, max_length=1024)
    dependsOn: tuple[str, ...] = ()
    timeoutSeconds: int = Field(ge=1, le=3600)
    requiredEvidenceKinds: tuple[str, ...] = ("report",)

    @field_validator("kind")
    @classmethod
    def known_kind(cls, value: str) -> str:
        if value not in QUALITY_CHECK_KINDS:
            raise ValueError(f"unknown quality check kind: {value}")
        return value

    @field_validator("command")
    @classmethod
    def bounded_command(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not part or len(part) > 1024 or "\x00" in part for part in value):
            raise ValueError("command arguments must be non-empty and bounded")
        return value

    @field_validator("dependsOn", "requiredEvidenceKinds")
    @classmethod
    def unique_tuple(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("a check tuple contains a duplicate")
        return value

    @model_validator(mode="after")
    def applicable_command(self) -> QualityCheck:
        if not self.applicable and self.mandatory:
            raise ValueError("a non-applicable check cannot be marked mandatory")
        return self


class QualityPolicy(QualityModel):
    policyId: str = Field(pattern=IDENTIFIER_PATTERN)
    version: str = Field(min_length=1, max_length=32)
    digest: str = Field(pattern=SHA256_PATTERN)
    profile: str = Field(pattern=IDENTIFIER_PATTERN)
    mandatoryCheckKinds: tuple[str, ...]
    maxRunSeconds: int = Field(ge=1, le=14400)
    maxCheckSeconds: int = Field(ge=1, le=3600)
    maxOutputBytes: int = Field(ge=1024, le=4 * 1024 * 1024)
    coverageThreshold: float | None = Field(default=None, ge=0, le=100)
    trainingAllowed: Literal[False] = False

    @field_validator("mandatoryCheckKinds")
    @classmethod
    def known_unique_kinds(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values or len(values) != len(set(values)):
            raise ValueError("mandatory check kinds must be a non-empty unique set")
        unknown = sorted(set(values) - set(QUALITY_CHECK_KINDS))
        if unknown:
            raise ValueError(f"unknown mandatory check kinds: {', '.join(unknown)}")
        return values


class QualityPlan(QualityModel):
    planId: str = Field(pattern=SHA256_PATTERN)
    snapshotId: str = Field(pattern=IDENTIFIER_PATTERN)
    snapshotDigest: str = Field(pattern=SHA256_PATTERN)
    projectProfile: str = Field(pattern=IDENTIFIER_PATTERN)
    projectProfileDigest: str = Field(pattern=SHA256_PATTERN)
    policy: QualityPolicy
    checks: tuple[QualityCheck, ...] = Field(min_length=1, max_length=128)
    createdAt: datetime

    @model_validator(mode="after")
    def unique_checks_and_acyclic_dependencies(self) -> QualityPlan:
        identities = [check.checkId for check in self.checks]
        if len(identities) != len(set(identities)):
            raise ValueError("a quality plan contains duplicate check identifiers")
        known = set(identities)
        graph = {check.checkId: set(check.dependsOn) for check in self.checks}
        unknown = sorted({item for values in graph.values() for item in values} - known)
        if unknown:
            raise ValueError(f"unknown check dependencies: {', '.join(unknown)}")
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(identifier: str) -> None:
            if identifier in visiting:
                raise ValueError("quality check dependencies contain a cycle")
            if identifier in visited:
                return
            visiting.add(identifier)
            for dependency in graph[identifier]:
                visit(dependency)
            visiting.remove(identifier)
            visited.add(identifier)

        for identifier in identities:
            visit(identifier)
        return self


class QualityResult(QualityModel):
    resultId: str = Field(pattern=IDENTIFIER_PATTERN)
    runId: str = Field(pattern=IDENTIFIER_PATTERN)
    checkId: str = Field(pattern=IDENTIFIER_PATTERN)
    origin: Literal["EVALUATOR"] = QUALITY_RESULT_ORIGIN
    status: str
    exitCode: int | None = None
    durationMs: int = Field(ge=0)
    timedOut: bool = False
    truncated: bool = False
    summary: str = Field(max_length=2048)
    coveragePercent: float | None = Field(default=None, ge=0, le=100)
    sandboxId: str | None = Field(default=None, max_length=128)
    evidence: tuple[QualityEvidence, ...] = ()
    findings: tuple[QualityFinding, ...] = ()
    finishedAt: datetime

    @field_validator("status")
    @classmethod
    def known_status(cls, value: str) -> str:
        if value not in QUALITY_RESULT_STATUSES:
            raise ValueError(f"unknown quality result status: {value}")
        return value

    @model_validator(mode="after")
    def coherent_outcome(self) -> QualityResult:
        if self.status == "PASSED" and self.exitCode != 0:
            raise ValueError("a passed check requires exit code zero")
        if self.status in ("DENIED", "CANCELLED", "ERROR") and self.exitCode is not None:
            raise ValueError(f"{self.status} work that did not execute cannot invent an exit code")
        if self.status == "TIMED_OUT" and not self.timedOut:
            raise ValueError("a timed-out result must say timedOut=true")
        if self.status != "TIMED_OUT" and self.timedOut:
            raise ValueError("timedOut=true requires TIMED_OUT status")
        evidence_ids = [item.evidenceId for item in self.evidence]
        evidence_digests = [item.digest for item in self.evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("a result cannot contain the same evidence reference twice")
        if len(evidence_digests) != len(set(evidence_digests)):
            raise ValueError("a result cannot contain the same evidence digest twice")
        known_evidence = set(evidence_ids)
        for finding in self.findings:
            if finding.checkId != self.checkId:
                raise ValueError("a finding must belong to the result's check")
            unknown = sorted(set(finding.evidenceIds) - known_evidence)
            if unknown:
                raise ValueError(
                    "a finding references evidence outside its result: " + ", ".join(unknown)
                )
        return self


class QualityVerdict(QualityModel):
    runId: str = Field(pattern=IDENTIFIER_PATTERN)
    planId: str = Field(pattern=SHA256_PATTERN)
    verdict: str
    reasons: tuple[str, ...] = Field(min_length=1)
    resultDigests: tuple[str, ...]
    evidenceDigests: tuple[str, ...]
    derivedAt: datetime
    digest: str = Field(pattern=SHA256_PATTERN)

    @field_validator("verdict")
    @classmethod
    def known_verdict(cls, value: str) -> str:
        if value not in QUALITY_VERDICTS:
            raise ValueError(f"unknown quality verdict: {value}")
        return value


class QualityRun(QualityModel):
    runId: str = Field(pattern=IDENTIFIER_PATTERN)
    ownerRunId: str | None = Field(default=None, max_length=128)
    plan: QualityPlan
    state: str
    createdAt: datetime
    startedAt: datetime | None = None
    finishedAt: datetime | None = None
    verdict: QualityVerdict | None = None
    idempotencyKey: str | None = Field(default=None, min_length=1, max_length=128)
    trainingAllowed: Literal[False] = False

    @field_validator("state")
    @classmethod
    def known_state(cls, value: str) -> str:
        if value not in QUALITY_RUN_STATES:
            raise ValueError(f"unknown quality run state: {value}")
        return value

    @model_validator(mode="after")
    def terminal_shape(self) -> QualityRun:
        terminal = self.state in QUALITY_TERMINAL_RUN_STATES
        if terminal != (self.finishedAt is not None):
            raise ValueError("only a terminal quality run has finishedAt")
        if self.verdict is not None and not terminal:
            raise ValueError("a non-terminal quality run cannot carry a verdict")
        return self


class CreateQualityRunRequest(QualityModel):
    snapshotId: str = Field(pattern=IDENTIFIER_PATTERN)
    snapshotDigest: str = Field(pattern=SHA256_PATTERN)
    policyId: str = Field(pattern=IDENTIFIER_PATTERN)
    idempotencyKey: str = Field(min_length=1, max_length=128)
    ownerRunId: str | None = Field(default=None, max_length=128)
    configuration: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def no_caller_owned_execution_or_verdict(self) -> CreateQualityRunRequest:
        forbidden = {
            "command",
            "commands",
            "runner",
            "image",
            "mount",
            "network",
            "limit",
            "limits",
            "result",
            "results",
            "evidence",
            "verdict",
            "sandboxResult",
        }
        present = sorted(forbidden & set(self.configuration))
        if present:
            raise ValueError(f"configuration cannot set protected fields: {', '.join(present)}")
        return self


__all__ = [name for name in globals() if name.startswith("QUALITY_")] + [
    "CreateQualityRunRequest",
    "QualityCheck",
    "QualityEvidence",
    "QualityFinding",
    "QualityPlan",
    "QualityPolicy",
    "QualityResult",
    "QualityRun",
    "QualityVerdict",
]
