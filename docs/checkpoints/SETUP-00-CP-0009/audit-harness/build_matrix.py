#!/usr/bin/env python3
"""Build the FINAL-M0-AUDIT-MATRIX for SETUP-00-CP-0009 before substantive audit."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)
CP = ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0009"

rows: list[dict] = []


def add(rid, prompt_section, dimension, expected, method, mandatory=True):
    rows.append({
        "id": rid,
        "promptSection": prompt_section,
        "dimension": dimension,
        "expected": expected,
        "method": method,
        "mandatory": mandatory,
        "status": "NOT_STARTED",
        "observed": None,
        "evidence": [],
        "verdict": None,
    })


# --- Execution profile, cold start, baseline, matrix ----------------------------------
add("AUD-001", "1", "Execution profile recorded",
    "tool, version, provider, model, effort, OS, branch, commits and timestamps recorded truthfully",
    "inspect RUN-METADATA.json and STATE.json of this checkpoint")
add("AUD-002", "1,12,39", "Independence model recorded honestly",
    "freshSession true; sameTool/sameProvider recorded; crossToolValidation NOT_AVAILABLE",
    "inspect RUN-METADATA.json auditor block")
add("AUD-003", "4", "Cold start executed from the repository only",
    "every canonical document and CP-0007/CP-0008 artifact read from the repository",
    "recorded read list; no external summary used as evidence")
add("AUD-004", "5", "Baseline recorded",
    "git state captured; checkpoint validator run; worktree clean at baseline",
    "command evidence")
add("AUD-005", "6", "Audit matrix created before substantive audit",
    "matrix exists with every row NOT_STARTED before execution",
    "this artifact, in its pre-execution form")

# --- Section 8: canonical requirement derivation --------------------------------------
add("REQ-001", "8", "Canonical checklist re-parsed independently",
    "71 canonical rows parsed from docs/SETUP-00-CHECKLIST.md without using policies.py",
    "independent parser in the audit harness")
add("REQ-002", "8", "EXPECTED set re-derived independently",
    "EXPECTED = 71 canonical + 23 lesson + 11 finding + 26 attack anchored references",
    "independent derivation")
add("REQ-003", "8", "EXPECTED equals DECLARED exactly",
    "0 missing, 0 unexpected, 0 duplicated anchors against CP-0008 REQUIREMENTS-MATRIX.json",
    "set comparison")
add("REQ-004", "8", "Completeness and evidence coverage recomputed",
    "coverage 100.00 percent, evidence coverage 100.00 percent, 0 PARTIAL, 0 MISSING",
    "independent recomputation of every row and every evidence reference")

# --- Section 9: the eleven CP-0007 findings -------------------------------------------
FINDINGS = {
    "M0-F-001": "positive terminal status bypasses delivery assurance",
    "M0-F-002": "external milestone PASS self-asserted on an intermediate Gate",
    "M0-F-003": "lesson preflight not bound to the checkpoint Gate or canonical memory",
    "M0-F-004": "engineering memory accepts forged controls, missing evidence, nested secrets",
    "M0-F-005": "Green Keeper vacuous PASS path",
    "M0-F-006": "completeness denominator is not anchored",
    "M0-F-007": "historical immutability is not anchored externally",
    "M0-F-008": "CP-0006 mandatory count contradictory and accepted",
    "M0-F-009": "command records not reproducible at their declared commits",
    "M0-F-010": "sealed finalization chronology internally inconsistent",
    "M0-F-011": "one lesson source locator is inaccurate",
}
for fid, title in FINDINGS.items():
    add("F-" + fid[-3:], "9", "CP7 finding " + fid + " - " + title,
        "finding CLOSED: correction present, regression test present and representative, test executed green",
        "read closure record, read the regression test source, execute the test, attempt a safe bypass variation")

# --- Section 10: the original A-Z battery ---------------------------------------------
AZ = {
    "A": "readiness and blocker invariant", "B": "mandatory quality",
    "C": "completeness denominator", "D": "completeness claims",
    "E": "lesson-derived requirement", "F": "GUARDED semantics",
    "G": "lesson identity", "H": "lesson secret handling",
    "I": "sealed predecessor", "J": "tag immutability",
    "K": "file inventory entry", "L": "silent tracked modification",
    "M": "wrong hashBefore", "N": "wrong hashAfter",
    "O": "quality evidence", "P": "evidence resolution",
    "Q": "second-tool evidence", "R": "pass vocabulary",
    "S": "external milestone review", "T": "extraordinary cadence",
    "U": "preflight freshness", "V": "Green Keeper mandatory set",
    "W": "partial completeness", "X": "command audit",
    "Y": "latest pointer", "Z": "path safety",
}
for aid, target in AZ.items():
    add("RT-" + aid, "10", "CP7 mandatory attack " + aid + " - " + target,
        "DEFENDED in a synthetic fixture",
        "execute the attack against an isolated fixture clone and record the observed rejection")

# --- Section 11: external PASS / attestation ------------------------------------------
EXT = [
    ("EXT-001", "forged secondToolValidation"),
    ("EXT-002", "forged MILESTONE_EXTERNAL_PASS without attestation"),
    ("EXT-003", "attestation copied from another audit"),
    ("EXT-004", "attestation self-authored by the audited checkpoint"),
    ("EXT-005", "attestation naming the wrong subject checkpoint"),
    ("EXT-006", "attestation naming the wrong subject commit"),
    ("EXT-007", "review FAIL with attestation PASS"),
    ("EXT-008", "red team FAIL with attestation PASS"),
    ("EXT-009", "incomplete audit coverage with attestation PASS"),
    ("EXT-010", "attestation whose audit checkpoint is unsealed or not in the chain"),
]
for rid, desc in EXT:
    add(rid, "11", "External PASS forgery - " + desc, "rejected",
        "synthetic attestation fixture verified through attestation.py and the checkpoint validator")

# --- Section 12/39/40: independence and governance -------------------------------------
add("IND-001", "12,39", "Cross-tool validation not falsely claimed",
    "crossToolValidation recorded NOT_AVAILABLE; no PASSED claim for a mechanism that did not run",
    "inspect this checkpoint's recorded state and reports")
add("IND-002", "12,40", "Canonical policy position on cross-tool closure",
    "determine whether policy literally requires a different tool or provider for M0 closure and record a PROCESS_BLOCKER if the owner decision does not cover it",
    "read MILESTONE-VALIDATION.md, QUALITY-GATES.md and the validator implementation")
add("GOV-001", "40", "Owner governance decision recorded without weakening another gate",
    "the FRESH_SESSION_INDEPENDENT_AUDIT mechanism is versioned and explicit; no other gate weakened",
    "diff of governance documents in this checkpoint")

# --- Section 13: Green Keeper ----------------------------------------------------------
GK = [
    ("GK-001", "requiredGates empty"),
    ("GK-002", "mandatory gate omitted from the run"),
    ("GK-003", "mandatory gate NOT_EXECUTED"),
    ("GK-004", "mandatory gate FAIL"),
    ("GK-005", "gate evidence absent"),
    ("GK-006", "remainingFailures greater than zero with PASS"),
    ("GK-007", "unresolvedReworkItems greater than zero with PASS"),
    ("GK-008", "fabricated PASS cycle in the rework log"),
    ("GK-009", "stale PASS after a relevant scope change"),
]
for rid, desc in GK:
    add(rid, "13", "Green Keeper - " + desc, "rejected",
        "synthetic fixture mutation validated through green_keeper.py and validate_checkpoint.py")
add("GK-010", "13", "Mandatory gate set derived from policy, not the caller",
    "the mandatory set comes from .iacode/policies/quality-gates.json and --gates can only extend it",
    "read the implementation and prove it with a fixture")

# --- Section 14: delivery completeness -------------------------------------------------
DC = [
    ("DC-001", "canonical requirement removed"),
    ("DC-002", "lesson-derived requirement removed"),
    ("DC-003", "audit-finding requirement removed"),
    ("DC-004", "audit-attack requirement removed"),
    ("DC-005", "denominator decreased"),
    ("DC-006", "total falsified upward"),
    ("DC-007", "coverage forged to 100 over an incomplete matrix"),
    ("DC-008", "report claiming 100 percent over an incomplete matrix"),
    ("DC-009", "COMPLETE row without evidence"),
    ("DC-010", "evidence reference that does not resolve"),
    ("DC-011", "evidence referencing a command that failed"),
]
for rid, desc in DC:
    add(rid, "14,30", "Delivery completeness - " + desc, "rejected",
        "synthetic fixture mutation validated through check_completeness.py and validate_checkpoint.py")

# --- Section 15: preflight freshness ---------------------------------------------------
PRE = [
    ("PRE-001", "an active lesson changed"),
    ("PRE-002", "a lesson retired"),
    ("PRE-003", "applicability changed"),
    ("PRE-004", "the guardrail registry changed"),
    ("PRE-005", "the lesson schema or selection policy changed"),
    ("PRE-006", "the Gate or scope changed"),
]
for rid, desc in PRE:
    add(rid, "15", "Preflight freshness - " + desc,
        "the previous preflight becomes STALE or INVALID and a regenerated preflight passes",
        "fixture mutation plus recomputation of inputsFingerprint")

# --- Section 16: engineering memory ----------------------------------------------------
MEM = [
    ("MEM-001", "lesson counts recomputed from the registry, not from a report"),
    ("MEM-002", "every GUARDED lesson resolves lesson to guardrail to registry to control to test to execution"),
    ("MEM-003", "documentation-only prevention never yields GUARDED"),
    ("MEM-004", "provenance of every lesson resolves to a real checkpoint and finding"),
    ("MEM-005", "trainingAllowed is false by default across the memory"),
    ("MEM-006", "recurrenceCount and GUARDRAIL_FAILURE lifecycle behave as specified"),
    ("MEM-007", "lesson status lifecycle is valid and SUPERSEDED or RETIRED derive no requirement"),
    ("MEM-008", "every applicable lesson became a requirement of the delivery"),
]
for rid, desc in MEM:
    add(rid, "16", "Engineering memory - " + desc, "verified by recomputation and execution",
        "independent recomputation from .iacode/memory plus targeted fixtures")

# --- Section 17: the four previously bypassable guardrails ------------------------------
for lesson in ("LSN-0005", "LSN-0007", "LSN-0008", "LSN-0009"):
    add("GRD-" + lesson, "17", "Previously bypassed guardrail " + lesson,
        "the CP-0007 bypass is now blocked, and a reasonable variation of it is also blocked",
        "reproduce the original bypass in a safe fixture, then a variation")

# --- Section 18: guardrail effectiveness ------------------------------------------------
add("GRE-001", "18", "Guardrail effectiveness recomputed",
    "guardrailsTotal, Resolved, Tested and Effective recomputed independently and guardrailFailures is zero",
    "independent recomputation from the registry and the suite")

# --- Section 19: history and tag integrity ----------------------------------------------
HIST = [
    ("HIST-001", "historical tag moved"),
    ("HIST-002", "anchor names the wrong tag"),
    ("HIST-003", "anchor names the wrong commit"),
    ("HIST-004", "anchor names the wrong tree"),
    ("HIST-005", "previous-anchor digest wrong"),
    ("HIST-006", "chain link removed"),
    ("HIST-007", "anchor names the wrong previous checkpoint"),
]
for rid, desc in HIST:
    add(rid, "19", "History integrity - " + desc, "rejected",
        "temporary Git fixture repository; the real repository and its tags are never modified")
add("HIST-008", "19", "CP-0001 through CP-0007 intact",
    "every sealed tag still resolves to its recorded commit and tree under read-only inspection",
    "git rev-parse and cat-file over the real repository, read-only")

# --- Section 20: CP-0008 successor anchor -----------------------------------------------
add("ANC-001", "20", "CP-0008 successor anchor architecture",
    "this audit checkpoint can legitimately anchor CP-0008 without modifying CP-0008",
    "produce the anchor and validate the chain")

# --- Section 21: semantic counts ---------------------------------------------------------
CNT = [
    ("CNT-001", "SETUP requirements"), ("CNT-002", "M0 closure requirements"),
    ("CNT-003", "findings"), ("CNT-004", "tests"), ("CNT-005", "lessons"),
    ("CNT-006", "guardrails"), ("CNT-007", "attacks"),
]
for rid, desc in CNT:
    add(rid, "21", "Semantic count - " + desc,
        "recomputed from the machine-readable owner and consistent wherever current artifacts state it",
        "independent recomputation plus cross-artifact comparison")

# --- Section 22: full suite and mandatory validators --------------------------------------
TST = [
    ("TST-001", "unit and integration suite via unittest discovery over tests/"),
    ("TST-002", "static analysis via compileall"),
    ("TST-003", "checkpoint validator"),
    ("TST-004", "lesson validator"),
    ("TST-005", "integrity validator"),
    ("TST-006", "completeness validator"),
    ("TST-007", "green keeper and delivery assurance"),
    ("TST-008", "secret policy scan"),
    ("TST-009", "git diff --check"),
    ("TST-010", "derived counts validator"),
]
for rid, desc in TST:
    add(rid, "22", "Mandatory execution - " + desc,
        "executed and green, with the real observed value recorded",
        "execute the repository's own official command")

# --- Section 23: clean clone ---------------------------------------------------------------
add("CLN-001", "23", "Clean clone of the subject commit validates",
    "a detached clone at the CP-0008 tag validates and the full suite passes",
    "isolated clone in a disposable workspace")
add("CLN-002", "23", "No dependency on untracked files, local cache or session state",
    "the clean clone runs every mandatory validator without anything outside the repository",
    "execute the validators in the clone")
add("CLN-003", "23", "No dependency on an external prompt or attachment",
    "every mandatory SETUP artifact is inside the repository",
    "inventory of referenced artifacts")

# --- Section 24: new surfaces ---------------------------------------------------------------
NS = [
    ("NS-001", "external audit attestation", "scripts/development-ledger/attestation.py"),
    ("NS-002", "canonical requirements registry", "scripts/development-ledger/policies.py"),
    ("NS-003", "quality gate registry", ".iacode/policies/quality-gates.json"),
    ("NS-004", "preflight fingerprint", "scripts/development-ledger/lesson_preflight.py"),
    ("NS-005", "guardrail registry", ".iacode/memory/guardrails/registry.json"),
    ("NS-006", "checkpoint anchor chain", "scripts/development-ledger/anchors.py"),
]
for rid, desc, impl in NS:
    add(rid, "24", "New surface - " + desc,
        "implementation inspected, its tests read and executed, and one additional safe negative scenario run",
        "read " + impl + ", execute its tests, add an independent negative fixture")

# --- Section 25: additional red team (surfaces introduced by CP-0008) ------------------------
ADD = {
    "AA": "aggregate consistency", "AB": "control resolution", "AC": "evidence resolution",
    "AD": "nested secret scan", "AE": "preflight gate binding", "AF": "promotion invariant",
    "AG": "gate registry narrowing", "AH": "gate staleness", "AI": "external attestation self-audit",
    "AJ": "external attestation over a failed review", "AK": "attestation of a different commit",
    "AL": "forged derived count", "AM": "count contradiction in Markdown",
    "AN": "open audit finding", "AO": "internal Red Team false PASS",
    "AP": "internal mirror false PASS", "AQ": "guardrail verified by a nonexistent test",
    "AR": "broken anchor link", "AS": "command input binding removed",
    "AT": "seal chronology evidence removed",
}
for aid, target in ADD.items():
    add("ART-" + aid, "25", "Additional attack " + aid + " - " + target,
        "DEFENDED in a synthetic fixture",
        "execute the attack against an isolated fixture clone")

# --- Sections 26-28: staleness ----------------------------------------------------------------
add("STL-001", "26", "Green Keeper staleness",
    "a PASS recorded before a relevant scope change is refused until re-execution",
    "fixture: mutate the assurance scope after a green cycle")
add("STL-002", "27", "Delivery completeness staleness",
    "a completeness PASS is refused after requirements, lessons, policy or implementation change",
    "fixture: mutate the scope after the report")
add("STL-003", "28", "Internal Red Team and mirror staleness",
    "an attacked control changing after the Red Team makes the previous result stale",
    "fixture: mutate the scope after the report")

# --- Section 29: command auditability ------------------------------------------------------------
add("CMD-001", "29", "Command records carry every reproducibility field",
    "runtime, cwd, command, sanitized arguments, inputs, commit, purpose, result and duration present",
    "schema recomputation over CP-0008 COMMANDS.jsonl")
add("CMD-002", "29", "Representative command sample reproduces",
    "a deterministic sample of safe, read-only commands replays with the recorded result",
    "replay in an isolated checkout")
add("CMD-003", "29", "Declared inputs are bound by content",
    "every declared input resolves and its recorded digest matches the content at the declared commit",
    "recomputation")

# --- Section 30: evidence integrity ---------------------------------------------------------------
EVD = [
    ("EVD-001", "PASS without evidence"),
    ("EVD-002", "evidence file that does not exist"),
    ("EVD-003", "command reference that does not exist"),
    ("EVD-004", "command reference whose record failed"),
    ("EVD-005", "evidence file that exists but is empty"),
    ("EVD-006", "stale evidence describing older content"),
]
for rid, desc in EVD:
    add(rid, "30", "Evidence integrity - " + desc, "rejected",
        "synthetic fixture through validate_checkpoint.py")

# --- Sections 31-33 ------------------------------------------------------------------------------
add("SCR-001", "31", "Self-contained repository",
    "a new session can reconstruct the state from the repository alone and START-HERE leads to the needed context",
    "cold-start simulation from the clean clone")
DOC = [
    ("DOC-001", "internal documentation links resolve"),
    ("DOC-002", "no missing referenced artifact"),
    ("DOC-003", "no stale checkpoint reference or contradictory status"),
    ("DOC-004", "no contradictory instruction that could make another tool act wrongly"),
]
for rid, desc in DOC:
    add(rid, "32", "Documentation integrity - " + desc, "verified",
        "link resolution and consistency recomputation")
add("SAF-001", "33", "Safe reproduction available for every critical control",
    "no critical integrity, security, governance, auditability or quality control lacks a safe reproduction",
    "inventory of controls against the fixtures that exercise them")

# --- Sections 34-38, 41-46 -------------------------------------------------------------------------
add("AUD-006", "34", "Audit of the audit",
    "matrix recomputed: mandatory equals complete, zero failed, zero unverified, zero not started, zero missing evidence",
    "recomputation of this matrix")
add("FND-001", "35", "Consolidated findings package",
    "every finding carries id, severity, source rows, expected, observed, reproduction, evidence, acceptance and regression scenario",
    "REVIEW-REPORT.md of this checkpoint")
add("LSC-001", "36", "Lesson candidates recorded and the memory unchanged by the audit",
    "LESSON-CANDIDATES.json and .md produced; .iacode/memory not modified by this audit",
    "artifact plus git diff")
add("TFP-001", "37", "Test failure policy applied",
    "every red result classified PRODUCT_DEFECT, AUDIT_ENVIRONMENT or FLAKY, with no rerun-until-green",
    "recorded classification")
add("CKP-001", "38", "Audit checkpoint complete",
    "every artifact required by the current schema plus the audit-specific artifacts exists",
    "checkpoint validator")
add("CKP-002", "45", "This checkpoint validates from a clean detached checkout",
    "CP-0009 validates at its own sealed tag with a clean worktree",
    "detached validation in an isolated clone")
add("VER-001", "41,42", "Binary verdict",
    "MILESTONE_AUDIT_PASS or REWORK_REQUIRED, with no conditional wording",
    "this checkpoint's reports")
add("VER-002", "43,44,46", "Final state and reporting",
    "recorded state and final response match the evidence exactly",
    "FINAL-REPORT.md and the session response")

matrix = {
    "schemaVersion": "1.0.0",
    "artifact": "FINAL-M0-AUDIT-MATRIX",
    "checkpoint": "SETUP-00-CP-0009",
    "milestone": "M0",
    "gate": "SETUP-00",
    "subjectCheckpoint": "SETUP-00-CP-0008",
    "subjectCommit": "c53f4c59a77870414324efa6b5f61b35d26c5090",
    "auditMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
    "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "note": "Created before substantive audit execution. Every row starts NOT_STARTED.",
    "allowedStatuses": ["NOT_STARTED", "IN_PROGRESS", "COMPLETE", "FAILED", "UNVERIFIED"],
    "rows": rows,
    "summary": {
        "total": len(rows),
        "mandatory": sum(1 for r in rows if r["mandatory"]),
        "complete": 0, "failed": 0, "unverified": 0,
        "inProgress": 0, "notStarted": len(rows),
        "missingEvidence": len(rows),
        "coveragePercent": 0.0, "evidenceCoveragePercent": 0.0,
    },
}
ids = [r["id"] for r in rows]
assert len(ids) == len(set(ids)), "duplicate row id"
CP.mkdir(parents=True, exist_ok=True)
(CP / "FINAL-M0-AUDIT-MATRIX.json").write_text(
    json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")
print("rows=" + str(len(rows)) + " mandatory=" + str(matrix["summary"]["mandatory"]))
