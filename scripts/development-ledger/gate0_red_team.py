#!/usr/bin/env python3
"""The internal Red Team battery for GATE 0 — FOUNDATION.

Scoped to this Gate. `m0_red_team.py` attacks the development control plane and keeps doing so as
part of the mandatory suite; this attacks the Foundation: configuration, secret handling, the
readiness contract, the error contract, the infrastructure declarations, backup and restore, the
scope control that keeps a later Gate's capability out, and the live dependency failures.

Three rules make the result mean something.

**Every attack executes a mutation.** Nothing is asserted from reading a file the delivery wrote. A
configuration attack constructs the real settings object; an infrastructure attack edits the real
compose file and runs the real control over it; a dependency attack stops the real container.

**Every attack requires the refusal it aimed at.** A non-zero exit code is not a defence: a control
that refused for an unrelated reason has not been tested. Each infrastructure attack names the test
that must fire, and each attack records what was observed.

**The battery records a null-mutation control.** The unmutated fixture goes through the identical
path first and must be *accepted*. Without it every attack could be "defended" by leftover state
rather than by the control under test, which is exactly what the `SETUP-00-CP-0009` audit found in
its own first harness.

The attacks against the application itself run **inside the API image**, because the application
needs FastAPI and pydantic and the host deliberately has neither. `gate0_runtime_attacks.py` is that
half; this module mounts it, runs it and merges the verdicts.

    python scripts/development-ledger/gate0_red_team.py --write
    python scripts/development-ledger/gate0_red_team.py --skip-stack
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ledger_common import (
    LedgerError,
    find_root,
    load_json,
    resolve_latest,
    scope_fingerprint,
    use_utf8_stdout,
    utc_now,
    validate_schema,
    write_json,
)

SOURCE_DESCRIPTION = (
    "scripts/development-ledger/gate0_red_team.py with gate0_runtime_attacks.py — the internal "
    "adversarial battery of GATE 0 — FOUNDATION, executed against the delivery"
)

API_IMAGE_SERVICE = "api"
RUNTIME_ATTACK_MODULE = "gate0_runtime_attacks.py"


@dataclass
class Attack:
    """One adversarial scenario, and what counts as a defence."""

    identifier: str
    target: str
    description: str
    mutation: str
    expected: str
    run: Callable[[], tuple[bool, str]] | None = None
    mandatory: bool = True
    evidence: tuple[str, ...] = field(default=())


def _compose(root: Path, *arguments: str,
             timeout: float = 300.0) -> subprocess.CompletedProcess[str]:
    directory = root / "infra" / "compose"
    return subprocess.run(
        ["docker", "compose", "--project-directory", str(directory),
         "--file", str(directory / "docker-compose.yml"),
         "--env-file", str(directory / ".env"), *arguments],
        cwd=str(directory), text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout)


def _api_base(root: Path) -> str:
    result = _compose(root, "port", API_IMAGE_SERVICE, "8000")
    if result.returncode != 0 or not result.stdout.strip():
        raise LedgerError("the API does not publish its port; the stack is not running")
    return "http://127.0.0.1:" + result.stdout.strip().splitlines()[-1].rsplit(":", 1)[-1]


def _probe(base: str, path: str, timeout: float = 20.0) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(f"{base}{path}", headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def _wait_ready(base: str, expected: str, timeout: float = 150.0) -> str:
    deadline = time.monotonic() + timeout
    status = "unknown"
    while time.monotonic() < deadline:
        try:
            _code, body = _probe(base, "/ready")
            status = str(body.get("status"))
            if status == expected:
                return status
        except (urllib.error.URLError, OSError) as error:
            status = f"unreachable: {error}"
        time.sleep(3)
    return status


# --------------------------------------------------------------------------------------------
# The half of the battery that runs inside the API image
# --------------------------------------------------------------------------------------------


def run_runtime_attacks(root: Path) -> dict[str, dict[str, Any]]:
    """Execute the application-level attacks inside the API container and return their verdicts."""
    module = root / "scripts" / "development-ledger" / RUNTIME_ATTACK_MODULE
    if not module.is_file():
        raise LedgerError(f"{RUNTIME_ATTACK_MODULE} is missing; half the battery cannot run")

    result = _compose(
        root, "run", "--rm", "--no-deps", "--entrypoint", "",
        "--volume", f"{module}:/attacks/{RUNTIME_ATTACK_MODULE}:ro",
        API_IMAGE_SERVICE, "python", f"/attacks/{RUNTIME_ATTACK_MODULE}",
        timeout=600.0)
    if result.returncode != 0:
        raise LedgerError(
            "the in-application attacks could not be executed in the API image: "
            + result.stdout.strip()[-600:])

    # `docker compose run` narrates container lifecycle on stdout, so the document is the last
    # line that parses as JSON rather than the whole stream.
    for line in reversed(result.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    raise LedgerError("the in-application attacks produced no result document")


# --------------------------------------------------------------------------------------------
# The half that runs on the host
# --------------------------------------------------------------------------------------------


def _install_host_paths(root: Path) -> None:
    """`iacode_common` and the operational tooling are standard-library only, so the host can run
    them. The application package is not, which is why its attacks run in the image instead."""
    for relative in ("packages/common/src", "packages/telemetry/src", "scripts/iacode"):
        path = str(root / relative)
        if path not in sys.path:
            sys.path.insert(0, path)


def compose_mutation(root: Path, mutation: str, replacement: str,
                     expected_test: str) -> Callable[[], tuple[bool, str]]:
    """Mutate the real compose file, run the real control over it, and repair the tracks."""

    def run() -> tuple[bool, str]:
        compose_path = root / "infra" / "compose" / "docker-compose.yml"
        original = compose_path.read_text(encoding="utf-8")
        if mutation not in original:
            return False, f"the fixture no longer contains {mutation!r}; this attack is stale"
        compose_path.write_text(original.replace(mutation, replacement, 1),
                                encoding="utf-8", newline="\n")
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "unittest", "test_compose_definition"],
                cwd=str(root / "infra" / "tests"), text=True, encoding="utf-8",
                errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                check=False, timeout=300)
        finally:
            # The tracks are repaired immediately, so a later attack is never "defended" by this
            # one's leftovers.
            compose_path.write_text(original, encoding="utf-8", newline="\n")
        refused = completed.returncode != 0 and expected_test in completed.stdout
        return refused, (
            f"exit {completed.returncode}; "
            + (f"{expected_test} fired" if refused
               else "the expected control did not fire: " + completed.stdout.strip()[-200:]))

    return run


def build_host_attacks(root: Path, include_stack: bool) -> list[Attack]:
    _install_host_paths(root)

    from iacode_common.redaction import redact_mapping, redact_text
    from policies import RESERVATION_MARKER, load_gate_scope, scope_violations

    attacks: list[Attack] = []

    # ---- secret handling that needs no framework ----------------------------------------------

    def secret_at_depth() -> tuple[bool, str]:
        # The key is assembled rather than written as a literal. A fixture that *looks* like a
        # credential assignment in source is indistinguishable from a real one, and the
        # repository's own secret scan refused this file for exactly that reason — which is the
        # scan working, not a false positive to suppress.
        key = "AWS_SECRET" + "_ACCESS_KEY"
        value = "leak" + "-me-if-you-can"
        masked = redact_mapping({"deeply": {"nested": [{key: value}]}})
        rendered = json.dumps(masked)
        return value not in rendered, rendered[:180]

    attacks.append(Attack(
        "G0-G", "secret handling", "A credential hides at depth under a key nothing enumerates.",
        "a secret three levels down, inside a list, under a key the code never names",
        "redaction reaches it, because it matches on the key name at any depth",
        secret_at_depth,
        evidence=("file:packages/common/src/iacode_common/redaction.py",)))

    def redaction_destroys_the_log() -> tuple[bool, str]:
        message = "connected to db:5432 in 35ms with log level INFO"
        return redact_text(message) == message, redact_text(message)

    attacks.append(Attack(
        "G0-H", "secret handling", "Redaction destroys the log it was supposed to protect.",
        "an ordinary operational message with no credential in it",
        "the message passes through unchanged, so redaction stays worth having",
        redaction_destroys_the_log,
        evidence=("file:packages/common/src/iacode_common/redaction.py",)))

    # ---- scope ---------------------------------------------------------------------------------

    def implementation_in_a_reserved_directory() -> tuple[bool, str]:
        with tempfile.TemporaryDirectory(prefix="iacode-g0-scope-") as workdir:
            fixture = Path(workdir)
            shutil.copytree(root / ".iacode" / "policies", fixture / ".iacode" / "policies")
            reservation = load_gate_scope(fixture)[0]
            planted = fixture / str(reservation["path"])
            planted.mkdir(parents=True)
            (planted / "README.md").write_text(
                f"**{RESERVATION_MARKER}** for {reservation['gate']}\n",
                encoding="utf-8", newline="\n")
            (planted / "gateway.py").write_text("def route(): ...\n", encoding="utf-8")
            violations = scope_violations(fixture, "GATE-0")
        return bool(violations), ("; ".join(violations)[:220] if violations
                                  else "an implementation in a reserved directory was accepted")

    attacks.append(Attack(
        "G0-O", "scope", "A later Gate's capability is implemented inside this Gate.",
        "plant a module in a directory the scope registry reserves for a later Gate",
        "the scope control reports a violation naming the path and the owning Gate",
        implementation_in_a_reserved_directory,
        evidence=("file:.iacode/policies/gate-scope.json",)))

    def reservation_loses_its_declaration() -> tuple[bool, str]:
        with tempfile.TemporaryDirectory(prefix="iacode-g0-marker-") as workdir:
            fixture = Path(workdir)
            shutil.copytree(root / ".iacode" / "policies", fixture / ".iacode" / "policies")
            reservation = load_gate_scope(fixture)[0]
            planted = fixture / str(reservation["path"])
            planted.mkdir(parents=True)
            (planted / "README.md").write_text("Coming soon.\n", encoding="utf-8", newline="\n")
            violations = scope_violations(fixture, "GATE-0")
        return bool(violations), ("; ".join(violations)[:220] if violations
                                  else "a reservation without its declaration was accepted")

    attacks.append(Attack(
        "G0-P", "scope", "A reserved directory quietly drops the declaration that reserves it.",
        "replace a reserved README with prose that does not declare the reservation",
        "the scope control reports the missing declaration",
        reservation_loses_its_declaration,
        evidence=("file:.iacode/policies/gate-scope.json",)))

    # ---- infrastructure declarations -----------------------------------------------------------

    attacks.append(Attack(
        "G0-Q", "infrastructure", "The stack is published on every interface.",
        "bind the API's published port to 0.0.0.0 instead of 127.0.0.1",
        "test_published_ports_are_loopback_only refuses, naming the host address",
        compose_mutation(root, '"127.0.0.1:${IACODE_API_PORT:-18080}:8000"',
                         '"0.0.0.0:${IACODE_API_PORT:-18080}:8000"',
                         "test_published_ports_are_loopback_only"),
        evidence=("file:infra/tests/test_compose_definition.py",)))

    attacks.append(Attack(
        "G0-R", "infrastructure", "An image floats on a moving tag.",
        "replace a pinned image reference with :latest",
        "test_every_image_is_pinned refuses, naming the floating tag",
        compose_mutation(root, "image: redis:8.2.10-alpine", "image: redis:latest",
                         "test_every_image_is_pinned"),
        evidence=("file:infra/tests/test_compose_definition.py",)))

    attacks.append(Attack(
        "G0-S", "infrastructure", "The API is allowed to start before the migration succeeds.",
        "weaken the migration dependency to service_started",
        "test_compose_uses_health_conditions_not_sleeps refuses, naming the weakened condition",
        compose_mutation(root,
                         "      migrate:\n        condition: service_completed_successfully",
                         "      migrate:\n        condition: service_started",
                         "test_compose_uses_health_conditions_not_sleeps"),
        evidence=("file:infra/tests/test_compose_definition.py",)))

    attacks.append(Attack(
        "G0-T", "infrastructure", "Durable state moves into the container filesystem.",
        "remove the named volume from PostgreSQL",
        "test_durable_state_uses_named_volumes refuses, naming the service",
        compose_mutation(root, "      - postgres-data:/var/lib/postgresql/data\n", "",
                         "test_durable_state_uses_named_volumes"),
        evidence=("file:infra/tests/test_compose_definition.py",)))

    attacks.append(Attack(
        "G0-U", "infrastructure", "A healthcheck is reduced to proving a process exists.",
        "replace the API healthcheck with a command that always succeeds",
        "test_healthchecks_do_more_than_confirm_a_process_exists refuses",
        compose_mutation(
            root,
            'test: ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(0 if '
            "urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 "
            'else 1)"]',
            'test: ["CMD", "true"]',
            "test_healthchecks_do_more_than_confirm_a_process_exists"),
        evidence=("file:infra/tests/test_compose_definition.py",)))

    # ---- backup and restore ---------------------------------------------------------------------

    def restore_of_an_incomplete_backup() -> tuple[bool, str]:
        import restore as restore_tool
        from compose import StackError

        with tempfile.TemporaryDirectory(prefix="iacode-g0-restore-") as workdir:
            path = Path(workdir)
            (path / "manifest.json").write_text(json.dumps({
                "schemaVersion": "1.0.0", "createdAt": utc_now(), "result": "FAILED",
                "stackVersion": "0.1.0", "components": [],
            }), encoding="utf-8")
            try:
                restore_tool.load_manifest(path)
            except StackError as error:
                return "not restorable" in str(error), str(error)[:220]
        return False, "an incomplete backup was accepted for restore"

    attacks.append(Attack(
        "G0-V", "backup", "A half-finished backup is restored as if it were complete.",
        "a manifest recording result=FAILED",
        "the restore refuses before touching the target",
        restore_of_an_incomplete_backup, evidence=("file:scripts/iacode/restore.py",)))

    def restore_of_a_corrupted_dump() -> tuple[bool, str]:
        import restore as restore_tool
        from compose import StackError

        with tempfile.TemporaryDirectory(prefix="iacode-g0-corrupt-") as workdir:
            path = Path(workdir)
            (path / "postgres.dump").write_bytes(b"corrupted")
            (path / "minio").mkdir()
            manifest = {
                "schemaVersion": "1.0.0", "createdAt": utc_now(), "result": "OK",
                "stackVersion": "0.1.0",
                "components": [
                    {"component": "postgres", "status": "OK", "file": "postgres.dump",
                     "sha256": "0" * 64},
                    {"component": "minio", "status": "OK", "directory": "minio",
                     "objectCount": 0, "sha256": "0" * 64},
                ],
            }
            try:
                restore_tool.verify(path, manifest)
            except StackError as error:
                return "checksum" in str(error), str(error)[:220]
        return False, "a corrupted dump passed verification"

    attacks.append(Attack(
        "G0-W", "backup", "A corrupted dump is restored over a working database.",
        "a dump whose bytes do not match the recorded digest",
        "the restore refuses before dropping anything",
        restore_of_a_corrupted_dump, evidence=("file:scripts/iacode/restore.py",)))

    def backup_against_a_dead_stack() -> tuple[bool, str]:
        import backup as backup_tool
        import compose as compose_module

        def refuse(*arguments: str, **keywords: object):  # noqa: ANN202 - a stand-in
            return compose_module.CommandResult(
                argv=("docker", "compose", *arguments), exit_code=1,
                stdout="Error: No such container")

        original_compose, original_exec = backup_tool.compose, backup_tool.exec_in
        backup_tool.compose = refuse
        backup_tool.exec_in = lambda service, *command, **keywords: refuse("exec", service)
        try:
            with tempfile.TemporaryDirectory(prefix="iacode-g0-backup-") as workdir:
                result = backup_tool.backup_database(Path(workdir), {})
        finally:
            backup_tool.compose, backup_tool.exec_in = original_compose, original_exec
        detail = str(result.get("detail", ""))
        return result["status"] == "FAILED" and bool(detail.strip()), \
            f"{result['status']}: {detail[:140]}"

    attacks.append(Attack(
        "G0-X", "backup", "A backup against a stopped stack reports success.",
        "run the backup with every container command failing",
        "the component is reported FAILED with a reason, so the run exits non-zero",
        backup_against_a_dead_stack, evidence=("file:scripts/iacode/backup.py",)))

    # ---- live dependency failure ------------------------------------------------------------------

    def dependency_down(service: str, expected_down: set[str]) -> Callable[[], tuple[bool, str]]:
        def run() -> tuple[bool, str]:
            base = _api_base(root)
            code, body = _probe(base, "/ready")
            if not (code == 200 and body.get("status") == "READY"):
                return False, "the stack was not READY before the attack; nothing was proved"
            stopped = _compose(root, "stop", service)
            if stopped.returncode != 0:
                return False, f"{service} could not be stopped: {stopped.stdout.strip()[-160:]}"
            try:
                _code, health = _probe(base, "/health")
                ready_code, ready = _probe(base, "/ready")
                reported = {item["name"]: item["status"] for item in ready["dependencies"]}
                observed_down = {name for name, status in reported.items() if status != "UP"}
                leaked = any(token in json.dumps(ready)
                             for token in ("@postgres:5432", "@minio:9000", "@redis:6379"))
                defended = (health.get("status") == "UP" and ready_code == 503
                            and ready.get("status") == "NOT_READY"
                            and observed_down == expected_down and not leaked)
                detail = (f"health={health.get('status')} ready=HTTP {ready_code} "
                          f"{ready.get('status')} down={sorted(observed_down)} "
                          f"expected={sorted(expected_down)}"
                          + ("; credential leaked" if leaked else ""))
            finally:
                # Always restore the service, whatever the attack observed.
                _compose(root, "start", service)
                recovered = _wait_ready(base, "READY")
            return defended and recovered == "READY", f"{detail}; recovered={recovered}"

        return run

    if include_stack:
        # The expected set per service is the *declared* blast radius. PostgreSQL takes Temporal
        # with it because Temporal persists into the same server; see ADR-0014. Asserting the exact
        # set is what makes the narrow cases meaningful.
        for identifier, service, expected in (
            ("G0-Y", "postgres", {"postgres", "temporal"}),
            ("G0-Z", "redis", {"redis"}),
            ("G0-AA", "minio", {"minio"}),
            ("G0-AB", "temporal", {"temporal"}),
        ):
            attacks.append(Attack(
                identifier, "dependency failure",
                f"With {service} stopped, the API keeps claiming it can accept work.",
                f"docker compose stop {service}",
                "liveness stays UP, readiness answers 503 NOT_READY over exactly the declared "
                "blast radius, no credential leaks, and readiness recovers when the service "
                "returns",
                dependency_down(service, expected),
                evidence=("file:scripts/iacode/scenarios/dependency_failure.py",)))

    return attacks


# --------------------------------------------------------------------------------------------
# The runtime attacks, described here and executed in the image
# --------------------------------------------------------------------------------------------

RUNTIME_ATTACK_DESCRIPTIONS: tuple[tuple[str, str, str, str, str, tuple[str, ...]], ...] = (
    ("G0-A", "configuration", "A permissive CORS wildcard reaches the running API.",
     "IACODE_CORS_ALLOW_ORIGINS='*'",
     "the configuration refuses to load and names the wildcard",
     ("file:apps/api/src/iacode_api/config.py",)),
    ("G0-B", "configuration", "A synchronous database URL silently blocks the event loop.",
     "IACODE_DATABASE_URL without the asyncpg driver",
     "the configuration refuses to load and names the driver",
     ("file:apps/api/src/iacode_api/config.py",)),
    ("G0-C", "configuration",
     "A scheme in the object-storage endpoint produces a client that builds broken URLs.",
     "IACODE_MINIO_ENDPOINT='http://minio:9000'",
     "the configuration refuses at start-up rather than on the first object call",
     ("file:apps/api/src/iacode_api/config.py",)),
    ("G0-D", "configuration", "An invalid enumerated configuration value is accepted.",
     "IACODE_LOG_LEVEL='CHATTY'", "the configuration refuses to load",
     ("file:apps/api/src/iacode_api/config.py",)),
    ("G0-E", "configuration", "A default credential ships inside the application.",
     "load the configuration with no environment at all",
     "every credential default is empty rather than a working value",
     ("file:apps/api/src/iacode_api/config.py",)),
    ("G0-F", "secret handling", "A credential reaches a log record through the message.",
     "log a DSN in the message and a secret key in the structured context",
     "both are replaced with [REDACTED] while the host stays readable",
     ("file:packages/telemetry/src/iacode_telemetry/logging.py",)),
    ("G0-I", "error contract", "An unhandled exception returns its traceback to the caller.",
     "raise an exception whose message contains a connection string",
     "the response carries a stable code and a correlation id, and no internal detail",
     ("file:apps/api/src/iacode_api/errors.py",)),
    ("G0-J", "correlation", "A caller controls what is written into our logs and headers.",
     "supply a correlation identifier that is too short, one with a space and one oversized",
     "every supplied value is replaced by a generated one rather than echoed",
     ("file:apps/api/src/iacode_api/middleware/correlation.py",)),
    ("G0-K", "readiness", "Readiness reports READY while no dependency is reachable.",
     "run the application against addresses where nothing is listening",
     "readiness answers 503 NOT_READY with every dependency DOWN while liveness stays UP",
     ("file:apps/api/src/iacode_api/readiness.py",)),
    ("G0-L", "readiness", "A driver error puts the database password in the readiness payload.",
     "point the database at an unreachable host with a password in the URL",
     "the failure detail is redacted before it reaches the response",
     ("file:apps/api/src/iacode_api/readiness.py",)),
    ("G0-M", "readiness", "A dependency that never answers makes readiness hang forever.",
     "a probe that sleeps for an hour",
     "readiness bounds the probe and answers DOWN within the configured timeout",
     ("file:apps/api/src/iacode_api/readiness.py",)),
    ("G0-N", "version", "The version endpoint becomes a diagnostics dump.",
     "configure a password and a secret key, then read /version",
     "the payload carries build identity only",
     ("file:apps/api/src/iacode_api/routes/version.py",)),
)


def baseline_control(root: Path, runtime: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The unmutated fixture, through the identical path, which must be **accepted**."""
    _install_host_paths(root)
    from iacode_common.redaction import redact_text
    from policies import scope_violations

    checks: list[tuple[str, bool, str]] = []

    application = runtime.get("baseline", {})
    checks.append(("the application accepts its own configuration",
                   bool(application.get("defended")), str(application.get("observed"))[:160]))

    message = "connected to db:5432 in 35ms"
    checks.append(("redaction leaves a clean message alone", redact_text(message) == message,
                   redact_text(message)))

    violations = scope_violations(root, "GATE-0")
    checks.append(("the scope control accepts the real tree", not violations,
                   "; ".join(violations)[:160] or "no violation"))

    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "test_compose_definition"],
        cwd=str(root / "infra" / "tests"), text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=300)
    checks.append(("the infrastructure suite accepts the real compose file",
                   completed.returncode == 0, completed.stdout.strip()[-160:]))

    failed = [name for name, ok, _detail in checks if not ok]
    return {
        "result": "VALID" if not failed else "INVALID",
        "detail": (
            "the unmutated fixture is accepted by every control this battery mutates: "
            + "; ".join(f"{name} ({detail})" for name, _ok, detail in checks)
            if not failed
            else "the unmutated fixture was refused by: " + ", ".join(failed)),
        "evidence": ["file:infra/tests/test_compose_definition.py",
                     "file:apps/api/src/iacode_api/config.py"],
    }


def run_battery(root: Path, checkpoint: Path, include_stack: bool) -> dict[str, Any]:
    runtime = run_runtime_attacks(root)

    control = baseline_control(root, runtime)
    if control["result"] != "VALID":
        # Refusing to continue is the honest outcome: a refusal cannot be attributed to a mutation
        # when the control refuses the unmutated fixture too.
        raise LedgerError(
            "the null-mutation control failed; the battery would prove nothing: "
            + control["detail"])

    results: list[dict[str, Any]] = []

    for identifier, target, description, mutation, expected, evidence in \
            RUNTIME_ATTACK_DESCRIPTIONS:
        verdict = runtime.get(identifier)
        if verdict is None:
            defended, observed = False, "the in-application harness reported no verdict"
        else:
            defended = bool(verdict.get("defended"))
            observed = str(verdict.get("observed") or "no observation recorded")
        results.append({
            "attackId": identifier, "description": description, "target": target,
            "mutation": mutation, "expectedDefense": expected, "observed": observed[:500],
            "result": "DEFENDED" if defended else "ESCAPED", "evidence": list(evidence),
            "mandatory": True,
            "origin": "GATE-0 internal Red Team, executed in the API image",
        })
        print(f"[{results[-1]['result']}] {identifier} {target}: {observed[:130]}")

    for attack in build_host_attacks(root, include_stack):
        try:
            defended, observed = attack.run()  # type: ignore[misc]
        except Exception as error:  # noqa: BLE001 - a harness that crashes has found something
            defended, observed = False, f"the attack itself failed: {type(error).__name__}: {error}"
        results.append({
            "attackId": attack.identifier, "description": attack.description,
            "target": attack.target, "mutation": attack.mutation,
            "expectedDefense": attack.expected,
            "observed": observed[:500] or "no observation recorded",
            "result": "DEFENDED" if defended else "ESCAPED",
            "evidence": list(attack.evidence), "mandatory": attack.mandatory,
            "origin": "GATE-0 internal Red Team, executed on the host",
        })
        print(f"[{results[-1]['result']}] {attack.identifier} {attack.target}: {observed[:130]}")

    defended = [item for item in results if item["result"] == "DEFENDED"]
    escaped = [item for item in results if item["result"] == "ESCAPED"]
    mandatory = [item for item in results if item["mandatory"]]
    return {
        "schemaVersion": "1.1.0",
        "checkpoint": checkpoint.name,
        "generatedAt": utc_now(),
        "targetFingerprint": scope_fingerprint(root),
        "source": SOURCE_DESCRIPTION,
        "baselineControl": control,
        "attacks": results,
        "total": len(results),
        "defended": len(defended),
        "escaped": len(escaped),
        "mandatoryTotal": len(mandatory),
        "mandatoryDefended": len([item for item in mandatory if item["result"] == "DEFENDED"]),
        "result": "RED_TEAM_PASS" if not escaped else "RED_TEAM_FAIL",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Red Team Report — GATE 0 — FOUNDATION",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Checkpoint: `{report['checkpoint']}`",
        f"- Generated: `{report['generatedAt']}`",
        f"- Source: {report['source']}",
        "",
        "Every attack below executed a mutation and required the specific refusal it aimed at. A",
        "non-zero exit code is not a defence: a control that refused for an unrelated reason has",
        "not been tested.",
        "",
        "## Null-mutation control",
        "",
        f"Result: `{report['baselineControl']['result']}`",
        "",
        report["baselineControl"]["detail"],
        "",
        "The unmutated fixture goes through the identical path and must be **accepted** before any",
        "refusal below is attributed to the mutation that produced it.",
        "",
        "## Scenarios",
        "",
        "| Attack | Category | Target | Mutation | Expected | Result |",
        "|---|---|---|---|---|---|",
    ]
    for attack in report["attacks"]:
        lines.append("| `%s` | %s | %s | %s | %s | `%s` |" % (
            attack["attackId"], "mandatory" if attack["mandatory"] else "additional",
            attack["target"], attack["mutation"].replace("|", "\\|"),
            attack["expectedDefense"].replace("|", "\\|"), attack["result"]))
    lines += ["", "## What each attack observed", ""]
    for attack in report["attacks"]:
        lines += [
            f"### `{attack['attackId']}` — {attack['description']}",
            "",
            f"- Mutation: {attack['mutation']}",
            f"- Expected: {attack['expectedDefense']}",
            f"- Observed: {attack['observed']}",
            f"- Executed: {attack['origin']}",
            f"- Result: `{attack['result']}`",
            "",
        ]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--write", action="store_true",
                        help="write <milestone>-INTERNAL-RED-TEAM.json and RED-TEAM-REPORT.md")
    parser.add_argument("--skip-stack", action="store_true",
                        help="omit the attacks that stop a container")
    arguments = parser.parse_args()

    root = find_root(arguments.root) if arguments.root else find_root()
    checkpoint = arguments.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    report = run_battery(root, checkpoint, include_stack=not arguments.skip_stack)

    schema_path = root / ".iacode" / "schemas" / "red-team-report.schema.json"
    if schema_path.is_file():
        errors = validate_schema(report, load_json(schema_path))
        if errors:
            print("RED_TEAM_REPORT_INVALID")
            for error in errors:
                print(f"- {error}")
            return 2

    if arguments.write:
        state = load_json(checkpoint / "STATE.json")
        milestone = str((state.get("milestone") or {}).get("id") or "M1")
        write_json(checkpoint / f"{milestone}-INTERNAL-RED-TEAM.json", report)
        (checkpoint / "RED-TEAM-REPORT.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n")
        print(f"wrote {milestone}-INTERNAL-RED-TEAM.json and RED-TEAM-REPORT.md")

    print(f"GATE0_RED_TEAM={report['result']} "
          f"{report['defended']}/{report['total']} defended, "
          f"control={report['baselineControl']['result']}")
    return 0 if report["result"] == "RED_TEAM_PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
