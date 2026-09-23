"""The versioned contracts of the sandbox.

Every object that crosses a process boundary is a frozen dataclass with an explicit ``to_dict`` /
``from_dict`` pair, for the reason the agent runtime gives: these cross a Temporal boundary, and
serialisation is part of the contract rather than an accident of whichever library a worker image
happens to carry.

``from_dict`` is strict. A key the contract does not declare is refused, never ignored: a tool
request is written by a model, and a model that learned to add ``"network": "full"`` or
``"privileged": true`` to a request must meet a refusal rather than a parser that drops the key and
carries on. A refusal is not the end of the world; silently discarding what the caller asked for is.

**No exit code is ever invented.** :class:`CommandExecution` carries ``exit_code = None`` whenever
no process was started — a refused command, a missing working directory, a cancelled request — and
the contract refuses an exit code on a result that says nothing was started.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar

from iacode_contracts.sandbox import (
    SANDBOX_CONTRACT_VERSION,
    SANDBOX_SESSION_STATES,
    TOOL_EXECUTION_STATUSES,
)

__all__ = [
    "CONTRACT_VERSION",
    "ArtifactReference",
    "CommandExecution",
    "ContractError",
    "FileOperation",
    "GitOperation",
    "SandboxSession",
    "ToolExecutionRequest",
    "ToolExecutionResult",
    "Workspace",
    "WorkspaceSource",
]

CONTRACT_VERSION = SANDBOX_CONTRACT_VERSION


class ContractError(ValueError):
    """A payload that does not satisfy a sandbox contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _strict(payload: Any, allowed: set[str], required: set[str], what: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ContractError("CONTRACT_INVALID", f"{what} must be an object")
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ContractError("CONTRACT_UNKNOWN_FIELD",
                            f"{what} carries fields the contract does not declare: "
                            + ", ".join(unknown))
    missing = sorted(key for key in required if payload.get(key) in (None, ""))
    if missing:
        raise ContractError("CONTRACT_MISSING_FIELD",
                            f"{what} is missing required fields: " + ", ".join(missing))
    return payload


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


@dataclass(frozen=True)
class WorkspaceSource:
    """Where a workspace's initial content comes from: nothing, or an authorised snapshot."""

    kind: str = "empty"
    artifact_id: str | None = None
    checksum: str | None = None

    KINDS: ClassVar[tuple[str, ...]] = ("empty", "snapshot")

    def __post_init__(self) -> None:
        if self.kind not in self.KINDS:
            raise ContractError("WORKSPACE_SOURCE_INVALID",
                                f"{self.kind!r} is not a workspace source kind")
        if self.kind == "snapshot" and not self.artifact_id:
            raise ContractError("WORKSPACE_SOURCE_INVALID",
                                "a snapshot workspace names the artifact it is provisioned from")
        if self.kind == "empty" and (self.artifact_id or self.checksum):
            raise ContractError("WORKSPACE_SOURCE_INVALID",
                                "an empty workspace names no artifact")

    def to_dict(self) -> dict[str, Any]:
        body: dict[str, Any] = {"kind": self.kind}
        if self.artifact_id:
            body["artifactId"] = self.artifact_id
        if self.checksum:
            body["checksum"] = self.checksum
        return body

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> WorkspaceSource:
        if not payload:
            return cls()
        _strict(payload, {"kind", "artifactId", "checksum"}, {"kind"}, "the workspace source")
        return cls(kind=str(payload["kind"]), artifact_id=payload.get("artifactId"),
                   checksum=payload.get("checksum"))


@dataclass(frozen=True)
class Workspace:
    """The one directory a session may touch, inside its own container."""

    workspace_id: str
    source: WorkspaceSource
    root: str = "/workspace"
    size_limit_mb: int = 256

    def to_dict(self) -> dict[str, Any]:
        return {"workspaceId": self.workspace_id, "source": self.source.to_dict(),
                "root": self.root, "sizeLimitMb": self.size_limit_mb}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Workspace:
        _strict(payload, {"workspaceId", "source", "root", "sizeLimitMb"},
                {"workspaceId", "source"}, "the workspace")
        return cls(workspace_id=str(payload["workspaceId"]),
                   source=WorkspaceSource.from_dict(payload.get("source")),
                   root=str(payload.get("root") or "/workspace"),
                   size_limit_mb=int(payload.get("sizeLimitMb") or 256))


@dataclass(frozen=True)
class SandboxSession:
    """One disposable execution environment, owned by exactly one run."""

    session_id: str
    run_id: str
    policy: str
    state: str
    workspace: Workspace
    container_name: str
    image: str
    network_profile: str
    created_at: datetime | None = None
    expires_at: datetime | None = None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if self.state not in SANDBOX_SESSION_STATES:
            raise ContractError("SESSION_STATE_INVALID",
                                f"{self.state!r} is not a sandbox session state")

    def to_dict(self) -> dict[str, Any]:
        return {
            "sessionId": self.session_id, "runId": self.run_id, "policy": self.policy,
            "state": self.state, "workspace": self.workspace.to_dict(),
            "containerName": self.container_name, "image": self.image,
            "networkProfile": self.network_profile, "createdAt": _iso(self.created_at),
            "expiresAt": _iso(self.expires_at), "failureReason": self.failure_reason,
        }


@dataclass(frozen=True)
class ToolExecutionRequest:
    """What the agent runtime asks the sandbox to do. The policy is named, never described.

    ``policy`` is the name of a canonical sandbox policy, frozen into the run's plan from the
    agent's profile when the run was created. The request cannot carry a limit, a mount, an image or
    a network profile: those come from the policy the sandbox reads, and a request that tries to
    supply one is refused by :func:`_strict` before anything else looks at it.
    """

    tool_request_id: str
    run_id: str
    tool: str
    arguments: dict[str, Any]
    policy: str
    agent_run_id: str | None = None
    agent: str | None = None
    workspace_source: WorkspaceSource = field(default_factory=WorkspaceSource)
    contract_version: str = CONTRACT_VERSION

    FIELDS: ClassVar[frozenset[str]] = frozenset({
        "contractVersion", "toolRequestId", "runId", "agentRunId", "agent", "tool", "arguments",
        "policy", "workspace"})

    def to_dict(self) -> dict[str, Any]:
        return {
            "contractVersion": self.contract_version, "toolRequestId": self.tool_request_id,
            "runId": self.run_id, "agentRunId": self.agent_run_id, "agent": self.agent,
            "tool": self.tool, "arguments": dict(self.arguments), "policy": self.policy,
            "workspace": self.workspace_source.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ToolExecutionRequest:
        _strict(payload, cls.FIELDS,
                {"contractVersion", "toolRequestId", "runId", "tool", "policy"},
                "the tool execution request")
        if payload["contractVersion"] != CONTRACT_VERSION:
            raise ContractError("CONTRACT_VERSION_UNSUPPORTED",
                                f"contract version {payload['contractVersion']!r} is not "
                                f"{CONTRACT_VERSION!r}")
        arguments = payload.get("arguments")
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            raise ContractError("CONTRACT_INVALID", "the tool arguments must be an object")
        return cls(
            tool_request_id=str(payload["toolRequestId"]), run_id=str(payload["runId"]),
            tool=str(payload["tool"]), arguments=dict(arguments), policy=str(payload["policy"]),
            agent_run_id=payload.get("agentRunId"), agent=payload.get("agent"),
            workspace_source=WorkspaceSource.from_dict(payload.get("workspace")),
            contract_version=str(payload["contractVersion"]),
        )


@dataclass(frozen=True)
class ArtifactReference:
    """A stored object holding what did not fit inline: a full log, a full diff."""

    artifact_id: str
    kind: str
    bucket: str
    key: str
    size_bytes: int
    sha256: str
    content_type: str = "text/plain; charset=utf-8"

    def to_dict(self) -> dict[str, Any]:
        return {"artifactId": self.artifact_id, "kind": self.kind, "bucket": self.bucket,
                "key": self.key, "sizeBytes": self.size_bytes, "sha256": self.sha256,
                "contentType": self.content_type}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ArtifactReference:
        _strict(payload, {"artifactId", "kind", "bucket", "key", "sizeBytes", "sha256",
                          "contentType"},
                {"artifactId", "kind", "bucket", "key", "sha256"}, "the artifact reference")
        return cls(artifact_id=str(payload["artifactId"]), kind=str(payload["kind"]),
                   bucket=str(payload["bucket"]), key=str(payload["key"]),
                   size_bytes=int(payload.get("sizeBytes") or 0), sha256=str(payload["sha256"]),
                   content_type=str(payload.get("contentType") or "text/plain; charset=utf-8"))


@dataclass(frozen=True)
class CommandExecution:
    """What happened to one command. ``exit_code`` is ``None`` unless a process was started."""

    started: bool
    exit_code: int | None
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool = False
    truncated: bool = False
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    orphans_killed: int = 0

    def __post_init__(self) -> None:
        if not self.started and self.exit_code is not None:
            raise ContractError("EXIT_CODE_FABRICATED",
                                "a command that was never started has no exit code")

    def to_dict(self) -> dict[str, Any]:
        return {"started": self.started, "exitCode": self.exit_code, "stdout": self.stdout,
                "stderr": self.stderr, "durationMs": self.duration_ms,
                "timedOut": self.timed_out, "truncated": self.truncated,
                "stdoutBytes": self.stdout_bytes, "stderrBytes": self.stderr_bytes,
                "orphansKilled": self.orphans_killed}


@dataclass(frozen=True)
class FileOperation:
    """One filesystem operation, already resolved against the workspace."""

    operation: str
    path: str
    size_bytes: int = 0

    OPERATIONS: ClassVar[tuple[str, ...]] = ("list", "read", "write", "patch", "search")

    def __post_init__(self) -> None:
        if self.operation not in self.OPERATIONS:
            raise ContractError("FILE_OPERATION_INVALID",
                                f"{self.operation!r} is not a filesystem operation")


@dataclass(frozen=True)
class GitOperation:
    """One Git operation. The verb is from a closed set; nothing reaches ``git`` as free text."""

    verb: str
    arguments: tuple[str, ...] = ()

    VERBS: ClassVar[tuple[str, ...]] = ("status", "diff", "log", "show", "add", "commit")

    def __post_init__(self) -> None:
        if self.verb not in self.VERBS:
            raise ContractError("GIT_OPERATION_INVALID",
                                f"{self.verb!r} is not a Git operation this sandbox offers")


@dataclass(frozen=True)
class ToolExecutionResult:
    """What one execution produced, in the shape the agent runtime turns into a tool result."""

    tool_request_id: str
    tool: str
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    error_code: str | None = None
    exit_code: int | None = None
    duration_ms: int = 0
    timed_out: bool = False
    truncated: bool = False
    session_id: str | None = None
    artifacts: tuple[ArtifactReference, ...] = ()
    replayed: bool = False

    def __post_init__(self) -> None:
        if self.status not in TOOL_EXECUTION_STATUSES:
            raise ContractError("RESULT_STATUS_INVALID",
                                f"{self.status!r} is not a tool execution status")

    def to_dict(self) -> dict[str, Any]:
        return {
            "toolRequestId": self.tool_request_id, "tool": self.tool, "status": self.status,
            "output": dict(self.output), "error": self.error, "errorCode": self.error_code,
            "exitCode": self.exit_code, "durationMs": self.duration_ms,
            "timedOut": self.timed_out, "truncated": self.truncated,
            "sessionId": self.session_id,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "replayed": self.replayed,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ToolExecutionResult:
        _strict(payload, {"toolRequestId", "tool", "status", "output", "error", "errorCode",
                          "exitCode", "durationMs", "timedOut", "truncated", "sessionId",
                          "artifacts", "replayed"},
                {"toolRequestId", "tool", "status"}, "the tool execution result")
        return cls(
            tool_request_id=str(payload["toolRequestId"]), tool=str(payload["tool"]),
            status=str(payload["status"]), output=dict(payload.get("output") or {}),
            error=payload.get("error"), error_code=payload.get("errorCode"),
            exit_code=payload.get("exitCode"), duration_ms=int(payload.get("durationMs") or 0),
            timed_out=bool(payload.get("timedOut")), truncated=bool(payload.get("truncated")),
            session_id=payload.get("sessionId"),
            artifacts=tuple(ArtifactReference.from_dict(item)
                            for item in payload.get("artifacts") or ()),
            replayed=bool(payload.get("replayed")),
        )

    def agent_result(self) -> dict[str, Any]:
        """The tool result the agent runtime persists and hands back to the agent, as data.

        ``CANCELLED`` and ``INTERRUPTED`` never reach an agent — a cancelled run asks nothing
        further, and an interrupted execution is reported as a failure whose outcome is unknown.
        """
        status = self.status
        if status in ("CANCELLED", "INTERRUPTED"):
            status = "FAILED"
        output = dict(self.output)
        output.setdefault("exitCode", self.exit_code)
        output.setdefault("timedOut", self.timed_out)
        output.setdefault("truncated", self.truncated)
        output.setdefault("durationMs", self.duration_ms)
        if self.artifacts:
            output["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        metadata = {"executor": "sandbox", "tool": self.tool}
        if self.session_id:
            metadata["sandboxSession"] = self.session_id
        if self.error_code:
            metadata["errorCode"] = self.error_code
        return {"toolRequestId": self.tool_request_id, "status": status, "output": output,
                "error": self.error, "metadata": metadata}
