#!/usr/bin/env python3
"""The M1 audit's own focused Red Team, across the four Gates of the milestone.

Not a replay of the Gates' batteries. Each attack aims at a claim the milestone makes as a whole —
nothing an agent asks for runs on the host; no host secret, engine socket, host path or remote
reaches a sandbox; one run cannot see another; the policy, never the request, decides; the runtime
reaches a model only through the gateway; a cancelled or overdue run ends; the published history
cannot be rewritten or left unsynchronised without a control saying so.

Two halves:

- **in the sandbox service's image**, against the real engine: `m1_sandbox_attacks.py`, with the
  GATE 3 module mounted beside it for the service scaffolding;
- **on the host**, against the running stack and against disposable clones of the repository.

Every attack executes a mutation and requires the refusal it aimed at. The battery records a
null-mutation control: the unmutated requests are accepted by the identical service, the unmutated
clone passes the integrity and synchronisation controls, and the unmutated API request is accepted.

    python red_team.py --write
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
CHECKPOINT = HARNESS.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))
sys.path.insert(0, str(ROOT / "scripts" / "iacode"))

from compose import published_port  # noqa: E402
from ledger_common import scope_fingerprint, utc_now, write_json  # noqa: E402

SANDBOX = "file:services/sandbox/src/iacode_sandbox"

IN_IMAGE = (
    ("M1-A", "host execution",
     "A tool command runs anywhere but the run's own container.",
     "run a shell command that reports its host name and user and probes the host's mount points",
     "the host name is the sandbox container's, the user is 10001, no host mount point exists",
     (f"{SANDBOX}/backend.py", "test:test_an_injected_host_command_only_reaches_the_sandbox")),
    ("M1-B", "secret isolation",
     "A credential of the controller reaches a sandbox.",
     "give the controller a variable named like the provider key, then read env, /proc/1/environ "
     "and search the filesystem for credential files from inside a sandbox",
     "no controller variable, no secret value and no credential file is visible",
     (f"{SANDBOX}/backend.py", "test:test_the_environment_is_the_allowlist_and_nothing_else")),
    ("M1-C", "engine socket",
     "The container engine is reachable from a sandbox.",
     "look for the socket, DOCKER_HOST and connect to the socket path; inspect the container",
     "no socket, no endpoint, no mount and no bind in the sandbox container",
     (f"{SANDBOX}/backend.py", "test:test_no_docker_socket_or_engine_endpoint_is_reachable")),
    ("M1-D", "workspace escape",
     "A path or a link leaves the workspace.",
     "read ../, an absolute path, a Windows path, a climbing sub-path; read and write through "
     "links to / and to /etc/passwd",
     "every one is DENIED with a PATH_ code",
     (f"{SANDBOX}/paths.py", "test:PathResolverTests")),
    ("M1-E", "cross-run isolation",
     "One run sees another run's workspace.",
     "write a token in one run's workspace and search the whole filesystem of another run's "
     "sandbox for it",
     "two containers, and the token is not visible from the second",
     (f"{SANDBOX}/service.py", "test:test_one_run_gets_one_session_and_two_runs_get_two")),
    ("M1-F", "tool policy escalation",
     "A request widens what its policy allows.",
     "a reviewer writes and runs a shell, an unknown docker.run tool, a raised timeout, fields "
     "beside the contract (privileged, image, mounts) and an unknown policy",
     "every one is DENIED before a process starts",
     (f"{SANDBOX}/tools.py", "test:SandboxPolicyTests")),
    ("M1-G", "engine operation from untrusted input (R-G3-001)",
     "Something a request carries becomes an argument of the engine.",
     "run identifiers shaped like engine flags, a command shaped like engine flags, and a "
     "workspace naming a host path",
     "the containers are created from the policy alone: not privileged, no bind, no mount, no "
     "added capability, network none; the host-path workspace is refused",
     (f"{SANDBOX}/backend.py", "test:ContainerSpecTests")),
    ("M1-H", "Git remote exposure",
     "An agent's Git reaches a remote or a credential.",
     "list remotes and credential helpers, look for SSH keys and a credential store, push to the "
     "public repository, and ask for git.push, git.fetch and git.clone",
     "no remote, no credential, the push fails for lack of network and the tools do not exist",
     (f"{SANDBOX}/tools.py", "test:test_no_remote_operation_is_offered_or_possible")),
    ("M1-I", "network egress",
     "A sandbox reaches the internet or the stack.",
     "connect to a public address, the API, Temporal, the host and the database",
     "every connection fails",
     (f"{SANDBOX}/backend.py", "test:test_external_egress_fails")),
)


def docker(*arguments: str, timeout: float = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["docker", *arguments], text=True, encoding="utf-8", errors="replace",
                          capture_output=True, timeout=timeout, check=False)


def compose(*arguments: str, timeout: float = 1800) -> subprocess.CompletedProcess[str]:
    directory = ROOT / "infra" / "compose"
    return subprocess.run(
        ["docker", "compose", "--project-directory", str(directory),
         "--file", str(directory / "docker-compose.yml"), "--env-file", str(directory / ".env"),
         *arguments], cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)


def git(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *arguments], cwd=cwd, text=True, encoding="utf-8",
                          errors="replace", capture_output=True, check=False)


def ledger(cwd: Path, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, f"scripts/development-ledger/{script}", *arguments],
                          cwd=cwd, text=True, encoding="utf-8", errors="replace",
                          capture_output=True, check=False, timeout=900)


def request(url: str, payload: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        try:
            return error.code, json.loads(body)
        except json.JSONDecodeError:
            return error.code, {"raw": body[:300]}


# -- in-image ---------------------------------------------------------------------------------


def run_in_image() -> dict:
    built = compose("build", "sandbox")
    if built.returncode != 0:
        raise SystemExit("the sandbox service image could not be built:\n" + built.stdout[-1500:])
    images = subprocess.run([sys.executable, str(ROOT / "scripts" / "iacode" / "sandbox_image.py")],
                            cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                            capture_output=True, check=False)
    if images.returncode != 0:
        raise SystemExit("the sandbox image could not be built:\n" + images.stdout[-1500:])
    gate3 = ROOT / "scripts" / "development-ledger" / "gate3_sandbox_attacks.py"
    module = HARNESS / "m1_sandbox_attacks.py"
    completed = compose(
        "run", "--rm", "--no-deps", "--entrypoint", "",
        "--volume", f"{gate3.as_posix()}:/tmp/gate3_sandbox_attacks.py:ro",
        "--volume", f"{module.as_posix()}:/tmp/m1_sandbox_attacks.py:ro",
        "sandbox", "python", "/tmp/m1_sandbox_attacks.py")
    for line in reversed(completed.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise SystemExit("the in-image half printed no verdict document:\n" + completed.stdout[-2500:])


# -- host -------------------------------------------------------------------------------------


def provider_bypass() -> tuple[bool, str, dict]:
    """The runtime reaches a model only through the gateway, and no request can name a provider."""
    base = f"http://127.0.0.1:{published_port('api', 8000)}"
    control_status, control = request(f"{base}/api/v1/agent-runs", {
        "task": "Reply with exactly: M1_AUDIT_CONTROL", "team": "single-agent",
        "maxModelCalls": 1, "maxTurns": 1, "metadata": {"origin": "m1-red-team-null-control"}})
    if control.get("runId"):
        request(f"{base}/api/v1/agent-runs/{control['runId']}/cancel", {})
    forged = {}
    for name, extra in (("baseUrl", {"baseUrl": "http://attacker.invalid/v1"}),
                        ("apiKey", {"apiKey": "forged-by-the-m1-audit"}),
                        ("headers", {"headers": {"X-M1-Audit": "forged"}}),
                        ("provider", {"provider": {"base_url": "http://attacker.invalid"}})):
        status, _body = request(f"{base}/api/v1/agent-runs", {
            "task": "Reply with exactly: M1_AUDIT", "team": "single-agent", **extra})
        forged[name] = status
    names: dict[str, list[str]] = {}
    for container in ("iacode-worker", "iacode-sandbox", "iacode-web"):
        inspected = docker("inspect", "--format", "{{json .Config.Env}}", container)
        variables = json.loads(inspected.stdout or "[]") if inspected.returncode == 0 else []
        names[container] = sorted({item.split("=", 1)[0] for item in variables
                                   if item.split("=", 1)[0] in (
                                       "IACODE_DEVWORLD_API_KEY", "IACODE_OPENAI_API_KEY",
                                       "IACODE_DEVWORLD_BASE_URL", "IACODE_OPENAI_BASE_URL")})
    # Read as code, not as text: a docstring that says the runtime does not import the gateway is
    # not an import of it (the first run of this battery counted two such sentences, cmd-0020).
    imports = []
    for directory in ("services/agent-runtime/src", "services/orchestrator/src",
                      "services/sandbox/src"):
        for path in (ROOT / directory).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            docstrings = {id(node.body[0].value) for node in ast.walk(tree)
                          if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                               ast.AsyncFunctionDef))
                          and node.body and isinstance(node.body[0], ast.Expr)
                          and isinstance(node.body[0].value, ast.Constant)}
            for node in ast.walk(tree):
                named = []
                if isinstance(node, ast.Import):
                    named = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    named = [node.module or ""]
                elif (isinstance(node, ast.Constant) and isinstance(node.value, str)
                      and id(node) not in docstrings):
                    if any(marker in node.value for marker in (
                            "/chat/completions", "api.openai.com", "/v1/responses")):
                        named = [node.value[:60]]
                if any(name.split(".")[0] in ("iacode_model_gateway", "openai", "anthropic")
                       or "/" in name for name in named):
                    imports.append(f"{path.relative_to(ROOT).as_posix()}:{node.lineno}")
    control_ok = control_status in (200, 201, 202) and bool(control.get("runId"))
    defended = (all(status == 422 for status in forged.values())
                and not any(names.values()) and not imports)
    return defended, (f"forged provider fields {forged}; provider variables in worker, sandbox "
                      f"and web {names}; provider modules in runtime, worker or sandbox "
                      f"{imports or 'none'}"), {
        "name": "the unmutated run request is accepted", "ok": control_ok,
        "detail": f"HTTP {control_status}, runId {control.get('runId')}, cancelled at once"}


def scenario(script: str, *arguments: str) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="iacode-m1-rt-") as scratch:
        report = Path(scratch) / "report.json"
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "iacode" / "scenarios" / script), *arguments,
             "--report", str(report)], cwd=ROOT, text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False, timeout=1800)
        tail = (completed.stdout + completed.stderr).strip().splitlines()[-1:]
        return completed.returncode == 0, f"exit {completed.returncode}; {' '.join(tail)[:300]}"


def cancel_attack() -> tuple[bool, str]:
    return scenario("sandbox_coding_e2e.py", "--scenario", "cancel")


def deadline_attack() -> tuple[bool, str]:
    return scenario("agent_runtime_deadline.py")


def clone(destination: Path) -> None:
    completed = git(ROOT.parent, "clone", "--quiet", "--no-local", str(ROOT), str(destination))
    if completed.returncode != 0:
        raise SystemExit(f"clone failed: {completed.stderr}")
    git(destination, "fetch", "--quiet", "--tags", str(ROOT))


def history_integrity() -> tuple[bool, str, dict]:
    with tempfile.TemporaryDirectory(prefix="iacode-m1-hist-") as scratch:
        control_dir = Path(scratch) / "control"
        clone(control_dir)
        control = ledger(control_dir, "verify_integrity.py")
        moved_dir = Path(scratch) / "moved"
        clone(moved_dir)
        other = git(moved_dir, "rev-parse", "iacode-checkpoints/GATE-1-CP-0001").stdout.strip()
        git(moved_dir, "tag", "-f", "iacode-checkpoints/GATE-2-CP-0002", other)
        moved = ledger(moved_dir, "verify_integrity.py")
        # A rewrite is attacked on anchored checkpoints only. The newest sealed checkpoint carries
        # no anchor until its successor commits one — the design's stated residual limit — so the
        # first run of this battery (cmd-0020), which rewrote GATE-3-CP-0001 in a clone of the
        # committed history, attacked the one checkpoint no anchor covers there yet. Here the
        # anchor this audit commits is applied to the clone, and an older anchored checkpoint is
        # rewritten in a clone of the committed history as it stands.
        anchors = ROOT / ".iacode" / "anchors" / "checkpoint-chain.json"
        rewritten = {}
        for checkpoint, apply_audit_anchor in (("GATE-2-CP-0002", False),
                                               ("GATE-3-CP-0001", True)):
            directory = Path(scratch) / f"rewritten-{checkpoint}"
            clone(directory)
            if apply_audit_anchor:
                shutil.copyfile(anchors, directory / ".iacode" / "anchors" / "checkpoint-chain.json")
                git(directory, "-c", "user.name=m1", "-c", "user.email=m1@invalid", "commit",
                    "--quiet", "-am", "the audit's anchor")
                baseline = ledger(directory, "verify_integrity.py")
                rewritten[f"{checkpoint} anchored, unmutated"] = baseline.returncode
            tag = f"iacode-checkpoints/{checkpoint}"
            tree = git(directory, "rev-parse", f"{tag}^{{tree}}").stdout.strip()
            parent = git(directory, "rev-parse", f"{tag}^").stdout.strip()
            forged = subprocess.run(
                ["git", "commit-tree", tree, "-p", parent, "-m", "rewritten"],
                cwd=directory, text=True, capture_output=True, check=False,
                env={**os.environ, "GIT_AUTHOR_NAME": "m1", "GIT_AUTHOR_EMAIL": "m1@invalid",
                     "GIT_COMMITTER_NAME": "m1", "GIT_COMMITTER_EMAIL": "m1@invalid"}
            ).stdout.strip()
            git(directory, "tag", "-f", tag, forged)
            rewritten[checkpoint] = ledger(directory, "verify_integrity.py").returncode
    defended = (moved.returncode != 0 and rewritten["GATE-2-CP-0002"] != 0
                and rewritten["GATE-3-CP-0001"] != 0
                and rewritten["GATE-3-CP-0001 anchored, unmutated"] == 0)
    first = lambda completed: (completed.stdout.strip().splitlines() or [""])[0][:160]  # noqa: E731
    return defended, (f"moved GATE-2-CP-0002 tag: exit {moved.returncode} {first(moved)}; "
                      f"rewritten with the same tree and the tag moved (exit codes): {rewritten}"), {
        "name": "the unmutated clone verifies", "ok": control.returncode == 0,
        "detail": first(control)}


def remote_sync_attack() -> tuple[bool, str, dict]:
    with tempfile.TemporaryDirectory(prefix="iacode-m1-sync-") as scratch:
        work = Path(scratch) / "work"
        clone(work)
        bare = Path(scratch) / "remote.git"
        git(Path(scratch), "clone", "--quiet", "--bare", str(work), str(bare))
        git(work, "remote", "set-url", "origin", str(bare))
        git(work, "push", "--quiet", "origin", "--tags")
        url = str(bare)
        arguments = ("--authorised-url", url, "--tag", "iacode-checkpoints/GATE-3-CP-0001")
        control = ledger(work, "remote_sync.py", *arguments)
        (work / "unpushed.txt").write_text("m1\n", encoding="utf-8")
        git(work, "add", "unpushed.txt")
        git(work, "-c", "user.name=m1", "-c", "user.email=m1@invalid", "commit", "--quiet", "-m",
            "unpushed")
        unpushed = ledger(work, "remote_sync.py", *arguments)
        git(work, "reset", "--quiet", "--hard", "HEAD~1")
        git(bare, "tag", "-d", "iacode-checkpoints/GATE-3-CP-0001")
        missing_tag = ledger(work, "remote_sync.py", *arguments)
        wrong_url = ledger(work, "remote_sync.py", "--tag", "iacode-checkpoints/GATE-2-CP-0002")
    defended = unpushed.returncode == 1 and missing_tag.returncode == 1 and wrong_url.returncode == 1
    last = lambda completed: (completed.stdout.strip().splitlines() or [""])[-1][:120]  # noqa: E731
    return defended, (f"unpushed commit: exit {unpushed.returncode}; tag deleted on the remote: "
                      f"exit {missing_tag.returncode}; remote not the authorised URL: exit "
                      f"{wrong_url.returncode}"), {
        "name": "the synchronised clone passes", "ok": control.returncode == 0,
        "detail": last(control)}


HOST = (
    ("M1-J", "direct provider bypass",
     "A run reaches a provider other than through the gateway, or a caller names one.",
     "create runs carrying a provider address, a key, headers and a provider object; read the "
     "variable names of the worker, the sandbox and the web; scan the runtime, the worker and the "
     "sandbox for a provider module",
     "every forged request is refused with 422, no provider variable exists outside the API, and "
     "no provider module is imported below the gateway",
     ("file:packages/contracts/src/iacode_contracts/agent_runtime.py",
      "test:test_creation_cannot_supply_a_credential_or_address"), provider_bypass),
    ("M1-K", "cancellation",
     "A cancelled run keeps executing a tool, or leaves its sandbox behind.",
     "cancel a coding run while its sandbox runs a long command (scenario cancel, on the stack)",
     "the command stops, the run ends CANCELLED and no sandbox container remains",
     ("file:scripts/iacode/scenarios/sandbox_coding_e2e.py",
      "test:test_a_cancelled_run_stops_its_command_and_leaves_nothing_running"), cancel_attack),
    ("M1-L", "deadline",
     "A run that goes nowhere outlives its deadline.",
     "a run waiting on a tool past its own deadline (scenario deadline, on the stack)",
     "the run is ended by its deadline and records why",
     ("file:scripts/iacode/scenarios/agent_runtime_deadline.py",
      "test:test_the_deadline_path_writes_the_failure_down"), deadline_attack),
    ("M1-M", "history integrity",
     "A sealed checkpoint's tag is moved, or its commit rewritten, without a control noticing.",
     "in disposable clones: move GATE-2-CP-0002's tag to another commit; replace GATE-3-CP-0001's "
     "commit by one with the same tree and move its tag",
     "verify_integrity.py refuses both",
     ("file:scripts/development-ledger/anchors.py", "test:IntegrityAnchorTests"),
     history_integrity),
    ("M1-N", "remote synchronisation",
     "A delivery claims synchronisation it does not have.",
     "in a disposable clone with its own remote: an unpushed commit, a tag deleted on the remote, "
     "and a remote that is not the authorised URL",
     "remote_sync.py reports NOT_SYNCHRONISED for each",
     ("file:scripts/development-ledger/remote_sync.py", "test:RemoteSyncTests"),
     remote_sync_attack),
)


def run_battery() -> dict:
    image = run_in_image()
    controls = [{"name": "the unmutated sandbox requests are accepted by the identical service",
                 "ok": bool((image.get("baseline") or {}).get("defended")),
                 "detail": (image.get("baseline") or {}).get("observed", "")}]
    results = []
    for identifier, target, description, mutation, expected, evidence in IN_IMAGE:
        verdict = image.get(identifier) or {}
        defended = bool(verdict.get("defended"))
        results.append({
            "attackId": identifier, "description": description, "target": target,
            "mutation": mutation, "expectedDefense": expected,
            "observed": str(verdict.get("observed") or "no verdict reported")[:500],
            "result": "DEFENDED" if defended else "ESCAPED", "evidence": list(evidence),
            "mandatory": True,
            "origin": "M1 fresh-session audit, executed in the sandbox service image"})
        print(f"[{results[-1]['result']}] {identifier} {target}: {results[-1]['observed'][:150]}",
              flush=True)
    residue = int((image.get("residueAfterRelease") or {}).get("containers", -1))
    controls.append({"name": "the in-image half leaves no sandbox behind", "ok": residue == 0,
                     "detail": f"{residue} container(s) left"})

    for identifier, target, description, mutation, expected, evidence, attack in HOST:
        try:
            outcome = attack()
        except Exception as error:  # noqa: BLE001 - a crashed attack has found something
            outcome = (False, f"the attack failed: {type(error).__name__}: {error}")
        defended, observed = outcome[0], outcome[1]
        if len(outcome) > 2:
            controls.append(outcome[2])
        results.append({
            "attackId": identifier, "description": description, "target": target,
            "mutation": mutation, "expectedDefense": expected, "observed": observed[:500],
            "result": "DEFENDED" if defended else "ESCAPED", "evidence": list(evidence),
            "mandatory": True, "origin": "M1 fresh-session audit, executed on the host"})
        print(f"[{results[-1]['result']}] {identifier} {target}: {observed[:150]}", flush=True)

    failed = [item for item in controls if not item["ok"]]
    control = {
        "result": "VALID" if not failed else "INVALID",
        "detail": ("the unmutated fixture is accepted by every control this battery mutates: "
                   + "; ".join(f"{item['name']} ({item['detail']})" for item in controls)
                   if not failed else "refused unmutated: "
                   + "; ".join(f"{item['name']} ({item['detail']})" for item in failed)),
        "evidence": ["file:services/sandbox/src/iacode_sandbox/service.py",
                     "file:scripts/development-ledger/verify_integrity.py",
                     "file:scripts/development-ledger/remote_sync.py"],
    }
    escaped = [item for item in results if item["result"] == "ESCAPED"]
    return {
        "schemaVersion": "1.1.0",
        "checkpoint": CHECKPOINT.name,
        "generatedAt": utc_now(),
        "targetFingerprint": scope_fingerprint(ROOT),
        "source": ("docs/checkpoints/GATE-3-CP-0002/audit-harness/red_team.py with "
                   "m1_sandbox_attacks.py — the focused cross-gate adversarial battery of the M1 "
                   "fresh-session milestone audit"),
        "baselineControl": control,
        "attacks": results,
        "total": len(results),
        "defended": len(results) - len(escaped),
        "escaped": len(escaped),
        "mandatoryTotal": len(results),
        "mandatoryDefended": len(results) - len(escaped),
        "result": ("RED_TEAM_PASS" if not escaped and control["result"] == "VALID"
                   else "RED_TEAM_FAIL"),
    }


def render(report: dict) -> str:
    lines = [
        "# Red Team Report — M1 fresh-session milestone audit",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Checkpoint: `{report['checkpoint']}`",
        f"- Generated: `{report['generatedAt']}`",
        f"- Attacks: {report['total']}, defended {report['defended']}, escaped {report['escaped']}",
        f"- Null-mutation control: `{report['baselineControl']['result']}`",
        "",
        "This battery belongs to the audit. It was written by the auditing session against the M1",
        "criteria as a whole, not copied from a Gate: nine attacks against real sandboxes on the real",
        "engine, and five against the running stack and disposable clones of the repository.",
        "",
        "## Null-mutation control",
        "",
        report["baselineControl"]["detail"],
        "",
        "## Mandatory battery",
        "",
        "| Attack | Target | Mutation | Expected | Observed | Result |",
        "|---|---|---|---|---|---|",
    ]
    for item in report["attacks"]:
        cells = [item["attackId"], item["target"], item["mutation"], item["expectedDefense"],
                 item["observed"], f"`{item['result']}`"]
        lines.append("| " + " | ".join(str(cell).replace("|", "/").replace("\n", " ")
                                       for cell in cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    started = time.monotonic()
    report = run_battery()
    if arguments.write:
        write_json(CHECKPOINT / "M1-INTERNAL-RED-TEAM.json", report)
        (CHECKPOINT / "RED-TEAM-REPORT.md").write_text(render(report), encoding="utf-8",
                                                        newline="\n")
    print(f"RED_TEAM={report['result']} {report['defended']}/{report['total']} "
          f"control={report['baselineControl']['result']} "
          f"seconds={time.monotonic() - started:.0f}")
    return 0 if report["result"] == "RED_TEAM_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
