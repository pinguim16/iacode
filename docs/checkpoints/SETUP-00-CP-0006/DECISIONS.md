# Decisions

## Preserve every sealed checkpoint

`SETUP-00-CP-0001` through `SETUP-00-CP-0005` and their tags are untouched. The engineering memory is
seeded from what those checkpoints already recorded; it does not reinterpret them.

## The memory belongs to the project, not to the user

`.iacode/memory/` holds organizational engineering knowledge: what failed here, why, and what now
prevents it. It holds no personal preference, no profile, no chain-of-thought and no secret, and the
validator scans every lesson field for credential shapes.

## Memory is not enough, so a lesson must become a guardrail

Prose depends on a future run remembering to read it, and that dependency has already failed in this
project. The stated preference is an automated control first, a preflight-enforced lesson second,
prose last. `GUARDED` therefore requires a control of kind test, validator, lint, policy, schema,
invariant or automated check, and `validate_lessons.py` rejects a `GUARDED` lesson whose only
prevention is documentation.

## Only confirmed history became a lesson

Fourteen lessons were seeded, each citing a specific finding in a sealed checkpoint. Twelve are
`GUARDED` by named tests and validator behaviour. Two are deliberately `CONFIRMED`: neither the state
of an arbitrary machine's installation nor the moment a record was written can be observed from this
repository, so claiming a control for them would be false. They are carried by the mandatory
preflight instead, which is precisely why the preflight is not optional.

## A lesson reaches the work through a requirement, not through reading

`lesson_preflight.py` turns each applicable lesson into a `LESSON-REQ-` requirement of the Gate, and
the completeness audit fails the delivery when one is absent. That is what converts the memory from a
document into a control.

## The derived requirements of this Gate were added after the memory existed

The requirements matrix was written before implementation, as the contract demands. The fourteen
`LESSON-REQ-` entries were appended once the memory they derive from existed, which is unavoidable in
the delivery that creates the memory. Every later Gate runs the preflight first and has them from the
start.

## External validation is grouped into milestones

Calling the external auditor after every Gate is expensive and misdirected now that the internal
gates exist. Gates are grouped into `M0` to `M6`; an intermediate Gate closes at
`INTERNAL_GATE_PASS`, and the Gate that closes a milestone is audited as a whole. An extraordinary
audit is possible only through `externalAuditRequired` with a reason naming a recorded trigger.

## Internal and external approval are different statuses

`INTERNAL_GATE_PASS` and `MILESTONE_EXTERNAL_PASS` exist so the difference cannot be blurred by
wording. Validation refuses an external status without a passed milestone and a passed cross-tool
validation, and refuses an internal status that carries an external verdict.

## Version the format again rather than rewrite history

The new blocks bind to `schemaVersion` `3.1.0`. `1.0.0`, `2.0.0` and `3.0.0` keep their rules, and
the regression suite validates clean clones detached at all five sealed tags. Recorded in
[ADR-0009](../../adr/ADR-0009-engineering-memory-and-milestone-validation.md).

## This checkpoint closes at READY_FOR_REVIEW, not INTERNAL_GATE_PASS

`INTERNAL_GATE_PASS` is introduced by this delivery and belongs to Gates that close on the project's
own controls under the new cadence. SETUP-00 itself is the `M0` milestone and still owes an external
audit, so this checkpoint is offered for review in the established way and the Gate verdict stays
with Codex.

## Corrections before handoff re-create this checkpoint's own tag

A defect found in this checkpoint after sealing but before handoff is corrected in its own commit
rather than amended away, so every superseded sealing commit stays reachable with a message saying
what it got wrong. Each such correction deletes and re-creates
`refs/tags/iacode-checkpoints/SETUP-00-CP-0006`, because validation requires the tag to resolve to
the checked-out commit. No sealed checkpoint and no historical tag is touched, and `git log` is the
complete record.
