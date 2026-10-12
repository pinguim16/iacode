# Handoff

Current Gate: GATE-4
Current Status: REWORK_REQUIRED

## Objective

Independently audit the sealed `GATE-4-CP-0007` subject without modifying product code.

## What was completed

Published subject identity, the single full 42-stage verifier, counts, architecture, functional acceptance, G4-X7, transport attacks, deterministic bundle rebuilds, the complete A-T Red Team, checkpoint assurance, and delivery completeness were executed.

## What was NOT completed

Gate 4 was not approved. M2 was not approved and Gate 5 was not started.

## Current repository state

See `STATE.json`; finalization records `REWORK_REQUIRED` with blocker `G4-F-004`.

## Files changed

See `FILES.json`; no product path changed.

## Important decisions

The valid and byte-identical rebuilt bundles characterize the failure; they do not replace CP0007's sealed declared digest.

## Tests executed

The published full verifier passed 42/42 in one invocation. Functional acceptance passed 12/12. The independent Red Team defended 19/20; attack T escaped.

## Known failures

`G4-F-004` (HIGH): CP0007's declared review-bundle digest and size cannot be reconstructed from its sealed published subject.

## Known risks

A stale producer-time bundle can be valid while misrepresenting the final sealed evidence set.

## Do not repeat

Do not treat archive validity or deterministic rebuilds as proof that a previously declared digest represents the final sealed content.

## Required next action

Open a corrective Gate 4 checkpoint, make review transport final-content-derived, and submit the sealed correction to a later independent audit.

## Exact continuation sequence

Lesson preflight, requirement derivation, baseline, plan, correction, tests, Green Keeper, completeness, internal Red Team, closure audit, `READY_FOR_REVIEW`, seal/publish, and a later fresh independent audit.

## Validation commands

Rebuild the declared review bundle twice from a remote detached subject tag, compare both digests to the sealed declaration, then run the standard ledger validators.

## Stop conditions

Stop on any digest mismatch, stage failure, missing evidence, escaped attack, incomplete requirement, divergence, or attempted Gate 5 change.
