"""Update nonterminal bookkeeping only from successful current executed assurance artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from delivery_assurance import collect_test_ids, completeness_scope, evaluate_matrix, load_command_results
from derive_counts import count_test_cases, count_unittest_cases
from ledger_common import LedgerError, load_json, scope_fingerprint, utc_now, write_json
from lessons import guardrail_effectiveness
from validate_checkpoint import _validate_green_keeper_cycle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--complete-assurance-step", action="store_true")
    args = parser.parse_args()
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    functional = load_json(CHECKPOINT / "FUNCTIONAL-SCENARIOS.json")
    fingerprint = scope_fingerprint(ROOT)
    if (verification.get("result") != "PASS" or verification.get("fast") is not False
            or any(row["result"] != "PASS" for row in verification["stages"])
            or publication.get("result") != "PASS"
            or functional["scenarios"]["experience-store-e2e.json"].get("sourceFingerprint") != fingerprint):
        raise LedgerError("actual complete unchanged verification is required")
    commands = load_command_results(CHECKPOINT)
    full = [row for row in commands.values() if row.get("exitCode") == 0
            and "audit-harness/run_full_verification.py" in row.get("command", "")
            and row.get("subjectCommit") == publication["publishedCommit"]]
    if len(full) != 1:
        raise LedgerError("exactly one current complete published invocation must resolve")
    full_command = full[0]
    full_ref = "command:" + full_command["id"]
    quality = load_json(CHECKPOINT / "QUALITY.json")
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS":
        raise LedgerError("this assembler cannot rewrite terminal or sealed status")

    def passed(dimension: str, evidence: list[str]) -> None:
        quality["checks"][dimension] = {"status": "PASS", "evidence": evidence, "justification": None}

    for dimension in ("build", "unitTests", "integrationTests", "e2e", "lint", "staticAnalysis", "security"):
        passed(dimension, ["file:VERIFY.json", "file:PUBLISHED-CLEAN-CLONE-REPORT.json", full_ref])
    documentation = load_json(CHECKPOINT / "DOCUMENTATION-LINKS.json")
    if documentation.get("result") == "PASS" and documentation.get("scopeFingerprint") == fingerprint:
        passed("documentation", ["file:DOCUMENTATION-LINKS.json", full_ref])
    root_cases, all_cases = count_unittest_cases(ROOT, "tests"), count_test_cases(ROOT)
    run_label = "published-" + publication["publishedCommit"][:12]
    tests = {"schemaVersion": state["schemaVersion"],
        "unit": {"executed": True, "passed": root_cases, "failed": 0,
                 "command": full_command["command"], "evidence": full_ref,
                 "runId": run_label + "-root-suite"},
        "integration": {"executed": True, "passed": all_cases - root_cases, "failed": 0,
                        "command": full_command["command"], "evidence": full_ref,
                        "runId": run_label + "-counted-runtime-suites"},
        "e2e": {"executed": True, "passed": len(verification["stages"]), "failed": 0,
                "command": full_command["command"], "evidence": full_ref,
                "runId": run_label + "-counted-runtime-suites"}}
    cycles = [json.loads(line) for line in (CHECKPOINT / "REWORK-LOG.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    green = False
    if cycles and cycles[-1].get("result") == "GREEN":
        cycle = cycles[-1]
        errors: list[str] = []
        _validate_green_keeper_cycle(ROOT, {}, cycle, errors, closure=True)
        if errors:
            raise LedgerError("actual Green Keeper is not current: " + str(errors))
        if any(commands.get(identifier, {}).get("exitCode") != 0 for identifier in cycle["commandsExecuted"]):
            raise LedgerError("a recorded mandatory Green Keeper invocation did not succeed")
        references = ["command:" + identifier for identifier in cycle["commandsExecuted"]]
        state["greenKeeper"].update({"status": "PASS", "cycles": len(cycles),
            "remainingFailures": 0, "unresolvedReworkItems": 0, "externalBlockers": [],
            "evidence": references, "requiredGates": cycle["requiredGates"],
            "scopeFingerprint": fingerprint})
        state["reworkCycles"] = len(cycles)
        passed("greenKeeper", ["file:REWORK-LOG.jsonl", *references])
        checkpoint_execution = next(row for row in cycle["gateResults"] if row["gate"] == "checkpointValidation")
        passed("checkpointValidation", ["command:" + checkpoint_execution["commandId"]])
        root_execution = next(row for row in cycle["gateResults"] if row["gate"] == "tests")
        root_record = commands[root_execution["commandId"]]
        tests["unit"].update({"command": root_record["command"], "evidence": "command:" + root_record["id"],
                               "runId": "green-keeper-cycle-" + str(cycle["cycle"]) + "-root-suite"})
        green = True
    complete = False
    path = CHECKPOINT / "COMPLETENESS-REPORT.json"
    if path.is_file():
        report = load_json(path)
        if (report.get("result") != "PASS" or report.get("scopeFingerprint") !=
                scope_fingerprint(ROOT, completeness_scope(ROOT, CHECKPOINT))):
            raise LedgerError("completeness is not green")
        state["deliveryCompleteness"].update({"status": "PASS", "coveragePercent": report["coveragePercent"],
            "evidenceCoveragePercent": report["evidenceCoveragePercent"],
            "auditor": "same-session Delivery Completeness Validator; audit only; no independent M2 verdict",
            "evidence": ["checkpoint:COMPLETENESS-REPORT.json"]})
        passed("deliveryCompleteness", ["file:COMPLETENESS-REPORT.json"])
        complete = True
    attacked = False
    path = CHECKPOINT / "M2-INTERNAL-RED-TEAM.json"
    if path.is_file():
        report = load_json(path)
        if (report.get("result") != "RED_TEAM_PASS" or report.get("targetFingerprint") != fingerprint
                or report.get("baselineControl", {}).get("result") != "VALID"):
            raise LedgerError("actual internal Red Team is not current and green")
        passed("redTeam", ["file:M2-INTERNAL-RED-TEAM.json", "file:RED-TEAM-EXECUTIONS.json", "file:RED-TEAM-EXPERIENCE.json"])
        attacked = True
    if args.complete_assurance_step:
        mirror = load_json(CHECKPOINT / "M2-INTERNAL-MIRROR.json")
        if (not green or not complete or not attacked or mirror.get("result") != "PASS"
                or mirror.get("targetFingerprint") != fingerprint):
            raise LedgerError("all ordered actual assurance reports must pass before completing G6-S02")
        steps = load_json(CHECKPOINT / "STEPS.json")
        for step in steps["steps"]:
            if step["stepId"] == "G6-S02":
                step.update({"status": "COMPLETE", "functionalProof": "Complete published non-fast verifier, full mandatory Green Keeper, completeness, fresh internal Red Team/null control and full closure mirror actually pass against unchanged source. Same-session only.",
                             "evidence": [full_command["id"], "M2-INTERNAL-MIRROR.json", "M2-INTERNAL-RED-TEAM.json", "COMPLETENESS-REPORT.json", "REWORK-LOG.jsonl"]})
            if step["stepId"] == "G6-S03":
                step["status"] = "IN_PROGRESS"
        write_json(CHECKPOINT / "STEPS.json", steps)
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    summary = evaluate_matrix(ROOT, CHECKPOINT, matrix, commands, collect_test_ids(ROOT))
    rows = matrix["requirements"]
    state["requirementsMatrix"] = {"path": "REQUIREMENTS-MATRIX.json", "total": len(rows),
        "mandatory": sum(bool(row["mandatory"]) for row in rows),
        "complete": sum(row["status"] == "COMPLETE" for row in rows),
        "partial": sum(row["status"] == "PARTIAL" for row in rows),
        "missing": sum(row["status"] == "MISSING" for row in rows),
        "notApplicable": sum(row["status"] == "NOT_APPLICABLE" for row in rows),
        "coveragePercent": summary["coveragePercent"]}
    effectiveness = guardrail_effectiveness(ROOT)
    state["guardrailEffectiveness"] = {name: effectiveness[name] for name in (
        "guardrailsTotal", "guardrailsResolved", "guardrailsTested", "guardrailsEffective", "guardrailFailures")}
    state["guardrailEffectiveness"]["evidence"] = [full_ref, "checkpoint:VERIFY.json"]
    state["dirty"] = True
    state["updatedAt"] = utc_now()
    state["nextAllowedAction"] = "Complete only the next ordered Gate 6 assurance/handoff/seal step; independent M2 validation remains pending and Gate 7 is not authorized."
    write_json(CHECKPOINT / "TESTS.json", tests)
    write_json(CHECKPOINT / "QUALITY.json", quality)
    write_json(CHECKPOINT / "STATE.json", state)
    print(f"VERIFIED_PROGRESS_RECORDED tests={all_cases} green={green} complete={complete} attacked={attacked} status=IN_PROGRESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
