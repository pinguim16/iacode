# Handoff Protocol

## Before changing tools

1. Finalize the checkpoint.
2. Validate it.
3. Update `docs/checkpoints/LATEST.md` textually; do not use a symlink.
4. Complete `HANDOFF.md` and `NEXT.md`.
5. Record branch, commit semantics, and dirty state.

No Codex-to-Claude or Claude-to-Codex transition is informal.

## Receiver sequence

1. Read `START-HERE.md`.
2. Read `docs/checkpoints/LATEST.md`.
3. Read the entire named checkpoint.
4. Run `git status --short --branch`, `git branch --show-current`, and `git rev-parse HEAD`.
5. Compare observations with `STATE.json`.
6. On unexpected divergence, stop; create `DIVERGENCE.md` describing expected state, observed state, difference, and possible cause; mark the run `BLOCKED`; do not fix it silently.
7. Run the commands in the handoff's validation section.
8. Continue only after validation, starting exactly from `NEXT.md`.

The receiver must verify the handoff rather than trust it.

## Validating a sealed checkpoint from a clean clone

1. Clone the repository into a new temporary directory.
2. Either stay on the default branch, or check out the checkpoint's canonical tag; a detached
   checkout of that tag is supported and validates as long as the worktree stays clean.
3. Run `python scripts/development-ledger/validate_checkpoint.py` and the handoff's commands.
4. Record the result in a new checkpoint. Never modify a sealed checkpoint, and never move its tag.

## Granting a Gate

The implementing run closes at `READY_FOR_REVIEW` and records `secondToolValidation` as
`PENDING_MANUAL`. The independent run performs the review and Red Team, sets that record to `PASSED`
or `FAILED` with tool, provider, and timestamp, and only then may a checkpoint reach `GATE_PASS`.

