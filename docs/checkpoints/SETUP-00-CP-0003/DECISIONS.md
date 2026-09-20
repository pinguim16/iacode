# Decisions

## Preserve both sealed checkpoints

`SETUP-00-CP-0001` and `SETUP-00-CP-0002`, and their tags, are untouched. Their statements, including
`CP-0002`'s `GATE_PASS`, remain historical fact. This checkpoint corrects the control plane going
forward; it does not reinterpret what those checkpoints recorded.

## Version the checkpoint format instead of rewriting history

The corrections change checkpoint semantics, so they are bound to a new `schemaVersion`, `2.0.0`.
Validation dispatches on the version a checkpoint declares, which keeps the sealed `1.0.0`
checkpoints valid under the rules they were written against. `HistoricalCheckpointCompatibilityTests`
runs the corrected validator against clean clones detached at both sealed tags.
Recorded in [ADR-0007](../../adr/ADR-0007-checkpoint-schema-2-and-independent-promotion.md).

## Accept a detached HEAD only at the checkpoint's own tag

A detached checkout is the natural way for a second tool to inspect an immutable reference, and the
previous validator rejected it as a branch mismatch. Detached validation is now allowed, but only
when the worktree is clean, `currentCommit` names the canonical tag, the tag exists, and it resolves
to the checked-out commit. Detachment is never a generic relaxation, and finalization still requires
an attached branch.

## Bind the file inventory to Git rather than to an assertion

The manifest is now recomputed from the repository and compared to `FILES.json` exactly, with content
hashes on both sides of each change. `finalize_checkpoint.py` derives the hashes but never invents a
declaration, so authorship of the change set stays with the author while verification stays with the
tool. The single self-referential exclusion, `FILES.json` itself, is declared in code and justified in
[ADR-0006](../../adr/ADR-0006-checkpoint-inventory-binding.md).

## Make finalization observable instead of inferable

Every finalization attempt appends its own record with its exit code. A failure restores the previous
metadata but keeps its record and a sanitized summary of the reasons, and the successful attempt is
written before the hashes are sealed so it falls inside the inventory it seals. This removes the
`CP-0002` gap where two failures were recorded and the successful transition was not.

## Replace prose status with structured state

`secondToolValidation` in `STATE.json` carries an explicit status and attribution. The hardcoded
requirement for the sentence `SECOND_TOOL_VALIDATION = PENDING_MANUAL` now applies only to `1.0.0`
checkpoints, so a future run can record a completed cross-tool validation truthfully.

## Require evidence for every PASS

`QUALITY.json` `2.0.0` records `{status, evidence, justification}` per dimension, and a `PASS` must
reference a command that exited `0` or a non-empty file inside the checkpoint. This is an explicit
reference mechanism, not a heuristic over command text.

## The implementing run does not grant the Gate

This run is Claude Code. It closes at `READY_FOR_REVIEW`, records `secondToolValidation` as
`PENDING_MANUAL`, and labels its own review and adversarial work as non-independent. The validator now
refuses `GATE_PASS` unless cross-tool validation is `PASSED` or explicitly justified as
`NOT_REQUIRED`.

## Command timestamps in this checkpoint

Records `cmd-0001` through `cmd-0010` were written after their commands ran, because the recorder was
introduced during the run; their ordering is exact and their timestamps are recording times, which is
stated in each record. Every later record carries the real execution time and measured duration.

## Corrected the handoff before handing it off, and re-created this checkpoint's own tag

The first sealing commit, `64b132ca70a521d5ba8844dd3e976a4cb74f3e47`, carried a false statement in
`HANDOFF.md`: it claimed that two failed finalization records were present in this ledger. Those two
failures happened in the isolated sealing rehearsal and died with that fixture; the real ledger
contains only the successful finalization. Shipping that sentence would have been exactly the kind of
unverifiable claim this correction exists to prevent, so it was fixed and the checkpoint was re-sealed
at a later commit.

Re-sealing required the `refs/tags/iacode-checkpoints/SETUP-00-CP-0003` tag to be deleted and
re-created, because validation requires the tag to resolve to the checked-out commit. This is
recorded rather than done quietly. It is bounded and does not weaken the audit model: the tag had
existed only in this working repository for a few minutes, no handoff or publication had occurred, no
history was rewritten, the superseded commit `64b132ca70a521d5ba8844dd3e976a4cb74f3e47` remains
reachable in the branch, and no sealed checkpoint tag was touched. Once this checkpoint is handed to
the independent run, its tag is immutable like the others.

## Secret scanner scope left unchanged

The independent review confirmed that the detector matches the scope documented in
`.iacode/policies/secret-policy.md` and that the uncovered credential shapes are recorded as residual
risk. Expanding the detector was not bundled into this correction, to keep the six findings and their
regressions reviewable. The limitation is restated in `RISKS.md`.
