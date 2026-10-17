"""Record the actual rejected handoff projection, not a fabricated product regression."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, use_utf8_stdout, write_json
from lessons import load_lessons, save_lessons


def main() -> int:
    records = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    actual = next(row for row in records if row["id"] == "cmd-0081")
    if actual["exitCode"] != 1 or "HANDOFF.md is missing heading" not in actual["failureReason"]:
        raise ValueError("actual canonical handoff refusal is required")
    cause = ("The local assembler replaced the structured handoff with a prose summary and "
             "emitted NEXT without its mandatory subsection. Semantically related prose does "
             "not satisfy the canonical artifact structure. Render every owning-validator "
             "heading in order with substantive content; reject missing/empty sections and "
             "retain the next-action heading before writing. Never relax the validator.")
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    if not any(row["findingId"] == "G6-INT-009" for row in findings["findings"]):
        findings["findings"].append({"findingId": "G6-INT-009", "severity": "MEDIUM",
            "title": "Local summary overwrites required continuation structure", "status": "OPEN",
            "observed": "Cmd-0081 actually rejects preparatory finalization with all14 missing HANDOFF headings and an unpopulated NEXT structure; no runtime commit or final seal was issued.",
            "rootCause": cause, "evidence": ["command:cmd-0081"]})
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    lessons = load_lessons(ROOT)
    if not any(row["lessonId"] == "LSN-0140" for row in lessons):
        now = utc_now()
        lessons.append({"lessonId": "LSN-0140", "title": "Summaries preserve canonical continuation structure",
            "category": "quality", "severity": "MEDIUM",
            "source": {"gate": "GATE-6", "checkpoint": CHECKPOINT.name, "finding": "G6-INT-009"},
            "symptom": "A local assembler emits readable prose but removes mandatory handoff/next-action sections.",
            "rootCauseSummary": cause, "resolution": "Render from the owning canonical headings, require meaningful content for every section and prove real output plus omission/empty-section refusals before current checkpoint acceptance.",
            "prevention": [], "guardrails": [],
            "evidence": ["file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl", "file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json"],
            "applicability": {"gates": ["*"], "scopes": [], "technologies": [], "modules": [],
                "requiredCheck": "Any helper that replaces a checkpoint artifact must preserve the owning canonical structural contract, not substitute an unstructured summary; required sections stay substantive and complete.",
                "requiredEvidence": "Actual renderer output against canonical headings, omission/empty-section adverse controls and current canonical checkpoint acceptance without any validator weakening."},
            "status": "CONFIRMED", "recurrenceKey": "quality/local-summary-removes-canonical-handoff-structure",
            "recurrenceCount": 0, "guardrailFailures": [], "createdAt": now, "updatedAt": now,
            "provenance": {"sourceType": "repository-generated", "provider": "local-execution", "model": None,
                "ownership": "project-generated evidence", "license": "not-applicable", "notes": "Actual local finalizer refusal; no secret or private reasoning."},
            "trainingEligibility": {"trainingAllowed": False, "ragAllowed": False, "distillationAllowed": False, "justification": None},
            "notes": "Confirmed before causal renderer acceptance; no product or independent verdict is inferred."})
    save_lessons(ROOT, lessons)
    print("G6-INT-009/LSN-0140 CONFIRMED; canonical continuation structure remains mandatory")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
