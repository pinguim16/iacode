#!/usr/bin/env python3
"""Fill the FINAL-M0-AUDIT-MATRIX from the recorded audit evidence and render it."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

AUDIT = Path(_os.environ.get("IACODE_AUDIT_OUT") or (_DEFAULT_ROOT / "audit-out"))
CP = _DEFAULT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0009"
MATRIX = CP / "FINAL-M0-AUDIT-MATRIX.json"


def load(relative: str):
    path = AUDIT / relative
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


battery = {item["attackId"]: item for item in (load("battery/attack-results.json") or [])}
scenarios = {item["id"]: item for item in (load("scenarios/scenario-results.json") or [])}
preflight = {item["id"]: item for item in (load("preflight/preflight-results.json") or [])}
guardrails = {item["id"]: item for item in (load("guardrails/guardrail-results.json") or [])}
attestation = {item["id"]: item for item in (load("attestation/attestation-results.json") or [])}
history = {item["id"]: item for item in (load("history/history-results.json") or [])}
counts = load("counts/counts-docs.json") or {}
commands = load("commands/command-audit.json") or {}
reachability = load("work4/ext-reachability.json") or {}
memory = load("memory/memory-results.json") or {}
executions = load("audit-executions.json") or {}

matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
rows = {row["id"]: row for row in matrix["rows"]}


def brief(text, limit: int = 260) -> str:
    if isinstance(text, list):
        text = " | ".join(str(item) for item in text)
    text = " ".join(str(text).split())
    return text[:limit]


def set_row(row_id: str, status: str, observed, evidence, verdict: str = "PASS") -> None:
    row = rows[row_id]
    row["status"] = status
    row["observed"] = brief(observed)
    row["evidence"] = list(evidence)
    row["verdict"] = verdict


def add_row(row_id, prompt_section, dimension, expected, method, reason) -> None:
    row = {"id": row_id, "promptSection": prompt_section, "dimension": dimension,
           "expected": expected, "method": method, "mandatory": True,
           "addedDuringExecution": True, "addedBecause": reason,
           "status": "NOT_STARTED", "observed": None, "evidence": [], "verdict": None}
    matrix["rows"].append(row)
    rows[row_id] = row


# --------------------------------------------------------------------------- added rows
add_row("EXT-011", "11", "Positive control - a legitimate attestation is accepted",
        "a structurally valid attestation passes verification",
        "call attestation.verify_attestation with a valid document",
        "section 11 audits a control; a control that refuses every input, including the true "
        "one, is not a control, so the positive path has to be executed too")
add_row("EXT-012", "11,43",
        "End-to-end reachability of MILESTONE_EXTERNAL_PASS",
        "a legitimately attested subject can actually reach MILESTONE_EXTERNAL_PASS",
        "build the most favourable legitimate promotion in a disposable clone",
        "the rejection scenarios alone cannot show whether the mechanism can ever be satisfied")
add_row("TST-011", "22,23",
        "The sealed suite stays green for the next delivery",
        "sealing the next checkpoint does not make a mandatory gate red",
        "simulate the next sealed checkpoint in a disposable clone and run the suite",
        "the tests gate is mandatory for every delivery, so its durability past this seal is "
        "part of auditing the delivery that seals it")

# --------------------------------------------------------------------------- 1-6
set_row("AUD-001", "COMPLETE",
        "RUN-METADATA.json records tool Claude Code 2.1.195, provider Anthropic, model "
        "claude-opus-5, effort not-exposed, Windows 11 10.0.26200, branch main, initial and "
        "final commit, startedAt and finishedAt",
        ["checkpoint:RUN-METADATA.json", "checkpoint:STATE.json"])
set_row("AUD-002", "COMPLETE",
        "auditor.freshSession=true, sameToolAsImplementer=true, sameProviderAsImplementer=true, "
        "crossToolValidation=NOT_AVAILABLE, freshSessionIndependentAudit recorded",
        ["checkpoint:RUN-METADATA.json", "checkpoint:MILESTONE-REPORT.md"])
set_row("AUD-003", "COMPLETE",
        "13 canonical documents plus SETUP-00-CP-0007 and SETUP-00-CP-0008 read from the "
        "repository; no external summary used as evidence",
        ["checkpoint:AUDIT-EXECUTIONS.md"])
set_row("AUD-004", "COMPLETE",
        "baseline captured: branch main, HEAD c53f4c5, clean worktree after the stale scaffold "
        "was removed; CHECKPOINT_VALID on the branch and from a detached clone of the CP-0008 tag",
        ["command:cmd-0002", "command:cmd-0003", "checkpoint:AUDIT-EXECUTIONS.md"])
set_row("AUD-005", "COMPLETE",
        "the matrix was written with 180 rows, every row NOT_STARTED, before any substantive "
        "audit step; three further rows were added during execution and are flagged "
        "addedDuringExecution with the reason",
        ["checkpoint:FINAL-M0-AUDIT-MATRIX.json", "checkpoint:DECISIONS.md"])

# --------------------------------------------------------------------------- 8
set_row("REQ-001", "COMPLETE",
        "71 canonical rows parsed from docs/SETUP-00-CHECKLIST.md by an independent parser that "
        "does not import policies.py",
        ["checkpoint:audit-harness/derive_expected.py", "checkpoint:AUDIT-EXECUTIONS.json"])
set_row("REQ-002", "COMPLETE",
        "EXPECTED = 71 canonical + 23 lesson + 11 finding + 26 attack = 131 anchored references, "
        "re-derived from the checklist, the sealed CP-0007 reports and the preflight",
        ["checkpoint:audit-harness/derive_expected.py", "checkpoint:AUDIT-EXECUTIONS.json"])
set_row("REQ-003", "COMPLETE",
        "declared 131, expected 131, missing 0, unexpected 0, duplicated 0, local rows 0",
        ["checkpoint:AUDIT-EXECUTIONS.json"])
set_row("REQ-004", "COMPLETE",
        "coverage 100.00 and evidence coverage 100.00 recomputed; 131 COMPLETE, 0 PARTIAL, "
        "0 MISSING; check_completeness.py reproduced the same values in a clean clone",
        ["command:cmd-0006", "checkpoint:AUDIT-EXECUTIONS.json"])

# --------------------------------------------------------------------------- 9
FINDING_TESTS = load("finding-tests.json") or {"findings": []}
for entry in FINDING_TESTS["findings"]:
    row_id = "F-" + entry["id"][-3:]
    set_row(row_id, "COMPLETE",
            entry["id"] + " " + str(entry["status"]) + "; lesson " + str(entry["lesson"])
            + "; guardrail " + str(entry["guardrail"]) + "; "
            + str(len(entry["tests"])) + " regression and negative tests read and executed green",
            ["checkpoint:AUDIT-EXECUTIONS.md", "command:cmd-0010"])

# --------------------------------------------------------------------------- 10 and 25
for attack_id, item in battery.items():
    row_id = ("RT-" + attack_id) if len(attack_id) == 1 else ("ART-" + attack_id)
    if row_id not in rows:
        continue
    set_row(row_id, "COMPLETE", item["observed"], ["checkpoint:AUDIT-EXECUTIONS.json"],
            item["result"])

# --------------------------------------------------------------------------- 11
EXT_MAP = {"EXT-001": "EXT-001", "EXT-002": "EXT-002", "EXT-003": "EXT-003",
           "EXT-004": "EXT-004", "EXT-005": "EXT-005", "EXT-006": "EXT-006",
           "EXT-007": "EXT-007", "EXT-008": "EXT-008", "EXT-009": "EXT-009",
           "EXT-010": "EXT-010"}
for row_id, probe_id in EXT_MAP.items():
    item = attestation[probe_id]
    set_row(row_id, "COMPLETE", item["observed"], ["checkpoint:AUDIT-EXECUTIONS.json"],
            item["result"])
set_row("EXT-011", "COMPLETE", attestation["EXT-000"]["observed"],
        ["checkpoint:AUDIT-EXECUTIONS.json"], attestation["EXT-000"]["result"])
set_row("EXT-012", "FAILED",
        "no repository state satisfies the promotion: the attestation must live in the tree of "
        "the commit it names as subjectCommit. Three attempts and a fixed-point iteration all "
        "fail with 'attests commit X, not the subject commit Y'; and once the attestation is "
        "committed by the audit checkpoint, the subject can no longer be validated at all "
        "(commit mismatch against its own tag)",
        ["checkpoint:AUDIT-EXECUTIONS.json", "checkpoint:audit-harness/ext_reachability.py",
         "checkpoint:REVIEW-REPORT.md"], "FAIL")

# --------------------------------------------------------------------------- 12, 39, 40
set_row("IND-001", "COMPLETE",
        "crossToolValidation is recorded NOT_AVAILABLE; the implementer of CP-0008 and this "
        "auditor are both Claude Code on Anthropic, in different sessions",
        ["checkpoint:RUN-METADATA.json", "checkpoint:MILESTONE-REPORT.md"])
set_row("IND-002", "COMPLETE",
        "docs/MILESTONE-VALIDATION.md and docs/QUALITY-GATES.md require an independent tool and "
        "a derived attestation, not literally a different vendor; attestation.py enforces a "
        "different sealed checkpoint, never a different provider. The owner authorisation for "
        "FRESH_SESSION_INDEPENDENT_AUDIT is therefore consistent with the canonical mechanism, "
        "and no PROCESS_BLOCKER arises from the same-tool limitation itself",
        ["checkpoint:MILESTONE-REPORT.md", "file:docs/MILESTONE-VALIDATION.md",
         "file:scripts/development-ledger/attestation.py"])
set_row("GOV-001", "COMPLETE",
        "no governance document was weakened; the audit changed no policy, no gate, no test and "
        "no canonical memory. The owner decision is recorded in this checkpoint rather than by "
        "editing a gate",
        ["checkpoint:DECISIONS.md", "checkpoint:MILESTONE-REPORT.md"])

# --------------------------------------------------------------------------- 13, 14, 26-28, 30
for row_id in ["GK-001", "GK-002", "GK-003", "GK-004", "GK-005", "GK-006", "GK-007",
               "GK-008", "GK-009", "GK-010",
               "DC-001", "DC-002", "DC-003", "DC-004", "DC-005", "DC-006", "DC-007",
               "DC-008", "DC-009", "DC-010", "DC-011",
               "EVD-001", "EVD-002", "EVD-003", "EVD-004", "EVD-005", "EVD-006",
               "STL-001", "STL-002"]:
    item = scenarios[row_id]
    set_row(row_id, "COMPLETE", item["observed"], ["checkpoint:AUDIT-EXECUTIONS.json"],
            item["result"])
set_row("STL-003", "COMPLETE",
        "internal Red Team: " + brief(scenarios["STL-003a"]["observed"], 120)
        + " ;; internal mirror: " + brief(scenarios["STL-003b"]["observed"], 120)
        + " ;; a false PASS over an escaped attack or a failed mirror check is also refused",
        ["checkpoint:AUDIT-EXECUTIONS.json"],
        "DEFENDED" if scenarios["STL-003a"]["result"] == "DEFENDED"
        and scenarios["STL-003b"]["result"] == "DEFENDED" else "ESCAPED")

# --------------------------------------------------------------------------- 15
PRE_MAP = {"PRE-001": "PRE-001", "PRE-002": "PRE-002", "PRE-003": "PRE-003",
           "PRE-004": "PRE-004", "PRE-006": "PRE-006"}
for row_id, probe_id in PRE_MAP.items():
    item = preflight[probe_id]
    set_row(row_id, "COMPLETE",
            "stored preflight stale=" + str(item["storedStale"])
            + ", regenerated preflight fresh=" + str(item["regeneratedFresh"])
            + " :: " + brief(item["observed"], 160),
            ["checkpoint:AUDIT-EXECUTIONS.json"], item["result"])
set_row("PRE-005", "COMPLETE",
        "changing the lesson schema makes the stored preflight STALE; bumping the memory policy "
        "version makes it STALE; an inert prose edit to POLICY.json correctly does not, because "
        "the fingerprint covers the policy version, the schema, the memory and the registry "
        "content rather than the prose",
        ["checkpoint:AUDIT-EXECUTIONS.json"], "DEFENDED")

# --------------------------------------------------------------------------- 16, 18
MEM_OBSERVED = {
    "MEM-001": "recomputed directly from .iacode/memory/lessons.jsonl: 23 lessons, 22 GUARDED, "
               "1 CONFIRMED; identical to COUNTS.json LESSONS 22/23 and to STATE",
    "MEM-002": "all 22 GUARDED lessons resolve lesson -> guardrailId -> registry entry -> control "
               "-> verifying tests -> execution; 22/22 controls resolve, 22/22 verifying tests "
               "exist in the 306-case suite and were executed green",
    "MEM-003": "a GUARDED lesson whose prevention is documentation only is refused "
               "(attack F); a control naming a nonexistent test is refused (attacks AB, AQ)",
    "MEM-004": "every lesson provenance resolves: each cited checkpoint exists and each finding "
               "identifier appears in the evidence of a checkpoint the lesson names; "
               "LSN-0007, the CP-0007 M0-F-011 defect, now cites the correct checkpoint",
    "MEM-005": "trainingAllowed is false for all 23 lessons; no rights justification is claimed",
    "MEM-006": "register_recurrence escalates a repeat against a GUARDED lesson to "
               "CONFIRMED with a GUARDRAIL_FAILURE and raises severity; validation refuses "
               "GUARDED while a failure is unresolved and accepts it once the failure names the "
               "repairing checkpoint",
    "MEM-007": "statuses are within the documented lifecycle; retiring a lesson removes its "
               "derived requirement (23 -> 22) and makes the stored preflight STALE",
    "MEM-008": "23 active lessons, 23 derived requirements, 23 lesson rows in the matrix; "
               "no active lesson without a requirement and no requirement without a lesson",
}
for row_id, observed in MEM_OBSERVED.items():
    set_row(row_id, "COMPLETE", observed, ["checkpoint:AUDIT-EXECUTIONS.md"], "PASS")
set_row("GRE-001", "COMPLETE",
        "independent recomputation: total 22, resolved 22, tested 22, effective 22, "
        "unresolved guardrail failures 0; identical to guardrail_effectiveness() and to "
        "STATE.guardrailEffectiveness. Six resolved guardrail failures are recorded against "
        "LSN-0005, LSN-0007, LSN-0008, LSN-0009, LSN-0010 and LSN-0012, each naming "
        "SETUP-00-CP-0008 as the repairing checkpoint",
        ["checkpoint:AUDIT-EXECUTIONS.md"], "PASS")

# --------------------------------------------------------------------------- 17
for lesson in ("LSN-0005", "LSN-0007", "LSN-0008", "LSN-0009"):
    original = guardrails["GRD-" + lesson + "-original"]
    variation = guardrails["GRD-" + lesson + "-variation"]
    set_row("GRD-" + lesson, "COMPLETE",
            "original bypass: " + brief(original["observed"], 150)
            + " ;; variation: " + brief(variation["observed"], 150),
            ["checkpoint:AUDIT-EXECUTIONS.json"],
            "DEFENDED" if original["result"] == "DEFENDED"
            and variation["result"] == "DEFENDED" else "ESCAPED")

# --------------------------------------------------------------------------- 19
for row_id in ("HIST-001", "HIST-002", "HIST-003", "HIST-004", "HIST-005", "HIST-006",
               "HIST-007"):
    item = history[row_id]
    set_row(row_id, "COMPLETE", item["observed"], ["checkpoint:AUDIT-EXECUTIONS.json"],
            item["result"])
set_row("HIST-008", "COMPLETE",
        "read-only inspection of the real repository: all 7 sealed anchors match their tag, "
        "commit, tree, predecessor and digest; no tag in the real repository was written to",
        ["checkpoint:AUDIT-EXECUTIONS.json"], "PASS")

# --------------------------------------------------------------------------- 20
set_row("ANC-001", "COMPLETE",
        "this audit checkpoint anchors SETUP-00-CP-0008 without modifying it: "
        "verify_integrity.py --rebuild adds the eighth anchor over the sealed tag, commit and "
        "tree, and the chain verifies with this checkpoint excluded as the one being sealed",
        ["command:cmd-0016", "file:.iacode/anchors/checkpoint-chain.json"], "PASS")

# --------------------------------------------------------------------------- 21
derived = counts.get("counts", {}).get("derived", {})
set_row("CNT-001", "COMPLETE",
        "71 canonical SETUP-00 rows re-parsed; matches the registry and the matrix",
        ["checkpoint:AUDIT-EXECUTIONS.json"])
set_row("CNT-002", "COMPLETE",
        "131 M0 closure requirements, 130 mandatory; matches STATE, the report and COUNTS.json",
        ["checkpoint:AUDIT-EXECUTIONS.json"])
set_row("CNT-003", "COMPLETE",
        "11 findings parsed from the sealed CP-0007 review report, 11 CLOSED in the closure record",
        ["checkpoint:AUDIT-EXECUTIONS.json"])
set_row("CNT-004", "COMPLETE",
        "306 test cases discovered; matches COUNTS.json and the executed suite",
        ["command:cmd-0004", "checkpoint:AUDIT-EXECUTIONS.json"])
set_row("CNT-005", "COMPLETE",
        "23 lessons, 22 GUARDED; matches COUNTS.json LESSONS 22/23",
        ["checkpoint:AUDIT-EXECUTIONS.json"])
set_row("CNT-006", "COMPLETE",
        "22 guardrails; matches COUNTS.json and STATE.guardrailEffectiveness",
        ["checkpoint:AUDIT-EXECUTIONS.json"])
set_row("CNT-007", "COMPLETE",
        "18 cross-artifact comparisons between the derivation and COUNTS.json, STATE.json and "
        "COMPLETENESS-REPORT.json: 0 mismatches; 8 Markdown N/M claims, all consistent",
        ["checkpoint:AUDIT-EXECUTIONS.json"])

matrix["summary"]["recomputedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
MATRIX.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")
print("part 1 recorded; rows now " + str(len(matrix["rows"])))
