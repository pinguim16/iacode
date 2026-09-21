#!/usr/bin/env python3
"""Row definitions for the final M0 audit matrix.

Rows that describe repository content are derived from the repository so the matrix cannot drift
from what it audits. Rows that describe audit obligations come from the audit mandate itself.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CP10 = ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0010"
CP09 = ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0009"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _row(identifier, section, dimension, expected, method, mandatory=True):
    return {
        "id": identifier,
        "promptSection": section,
        "dimension": dimension,
        "expected": expected,
        "method": method,
        "mandatory": bool(mandatory),
        "status": "NOT_STARTED",
        "observed": None,
        "evidence": [],
        "verdict": None,
    }


def finding_rows() -> list[dict]:
    """One row per CP-0009 finding, plus the specific proofs the audit mandate requires."""
    rows: list[dict] = []
    closure = _load(CP10 / "CP9-FINDINGS-CLOSURE.json")
    findings = closure.get("findings", closure.get("closures", []))
    for index, finding in enumerate(findings, start=1):
        identifier = finding.get("findingId") or finding.get("id")
        rows.append(_row(
            f"FND-{index:03d}", "2-6",
            f"{identifier} closed",
            f"{identifier} is closed by an implementation this audit can observe, not by an "
            f"assertion in the delivery",
            "independent inspection of the named implementation and execution of the named tests"))
        rows[-1]["findingId"] = identifier
    proofs = [
        ("F1A", "CP9-F-001 subject immutability",
         "SETUP-00-CP-0010 is never rewritten, re-tagged or re-sealed to become approved",
         "compare the sealed tag, commit and tree of the subject before and after the audit"),
        ("F1B", "CP9-F-001 attestation location",
         "the attestation lives in the audit checkpoint, not in the subject",
         "inspect the attestation model and the tree of the sealed subject commit"),
        ("F1C", "CP9-F-001 no subject self-reference",
         "no attestation has to name the commit of the tree that contains it",
         "read attestation.py and execute the promotion fixture"),
        ("F1D", "CP9-F-001 positive attestation accepted",
         "a structurally valid attestation over a sealed subject is accepted end to end",
         "execute a two-checkpoint promotion fixture in a disposable repository"),
        ("F1E", "CP9-F-001 forgeries still refused",
         "every invalid attestation shape is still refused after the repair",
         "execute an attestation probe battery written by this audit"),
        ("F1F", "CP9-F-001 audit checkpoint sealable",
         "a valid audit checkpoint validates and seals",
         "seal the fixture audit checkpoint and validate it"),
        ("F1G", "CP9-F-001 milestone PASS reachable",
         "milestone_status.py derives PASSED from an honest sequence of repository states",
         "execute milestone_status.py inside the promotion fixture"),
        ("F1H", "CP9-F-001 subject assurance not stale",
         "creating the audit checkpoint does not make the assurance results of the subject stale",
         "validate the subject from its canonical tag after the audit checkpoint exists"),
        ("F1I", "CP9-F-001 honest mechanism semantics",
         "the derived status names the mechanism and refuses the status the evidence does not "
         "support",
         "derive the verdict and attempt the cross-tool status from a fresh-session attestation"),
        ("F1J", "CP9-F-001 positive fixture present",
         "a positive fixture exists in the product, not only in the audit",
         "inspect promotion_fixture.py and the tests that consume it"),
        ("F2A", "CP9-F-002 no literal checkpoint identifiers",
         "no generic executable integrity logic depends on a literal historical checkpoint id",
         "scan scripts and tests for historical checkpoint literals and classify every hit"),
        ("F2B", "CP9-F-002 successor durability",
         "A, then B anchoring A and sealing, then C anchoring B and sealing, stays green at every "
         "state",
         "execute the three-checkpoint succession and run the integrity controls at every state"),
        ("F3A", "CP9-F-003 stale cardinality gone",
         "the superseded requirement-set cardinality is absent from every current artifact",
         "scan the working tree for the stale cardinality"),
        ("F3B", "CP9-F-003 prose counts are not authoritative",
         "no comment or docstring in scripts or tests states a derived count, and the policy is "
         "documented",
         "re-implement the control independently and compare with the documented decision"),
        ("F4A", "CP9-F-004 lesson prose agrees with status",
         "LSN-0014 status, guardrail and residual-limit note agree",
         "read the lesson record, the guardrail registry and the refusal control"),
        ("F5A", "CP9-F-005 no dead policy key",
         "guardrailRegistry is either consumed and tested, or removed and documented as fixed",
         "inspect the policy document, its schema and every reader of the registry path"),
    ]
    for identifier, dimension, expected, method in proofs:
        rows.append(_row(f"FND-{identifier}", "2-6", dimension, expected, method))
    return rows


def requirement_rows() -> list[dict]:
    """One row per declared CP-0010 requirement, audited against its own evidence."""
    matrix = _load(CP10 / "REQUIREMENTS-MATRIX.json")
    rows = []
    for index, requirement in enumerate(matrix["requirements"], start=1):
        row = _row(
            f"CPR-{index:03d}", "1",
            f"{requirement['id']} at {requirement['sourceRef']}",
            "the requirement is in the independently derived expected set and every evidence "
            "reference it declares resolves",
            "independent derivation of the expected set and resolution of every evidence reference")
        row["requirementId"] = requirement["id"]
        rows.append(row)
    return rows


def regression_rows() -> list[dict]:
    """One row per distinct test the closure names, executed by this audit rather than trusted."""
    closure = _load(CP10 / "CP9-FINDINGS-CLOSURE.json")
    findings = closure.get("findings", closure.get("closures", []))
    seen: list[str] = []
    for finding in findings:
        for key in ("regressionTest", "negativeTest", "regressionTests", "negativeTests"):
            for reference in finding.get(key, []):
                name = reference.split(":", 1)[-1]
                if name not in seen:
                    seen.append(name)
    rows = []
    for index, name in enumerate(sorted(seen), start=1):
        row = _row(
            f"REG-{index:03d}", "1",
            f"regression test {name}",
            "the named test exists in the suite and passes when executed by this audit",
            "targeted execution of the named test by identifier")
        row["testName"] = name
        rows.append(row)
    return rows


CONTROL_DEFINITIONS = [
    ("POS-001", "1", "Positive promotion reachability recorded",
     "the positive promotion artifact of the delivery records an executed, reproducible run",
     "read POSITIVE-PROMOTION-VALIDATION.json and re-execute its entry point"),
    ("POS-002", "1", "Positive promotion re-executed by the auditor",
     "promotion_simulation.py completes a two-checkpoint promotion in a disposable repository",
     "execute promotion_simulation.py from a clean checkout"),
    ("POS-003", "1", "Promotion subject unchanged",
     "the subject checkpoint of the simulation is unchanged before and after its audit",
     "compare the subject tree hash across the simulation states"),
    ("SUC-001", "1", "Successor durability recorded",
     "SUCCESSOR-DURABILITY.json records an executed three-state succession",
     "read the artifact and re-execute its entry point"),
    ("SUC-002", "1", "Successor durability re-executed by the auditor",
     "successor_durability.py is green at every state of the chain",
     "execute successor_durability.py from a clean checkout"),
    ("SUC-003", "1", "Missing anchor still detected after the chain advances",
     "the negative control still fails when an owed anchor is absent",
     "execute the negative scenario inside the durability fixture"),
    ("TST-001", "1", "Full current suite executed by the auditor",
     "the complete suite executes green in the working repository",
     "python -m unittest discover -s tests"),
    ("TST-002", "1", "Actual test count recorded independently",
     "the number of executed cases is counted by this audit, not taken from the delivery",
     "parse the result object of the suite"),
    ("TST-003", "1", "Canonical mandatory validators executed",
     "every canonical mandatory validator exits zero",
     "execute each validator named in the contract and record its exit code"),
    ("TST-004", "1", "Compilation gate",
     "every script and test compiles",
     "python -m compileall -q scripts tests"),
    ("TST-005", "1", "No whitespace corruption in the audited change set",
     "git diff --check is clean over the change set of the delivery",
     "git diff --check over the base and the sealed commit of the subject"),
    ("CLN-001", "1", "Clean isolated checkout of the subject",
     "a clean clone detached at the canonical tag of the subject validates",
     "clone to a disposable path, detach at the tag, run validate_checkpoint.py"),
    ("CLN-002", "1", "Full suite from the clean clone",
     "the complete suite executes green from the clean isolated checkout",
     "python -m unittest discover -s tests inside the clone"),
    ("CLN-003", "1", "Mandatory validators from the clean clone",
     "every canonical mandatory validator exits zero inside the clean clone",
     "execute each validator inside the clone and record its exit code"),
    ("GK-001", "1", "Green Keeper verdict independently recomputed",
     "the recorded PASS is reproduced by executing the Green Keeper over the subject",
     "execute green_keeper.py against the subject checkpoint"),
    ("GK-002", "1", "Green Keeper not stale",
     "the recorded scope fingerprint still describes the sealed content of the subject",
     "recompute the delivery-assurance scope fingerprint of the tree of the subject"),
    ("GK-003", "1", "Green Keeper counters",
     "remainingFailures and unresolvedReworkItems are both zero and the rework log agrees",
     "read STATE.json and REWORK-LOG.jsonl of the subject"),
    ("GK-004", "1", "Canonical mandatory gate set not narrowed",
     "the required gate set equals the canonical policy set",
     "compare the declared required gates with the policy definition"),
    ("DCV-001", "1", "Expected requirement set derived independently",
     "an independent derivation of the expected set equals the declared set exactly",
     "independent parser over the checklist, the canonical policy, the audit registry and the "
     "preflight"),
    ("DCV-002", "1", "Completeness recomputed",
     "coverage and evidence coverage are both total with no partial and no missing requirement",
     "execute check_completeness.py against the subject and recompute independently"),
    ("DCV-003", "1", "Every evidence reference resolves",
     "every implementation, test, documentation and validation reference resolves to a real "
     "artifact",
     "resolve every reference of every declared requirement"),
    ("MEM-001", "1", "Engineering memory valid",
     "the lesson store validates and the status of every lesson is supported",
     "execute validate_lessons.py and recompute independently"),
    ("MEM-002", "1", "Guardrail effectiveness recomputed",
     "every guardrail resolves, is tested and is effective",
     "recompute guardrail effectiveness from the registry and the suite"),
    ("MEM-003", "1", "Guardrail failures at final state",
     "no unresolved guardrail failure remains",
     "recompute the guardrail failure count from the lesson store"),
    ("MEM-004", "1", "CP-0009 lesson candidates assessed",
     "every candidate the previous audit raised has a recorded assessment",
     "compare LESSON-CANDIDATES.json with LESSON-CANDIDATE-ASSESSMENT.md"),
    ("MEM-005", "1", "Systemic new defects produced lessons or recurrences",
     "each systemic defect this delivery disclosed is recorded as a lesson or a recurrence",
     "map the disclosed defects onto the lesson store"),
    ("MEM-006", "1", "No duplicate lesson created to satisfy the audit",
     "no lesson duplicates an existing one in failure class and guardrail",
     "cluster the lesson store by failure class and inspect every new lesson"),
    ("MEM-007", "1", "Retrospective produced",
     "the Gate retrospective exists and follows the canonical template",
     "compare the retrospective with the template"),
    ("PRE-001", "1", "Preflight freshness",
     "the recorded preflight fingerprint matches a recomputation over the current lesson store",
     "recompute the preflight and compare the fingerprint"),
    ("PRE-002", "1", "Preflight requirements carried into the matrix",
     "every derived lesson requirement appears in the requirements matrix",
     "compare the derived requirements of the preflight with the matrix"),
    ("PRE-003", "1", "Stale preflight refused",
     "a preflight that no longer describes the lesson store is refused",
     "mutate the lesson store in a disposable clone and re-validate"),
    ("HIS-001", "1", "Sealed chain verified",
     "every sealed checkpoint from the first to the subject verifies against its anchor",
     "execute verify_integrity.py and re-derive every anchor independently"),
    ("HIS-002", "1", "Every historical tag resolves to its anchored commit and tree",
     "tag, commit and tree agree for every anchored checkpoint",
     "re-derive tag, commit and tree from Git for every anchor"),
    ("HIS-003", "1", "Subject anchored by the audit successor",
     "the audit checkpoint anchors the subject, which the subject could not anchor itself",
     "inspect the chain after this audit records its anchor"),
    ("HIS-004", "1", "Moved tag detected",
     "moving a historical tag is detected",
     "move a tag in a disposable clone and verify"),
    ("HIS-005", "1", "Rewritten sealed content detected",
     "rewriting the content of a sealed checkpoint is detected",
     "rewrite content in a disposable clone and verify"),
    ("HIS-006", "1", "Broken anchor link detected",
     "breaking the link between two anchors is detected",
     "break a link in a disposable clone and verify"),
    ("HIS-007", "1", "Missing anchor detected",
     "a sealed checkpoint with no anchor, other than the newest, is detected",
     "remove an anchor in a disposable clone and verify"),
    ("HIS-008", "1", "Sealed checkpoints validate from their own tags",
     "every sealed checkpoint still validates from a detached checkout of its canonical tag",
     "detached validation of every sealed checkpoint in a disposable clone"),
    ("ART-001", "1", "Affected Red Team battery re-executed",
     "affected_red_team.py replays every affected scenario and all are defended",
     "execute affected_red_team.py from a clean checkout"),
    ("ART-002", "1", "Null-mutation control present and valid",
     "every adversarial battery records a control that is accepted before any refusal counts",
     "inspect every battery report and its control"),
    ("ART-003", "1", "Attestation attacks written by this audit",
     "forged attestations written by this audit are refused",
     "execute the attestation probe battery of this audit"),
    ("ART-004", "1", "Positive control accepted",
     "the unmutated positive attestation of this audit is accepted",
     "execute the positive control of the battery of this audit"),
    ("ART-005", "1", "Promotion reachability attacks",
     "an attestation that names the wrong subject, auditor or commit cannot promote",
     "execute the promotion attacks against the fixture"),
    ("ART-006", "1", "Anchor successor dynamics attacks",
     "the pending-anchor exclusion cannot be abused to skip an owed anchor",
     "execute the successor attacks against the fixture"),
    ("ART-007", "1", "Preflight attacks",
     "a forged, stale or narrowed preflight is refused",
     "execute the preflight mutations"),
    ("ART-008", "1", "Guardrail registry attacks",
     "the registry path cannot be re-pointed to weaken the memory controls",
     "execute the registry mutations"),
    ("ART-009", "1", "Evidence and staleness semantics attacks",
     "a gate result whose scope changed is refused as stale",
     "execute the staleness mutations"),
    ("ART-010", "1", "Mandatory battery re-executed",
     "the canonical mandatory attack battery is fully defended",
     "execute m0_red_team.py from a clean checkout"),
    ("ART-011", "1", "Internal mirror re-executed",
     "the internal mirror audit is green from a clean clone and is not recorded as independent",
     "execute m0_mirror_audit.py --clean-clone and inspect how its verdict is recorded"),
    ("AUD-001", "1", "Audit profile recorded truthfully",
     "tool, provider, model, session independence and cross-tool availability are recorded "
     "without inflation",
     "inspect RUN-METADATA.json and STATE.json of this checkpoint"),
    ("AUD-002", "1", "Matrix created before substantive execution",
     "the matrix was created with every row NOT_STARTED before any audited execution",
     "inspect the creation record and the initial artifact"),
    ("AUD-003", "1", "No mandatory row left unexecuted",
     "no mandatory row remains NOT_STARTED, IN_PROGRESS or UNVERIFIED",
     "recompute the summary from the rows"),
    ("AUD-004", "1", "Every row carries evidence",
     "no row is complete without a resolvable evidence reference",
     "recompute evidence coverage from the rows"),
    ("AUD-005", "1", "No implementer assertion used as proof",
     "every PASS rests on an execution this audit performed or an artifact it inspected",
     "inspect the observed field of every row for an assertion-only basis"),
    ("AUD-006", "1", "Verdict recorded honestly",
     "the mechanism, the independence claimed and the milestone status are consistent",
     "compare the attestation, STATE.json and the derived verdict"),
    ("AUD-007", "1", "Gate 0 not started",
     "no Gate 0 implementation exists in this change set",
     "inspect the change set of this checkpoint"),
]


def control_rows() -> list[dict]:
    return [_row(*item) for item in CONTROL_DEFINITIONS]


def all_rows() -> list[dict]:
    return finding_rows() + requirement_rows() + regression_rows() + control_rows()


if __name__ == "__main__":
    print(len(all_rows()))
