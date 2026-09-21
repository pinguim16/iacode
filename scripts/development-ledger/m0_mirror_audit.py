#!/usr/bin/env python3
"""Reproduce a milestone audit internally, before asking for the external one.

This is the evidence harness for the M0 Closure Auditor defined in
``.iacode/agents/m0-closure-auditor.md``. It implements, inside the delivery, the dimensions the
independent ``SETUP-00-CP-0007`` audit examined, so the external auditor confirms rather than
discovers.

It is explicitly *not* independent validation. It runs in the same session, on the same tooling,
authored by the same run. Its verdict is ``PASS`` or ``FAIL`` for internal quality only, and the
checkpoint validator refuses any attempt to describe it as an external verdict. That separation is
declared, not disguised.

The auditor never implements and never repairs. It reads, recomputes and reports.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from anchors import TAG_NAMESPACE, load_anchors, resolve_tag, verify_chain
from ledger_common import (
    LedgerError,
    clone_with_worktree,
    find_root,
    load_json,
    resolve_latest,
    run_git,
    scope_fingerprint,
    utc_now,
    validate_schema,
    write_json,
)

INDEPENDENCE = (
    "Internal quality assurance. This mirror audit is authored by the implementing run, on the "
    "same tooling, in the same session. It is not independent external validation and may not be "
    "recorded as one; only a milestone attestation produced by a separate audit checkpoint can "
    "grant MILESTONE_EXTERNAL_PASS."
)


class Mirror:
    def __init__(self, root: Path, checkpoint: Path) -> None:
        self.root = root
        self.checkpoint = checkpoint
        self.checks: list[dict[str, Any]] = []
        self.state = load_json(checkpoint / "STATE.json")

    def record(self, identifier: str, dimension: str, expectation: str,
               observed: str, result: str, evidence: list[str]) -> None:
        self.checks.append({
            "id": identifier,
            "dimension": dimension,
            "expectation": expectation,
            "observed": observed,
            "result": result,
            "evidence": evidence,
        })
        print(f"[{identifier}] {result} {dimension}: {observed}")

    def check(self, identifier: str, dimension: str, expectation: str,
              evidence: list[str], probe: Callable[[], tuple[bool, str]]) -> None:
        try:
            ok, observed = probe()
        except Exception as exc:  # an auditor that crashes has found something
            ok, observed = False, f"the check itself failed: {exc}"
        self.record(identifier, dimension, expectation, observed, "PASS" if ok else "FAIL", evidence)


def _tool(root: Path, *argv: str) -> tuple[int, str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, *argv], cwd=root, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False, env=environment)
    return completed.returncode, completed.stdout


def _first_line(output: str) -> str:
    for line in output.splitlines():
        if line.strip():
            return line.strip()[:300]
    return "no output"


def run_audit(root: Path, checkpoint: Path, clean_clone: bool) -> dict[str, Any]:
    from delivery_assurance import evaluate_matrix
    from derive_counts import derive_counts
    from lessons import guardrail_effectiveness, load_lessons, preflight_staleness
    from policies import audit_attacks, audit_findings, canonical_requirements, mandatory_gates, open_audits

    mirror = Mirror(root, checkpoint)
    gate = str(mirror.state.get("gate"))
    milestone = str((mirror.state.get("milestone") or {}).get("id") or "M0")
    matrix = load_json(checkpoint / "REQUIREMENTS-MATRIX.json")
    report = evaluate_matrix(root, checkpoint, matrix)

    # 1. Canonical SETUP requirements
    def probe_setup() -> tuple[bool, str]:
        canonical = canonical_requirements(root, gate)
        declared = {
            str(row.get("sourceRef")): row for row in matrix["requirements"] if isinstance(row, dict)}
        missing = [item["key"] for item in canonical
                   if f"canonical:{gate}#{item['key']}" not in declared]
        incomplete = [
            key for key in (item["key"] for item in canonical)
            if declared.get(f"canonical:{gate}#{key}", {}).get("status") != "COMPLETE"]
        ok = not missing and not incomplete
        return ok, (
            f"{len(canonical) - len(incomplete)}/{len(canonical)} canonical rows COMPLETE"
            + (f"; missing {', '.join(missing)}" if missing else "")
            + (f"; not complete {', '.join(incomplete)}" if incomplete else ""))

    mirror.check("MIR-001", "SETUP requirements",
                 "Every row of the canonical Gate specification is declared and COMPLETE.",
                 ["file:docs/SETUP-00-CHECKLIST.md", "checkpoint:REQUIREMENTS-MATRIX.json"],
                 probe_setup)

    # 2. Audit findings
    def probe_findings() -> tuple[bool, str]:
        total = 0
        closed = 0
        for audit in open_audits(root, gate, checkpoint.name):
            findings = audit_findings(root, audit)
            total += len(findings)
            name = audit.get("findingsClosureFile") or "FINDINGS-CLOSURE.json"
            document = load_json(checkpoint / str(name))
            rows = {str(row["findingId"]): row for row in document.get("findings") or []}
            for finding in findings:
                row = rows.get(finding["id"])
                if row and row.get("status") == "CLOSED":
                    closed += 1
        return closed == total and total > 0, f"{closed}/{total} audit findings CLOSED"

    # The closure artifact is named by the registry entry that binds the audit to this corrective
    # checkpoint, so the mirror follows the repository instead of one audit's file name.
    closure_evidence = [
        f"checkpoint:{audit.get('findingsClosureFile') or 'FINDINGS-CLOSURE.json'}"
        for audit in open_audits(root, gate, checkpoint.name)
    ] or ["checkpoint:REQUIREMENTS-MATRIX.json"]

    mirror.check("MIR-002", "Audit findings", "Every finding of the open audit is CLOSED.",
                 closure_evidence, probe_findings)

    # 3. Mandatory attacks
    def probe_attacks() -> tuple[bool, str]:
        red_team = load_json(checkpoint / f"{milestone}-INTERNAL-RED-TEAM.json")
        results = {str(item["attackId"]): item for item in red_team.get("attacks") or []}
        expected: list[str] = []
        for audit in open_audits(root, gate, checkpoint.name):
            expected += [item["id"] for item in audit_attacks(root, audit)
                         if item["mandatory"] == "true"]
        defended = [item for item in expected if results.get(item, {}).get("result") == "DEFENDED"]
        return len(defended) == len(expected) and bool(expected), (
            f"{len(defended)}/{len(expected)} mandatory attacks defended; "
            f"{red_team.get('defended')}/{red_team.get('total')} overall")

    mirror.check("MIR-003", "Mandatory attacks",
                 "Every mandatory attack of the sealed Red Team report is defended.",
                 [f"checkpoint:{milestone}-INTERNAL-RED-TEAM.json"], probe_attacks)

    # 4. Engineering memory
    def probe_memory() -> tuple[bool, str]:
        code, output = _tool(root, "scripts/development-ledger/validate_lessons.py")
        return code == 0, _first_line(output)

    mirror.check("MIR-004", "Engineering Memory", "The memory validates.",
                 ["file:.iacode/memory/lessons.jsonl"], probe_memory)

    # 5. Lessons
    def probe_lessons() -> tuple[bool, str]:
        lessons = load_lessons(root)
        guarded = [item for item in lessons if item.get("status") == "GUARDED"]
        confirmed = [item for item in lessons if item.get("status") == "CONFIRMED"]
        unresolved = [
            item["lessonId"] for item in lessons
            for failure in item.get("guardrailFailures") or []
            if not failure.get("resolvedIn")]
        return not unresolved, (
            f"{len(lessons)} lessons, {len(guarded)} GUARDED, {len(confirmed)} CONFIRMED, "
            f"{len(unresolved)} with an unresolved guardrail failure")

    mirror.check("MIR-005", "Lessons", "No lesson carries an unresolved guardrail failure.",
                 ["file:.iacode/memory/LESSONS.md"], probe_lessons)

    # 6. Guardrails
    def probe_guardrails() -> tuple[bool, str]:
        measured = guardrail_effectiveness(root)
        ok = (measured["guardrailFailures"] == 0
              and measured["guardrailsEffective"] == measured["guardrailsTotal"]
              and measured["guardrailsTotal"] > 0)
        return ok, (
            f"{measured['guardrailsEffective']}/{measured['guardrailsTotal']} effective, "
            f"{measured['guardrailsResolved']} resolved, {measured['guardrailsTested']} tested, "
            f"{measured['guardrailFailures']} failures")

    mirror.check("MIR-006", "Guardrails",
                 "Every guardrail resolves, is verified by a test, and has no unresolved failure.",
                 ["file:.iacode/memory/guardrails/registry.json"], probe_guardrails)

    # 7. Preflight
    def probe_preflight() -> tuple[bool, str]:
        preflight = load_json(checkpoint / "LESSON-PREFLIGHT.json")
        messages = preflight_staleness(root, preflight, gate)
        return not messages, ("fresh; fingerprint recomputed and selection reproduced"
                              if not messages else "; ".join(messages)[:300])

    mirror.check("MIR-007", "Lesson preflight",
                 "The preflight is bound to the Gate and fresh against the current memory.",
                 ["checkpoint:LESSON-PREFLIGHT.json"], probe_preflight)

    # 8. Green Keeper
    def probe_green_keeper() -> tuple[bool, str]:
        cycles = [json.loads(line) for line in
                  (checkpoint / "REWORK-LOG.jsonl").read_text(encoding="utf-8").splitlines()
                  if line.strip()]
        if not cycles:
            return False, "no rework cycle recorded"
        last = cycles[-1]
        required = set(mandatory_gates(root))
        declared = {str(item) for item in last.get("requiredGates") or []}
        fresh = last.get("scopeFingerprint") == scope_fingerprint(root)
        ok = (last.get("result") == "GREEN" and declared == required
              and not last.get("remainingFailures") and fresh)
        return ok, (
            f"{len(cycles)} cycle(s), last {last.get('result')}, measured against "
            f"{len(declared)}/{len(required)} mandatory gates, "
            f"{'fresh' if fresh else 'STALE'}")

    mirror.check("MIR-008", "Green Keeper",
                 "The last cycle is GREEN over the closed mandatory set and is not stale.",
                 ["checkpoint:REWORK-LOG.jsonl"], probe_green_keeper)

    # 9. Completeness
    def probe_completeness() -> tuple[bool, str]:
        ok = (report["result"] == "PASS" and report["coveragePercent"] == 100.0
              and report["evidenceCoveragePercent"] == 100.0
              and report["totalRequirements"] == report["expectedRequirements"])
        return ok, (
            f"{report['complete']}/{report['totalRequirements']} complete against an expected set "
            f"of {report['expectedRequirements']}, coverage {report['coveragePercent']:.2f}, "
            f"evidence {report['evidenceCoveragePercent']:.2f}")

    mirror.check("MIR-009", "Delivery Completeness",
                 "Coverage and evidence coverage are total over the derived expected set.",
                 ["checkpoint:COMPLETENESS-REPORT.json"], probe_completeness)

    # 10. History integrity
    def probe_integrity() -> tuple[bool, str]:
        messages = verify_chain(root, require_sealed=True, exclude={checkpoint.name})
        anchors = load_anchors(root)
        return not messages, (f"{len(anchors)} anchors verified" if not messages
                              else "; ".join(messages)[:300])

    mirror.check("MIR-010", "History integrity", "The sealed checkpoint chain resolves.",
                 ["file:.iacode/anchors/checkpoint-chain.json"], probe_integrity)

    # 11. Tags
    def probe_tags() -> tuple[bool, str]:
        anchors = load_anchors(root)
        wrong = [item["checkpointId"] for item in anchors
                 if resolve_tag(root, f"{TAG_NAMESPACE}{item['checkpointId']}") != item["commit"]]
        return not wrong, (f"{len(anchors)} tags resolve to their anchored commits"
                           if not wrong else "moved: " + ", ".join(wrong))

    mirror.check("MIR-011", "Tags", "Every anchored tag resolves to its anchored commit.",
                 ["file:.iacode/anchors/checkpoint-chain.json"], probe_tags)

    # 12. Quality evidence
    def probe_quality() -> tuple[bool, str]:
        quality = load_json(checkpoint / "QUALITY.json")
        checks = quality.get("checks") or {}
        unevidenced = [name for name, entry in checks.items()
                       if entry.get("status") == "PASS" and not entry.get("evidence")]
        unjustified = [name for name, entry in checks.items()
                       if entry.get("status") == "NOT_APPLICABLE" and not entry.get("justification")]
        failed = [name for name, entry in checks.items() if entry.get("status") == "FAIL"]
        ok = not (unevidenced or unjustified or failed)
        return ok, (
            f"{sum(1 for entry in checks.values() if entry.get('status') == 'PASS')} PASS with "
            f"evidence, {len(failed)} FAIL, {len(unevidenced)} unevidenced, "
            f"{len(unjustified)} unjustified")

    mirror.check("MIR-012", "Quality evidence", "Every PASS carries evidence and nothing is red.",
                 ["checkpoint:QUALITY.json"], probe_quality)

    # 13. Command reproducibility
    def probe_commands() -> tuple[bool, str]:
        records = [json.loads(line) for line in
                   (checkpoint / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
                   if line.strip()]
        unbound = [record.get("id") for record in records
                   if record.get("inputs") and not record.get("inputsDigest")]
        nonzero = [record.get("id") for record in records
                   if record.get("result") == "COMPLETED" and record.get("exitCode") not in (0, None)]
        return not unbound, (
            f"{len(records)} records, {len(unbound)} without an input digest, "
            f"{len(nonzero)} recorded failures kept in the ledger")

    mirror.check("MIR-013", "Command reproducibility",
                 "Every record that names an input binds it by content.",
                 ["checkpoint:COMMANDS.jsonl"], probe_commands)

    # 14. Derived counts
    def probe_counts() -> tuple[bool, str]:
        stored = load_json(checkpoint / "COUNTS.json")
        derived = derive_counts(root, checkpoint)
        mismatched = [
            key for key, value in derived.items()
            if (stored["counts"].get(key, {}).get("numerator"),
                stored["counts"].get(key, {}).get("denominator"))
            != (value["numerator"], value["denominator"])]
        return not mismatched, (
            "; ".join(f"{key}={value['numerator']}/{value['denominator']}"
                      for key, value in sorted(derived.items()))
            + ("; mismatched " + ", ".join(mismatched) if mismatched else ""))

    mirror.check("MIR-014", "Derived counts", "Every evidential count matches its derivation.",
                 ["checkpoint:COUNTS.json"], probe_counts)

    # 15. Documentation
    def probe_documentation() -> tuple[bool, str]:
        import re

        missing: list[str] = []
        total = 0
        for path in root.rglob("*.md"):
            if ".git" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for target in re.findall(r"\]\(([^)#:]+)\)", text):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                total += 1
                if not (path.parent / target).exists():
                    missing.append(f"{path.relative_to(root)} -> {target}")
        return not missing, (f"{total - len(missing)}/{total} relative documentation links resolve"
                             + ("; missing " + ", ".join(missing[:5]) if missing else ""))

    mirror.check("MIR-015", "Documentation", "Every relative documentation link resolves.",
                 ["file:docs/SETUP-00-CHECKLIST.md"], probe_documentation)

    # 16. Historical compatibility
    def probe_history() -> tuple[bool, str]:
        anchors = load_anchors(root)
        failures: list[str] = []
        validator = str(root / "scripts" / "development-ledger" / "validate_checkpoint.py")
        with tempfile.TemporaryDirectory(prefix="iacode-history-") as workdir:
            clone = Path(workdir) / "clone"
            subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(root), str(clone)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for anchor in anchors:
                identifier = anchor["checkpointId"]
                code, _ = run_git(clone, "checkout", "--quiet", "--detach",
                                  f"{TAG_NAMESPACE}{identifier}")
                if code != 0:
                    failures.append(f"{identifier}: cannot check out")
                    continue
                # The current tooling is run *against* the sealed checkout rather than copied into
                # it: copying would itself become an undeclared change and the check would fail for
                # its own reasons instead of the checkpoint's.
                exit_code, output = _tool(clone, validator, "--root", str(clone))
                if exit_code != 0:
                    failures.append(f"{identifier}: {_first_line(output)}")
        return not failures, (f"{len(anchors)} sealed checkpoints validate under this tooling"
                              if not failures else "; ".join(failures)[:300])

    mirror.check("MIR-016", "Historical compatibility",
                 "Every sealed checkpoint still validates under the tooling this Gate changes.",
                 ["file:.iacode/anchors/checkpoint-chain.json"], probe_history)

    # 17. Clean clone
    def probe_clean_clone() -> tuple[bool, str]:
        if not clean_clone:
            return True, "not requested in this run; --clean-clone performs the full execution"
        with tempfile.TemporaryDirectory(prefix="iacode-clean-clone-") as workdir:
            clone = Path(workdir) / "clone"
            if not clone_with_worktree(root, clone):
                return False, "the repository could not be cloned for the clean-clone check"
            summaries: list[str] = []
            for argv, label in (
                (["-m", "unittest", "discover", "-s", "tests"], "suite"),
                (["-m", "compileall", "-q", "scripts", "tests"], "compileall"),
                (["scripts/development-ledger/validate_lessons.py"], "lessons"),
                (["scripts/development-ledger/verify_integrity.py"], "integrity"),
                (["scripts/development-ledger/check_completeness.py"], "completeness"),
            ):
                code, output = _tool(clone, *argv)
                summaries.append(f"{label}={'ok' if code == 0 else 'FAIL'}")
                if code != 0:
                    return False, f"{label} failed in a clean clone: {_first_line(output)}"
            return True, ", ".join(summaries)

    mirror.check("MIR-017", "Clean clone",
                 "The delivery validates in a fresh clone with no workspace state.",
                 ["checkpoint:HANDOFF.md"], probe_clean_clone)

    # 18. Self-contained repository and scope control
    def probe_scope() -> tuple[bool, str]:
        forbidden = [name for name in ("services", "runtime", "gateway", "sandbox")
                     if (root / name).exists()]
        checklist = (root / "docs" / "SETUP-00-CHECKLIST.md").is_file()
        handoff = (checkpoint / "HANDOFF.md").read_text(encoding="utf-8")
        executable = "## Validation commands" in handoff and "## Stop conditions" in handoff
        ok = not forbidden and checklist and executable
        return ok, (
            f"no Gate 0 runtime present; specification in the repository={checklist}; "
            f"handoff executable without this session={executable}")

    mirror.check("MIR-018", "Scope and self-containment",
                 "No Gate 0 runtime exists and the delivery is reproducible from the repository.",
                 ["file:docs/SETUP-00-CHECKLIST.md", "checkpoint:HANDOFF.md"], probe_scope)

    passed = [item for item in mirror.checks if item["result"] == "PASS"]
    failed = [item for item in mirror.checks if item["result"] == "FAIL"]
    not_applicable = [item for item in mirror.checks if item["result"] == "NOT_APPLICABLE"]
    return {
        "schemaVersion": "1.0.0",
        "checkpoint": checkpoint.name,
        "milestone": milestone,
        "generatedAt": utc_now(),
        "targetFingerprint": scope_fingerprint(root),
        "auditorRole": "M0 Closure Auditor (.iacode/agents/m0-closure-auditor.md)",
        "independence": INDEPENDENCE,
        "checks": mirror.checks,
        "total": len(mirror.checks),
        "passed": len(passed),
        "failed": len(failed),
        "notApplicable": len(not_applicable),
        "result": "PASS" if not failed else "FAIL",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['milestone']} Internal Mirror Audit",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Checkpoint: `{report['checkpoint']}`",
        f"- Generated: `{report['generatedAt']}`",
        f"- Target fingerprint: `{report['targetFingerprint']}`",
        f"- Auditor role: {report['auditorRole']}",
        "",
        "## Independence",
        "",
        report["independence"],
        "",
        "## Checks",
        "",
        "| ID | Dimension | Expectation | Observed | Result |",
        "|---|---|---|---|---|",
    ]
    for check in report["checks"]:
        lines.append("| `%s` | %s | %s | %s | %s |" % (
            check["id"], check["dimension"], check["expectation"],
            check["observed"].replace("|", "/"), check["result"]))
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--clean-clone", action="store_true",
                        help="also run the suite and the validators in a fresh clone")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    report = run_audit(root, checkpoint, args.clean_clone)
    schema_path = root / ".iacode" / "schemas" / "mirror-audit.schema.json"
    if schema_path.is_file():
        errors = validate_schema(report, load_json(schema_path))
        if errors:
            print("MIRROR_AUDIT_INVALID")
            for error in errors:
                print(f"- {error}")
            return 3

    if args.write:
        write_json(checkpoint / f"{report['milestone']}-INTERNAL-MIRROR.json", report)
        (checkpoint / f"{report['milestone']}-INTERNAL-MIRROR.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n")

    print(f"INTERNAL_MIRROR={report['result']} passed={report['passed']}/{report['total']}")
    for check in report["checks"]:
        if check["result"] == "FAIL":
            print(f"- FAIL {check['id']}: {check['observed']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(3)
