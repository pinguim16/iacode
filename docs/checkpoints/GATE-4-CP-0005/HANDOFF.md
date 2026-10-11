# Handoff

Current Gate: GATE-4
Current Status: READY_FOR_REVIEW

Last sealed predecessor: 73cfa5eeb7fca2bf9312ec777d02f9ddfb2ad3d5
Current branch: main

## Objective

Close `G4-F-002` without broadening scope, publish a sealed Gate 4 corrective checkpoint at
`READY_FOR_REVIEW`, and preserve promotion for a later independent run.

## What was completed

The published clean-clone verifier passed all 42 stages in one invocation with zero retries.
Checkout-owned Compose identity, dynamic ports, frozen stage environment, owned cleanup and the
bounded Prometheus observer remove the order/state coupling behind the sealed 40/42 result. Green
Keeper cycle 4 passed 13/13 mandatory gates, completeness passed 221/221, internal Red Team passed
20/20 A-T, and the clean-clone M2 mirror passed 18/18.

## What was NOT completed

Independent review, second-tool validation and Gate 4 promotion were intentionally not performed.
Gate 5 was not started.

## Current repository state

The declared Gate 4 correction is on `main`, based on sealed predecessor
`73cfa5eeb7fca2bf9312ec777d02f9ddfb2ad3d5`. `STATE.json` is finalized to the canonical checkpoint
tag during sealing; this handoff never grants `GATE_PASS`.

## Files changed

See `FILES.json`. Principal runtime paths are the verifier, Compose environment, shared
observability helper, infrastructure/smoke checks, Red Team runner and their regression tests.

## Important decisions

See `DECISIONS.md` and ADR-0033. A verifier owns exactly one checkout-derived runtime namespace,
and observation may wait within policy while judged actions are never retried.

## Tests executed

The representative published run (`cmd-0052`) passed 42/42 stages. Counted executions are
1701/1701: 767 root tests and 934 deduplicated integration executions. Cycle 4 passed all 13
mandatory gates (`cmd-0139`–`cmd-0151`); completeness passed 221/221 (`cmd-0152`); internal Red
Team passed 20/20 (`cmd-0153`); and the clean-clone mirror passed 18/18 (`cmd-0156`).

## Known failures

The ledger preserves 17 failed commands and four rework cycles. They include the original
representative-run harness failure, the non-canonical result-field reconciliation, stale
self-evidence, incomplete declaration, and diagnostic validation failures. Every terminal failure
is retained; the final Green Keeper and assurance runs are separate later executions.

## Known risks

See `RISKS.md`. Current assurance is internal to the implementing session and cannot promote the
Gate.

## Do not repeat

Do not retry failed verification actions, reuse a shared Compose project, reduce or reorder the 42
stages, weaken G4-X7/Q, erase failed commands, rewrite the sealed checkpoint, grant `GATE_PASS` in
this run, or start Gate 5.

## Required next action

Seal, tag and publish this checkpoint, verify remote synchronization and then stop for a later
fresh-session independent review.

## Exact continuation sequence

Finalize to `READY_FOR_REVIEW`; commit; seal the committed checkpoint; publish `main` and the
canonical tag; verify remote sync and integrity; stop.

## Validation commands

Use `COMMANDS.jsonl`, especially `cmd-0052`, `cmd-0139`–`cmd-0156`, then
`validate_checkpoint.py`, `verify_integrity.py` and `remote_sync.py`.

## Stop conditions

Stop on an unrepaired finalizer, seal, integrity or publication failure. After successful
publication, stop for independent review and do not advance the Gate.
