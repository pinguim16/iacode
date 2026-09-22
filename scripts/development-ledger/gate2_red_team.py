#!/usr/bin/env python3
"""The internal Red Team battery for GATE 2 — AGENT RUNTIME.

Focused, not exhaustive. `m0_red_team.py` attacks the development control plane, `gate0_red_team.py`
the Foundation and `gate1_red_team.py` the Model Gateway; all three keep running. This attacks what
Gate 2 added: the state machine, the budgets, the repair, the tool boundary, the cancellation, the
event log, the context separation, the isolation between runs and the rule that no inference may
leave the gateway.

Three rules make the result mean something, and they are the three every battery in this repository
uses.

**Every attack executes a mutation.** Nothing is asserted from reading a file the delivery wrote. A
budget attack runs a real engine with an agent that never stops; a scope attack plants a real file
in a reserved directory and runs the real control.

**Every attack requires the refusal it aimed at.** A non-zero exit code is not a defence: an attack
refused for an unrelated reason has tested nothing, so each one names the refusal it is looking for
and records what it observed.

**The battery records a null-mutation control.** The unmutated path goes through the identical code
first and must be *accepted*. Without it a runtime that refused everything would look perfectly
defended.

Most of the battery runs **inside the API image**, because the runtime needs pydantic and SQLAlchemy
and the host deliberately has neither. `gate2_runtime_attacks.py` is that half; this module mounts
it, runs it and merges the verdicts with the host-side attacks, which are about the repository
itself.

    python scripts/development-ledger/gate2_red_team.py --write
    python scripts/development-ledger/gate2_red_team.py --skip-gate-rebuild
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import policies
from ledger_common import (
    LedgerError,
    delivered_gate,
    find_root,
    resolve_latest,
    scope_fingerprint,
    use_utf8_stdout,
    utc_now,
    write_json,
)

SOURCE_DESCRIPTION = (
    "scripts/development-ledger/gate2_red_team.py with gate2_runtime_attacks.py — the internal "
    "adversarial battery of GATE 2 — AGENT RUNTIME, executed against the delivery"
)

RUNTIME_ATTACK_MODULE = "gate2_runtime_attacks.py"

#: What the in-image half attacks, in the order it reports them. The description lives here so the
#: report reads as one battery rather than as two.
RUNTIME_ATTACKS: tuple[tuple[str, str, str, str, str, tuple[str, ...]], ...] = (
    ("G2-A", "state machine",
     "A finished run is asked to run again.",
     "apply every transition out of SUCCEEDED, FAILED and CANCELLED through the real state machine",
     "every one is refused and a terminal run stays terminal",
     ("file:services/agent-runtime/src/iacode_agent_runtime/states.py",
      "test:RunStateMachineTests")),
    ("G2-B", "budgets",
     "An agent that never finishes, against a run that must stop.",
     "run a real engine with an agent that answers MESSAGE for ever",
     "the run ends with BUDGET_EXCEEDED at the configured turn limit",
     ("file:services/agent-runtime/src/iacode_agent_runtime/budgets.py",
      "test:test_budget_exhaustion_ends_the_run")),
    ("G2-C", "agent protocol",
     "An agent that answers with rubbish for ever.",
     "run a real engine with a model that never produces a valid envelope",
     "one repair is attempted and the second refusal ends the run",
     ("file:services/agent-runtime/src/iacode_agent_runtime/protocol.py",
      "test:test_two_invalid_outputs_fail_the_run")),
    ("G2-D", "budgets",
     "A repair that is not charged makes one turn cost two invisibly.",
     "run a turn that needs a repair and read the ledger",
     "the repair is counted as a model call like any other",
     ("file:services/agent-runtime/src/iacode_agent_runtime/engine.py",
      "test:test_repair_counts_against_the_budget")),
    ("G2-E", "agent protocol",
     "Fourteen shapes of nearly-right output.",
     "parse every one of them with the real parser",
     "none is read as an answer",
     ("file:services/agent-runtime/src/iacode_agent_runtime/protocol.py",
      "test:test_invalid_envelope_is_not_accepted_silently")),
    ("G2-F", "tool execution",
     "An agent asks for a shell, with a command that would destroy the machine.",
     "run a real engine whose agent requests shell.exec with a destructive command",
     "the request is stored as data, the run pauses, and nothing executes",
     ("file:services/agent-runtime/src/iacode_agent_runtime/engine.py",
      "test:ToolExecutionBoundaryTests")),
    ("G2-G", "tool execution",
     "An agent asks for a tool its profile does not permit.",
     "run a real engine whose agent requests a tool outside its allowed actions",
     "the request is refused before anything is persisted",
     ("file:services/agent-runtime/src/iacode_agent_runtime/profiles.py",
      "test:test_tool_request_outside_allowed_actions_is_refused")),
    ("G2-H", "cancellation",
     "A cancelled run is woken by a tool result.",
     "cancel a run that is waiting for a tool and let the wait return",
     "the run reaches CANCELLED and makes no further call",
     ("file:services/agent-runtime/src/iacode_agent_runtime/engine.py",
      "test:test_cancel_while_waiting_for_tool")),
    ("G2-I", "cancellation",
     "A cancelled run keeps calling the model.",
     "request cancellation and execute a run whose agent would loop for ever",
     "no model call is made after the cancellation",
     ("file:services/agent-runtime/src/iacode_agent_runtime/engine.py",
      "test:test_no_model_call_after_cancellation")),
    ("G2-J", "event log",
     "The history is replayed to forge extra events.",
     "append every recorded event a second time through the real store contract",
     "the log is unchanged and its sequence stays monotonic and unique",
     ("file:services/agent-runtime/src/iacode_agent_runtime/persistence.py",
      "test:test_duplicate_append_does_not_duplicate_the_event")),
    ("G2-K", "privacy",
     "A prompt, a transcript or a credential is written into the run's history.",
     "append an event payload carrying each forbidden key, including nested",
     "every one is refused rather than truncated",
     ("file:services/agent-runtime/src/iacode_agent_runtime/events.py",
      "test:test_event_payload_carries_no_private_reasoning")),
    ("G2-L", "prompt separation",
     "A task written to look like a platform instruction.",
     "assemble a context and build a real turn from a task that claims to override the protocol",
     "the task stays in the user channel and never reaches the instructions",
     ("file:services/agent-runtime/src/iacode_agent_runtime/context.py",
      "test:test_task_never_enters_the_system_channel")),
    ("G2-M", "isolation",
     "Two runs at once, reading each other's task and history.",
     "execute two real engines concurrently with different tasks",
     "neither run sees the other's task, events or result",
     ("file:services/agent-runtime/src/iacode_agent_runtime/engine.py",
      "test:ConcurrentRunIsolationTests")),
    ("G2-N", "provider boundary",
     "The runtime reaches a provider directly.",
     "read every module of the installed runtime package and look for a provider or an adapter",
     "no module names a provider or imports the gateway implementation",
     ("file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py",
      "test:test_no_provider_specific_name_escapes_the_runtime")),
    ("G2-O", "gateway boundary",
     "An inference escapes the one port the runtime has.",
     "close the model port and execute a real run",
     "no inference happens at all and the run fails with a gateway error",
     ("file:services/agent-runtime/src/iacode_agent_runtime/ports.py",
      "test:test_every_inference_goes_through_the_gateway")),
    ("G2-P", "observability",
     "A task becomes a Prometheus label.",
     "record every instrument with a task as the label value",
     "the published labels are the permitted set and every value is bounded",
     ("file:services/agent-runtime/src/iacode_agent_runtime/telemetry.py",
      "test:test_no_metric_label_carries_content")),
    ("G2-Q", "limits",
     "An unbounded task, tool argument set and agent answer.",
     "run real engines with payloads far above the configured limits",
     "each one is refused before anything is stored or sent",
     ("file:services/agent-runtime/src/iacode_agent_runtime/limits.py",
      "test:PayloadLimitTests")),
    ("G2-R", "budgets",
     "A run configured with no bound at all.",
     "construct budgets with zero, negative and absurd limits",
     "every one is refused at validation",
     ("file:services/agent-runtime/src/iacode_agent_runtime/budgets.py",
      "test:test_absurd_budget_is_refused")),
    ("G2-S", "budgets",
     "A token budget enforced against usage the provider never reported.",
     "record an absent usage against a run with a token budget",
     "the budget becomes unenforceable and says so, rather than counting zero",
     ("file:services/agent-runtime/src/iacode_agent_runtime/budgets.py",
      "test:test_token_budget_is_unenforceable_without_usage")),
)


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


def _compose(root: Path, *arguments: str, timeout: float = 900.0,
             ) -> subprocess.CompletedProcess[str]:
    compose_directory = root / "infra" / "compose"
    return subprocess.run(
        ["docker", "compose", "--project-directory", str(compose_directory),
         "--file", str(compose_directory / "docker-compose.yml"),
         "--env-file", str(compose_directory / ".env"), *arguments],
        cwd=str(root), text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout)


def run_runtime_attacks(root: Path) -> dict[str, dict[str, Any]]:
    """Execute the in-image half and read its verdicts."""
    module = root / "scripts" / "development-ledger" / RUNTIME_ATTACK_MODULE
    if not module.is_file():
        raise LedgerError(f"the runtime attack module is missing: {module}")
    completed = _compose(
        root, "run", "--rm", "--no-deps", "--entrypoint", "",
        "--volume", f"{module.as_posix()}:/tmp/{RUNTIME_ATTACK_MODULE}:ro",
        "api", "python", f"/tmp/{RUNTIME_ATTACK_MODULE}")
    if completed.returncode != 0:
        raise LedgerError(
            "the in-image attack harness could not run:\n" + completed.stdout.strip()[-2000:])
    for line in reversed(completed.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise LedgerError(
        "the in-image attack harness printed no verdict document:\n"
        + completed.stdout.strip()[-2000:])


def build_host_attacks(root: Path, rebuild_gate: bool) -> list[Attack]:
    """The attacks that are about the repository rather than about a running engine."""
    attacks: list[Attack] = []

    def a_sandbox_is_implemented_early() -> tuple[bool, str]:
        """Plant an executor in the directory Gate 3 owns and run the real scope control.

        This Gate's most tempting mistake is to start the sandbox because the tool request is
        sitting there. The control that stops it is the scope registry, and the way to know it
        works is to break the rule and watch it refuse.
        """
        planted = root / "services" / "sandbox" / "executor.py"
        planted.write_text(
            '"""Planted by the GATE 2 Red Team. Deleted by the same attack."""\n\n\n'
            "def execute(command: str) -> int:\n"
            "    raise NotImplementedError\n",
            encoding="utf-8", newline="\n")
        try:
            violations = policies.scope_violations(root, delivered_gate(root))
        finally:
            planted.unlink(missing_ok=True)
        named = [item for item in violations if "services/sandbox" in item]
        if not named:
            return False, ("the scope control accepted an executor in the directory Gate 3 owns: "
                           + ("; ".join(violations) or "no violation at all"))
        return True, "the scope control refused it: " + named[0][:180]

    attacks.append(Attack(
        "G2-T", "gate scope",
        "The sandbox is started early, because the tool request is already there.",
        "plant an executor in services/sandbox and run the real scope control",
        "the control refuses the delivery, naming the reserved path",
        a_sandbox_is_implemented_early,
        evidence=("file:.iacode/policies/gate-scope.json",
                  "test:Gate2ScopeTests")))

    def the_workflow_becomes_non_deterministic() -> tuple[bool, str]:
        """Read the workflow module and look for what replay cannot survive.

        Workflow code is replayed from history. A clock read, a random value, a direct database
        call or a network call inside it produces a different answer on replay and corrupts the
        run. The mutation is a module that does exactly that, run through the same check.
        """
        source = (root / "services" / "orchestrator" / "src" / "iacode_orchestrator"
                  / "workflows" / "agent_run.py")
        if not source.is_file():
            return False, "the workflow module is missing"

        def offenders(text: str) -> list[str]:
            found: list[str] = []
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    target = node.func
                    parts: list[str] = []
                    while isinstance(target, ast.Attribute):
                        parts.append(target.attr)
                        target = target.value
                    if isinstance(target, ast.Name):
                        parts.append(target.id)
                    name = ".".join(reversed(parts))
                    if name in ("time.time", "time.monotonic", "datetime.now", "random.random",
                                "random.uniform", "uuid.uuid4", "os.getenv", "requests.get",
                                "httpx.get", "httpx.post"):
                        found.append(name)
                if isinstance(node, ast.Import):
                    found += [alias.name for alias in node.names
                              if alias.name in ("random", "requests", "httpx", "sqlalchemy",
                                                "subprocess")]
                if isinstance(node, ast.ImportFrom) and node.module in (
                        "random", "requests", "httpx", "sqlalchemy", "subprocess"):
                    found.append(node.module)
            return found

        real = offenders(source.read_text(encoding="utf-8"))
        mutated = offenders(
            "import random\nimport time\n\n\n"
            "def run():\n    return random.random() + time.time()\n")
        if not mutated:
            return False, "the check does not detect a non-deterministic module; it proves nothing"
        if real:
            return False, "the workflow is not deterministic: " + ", ".join(sorted(set(real)))
        return True, ("the workflow reads no clock, no randomness and no database, and the check "
                      f"detects a module that does ({', '.join(sorted(set(mutated)))})")

    attacks.append(Attack(
        "G2-U", "durability",
        "Workflow code that cannot be replayed.",
        "scan the real workflow for a clock, a random value, a database or a network call, and "
        "run the identical scan over a module that has them",
        "the workflow has none and the scan detects the mutated module",
        the_workflow_becomes_non_deterministic,
        evidence=("file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py",
                  "test:WorkflowDeterminismTests")))

    def a_red_agent_runtime_test_survives_a_stale_image() -> tuple[bool, str]:
        """Plant a failing test in the new suite and run the real mandatory gate over it."""
        probe = (root / "services" / "agent-runtime" / "tests" / "test_red_team_probe.py")
        probe.write_text(
            '"""Planted by the GATE 2 Red Team. Deleted by the same attack.\n\n'
            "If this file is still here, the battery was interrupted: delete it.\n"
            '"""\n\n\n'
            "def test_the_gate_measures_what_is_on_disk() -> None:\n"
            "    assert False, 'planted by the internal Red Team'\n",
            encoding="utf-8", newline="\n")
        try:
            completed = subprocess.run(
                [sys.executable,
                 str(root / "scripts" / "iacode" / "gates" / "agent_runtime_tests.py")],
                cwd=str(root), text=True, encoding="utf-8", errors="replace",
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=1800)
        finally:
            probe.unlink(missing_ok=True)
            # Rebuild so the image stops carrying the planted test. Leaving it would make the next
            # gate run red for a reason that no longer exists on disk.
            _compose(root, "build", "api")
        if completed.returncode == 0:
            return False, "the gate passed with a failing test on disk; it measured a stale image"
        return True, ("the gate rebuilt and failed on the planted test: "
                      + (completed.stdout.strip().splitlines() or ["no output"])[-1][:160])

    if rebuild_gate:
        attacks.append(Attack(
            "G2-V", "delivery assurance",
            "The new mandatory gate measures an image nobody rebuilt.",
            "plant a failing test in the agent runtime suite on disk and run the real gate",
            "the gate builds the image first and reports the failure",
            a_red_agent_runtime_test_survives_a_stale_image,
            evidence=("file:scripts/iacode/gates/agent_runtime_tests.py",
                      "file:scripts/iacode/compose.py")))

    return attacks


def baseline_control(root: Path, runtime: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The unmutated path, through the identical code, which must be **accepted**."""
    checks: list[tuple[str, bool, str]] = []

    application = runtime.get("baseline", {})
    checks.append(("the runtime executes an unmutated run",
                   bool(application.get("defended")), str(application.get("observed"))[:220]))

    violations = policies.scope_violations(root, delivered_gate(root))
    checks.append(("the scope control accepts the real tree", not violations,
                   "; ".join(violations)[:160] or "no violation"))

    declared = policies.canonical_requirements(root, delivered_gate(root))
    checks.append(("the canonical requirement set parses and mirrors", bool(declared),
                   f"{len(declared)} row(s)"))

    profiles = sorted((root / "agents" / "profiles").glob("*.json"))
    teams = sorted((root / "agents" / "teams").glob("*.json"))
    checks.append(("the declared agents and teams are readable",
                   bool(profiles) and bool(teams),
                   f"{len(profiles)} profile(s), {len(teams)} team(s)"))

    failed = [name for name, ok, _detail in checks if not ok]
    return {
        "result": "VALID" if not failed else "INVALID",
        "detail": (
            "the unmutated fixture is accepted by every control this battery mutates: "
            + "; ".join(f"{name} ({detail})" for name, _ok, detail in checks)
            if not failed else "the unmutated fixture was refused by: " + ", ".join(failed)),
        "evidence": ["file:services/agent-runtime/src/iacode_agent_runtime/engine.py",
                     "file:agents/teams/single-agent.json"],
    }


def run_battery(root: Path, checkpoint: Path, rebuild_gate: bool) -> dict[str, Any]:
    runtime = run_runtime_attacks(root)

    control = baseline_control(root, runtime)
    if control["result"] != "VALID":
        raise LedgerError(
            "the null-mutation control failed; the battery would prove nothing: "
            + control["detail"])

    results: list[dict[str, Any]] = []
    for identifier, target, description, mutation, expected, evidence in RUNTIME_ATTACKS:
        verdict = runtime.get(identifier)
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
            "origin": "GATE-2 internal Red Team, executed in the API image",
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
            "origin": "GATE-2 internal Red Team, executed on the host",
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
        "# Red Team Report — GATE 2 — AGENT RUNTIME",
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
        "Without this the battery would prove nothing: a runtime that refused every request would",
        "look perfectly defended. The unmutated path goes through the identical code and is",
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
            attack["observed"].replace("|", "\\|"), attack["result"]))
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
