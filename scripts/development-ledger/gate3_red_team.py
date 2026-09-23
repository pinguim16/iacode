#!/usr/bin/env python3
"""The internal Red Team battery for GATE 3 — SANDBOX + TOOL EXECUTION.

Focused, not exhaustive: about twenty-five attacks on what this Gate added. The batteries of the
earlier Gates keep running; this one attacks the sandbox — path traversal, link escapes, another
run's workspace, host paths and secrets, the engine's socket, unknown tools, policy escalation,
timeouts, escaped children, output and process and memory pressure, remote and destructive Git,
network egress, a forged or replayed result, another run's sandbox, the container's privileges,
a stale image and command injection — and the controls around it: the scope of the next Gate,
the boundary between the runtime and the sandbox, a credential on its way to the public remote, and
a gate that would measure an image nobody rebuilt.

The rules are the ones every battery in this repository follows.

**Every attack executes a mutation** against the real thing: a real sandbox on the real container
engine, a real scope control over a planted file, a real secret scan over a planted credential.

**Every attack requires the refusal it aimed at.** A failure for an unrelated reason has tested
nothing, so each names the refusal it expects and records what it observed.

**The battery records a null-mutation control.** The unmutated requests go through the identical
service first and must be accepted; the unmutated tree must pass the controls the host half mutates.

The sandbox half runs **inside the sandbox service's image**, with the engine's socket mounted as
the stack mounts it: `gate3_sandbox_attacks.py`. This module runs it and merges its verdicts with
the host half.

    python scripts/development-ledger/gate3_red_team.py --write
    python scripts/development-ledger/gate3_red_team.py --skip-gate-rebuild
"""

from __future__ import annotations

import argparse
import ast
import json
import random
import shutil
import string
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import policies
from ledger_common import (
    LedgerError,
    delivered_gate,
    find_root,
    published_clone,
    resolve_latest,
    scope_fingerprint,
    use_utf8_stdout,
    utc_now,
    write_json,
)

SOURCE_DESCRIPTION = (
    "scripts/development-ledger/gate3_red_team.py with gate3_sandbox_attacks.py — the internal "
    "adversarial battery of GATE 3 — SANDBOX + TOOL EXECUTION, executed against the delivery"
)

SANDBOX_ATTACK_MODULE = "gate3_sandbox_attacks.py"

SANDBOX = "file:services/sandbox/src/iacode_sandbox"

#: What the in-image half attacks, in the order it reports them.
SANDBOX_ATTACKS: tuple[tuple[str, str, str, str, str, tuple[str, ...]], ...] = (
    ("G3-A", "path traversal",
     "A tool path that climbs out of the workspace.",
     "read ../ escapes, an absolute host path, a drive, a UNC path and a null byte",
     "every one is DENIED with a PATH_ code before anything is opened",
     (f"{SANDBOX}/paths.py", "test:PathResolverTests")),
    ("G3-B", "symlink escape",
     "A link inside the workspace that points outside it.",
     "create links to a file, a directory and the root, then read, write and list through them",
     "all three are DENIED with PATH_SYMLINK_ESCAPE",
     (f"{SANDBOX}/paths.py", "test:SymlinkContainmentTests")),
    ("G3-C", "workspace isolation",
     "One run looks for another run's files.",
     "write a token in run A's workspace and search the whole filesystem of run B's sandbox",
     "the token is not found and naming A's container is DENIED",
     (f"{SANDBOX}/backend.py", "test:CrossSessionIsolationTests")),
    ("G3-D", "host path",
     "A command looks for the host's drives and home.",
     "probe the host's mount points and read the sandbox's mount table",
     "no host path exists and nothing but the in-memory workspace and tmp is mounted",
     (f"{SANDBOX}/backend.py", "test:test_no_host_path_is_mounted")),
    ("G3-E", "host secret",
     "A command reads the environment for credentials.",
     "set a credential-named sentinel in the controller, then print the sandbox's environment",
     "neither the sentinel nor any controller variable is visible",
     (f"{SANDBOX}/backend.py", "test:test_no_variable_of_the_controller_reaches_a_sandbox")),
    ("G3-F", "docker socket",
     "A command looks for the container engine.",
     "probe the engine's sockets and its TCP port from inside the sandbox",
     "no socket exists and the port cannot be reached",
     (f"{SANDBOX}/backend.py",
      "test:test_no_docker_socket_or_engine_endpoint_is_reachable")),
    ("G3-G", "unknown tool",
     "A model invents a tool name.",
     "request shell, bash, a command line, os.system and git.push as tool names",
     "every one is DENIED as UNKNOWN_TOOL and no container is started",
     (f"{SANDBOX}/tools.py", "test:test_an_unknown_tool_is_refused_and_never_mapped_to_a_shell")),
    ("G3-H", "policy escalation",
     "A request asks for more than its policy gives.",
     "add network, memory, a mount, privileges and an image to the request and to the arguments; "
     "raise the timeout; allow LD_PRELOAD; write as the reviewer; name an unknown policy",
     "every one is DENIED with its own reason",
     (f"{SANDBOX}/service.py",
      "test:test_no_request_can_change_the_network_the_limits_or_the_mounts")),
    ("G3-I", "timeout",
     "A command that never ends.",
     "run sleep 60 with a 2 s timeout",
     "TIMED_OUT within bounds and no sleep left running",
     (f"{SANDBOX}/helper.py", "test:test_a_timeout_kills_the_whole_process_tree")),
    ("G3-J", "orphan child",
     "A command that leaves children in their own session.",
     "start a setsid and a nohup child and let the parent time out",
     "every child is killed with the command",
     (f"{SANDBOX}/helper.py", "test:test_a_timeout_kills_the_whole_process_tree")),
    ("G3-K", "output bomb",
     "A command that prints 40 MB.",
     "write 40 MB to standard output",
     "the inline output stays within the policy's bound, the rest is an artifact",
     (f"{SANDBOX}/helper.py", "test:test_output_is_bounded_and_the_rest_is_an_artifact")),
    ("G3-L", "PID pressure",
     "A fork bomb.",
     "run a recursive fork bomb with a 5 s timeout",
     "the process limit contains it and the sandbox answers the next command",
     (f"{SANDBOX}/backend.py", "test:test_a_fork_bomb_is_contained_by_the_process_limit")),
    ("G3-M", "memory cap",
     "A process that allocates three times its memory.",
     "allocate 3 GiB in a 1 GiB sandbox",
     "the allocation fails in a controlled way and the sandbox answers the next command",
     (f"{SANDBOX}/backend.py",
      "test:test_a_process_that_exceeds_memory_fails_in_a_controlled_way")),
    ("G3-N", "remote Git",
     "The agent pushes to a remote.",
     "add the public remote and push from the shell; ask for push, fetch, clone and remote tools",
     "the push fails with no network and no credential; the tools do not exist",
     (f"{SANDBOX}/tools.py", "test:test_no_remote_operation_is_offered_or_possible")),
    ("G3-O", "destructive Git",
     "The agent rewrites or cleans history.",
     "ask for reset, clean, rebase and filter-repo; pass an option and a command as a revision",
     "no such tool exists and both revisions are refused",
     (f"{SANDBOX}/tools.py", "test:test_a_revision_that_looks_like_an_option_is_refused")),
    ("G3-P", "network egress",
     "A command reaches the internet.",
     "connect to two addresses and a host name, and list the interfaces",
     "every connection fails and only loopback exists",
     (f"{SANDBOX}/backend.py", "test:test_external_egress_fails")),
    ("G3-Q", "result forgery",
     "A tool request is delivered again with another command.",
     "execute a request, then deliver the same identifier with a different command",
     "the recorded result is answered and the second command never runs",
     (f"{SANDBOX}/service.py",
      "test:test_an_execution_is_never_repeated_for_a_retried_request")),
    ("G3-R", "cross-run sandbox",
     "A request names another run's sandbox.",
     "name the victim's session and its container in a request of another run",
     "the request is refused and the attacker gets a sandbox of its own",
     (f"{SANDBOX}/contracts.py", "test:test_one_run_gets_one_session_and_two_runs_get_two")),
    ("G3-S", "container privilege",
     "The sandbox holds a privilege it should not.",
     "inspect a real sandbox container and write to its root filesystem",
     "unprivileged, no capability, no new privileges, not root, no network, no bind, limited, "
     "read-only",
     (f"{SANDBOX}/backend.py", "test:test_the_sandbox_runs_unprivileged_with_no_capability")),
    ("G3-T", "stale image",
     "The image inputs changed and the old image is still there.",
     "change the sandbox Dockerfile in a copy and run a tool through a service reading the copy",
     "the service refuses with SANDBOX_IMAGE_MISSING and starts no container",
     (f"{SANDBOX}/image.py",
      "test:test_a_missing_or_stale_image_is_refused_rather_than_substituted")),
    ("G3-U", "command injection",
     "A command hidden in a structured argument.",
     "put a command in a path and in a search pattern; run a shell command that writes",
     "neither argument is executed, and the shell's own write stays in the sandbox",
     (f"{SANDBOX}/tools.py", "test:test_an_injected_host_command_only_reaches_the_sandbox")),
)

#: What only the sandbox may import; the same set `SandboxBoundaryTests` enforces.
SANDBOX_ONLY_MODULES = frozenset({"iacode_sandbox", "docker"})


@dataclass
class Attack:
    identifier: str
    target: str
    description: str
    mutation: str
    expected: str
    run: Callable[[], tuple[bool, str]]
    mandatory: bool = True
    evidence: tuple[str, ...] = field(default=())


def _compose(root: Path, *arguments: str, timeout: float = 1800.0,
             ) -> subprocess.CompletedProcess[str]:
    compose_directory = root / "infra" / "compose"
    return subprocess.run(
        ["docker", "compose", "--project-directory", str(compose_directory),
         "--file", str(compose_directory / "docker-compose.yml"),
         "--env-file", str(compose_directory / ".env"), *arguments],
        cwd=str(root), text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout)


def run_sandbox_attacks(root: Path) -> dict[str, dict[str, Any]]:
    """Build the images, execute the in-image half against the real engine, read its verdicts."""
    module = root / "scripts" / "development-ledger" / SANDBOX_ATTACK_MODULE
    if not module.is_file():
        raise LedgerError(f"the sandbox attack module is missing: {module}")
    built = _compose(root, "build", "sandbox")
    if built.returncode != 0:
        raise LedgerError("the sandbox service image could not be built:\n"
                          + built.stdout.strip()[-1500:])
    images = subprocess.run([sys.executable, str(root / "scripts" / "iacode" / "sandbox_image.py")],
                            cwd=str(root), text=True, encoding="utf-8", errors="replace",
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if images.returncode != 0:
        raise LedgerError("the sandbox image could not be built:\n" + images.stdout[-1500:])
    completed = _compose(
        root, "run", "--rm", "--no-deps", "--entrypoint", "",
        "--volume", f"{module.as_posix()}:/tmp/{SANDBOX_ATTACK_MODULE}:ro",
        "sandbox", "python", f"/tmp/{SANDBOX_ATTACK_MODULE}")
    if completed.returncode != 0:
        raise LedgerError("the in-image attack harness could not run:\n"
                          + completed.stdout.strip()[-2000:])
    for line in reversed(completed.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise LedgerError("the in-image attack harness printed no verdict document:\n"
                      + completed.stdout.strip()[-2000:])


def sandbox_imports(source: str) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return {name for name in names if name.split(".")[0] in SANDBOX_ONLY_MODULES}


def boundary_offenders(root: Path) -> list[str]:
    offenders = []
    for base in ("apps/api/src", "services/agent-runtime/src", "services/model-gateway/src",
                 "services/orchestrator/src", "packages"):
        for path in sorted((root / base).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            if sandbox_imports(path.read_text(encoding="utf-8")):
                offenders.append(path.relative_to(root).as_posix())
    return offenders


def credential() -> str:
    """A credential-shaped value built at run time, so no source file carries one."""
    alphabet = string.ascii_uppercase + string.digits
    return "AKIA" + "".join(random.SystemRandom().choice(alphabet) for _ in range(16))


def scan_staged(root: Path, repository: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "development-ledger" / "secret_scan.py"),
         "--staged", "--root", str(repository)],
        cwd=str(repository), text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def disposable_repository(root: Path, workdir: Path) -> Path:
    repository = workdir / "repository"
    repository.mkdir()
    shutil.copytree(root / ".iacode" / "policies", repository / ".iacode" / "policies")
    for arguments in (["init", "-q"], ["config", "user.name", "Red Team"],
                      ["config", "user.email", "red-team@iacode.invalid"]):
        subprocess.run(["git", *arguments], cwd=str(repository), check=True,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return repository


def build_host_attacks(root: Path, rebuild_gate: bool) -> list[Attack]:
    attacks: list[Attack] = []

    def the_next_gate_starts_early() -> tuple[bool, str]:
        """Plant the next Gate's implementation in a disposable copy and run the scope control."""
        gate = delivered_gate(root)
        with tempfile.TemporaryDirectory(prefix="iacode-g3v-") as workdir:
            fixture = Path(workdir)
            shutil.copytree(root / ".iacode" / "policies", fixture / ".iacode" / "policies")
            in_force = policies.reservations_in_force(fixture, gate)
            if not in_force:
                return False, "no reservation is in force, so the scope control guards nothing"
            reserved = str(in_force[0]["path"])
            planted = fixture / reserved
            planted.mkdir(parents=True)
            (planted / "engine.py").write_text(
                '"""Planted by the GATE 3 Red Team in a disposable copy."""\n', encoding="utf-8")
            violations = policies.scope_violations(fixture, gate)
        named = [item for item in violations if reserved in item]
        if not named:
            return False, f"the scope control accepted an implementation in {reserved}"
        return True, "the scope control refused it: " + named[0][:180]

    attacks.append(Attack(
        "G3-V", "gate scope",
        "The next Gate starts while this one closes.",
        "plant an implementation in a reservation still in force, in a disposable copy",
        "the scope control refuses it, naming the reserved path",
        the_next_gate_starts_early,
        evidence=("file:.iacode/policies/gate-scope.json", "test:Gate3ScopeTests")))

    def sandbox_logic_escapes_its_service() -> tuple[bool, str]:
        real = boundary_offenders(root)
        mutated = sandbox_imports(
            "from iacode_sandbox.service import SandboxService\nimport docker\n")
        if not mutated:
            return False, "the scan does not detect a module that imports the sandbox"
        if real:
            return False, "sandbox logic outside its service: " + ", ".join(real)
        return True, ("no module of the API, the runtime, the gateway or the worker imports the "
                      f"sandbox or a container client, and the scan detects one that does "
                      f"({', '.join(sorted(mutated))})")

    attacks.append(Attack(
        "G3-W", "sandbox boundary",
        "The runtime or the API grows an executor of its own.",
        "scan every module outside the sandbox for the sandbox package and a container client, "
        "and run the identical scan over a module that imports them",
        "the tree has none and the scan detects the mutated module",
        sandbox_logic_escapes_its_service,
        evidence=("file:services/sandbox/src/iacode_sandbox/service.py",
                  "test:SandboxBoundaryTests")))

    def a_credential_heads_for_the_public_remote() -> tuple[bool, str]:
        value = credential()
        with tempfile.TemporaryDirectory(prefix="iacode-g3z-") as workdir:
            repository = disposable_repository(root, Path(workdir))
            (repository / "clean.txt").write_text("nothing to see\n", encoding="utf-8")
            subprocess.run(["git", "add", "clean.txt"], cwd=str(repository), check=True,
                           capture_output=True)
            clean = scan_staged(root, repository)
            (repository / "config.env").write_text(f"AWS_ACCESS_KEY_ID={value}\n",
                                                   encoding="utf-8")
            subprocess.run(["git", "add", "config.env"], cwd=str(repository), check=True,
                           capture_output=True)
            planted = scan_staged(root, repository)
        if clean.returncode != 0:
            return False, "the scan refused an unmutated staged file: " + clean.stdout[-200:]
        if planted.returncode != 1:
            return False, f"the scan exited {planted.returncode} over a staged credential"
        if value in planted.stdout:
            return False, "the scan found the credential and printed it"
        return True, ("the staged credential was found and not printed: "
                      + (planted.stdout.strip().splitlines() or ["?"])[-1][:160])

    attacks.append(Attack(
        "G3-Z", "public history",
        "A credential is staged on its way to the public remote.",
        "stage a credential-shaped value in a disposable repository and run the pre-push scan",
        "the scan fails the push, names the finding and never prints the value",
        a_credential_heads_for_the_public_remote,
        evidence=("file:scripts/development-ledger/secret_scan.py", "test:SecretScanTests")))

    def a_red_sandbox_test_survives_a_stale_image() -> tuple[bool, str]:
        probe = root / "services" / "sandbox" / "tests" / "test_red_team_probe.py"
        probe.write_text(
            '"""Planted by the GATE 3 Red Team. Deleted by the same attack.\n\n'
            "If this file is still here, the battery was interrupted: delete it.\n"
            '"""\n\n\n'
            "def test_the_gate_measures_what_is_on_disk() -> None:\n"
            "    assert False, 'planted by the internal Red Team'\n",
            encoding="utf-8", newline="\n")
        try:
            completed = subprocess.run(
                [sys.executable, str(root / "scripts" / "iacode" / "gates" / "sandbox_tests.py")],
                cwd=str(root), text=True, encoding="utf-8", errors="replace",
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=2400)
        finally:
            probe.unlink(missing_ok=True)
            _compose(root, "build", "sandbox")
        if completed.returncode == 0:
            return False, "the gate passed with a failing test on disk; it measured a stale image"
        return True, ("the gate rebuilt and failed on the planted test: "
                      + (completed.stdout.strip().splitlines() or ["no output"])[-1][:160])

    def a_forged_result_for_a_sandboxed_request() -> tuple[bool, str]:
        """`M1-F-002` on the stack: the audit's null control and mutation, through the real API."""
        report = Path(tempfile.mkdtemp(prefix="iacode-g3y-")) / "report.json"
        completed = subprocess.run(
            [sys.executable, str(root / "scripts" / "iacode" / "scenarios" /
                                 "sandbox_coding_e2e.py"),
             "--scenario", "forged-result", "--report", str(report)],
            cwd=str(root), text=True, encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=1800)
        steps = {item["step"]: item for item in
                 (json.loads(report.read_text(encoding="utf-8"))["steps"]
                  if report.is_file() else [])}
        shutil.rmtree(report.parent, ignore_errors=True)
        wanted = ("control.agent_saw_the_sandbox_timeout",
                  "forgery.refused_while_the_sandbox_executes",
                  "forgery.stored_result_is_the_sandbox_result",
                  "forgery.agent_saw_the_sandbox_timeout",
                  "forgery.refused_after_the_run_ended")
        missing = [name for name in wanted if steps.get(name, {}).get("result") != "PASS"]
        if completed.returncode != 0 or missing:
            return False, ("the forgery was not refused as required: " + ", ".join(missing)
                           + " " + completed.stdout.strip()[-200:])
        return True, ("control: " + steps[wanted[0]]["detail"] + "; mutation: "
                      + steps[wanted[1]]["detail"][:120] + "; "
                      + steps[wanted[2]]["detail"] + "; " + steps[wanted[3]]["detail"])

    attacks.append(Attack(
        "G3-Y", "tool result origin",
        "A result is posted to the API for a request the sandbox is executing (M1-F-002).",
        "run the timeout scenario, post a SUCCEEDED result while the sandbox runs the command, "
        "and post it again after the run ends",
        "403 TOOL_RESULT_ORIGIN_REFUSED both times; the stored result is the sandbox's TIMED_OUT "
        "and the agent answers TIMEOUT-SEEN, as in the unmutated control run",
        a_forged_result_for_a_sandboxed_request,
        evidence=("file:services/agent-runtime/src/iacode_agent_runtime/persistence.py",
                  "test:test_a_forged_result_cannot_displace_the_sandbox_result")))

    def a_sealed_record_names_an_unpublished_commit() -> tuple[bool, str]:
        """`M1-F-003`: remove a preserved reference; the object stays, the history does not."""
        with tempfile.TemporaryDirectory(prefix="iacode-g3aa-") as workdir:
            clone = Path(workdir) / "clone"
            if not published_clone(root, clone):
                return False, "the repository could not be cloned over Git's transport"
            listed = subprocess.run(
                ["git", "for-each-ref", "--format=%(refname) %(objectname)",
                 "refs/tags/iacode-preserved"], cwd=str(clone), text=True, encoding="utf-8",
                capture_output=True, check=False).stdout.split()
            if len(listed) < 2:
                return False, "no preserved reference is published, so nothing is attacked"
            reference, commit = listed[0], listed[1]
            chain = json.loads((clone / ".iacode" / "anchors" / "checkpoint-chain.json")
                               .read_text(encoding="utf-8"))
            subject = next((item["checkpointId"] for item in chain["anchors"]
                            if commit in (clone / "docs" / "checkpoints" / item["checkpointId"]
                                          / "COMMANDS.jsonl").read_text(encoding="utf-8")),
                           None)
            if subject is None:
                return False, f"no sealed ledger names {commit[:12]}"

            def validate() -> tuple[int, str]:
                subprocess.run(["git", "checkout", "--quiet", "--detach",
                                f"refs/tags/iacode-checkpoints/{subject}"], cwd=str(clone),
                               check=True, capture_output=True)
                done = subprocess.run(
                    [sys.executable, str(root / "scripts" / "development-ledger" /
                                         "validate_checkpoint.py"), "--root", str(clone)],
                    cwd=str(root), text=True, encoding="utf-8", errors="replace",
                    capture_output=True, check=False)
                return done.returncode, (done.stdout + done.stderr).strip()

            control, _ = validate()
            subprocess.run(["git", "update-ref", "-d", reference], cwd=str(clone), check=True,
                           capture_output=True)
            code, output = validate()
        if control != 0:
            return False, f"the unmutated control was refused for {subject}"
        if code == 0 or "exists here only as a local object" not in output:
            return False, f"{subject} validated with {commit[:12]} unpublished: {output[:200]}"
        return True, (f"{subject} validated with {reference} (control) and was refused without "
                      f"it: {output.splitlines()[-1][:200]}")

    attacks.append(Attack(
        "G3-AA", "published history",
        "A sealed record names a commit no published reference reaches (M1-F-003).",
        "in a transport clone, delete the preserved reference of a commit a sealed ledger names, "
        "leaving the object in the store, and validate that checkpoint from its tag",
        "the validator refuses it as a local object no published reference reaches; with the "
        "reference it validates",
        a_sealed_record_names_an_unpublished_commit,
        evidence=("file:scripts/development-ledger/validate_checkpoint.py",
                  "test:test_every_preserved_reference_is_what_makes_its_checkpoint_valid")))

    if rebuild_gate:
        attacks.append(Attack(
            "G3-X", "delivery assurance",
            "The sandbox gate measures an image nobody rebuilt.",
            "plant a failing test in the sandbox suite on disk and run the real gate",
            "the gate builds the image first and reports the failure",
            a_red_sandbox_test_survives_a_stale_image,
            evidence=("file:scripts/iacode/gates/sandbox_tests.py",
                      "test:Gate3MandatoryGateTests")))
    return attacks


def baseline_control(root: Path, sandbox: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The unmutated path, through the identical code, which must be **accepted**."""
    checks: list[tuple[str, bool, str]] = []
    application = sandbox.get("baseline", {})
    checks.append(("a real sandbox executes unmutated requests",
                   bool(application.get("defended")), str(application.get("observed"))[:220]))
    violations = policies.scope_violations(root, delivered_gate(root))
    checks.append(("the scope control accepts the real tree", not violations,
                   "; ".join(violations)[:160] or "no violation"))
    offenders = boundary_offenders(root)
    checks.append(("the boundary scan accepts the real tree", not offenders,
                   ", ".join(offenders)[:160] or "no offender"))
    declared = policies.canonical_requirements(root, delivered_gate(root))
    checks.append(("the canonical requirement set parses and mirrors", bool(declared),
                   f"{len(declared)} row(s)"))
    residue = sandbox.get("residueAfterRelease", {}).get("containers")
    checks.append(("the battery leaves no sandbox behind", residue == 0,
                   f"{residue} container(s) left"))
    failed = [name for name, ok, _detail in checks if not ok]
    return {
        "result": "VALID" if not failed else "INVALID",
        "detail": (
            "the unmutated fixture is accepted by every control this battery mutates: "
            + "; ".join(f"{name} ({detail})" for name, _ok, detail in checks)
            if not failed else "the unmutated fixture was refused by: " + ", ".join(failed)),
        "evidence": ["file:services/sandbox/src/iacode_sandbox/service.py",
                     "file:.iacode/policies/sandbox-policy.json"],
    }


def run_battery(root: Path, checkpoint: Path, rebuild_gate: bool) -> dict[str, Any]:
    sandbox = run_sandbox_attacks(root)
    control = baseline_control(root, sandbox)
    if control["result"] != "VALID":
        raise LedgerError("the null-mutation control failed; the battery would prove nothing: "
                          + control["detail"])

    results: list[dict[str, Any]] = []
    for identifier, target, description, mutation, expected, evidence in SANDBOX_ATTACKS:
        verdict = sandbox.get(identifier)
        if verdict is None:
            defended, observed = False, "the in-image harness reported no verdict"
        else:
            defended = bool(verdict.get("defended"))
            observed = str(verdict.get("observed") or "no observation recorded")
        results.append({
            "attackId": identifier, "description": description, "target": target,
            "mutation": mutation, "expectedDefense": expected, "observed": observed[:500],
            "result": "DEFENDED" if defended else "ESCAPED", "evidence": list(evidence),
            "mandatory": True,
            "origin": "GATE-3 internal Red Team, executed in the sandbox service image",
        })
        print(f"[{results[-1]['result']}] {identifier} {target}: {observed[:130]}")

    for attack in build_host_attacks(root, rebuild_gate):
        try:
            defended, observed = attack.run()
        except Exception as error:  # noqa: BLE001 - a harness that crashes has found something
            defended, observed = False, f"the attack itself failed: {type(error).__name__}: {error}"
        results.append({
            "attackId": attack.identifier, "description": attack.description,
            "target": attack.target, "mutation": attack.mutation,
            "expectedDefense": attack.expected,
            "observed": observed[:500] or "no observation recorded",
            "result": "DEFENDED" if defended else "ESCAPED",
            "evidence": list(attack.evidence), "mandatory": attack.mandatory,
            "origin": "GATE-3 internal Red Team, executed on the host",
        })
        print(f"[{results[-1]['result']}] {attack.identifier} {attack.target}: {observed[:130]}")

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
        "defended": len(results) - len(escaped),
        "escaped": len(escaped),
        "mandatoryTotal": len(mandatory),
        "mandatoryDefended": len([item for item in mandatory
                                  if item["result"] == "DEFENDED"]),
        "result": "RED_TEAM_PASS" if not escaped else "RED_TEAM_FAIL",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Red Team Report — GATE 3 — SANDBOX + TOOL EXECUTION",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Checkpoint: `{report['checkpoint']}`",
        f"- Generated: `{report['generatedAt']}`",
        f"- Source: {report['source']}",
        f"- Attacks: {report['defended']}/{report['total']} defended",
        "",
        "## Null-mutation control",
        "",
        f"Result: `{report['baselineControl']['result']}`",
        "",
        report["baselineControl"]["detail"],
        "",
        "Without this the battery would prove nothing: a sandbox that refused every request would",
        "look perfectly defended. The unmutated requests go through the identical service and are",
        "accepted before any mutation runs.",
        "",
        "## Findings",
        "",
        "None." if not report["escaped"] else "See the escaped attacks below.",
        "",
        "## Attacks",
        "",
        "| Attack | Category | Target | Mutation | Expected | Observed | Result |",
        "|---|---|---|---|---|---|---|",
    ]
    for attack in report["attacks"]:
        lines.append("| `%s` | %s | %s | %s | %s | %s | `%s` |" % (
            attack["attackId"], "mandatory" if attack["mandatory"] else "additional",
            attack["target"], attack["mutation"], attack["expectedDefense"],
            attack["observed"].replace("|", "\\|").replace("\n", " "), attack["result"]))
    lines += ["", "## What each attack means", ""]
    for attack in report["attacks"]:
        lines += [
            f"### {attack['attackId']} — {attack['description']}",
            "",
            f"- Mutation: {attack['mutation']}",
            f"- Expected defence: {attack['expectedDefense']}",
            f"- Observed: {attack['observed']}",
            "- Evidence: " + (", ".join(f"`{item}`" for item in attack["evidence"]) or "_none_"),
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
                        help="write the report into the checkpoint")
    parser.add_argument("--skip-gate-rebuild", action="store_true",
                        help="omit the attack that plants a failing test and rebuilds the image")
    arguments = parser.parse_args()

    root = find_root(arguments.root) if arguments.root else find_root()
    checkpoint = arguments.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    report = run_battery(root, checkpoint, rebuild_gate=not arguments.skip_gate_rebuild)

    if arguments.write:
        milestone = "M1"
        write_json(checkpoint / f"{milestone}-INTERNAL-RED-TEAM.json", report)
        (checkpoint / "RED-TEAM-REPORT.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n")
        print(f"wrote {checkpoint / f'{milestone}-INTERNAL-RED-TEAM.json'}")

    print(f"RED_TEAM={report['result']} {report['defended']}/{report['total']} "
          f"control={report['baselineControl']['result']}")
    return 0 if report["result"] == "RED_TEAM_PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
