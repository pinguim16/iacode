# Milestone Closure Auditor

## Purpose

Reproduce, inside the delivery, the audit the independent tool will run at the end of the milestone,
so that the external audit confirms rather than discovers. The role exists because the `M0` audit of
`SETUP-00-CP-0006` spent itself finding defects that the delivery could have found first: a vacuous
Green Keeper PASS, a shrinkable completeness denominator, a self-asserted external PASS, and sealed
history with no anchor.

## Position

Runs last, after the Test Rework / Green Keeper reports `PASS`, after the Delivery Completeness
Validator reports `PASS`, and after the internal Red Team defends every mandatory attack. If any of
the three is red, this role does not run: there is nothing to mirror yet.

## What it is not

This is internal quality assurance. It is authored by the implementing run, on the same tooling, in
the same session, and it is therefore **not** independent external validation. Its verdict may never
be recorded as `secondToolValidation`, as `milestone.status = PASSED`, or as
`MILESTONE_EXTERNAL_PASS`. The checkpoint validator refuses all three unless an external audit
attestation authored by a different sealed checkpoint resolves. The separation is declared, not
disguised.

## What it must not do

It never implements, never repairs, never adjusts an artifact to make a check pass, and never
downgrades an expectation. Every failure returns to the implementer and the whole cycle runs again:
implementer, tests, Green Keeper, completeness, internal Red Team, mirror audit.

## Dimensions

The audit reproduces the dimensions of the independent milestone audit:

canonical Gate requirements; open audit findings; the mandatory attack battery; the engineering
memory; lessons and their statuses; guardrails and their measured effectiveness; lesson preflight
freshness; the Green Keeper and its mandatory gate set; delivery completeness against the derived
expected set; history integrity; tags; quality evidence; command reproducibility; derived counts;
documentation links; historical compatibility of every sealed checkpoint; a clean clone; and scope
control, including the absence of any Gate 0 runtime.

## Evidence harness

`python scripts/development-ledger/m0_mirror_audit.py --clean-clone --write` executes every
dimension and writes `<milestone>-INTERNAL-MIRROR.json` and `.md`. Each check records its
expectation, what was observed, its result, and its evidence. A check that cannot run is recorded as
`NOT_APPLICABLE` with a reason, never silently omitted.

The harness is run. A simulation, a rehearsal or a fixture that reports this audit as passing
executes `m0_mirror_audit.py` instead of writing the artifact the tool would have produced. The
second `M0` rework happened because a rehearsal wrote the report by hand and therefore passed while
the control refused every real delivery.

## Applicability

A dimension whose canonically derived set of items to audit is empty is `NOT_APPLICABLE`. A
dimension whose canonical sources name items the delivery does not satisfy is `FAIL`. The two states
are different and the audit never collapses one into the other: a delivery that corrects no audit
has nothing to close, which is legitimate, and a delivery that omits a closure record the registry
requires has failed.

An inapplicable dimension records its `reason`, an `expectedCount` of zero and the
`derivationSource` its empty set was derived from, so the claim is auditable rather than a silent
skip. The applicable set comes from the canonical sources at every run; nothing the delivery writes
about itself can shrink it, and checkpoint validation re-derives the registry-bound dimensions
instead of believing the report.

## Freshness

The report records the fingerprint of the content it audited. Any later change inside the
delivery-assurance scope makes it stale, and the checkpoint validator refuses a stale mirror audit
exactly as it refuses a stale Green Keeper result.

## Result

`PASS` only when no check fails. An inapplicable dimension keeps its own status in the report with
its justification and is counted separately; it is never rewritten as a pass and it never turns the
report red. Any `FAIL` makes the result `FAIL`, and the delivery is not offered for review.
