# Resume Validation

`SECOND_TOOL_VALIDATION = PENDING_MANUAL`

The authoritative record is `STATE.json` `secondToolValidation`, which reads `PENDING_MANUAL`. This
line is kept for readers of the sealed `1.0.0` checkpoints, where the same status was expressed only
as text.

## Repository-only checks completed by this run

- An authenticated Claude Code desktop session executed `prompts/RESUME-WORK.md` from repository
  content only, reconstructed phase, Gate, status, commit, and next action, and matched `STATE.json`
  of `SETUP-00-CP-0002` exactly.
- The corrected validator was run against clean clones detached at both sealed tags and returned
  `CHECKPOINT_VALID` for each, which is also asserted by `HistoricalCheckpointCompatibilityTests`.
- The full suite, static analysis, and the adversarial battery were executed; results are in
  `TESTS.json`, `QUALITY.json`, and `RED-TEAM-DEV-REPORT.md`.

## Why this is not cross-tool validation

The session that ran those checks is the session that implemented this checkpoint. Its review and
adversarial work are recorded as `SELF-REVIEW.md` and `RED-TEAM-DEV-REPORT.md` precisely so they are
not mistaken for independent verification. The separate Claude Code CLI installation at
`C:/Users/cesar/.local/bin/claude.exe` reported `loggedIn: false` again on 2026-09-20, so the
clean-clone CLI cold start remains `BLOCKED_AUTHENTICATION`, exactly as `SETUP-00-CP-0002` recorded.

## Procedure for the independent run

1. Obtain a clean clone of this repository in a new temporary directory.
2. Either stay on `main` or run `git checkout --detach refs/tags/iacode-checkpoints/SETUP-00-CP-0003`;
   both are supported, and the detached form is now covered by tests.
3. Run `python scripts/development-ledger/validate_checkpoint.py` and the remaining commands in
   `HANDOFF.md`.
4. Reconstruct the Gate, status, commit, and next action from repository files alone and compare them
   with `STATE.json`.
5. Re-run the attacks in `RED-TEAM-DEV-REPORT.md` and add new ones.
6. Record the outcome in a new checkpoint whose `STATE.json` sets `secondToolValidation.status` to
   `PASSED` or `FAILED`, with `tool`, `provider`, `model`, and `validatedAt`. Do not edit this sealed
   checkpoint.

## Expected result

An independent tool should reconstruct the state from the repository alone, report `SETUP-00` as
`READY_FOR_REVIEW`, report that Gate 0 stays blocked, leave the clone unchanged, and then record its
own verdict in a new checkpoint.
