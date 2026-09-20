# Handoff

Current Gate: SETUP-00
Current Status: IN_PROGRESS

Last valid commit: 5780b0f86dbf46ad84d69b88a637be6f076946f4
Current branch: main

## Objective

Hand the independent CP-0003 validation findings back to Claude Code without implementing fixes.

## What was completed

- Cold-started from repository state and verified CP-0003 at its immutable tag.
- Independently reviewed R1 through R7.
- Ran the full 75-test suite, static compilation, Git whitespace check, checkpoint/secret validation,
  historical compatibility, adapter tests, focused inventory tests, and clone attacks.
- Recorded exact blocking findings in `REVIEW-REPORT.md` and `RED-TEAM-REPORT.md`.
- Recorded structured cross-tool validation as `FAILED`.

## What was NOT completed

No corrective implementation. SETUP-00 did not reach GATE_PASS. Gate 0 was not started.

## Current repository state

CP-0003 remains sealed at `5780b0f86dbf46ad84d69b88a637be6f076946f4`. CP-0004 records
`REWORK_REQUIRED`; see `STATE.json` for its final immutable reference.

## Files changed

Only this checkpoint was created and `docs/checkpoints/LATEST.md` was modified. See `FILES.json`.

## Important decisions

Mandatory R3 and Red Team findings block promotion. Independence is preserved by returning fixes to
Claude Code.

## Tests executed

- `python -B -m unittest discover -s tests -v`: 75 passed, 0 failed, 81.438 seconds.
- `DeltaInventoryTests`: 8 passed, 0 failed, 23.464 seconds.
- Focused cross-tool/quality/history/adapter tests: 23 passed, 0 failed, 2.294 seconds.
- `python -m compileall -q scripts tests`: exit 0.
- `git diff --check ...`: exit 0.
- Checkpoint validator/secret scan: `CHECKPOINT_VALID` before review checkpoint creation.

## Known failures

- Finalization refusal in detached HEAD is not recorded in `COMMANDS.jsonl`.
- A fully resealed `READY_FOR_REVIEW` fixture with nonempty `blockedBy` returns `CHECKPOINT_VALID`.
- Recorded CP-0003 finalizer command strings do not resolve from their recorded working directory.

## Known risks

See `RISKS.md`; both blocking findings affect control-plane trust and auditability.

## Do not repeat

Do not fix the findings in this validation checkpoint, rewrite or retag sealed checkpoints, count the
green suite as overriding Red Team failures, or begin Gate 0.

## Required next action

Claude Code creates and implements the next corrective SETUP-00 checkpoint described in `NEXT.md`.

## Exact continuation sequence

1. Read this entire checkpoint, especially `REVIEW-REPORT.md` and `RED-TEAM-REPORT.md`.
2. Reproduce RT-01 and RT-02 in new isolated clones.
3. Create the next SETUP-00 checkpoint; do not edit CP-0004.
4. Implement both corrections and regression tests.
5. Run all validation and close at `READY_FOR_REVIEW` for Codex.

## Validation commands

- `python scripts/development-ledger/validate_checkpoint.py`
- `python -B -m unittest discover -s tests -v`
- `python -m compileall -q scripts tests`
- `git diff --check`

## Stop conditions

Stop on divergence, any need to change a sealed checkpoint, secret exposure, or any request to start
Gate 0.
