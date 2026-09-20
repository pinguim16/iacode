# Plan

## Objective

Independently validate Claude Code's sealed `SETUP-00-CP-0003` without correcting implementation
files and without starting Gate 0.

## Baseline

Branch `main`, clean tree, `HEAD` and CP-0003 tag both at
`5780b0f86dbf46ad84d69b88a637be6f076946f4`; CP-0003 status `READY_FOR_REVIEW`; checkpoint validator
returned `CHECKPOINT_VALID`.

## Steps

1. Cold-start exclusively from repository documents and validate Git/checkpoint state.
2. Review R1 through R7 against code, schemas, ledger evidence, and independent executions.
3. Reproduce R1 in new clones and R2 in one isolated Git fixture per attack.
4. Execute the full suite, static compilation, Git whitespace check, secret scan through the
   checkpoint validator, historical compatibility, and adapter tests.
5. Execute every requested Red Team mutation in clones or isolated fixtures and add new attacks for
   surfaces found during code review.
6. Record PASS/FAIL evidence. If any mandatory control fails, do not correct it; close CP-0004 as
   `REWORK_REQUIRED` and hand back to Claude Code.

## Stop conditions

Stop implementation work on any finding, preserve sealed checkpoints and tags, never begin Gate 0,
and never record a failed or unexecuted check as PASS.
