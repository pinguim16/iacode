#!/usr/bin/env python3
"""The dimensions this audit must decide, written before substantive execution.

The mandate of this audit is the final M0 confirmation after ``CP11-F-001``. Each row names one
dimension, whether it is mandatory, and what would make it fail. Results are not written here: they
arrive as append-only records in ``RESULTS.jsonl`` and ``build_matrix.py`` merges them, so the
published matrix is always a function of the recorded executions.
"""

from __future__ import annotations

from typing import Any

ROWS: tuple[dict[str, Any], ...] = (
    {
        "id": "AM-001",
        "dimension": "CP11-F-001 closure",
        "expectation": "The single critical finding of the sealed SETUP-00-CP-0011 review report "
                       "is closed, and the closure is verified against that sealed report rather "
                       "than against the delivery's own summary.",
        "failsIf": "The finding set re-parsed from the sealed report contains an identifier the "
                   "closure record does not carry as CLOSED.",
        "mandatory": True,
    },
    {
        "id": "AM-002",
        "dimension": "Mirror zero-set semantics",
        "expectation": "An empty canonically derived applicable set is reported as NOT_APPLICABLE "
                       "and the overall mirror can still PASS.",
        "failsIf": "A dimension with nothing to audit reports FAIL, or the overall report cannot "
                   "reach PASS in that state.",
        "mandatory": True,
    },
    {
        "id": "AM-003",
        "dimension": "Mirror closed-set semantics",
        "expectation": "A non-empty applicable set whose items are all satisfied reports PASS, so "
                       "the repair did not replace the check with an unconditional pass.",
        "failsIf": "MIR-002 or MIR-003 passes without evaluating the items the canonical sources "
                   "name.",
        "mandatory": True,
    },
    {
        "id": "AM-004",
        "dimension": "Mirror open-set semantics",
        "expectation": "A non-empty applicable set with one item unsatisfied reports FAIL, and so "
                       "does a required artifact that is absent.",
        "failsIf": "An open finding or a missing required closure record reaches a passing mirror.",
        "mandatory": True,
    },
    {
        "id": "AM-005",
        "dimension": "The caller cannot forge an empty expected set",
        "expectation": "No invocation argument and no artifact inside the delivery can shrink the "
                       "applicable set; the canonical derivation prevails, and an unreadable "
                       "report raises instead of reducing to an empty set.",
        "failsIf": "A declaration inside the checkpoint, a command-line argument, or an "
                   "unparseable report produces an empty applicable set that is then accepted.",
        "mandatory": True,
    },
    {
        "id": "AM-006",
        "dimension": "NOT_APPLICABLE is evidence, not an escape",
        "expectation": "An inapplicable dimension carries a reason, an expected count of zero and "
                       "a named canonical derivation source; the reverse escape is refused by the "
                       "auditor and again by checkpoint validation.",
        "failsIf": "An unjustified inapplicable dimension, one carrying items, one counted as a "
                   "pass, one under report schemaVersion 1.0.0, or one declared over work the "
                   "audit registry still names is accepted.",
        "mandatory": True,
    },
    {
        "id": "AM-007",
        "dimension": "The real m0_mirror_audit.py",
        "expectation": "Every mirror verdict this audit relies on comes from executing the shipped "
                       "command-line tool, never from reading an artifact a delivery wrote.",
        "failsIf": "A conclusion rests on a hand-crafted mirror report.",
        "mandatory": True,
    },
    {
        "id": "AM-008",
        "dimension": "Positive promotion simulation",
        "expectation": "promotion_simulation.py reaches a derived milestone verdict of PASSED and "
                       "produces every mirror report in it by executing m0_mirror_audit.py.",
        "failsIf": "The simulation writes a mirror artifact instead of running the tool, or the "
                   "positive path does not reach PASSED.",
        "mandatory": True,
    },
    {
        "id": "AM-009",
        "dimension": "Gate 0 transition",
        "expectation": "A closed milestone followed by the first checkpoint of the next Gate "
                       "reaches READY_FOR_REVIEW with no applicable audit findings, a passing "
                       "mirror and a verifying integrity chain, inside a disposable repository.",
        "failsIf": "The first delivery of the next Gate cannot reach a handoff-ready status, or "
                   "any Gate 0 runtime is created in this repository.",
        "mandatory": True,
    },
    {
        "id": "AM-010",
        "dimension": "Successor durability",
        "expectation": "Several successors are sealed in succession, each anchoring its "
                       "predecessor, and the integrity controls stay green at every state, with "
                       "the negative control still detecting a removed anchor.",
        "failsIf": "Any state of the advancing chain turns a mandatory control red, or the "
                   "detection control stops detecting.",
        "mandatory": True,
    },
    {
        "id": "AM-011",
        "dimension": "Full suite",
        "expectation": "The whole discovered suite executes with zero failures and zero errors, "
                       "and every skip is investigated and explained.",
        "failsIf": "Any test fails or errors, or a skip hides an unexecuted mandatory control.",
        "mandatory": True,
    },
    {
        "id": "AM-012",
        "dimension": "Clean clone",
        "expectation": "The mandatory validations and the suite reproduce in a fresh clone "
                       "detached at the subject's canonical tag, with no workspace state.",
        "failsIf": "Any mandatory validation or the suite behaves differently in a clean clone.",
        "mandatory": True,
    },
    {
        "id": "AM-013",
        "dimension": "Green Keeper",
        "expectation": "The mandatory gate set is closed and green, measured against the canonical "
                       "registry rather than an invocation, with a fresh scope fingerprint.",
        "failsIf": "A cycle is red, measures less than the canonical set, or is stale.",
        "mandatory": True,
    },
    {
        "id": "AM-014",
        "dimension": "Delivery completeness",
        "expectation": "The expected requirement set is re-derived independently and equals the "
                       "anchored declared set exactly, with total coverage and total evidence "
                       "coverage and no PARTIAL or MISSING row.",
        "failsIf": "The denominator differs from an independent derivation, or any evidence "
                   "reference does not resolve.",
        "mandatory": True,
    },
    {
        "id": "AM-015",
        "dimension": "Engineering memory",
        "expectation": "The memory validates, the lesson raised by CP11-F-001 exists, and the "
                       "GUARDRAIL_FAILURE of the recurrence is recorded against the lessons whose "
                       "classes recurred and is resolved.",
        "failsIf": "The memory is invalid, the recurrence is filed as a new lesson instead of a "
                   "guardrail failure, or any guardrail failure is unresolved.",
        "mandatory": True,
    },
    {
        "id": "AM-016",
        "dimension": "Guardrails",
        "expectation": "Every registered guardrail resolves to a real control, names verifying "
                       "tests that exist in the suite, and no guardrail failure is unresolved.",
        "failsIf": "guardrailFailures is non-zero, or a guardrail names a control or a test that "
                   "does not resolve.",
        "mandatory": True,
    },
    {
        "id": "AM-017",
        "dimension": "Lesson preflight",
        "expectation": "The preflight of the subject is bound to its Gate and fresh against the "
                       "memory, recomputed rather than read, and this audit runs its own.",
        "failsIf": "The recorded preflight cannot be reproduced from the memory it names.",
        "mandatory": True,
    },
    {
        "id": "AM-018",
        "dimension": "History integrity",
        "expectation": "Every sealed checkpoint resolves to its anchored commit and tree, the "
                       "hash-linked chain verifies, and every sealed checkpoint still validates "
                       "under the current tooling.",
        "failsIf": "A tag moved, a tree changed, a link broke, or a sealed checkpoint no longer "
                   "validates.",
        "mandatory": True,
    },
    {
        "id": "AM-019",
        "dimension": "The subject is untouched",
        "expectation": "This audit rewrites no sealed checkpoint, moves no historical tag and "
                       "changes no product code; the subject's tag, tree and STATE.json are the "
                       "same before and after.",
        "failsIf": "Any sealed content differs, or any file under scripts/ changes.",
        "mandatory": True,
    },
    {
        "id": "AM-020",
        "dimension": "Honest audit semantics",
        "expectation": "This audit records FRESH_SESSION_INDEPENDENT_AUDIT with crossToolValidation "
                       "NOT_AVAILABLE, and the derivation refuses to promote a cross-tool status "
                       "from it.",
        "failsIf": "A same-tool audit is recorded as cross-tool validation, or an internal verdict "
                   "is recorded as an independent one.",
        "mandatory": True,
    },
    {
        "id": "AM-021",
        "dimension": "Secrets and diff hygiene",
        "expectation": "No tracked file carries a credential-shaped value and the diff carries no "
                       "whitespace or conflict damage.",
        "failsIf": "A credential-shaped value exists in a tracked file, or git diff --check "
                   "reports damage.",
        "mandatory": True,
    },
    {
        "id": "AM-022",
        "dimension": "Audit completeness",
        "expectation": "This matrix itself ends fully executed, with evidence on every terminal "
                       "row, no failed mandatory row, no UNVERIFIED row and no NOT_STARTED row.",
        "failsIf": "Any row is left unexecuted or unevidenced.",
        "mandatory": True,
    },
)


def all_rows() -> list[dict[str, Any]]:
    return [
        {**row, "status": "NOT_STARTED", "observed": "", "evidence": [], "verdict": None}
        for row in ROWS
    ]
