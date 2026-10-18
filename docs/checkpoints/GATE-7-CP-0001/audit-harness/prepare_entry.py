"""Bind completed entry observations without claiming implementation or future assurance."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from anchors import load_anchors
from ledger_common import load_json, write_json
from sync_in_progress_metadata import synchronize


def main() -> int:
    records = {row["id"]: row for row in (
        json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
            encoding="utf-8").splitlines() if line.strip())}
    for identifier in ("cmd-0002", "cmd-0003", "cmd-0004", "cmd-0005", "cmd-0006"):
        if records[identifier].get("exitCode") != 0:
            raise ValueError("entry requires successful actual commands")
    observed = (CHECKPOINT / "suite-attempts/BASELINE-0001.log").read_text(encoding="utf-8")
    matches = re.findall(r"Ran (\d+) tests in ([0-9.]+)s\s+OK", observed)
    if len(matches) != 1:
        raise ValueError("one completed successful baseline transcript is required")
    state = load_json(CHECKPOINT / "STATE.json")
    if state["gate"] != "GATE-7" or state["status"] != "IN_PROGRESS":
        raise ValueError("not the authorized unsealed entry checkpoint")
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")["requirements"]
    if not matrix or any(row["status"] != "NOT_STARTED" for row in matrix):
        raise ValueError("entry cannot overwrite implementation evidence")
    state["currentCommit"] = "HEAD"
    state["nextAllowedAction"] = (
        "Validate the declared Gate7 entry, then implement PLAN G7-S01; complete every internal "
        "control and seal READY_FOR_REVIEW for the separate M2 audit. No Gate8 authority."
    )
    state["requirementsMatrix"].update({
        "total": len(matrix), "mandatory": sum(row["mandatory"] for row in matrix),
        "complete": 0, "partial": 0, "missing": 0, "notApplicable": 0,
        "coveragePercent": 0.0})
    state["lessonPreflight"]["evidence"] = ["command:cmd-0004"]
    state["integrity"].update({"status": "PASS", "anchors": len(load_anchors(ROOT)),
                               "evidence": ["command:cmd-0003"]})
    write_json(CHECKPOINT / "STATE.json", state)
    metadata = load_json(CHECKPOINT / "RUN-METADATA.json")
    metadata.update({"tool": "Codex", "toolVersion": "not-exposed", "provider": "OpenAI",
                     "model": "not-exposed", "effort": "not-exposed",
                     "operatingSystem": "Windows / PowerShell"})
    write_json(CHECKPOINT / "RUN-METADATA.json", metadata)
    tests = load_json(CHECKPOINT / "TESTS.json")
    tests["unit"].update({"executed": True, "passed": int(matches[0][0]), "failed": 0,
                          "command": records["cmd-0006"]["command"],
                          "evidence": "command:cmd-0006",
                          "runId": "gate7-inherited-preimplementation-baseline"})
    write_json(CHECKPOINT / "TESTS.json", tests)
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    marker = "\n<!-- BEGIN DERIVED LESSON COMMITMENTS -->\n"
    path = CHECKPOINT / "PLAN.md"
    text = path.read_text(encoding="utf-8").split(marker, 1)[0].rstrip()
    lines = []
    for row in preflight["applicable"]:
        lines.extend(["", "### " + row["derivedRequirementId"] + " — " + row["lessonId"],
                      "", "- Required check: " + row["requiredCheck"],
                      "- Required evidence: " + row["requiredEvidence"]])
    path.write_text(text + marker + "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    provenance = load_json(CHECKPOINT / "PROVENANCE.json")
    provenance["artifacts"][0].update({
        "sourceType": "repository-generated and AI-assisted engineering work/evidence",
        "provider": "OpenAI / local execution", "model": "not-exposed",
        "ownership": "project-generated engineering evidence", "license": "project-policy",
        "evidence": "AUTHORIZATION.md, BASELINE.md, PLAN.md, COMMANDS.jsonl and FILES.json",
        "notes": "No private reasoning, secrets, inferred reuse rights or independent approval."})
    write_json(CHECKPOINT / "PROVENANCE.json", provenance)
    synchronize(ROOT, CHECKPOINT)
    print(f"ENTRY_BOUND baseline={matches[0][0]} requirements={len(matrix)} "
          f"lessons={len(preflight['applicable'])} implementation=NOT_STARTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
