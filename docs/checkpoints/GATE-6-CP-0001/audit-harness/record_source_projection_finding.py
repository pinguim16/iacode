"""Record actual SQL selection overreach before accepting the causal repair."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, use_utf8_stdout, write_json
from lessons import load_lessons, save_lessons


def main() -> int:
    report = load_json(CHECKPOINT / "suite-attempts/INTEGRATION-0003.json")
    output = (CHECKPOINT / "suite-attempts/INTEGRATION-0003.log").read_text(encoding="utf-8")
    if report["result"] != "FAIL" or "Unneeded private source column selected:" not in output:
        raise ValueError("actual causal SQL projection failure is required")
    cause = ("Selecting ORM entities loaded whole source records before projecting the closed "
             "document. Final serialization excluded private text, but the SQL read still fetched "
             "unneeded task results, agent output and event payloads. Cardinality alone did not "
             "bound source JSON/text. Select only consumed columns with raiseload, extract exact "
             "workspace/permission scalars and bound required command arguments in SQL before loading.")
    evidence = ["file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0003.json",
                "file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0003.log",
                "file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl"]
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    if not any(row["findingId"] == "G6-INT-007" for row in findings["findings"]):
        findings["findings"].append({"findingId": "G6-INT-007", "severity": "HIGH",
            "title": "Source query fetches unneeded private columns before safe projection",
            "status": "OPEN", "expected": "The real SQL projection reads only consumed bounded observable source facts.",
            "observed": "The actual owning PostgreSQL regression detects an unneeded private task_runs column in the executed SELECT. This is over-fetch into memory, not evidence of private content persisted/exported.",
            "rootCause": cause, "evidence": evidence})
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    lessons = load_lessons(ROOT)
    if not any(row["lessonId"] == "LSN-0139" for row in lessons):
        now = utc_now()
        lessons.append({"lessonId": "LSN-0139", "title": "Privacy projection begins in the source query",
            "category": "security", "severity": "HIGH",
            "source": {"gate": "GATE-6", "checkpoint": CHECKPOINT.name, "finding": "G6-INT-007"},
            "symptom": "Actual SQL retrieves unneeded private source fields although the serialized fact omits them.",
            "rootCauseSummary": cause,
            "resolution": "Use explicit raiseload column projections, exact JSON scalar extraction and SQL-side byte bounds before required structured data enters application memory.",
            "prevention": [], "guardrails": [], "evidence": evidence,
            "applicability": {"gates": ["*"], "scopes": [], "technologies": ["PostgreSQL", "Python"],
                "modules": [], "requiredCheck": "A bounded privacy-safe output must not justify fetching unneeded private source columns; the actual query must project only consumed fields and bound required source JSON before transfer.",
                "requiredEvidence": "Actual owning SQL statement observation, oversized-source zero-effect refusal and real clean source capture/recovery, not a query-shaped mock."},
            "status": "CONFIRMED", "recurrenceKey": "security/private-source-overfetch-before-output-projection",
            "recurrenceCount": 0, "guardrailFailures": [], "createdAt": now, "updatedAt": now,
            "provenance": {"sourceType": "repository-generated", "provider": "local-execution", "model": None,
                "ownership": "project-generated evidence", "license": "not-applicable",
                "notes": "Actual SQL column identities only; no source text, secrets or private reasoning recorded."},
            "trainingEligibility": {"trainingAllowed": False, "ragAllowed": False,
                "distillationAllowed": False, "justification": None},
            "notes": "Confirmed actual source-read overreach; no automated guard or final acceptance claimed yet."})
    save_lessons(ROOT, lessons)
    print("G6-INT-007/LSN-0139 CONFIRMED; final output non-disclosure is not a query bound")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
