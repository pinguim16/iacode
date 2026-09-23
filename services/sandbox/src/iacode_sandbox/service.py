"""The Sandbox Service: create a session, execute a tool, inspect, terminate, recover.

One question decides every step here: *what may this request cause?* The answer is read from the
canonical policy the run's plan named, and from nothing the request says. The order is fixed:

1. the policy exists, the tool is registered, the policy allows it, the workspace access allows it,
   and every argument is declared and well typed — otherwise ``DENIED``, and nothing starts;
2. the execution has not already happened — otherwise the recorded outcome is returned, and the tool
   is not run a second time for a retried activity;
3. the run's session exists, or is created from the policy and provisioned from the run's workspace
   source — one container, one workspace, one run;
4. the tool runs through the helper inside that container, bounded by the command's own timeout
   inside and by a deadline outside, and stoppable by cancellation;
5. what did not fit inline goes to the artifact store, the execution is recorded once, and the
   result is returned as data.

Sessions are serialised per run: one tool at a time in one workspace, so a command and a patch never
race. The service's memory is a cache; the store and the engine's labels are the truth, and
:meth:`SandboxService.reconcile` rebuilds from them after a restart. :meth:`SandboxService.sweep`
removes what has outlived its expiry, a bounded number at a time, and never a session that is
running a tool.
"""

from __future__ import annotations

import asyncio
import base64
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from iacode_common.identifiers import uuid7
from iacode_telemetry.logging import get_logger

from iacode_sandbox.artifacts import ArtifactSink
from iacode_sandbox.backend import BackendError, ContainerSpec, DockerBackend
from iacode_sandbox.contracts import (
    ArtifactReference,
    ContractError,
    ToolExecutionRequest,
    ToolExecutionResult,
)
from iacode_sandbox.image import FINGERPRINT_LABEL, image_reference, input_fingerprint
from iacode_sandbox.policy import PolicyRegistry, SandboxPolicy
from iacode_sandbox.snapshots import SnapshotError
from iacode_sandbox.store import ExecutionRecord, SandboxStore, SessionRecord, StoreConflictError
from iacode_sandbox.telemetry import SandboxMetrics, sandbox_log_fields
from iacode_sandbox.tools import ToolRejectedError, build_helper_request

__all__ = ["ImageUnavailableError", "SandboxService", "SessionUnavailableError"]

logger = get_logger(__name__)

#: Seconds the controller waits beyond a command's own timeout before it stops everything itself.
DEADLINE_GRACE_SECONDS = 30

#: How often a long execution reports that it is alive, so a cancellation reaches it promptly.
HEARTBEAT_SECONDS = 5.0

#: Helper refusal codes that mean "outside the policy" rather than "did not work".
DENIAL_CODES = frozenset({
    "PATH_EMPTY", "PATH_TOO_LONG", "PATH_NULL_BYTE", "PATH_CONTROL_CHARACTER", "PATH_BACKSLASH",
    "PATH_DRIVE", "PATH_UNC", "PATH_ABSOLUTE_OUTSIDE", "PATH_ESCAPE", "PATH_SYMLINK_ESCAPE",
    "PATH_IS_WORKSPACE",
})


class SessionUnavailableError(RuntimeError):
    """A session could not be created or has been lost."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class ImageUnavailableError(SessionUnavailableError):
    """The content-addressed image for a profile does not exist or carries the wrong fingerprint."""


@dataclass
class _Clock:
    now: Callable[[], datetime] = lambda: datetime.now(UTC)


class SandboxService:
    """Everything a sandbox does, behind five operations."""

    def __init__(self, *, root: Path, policies: PolicyRegistry, backend: DockerBackend,
                 store: SandboxStore, artifacts: ArtifactSink,
                 metrics: SandboxMetrics | None = None, snapshot_reader: Any = None,
                 now: Callable[[], datetime] | None = None, owner: str = "iacode") -> None:
        self.root = root
        self.owner = owner
        self.policies = policies
        self.backend = backend
        self.store = store
        self.artifacts = artifacts
        self.metrics = metrics
        self.snapshot_reader = snapshot_reader
        self.clock = _Clock(now or (lambda: datetime.now(UTC)))
        self._locks: dict[str, asyncio.Lock] = {}

    # -- images ---------------------------------------------------------------------------------

    def expected_image(self, policy: SandboxPolicy) -> tuple[str, str]:
        """The reference and fingerprint the policy's image must have, from the inputs here."""
        fingerprint = input_fingerprint(self.root, policy.image.context)
        return image_reference(policy.image.repository, fingerprint), fingerprint

    def verify_image(self, policy: SandboxPolicy) -> tuple[str, str]:
        reference, fingerprint = self.expected_image(policy)
        labels = self.backend.image_labels(reference)
        if labels is None:
            raise ImageUnavailableError(
                "SANDBOX_IMAGE_MISSING",
                f"the {policy.image.name} image {reference} has not been built from the current "
                "inputs; build it with scripts/iacode/sandbox_image.py")
        if labels.get(FINGERPRINT_LABEL) != fingerprint:
            raise ImageUnavailableError(
                                        "SANDBOX_IMAGE_STALE",
                f"the image tagged {reference} does not carry the fingerprint of the current "
                "inputs")
        return reference, fingerprint

    # -- sessions -------------------------------------------------------------------------------

    def _lock(self, run_id: str) -> asyncio.Lock:
        return self._locks.setdefault(run_id, asyncio.Lock())

    async def _ensure_session(self, request: ToolExecutionRequest,
                              policy: SandboxPolicy) -> SessionRecord:
        # One run, one workspace. A later stage under another policy — a reviewer after a developer
        # — works in the same container: the workspace belongs to the run, and what each policy may
        # do in it was decided per request, before this point.
        existing = await self.store.active_session_for_run(request.run_id)
        if existing is not None:
            return existing
        return await self.create_session(request.run_id, policy, request.workspace_source)

    async def create_session(self, run_id: str, policy: SandboxPolicy,
                             source: Any) -> SessionRecord:
        """A container for ``run_id``, provisioned from its workspace source, or an error."""
        reference, fingerprint = await asyncio.to_thread(self.verify_image, policy)
        session_id = str(uuid7())
        now = self.clock.now()
        expires = now + timedelta(seconds=policy.resources.session_ttl_seconds)
        name = f"iacode-sbx-{session_id.replace('-', '')}"
        resources = policy.resources
        record = SessionRecord(
            session_id=session_id, run_id=run_id, state="CREATED", policy=policy.name,
            image=reference, image_fingerprint=fingerprint, container_name=name,
            network_profile=policy.network_profile, workspace_source=source.to_dict(),
            resource_limits={"cpus": resources.cpus, "memoryMb": resources.memory_mb,
                             "pids": resources.pids, "workspaceMb": resources.workspace_mb,
                             "tmpMb": resources.tmp_mb},
            expires_at=expires)
        try:
            record = await self.store.create_session(record)
        except StoreConflictError:
            existing = await self.store.active_session_for_run(run_id)
            if existing is None:
                raise
            return existing
        record = await self.store.update_session(session_id, state="STARTING", started_at=now)
        network = "none"
        try:
            if policy.network_profile == "local-services":
                network = f"iacode-sbx-net-{session_id.replace('-', '')}"
                await asyncio.to_thread(self.backend.create_internal_network, network,
                                        {"org.iacode.sandbox": "1",
                                         "org.iacode.sandbox.owner": self.owner,
                                         "org.iacode.sandbox.session": session_id})
            spec = ContainerSpec(
                name=name, image=reference, session_id=session_id, run_id=run_id,
                policy=policy.name, expires_at_epoch=int(expires.timestamp()),
                cpus=resources.cpus, memory_mb=resources.memory_mb, pids=resources.pids,
                workspace_mb=resources.workspace_mb, tmp_mb=resources.tmp_mb,
                owner=self.owner, network=network)
            await asyncio.to_thread(self.backend.create, spec)
            await self._provision(record, policy, source)
        except (BackendError, SessionUnavailableError, SnapshotError) as error:
            await asyncio.to_thread(self.backend.remove, name)
            if network != "none":
                await asyncio.to_thread(self.backend.remove_network, network)
            await self.store.update_session(session_id, state="FAILED",
                                            failure_reason=str(error)[:500],
                                            stopped_at=self.clock.now())
            if self.metrics:
                self.metrics.session_created(policy.name, "failed")
            raise SessionUnavailableError(getattr(error, "code", "SESSION_CREATE_FAILED"),
                                          str(error)) from None
        record = await self.store.update_session(session_id, state="READY")
        if self.metrics:
            self.metrics.session_created(policy.name, "ready")
            self.metrics.set_active_sessions(len(await self.store.sessions(active_only=True)))
        logger.info("sandbox session ready",
                    extra=sandbox_log_fields(run_id=run_id, sandbox_id=session_id,
                                             status="READY"))
        return record

    async def _provision(self, record: SessionRecord, policy: SandboxPolicy, source: Any) -> None:
        payload: dict[str, Any] = {"op": "workspace.init",
                                   "maxBytes": policy.resources.workspace_mb * 1024 * 1024 // 2}
        if source.kind == "snapshot":
            if self.snapshot_reader is None:
                raise SessionUnavailableError("SNAPSHOT_UNAVAILABLE",
                                              "this service has no snapshot reader")
            data = await self.snapshot_reader.read(source.artifact_id, source.checksum)
            payload["snapshot"] = base64.b64encode(data).decode("ascii")
        outcome = await asyncio.to_thread(self.backend.exec_helper, record.container_name, payload,
                                          deadline_seconds=300)
        response = outcome.response or {}
        if not response.get("ok"):
            raise SessionUnavailableError(str(response.get("errorCode") or "WORKSPACE_INIT_FAILED"),
                                          str(response.get("error") or outcome.stderr or
                                          "the workspace could not be provisioned")[:500])

    async def terminate(self, session_id: str, *, state: str = "STOPPED",
                        reason: str | None = None) -> SessionRecord | None:
        """Remove a session's container and record the terminal state."""
        record = await self.store.session(session_id)
        if record is None:
            return None
        if record.state in ("STOPPED", "FAILED", "EXPIRED"):
            return record
        await self.store.update_session(session_id, state="STOPPING")
        await asyncio.to_thread(self.backend.remove, record.container_name)
        if record.network_profile == "local-services":
            await asyncio.to_thread(self.backend.remove_network,
                                    f"iacode-sbx-net-{session_id.replace('-', '')}")
        record = await self.store.update_session(
            session_id, state=state, stopped_at=self.clock.now(), active_tool_request_id=None,
            failure_reason=reason)
        if self.metrics:
            self.metrics.set_active_sessions(len(await self.store.sessions(active_only=True)))
        logger.info("sandbox session ended",
                    extra=sandbox_log_fields(run_id=record.run_id, sandbox_id=session_id,
                                             status=state, reason=reason))
        return record

    async def release_run(self, run_id: str) -> int:
        """End every session of a run. Called by the workflow when the run reaches its end."""
        released = 0
        async with self._lock(run_id):
            for record in await self.store.sessions(active_only=True):
                if record.run_id == run_id:
                    await self.terminate(record.session_id, reason="the run ended")
                    released += 1
        return released

    async def inspect(self, session_id: str) -> dict[str, Any] | None:
        """What the store and the engine each say about a session."""
        record = await self.store.session(session_id)
        if record is None:
            return None
        container = await asyncio.to_thread(self.backend.inspect, record.container_name)
        return {
            "sessionId": record.session_id, "runId": record.run_id, "state": record.state,
            "policy": record.policy, "image": record.image, "containerName": record.container_name,
            "containerState": (container or {}).get("State", {}).get("Status") if container
            else None,
            "expiresAt": record.expires_at.isoformat(), "failureReason": record.failure_reason,
        }

    # -- recovery -------------------------------------------------------------------------------

    async def reconcile(self) -> dict[str, list[str]]:
        """Make the store and the engine agree after a restart, without trusting memory.

        - an active session whose container is gone is ``FAILED`` — its workspace went with it;
        - an active session caught ``RUNNING`` is returned to ``READY``: the process that drove the
          tool died with the old service, and the execution record says what is known about it;
        - a container carrying this service's label and no active session is removed.
        """
        report: dict[str, list[str]] = {"lost": [], "recovered": [], "removed": []}
        containers = await asyncio.to_thread(self.backend.managed, self.owner)
        by_session = {item["session"]: item for item in containers}
        active = await self.store.sessions(active_only=True)
        active_ids = {record.session_id for record in active}
        for record in active:
            container = by_session.get(record.session_id)
            if container is None or container["state"] not in ("running", "created"):
                await self.store.update_session(
                    record.session_id, state="FAILED", stopped_at=self.clock.now(),
                    active_tool_request_id=None,
                    failure_reason="the container was not running when the service restarted")
                if container is not None:
                    await asyncio.to_thread(self.backend.remove, record.container_name)
                report["lost"].append(record.session_id)
            elif record.state in ("RUNNING", "STARTING", "STOPPING"):
                if record.state == "STOPPING":
                    await self.terminate(record.session_id, reason="stopping when restarted")
                    report["removed"].append(record.session_id)
                    continue
                await asyncio.to_thread(self.backend.stop_everything, record.container_name)
                await self.store.update_session(record.session_id, state="READY",
                                                active_tool_request_id=None)
                report["recovered"].append(record.session_id)
        for container in containers:
            if container["session"] not in active_ids:
                await asyncio.to_thread(self.backend.remove, container["name"])
                report["removed"].append(container["session"] or container["name"])
        if self.metrics:
            self.metrics.set_active_sessions(len(await self.store.sessions(active_only=True)))
        return report

    async def sweep(self, *, limit: int = 10) -> list[str]:
        """Expire sessions past their expiry, oldest first, at most ``limit`` of them.

        A session that is running a tool is never swept: its expiry waits for the tool to end, and
        the run's own release ends it normally.
        """
        now = self.clock.now()
        candidates = sorted(
            (record for record in await self.store.sessions(active_only=True)
             if record.expires_at <= now and record.state != "RUNNING"),
            key=lambda item: item.expires_at)
        expired: list[str] = []
        for record in candidates[:max(limit, 0)]:
            lock = self._lock(record.run_id)
            if lock.locked():
                continue
            async with lock:
                await self.terminate(record.session_id, state="EXPIRED",
                                     reason="the session outlived its expiry")
            expired.append(record.session_id)
        return expired

    # -- execution ------------------------------------------------------------------------------

    def _denied(self, request_tool: str, tool_request_id: str, code: str, message: str,
                session_id: str | None = None) -> ToolExecutionResult:
        if self.metrics:
            self.metrics.rejected(code)
        return ToolExecutionResult(tool_request_id=tool_request_id, tool=request_tool,
                                   status="DENIED", error=message, error_code=code,
                                   session_id=session_id)

    async def execute(self, payload: dict[str, Any] | ToolExecutionRequest, *,
                      heartbeat: Callable[[], None] = lambda: None) -> ToolExecutionResult:
        """Execute one tool request; a cancellation is cleaned up and then re-raised."""
        started = time.monotonic()
        try:
            request = (payload if isinstance(payload, ToolExecutionRequest)
                       else ToolExecutionRequest.from_dict(payload))
        except ContractError as error:
            identifier = str((payload or {}).get("toolRequestId") or "") \
                if isinstance(payload, dict) else ""
            tool = str((payload or {}).get("tool") or "") if isinstance(payload, dict) else ""
            return self._denied(tool, identifier, error.code, str(error))

        policy = self.policies.get(request.policy)
        if policy is None:
            return self._denied(request.tool, request.tool_request_id, "POLICY_UNKNOWN",
                                f"{request.policy!r} is not a sandbox policy")
        try:
            helper_request = build_helper_request(request.tool, request.arguments, policy)
        except ToolRejectedError as rejected:
            denied = self._denied(request.tool, request.tool_request_id, rejected.code,
                                  str(rejected))
            return await self._record(request, None, denied, started)

        recorded = await self.store.execution(request.tool_request_id)
        if recorded is not None:
            return ToolExecutionResult(
                tool_request_id=request.tool_request_id, tool=request.tool,
                status=recorded.status if recorded.status != "INTERRUPTED" else "FAILED",
                output={"replayed": True, "summary": recorded.summary,
                        "exitCode": recorded.exit_code},
                error=("this request was already executed; its output was delivered to an "
                       "earlier attempt and is not repeated"),
                error_code="EXECUTION_REPLAYED", exit_code=recorded.exit_code,
                duration_ms=recorded.duration_ms, timed_out=recorded.timed_out,
                truncated=recorded.truncated, session_id=recorded.session_id, replayed=True)

        async with self._lock(request.run_id):
            try:
                session = await self._ensure_session(request, policy)
            except SessionUnavailableError as error:
                result = ToolExecutionResult(
                    tool_request_id=request.tool_request_id, tool=request.tool, status="FAILED",
                    error=str(error)[:500], error_code=error.code)
                return await self._record(request, None, result, started)
            await self.store.update_session(session.session_id, state="RUNNING",
                                            active_tool_request_id=request.tool_request_id)
            timeout = float(helper_request.get("timeoutSeconds") or 60)
            cancel = threading.Event()
            loop = asyncio.get_running_loop()
            future = loop.run_in_executor(
                None, lambda: self.backend.exec_helper(
                    session.container_name, helper_request,
                    deadline_seconds=timeout + DEADLINE_GRACE_SECONDS, cancelled=cancel.is_set))
            cancelled_error: asyncio.CancelledError | None = None
            try:
                while True:
                    done, _pending = await asyncio.wait({future}, timeout=HEARTBEAT_SECONDS)
                    if done:
                        break
                    heartbeat()
            except asyncio.CancelledError as error:
                cancelled_error = error
                cancel.set()
            outcome = await asyncio.shield(future) if cancelled_error else future.result()
            await self.store.update_session(session.session_id, state="READY",
                                            active_tool_request_id=None)
            result = await self._result(request, session, outcome)
            result = await self._record(request, session, result, started)
            if cancelled_error is not None:
                raise cancelled_error
            return result

    async def _result(self, request: ToolExecutionRequest, session: SessionRecord,
                      outcome: Any) -> ToolExecutionResult:
        base = {"tool_request_id": request.tool_request_id, "tool": request.tool,
                "session_id": session.session_id}
        if outcome.cancelled:
            return ToolExecutionResult(**base, status="CANCELLED", error_code="CANCELLED",
                                       error="the run was cancelled while the tool ran; every "
                                             "process it started was stopped")
        if outcome.deadline_exceeded:
            return ToolExecutionResult(**base, status="TIMED_OUT", timed_out=True,
                                       error_code="SANDBOX_DEADLINE_EXCEEDED",
                                       error="the sandbox did not answer within its deadline; "
                                             "every process was stopped")
        response = outcome.response
        if not isinstance(response, dict):
            container = await asyncio.to_thread(self.backend.inspect, session.container_name)
            running = bool(container and container.get("State", {}).get("Running"))
            if not running:
                await self.terminate(session.session_id, state="FAILED",
                                     reason="the container stopped during a tool execution")
            return ToolExecutionResult(**base, status="FAILED", error_code="SANDBOX_HELPER_FAILED",
                                       error=("the sandbox helper returned no answer"
                                              + ("" if running else "; the container stopped")))
        if not response.get("ok"):
            code = str(response.get("errorCode") or "TOOL_FAILED")
            status = "DENIED" if code in DENIAL_CODES else "FAILED"
            return ToolExecutionResult(**base, status=status, error_code=code,
                                       error=str(response.get("error") or "")[:1000])
        body = dict(response.get("result") or {})
        artifacts: list[ArtifactReference] = []
        for stream in ("stdout", "stderr"):
            full = body.pop(f"{stream}Full", None)
            if full:
                artifacts.append(await self.artifacts.put(
                    run_id=request.run_id, tool_request_id=request.tool_request_id,
                    name=f"{stream}.log", content=base64.b64decode(full),
                    kind=f"sandbox.{stream}"))
        if "exitCode" in body or "started" in body:
            started = bool(body.pop("started", True))
            error = body.pop("error", None)
            error_code = body.pop("errorCode", None)
            exit_code = body.get("exitCode") if started else None
            timed_out = bool(body.get("timedOut"))
            status = ("TIMED_OUT" if timed_out else "SUCCEEDED" if exit_code == 0 else "FAILED")
            return ToolExecutionResult(
                **base, status=status, output=body, error=error, error_code=error_code,
                exit_code=exit_code, duration_ms=int(body.get("durationMs") or 0),
                timed_out=timed_out, truncated=bool(body.get("truncated")),
                artifacts=tuple(artifacts))
        return ToolExecutionResult(**base, status="SUCCEEDED", output=body,
                                   truncated=bool(body.get("truncated")),
                                   artifacts=tuple(artifacts))

    async def _record(self, request: ToolExecutionRequest, session: SessionRecord | None,
                      result: ToolExecutionResult, started: float) -> ToolExecutionResult:
        duration = result.duration_ms or int((time.monotonic() - started) * 1000)
        summary = _summary(result)
        if request.agent_run_id:
            await self.store.record_execution(ExecutionRecord(
                tool_request_id=request.tool_request_id, agent_run_id=request.agent_run_id,
                session_id=session.session_id if session else None, tool=request.tool,
                status=result.status, exit_code=result.exit_code, duration_ms=duration,
                timed_out=result.timed_out, truncated=result.truncated,
                error_code=result.error_code, summary=summary,
                artifact_ids=tuple(item.artifact_id for item in result.artifacts)))
        if self.metrics:
            self.metrics.execution(request.tool, result.status, duration / 1000,
                                   result.error_code)
        logger.info("sandbox tool executed",
                    extra=sandbox_log_fields(run_id=request.run_id, agent_id=request.agent,
                                             agent_run_id=request.agent_run_id,
                                             sandbox_id=session.session_id if session else None,
                                             tool=request.tool, status=result.status,
                                             duration_ms=duration, reason=result.error_code))
        if result.duration_ms:
            return result
        return ToolExecutionResult(**{**_fields(result), "duration_ms": duration})


def _fields(result: ToolExecutionResult) -> dict[str, Any]:
    return {"tool_request_id": result.tool_request_id, "tool": result.tool,
            "status": result.status, "output": result.output, "error": result.error,
            "error_code": result.error_code, "exit_code": result.exit_code,
            "duration_ms": result.duration_ms, "timed_out": result.timed_out,
            "truncated": result.truncated, "session_id": result.session_id,
            "artifacts": result.artifacts, "replayed": result.replayed}


def _summary(result: ToolExecutionResult) -> str:
    """A short, verifiable fact about an execution. Never its output."""
    parts = [result.status.lower()]
    if result.exit_code is not None:
        parts.append(f"exit {result.exit_code}")
    if result.timed_out:
        parts.append("timed out")
    if result.truncated:
        parts.append("output truncated")
    if result.error_code:
        parts.append(result.error_code)
    if result.tool.startswith("filesystem.") and "size" in result.output:
        parts.append(f"{result.output['size']} bytes")
    if result.tool == "filesystem.apply_patch" and "files" in result.output:
        parts.append(f"{len(result.output['files'])} file(s)")
    return ", ".join(parts)[:240]

