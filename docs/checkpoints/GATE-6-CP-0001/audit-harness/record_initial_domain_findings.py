"""Escalate the actual first domain run before repair; never turn an observation into PASS."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import load_json, utc_now, use_utf8_stdout, write_json
from lessons import load_lessons, register_recurrence, save_lessons


def main() -> int:
    command = next(row for row in __import__("json").loads("[" + ",".join(
        (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()) + "]")
        if row["id"] == "cmd-0014")
    if command["exitCode"] != 1:
        raise ValueError("the preserved actual failing command is required")
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    definitions = (
        ("G6-INT-001", "MEDIUM", "Strict JSON validation loses transport context",
         "Valid JSON arrays and aware RFC3339 timestamps must round-trip under the strict contract.",
         "Cmd-0014 actually reports 18 setup errors rejecting valid arrays/dates, one distinct failed security case and seven passed cases; its process exits 1.",
         "An inherited model-before validator materializes the entire JSON model as a Python dictionary before strict tuple/datetime handling. Restrict boolean prevalidation to the permission fields."),
        ("G6-INT-002", "CRITICAL", "GUARDRAIL_FAILURE: encoded known capability gap",
         "Every declared known-capability form is refused by the new domain scanner before effects.",
         "Cmd-0014 test_known_opaque_capability_refused_in_declared_forms actually fails DID NOT RAISE; no real capture was attempted or accepted in that pure test.",
         "The new scanner copied only raw/case/base64/hex known forms, omitting percent and literal Unicode forms. LSN-0126/GRD-0128 had already required the complete set; this is an escalated recurrence, not a silent fix."),
    )
    for identifier, severity, title, expected, observed, cause in definitions:
        if not any(row["findingId"] == identifier for row in findings["findings"]):
            findings["findings"].append({"findingId": identifier, "severity": severity,
                "title": title, "status": "OPEN", "expected": expected, "observed": observed,
                "rootCause": cause, "evidence": ["command:cmd-0014"],
                "limits": "Concise direct tool-output observation; no raw-output artifact was configured for the first run. No independent result or correction acceptance is claimed."})
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    lessons = load_lessons(ROOT)
    for index, lesson in enumerate(lessons):
        if lesson["lessonId"] == "LSN-0126" and not any(
                "G6-INT-002" in row["detail"] for row in lesson.get("guardrailFailures", [])):
            lessons[index] = register_recurrence(lesson, CHECKPOINT.name, definitions[1][0] + ": " + definitions[1][5])
    if not any(row["lessonId"] == "LSN-0136" for row in lessons):
        now = utc_now()
        lessons.append({"lessonId": "LSN-0136", "title": definitions[0][2],
            "category": "implementation", "severity": "MEDIUM",
            "source": {"gate": "GATE-6", "checkpoint": CHECKPOINT.name, "finding": "G6-INT-001"},
            "symptom": definitions[0][4], "rootCauseSummary": definitions[0][5],
            "resolution": "Preserve strict JSON-mode collection/date handling; apply exact-boolean checks at their owning fields and retain positive/adverse round-trip controls.",
            "prevention": [], "guardrails": [], "evidence": [
                "file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl",
                "file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json"],
            "applicability": {"gates": ["*"], "scopes": [], "technologies": ["Python"],
                "modules": [], "requiredCheck": "Strict contract prevalidators must preserve the transport semantics of valid JSON arrays/dates while refusing coerced boolean/numeric values.",
                "requiredEvidence": "Actual JSON-mode clean round-trip and adverse type/privacy cases through the pinned production dependency runtime."},
            "status": "CONFIRMED", "recurrenceKey": "implementation/model-before-validator-loses-strict-json-context",
            "recurrenceCount": 0, "guardrailFailures": [], "createdAt": now, "updatedAt": now,
            "provenance": {"sourceType": "repository-generated", "provider": "local-execution",
                "model": None, "ownership": "project-generated evidence", "license": "not-applicable",
                "notes": "Actual initial domain suite and causal source inspection; no private reasoning or credential."},
            "trainingEligibility": {"trainingAllowed": False, "ragAllowed": False,
                "distillationAllowed": False, "justification": None},
            "notes": "No prevention or correction is accepted until the unchanged complete suite executes."})
    save_lessons(ROOT, lessons)
    print("FINDINGS_RECORDED G6-INT-001 OPEN; G6-INT-002 GUARDRAIL_FAILURE OPEN; LSN-0136 CONFIRMED")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
