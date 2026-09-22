# ADR-0023 — A sealed checkpoint is bound to its own canonical tag

Status: Accepted
Date: 2026-09-22
Owners: GATE 2 — Agent Runtime (closure, `GATE-2-CP-0002`)

## Context

A checkpoint is validated from its own tag long after it was sealed: every successor, the internal
mirror's historical-compatibility probe (`MIR-016`) and
`test_every_sealed_checkpoint_validates_from_its_own_tag` check out each anchored checkpoint's
`refs/tags/iacode-checkpoints/<id>` with a detached HEAD and run the validator there. With a detached
HEAD the branch-identity control is gone, so the validator required `STATE.json` `currentCommit` to
name the checkpoint tag and required that tag to resolve to the checked-out commit.

Two other rules made that requirement unreachable for part of the status space.
`docs/CHECKPOINT-PROTOCOL.md` lets a work-in-progress status keep the symbolic `HEAD`, and only a
handoff-ready or terminal status must name an immutable reference. `seal_checkpoint.py` sealed
whatever state it was given. `GATE-2-CP-0001` was finalized at `BLOCKED`, which may keep `HEAD`,
sealed with it, and tagged — and from that moment could not be validated from its own tag at all.
Nothing noticed while it was the latest checkpoint, because the newest sealed checkpoint is not
yet anchored; the first successor anchored it and the historical check turned red for good
(`G2-F-013`).

The sealed checkpoint cannot be repaired: it is immutable, its tag cannot move, and the integrity
chain exists to detect either.

## Decision

**A sealed checkpoint is bound to its own canonical tag, whichever way its state names it.**

1. With a detached HEAD, `currentCommit` naming `refs/tags/iacode-checkpoints/<id>` is checked as
   before. `currentCommit` equal to the symbolic `HEAD` is accepted only when the checkpoint's own
   canonical tag — derived from its directory, `refs/tags/iacode-checkpoints/<checkpoint id>` —
   exists and resolves to the checked-out commit. Any other value is still refused, and a symbolic
   HEAD checked out anywhere but at that tag is refused with the same message a named tag gets.
2. `seal_checkpoint.py` refuses to seal a checkpoint whose `currentCommit` is not its own canonical
   tag, before it validates, commits or tags anything. A checkpoint is therefore finalized with
   `--commit-ref refs/tags/iacode-checkpoints/<id>` before it is sealed, at every status.

The first rule is what lets the one checkpoint sealed the old way be validated from its tag; the
second is what keeps it the only one.

## Consequences

- The binding is not weakened: in both forms the checked-out commit must be the checkpoint's own
  canonical tag, and the tag's commit is anchored in `.iacode/anchors/checkpoint-chain.json`, so a
  moved tag is still detected there. What the first form no longer requires is that the state
  *spell* the tag; the identity it binds to is the one the directory already carries.
- The dirty-tree rule of a detached HEAD is unchanged: clean worktree and `dirty=false`.
- No sealed checkpoint was edited and no tag was moved. `GATE-2-CP-0001` validates from its tag
  under this rule, and `test_every_sealed_checkpoint_validates_from_its_own_tag` checks every
  anchored checkpoint again.
- Controls: `test_a_symbolic_head_validates_from_its_own_canonical_tag`,
  `test_a_symbolic_head_away_from_its_canonical_tag_is_still_refused` and
  `test_sealing_refuses_a_state_that_does_not_name_its_own_tag`, each shown to fail on the previous
  tooling. Recorded as `LSN-0050` and `GRD-0052`.
- Operators sealing a `BLOCKED` checkpoint now pass `--commit-ref` exactly as they do for
  `INTERNAL_GATE_PASS`; the refusal names the reference to pass.
