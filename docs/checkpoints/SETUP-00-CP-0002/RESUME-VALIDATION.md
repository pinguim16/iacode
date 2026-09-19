# Resume Validation

`SECOND_TOOL_VALIDATION = PENDING_MANUAL`

Observed attempt state: `BLOCKED_AUTHENTICATION`.

## Completed repository-only checks

- The checkpoint validator passed.
- The complete test suite passed 37 of 37 tests.
- Independent review returned `APPROVED`.
- Red Team returned `RED_TEAM_PASS` after the initial ledger findings were corrected.
- The sealed CP-0001 checkpoint was not modified.

## Claude Code attempt

The clean-clone command and sanitized result are recorded in `CLAUDE-COLD-START.md`. The executable started successfully but did not execute a model turn because the local Claude Code installation is unauthenticated. This does not satisfy genuine cross-provider resume validation.

## Optional authenticated procedure

Only after the user authenticates Claude Code outside repository scope:

1. Confirm `& 'C:/Users/cesar/.local/bin/claude.exe' auth status` reports an authenticated account.
2. Create a new temporary directory under the operating-system temporary root.
3. Clone this repository without copying the working tree and check out `refs/tags/iacode-checkpoints/SETUP-00-CP-0002`.
4. Confirm the clone is clean and run `python scripts/development-ledger/validate_checkpoint.py`.
5. Invoke Claude Code from the clone with the exact repository-only resume prompt in `CLAUDE-COLD-START.md`.
6. Require Claude to identify SETUP-00, the current checkpoint, its status, and the next allowed action; run the checkpoint validator and test suite without modifying files.
7. Compare Git status before and after. Any write, validator failure, invented metadata, or Gate advancement is a failure.
8. Record the actual provider/model/tool metadata and result in a new checkpoint. Do not edit this sealed checkpoint.

## Expected result after authentication

Claude should reconstruct state from repository files alone, report that SETUP-00 is complete, report that Gate 0 requires explicit authorization, and leave the clone unchanged. Until this is executed with a model call, cross-provider validation remains pending.
