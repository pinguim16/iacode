"""What the sandbox suite shares: the repository root, a service, requests, and a test double.

``FakeBackend`` is a double of the container engine for the cases that are about the service's
decisions — dedupe, denial, reconciliation, sweeping — and not about isolation. Every isolation,
limit and tool case runs against the real engine through :class:`DockerBackend`, from inside the
sandbox service's image; nothing about a container's hardening is asserted against a double.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from iacode_contracts.sandbox import SANDBOX_CONTRACT_VERSION
from iacode_sandbox.artifacts import MemoryArtifactSink
from iacode_sandbox.backend import DockerBackend, HelperOutcome
from iacode_sandbox.policy import load_policy_registry
from iacode_sandbox.service import SandboxService
from iacode_sandbox.store import MemorySandboxStore
from iacode_sandbox.telemetry import SandboxMetrics
from prometheus_client import CollectorRegistry


def repository_root() -> Path:
    """``/app`` inside the image, the repository root in a checkout."""
    configured = os.environ.get("IACODE_REPOSITORY_ROOT")
    if configured and (Path(configured) / ".iacode" / "policies").is_dir():
        return Path(configured)
    return Path(__file__).resolve().parents[3]


def policies():
    return load_policy_registry(repository_root())


def request(tool: str, arguments: dict[str, Any] | None = None, *, run_id: str,
            policy: str = "developer", tool_request_id: str | None = None,
            workspace: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "contractVersion": SANDBOX_CONTRACT_VERSION,
        "toolRequestId": tool_request_id or str(uuid.uuid4()),
        "runId": run_id,
        "agentRunId": str(uuid.uuid4()),
        "agent": "developer" if policy == "developer" else "code-reviewer",
        "tool": tool,
        "arguments": arguments if arguments is not None else {},
        "policy": policy,
        "workspace": workspace or {"kind": "empty"},
    }


@dataclass
class EngineHarness:
    """A real service over the real engine, with an in-memory store and artifact sink."""

    service: SandboxService
    store: MemorySandboxStore
    artifacts: MemoryArtifactSink
    registry: CollectorRegistry
    runs: list[str] = field(default_factory=list)

    def run_id(self) -> str:
        identifier = str(uuid.uuid4())
        self.runs.append(identifier)
        return identifier

    def execute(self, tool: str, arguments: dict[str, Any] | None = None, *, run_id: str,
                policy: str = "developer"):
        return asyncio.run(self.service.execute(request(tool, arguments, run_id=run_id,
                                                        policy=policy)))

    def shell(self, command: str, *, run_id: str, **extra: Any):
        return self.execute("shell.exec", {"command": command, **extra}, run_id=run_id)

    def session(self, run_id: str):
        return asyncio.run(self.store.active_session_for_run(run_id))

    def close(self) -> None:
        for run_id in self.runs:
            asyncio.run(self.service.release_run(run_id))


def engine_harness(now=None, owner: str | None = None) -> EngineHarness:
    """A service with an owner of its own, so its reconciliation never reaches the stack's."""
    store = MemorySandboxStore()
    artifacts = MemoryArtifactSink(store)
    registry = CollectorRegistry()
    service = SandboxService(root=repository_root(), policies=policies(), backend=DockerBackend(),
                             store=store, artifacts=artifacts, metrics=SandboxMetrics(registry),
                             now=now, owner=owner or f"iacode-test-{uuid.uuid4().hex[:12]}")
    return EngineHarness(service=service, store=store, artifacts=artifacts, registry=registry)


class FakeBackend:
    """A double of the engine that records what the service asked of it."""

    def __init__(self, responses: list[dict[str, Any] | None] | None = None,
                 labels: dict[str, str] | None = None) -> None:
        self.responses = list(responses or [])
        self.created: list[Any] = []
        self.removed: list[str] = []
        self.requests: list[dict[str, Any]] = []
        self.labels = labels
        self.containers: list[dict[str, str]] = []
        self.stopped: list[str] = []

    def image_labels(self, reference: str) -> dict[str, str] | None:
        return self.labels

    def create(self, spec) -> str:
        self.created.append(spec)
        self.containers.append({"name": spec.name, "state": "running",
                                "session": spec.session_id, "run": spec.run_id,
                                "expiresAt": str(spec.expires_at_epoch)})
        return spec.name

    def remove(self, name: str) -> bool:
        self.removed.append(name)
        self.containers = [item for item in self.containers if item["name"] != name]
        return True

    def remove_network(self, name: str) -> None:
        return None

    def create_internal_network(self, name: str, labels: dict[str, str]) -> None:
        return None

    def inspect(self, name: str):
        running = any(item["name"] == name for item in self.containers)
        return {"State": {"Running": running, "Status": "running" if running else "exited"}}

    def managed(self, owner: str) -> list[dict[str, str]]:
        return list(self.containers)

    def stop_everything(self, name: str) -> int:
        self.stopped.append(name)
        return 0

    def exec_helper(self, name: str, payload: dict[str, Any], *, deadline_seconds: float,
                    cancelled=lambda: False, tick=lambda: None) -> HelperOutcome:
        self.requests.append(payload)
        if payload.get("op") == "workspace.init":
            return HelperOutcome(response={"ok": True, "result": {"files": 0}}, exit_code=0,
                                 stderr="")
        response = self.responses.pop(0) if self.responses else {"ok": True, "result": {}}
        return HelperOutcome(response=response, exit_code=0, stderr="")


def fake_service(backend: FakeBackend, *, now=None) -> tuple[SandboxService, MemorySandboxStore]:
    """A service whose image check passes: the double reports the expected fingerprint."""
    store = MemorySandboxStore()
    service = SandboxService(root=repository_root(), policies=policies(), backend=backend,
                             store=store, artifacts=MemoryArtifactSink(store),
                             metrics=SandboxMetrics(CollectorRegistry()), now=now)
    if backend.labels is None:
        policy = service.policies.get("developer")
        _reference, fingerprint = service.expected_image(policy)
        backend.labels = {"org.iacode.sandbox.fingerprint": fingerprint}
    return service, store


def utc(year: int = 2026, month: int = 9, day: int = 22, hour: int = 12) -> datetime:
    return datetime(year, month, day, hour, tzinfo=UTC)
