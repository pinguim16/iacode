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

## Internal, independent and external verdicts

`INTERNAL_GATE_PASS` records that a Gate satisfied the project's own controls.

An independent audit produces one of two statuses, named for what its evidence supports:

| Status | Mechanism | What it claims |
|---|---|---|
| `MILESTONE_INDEPENDENT_AUDIT_PASS` | `FRESH_SESSION_INDEPENDENT_AUDIT` | A new session with no memory of the implementing run audited the milestone. Independent of the run, not of the tool. |
| `MILESTONE_EXTERNAL_PASS` | `CROSS_TOOL_INDEPENDENT_AUDIT` | A different tool, provider or model audited the milestone. |

Both are carried by the **audit checkpoint**, about the sealed subject checkpoint it judged, and both
are derived from an audit attestation rather than asserted. A fresh-session attestation cannot
produce the cross-tool status: validation refuses a status the recorded mechanism does not authorise.
An `INTERNAL_GATE_PASS` that carries an independent verdict is refused, and the first status is never
described as either of the other two.

## The closed mandatory gate set

`.iacode/policies/quality-gates.json` is the registry of mandatory gates. The Green Keeper reads it
and runs every mandatory gate; `--gates` may add to a run and can never remove from it. Every rework
cycle records the mandatory set it was measured against, along with each gate's command evidence and
exit code, and validation refuses a `PASS` whose cycle measured anything less than the canonical set.

Adding a gate to the registry is how the mandatory set grows. Removing one is a policy change, not
an invocation, and the change is visible in the diff.

## The shared promotion invariant

One set of checks governs every positive terminal status: `READY_FOR_REVIEW`, `READY_FOR_RED_TEAM`,
`INTERNAL_GATE_PASS`, `MILESTONE_INDEPENDENT_AUDIT_PASS`, `MILESTONE_EXTERNAL_PASS` and
`GATE_PASS`. All of them require the Green Keeper
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

## Applicability: an empty set is not a missing one

A control that judges a derived set can find that set empty for two different reasons, and they are
not the same result.

| State | Meaning | Outcome |
|---|---|---|
| empty applicable set | the canonical sources name nothing of this kind for this delivery to judge | `NOT_APPLICABLE` with a justification |
| missing required set | the canonical sources name items and the delivery does not carry or satisfy them | `FAIL` |

The third `M0` audit found the two collapsed into one: the internal mirror audit required its
derived set to be non-empty in order to report success, so a delivery that corrects no audit was
refused for having nothing to correct, and with it the audit checkpoint of this milestone and the
first delivery of every future Gate.

An inapplicable result is auditable, never a silent skip. It records why the dimension does not
apply, an expected count of zero, and the canonical source the emptiness was derived from. An
inapplicable result without those is refused, and so is one that records items it claims not to
have.

The applicable set is derived from the canonical sources at every run and never supplied by the
delivery. Nothing a checkpoint writes about itself reduces it, and validation re-derives the
dimensions whose source is canonical rather than believing the report, so declaring work away is
refused exactly like leaving it open. This is the same rule as the closed mandatory gate set and the
anchored completeness denominator: a control that trusts its own input is not a control.

## Simulations execute the control they report

A simulation, a rehearsal or a fixture that reports a control as passing runs that control. Writing
the artifact the control would have produced makes the rehearsal pass while the control itself may
refuse every real delivery, which is exactly how the applicability defect survived a green
`promotion_simulation.py`. Where a simulation must model an artifact it cannot execute, it says so
in the artifact and in its own report, so what was executed and what was modelled are never
confused.

## Derived counts

Any count used as evidence is derived once into `COUNTS.json` from the artifact that owns it, and
validation recomputes it. A checkpoint document that writes `N/M TESTS`, `N/M REQUIREMENTS`,
`N/M FINDINGS`, `N/M ATTACKS`, `N/M LESSONS` or `N/M GUARDRAILS` is checked against the derivation,
so two artifacts can no longer state different numbers for the same fact.

A count of executions never exceeds what exists to execute. One physical test run recorded under
several categories is one measurement, not their sum, and a numerator larger than its denominator is
refused: the second `M0` audit recorded a single 306-case run as both unit and integration and
derived 610 passing tests from it.

**A count stated in a source comment or docstring is not evidence.** Canonical counts live in
`COUNTS.json`, derived and recomputed; comments and docstrings describe semantics. The suite refuses
a cardinality or an `N/M LABEL` claim written in a comment or a docstring of `scripts/` or `tests/`,
because such a number has no derivation behind it and drifts silently, which is exactly what
`CP9-F-003` found. A count inside an ordinary string literal is data, not a claim: the Red Team
forges one deliberately.
