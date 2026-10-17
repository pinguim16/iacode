"""Record actual complete integration red and canonical recurrence before repair acceptance."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import load_json, utc_now, use_utf8_stdout, write_json
from lessons import load_lessons, register_recurrence, save_lessons


def main() -> int:
    report = load_json(CHECKPOINT / "suite-attempts/INTEGRATION-0001.json")
    if report["result"] != "FAIL" or report["commands"][-1]["exitCode"] != 1:
        raise ValueError("actual original integration failure is required")
    definitions = (
        ("G6-INT-003", "CRITICAL", "GUARDRAIL_FAILURE: UNIQUE naming diverges from migration",
         "Actual Alembic check must find no ORM/schema drift, including new UNIQUE constraints.",
         "Cmd-0023 preserves actual autogenerate refusal: ORM project_request/project_source differ from migrated uq_experiences_project_request/uq_experiences_project_source.",
         "The new ORM UNIQUE names assumed the convention prefixes explicit names as CHECK does. LSN-0042 already distinguishes these naming rules; escalate the guarded recurrence and align actual explicit UNIQUE names, preserving the unchanged real migration assertion."),
        ("G6-INT-004", "MEDIUM", "SQL text interprets inline JSON colons as bindings",
         "The actual corruption and legacy fixtures must reach PostgreSQL with the intended JSON bytes.",
         "Cmd-0023 preserves two StatementError failures demanding bind parameter true before those fixtures execute; 27 other cases pass and owned cleanup is complete.",
         "Inline JSON literals inside SQLAlchemy text contain colon-prefixed tokens that its lexical binder treats as parameters. Bind the JSON data through CAST(:body AS JSONB), without changing either substantive corruption/legacy assertion."),
    )
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    for identifier, severity, title, expected, observed, cause in definitions:
        if not any(row["findingId"] == identifier for row in findings["findings"]):
            findings["findings"].append({"findingId": identifier, "severity": severity,
                "title": title, "status": "OPEN", "expected": expected, "observed": observed,
                "rootCause": cause, "evidence": ["command:cmd-0023",
                    "file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0001.json",
                    "file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0001.log"]})
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    lessons = load_lessons(ROOT)
    for index, lesson in enumerate(lessons):
        if lesson["lessonId"] == "LSN-0042" and not any("G6-INT-003" in row["detail"]
                for row in lesson.get("guardrailFailures", [])):
            lessons[index] = register_recurrence(lesson, CHECKPOINT.name, definitions[0][0] + ": " + definitions[0][5])
    if not any(row["lessonId"] == "LSN-0137" for row in lessons):
        now = utc_now()
        lessons.append({"lessonId": "LSN-0137", "title": definitions[1][2],
            "category": "testing", "severity": "MEDIUM",
            "source": {"gate": "GATE-6", "checkpoint": CHECKPOINT.name, "finding": "G6-INT-004"},
            "symptom": definitions[1][4], "rootCauseSummary": definitions[1][5],
            "resolution": "Bind JSON as data instead of embedding colon-bearing JSON literals in SQLAlchemy text; retain actual database assertions and complete migration execution.",
            "prevention": [], "guardrails": [], "evidence": [
                "file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0001.log",
                "file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl"],
            "applicability": {"gates": ["*"], "scopes": [], "technologies": ["Python", "PostgreSQL"],
                "modules": [], "requiredCheck": "SQL fixtures must transport structured JSON through bindings rather than let a SQL text parser reinterpret JSON property/value colons.",
                "requiredEvidence": "Actual previously failing legacy/corruption fixtures and full migration agreement through the real owning SQLAlchemy/PostgreSQL runtime."},
            "status": "CONFIRMED", "recurrenceKey": "testing/inline-json-colon-reinterpreted-as-sql-binding",
            "recurrenceCount": 0, "guardrailFailures": [], "createdAt": now, "updatedAt": now,
            "provenance": {"sourceType": "repository-generated", "provider": "local-execution",
                "model": None, "ownership": "project-generated evidence", "license": "not-applicable",
                "notes": "Actual owned SQL execution; no credential or private reasoning."},
            "trainingEligibility": {"trainingAllowed": False, "ragAllowed": False,
                "distillationAllowed": False, "justification": None},
            "notes": "Confirmed; no corrected fixture or whole-Gate acceptance claimed yet."})
    save_lessons(ROOT, lessons)
    print("SQL_FINDINGS_RECORDED G6-INT-003 GUARDRAIL_FAILURE; G6-INT-004/LSN-0137 CONFIRMED")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
