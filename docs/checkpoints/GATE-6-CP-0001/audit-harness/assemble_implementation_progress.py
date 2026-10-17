"""Bind observed local progress only; never promote live/full/independent acceptance."""

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


def main() -> int:
    commands = {row["id"]: row for row in (json.loads(line) for line in
        (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
    for identifier in ("cmd-0026", "cmd-0028", "cmd-0030"):
        if commands[identifier]["exitCode"] != 0:
            raise ValueError("actual completed local controls are required")
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    for row in matrix["requirements"]:
        key = row["sourceRef"].partition("#")[2]
        if row["sourceRef"].startswith("canonical:GATE-6#") and key in ("1.1", "1.2", "1.3"):
            row.update({"status": "COMPLETE", "implementationEvidence": [
                "file:docs/checkpoints/GATE-6-CP-0001/AUTHORIZATION.md",
                "file:docs/GATE-6-CHECKLIST.md"],
                "testEvidence": ["command:cmd-0003", "command:cmd-0030"],
                "documentationEvidence": ["file:docs/checkpoints/GATE-6-CP-0001/PLAN.md"],
                "validationEvidence": ["command:cmd-0010", "command:cmd-0028"],
                "notes": "Actual separately authorized entry/derivation/preimplementation ADRs. This is not feature or Gate acceptance."})
        elif row["sourceRef"].startswith("canonical:GATE-6#") and key.partition(".")[0] in {"2", "3", "4", "5", "6"}:
            row.update({"status": "PARTIAL", "implementationEvidence": [
                "file:services/experience/src/iacode_experience/domain.py",
                "file:apps/api/src/iacode_api/experience/sources.py",
                "file:apps/api/src/iacode_api/experience/store.py",
                "file:apps/api/src/iacode_api/routes/experiences.py"],
                "testEvidence": ["command:cmd-0026"],
                "documentationEvidence": ["file:docs/runbooks/experience-store.md"],
                "validationEvidence": [],
                "notes": "Implemented with actual local domain29/API171/SQL-HTTP-migration33 passing. Added correlation coverage/live producer and complete frozen full assurance remain pending; no final acceptance is inferred."})
    write_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json", matrix)
    state = load_json(CHECKPOINT / "STATE.json")
    rows = matrix["requirements"]
    complete = sum(row["status"] == "COMPLETE" for row in rows)
    state["requirementsMatrix"].update({"total": len(rows), "mandatory": sum(row["mandatory"] for row in rows),
        "complete": complete, "partial": sum(row["status"] == "PARTIAL" for row in rows),
        "missing": 0, "notApplicable": 0, "coveragePercent": round(100 * complete / len(rows), 2)})
    state["lessonPreflight"]["evidence"] = ["command:cmd-0027", "command:cmd-0028"]
    measured = guardrail_effectiveness(ROOT)
    state["guardrailEffectiveness"] = {key: measured[key] for key in (
        "guardrailsTotal", "guardrailsResolved", "guardrailsTested", "guardrailsEffective", "guardrailFailures")}
    state["guardrailEffectiveness"]["evidence"] = ["command:cmd-0026", "command:cmd-0032"]
    write_json(CHECKPOINT / "STATE.json", state)
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    plan = CHECKPOINT / "PLAN.md"
    marker = "\n<!-- BEGIN DERIVED LESSON COMMITMENTS -->\n"
    text = plan.read_text(encoding="utf-8").split(marker, 1)[0].rstrip()
    rendered = []
    for item in preflight["applicable"]:
        rendered.extend(["", "### " + item["derivedRequirementId"] + " — " + item["lessonId"], "",
            "- Required check: " + item["requiredCheck"], "- Required evidence: " + item["requiredEvidence"]])
    plan.write_text(text + marker + "\n".join(rendered) + "\n", encoding="utf-8", newline="\n")
    steps = load_json(CHECKPOINT / "STEPS.json")
    steps["steps"][1]["functionalProof"] = (
        "Actual local complete sequence cmd-0026 passes domain29, API171, real SQL/HTTP and all migrations33, "
        "and the registered experience gate/schema. Cmd-0030 passes11 new root controls. Five original "
        "findings/three escalated guarded classes are retained; new correlation case/live actor and "
        "whole mandatory lint/client/full/ordered closure acceptance remain pending.")
    steps["steps"][1]["evidence"] = ["command:cmd-0026", "command:cmd-0030", "command:cmd-0032"]
    write_json(CHECKPOINT / "STEPS.json", steps)
    tests = load_json(CHECKPOINT / "TESTS.json")
    tests["unit"] = {"executed": True, "passed": 171, "failed": 0,
        "command": commands["cmd-0026"]["command"],
        "evidence": "file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/API-UNIT-0002.json",
        "runId": "gate6-api-unit-0002-20261017T123129Z"}
    tests["integration"] = {"executed": True, "passed": 33, "failed": 0,
        "command": commands["cmd-0026"]["command"],
        "evidence": "file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0002.json",
        "runId": "gate6-real-selected-integration-0002-20261017T123131Z"}
    write_json(CHECKPOINT / "TESTS.json", tests)
    provenance = load_json(CHECKPOINT / "PROVENANCE.json")
    provenance["artifacts"][0]["artifact"] = CHECKPOINT.relative_to(ROOT).as_posix()
    write_json(CHECKPOINT / "PROVENANCE.json", provenance)
    synchronize(ROOT, CHECKPOINT)
    print(f"LOCAL_PROGRESS_BOUND requirements={len(rows)} completeEntry={complete} status=IN_PROGRESS at={utc_now()}")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
