#!/usr/bin/env python3
"""The internal, non-implementing audit of SETUP-00-CP-0012.

This is the last control the delivery runs on itself, after the Green Keeper, the completeness audit,
the internal Red Team and the mirror audit are all green. It re-derives what the delivery claims,
from the repository and from the artifacts the tools produced, and records what it observed.

It is **internal quality assurance**. It runs on the same tooling, in the same session, and its
verdict may never be recorded as independent validation, as ``secondToolValidation``, as
``milestone.status = PASSED`` or as a milestone pass of any kind. Only an audit checkpoint authored
by a separate run, about a sealed subject, carries a milestone verdict.

The auditor never repairs. Every row it fails returns to the implementer.

    python docs/checkpoints/SETUP-00-CP-0012/audit-harness/final_internal_audit.py --write
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

HARNESS = Path(__file__).resolve().parent
CHECKPOINT = HARNESS.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from anchors import TAG_NAMESPACE, load_anchors, resolve_tag, verify_chain  # noqa: E402
from delivery_assurance import evaluate_matrix  # noqa: E402
from lessons import guardrail_effectiveness, load_lessons  # noqa: E402
from policies import audit_applicability, parse_findings  # noqa: E402

INDEPENDENCE = (
    "Internal quality assurance. This audit is authored by the implementing run, on the same "
    "tooling, in the same session. It is not independent validation and may not be recorded as "
    "one; only an audit checkpoint authored by a separate run about a sealed subject carries a "
    "milestone verdict."
)


def read(name: str) -> Any:
    return json.loads((CHECKPOINT / name).read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, check=False)
    return completed.stdout.strip()


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, identifier: str, question: str, how: str,
              probe: Callable[[], tuple[bool, str]]) -> None:
        try:
            ok, observed = probe()
        except Exception as exc:  # an auditor that crashes has found something
            ok, observed = False, f"the check itself failed: {exc}"
        self.rows.append({
            "id": identifier,
            "question": question,
            "howItWasEstablished": how,
            "observed": observed,
            "result": "PASS" if ok else "FAIL",
        })
        print(f"[{identifier}] {'PASS' if ok else 'FAIL'} {observed}")


def run() -> dict[str, Any]:
    audit = Audit()
    mirror = read("M0-INTERNAL-MIRROR.json")
    red_team = read("M0-INTERNAL-RED-TEAM.json")
    semantics = read("MIRROR-SEMANTICS-VALIDATION.json")
    transition = read("GATE0-TRANSITION-SIMULATION.json")
    promotion = read("POSITIVE-PROMOTION-VALIDATION.json")
    successor = read("SUCCESSOR-DURABILITY.json")
    closure = read("CP11-FINDINGS-CLOSURE.json")
    state = read("STATE.json")
    counts = read("COUNTS.json")

    def semantics_check(identifier: str) -> dict[str, Any]:
        return next(item for item in semantics["checks"] if item["id"] == identifier)

    def probe_finding_closed() -> tuple[bool, str]:
        sealed = (ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0011"
                  / "REVIEW-REPORT.md").read_text(encoding="utf-8")
        raised = [item["id"] for item in parse_findings(sealed)]
        recorded = {str(row["findingId"]): row["status"] for row in closure["findings"]}
        unclosed = [item for item in raised if recorded.get(item) != "CLOSED"]
        extra = [item for item in recorded if item not in raised]
        ok = bool(raised) and not unclosed and not extra
        return ok, (f"the sealed review raises {', '.join(raised)}; the closure record marks "
                    + ", ".join(f"{key}={value}" for key, value in sorted(recorded.items()))
                    + ("; unclosed " + ", ".join(unclosed) if unclosed else "")
                    + ("; not raised by that audit " + ", ".join(extra) if extra else ""))

    audit.check(
        "FIA-001", "Is CP11-F-001 closed, against the sealed report rather than against the record?",
        "The finding set was re-parsed from docs/checkpoints/SETUP-00-CP-0011/REVIEW-REPORT.md and "
        "compared with CP11-FINDINGS-CLOSURE.json.", probe_finding_closed)

    def probe_mirror_executed() -> tuple[bool, str]:
        import m0_mirror_audit

        identifiers = [item["id"] for item in mirror["checks"]]
        ok = (mirror["independence"] == m0_mirror_audit.INDEPENDENCE
              and "m0-closure-auditor.md" in mirror["auditorRole"]
              and "MIR-001" in identifiers and "MIR-018" in identifiers
              and len(identifiers) == len(set(identifiers)))
        return ok, (f"{len(identifiers)} dimensions, independence text identical to the tool's own, "
                    f"auditor role {mirror['auditorRole']!r}")

    audit.check(
        "FIA-002", "Was the internal mirror produced by the tool rather than written by hand?",
        "The sealed artifact was compared by content with the module's own constants and its "
        "complete dimension set.", probe_mirror_executed)

    def probe_zero_set() -> tuple[bool, str]:
        check = semantics_check("MSV-001")
        findings_check = check["findingsCheck"]
        ok = (check["result"] == "PASS"
              and findings_check["result"] == "NOT_APPLICABLE"
              and findings_check["expectedCount"] == 0
              and bool((findings_check.get("reason") or "").strip())
              and bool((findings_check.get("derivationSource") or "").strip()))
        return ok, f"{check['observed']}; reason recorded: {bool(findings_check.get('reason'))}"

    audit.check(
        "FIA-003", "Does an empty applicable set report NOT_APPLICABLE with a justification?",
        "MIRROR-SEMANTICS-VALIDATION.json MSV-001, produced by executing m0_mirror_audit.py.",
        probe_zero_set)

    def probe_missing_required() -> tuple[bool, str]:
        check = semantics_check("MSV-004")
        ok = check["result"] == "PASS" and check["findingsCheck"]["result"] == "FAIL"
        return ok, check["findingsCheck"]["observed"]

    audit.check(
        "FIA-004", "Does a missing required set fail instead of being inapplicable?",
        "MIRROR-SEMANTICS-VALIDATION.json MSV-004.", probe_missing_required)

    def probe_open_required() -> tuple[bool, str]:
        check = semantics_check("MSV-003")
        ok = (check["result"] == "PASS" and check["findingsCheck"]["result"] == "FAIL"
              and "sealed=False" in check["observed"])
        return ok, check["observed"]

    audit.check(
        "FIA-005", "Does an open applicable finding fail and block the seal?",
        "MIRROR-SEMANTICS-VALIDATION.json MSV-003.", probe_open_required)

    def probe_closed_required() -> tuple[bool, str]:
        check = semantics_check("MSV-002")
        ok = (check["result"] == "PASS" and check["findingsCheck"]["result"] == "PASS"
              and check["attacksCheck"]["result"] == "PASS")
        return ok, check["observed"]

    audit.check(
        "FIA-006", "Does a satisfied applicable set pass?",
        "MIRROR-SEMANTICS-VALIDATION.json MSV-002.", probe_closed_required)

    def probe_forged_empty() -> tuple[bool, str]:
        check = semantics_check("MSV-005")
        ok = (check["result"] == "PASS"
              and check["findingsCheck"]["result"] == "FAIL")
        return ok, check["findingsCheck"]["observed"]

    audit.check(
        "FIA-007", "Can a delivery declare its own applicable set empty?",
        "MIRROR-SEMANTICS-VALIDATION.json MSV-005, and the validator rule the battery attacks as "
        "BG.", probe_forged_empty)

    def probe_overall() -> tuple[bool, str]:
        inapplicable = [item for item in mirror["checks"] if item["result"] == "NOT_APPLICABLE"]
        passed = [item for item in mirror["checks"] if item["result"] == "PASS"]
        failed = [item for item in mirror["checks"] if item["result"] == "FAIL"]
        ok = (mirror["result"] == "PASS" and not failed
              and mirror["passed"] == len(passed)
              and mirror["notApplicable"] == len(inapplicable)
              and mirror["total"] == len(mirror["checks"])
              and len(passed) + len(failed) + len(inapplicable) == mirror["total"])
        return ok, (f"{mirror['result']}: {mirror['passed']} passed, {mirror['failed']} failed, "
                    f"{mirror['notApplicable']} inapplicable of {mirror['total']}")

    audit.check(
        "FIA-008", "Does the overall verdict handle NOT_APPLICABLE without rewriting it?",
        "The counts of M0-INTERNAL-MIRROR.json were recomputed from its own rows.", probe_overall)

    def probe_promotion() -> tuple[bool, str]:
        executed = [
            entry["internalMirror"]
            for entry in (promotion.get("artifactProvenance") or {}).values()]
        ok = (promotion["result"] == "PASS" and promotion["milestoneVerdict"] == "PASSED"
              and bool(executed)
              and all(item["producedBy"] == "execution" and item["exitCode"] == 0
                      for item in executed))
        return ok, (f"{promotion['result']}, verdict {promotion['milestoneVerdict']}, "
                    f"{len(executed)} mirror(s) produced by execution")

    audit.check(
        "FIA-009", "Does the positive milestone promotion still work, with the mirror executed?",
        "POSITIVE-PROMOTION-VALIDATION.json, produced by running the simulation.", probe_promotion)

    def probe_successor() -> tuple[bool, str]:
        return successor["result"] == "PASS", (
            f"{successor['result']}, {successor['passed']}/{successor['total']} checks")

    audit.check(
        "FIA-010", "Does successor durability still hold?",
        "SUCCESSOR-DURABILITY.json, produced by running the simulation.", probe_successor)

    def probe_transition() -> tuple[bool, str]:
        ok = (transition["result"] == "PASS"
              and transition["statusReached"] == "READY_FOR_REVIEW"
              and transition["mirror"]["result"] == "PASS"
              and transition["mirror"]["producedBy"] == "execution"
              and bool(transition["mirror"]["inapplicable"]))
        return ok, (f"{transition['checkpoint']} reached {transition['statusReached']}; mirror "
                    f"{transition['mirror']['result']} with "
                    f"{transition['mirror']['notApplicable']} inapplicable")

    audit.check(
        "FIA-011", "Can the first delivery of the next Gate reach READY_FOR_REVIEW?",
        "GATE0-TRANSITION-SIMULATION.json, produced by executing the transition in a disposable "
        "repository.", probe_transition)

    def probe_history() -> tuple[bool, str]:
        history = next((item for item in mirror["checks"] if item["id"] == "MIR-016"), None)
        anchors = load_anchors(ROOT)
        moved = [item["checkpointId"] for item in anchors
                 if resolve_tag(ROOT, f"{TAG_NAMESPACE}{item['checkpointId']}") != item["commit"]]
        chain = verify_chain(ROOT, require_sealed=True, exclude={CHECKPOINT.name})
        ok = (history is not None and history["result"] == "PASS" and not moved and not chain)
        return ok, (f"{len(anchors)} anchors, none moved, chain verifies; "
                    f"{history['observed'] if history else 'MIR-016 absent'}")

    audit.check(
        "FIA-012", "Do the sealed checkpoints still validate under this tooling?",
        "MIR-016 of the mirror audit, plus an independent re-derivation of every anchor from Git.",
        probe_history)

    def probe_clean_clone() -> tuple[bool, str]:
        clone = next((item for item in mirror["checks"] if item["id"] == "MIR-017"), None)
        ok = clone is not None and clone["result"] == "PASS" and "not requested" not in clone["observed"]
        return ok, (clone["observed"] if clone else "MIR-017 absent")

    audit.check(
        "FIA-013", "Does the delivery validate in a clean clone with no workspace state?",
        "MIR-017 of the mirror audit, executed with --clean-clone.", probe_clean_clone)

    def probe_language_policy() -> tuple[bool, str]:
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        required = ("Brazilian Portuguese", "progress updates", "final reports",
                    "never switches", "stay literal")
        missing = [item for item in required if item not in text]
        return not missing, ("CLAUDE.md records the language rule"
                             if not missing else "missing: " + ", ".join(missing))

    audit.check(
        "FIA-014", "Does the canonical Claude adapter record the language rule?",
        "CLAUDE.md was read and the required statements located.", probe_language_policy)

    def probe_memory() -> tuple[bool, str]:
        lessons = {item["lessonId"]: item for item in load_lessons(ROOT)}
        measured = guardrail_effectiveness(ROOT)
        new = lessons.get("LSN-0031")
        failures = {
            identifier: [entry for entry in lessons[identifier]["guardrailFailures"]
                         if entry.get("checkpoint") == "SETUP-00-CP-0011"]
            for identifier in ("LSN-0024", "LSN-0029") if identifier in lessons}
        recorded = all(bool(value) for value in failures.values())
        resolved = all(entry.get("resolvedIn") == CHECKPOINT.name
                       for value in failures.values() for entry in value)
        ok = (new is not None and new["status"] == "GUARDED" and bool(new["guardrails"])
              and recorded and resolved
              and measured["guardrailFailures"] == 0
              and measured["guardrailsEffective"] == measured["guardrailsTotal"])
        return ok, (f"LSN-0031 {new['status'] if new else 'absent'}; the recurrence is recorded "
                    f"against {', '.join(sorted(failures))} and resolved in {CHECKPOINT.name}; "
                    f"{measured['guardrailsEffective']}/{measured['guardrailsTotal']} guardrails "
                    f"effective, {measured['guardrailFailures']} unresolved failures")

    audit.check(
        "FIA-015", "Is the recurrence recorded as a guardrail failure and resolved by a control?",
        "The engineering memory was read and the effectiveness measured, not assumed.", probe_memory)

    def probe_battery() -> tuple[bool, str]:
        applicable = audit_applicability(ROOT, str(state.get("gate")), CHECKPOINT.name)
        expected = {item["id"] for item in applicable["mandatoryAttacks"]}
        executed = {str(item["attackId"]) for item in red_team["attacks"]
                    if item["result"] == "DEFENDED"}
        missing = sorted(expected - executed)
        ok = (red_team["result"] == "RED_TEAM_PASS" and red_team["escaped"] == 0
              and not missing
              and (red_team.get("baselineControl") or {}).get("result") == "VALID")
        return ok, (f"{red_team['result']}, {red_team['defended']}/{red_team['total']} defended, "
                    f"control {(red_team.get('baselineControl') or {}).get('result')}"
                    + ("; not executed: " + ", ".join(missing) if missing else ""))

    audit.check(
        "FIA-016", "Was every mandatory attack of the registered audits defended?",
        "The expected battery was re-derived from the audit registry and the sealed reports, then "
        "compared with M0-INTERNAL-RED-TEAM.json.", probe_battery)

    def probe_completeness() -> tuple[bool, str]:
        matrix = read("REQUIREMENTS-MATRIX.json")
        recomputed = evaluate_matrix(ROOT, CHECKPOINT, matrix)
        ok = (recomputed["result"] == "PASS"
              and recomputed["coveragePercent"] == 100.0
              and recomputed["evidenceCoveragePercent"] == 100.0
              and recomputed["partial"] == 0 and recomputed["missing"] == 0
              and recomputed["anchoredRequirements"] == recomputed["expectedRequirements"])
        return ok, (f"{recomputed['result']}: {recomputed['complete']} complete of "
                    f"{recomputed['totalRequirements']}, {recomputed['anchoredRequirements']} "
                    f"anchored against an expected set of {recomputed['expectedRequirements']}, "
                    f"coverage {recomputed['coveragePercent']:.2f}, evidence "
                    f"{recomputed['evidenceCoveragePercent']:.2f}")

    audit.check(
        "FIA-017", "Is the delivery complete against an independently recomputed expected set?",
        "evaluate_matrix was re-run here rather than the stored report being read.",
        probe_completeness)

    def probe_counts() -> tuple[bool, str]:
        from derive_counts import derive_counts

        derived = derive_counts(ROOT, CHECKPOINT)
        mismatched = [
            key for key, value in derived.items()
            if (counts["counts"].get(key, {}).get("numerator"),
                counts["counts"].get(key, {}).get("denominator"))
            != (value["numerator"], value["denominator"])]
        return not mismatched, ("; ".join(
            f"{key}={value['numerator']}/{value['denominator']}"
            for key, value in sorted(derived.items()))
            + ("; mismatched " + ", ".join(mismatched) if mismatched else ""))

    audit.check(
        "FIA-018", "Does every count used as evidence match its derivation?",
        "The counts were re-derived here and compared with COUNTS.json.", probe_counts)

    def probe_status() -> tuple[bool, str]:
        ok = (state["status"] == "READY_FOR_REVIEW"
              and state["blockedBy"] == []
              and state["independentReview"]["status"] == "PENDING"
              and state["redTeam"]["status"] == "PENDING"
              and state["secondToolValidation"]["status"] == "PENDING_MANUAL"
              and (state.get("milestone") or {}).get("status") == "PENDING"
              and (state.get("externalAttestation") or {}).get("status") == "NONE")
        return ok, (f"status {state['status']}, blockedBy {state['blockedBy']}, review "
                    f"{state['independentReview']['status']}, red team "
                    f"{state['redTeam']['status']}, milestone "
                    f"{(state.get('milestone') or {}).get('status')}")

    audit.check(
        "FIA-019", "Does the implementing run refrain from granting itself any independent verdict?",
        "STATE.json was read and every verdict field checked.", probe_status)

    def probe_scope() -> tuple[bool, str]:
        forbidden = [name for name in ("services", "runtime", "gateway", "sandbox")
                     if (ROOT / name).exists()]
        gate_zero = [item.name for item in (ROOT / "docs" / "checkpoints").iterdir()
                     if item.is_dir() and not item.name.startswith("SETUP-00-")]
        changed = _git("diff", "--name-only", state["baseCommit"]).splitlines()
        sealed_touched = [
            path for path in changed
            if path.startswith("docs/checkpoints/SETUP-00-CP-") and CHECKPOINT.name not in path]
        ok = not forbidden and not gate_zero and not sealed_touched
        return ok, (f"no Gate 0 runtime; no Gate 0 checkpoint; {len(sealed_touched)} sealed "
                    f"checkpoint files touched")

    audit.check(
        "FIA-020", "Was the scope respected: no Gate 0 work and no sealed checkpoint rewritten?",
        "The repository tree and the change set against the base commit were inspected.",
        probe_scope)

    failed = [item for item in audit.rows if item["result"] != "PASS"]
    return {
        "schemaVersion": "1.0.0",
        "checkpoint": CHECKPOINT.name,
        "generatedAt": _git("log", "-1", "--format=%cI") or "",
        "auditorRole": "internal, non-implementing audit pass of the corrective delivery",
        "independence": INDEPENDENCE,
        "subject": CHECKPOINT.name,
        "checks": audit.rows,
        "total": len(audit.rows),
        "passed": len(audit.rows) - len(failed),
        "failed": len(failed),
        "result": "PASS" if not failed else "FAIL",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Final Internal Audit",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Subject: `{report['subject']}`",
        f"- Auditor role: {report['auditorRole']}",
        "",
        "## Independence",
        "",
        report["independence"],
        "",
        "## What was asked, and how the answer was established",
        "",
        "| Check | Question | How | Observed | Result |",
        "|---|---|---|---|---|",
    ]
    for row in report["checks"]:
        lines.append("| `%s` | %s | %s | %s | `%s` |" % (
            row["id"], row["question"].replace("|", "/"),
            row["howItWasEstablished"].replace("|", "/"),
            str(row["observed"]).replace("|", "/"), row["result"]))
    lines += ["", f"Passed: `{report['passed']}` of `{report['total']}` checks."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = run()
    if args.write:
        (CHECKPOINT / "FINAL-INTERNAL-AUDIT.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")
        (CHECKPOINT / "FINAL-INTERNAL-AUDIT.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"FINAL_INTERNAL_AUDIT={report['result']} "
              f"checks={report['passed']}/{report['total']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
