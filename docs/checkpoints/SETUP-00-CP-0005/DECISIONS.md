# Decisions

## Preserve every sealed checkpoint

`SETUP-00-CP-0001` through `SETUP-00-CP-0004` and their tags are untouched. `CP-0004`'s verdict of
`REWORK_REQUIRED` with `secondToolValidation.status = FAILED` stands as historical fact; this
checkpoint answers it rather than revising it.

## Extract requirements before implementing

`REQUIREMENTS-MATRIX.json` was written before the first implementation edit and carries 38
requirements drawn from the CP-0004 review and Red Team reports and from the authorizing prompt. A
requirement that exists only in a session is not a requirement, so the matrix, not the conversation,
is what the completeness audit reads.

## Version the format again instead of rewriting history

The delivery-assurance blocks, the reproducible command record, and the new gates change checkpoint
semantics, so they bind to `schemaVersion` `3.0.0`. Validation dispatches on the declared version and
`HistoricalCheckpointCompatibilityTests` runs the corrected validator against clean clones detached
at all four sealed tags. Recorded in
[ADR-0008](../../adr/ADR-0008-delivery-assurance-gates.md).

## A refusal is an attempt

The CP-0004 finding was that a finalization refused by a precondition left no trace. Preconditions
are now evaluated up front, the attempt is recorded before the error is returned, and the record
carries the evaluated preconditions with their observed values. No process runs during a refusal, so
inventing an exit code would be false evidence: the record instead carries
`result = PRECONDITION_REJECTED` with a documented `resultCode` and a `failureReason`.

## The status and blocker invariant applies to every version

RT-01 escaped because `blockedBy` was only inspected for `GATE_PASS`. A checkpoint that claims to be
ready while also claiming to be blocked is incoherent regardless of format, so the invariant is
enforced for every schema version and for any tool. `BLOCKED` now also requires a stated blocker.

## Gates are recomputed, never trusted

`green_keeper.py` and `check_completeness.py` produce the evidence, and `validate_checkpoint.py`
recomputes the completeness audit from the matrix and cross-checks the rework log. A checkpoint
cannot assert `GREEN_KEEPER_GATE=PASS` while its last cycle is red, nor
`DELIVERY_COMPLETENESS_GATE=PASS` over a matrix that does not support it.

## The implementer may not certify itself

`READY_FOR_REVIEW` now also requires `independentReview` and `redTeam` to remain `PENDING`. The
Green Keeper and the Completeness Validator are internal controls that make the delivery worth
reviewing; they are not a substitute for the independent run, and this checkpoint does not claim they
are.

## Role separation is emulated, and said to be

This session performed the implementation, the Green Keeper cycles, and the completeness audit. The
roles are separated by contract and by artifact, not by process: `.claude/agents/` carries a subagent
definition for each, and Codex adopts the canonical contracts through `AGENTS.md` because it has no
per-agent project file mechanism in this repository. The separation is documented as emulation rather
than described as independence.

## The Green Keeper was applied to this delivery

Several cycles of this checkpoint were red before it turned green: checkpoint validation failed while
the inventory was undeclared, a suite run failed because a lifecycle fixture did not ship the ledger
tooling whose path it recorded, the first ledger record predated the new command format, the
validation gate always observed stale hashes because a gate run appends to the checkpoint's own
evidence, and the report generators emitted a trailing blank line. Every one was repaired at the
cause, never by weakening a check, and every cycle with its root cause is in `REWORK-LOG.jsonl`.
`git log` and that file are the complete record; this decision states the mechanism rather than
enumerating instances, so it stays accurate without needing a correction to describe itself.

## Corrections before handoff re-create this checkpoint's own tag

Whenever a defect was found in this checkpoint after it had been sealed but before it was handed off,
it was corrected in its own commit rather than amended away, so every superseded sealing commit stays
reachable with a message saying what it got wrong. Each such correction required
`refs/tags/iacode-checkpoints/SETUP-00-CP-0005` to be deleted and re-created, because validation
requires the tag to resolve to the checked-out commit. This is bounded and does not weaken the audit
model: the tag existed only in this working repository, no handoff or publication had occurred, no
history was rewritten, and no sealed checkpoint or historical tag was touched. `git log` is the
complete record. Once this checkpoint reaches the independent run, its tag is immutable like the
others.

## Secret scanner scope unchanged

The detector still matches the scope documented in `.iacode/policies/secret-policy.md`. Expanding it
was not bundled into this correction, and the limitation remains recorded in `RISKS.md`.
