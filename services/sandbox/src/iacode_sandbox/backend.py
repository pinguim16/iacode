"""The container engine, driven through its command-line client and nothing else.

This is the only module of the sandbox that starts a process, and the only process it starts is the
container client named by :data:`DOCKER`. Every invocation is an argument vector; no string
reaches a shell here. What a tool asks for is carried to the helper inside the container as JSON on
standard input, so an agent's command never appears on this process's command line at all.

**Every hardening flag is derived from the policy, in one function.** :func:`container_arguments`
turns a :class:`ContainerSpec` into the ``docker run`` arguments, and nothing else creates a
container. The flags it always emits are the Gate's isolation claims, and
`ContainerSpecTests` reads them back:

- ``--read-only`` root filesystem; the workspace and ``/tmp`` are size-limited ``tmpfs`` mounts;
- ``--cap-drop ALL`` and ``--security-opt no-new-privileges``; never ``--privileged``;
- ``--user 10001:10001``, the image's unprivileged sandbox user;
- ``--network none`` (or the session's own internal network);
- ``--memory`` equal to ``--memory-swap``, ``--cpus``, ``--pids-limit``;
- the image's own init (the helper in ``--init`` mode) as PID 1, so a zombie is always reaped and
  nothing inside the sandbox can signal it away;
- **no** ``--volume``, **no** bind mount, **no** ``--env-file`` and no variable from this process's
  environment. The host's filesystem, its Docker socket, its SSH agent and its credentials do not
  exist inside a sandbox, because nothing here can put them there.

The labels every container carries (:data:`LABEL_MANAGED`, the owner, and the session, run and
expiry labels) are how the service finds its own containers after a restart, and the only
containers it ever removes. Other projects share this engine, and so may a second IACode stack or a
test suite: a service only ever lists and removes containers carrying **its own** owner label, so it
cannot delete a workspace another owner is using.
"""

from __future__ import annotations

import json
import subprocess
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "DOCKER",
    "HELPER_COMMAND",
    "LABEL_EXPIRES",
    "LABEL_MANAGED",
    "LABEL_OWNER",
    "LABEL_POLICY",
    "LABEL_RUN",
    "LABEL_SESSION",
    "SANDBOX_USER",
    "BackendError",
    "ContainerSpec",
    "DockerBackend",
    "HelperOutcome",
    "container_arguments",
]

#: The one executable this module ever starts.
DOCKER = "docker"

#: The image's unprivileged user. Never root, never the host's user.
SANDBOX_USER = "10001:10001"

#: How the helper is started inside a container. ``-I`` ignores the environment and the user site,
#: so nothing inherited can change what the helper imports.
HELPER_COMMAND = ("python3", "-I", "/opt/iacode/sandbox_helper.py")

LABEL_MANAGED = "org.iacode.sandbox"
LABEL_OWNER = "org.iacode.sandbox.owner"
LABEL_SESSION = "org.iacode.sandbox.session"
LABEL_RUN = "org.iacode.sandbox.run"
LABEL_POLICY = "org.iacode.sandbox.policy"
LABEL_EXPIRES = "org.iacode.sandbox.expires-at"


class BackendError(RuntimeError):
    """The engine could not do what was asked. The code says what; the message says why."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ContainerSpec:
    """Everything a sandbox container is created with. Built from a policy, never from a request."""

    name: str
    image: str
    session_id: str
    run_id: str
    policy: str
    expires_at_epoch: int
    cpus: float
    memory_mb: int
    pids: int
    workspace_mb: int
    tmp_mb: int
    owner: str = "iacode"
    network: str = "none"
    labels: dict[str, str] = field(default_factory=dict)


def container_arguments(spec: ContainerSpec) -> list[str]:
    """The complete ``docker run`` argument vector for a sandbox. The only one there is."""
    labels = {
        LABEL_MANAGED: "1",
        LABEL_OWNER: spec.owner,
        LABEL_SESSION: spec.session_id,
        LABEL_RUN: spec.run_id,
        LABEL_POLICY: spec.policy,
        LABEL_EXPIRES: str(spec.expires_at_epoch),
        **spec.labels,
    }
    arguments = [
        DOCKER, "run", "--detach",
        "--name", spec.name,
        "--read-only",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--user", SANDBOX_USER,
        "--network", spec.network,
        "--cpus", f"{spec.cpus:g}",
        "--memory", f"{spec.memory_mb}m",
        "--memory-swap", f"{spec.memory_mb}m",
        "--pids-limit", str(spec.pids),
        "--ulimit", "core=0",
        "--tmpfs", (f"/workspace:rw,nosuid,nodev,exec,size={spec.workspace_mb}m,"
                    "uid=10001,gid=10001,mode=0700"),
        "--tmpfs", f"/tmp:rw,nosuid,nodev,noexec,size={spec.tmp_mb}m,uid=10001,gid=10001,mode=1777",
        "--workdir", "/workspace",
        "--stop-timeout", "2",
    ]
    for key, value in sorted(labels.items()):
        arguments += ["--label", f"{key}={value}"]
    arguments.append(spec.image)
    return arguments


@dataclass
class HelperOutcome:
    """What one helper invocation produced, and whether it had to be stopped."""

    response: dict[str, Any] | None
    exit_code: int | None
    stderr: str
    cancelled: bool = False
    deadline_exceeded: bool = False


class DockerBackend:
    """A thin, synchronous client of the engine. The service calls it from a worker thread."""

    def __init__(self, executable: str = DOCKER) -> None:
        if executable != DOCKER:
            raise BackendError("BACKEND_INVALID", "the backend only ever starts the Docker client")
        self.executable = executable

    def _run(self, arguments: list[str], *, timeout: float = 120,
             stdin: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
        if not arguments or arguments[0] != DOCKER:
            raise BackendError("BACKEND_INVALID", "only the Docker client is ever started")
        try:
            return subprocess.run(arguments, input=stdin, capture_output=True, timeout=timeout,
                                  check=False)
        except FileNotFoundError:
            raise BackendError("ENGINE_UNAVAILABLE", "the Docker client is not installed") from None
        except subprocess.TimeoutExpired:
            raise BackendError("ENGINE_TIMEOUT",
                               f"docker {arguments[1]} did not answer within {timeout:g}s"
                               ) from None

    @staticmethod
    def _text(payload: bytes) -> str:
        return payload.decode("utf-8", "replace").strip()

    # -- images and networks --------------------------------------------------------------------

    def image_labels(self, reference: str) -> dict[str, str] | None:
        """The labels of a local image, or ``None`` when the engine has no such image."""
        completed = self._run([DOCKER, "image", "inspect", "--format", "{{json .Config.Labels}}",
                               reference], timeout=30)
        if completed.returncode != 0:
            return None
        labels = json.loads(self._text(completed.stdout) or "null")
        return dict(labels or {})

    def create_internal_network(self, name: str, labels: dict[str, str]) -> None:
        arguments = [DOCKER, "network", "create", "--internal", "--driver", "bridge"]
        for key, value in sorted(labels.items()):
            arguments += ["--label", f"{key}={value}"]
        completed = self._run([*arguments, name], timeout=30)
        if completed.returncode != 0:
            raise BackendError("NETWORK_CREATE_FAILED", self._text(completed.stderr)[-300:])

    def remove_network(self, name: str) -> None:
        self._run([DOCKER, "network", "rm", name], timeout=30)

    def network_is_internal(self, name: str) -> bool:
        completed = self._run([DOCKER, "network", "inspect", "--format", "{{.Internal}}", name],
                              timeout=30)
        return completed.returncode == 0 and self._text(completed.stdout) == "true"

    # -- containers -----------------------------------------------------------------------------

    def create(self, spec: ContainerSpec) -> str:
        completed = self._run(container_arguments(spec), timeout=120)
        if completed.returncode != 0:
            raise BackendError("CONTAINER_CREATE_FAILED", self._text(completed.stderr)[-400:])
        return self._text(completed.stdout)

    def remove(self, name: str) -> bool:
        completed = self._run([DOCKER, "rm", "--force", "--volumes", name], timeout=60)
        return completed.returncode == 0

    def inspect(self, name: str) -> dict[str, Any] | None:
        completed = self._run([DOCKER, "inspect", "--type", "container", name], timeout=30)
        if completed.returncode != 0:
            return None
        documents = json.loads(self._text(completed.stdout) or "[]")
        return documents[0] if documents else None

    def managed(self, owner: str) -> list[dict[str, str]]:
        """Every container this owner created, from the engine, with its labels."""
        completed = self._run([DOCKER, "ps", "--all", "--no-trunc", "--filter",
                               f"label={LABEL_MANAGED}=1", "--filter",
                               f"label={LABEL_OWNER}={owner}", "--format", "{{json .}}"],
                              timeout=60)
        if completed.returncode != 0:
            raise BackendError("ENGINE_UNAVAILABLE", self._text(completed.stderr)[-300:])
        containers = []
        for line in self._text(completed.stdout).splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            labels = dict(item.split("=", 1) for item in str(entry.get("Labels") or "").split(",")
                          if "=" in item)
            if labels.get(LABEL_MANAGED) != "1" or labels.get(LABEL_OWNER) != owner:
                continue
            containers.append({"name": str(entry.get("Names") or ""),
                               "state": str(entry.get("State") or ""),
                               "session": labels.get(LABEL_SESSION, ""),
                               "run": labels.get(LABEL_RUN, ""),
                               "expiresAt": labels.get(LABEL_EXPIRES, "")})
        return containers

    # -- the helper -----------------------------------------------------------------------------

    def exec_helper(self, name: str, request: dict[str, Any], *, deadline_seconds: float,
                    cancelled: Callable[[], bool] = lambda: False,
                    tick: Callable[[], None] = lambda: None) -> HelperOutcome:
        """Send one request to the helper in ``name`` and wait for its answer.

        The wait is bounded twice: the helper enforces a command's own timeout inside the
        container, and this call gives up at ``deadline_seconds`` in case the helper itself could
        not answer. Either a cancellation or that deadline stops every process in the container
        through a second, independent helper call, so nothing the request started keeps running.
        """
        payload = json.dumps(request).encode("utf-8")
        arguments = [DOCKER, "exec", "--interactive", "--user", SANDBOX_USER, "--workdir",
                     "/workspace", name, *HELPER_COMMAND]
        process = subprocess.Popen(arguments, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        collected: dict[str, bytes] = {}

        def communicate() -> None:
            stdout, stderr = process.communicate(input=payload)
            collected["stdout"], collected["stderr"] = stdout, stderr

        worker = threading.Thread(target=communicate, daemon=True)
        worker.start()
        started = time.monotonic()
        stopped_for: str | None = None
        while worker.is_alive():
            worker.join(timeout=0.5)
            tick()
            if not worker.is_alive():
                break
            if cancelled():
                stopped_for = "cancelled"
            elif time.monotonic() - started > deadline_seconds:
                stopped_for = "deadline"
            if stopped_for:
                self.stop_everything(name)
                worker.join(timeout=30)
                if worker.is_alive():
                    process.kill()
                    worker.join(timeout=10)
                break
        stdout = collected.get("stdout", b"")
        stderr = self._text(collected.get("stderr", b""))
        response = None
        if stdout.strip():
            try:
                response = json.loads(stdout.decode("utf-8", "replace"))
            except json.JSONDecodeError:
                response = None
        return HelperOutcome(response=response, exit_code=process.returncode, stderr=stderr[-2000:],
                             cancelled=stopped_for == "cancelled",
                             deadline_exceeded=stopped_for == "deadline")

    def stop_everything(self, name: str) -> int:
        """Kill every process in the container but its init, through an independent helper call."""
        completed = self._run([DOCKER, "exec", "--interactive", "--user", SANDBOX_USER, name,
                               *HELPER_COMMAND], stdin=json.dumps({"op": "kill-all"}).encode(),
                              timeout=30)
        try:
            return int(json.loads(self._text(completed.stdout))["result"]["killed"])
        except (ValueError, KeyError, TypeError):
            return 0
