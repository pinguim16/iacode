#!/usr/bin/env python3
"""Publish authored PARTIAL progress only; never issue a readiness or quality verdict."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import load_json, use_utf8_stdout, utc_now, write_json  # noqa: E402
from delivery_assurance import collect_test_ids, evaluate_matrix, load_command_results  # noqa: E402

# These mappings describe the actually implemented subset. Future clients, installation and
# functional acceptance are expressly excluded, and no row is marked COMPLETE by this publisher.
CANONICAL = {"1.1", "1.2", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6",
             "3.1", "3.2", "3.3", "3.4", "4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7",
             "1.3", "1.4", "1.5", "1.6", "3.5", "5.1", "5.2", "5.3", "5.4", "6.1", "6.2", "6.3", "6.4", "6.5",
             "7.1", "7.2", "7.3", "7.4", "8.1", "8.2", "8.3", "8.4", "8.5", "9.1", "9.2", "9.5", "9.7", "9.8"}
LESSONS = {"LESSON-REQ-0002", "LESSON-REQ-0003", "LESSON-REQ-0008", "LESSON-REQ-0010",
           "LESSON-REQ-0021", "LESSON-REQ-0083", "LESSON-REQ-0100", "LESSON-REQ-0115", "LESSON-REQ-0116", "LESSON-REQ-0117", "LESSON-REQ-0118", "LESSON-REQ-0119", "LESSON-REQ-0120", "LESSON-REQ-0121", "LESSON-REQ-0122", "LESSON-REQ-0123", "LESSON-REQ-0124", "LESSON-REQ-0125", "LESSON-REQ-0126", "LESSON-REQ-0127", "LESSON-REQ-0128", "LESSON-REQ-0129"}


def main() -> int:
    use_utf8_stdout()
    closure = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    for row in closure["requirements"]:
        key = row["sourceRef"].split("#")[-1]
        if ((row["sourceRef"].startswith("canonical:") and key in CANONICAL)
                or row["id"] in LESSONS or row["sourceRef"] in {"lesson:LSN-0131", "lesson:LSN-0132", "lesson:LSN-0133", "lesson:LSN-0134", "lesson:LSN-0135"}):
            if row["finalStatus"] == "NOT_STARTED":
                row["implementationStatus"] = "IN_PROGRESS"
                row["finalStatus"] = "PARTIAL"
                row["implementationEvidence"] = ["checkpoint:PROGRESS.md"]
                row["documentationEvidence"] = ["checkpoint:PLAN.md", "checkpoint:BASELINE.md"]
                row["notes"] = "Partial implementation/entry evidence only. The complete client, fresh install, functional proof and full assurance remain pending. No delivery PASS is inferred."
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    completed = subprocess.run([sys.executable, str(ROOT / "scripts/development-ledger/derive_requirements.py"),
                                "--write"], cwd=ROOT, check=False)
    if completed.returncode:
        return completed.returncode
    matrix = load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json")
    rows = matrix["requirements"]
    summary = evaluate_matrix(ROOT, CHECKPOINT, matrix, load_command_results(CHECKPOINT), collect_test_ids(ROOT))
    state = load_json(CHECKPOINT / "STATE.json")
    state["requirementsMatrix"] = {"path": "REQUIREMENTS-MATRIX.json", "total": len(rows),
        "mandatory": sum(bool(row["mandatory"]) for row in rows),
        "complete": sum(row["status"] == "COMPLETE" for row in rows),
        "partial": sum(row["status"] == "PARTIAL" for row in rows),
        "missing": sum(row["status"] == "MISSING" for row in rows),
        "notApplicable": sum(row["status"] == "NOT_APPLICABLE" for row in rows), "coveragePercent": summary["coveragePercent"]}
    anchors = load_json(ROOT / ".iacode/anchors/checkpoint-chain.json")["anchors"]
    state["integrity"].update({"status": "PASS", "anchors": len(anchors), "evidence": ["command:cmd-0002"]})
    records = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    state["lessonPreflight"].update({"lessonsConsidered": preflight["lessonsConsidered"],
                                    "lessonsApplicable": preflight["lessonsApplicable"],
                                    "derivedRequirements": len(preflight["derivedRequirements"])})
    state["lessonPreflight"]["evidence"] = ["command:" + record["id"] for record in records
        if record.get("exitCode") == 0 and "scripts/development-ledger/lesson_preflight.py" in record.get("command", "")]
    state["nextAllowedAction"] = "Complete causal full-v2 rework and current metadata, freeze/publish a new immutable runtime v3 subject, then repeat every non-fast stage and ordered internal assurance. No Gate 6 authorization."
    state["updatedAt"] = utc_now()
    write_json(CHECKPOINT / "STATE.json", state)
    print(f"PROGRESS_RECORDED total={len(rows)} partial={state['requirementsMatrix']['partial']} complete=0 status=IN_PROGRESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
