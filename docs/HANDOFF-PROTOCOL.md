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

