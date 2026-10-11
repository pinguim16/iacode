# Handoff

Current Gate: GATE-4
Current Status: REWORK_REQUIRED

## Objective

Independently re-audit the sealed Gate 4 correction without modifying product code.

## What was completed

Subject identity, detached validation, bundle integrity/determinism/portability, architecture, 198 requirements, functional acceptance, the full 42-stage run, focused failure repetitions, G4-X7 and the complete independent Red Team were executed.

## What was NOT completed

Gate 4 was not approved. M2 was not approved and Gate 5 was not started.

## Current repository state

See `STATE.json`; finalization records `REWORK_REQUIRED` with blocker `G4-F-002`.

## Files changed

See `FILES.json`; no product path changed.

## Important decisions

The isolated PASS repetitions characterize the failure but do not replace the red single full run.

## Tests executed

The published full verifier executed all 42 stages and returned 40 PASS / 2 FAIL. Exact isolated `infra` and `smoke` repetitions then passed. Functional acceptance passed 12/12 and Red Team passed 20/20.

## Known failures

`G4-F-002` (HIGH): the published full clean-clone run failed `infra` and `smoke`, demonstrating intermittent or order-dependent verification.

## Known risks

Retry-based promotion could hide the instability and create a false PASS.

## Do not repeat

Do not replace a red full-run result with isolated green reruns or weaken the 42-stage denominator.

## Required next action

Open a new corrective Gate 4 checkpoint, diagnose `G4-F-002`, make the complete run deterministic, and submit a later sealed correction to another independent audit.

## Exact continuation sequence

Lesson preflight, requirement derivation, baseline, plan, correction, tests, Green Keeper, completeness, internal Red Team, closure audit, `READY_FOR_REVIEW`, seal/publish, and a later fresh independent audit.

## Validation commands

`python scripts/iacode/verify.py --keep-going --report <new-report>` from a published transport clone, followed by the standard ledger validators.

## Stop conditions

Stop on any stage failure, missing evidence, escaped attack, incomplete requirement, divergence, or attempted Gate 5 change.
