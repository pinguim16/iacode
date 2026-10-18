"""Invalidate stale v6 acceptance after recorded canonical report and memory rework."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assemble_source_ready import local_handoff_sections, render_handoff, render_next
from derive_requirements import render_closure, render_matrix
from ledger_common import load_json, use_utf8_stdout, utc_now, write_json
from lessons import guardrail_effectiveness
from sync_in_progress_metadata import synchronize


def main() -> int:
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS" or (CHECKPOINT / "VERIFY.json").exists():
        raise ValueError("only archived unsealed rework may be prepared")
    archive = load_json(CHECKPOINT / "attempts/RUNTIME-V6-FINALIZATION-ARCHIVE.json")
    if archive["result"] != "PASS" or len(archive["records"]) != 30:
        raise ValueError("all original v6 assurance and refused finalization evidence is required")
    records = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(row["id"] == "cmd-0343" and row["exitCode"] == 0 for row in records):
        raise ValueError("actual causal corrective acceptance is required")
    for name, renderer in (("REQUIREMENTS-MATRIX.json", render_matrix), ("CLOSURE-REQUIREMENTS.json", render_closure)):
        document = load_json(CHECKPOINT / name)
        for row in document["requirements"]:
            row["status" if name.startswith("REQUIREMENTS") else "finalStatus"] = "PARTIAL"
            row["validationEvidence"] = []
            row["notes"] = "Original complete v6 assurance and refused final report are exact archives. Canonical rendering passes local causal controls; fresh immutable verification and every ordered internal control remain mandatory after engineering memory changes."
        write_json(CHECKPOINT / name, document)
        (CHECKPOINT / name.replace(".json", ".md")).write_text(renderer(document), encoding="utf-8", newline="\n")
    quality = load_json(CHECKPOINT / "QUALITY.json")
    for entry in quality["checks"].values():
        entry.update({"status": "NOT_EXECUTED", "evidence": ["file:attempts/RUNTIME-V6-FINALIZATION-ARCHIVE.json"],
            "justification": "Historical v6 evidence is preserved; source-scope memory changed, so fresh complete acceptance is required."})
    write_json(CHECKPOINT / "QUALITY.json", quality)
    tests = {"schemaVersion": state["schemaVersion"]}
    for category in ("unit", "integration", "e2e"):
        tests[category] = {"executed": False, "passed": 0, "failed": 0, "command": None, "evidence": None}
    write_json(CHECKPOINT / "TESTS.json", tests)
    total = len(load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")["requirements"])
    state["requirementsMatrix"].update({"total": total, "complete": 0, "partial": total, "missing": 0, "coveragePercent": 0})
    state["greenKeeper"].update({"status": "NOT_EXECUTED", "remainingFailures": 0, "unresolvedReworkItems": 0,
        "scopeFingerprint": None, "evidence": ["checkpoint:REWORK-LOG.jsonl"]})
    state["deliveryCompleteness"].update({"status": "NOT_EXECUTED", "report": None, "coveragePercent": 0,
        "evidenceCoveragePercent": 0, "evidence": []})
    measured = guardrail_effectiveness(ROOT)
    state["guardrailEffectiveness"] = {key: measured[key] for key in (
        "guardrailsTotal", "guardrailsResolved", "guardrailsTested", "guardrailsEffective", "guardrailFailures")}
    state["guardrailEffectiveness"]["evidence"] = ["command:cmd-0343", "command:cmd-0344"]
    state["nextAllowedAction"] = "Publish a fresh Gate6-only immutable subject after full lint and valid serialized bookkeeping; execute complete non-fast verification, whole Green Keeper, total completeness, fresh internal Red Team and full clean-clone mirror, then canonical finalization/seal/publication. All original v6 evidence and terminal refusal remain archived. Independent M2 remains pending; Gate7 is unauthorized."
    state["updatedAt"] = utc_now()
    write_json(CHECKPOINT / "STATE.json", state)
    steps = load_json(CHECKPOINT / "STEPS.json")
    for row in steps["steps"]:
        if row["stepId"] in {"G6-S02", "G6-S03"}:
            row.update({"status": "IN_PROGRESS", "functionalProof": "Historical v6 complete assurance passed but finalization refused missing report headings. Original bytes remain archived; actual local corrective rendering passes. Fresh memory-bound whole assurance and canonical seal are required, not claimed complete.",
                "evidence": ["cmd-0340", "cmd-0341", "cmd-0342", "cmd-0343", "attempts/RUNTIME-V6-FINALIZATION-ARCHIVE.json"]})
    write_json(CHECKPOINT / "STEPS.json", steps)
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    marker = "\n<!-- BEGIN DERIVED LESSON COMMITMENTS -->\n"
    path = CHECKPOINT / "PLAN.md"
    plan = path.read_text(encoding="utf-8").split(marker, 1)[0].rstrip()
    commitments = []
    for row in preflight["applicable"]:
        commitments.extend(["", "### " + row["derivedRequirementId"] + " — " + row["lessonId"], "",
            "- Required check: " + row["requiredCheck"], "- Required evidence: " + row["requiredEvidence"]])
    path.write_text(plan + marker + "\n".join(commitments) + "\n", encoding="utf-8", newline="\n")
    sections = local_handoff_sections()
    sections["## What was completed"] = "Historical runtime-v6 full47, functional37/37, Green Keeper15, completeness193, internal Red Team71 and mirror18 passed. All30 exact assurance/handoff originals are archived. Cmd-0340 terminal refusal and cmd-0342 causal failure remain; cmd-0343 proves canonical rendering and every-section adverse controls, with LSN-0008 recurrence3/CRITICAL and GRD-0146 local restoration. Fresh memory-bound whole assurance is due."
    sections["## Known failures"] = "G6-INT-021 is causally corrected, not silently repaired. Historical v6 successful assurance does not accept the changed current memory. All previous failures/counters/raw producers remain. No Gate, seal, publication or independent verdict is inferred."
    sections["## Do not repeat"] = "Never replay any historical archive, cleanup/recovery or capture helper, or any of four policy-refused targets. Do not overlap checkpoint writers, narrow controls or stop unrelated applications. Never mutate a sealed predecessor or published immutable tag."
    (CHECKPOINT / "HANDOFF.md").write_text(render_handoff(sections), encoding="utf-8", newline="\n")
    (CHECKPOINT / "NEXT.md").write_text(render_next(state["nextAllowedAction"]), encoding="utf-8", newline="\n")
    (CHECKPOINT / "STATUS.md").write_text("# Status\n\nIN_PROGRESS — local final-report repair accepted; fresh memory-bound immutable assurance and actual seal pending.\n", encoding="utf-8", newline="\n")
    (CHECKPOINT / "PROGRESS.md").write_text("# Gate 6 progress\n\n" + sections["## What was completed"] + "\n\n" + state["nextAllowedAction"] + "\n", encoding="utf-8", newline="\n")
    synchronize(ROOT, CHECKPOINT)
    print(f"FINAL_REPORT_REWORK_BOUND requirements={total} PARTIAL; fresh complete assurance and seal pending")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
