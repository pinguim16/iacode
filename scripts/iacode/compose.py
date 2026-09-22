"""Shared access to the Foundation stack.

Every operational script in this directory talks to Docker Compose through here, so there is one
definition of where the stack lives, one way to read its configuration and one way to run a command
against it. Scripts that each built their own ``docker compose`` invocation would drift, and the
first symptom would be a backup that read a different ``.env`` than the stack was started with.

Python rather than shell, because Windows is the primary environment.
`docs/GATE-0-CHECKLIST.md` row 13.1 requires the verification to run there as well as on POSIX, and
a bash-only operational path would make the primary environment the unsupported one.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_DIRECTORY = REPOSITORY_ROOT / "infra" / "compose"
COMPOSE_FILE = COMPOSE_DIRECTORY / "docker-compose.yml"
ENV_FILE = COMPOSE_DIRECTORY / ".env"
ENV_EXAMPLE = COMPOSE_DIRECTORY / ".env.example"

# Services that must become healthy before the stack is usable. The one-shot jobs are absent on
# purpose: they run to completion and exit, so waiting for them to be "healthy" would wait forever.
HEALTHY_SERVICES = (
    "postgres",
    "redis",
    "minio",
    "temporal",
    "api",
    "worker",
    "web",
    "prometheus",
    "grafana",
)


class StackError(RuntimeError):
    """Something about the stack is wrong in a way the caller must handle, not retry."""


@dataclass(frozen=True)
class CommandResult:
    argv: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    @property
    def output(self) -> str:
        """Everything the command printed, for a message a human reads."""
        return "\n".join(part for part in (self.stdout, self.stderr) if part.strip())


def require_docker() -> None:
    """Fail with an actionable message rather than a stack trace from ``FileNotFoundError``."""
    if shutil.which("docker") is None:
        raise StackError(
            "docker is not on PATH. The Foundation stack is local-first but it is not "
            "dependency-free: install Docker Desktop or the Docker engine and try again.")


def read_env_file(path: Path = ENV_FILE) -> dict[str, str]:
    """Parse the Compose environment file.

    Deliberately small: Compose's own ``.env`` format is ``KEY=value`` with ``#`` comments and no
    interpolation, and implementing more would mean this parser and Compose disagreeing about what
    a file means.
    """
    if not path.is_file():
        raise StackError(
            f"{path} does not exist. Run `python scripts/iacode/bootstrap_env.py` first; it "
            f"derives the file from {ENV_EXAMPLE.name} and generates the local credentials.")
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip()
    return values


def compose_environment(extra: dict[str, str] | None = None) -> dict[str, str]:
    """The process environment Compose should see."""
    environment = dict(os.environ)
    environment.update(extra or {})
    return environment


def compose(
    *arguments: str,
    capture: bool = True,
    check: bool = False,
    extra_env: dict[str, str] | None = None,
    timeout: float | None = None,
    merge_stderr: bool = True,
) -> CommandResult:
    """Run one ``docker compose`` command against the Foundation stack.

    ``merge_stderr`` is ``True`` for the common case, where the caller wants one readable stream.
    Set it to ``False`` when the command's *output* is data and the subcommand is ``exec``: Compose
    writes its own diagnostics to stderr there, so separating the streams gives the container's
    output exactly.

    It does **not** help for ``docker compose run``. That subcommand narrates container lifecycle
    on **stdout**, mixed in with the container's own output, so a value read that way arrives with
    "Container ... Created" in front of it and cannot be compared against anything. A ``run`` whose
    output matters exchanges data through a mounted file instead; see
    ``scripts/iacode/backup_restore_check.py``.
    """
    require_docker()
    argv = ("docker", "compose", "--project-directory", str(COMPOSE_DIRECTORY),
            "--file", str(COMPOSE_FILE), "--env-file", str(ENV_FILE), *arguments)
    completed = subprocess.run(
        argv,
        cwd=str(COMPOSE_DIRECTORY),
        env=compose_environment(extra_env),
        text=True,
        # UTF-8 explicitly, replacing anything undecodable. Windows defaults this to the ANSI code
        # page, and container output is UTF-8: a progress spinner in a build log was enough to make
        # an otherwise successful command raise UnicodeDecodeError from inside subprocess.
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE if capture else None,
        stderr=(subprocess.STDOUT if merge_stderr else subprocess.PIPE) if capture else None,
        check=False,
        timeout=timeout,
    )
    result = CommandResult(argv=argv, exit_code=completed.returncode,
                           stdout=completed.stdout or "", stderr=completed.stderr or "")
    if check and not result.ok:
        raise StackError(
            f"`{' '.join(arguments)}` failed with exit {result.exit_code}:\n{result.output}")
    return result


def run_in(service: str, *command: str, user: str | None = None,
           timeout: float | None = None) -> CommandResult:
    """Run a one-off command in a new container of ``service``."""
    prefix = ["run", "--rm", "--no-deps"]
    if user:
        prefix += ["--user", user]
    return compose(*prefix, service, *command, timeout=timeout)


def exec_in(service: str, *command: str, timeout: float | None = None) -> CommandResult:
    """Run a command inside the *running* container of ``service``."""
    return compose("exec", "-T", service, *command, timeout=timeout)


def service_health(service: str) -> str:
    """``healthy``, ``unhealthy``, ``starting``, ``running``, ``exited`` or ``absent``."""
    result = compose("ps", "--format", "json", service)
    if not result.ok or not result.stdout.strip():
        return "absent"
    import json

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        records = record if isinstance(record, list) else [record]
        for entry in records:
            if entry.get("Service") != service:
                continue
            health = (entry.get("Health") or "").lower()
            if health:
                return health
            return (entry.get("State") or "unknown").lower()
    return "absent"


def wait_for_health(services: Iterable[str] = HEALTHY_SERVICES, timeout: float = 420.0,
                    poll_seconds: float = 5.0,
                    report: bool = True) -> dict[str, str]:
    """Block until every named service is healthy, or the deadline passes.

    Polling a real health state rather than sleeping a fixed number of seconds:
    `docs/GATE-0-CHECKLIST.md` row 10.3 rules out fixed sleeps as a coordination mechanism, and a
    sleep is wrong in both directions — too short on a cold machine, wasted time on a warm one.
    """
    names = list(services)
    deadline = time.monotonic() + timeout
    states: dict[str, str] = {}
    while time.monotonic() < deadline:
        states = {name: service_health(name) for name in names}
        if all(state == "healthy" for state in states.values()):
            return states
        unhealthy = [name for name, state in states.items() if state == "unhealthy"]
        if unhealthy:
            # An unhealthy container will not become healthy by waiting; its healthcheck already
            # ran and failed the configured number of times.
            raise StackError(
                "service(s) reported unhealthy: " + ", ".join(sorted(unhealthy))
                + "\n" + compose("ps").stdout)
        if report:
            pending = ", ".join(
                f"{name}={state}" for name, state in sorted(states.items()) if state != "healthy")
            print(f"[stack] waiting for {pending}", flush=True)
        time.sleep(poll_seconds)
    raise StackError(
        "the stack did not become healthy within "
        f"{timeout:g}s: "
        + ", ".join(f"{name}={state}" for name, state in sorted(states.items()))
        + "\n" + compose("ps").stdout)


def published_port(service: str, container_port: int) -> int:
    """The host port a service's container port is published on."""
    result = compose("port", service, str(container_port))
    if not result.ok or not result.stdout.strip():
        raise StackError(
            f"{service} does not publish container port {container_port}: {result.stdout.strip()}")
    address = result.stdout.strip().splitlines()[-1]
    return int(address.rsplit(":", 1)[-1])


def log(message: str) -> None:
    print(f"[iacode] {message}", flush=True)


def fail(message: str) -> int:
    print(f"[iacode] FAILED: {message}", file=sys.stderr, flush=True)
    return 1


def main_guard(runner) -> None:
    """Run a script entry point, turning a :class:`StackError` into a clean non-zero exit.

    An operational script must fail with a readable reason and a correct exit code:
    `docs/GATE-0-CHECKLIST.md` row 12.1 makes that explicit for backup, and a traceback is not a
    reason.
    """
    # Output is UTF-8 whatever the machine's codepage is: these scripts re-emit what a container
    # wrote, and `cp1252` cannot encode a box character or a replacement character.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")
    try:
        sys.exit(runner())
    except StackError as error:
        sys.exit(fail(str(error)))
    except KeyboardInterrupt:
        sys.exit(130)


def sequence_as_text(value: Sequence[str]) -> str:
    return " ".join(value)
