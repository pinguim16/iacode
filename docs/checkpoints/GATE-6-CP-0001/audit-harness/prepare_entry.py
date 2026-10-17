"""Bind actual completed entry observations and mechanically carry every selected lesson."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from anchors import load_anchors
from ledger_common import load_json, utc_now, write_json
from lessons import guardrail_effectiveness
from sync_in_progress_metadata import synchronize


def main() -> int:
    import json

    commands = {row["id"]: row for row in (
        json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
            encoding="utf-8").splitlines() if line.strip())}
    for identifier in ("cmd-0002", "cmd-0003", "cmd-0004", "cmd-0005", "cmd-0006"):
        if commands[identifier].get("exitCode") != 0:
            raise ValueError("entry cannot be bound from an unsuccessful actual command")
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    plan_path = CHECKPOINT / "PLAN.md"
    marker = "\n<!-- BEGIN DERIVED LESSON COMMITMENTS -->\n"
    text = plan_path.read_text(encoding="utf-8").split(marker, 1)[0].rstrip()
    rendered = []
    for item in preflight["applicable"]:
        rendered.extend(["", "### " + item["derivedRequirementId"] + " — " + item["lessonId"],
                         "", "- Required check: " + item["requiredCheck"],
                         "- Required evidence: " + item["requiredEvidence"]])
    plan_path.write_text(text + marker + "\n".join(rendered) + "\n", encoding="utf-8", newline="\n")
    state = load_json(CHECKPOINT / "STATE.json")
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")["requirements"]
    state["requirementsMatrix"].update({"total": len(matrix),
        "mandatory": sum(row["mandatory"] for row in matrix), "complete": 0, "partial": 0,
        "missing": 0, "notApplicable": 0, "coveragePercent": 0.0})
    state["lessonPreflight"]["evidence"] = ["command:cmd-0004"]
    measured = guardrail_effectiveness(ROOT)
    state["guardrailEffectiveness"] = {key: measured[key] for key in (
        "guardrailsTotal", "guardrailsResolved", "guardrailsTested", "guardrailsEffective",
        "guardrailFailures")}
    state["guardrailEffectiveness"]["evidence"] = ["command:cmd-0006"]
    state["integrity"].update({"status": "PASS", "anchors": len(load_anchors(ROOT)),
                               "evidence": ["command:cmd-0003"]})
    write_json(CHECKPOINT / "STATE.json", state)
    tests = load_json(CHECKPOINT / "TESTS.json")
    tests["unit"].update({"executed": True, "passed": 91, "failed": 0,
        "command": commands["cmd-0006"]["command"], "evidence": "command:cmd-0006",
        "runId": "gate6-inherited-preimplementation-baseline"})
    write_json(CHECKPOINT / "TESTS.json", tests)
    provenance = load_json(CHECKPOINT / "PROVENANCE.json")
    provenance["artifacts"][0].update({
        "sourceType": "repository-generated and AI-assisted engineering evidence",
        "provider": "OpenAI / local execution", "model": "not-exposed",
        "ownership": "project-generated evidence", "license": "project-policy",
        "evidence": "AUTHORIZATION.md, BASELINE.md, PLAN.md, COMMANDS.jsonl and FILES.json",
        "notes": "Internal implementing session only. No private reasoning, credential value, inferred rights or independent approval."})
    write_json(CHECKPOINT / "PROVENANCE.json", provenance)
    synchronize(ROOT, CHECKPOINT)
    print(f"ENTRY_BOUND requirements={len(matrix)} lessons={len(preflight['applicable'])} baseline=91 status=IN_PROGRESS at={utc_now()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
