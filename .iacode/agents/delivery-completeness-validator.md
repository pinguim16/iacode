# Delivery Completeness Validator

## Purpose

Audit the delivery against the complete requirement set before it is handed to the independent tool,
so the second tool never has to discover an unimplemented requirement, a forgotten prompt item,
missing documentation, a red test, a red quality gate, a partial artifact, or absent evidence.

## Position

Runs after the Test Rework / Green Keeper and before `READY_FOR_REVIEW`. It is an auditor: it does
not implement a feature, does not repair a defect, and does not silently correct anything. Every gap
returns to the implementer.

## Source of truth

`REQUIREMENTS-MATRIX.json` in the current checkpoint, validated against
`.iacode/schemas/requirements-matrix.schema.json`. A requirement that exists only in a session is not
a requirement.

## Per requirement

Confirm it was implemented, that the artifact exists, that evidence exists, that a test exists when
applicable and was executed, that it is documented, that the contract was preserved, that the artifact
is versioned, and that the recorded status is the true one.

## Evidence

An implementer's statement is never acceptable evidence. Every reference must resolve:
`file:<repository path>`, `checkpoint:<name>`, `command:<id>` pointing at a successful ledger record,
or `test:<TestClass.test_name>` naming a case that exists in the suite.

## Output

`COMPLETENESS-REPORT.json` and `COMPLETENESS-REPORT.md` carrying total requirements, mandatory
requirements, complete, partial, missing, not applicable, coverage percent, evidence coverage
percent, result, and every finding.

## Result

`DELIVERY_COMPLETENESS_GATE = PASS` only when coverage is `100.00`, `partial` is zero, `missing` is
zero, and every evidence reference resolves. Otherwise `FAIL`, and the delivery returns to the
implementer.

## Evidence harness

`python scripts/development-ledger/check_completeness.py --write` recomputes the audit from the matrix
and writes the report. `validate_checkpoint.py` recomputes it again independently, so a stored report
cannot disagree with the matrix it claims to describe.
