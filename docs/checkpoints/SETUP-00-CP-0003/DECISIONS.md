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

## Secret scanner scope left unchanged

The independent review confirmed that the detector matches the scope documented in
`.iacode/policies/secret-policy.md` and that the uncovered credential shapes are recorded as residual
risk. Expanding the detector was not bundled into this correction, to keep the six findings and their
regressions reviewable. The limitation is restated in `RISKS.md`.
