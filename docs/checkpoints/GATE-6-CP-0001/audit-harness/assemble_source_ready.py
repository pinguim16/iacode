"""Record completed local implementation controls; immutable assurance remains a separate step."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, use_utf8_stdout, write_json
from lessons import guardrail_effectiveness
from sync_in_progress_metadata import synchronize
from validate_checkpoint import HANDOFF_HEADINGS


def local_handoff_sections() -> dict[str, str]:
    state = load_json(CHECKPOINT / "STATE.json")
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    open_ids = [row["findingId"] for row in findings["findings"] if row["status"] != "CLOSED"]
    return {
        "## Objective": "Finish only authorized Gate6 Experience Store and every internal control through canonical seal. Independent M2 remains pending; Gate7 is not authorized.",
        "## What was completed": "Entry/baseline/architecture and complete local causal implementation acceptance: lint, domain29, API173, client35, actual SQL/HTTP/migrations36 and fresh provider/sandbox/Quality lifecycle72 with owned cleanup. See cmd-0050/0054 and original producer receipts.",
        "## What was NOT completed": "Immutable published non-fast verification, whole Green Keeper, completeness, fresh internal Red Team/null control, full clean-clone mirror, final assembly and actual Gate6 seal/publication/archive reconstruction remain pending.",
        "## Current repository state": "Attached branch " + state["branch"] + "; current binding and dirty state are owned by STATE.json. The predecessor base is " + state["baseCommit"] + ". No unexpected divergence was observed.",
        "## Files changed": "FILES.json declares the actual Gate6 delta. Every later path must be explicitly declared before finalization; hash refresh may not invent a declaration or rewrite a sealed predecessor.",
        "## Important decisions": "ADR-0050 defines source-bound explicit-consent facts and pure ports; ADR-0051 defines finite retention/tombstones. All canonical criteria and selected lessons remain mandatory according to policy; all37 runtime criteria require functional evidence.",
        "## Tests executed": "Actual completed local invocations cmd-0050 and cmd-0054 cover the suites/runtime above; cmd-0109 proves root23 including canonical retrospective conformance. Suite-attempts and attempts retain exact safe output. These are local causal proofs, not a complete immutable Gate verdict. TESTS.json names distinct physical runs.",
        "## Known failures": "All original failures and escalated counters remain in FINDINGS/engineering memory. Currently open findings: " + (", ".join(open_ids) or "none") + ". INTEGRATION-0003's false identity flag has unproven cause; INTEGRATION-0004 observes every original identity preserved.",
        "## Known risks": "RISKS.md records security/rights/backup/retention, external provider and same-session assurance limits. Unknown reuse permission is denial; no independent M2 approval is implied.",
        "## Do not repeat": "Never overlap ledger/inventory/validation writers or treat a process session ID as completion. Preserve original failures and all denominators. Never retry the three predecessor policy-refused temporary cleanup targets, global profiles or operational storage.",
        "## Required next action": state["nextAllowedAction"],
        "## Exact continuation sequence": "Inspect STATE/PLAN/STEPS/COMMANDS and active processes; finish any named causal rework, freeze/publish the tested Gate6-only runtime, complete full immutable verification and ordered internal assurance, assemble/finalize/content-commit/seal/publish and verify fresh exact transport/archive. Do not start Gate7.",
        "## Validation commands": "python scripts/development-ledger/validate_checkpoint.py; python scripts/development-ledger/validate_lessons.py; python scripts/development-ledger/verify_integrity.py; python scripts/development-ledger/program_state.py. Use the current serial bookkeeping harness before unsealed validation and await its actual exit.",
        "## Stop conditions": "Stop for unexpected Git divergence or a genuine missing external prerequisite/authority. Ordinary failures require retained causal rework, never false PASS. No force, reset, amend, tag movement or independent self-approval is authorized.",
    }


def render_handoff(sections: dict[str, str]) -> str:
    if set(sections) != set(HANDOFF_HEADINGS):
        raise ValueError("the complete canonical handoff section set is required")
    if any(not isinstance(value, str) or len(value.strip()) < 20 for value in sections.values()):
        raise ValueError("every canonical handoff section needs substantive content")
    return "# Handoff\n\nCurrent Gate: GATE-6\nCurrent Status: IN_PROGRESS\n\n" + "\n\n".join(
        heading + "\n\n" + sections[heading] for heading in HANDOFF_HEADINGS) + "\n"


def render_next(action: str) -> str:
    if len(action.strip()) < 20:
        raise ValueError("a substantive next action is required")
    return "# Next\n\n## Required next action\n\n" + action + "\n"


def main() -> int:
    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS" or (CHECKPOINT / "CHECKSUMS.sha256").exists():
        raise ValueError("an unsealed current implementing checkpoint is required")
    progress = load_json(CHECKPOINT / "PRE-LIVE-PROGRESS.json")
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    if progress["status"] != "PASS" or any(row["status"] != "CLOSED" for row in findings["findings"]):
        raise ValueError("local causal execution and guard restoration must actually finish first")
    commands = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    sequence = [row for row in commands if row.get("exitCode") == 0
                and "audit-harness/run_pre_live_sequence.py" in row["command"]][-1]
    tests = load_json(CHECKPOINT / "TESTS.json")
    for category, suite in (("unit", "API-UNIT"), ("integration", "INTEGRATION")):
        path = sorted((CHECKPOINT / "suite-attempts").glob(suite + "-*.json"))[-1]
        report = load_json(path)
        if report["result"] != "PASS":
            raise ValueError("complete local actual suite missing")
        fragments = report.get("summaryFragments") or report["commands"][-1]["summaryFragments"]
        passed = [int(value.split()[0]) for value in fragments if value.endswith(" passed")]
        if len(passed) != 1:
            raise ValueError("one actual pytest passed count must resolve")
        tests[category] = {"executed": True, "passed": passed[0], "failed": 0,
            "command": sequence["command"] if category == "unit" else next(
                row["command"] for row in commands if row["id"] == "cmd-0050"),
            "evidence": "file:" + path.relative_to(ROOT).as_posix(),
            "runId": CHECKPOINT.name + "-local-" + path.stem.lower()}
    receipt_path = sorted((CHECKPOINT / "attempts").glob("EXPERIENCE-LIVE-*-RECEIPT.json"))[-1]
    receipt = load_json(receipt_path)
    if receipt["result"] != "PASS":
        raise ValueError("real completed experience lifecycle required")
    tests["e2e"] = {"executed": True, "passed": 1, "failed": 0,
        "command": sequence["command"], "evidence": "file:" + receipt["producerArchive"],
        "runId": CHECKPOINT.name + "-local-" + receipt_path.stem.lower()}
    write_json(CHECKPOINT / "TESTS.json", tests)
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    for row in matrix["requirements"]:
        if row["sourceRef"].startswith("canonical:GATE-6#"):
            section = int(row["sourceRef"].partition("#")[2].partition(".")[0])
            if 2 <= section <= 7:
                row.update({"status": "PARTIAL", "notes": "Complete causal local source implementation and actual live lifecycle pass; acceptance against the final immutable subject and ordered assurance remain pending.",
                    "implementationEvidence": ["file:apps/api/src/iacode_api/experience/sources.py",
                                               "file:services/experience/src/iacode_experience/domain.py"],
                    "testEvidence": ["command:" + sequence["id"], "command:cmd-0050"],
                    "documentationEvidence": ["file:docs/runbooks/experience-store.md"],
                    "validationEvidence": []})
    write_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json", matrix)
    state = load_json(CHECKPOINT / "STATE.json")
    rows = matrix["requirements"]
    complete = sum(row["status"] == "COMPLETE" for row in rows)
    state["requirementsMatrix"].update({"total": len(rows), "mandatory": sum(row["mandatory"] for row in rows),
        "complete": complete, "partial": sum(row["status"] == "PARTIAL" for row in rows),
        "missing": 0, "notApplicable": 0, "coveragePercent": round(100 * complete / len(rows), 2)})
    measured = guardrail_effectiveness(ROOT)
    state["guardrailEffectiveness"] = {key: measured[key] for key in (
        "guardrailsTotal", "guardrailsResolved", "guardrailsTested", "guardrailsEffective", "guardrailFailures")}
    state["guardrailEffectiveness"]["evidence"] = ["command:" + sequence["id"], "command:cmd-0050"]
    state["lessonPreflight"]["evidence"] = ["checkpoint:LESSON-PREFLIGHT.json", "checkpoint:REQUIREMENTS-MATRIX.json"]
    state["updatedAt"] = utc_now()
    state["nextAllowedAction"] = "Freeze and publish a tested Gate6-only runtime subject, execute complete immutable verification and every ordered internal control, then canonically seal. Independent M2 remains pending; Gate7 is not authorized."
    write_json(CHECKPOINT / "STATE.json", state)
    steps = load_json(CHECKPOINT / "STEPS.json")
    steps["steps"][1].update({"status": "COMPLETE",
        "functionalProof": "Complete unchanged lint, domain29/API173/client35, actual SQL/HTTP/migrations36, Gate6 root controls and fresh real experience lifecycle pass. All retained runtime and metadata findings close only after actual causal controls and canonical acceptance; later root23 includes complete positive/adverse continuation rendering and canonical retrospective conformance. This completes implementation, not whole-Gate acceptance.",
        "evidence": [sequence["id"], "cmd-0050", "cmd-0109", "FINDINGS.json", receipt_path.relative_to(CHECKPOINT).as_posix()]})
    steps["steps"][2]["status"] = "IN_PROGRESS"
    write_json(CHECKPOINT / "STEPS.json", steps)
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    plan_path = CHECKPOINT / "PLAN.md"
    marker = "\n<!-- BEGIN DERIVED LESSON COMMITMENTS -->\n"
    plan = plan_path.read_text(encoding="utf-8").split(marker, 1)[0].rstrip()
    commitments = []
    for row in preflight["applicable"]:
        commitments.extend(["", "### " + row["derivedRequirementId"] + " — " + row["lessonId"], "",
                            "- Required check: " + row["requiredCheck"],
                            "- Required evidence: " + row["requiredEvidence"]])
    plan_path.write_text(plan + marker + "\n".join(commitments) + "\n", encoding="utf-8", newline="\n")
    provenance = load_json(CHECKPOINT / "PROVENANCE.json")
    if len(provenance["artifacts"]) == 1:
        provenance["artifacts"].append({
            "artifact": "services/experience; packages/contracts; apps/api; scripts/iacode; tests and Gate6 documentation",
            "sourceType": "AI-assisted repository implementation and locally generated test/proof artifacts",
            "provider": "OpenAI / actual local owning toolchains", "model": "not-exposed",
            "ownership": "project-generated engineering work", "license": "project-policy",
            "rights": {"storageAllowed": True, "ragAllowed": False, "trainingAllowed": False, "distillationAllowed": False},
            "evidence": "FILES.json, COMMANDS.jsonl, suite-attempts and exact attempts producer receipts",
            "notes": "No raw provider exchange or private reasoning retained. Actual run/provider metadata is operational evidence, not proof of source ownership or a reuse license."})
    write_json(CHECKPOINT / "PROVENANCE.json", provenance)
    text = """# Gate 6 progress

Implementation and causal local acceptance are complete. The runtime captures only consented
source-bound observable facts, with closed contracts, immutable SQL/audit, bounded source queries,
authenticated project-scoped API, denied unproven reuse, finite retention and anti-resurrection.

The actual fresh provider/sandbox/Quality lifecycle passes, including response loss, concurrency,
restart, corrupt/missing evidence, withdrawal, real-clock expiry, automatic physical purge and
owned cleanup. The whole current local lint, domain/API/client/root controls and actual SQL/HTTP/
migrations pass. Exact original failures and producer bytes remain available in this checkpoint.

The current derived set contains all 51 canonical criteria plus every selected lesson; functional
acceptance must cover all 37 runtime criteria. Causal guard restoration is not a Gate verdict.

Next: complete immutable published non-fast verification, whole Green Keeper, completeness,
fresh same-session internal Red Team/null control, full clean-clone mirror, final assembly and
canonical seal/publication/archive reconstruction. No future test or seal is claimed complete.
Independent M2 and second-tool validation remain pending. Gate7 is not authorized.
"""
    (CHECKPOINT / "PROGRESS.md").write_text(text, encoding="utf-8", newline="\n")
    (CHECKPOINT / "NEXT.md").write_text(render_next(state["nextAllowedAction"]), encoding="utf-8", newline="\n")
    (CHECKPOINT / "STATUS.md").write_text("# Status\n\nIN_PROGRESS — implementation complete; immutable verification and ordered internal assurance/seal pending.\n", encoding="utf-8", newline="\n")
    handoff = render_handoff(local_handoff_sections())
    (CHECKPOINT / "HANDOFF.md").write_text(handoff, encoding="utf-8", newline="\n")
    synchronize(ROOT, CHECKPOINT)
    print(f"SOURCE_READY_RECORDED requirements={len(rows)} localCommand={sequence['id']} status=IN_PROGRESS")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
