# Quality Gates

## Canonical outcomes

Quality checks use only `PASS`, `FAIL`, `NOT_APPLICABLE`, or `NOT_EXECUTED`. Gate state uses only the statuses defined by `CHECKPOINT-PROTOCOL.md`.

## Required dimensions

Every Gate records build, unit tests, integration tests, end-to-end tests, lint, static analysis, security, documentation, checkpoint validation, and Red Team. Applicability and evidence are Gate-specific.

## Delivery assurance gates

From `schemaVersion` `3.0.0` every checkpoint additionally records two gates.

`GREEN_KEEPER_GATE` is `PASS` only when every mandatory executable gate is green, `remainingFailures`
is zero, and `unresolvedReworkItems` is zero. Each cycle is recorded in `REWORK-LOG.jsonl`. A real
external blocker produces `BLOCKED`, never `PASS`.

`DELIVERY_COMPLETENESS_GATE` is `PASS` only when the audit of `REQUIREMENTS-MATRIX.json` reports
`coveragePercent` `100.00`, zero `partial`, zero `missing`, and every evidence reference resolved.
The result is recorded in `COMPLETENESS-REPORT.json`, and validation recomputes it from the matrix so
a stored verdict cannot drift from what it claims to describe.

`READY_FOR_REVIEW` requires both gates to be `PASS`, every other non-independent dimension to be
`PASS` or justified `NOT_APPLICABLE`, an empty `blockedBy`, and `independentReview` and `redTeam` to
still be `PENDING`. An implementing run cannot record its own independent verdict.

## Evidence references

From `schemaVersion` `2.0.0`, `QUALITY.json` records each dimension as `{status, evidence, justification}`.
A `PASS` requires at least one resolvable evidence reference: `command:<id>` must name a record in the
checkpoint's `COMMANDS.jsonl` that exited `0`, and `file:<name>` must name a non-empty file inside the
checkpoint. `NOT_APPLICABLE` requires a justification. A verdict inherited from an earlier checkpoint
without re-execution is `NOT_EXECUTED`, never `PASS`.

The requirements matrix uses a wider vocabulary, because it also points at repository artifacts:
`file:<repository-relative path>`, `checkpoint:<name>` for a file inside the checkpoint,
`command:<id>` for a successful ledger record, and `test:<TestClass.test_name>` for a case that
exists in the suite. In `QUALITY.json`, `file:` keeps its original checkpoint-relative meaning so the
sealed `2.0.0` checkpoints stay valid.

## Promotion rule

A Gate can be `GATE_PASS` only when:

1. every acceptance criterion has direct evidence;
2. every applicable quality dimension is PASS with resolvable evidence;
3. unexecuted required work is absent;
4. independent review is approved;
5. Red Team has no unresolved failure;
6. the final checkpoint validates;
7. the next Gate has not been started;
8. the run granting `GATE_PASS` is independent of the run that implemented the Gate, and
   `secondToolValidation` records `PASSED` or a justified `NOT_REQUIRED`.

Any unmet mandatory criterion produces `GATE_FAIL`, `REWORK_REQUIRED`, or `BLOCKED`, as appropriate.


## Lesson-derived requirements

Before a Gate starts, the lesson preflight selects the applicable entries of the engineering memory
and derives a `LESSON-REQ-` requirement from each one. Those requirements are part of the Gate's
matrix, and the Delivery Completeness Validator fails the delivery when one is absent or unevidenced.
Lesson validation is part of the Green Keeper gate set, so a broken memory is a red delivery.

## Internal and external verdicts

`INTERNAL_GATE_PASS` records that a Gate satisfied the project's own controls.
`MILESTONE_EXTERNAL_PASS` records that an independent tool audited the whole milestone and approved
it. The two are different statuses and the first is never described as the second. Validation refuses
`MILESTONE_EXTERNAL_PASS` unless the milestone and the cross-tool validation are both `PASSED`, and
refuses an `INTERNAL_GATE_PASS` that carries an external verdict.

## The closed mandatory gate set

`.iacode/policies/quality-gates.json` is the registry of mandatory gates. The Green Keeper reads it
and runs every mandatory gate; `--gates` may add to a run and can never remove from it. Every rework
cycle records the mandatory set it was measured against, along with each gate's command evidence and
exit code, and validation refuses a `PASS` whose cycle measured anything less than the canonical set.

Adding a gate to the registry is how the mandatory set grows. Removing one is a policy change, not
an invocation, and the change is visible in the diff.

## The shared promotion invariant

One set of checks governs every positive terminal status: `READY_FOR_REVIEW`, `READY_FOR_RED_TEAM`,
`INTERNAL_GATE_PASS`, `MILESTONE_EXTERNAL_PASS` and `GATE_PASS`. All of them require the Green Keeper
gate to pass, delivery completeness to be total with total evidence coverage, no `PARTIAL` or
`MISSING` requirement, and every mandatory quality dimension executed and not `FAIL`. Each status then
adds its own requirements: a review-ready checkpoint leaves the independent verdicts `PENDING`, and a
terminal status requires them to have been given.

## Freshness

A gate result is a statement about a specific content. The Green Keeper cycle, the completeness
report, the internal Red Team report and the internal mirror audit each record a fingerprint of the
delivery-assurance scope they judged. Any later change inside that scope makes the result stale, and
a stale result is refused exactly like a red one. The scope is the code, the tests, the policies, the
memory, the prompts and the governing documents; the checkpoint's own evidence is deliberately
outside it, so recording evidence never invalidates the evidence being recorded.

## Derived counts

Any count used as evidence is derived once into `COUNTS.json` from the artifact that owns it, and
validation recomputes it. A checkpoint document that writes `N/M TESTS`, `N/M REQUIREMENTS`,
`N/M FINDINGS`, `N/M ATTACKS`, `N/M LESSONS` or `N/M GUARDRAILS` is checked against the derivation,
so two artifacts can no longer state different numbers for the same fact.
