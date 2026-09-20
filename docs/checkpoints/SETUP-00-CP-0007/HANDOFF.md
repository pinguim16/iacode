# Handoff

Current Gate: SETUP-00
Current Status: REWORK_REQUIRED

Last validated baseline: 994bab402873bc4d221c02d8c94bdebeb2b0f3cb
Validation checkpoint: SETUP-00-CP-0007
Current branch: main

## Objective

Transfer the independent M0 failure evidence to Claude Code for a corrective SETUP-00 checkpoint.

## What was completed

The full M0 audit, all 59 checklist dispositions, all 26 A-Z attacks, the full and clean-clone suites, historical validation, command sampling, Engineering Memory audit, lesson candidates, and binary verdict.

## What was NOT completed

No product defect was repaired, no canonical lesson was promoted, M0 did not pass, and Gate 0 was not started.

## Current repository state

CP-0007 is REWORK_REQUIRED with eleven findings, four PARTIAL checklist rows, and eight escaped attacks.

## Files changed

See FILES.json. Changes are limited to LATEST.md and CP-0007 audit evidence.

## Important decisions

See DECISIONS.md and REVIEW-REPORT.md.

## Tests executed

181/181 passed in the audit checkout and 181/181 passed in a fresh clone. See TESTS.json and AUDIT-EXECUTIONS.md.

## Known failures

M0-F-001 through M0-F-011. The principal failures are terminal-status assurance bypass, forgeable external PASS, stale preflight acceptance, forgeable lesson guardrails, vacuous Green Keeper PASS, unanchored completeness, and unanchored history.

## Known risks

See RISKS.md. Passing nominal validators are not proof that the escaped invariants are safe.

## Do not repeat

Do not self-assert external PASS, shrink a matrix denominator, accept empty mandatory gate sets, trust syntactic control references, rewrite sealed history, or start Gate 0.

## Required next action

Claude Code must create a new corrective SETUP-00 checkpoint implementing every acceptance condition in REVIEW-REPORT.md, then return the complete M0 milestone for a new independent audit.

## Exact continuation sequence

1. Read START-HERE.md and CP-0007 completely.
2. Reproduce every finding before editing.
3. Create a new requirements matrix and lesson preflight.
4. Implement fixes in a new checkpoint without rewriting CP-0001 through CP-0007 or their tags.
5. Add permanent negative tests for all escapes and aggregate contradictions.
6. Run the full Green Keeper and Delivery Completeness flows with the closed mandatory set.
7. Seal READY_FOR_REVIEW and request a new independent M0 audit.
8. Do not begin Gate 0.

## Validation commands

`python -B -m unittest discover -s tests -v`  
`python -B scripts/development-ledger/validate_lessons.py`  
`python -B scripts/development-ledger/check_completeness.py --checkpoint docs/checkpoints/<new-checkpoint>`  
`python -B scripts/development-ledger/validate_checkpoint.py`

## Stop conditions

Stop on any escaped attack, unresolved PARTIAL/MISSING requirement, contradictory aggregate, unresolved evidence, unbound preflight, red mandatory gate, historical drift, or attempted Gate 0 work.
