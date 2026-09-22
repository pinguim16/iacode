#!/usr/bin/env python3
"""The internal Red Team battery for GATE 1 — MODEL GATEWAY.

Focused, not exhaustive. `m0_red_team.py` attacks the development control plane and
`gate0_red_team.py` attacks the Foundation; both keep running. This attacks what Gate 1 added: the
credential boundary, the address boundary, the routing refusals, the resilience bounds, the rule
that two models can never write one answer, the catalog's refusal to destroy itself, and the record
that must never hold a prompt.

Three rules make the result mean something, and they are the same three the Foundation battery used.

**Every attack executes a mutation.** Nothing is asserted from reading a file the delivery wrote. A
routing attack builds a real gateway and calls it; a gate attack plants a failing test on disk and
runs the real gate over it.

**Every attack requires the refusal it aimed at.** A non-zero exit code is not a defence: an attack
that was refused for an unrelated reason has not tested anything, so each one names the refusal it
is looking for and records what it observed.

**The battery records a null-mutation control.** The unmutated path goes through the identical code
first and must be *accepted*. Without it a gateway that refused everything would look perfectly
defended.

Most of the battery runs **inside the API image**, because the gateway needs httpx and pydantic and
the host deliberately has neither. `gate1_runtime_attacks.py` is that half; this module mounts it,
runs it and merges the verdicts with the host-side attacks that are about the repository itself.

    python scripts/development-ledger/gate1_red_team.py --write
    python scripts/development-ledger/gate1_red_team.py --skip-gate-rebuild
"""

from __future__ import annotations

import argparse
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
    find_secrets,
    resolve_latest,
    scope_fingerprint,
    use_utf8_stdout,
    utc_now,
    write_json,
)

SOURCE_DESCRIPTION = (
    "scripts/development-ledger/gate1_red_team.py with gate1_runtime_attacks.py — the internal "
    "adversarial battery of GATE 1 — MODEL GATEWAY, executed against the delivery"
)

RUNTIME_ATTACK_MODULE = "gate1_runtime_attacks.py"

#: What the in-image half attacks, in the order it reports them. The description lives here so the
#: report reads as one battery rather than as two.
RUNTIME_ATTACKS: tuple[tuple[str, str, str, str, str, tuple[str, ...]], ...] = (
    ("G1-A", "secrets",
     "A provider echoes the credential back, and every surface the gateway produces is searched.",
     "classify a provider failure while a credential is resolved, then render the error, the "
     "resolved provider, its repr, the recorded calls and the provider registry",
     "the credential appears in none of them",
     ("file:services/model-gateway/src/iacode_model_gateway/config.py",
      "test:SecretContainmentTests")),
    ("G1-B", "trust boundary",
     "A caller supplies the address the gateway should call.",
     "look for a request field that could carry an address, then configure a link-local address, "
     "an address with user information, a file URL and one with a query string",
     "no request field exists, and every unusable configured address is refused",
     ("file:services/model-gateway/src/iacode_model_gateway/security/base_url.py",
      "test:BaseUrlSafetyTests")),
    ("G1-C", "routing",
     "A request needs a capability the catalog never recorded.",
     "send a request with tools to a model whose tool support is UNKNOWN",
     "the candidate is refused rather than tried",
     ("file:services/model-gateway/src/iacode_model_gateway/routing/policy.py",
      "test:test_unknown_capability_is_rejected_by_default")),
    ("G1-D", "resilience",
     "A credential failure is retried, burning quota on an answer that cannot change.",
     "script an authentication failure followed by a success and count the attempts",
     "exactly one attempt is made",
     ("file:services/model-gateway/src/iacode_model_gateway/resilience/retry.py",
      "test:RetryClassificationTests")),
    ("G1-E", "resilience",
     "A route names the same failing candidate twelve times.",
     "configure a route whose candidate list repeats one model and fail every call",
     "the duplicate collapses to one attempt and the chain stays bounded",
     ("file:services/model-gateway/src/iacode_model_gateway/routing/router.py",
      "test:test_fallback_chain_is_bounded_and_recorded")),
    ("G1-F", "resilience",
     "Traffic keeps arriving at a provider that is down, so every caller pays the full timeout.",
     "fail past the configured threshold, then call again and count the provider's attempts",
     "the circuit opens and the next call never reaches the provider",
     ("file:services/model-gateway/src/iacode_model_gateway/resilience/circuit.py",
      "test:CircuitBreakerTests")),
    ("G1-G", "streaming",
     "A stream dies after delivering text and a second model is offered the chance to finish it.",
     "stream text from the first candidate, fail it, and give the router a healthy second candidate",
     "the second model is never called and no output is spliced",
     ("file:services/model-gateway/src/iacode_model_gateway/gateway.py",
      "test:test_no_two_models_are_concatenated_in_one_stream")),
    ("G1-H", "routing",
     "A request far larger than the context window is sent anyway.",
     "send two hundred thousand characters to a model with a one-thousand token window",
     "the preflight refuses before the request leaves the process",
     ("file:services/model-gateway/src/iacode_model_gateway/routing/context.py",
      "test:ContextWindowTests")),
    ("G1-I", "catalog",
     "A synchronisation answers with nothing, then with a duplicated identifier.",
     "synchronise against an empty answer and then against a duplicate, and read the catalog",
     "the previous catalog survives both, active and intact",
     ("file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py",
      "test:test_failed_sync_preserves_the_previous_catalog")),
    ("G1-J", "privacy",
     "A confidential prompt is sent and the record is searched for it.",
     "send a sentence that must not be stored and render every recorded field",
     "neither the prompt nor the completion is present, and no field could hold one",
     ("file:services/model-gateway/src/iacode_model_gateway/ports.py",
      "test:PromptCaptureTests")),
    ("G1-K", "resilience",
     "Every provider is unreachable.",
     "fail both candidates of a route with a transport failure",
     "both are tried once, the failure is classified, and the caller is not held",
     ("file:services/model-gateway/src/iacode_model_gateway/providers/http_provider.py",
      "test:test_provider_unavailability_falls_back")),
    ("G1-L", "routing",
     "A caller names a model that is not in the catalog, hoping for a substitute.",
     "request an identifier the catalog does not hold while a healthy model exists",
     "the request is refused and no other model is used in its place",
     ("file:services/model-gateway/src/iacode_model_gateway/routing/router.py",
      "test:test_explicit_model_is_honoured_or_refused")),
    ("G1-M", "resilience",
     "The configuration is asked for a call with no time limit.",
     "read the client construction, then configure a zero and an absurd timeout",
     "connect and read are separate, always set, and an unusable value is refused at load time",
     ("file:services/model-gateway/src/iacode_model_gateway/config.py",
      "test:test_no_call_is_unbounded")),
    ("G1-N", "catalog",
     "A model vanishes from the provider between two synchronisations.",
     "record a call against a model, remove it from the provider's answer, synchronise again",
     "it is deactivated rather than deleted, its recorded call survives, and a new request for it "
     "is refused",
     ("file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py",
      "test:test_missing_model_is_deactivated_not_deleted")),
    ("G1-R", "secrets",
     "The key itself is pasted into the field that holds the name of its variable.",
     "configure a provider whose credential variable is a credential, and one that serves no "
     "protocol",
     "both are refused when the configuration loads, not when the first call fails",
     ("file:services/model-gateway/src/iacode_model_gateway/config.py",
      "test:test_a_configuration_that_put_a_value_where_a_name_belongs_is_refused")),
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
            "the in-image attack harness could not run:\n" + completed.stdout.strip()[-1500:])
    for line in reversed(completed.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise LedgerError(
        "the in-image attack harness printed no verdict document:\n"
        + completed.stdout.strip()[-1500:])


def build_host_attacks(root: Path, rebuild_gate: bool) -> list[Attack]:
    """The attacks that are about the repository rather than about a running gateway."""
    attacks: list[Attack] = []

    def a_stale_image_hides_a_red_test() -> tuple[bool, str]:
        """Plant a failing test on disk and run the real gate over it.

        This is the failure this Gate actually found: a gate that executes inside an image and does
        not build it first measures whatever the image happens to contain, and a red test survived a
        green gate that way for a whole Gate. The defence is that the gate builds before it
        measures, so the mutation must make it fail.
        """
        probe = root / "apps" / "api" / "tests" / "unit" / "test_red_team_probe.py"
        probe.write_text(
            '"""Planted by the GATE 1 Red Team. Deleted by the same attack.\n\n'
            "If this file is still here, the battery was interrupted: delete it.\n"
            '"""\n\n\n'
            "def test_the_gate_measures_what_is_on_disk() -> None:\n"
            "    assert False, 'planted by the internal Red Team'\n",
            encoding="utf-8", newline="\n")
        try:
            completed = subprocess.run(
                [sys.executable, str(root / "scripts" / "iacode" / "gates" / "api_tests.py")],
                cwd=str(root), text=True, encoding="utf-8", errors="replace",
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=1800)
        finally:
            probe.unlink(missing_ok=True)
            # Rebuild so the image stops carrying the planted test. Leaving it would make the next
            # gate run red for a reason that no longer exists on disk — the same class of defect,
            # pointed the other way.
            _compose(root, "build", "api")
        if completed.returncode == 0:
            return False, "the gate passed with a failing test on disk; it measured a stale image"
        return True, ("the gate rebuilt and failed on the planted test: "
                      + completed.stdout.strip().splitlines()[-1][:160])

    if rebuild_gate:
        attacks.append(Attack(
            "G1-O", "delivery assurance",
            "A gate that runs inside an image measures the image instead of the source.",
            "plant a failing test in the API suite on disk and run the real mandatory gate",
            "the gate builds the image first and reports the failure",
            a_stale_image_hides_a_red_test,
            evidence=("file:scripts/iacode/compose.py",
                      "file:scripts/iacode/gates/api_tests.py")))

    def a_control_that_names_its_gate_blinds_the_next_one() -> tuple[bool, str]:
        """The derivation is load-bearing, not decoration."""
        current = delivered_gate(root)
        derived = policies.scope_violations(root, current)
        literal = policies.scope_violations(root, "GATE-0")
        if derived:
            return False, f"the derived scope check refuses the real tree: {derived[:1]}"
        if not literal:
            return False, ("the literal produced the same answer, so the derivation is not "
                           "load-bearing and this attack proves nothing")
        return True, (f"derived from {current} the tree is clean; with the previous Gate written "
                      f"in, the same control reports {len(literal)} violation(s) — the literal "
                      f"would have blocked this Gate")

    attacks.append(Attack(
        "G1-P", "delivery assurance",
        "A generic control decides from the name of the Gate it was written during.",
        "run the scope control with the derived Gate and with the previous Gate written in",
        "the derived answer is clean and the literal one is not, so the derivation is what works",
        a_control_that_names_its_gate_blinds_the_next_one,
        evidence=("file:scripts/development-ledger/ledger_common.py",
                  "test:test_no_future_gate_capability_is_implemented")))

    def a_real_value_replaces_the_placeholder() -> tuple[bool, str]:
        """The committed example gains a credential instead of its placeholder.

        The real file is mutated and the real control is run over it, then the file is restored.
        Asserting against a copy would test a copy; the control reads the repository.
        """
        example = root / "infra" / "compose" / ".env.example"
        original = example.read_text(encoding="utf-8")
        shaped = "dw" + "-live-" + "s" * 32
        if "IACODE_DEVWORLD_API_KEY=" not in original:
            return False, "the example does not document the credential variable"
        try:
            example.write_text(
                original.replace("IACODE_DEVWORLD_API_KEY=",
                                 f"IACODE_DEVWORLD_API_KEY={shaped}"),
                encoding="utf-8", newline="\n")
            completed = subprocess.run(
                [sys.executable, "-m", "unittest", "test_compose_definition"],
                cwd=str(root / "infra" / "tests"), text=True, encoding="utf-8",
                errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                check=False, timeout=300)
        finally:
            example.write_text(original, encoding="utf-8", newline="\n")
        if completed.returncode == 0:
            return False, "the infrastructure control accepted a credential in the example file"
        if "not a placeholder" not in completed.stdout:
            return False, ("the control refused for an unrelated reason: "
                           + completed.stdout.strip()[-200:])
        return True, ("the control refused the example file the moment its placeholder became a "
                      "value, and the file was restored")

    attacks.append(Attack(
        "G1-Q", "secrets",
        "A credential value is committed where a placeholder belongs.",
        "replace the placeholder of the provider credential in the committed example file with a "
        "credential-shaped value and run the real infrastructure control",
        "the control refuses the file, naming the key",
        a_real_value_replaces_the_placeholder,
        evidence=("file:infra/compose/.env.example",
                  "file:infra/tests/test_compose_definition.py")))

    return attacks


def baseline_control(root: Path, runtime: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The unmutated path, through the identical code, which must be **accepted**."""
    checks: list[tuple[str, bool, str]] = []

    application = runtime.get("baseline", {})
    checks.append(("the gateway serves an unmutated request",
                   bool(application.get("defended")), str(application.get("observed"))[:200]))

    violations = policies.scope_violations(root, delivered_gate(root))
    checks.append(("the scope control accepts the real tree", not violations,
                   "; ".join(violations)[:160] or "no violation"))

    findings: list[str] = []
    for relative in (".iacode/policies/providers.json", ".iacode/policies/model-routes.json",
                     "infra/compose/.env.example"):
        found = find_secrets((root / relative).read_text(encoding="utf-8"))
        if found:
            findings.append(f"{relative}: {', '.join(found)}")
    checks.append(("the secret scan accepts the committed configuration", not findings,
                   "; ".join(findings) or "no finding"))

    declared = policies.canonical_requirements(root, delivered_gate(root))
    checks.append(("the canonical requirement set parses and mirrors", bool(declared),
                   f"{len(declared)} row(s)"))

    failed = [name for name, ok, _detail in checks if not ok]
    return {
        "result": "VALID" if not failed else "INVALID",
        "detail": (
            "the unmutated fixture is accepted by every control this battery mutates: "
            + "; ".join(f"{name} ({detail})" for name, _ok, detail in checks)
            if not failed else "the unmutated fixture was refused by: " + ", ".join(failed)),
        "evidence": ["file:.iacode/policies/providers.json",
                     "file:services/model-gateway/src/iacode_model_gateway/gateway.py"],
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
            "origin": "GATE-1 internal Red Team, executed in the API image",
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
            "origin": "GATE-1 internal Red Team, executed on the host",
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
        "# Red Team Report — GATE 1 — MODEL GATEWAY",
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
        "Without this the battery would prove nothing: a gateway that refused every request would",
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
    lines += [
        "",
        "## What each attack means",
        "",
    ]
    for attack in report["attacks"]:
        lines += [
            f"### {attack['attackId']} — {attack['description']}",
            "",
            f"- Mutation: {attack['mutation']}",
            f"- Expected defence: {attack['expectedDefense']}",
            f"- Observed: {attack['observed']}",
            f"- Evidence: " + (", ".join(f"`{item}`" for item in attack["evidence"]) or "_none_"),
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
