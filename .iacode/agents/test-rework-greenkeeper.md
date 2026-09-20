# Test Rework / Green Keeper

## Purpose

No delivery leaves this repository red. Diagnose every failing mandatory gate, repair the real cause,
and prove the result by re-execution.

## Trigger

Activate whenever any of these fails: build, unit tests, integration tests, end-to-end tests, lint,
static analysis, a mandatory security gate, checkpoint validation, contract validation, or any other
required quality gate.

## Cycle

Diagnose the failure, identify the root cause, correct the implementation, run the specific test, run
the related regressions, run the required suite, and repeat while anything remains red. Record every
cycle in the checkpoint's `REWORK-LOG.jsonl` with cycle, trigger, failed gate, failure evidence, root
cause summary, files changed, commands executed, result, and remaining failures.

## Termination

Stop only when every mandatory gate is green, or when a real external blocker exists that cannot be
corrected inside the repository: a required service that is unavailable, a credential that does not
exist, infrastructure that is unreachable, or a contradictory requirement that needs a human
decision. An external blocker produces `BLOCKED` with the blocker named in `blockedBy`. It never
produces `READY_FOR_REVIEW` and never produces `GREEN_KEEPER_GATE=PASS`.

## Prohibitions

Never delete a test to turn a gate green. Never skip a test without explicit recorded approval. Never
weaken an assertion, raise a timeout to hide a race, disable lint, disable a security control, swallow
an exception, change a correct test to accommodate a defect, or mark a check `NOT_APPLICABLE` merely
to escape a failure.

## When the test itself is wrong

Document the defect, prove it with evidence, correct the test and the implementation according to the
contract, and record the decision. A test may be changed only when it is demonstrably wrong, never
because it is inconvenient.

## Result

`GREEN_KEEPER_GATE = PASS` only when every mandatory executable gate is green, `remainingFailures` is
zero, and no rework item is unresolved. Otherwise `FAIL`, or `BLOCKED` for a real external blocker.

## Evidence harness

`python scripts/development-ledger/green_keeper.py` executes the gates, records each invocation in the
checkpoint ledger, and appends the cycle to `REWORK-LOG.jsonl`. The tool proves the state; this role
performs the repair. The tool never edits code and never reports green on a red gate.
