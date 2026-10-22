"""Render the final result layer over the criteria frozen before M2 audit execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PASS = {1, 2, 3, 5, 6, 7, 8, 12, 33, 39, 42, 43, 44, 45}
FAIL = {9, 14, 31, 32, 34, 35, 37, 40}
PARTIAL = {4, 11, 28, 29, 30, 36, 41}
BLOCKED = {10, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 38}


def _number(identifier: str) -> int:
    return int(identifier.rsplit("-", 1)[-1])


def _result(number: int) -> tuple[str, str, list[str]]:
    if number in {1, 2}:
        return "PASS", "Local and unauthenticated public identity observations agree with the declared sealed subject.", ["file:ENTRY-REPORT.md"]
    if number == 3:
        return "PASS", "The successor rebuild added the owed subject anchor and the chain validated with 36 anchors.", ["command:cmd-0005"]
    if number in {5, 6, 7, 39}:
        return "PASS", "Independent public detached reconstructions produced the expected historical red control and exact byte-identical corrective/final archives.", ["command:cmd-0010", "command:cmd-0011", "file:REVIEW-TRANSPORT-RECONSTRUCTION-RETRY-0002.json", "file:REVIEW-TRANSPORT-RECONSTRUCTION-RETRY-0003.json"]
    if number == 8:
        return "PASS", "Canonical checklist/registry derivation produced 105+50+51+48=254 Gate rows.", ["command:cmd-0004", "file:M2-AUDIT-REQUIREMENTS.json"]
    if number == 9:
        return "FAIL", "Two selected GUARDED lesson classes recurred as M2-F-001 and M2-F-002.", ["file:FINDINGS.json", "file:LESSON-PREFLIGHT.json"]
    if number == 10:
        return "BLOCKED", "The Docker-dependent functional and full-verifier evidence needed to close all 404 rows could not execute; rows remain unverified rather than inferred.", ["command:cmd-0007", "file:M2-AUDIT-REQUIREMENTS.json"]
    if number == 11:
        return "PARTIAL", "ADRs and boundaries were reviewed and 980 control-plane tests passed, but live cross-Gate architecture behavior could not be observed.", ["file:ARCHITECTURE-REVIEW.json", "command:cmd-0015"]
    if number == 12:
        return "PASS", "The audit created no Gate 8 content or transition and the frozen plan prohibits Gate 8.", ["file:PLAN.md"]
    if number == 13:
        return "BLOCKED", "The Docker engine named pipe was inaccessible, so scripts/iacode/verify.py was not launched and no partial result was promoted.", ["command:cmd-0007"]
    if number == 14:
        return "FAIL", "The integral control-plane suite ended red: 984 total, 980 pass, 1 skip, 1 failure and 2 errors; guardrail recurrence is nonzero.", ["command:cmd-0015", "file:controls/control-plane-full-suite.json"]
    if number == 15:
        return "BLOCKED", "The live dependency scanners and complete secret/security gates require Docker/network execution that could not be completed.", ["command:cmd-0007", "command:cmd-0015"]
    if 16 <= number <= 27:
        return "BLOCKED", "The criterion requires a real Docker/stack/native functional or isolation proof; engine access was denied and no substitute was allowed.", ["command:cmd-0007", "file:RISKS.md"]
    if number == 28:
        return "PARTIAL", "Most control-plane regressions passed, but the integral suite was red and inherited image/stack stages were not executable.", ["command:cmd-0015", "file:controls/control-plane-full-suite.json"]
    if number == 29:
        return "PARTIAL", "Documentation/link controls not among the three named failures passed in the integral suite, but behavior-dependent documentation could not be compared with live execution.", ["command:cmd-0015"]
    if number == 30:
        return "PARTIAL", "The audit and subject retain trainingAllowed=false and declared provenance, but unexecuted live producers prevent complete provenance observation.", ["file:PROVENANCE.json", "file:AUDITOR-INDEPENDENCE.json"]
    if number == 31:
        return "FAIL", "M2-F-001 and M2-F-002 are confirmed guardrail recurrences; zero recurrence failure is false.", ["file:FINDINGS.json", "file:INDEPENDENT-RED-TEAM-LEDGER-RETRY-0002.json"]
    if number == 32:
        return "FAIL", "cmd-0001 omits the consumed --phase option/value, and the canonical validator accepts that non-literal record.", ["command:cmd-0001", "file:FINDINGS.json"]
    if number == 33:
        return "PASS", "Internal subject claims were not adopted; this later session generated its own public, test and Red Team observations.", ["file:AUDITOR-INDEPENDENCE.json", "file:ENTRY-REPORT.md"]
    if number == 34:
        return "FAIL", "Independent review has one open Critical and one open High finding.", ["file:FINDINGS.json", "file:REVIEW-REPORT.md"]
    if number == 35:
        return "FAIL", "A valid-baseline independent mutation escaped; the remaining M2 attack battery was blocked by the inaccessible engine.", ["command:cmd-0013", "file:INDEPENDENT-RED-TEAM-LEDGER-RETRY-0002.json"]
    if number == 36:
        return "PARTIAL", "M2-RT-01 proved its marker was consumed and its clean control was VALID, but the complete battery could not execute.", ["file:INDEPENDENT-RED-TEAM-LEDGER-RETRY-0002.json"]
    if number == 37:
        return "FAIL", "M2-F-001 (High) and M2-F-002 (Critical) remain open and require an implementing checkpoint.", ["file:FINDINGS.json"]
    if number == 38:
        return "BLOCKED", "Fresh public no-credential validation passed, but complete verification could not start without Docker Engine access.", ["file:ENTRY-REPORT.md", "command:cmd-0007"]
    if number == 40:
        return "FAIL", "The audit checkpoint cannot pass its own assurance: command evidence is defective, Red Team failed, completeness is incomplete and Docker gates are blocked.", ["file:FINDINGS.json", "command:cmd-0013"]
    if number == 41:
        return "PARTIAL", "The report preserves commands, findings, attempts and limitations, but mandatory live/full evidence is incomplete.", ["file:FINAL-REPORT.md", "file:EXECUTION-NOTES.md"]
    if number == 42:
        return "PASS", "Codex/OpenAI/GPT-5 fresh-session attribution is explicit and cross-tool validation is truthfully NOT_AVAILABLE.", ["file:AUDITOR-INDEPENDENCE.json"]
    if number == 43:
        return "PASS", "Eligibility is false and no attestation was written.", ["file:FINDINGS.json", "file:AUDITOR-INDEPENDENCE.json"]
    if number == 44:
        return "PASS", "The evidence derives BLOCKED/REWORK_REQUIRED and grants neither independent nor external milestone PASS.", ["file:MILESTONE-REPORT.md", "file:FINAL-REPORT.md"]
    if number == 45:
        return "PASS", "No Gate 8 work or transition was created.", ["file:PLAN.md", "file:HANDOFF.md"]
    if number == 4:
        return "PARTIAL", "Selected historical public tags and current compatibility tests passed, but an explicit detached run for every Gate 4-7 sealed predecessor was not completed.", ["command:cmd-0010", "command:cmd-0011", "command:cmd-0015"]
    raise RuntimeError(f"no result mapping for criterion {number}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    checkpoint = args.checkpoint.resolve()
    frozen = json.loads((checkpoint / "FROZEN-M2-AUDIT-CRITERIA.json").read_text(encoding="utf-8"))
    rows = []
    for criterion in frozen["criteria"]:
        number = _number(criterion["id"])
        status, observation, evidence = _result(number)
        rows.append({**criterion, "status": status, "observation": observation, "evidence": evidence})
    counts = {name: sum(row["status"] == name for row in rows) for name in ("PASS", "FAIL", "PARTIAL", "BLOCKED")}
    if counts != {"PASS": 14, "FAIL": 8, "PARTIAL": 7, "BLOCKED": 16}:
        raise RuntimeError(f"unexpected result counts: {counts}")
    document = {
        "schemaVersion": "1.0.0",
        "artifact": "FINAL_M2_AUDIT_MATRIX",
        "checkpoint": checkpoint.name,
        "subjectCheckpoint": frozen["subjectCheckpoint"],
        "subjectCommit": frozen["subjectCommit"],
        "criteriaTotal": len(rows),
        "counts": counts,
        "criticalFindings": 1,
        "highFindings": 1,
        "auditExecutionStatus": "BLOCKED",
        "reviewVerdict": "REWORK_REQUIRED",
        "milestoneVerdict": "NOT_GRANTED",
        "independentAttestationWritten": False,
        "crossToolValidation": "NOT_AVAILABLE",
        "criteria": rows,
    }
    (checkpoint / "FINAL-M2-AUDIT-MATRIX.json").write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Final M2 audit matrix",
        "",
        f"Audit execution: **{document['auditExecutionStatus']}**. Review: **{document['reviewVerdict']}**. Milestone PASS: **not granted**.",
        "",
        f"Criteria: {len(rows)} — PASS {counts['PASS']}, FAIL {counts['FAIL']}, PARTIAL {counts['PARTIAL']}, BLOCKED {counts['BLOCKED']}.",
        "",
        "| ID | Status | Criterion | Observation |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| `{row['id']}` | `{row['status']}` | {row['criterion']} | {row['observation']} |")
    (checkpoint / "FINAL-M2-AUDIT-MATRIX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"M2_AUDIT_MATRIX=BLOCKED pass=14 fail=8 partial=7 blocked=16 total={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
