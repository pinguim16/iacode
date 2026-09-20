# Handoff Protocol

## Mandatory delivery order

`requirement extraction` → `baseline` → `plan` → `implementation` → `test and quality` →
`Green Keeper` → `Delivery Completeness Validator` → `READY_FOR_REVIEW` → `independent tool review` →
`Red Team` → `GATE_PASS`. No step may be skipped. The independent tool receives a delivery that has
already passed the internal controls; it is not the first line of defense against a red test or a
forgotten requirement.

## Before changing tools

1. Run the Green Keeper until every mandatory gate is green, or declare `BLOCKED`.
2. Run the Delivery Completeness Validator until coverage is total.
3. Finalize the checkpoint.
4. Validate it.
5. Update `docs/checkpoints/LATEST.md` textually; do not use a symlink.
6. Complete `HANDOFF.md` and `NEXT.md`.
7. Record branch, commit semantics, and dirty state.

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


## Milestone handoff

An intermediate Gate hands off internally and closes at `INTERNAL_GATE_PASS`. The Gate that closes a
milestone produces a milestone checkpoint consolidating the whole group: the Gates included, the
lessons produced, open risks, architecture changes, all tests, the regression position, cross-Gate
integration, requirements completeness, outstanding debt, provenance, and cost and model usage. That
checkpoint is what the external auditor receives, and it is the only handoff that asks for an
independent verdict. See [MILESTONE-VALIDATION.md](MILESTONE-VALIDATION.md).
