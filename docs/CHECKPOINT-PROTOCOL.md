# Checkpoint Protocol

A checkpoint is a reconstructible snapshot of observable engineering state.

## Canonical statuses

`NOT_STARTED`, `BASELINING`, `IN_PROGRESS`, `BLOCKED`, `READY_FOR_REVIEW`, `REWORK_REQUIRED`, `READY_FOR_RED_TEAM`, `GATE_PASS`, `GATE_FAIL`.

## Required events

Create or finalize a checkpoint before a Gate, after baseline, after a material architecture decision or milestone, before and after destructive change, on important failure, before switching tools, before ending a session or likely context exhaustion, before merge, after Red Team, and at Gate closure.

## Required contents

Each checkpoint contains status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. `LATEST.md` points textually to the last checkpoint accepted by validation.

## Schema versions

`schemaVersion` selects the rules a checkpoint is judged by. Version `1.0.0` is the historical
format used by the sealed SETUP-00 checkpoints. Version `2.0.0` adds the structured cross-tool
validation state, evidence-referenced quality results, command identifiers, and the bound file
inventory described below. Validation applies the rules of the version a checkpoint declares, so a
sealed checkpoint never becomes invalid because the tooling advanced. New checkpoints use `2.0.0`.

## Commit semantics

Git commits cannot embed their own hash. Work-in-progress checkpoints may use the canonical symbolic value `HEAD`, which validation resolves to the checked-out commit. Any handoff-ready or terminal state (`READY_FOR_REVIEW`, `READY_FOR_RED_TEAM`, `GATE_PASS`, or `GATE_FAIL`) must instead use an immutable namespaced reference such as `refs/tags/iacode-checkpoints/SETUP-00-CP-0001`, created at the checkpoint commit after that commit exists. Validation resolves the tag and requires it to equal the checked-out commit. `UNBORN` is allowed only before a first commit; exact 40-character commit IDs are compared literally. The final report delivered to a user provides the resolved hash.

Self-hashes in `FILES.json` are omitted because changing that file changes its own hash. Other hashes are included when useful and stable. Text hashes use UTF-8 with line endings normalized to LF so validation remains portable across Git checkouts.

## Checkout modes

Validation normally runs on an attached branch, where the branch name and the checked-out commit
must both match `STATE.json`. A sealed checkpoint may also be validated from a detached checkout,
which is how another tool inspects an immutable reference. Detached validation removes the branch
control, so every remaining anchor becomes mandatory: the worktree must be clean and `dirty` must be
`false`, `currentCommit` must name the checkpoint's canonical `refs/tags/iacode-checkpoints/` tag,
that tag must exist, and it must resolve to the checked-out commit. Finalization always requires an
attached branch; a detached checkout is read-only.

## File inventory binding

For `schemaVersion` `2.0.0`, `FILES.json` is the authoritative description of the change set between
`baseCommit` and the validated tree, and validation recomputes that change set from Git. Every added,
modified, or deleted path must be declared exactly once with a reason, an undeclared change or a
declared non-change is an error, added and modified paths carry `hashAfter`, and modified and deleted
paths carry `hashBefore`. Hashes are re-derived by `finalize_checkpoint.py`; the author still supplies
every declaration and reason, because the tool never invents one. The single exclusion is
`FILES.json` itself, which cannot contain its own hash and is instead bound by the checkpoint commit,
its required presence, and its schema. See
[ADR-0006](adr/ADR-0006-checkpoint-inventory-binding.md).

## Finalization

Finalization is observable. Every attempt appends its own sanitized record, with its exit code, to
the checkpoint's `COMMANDS.jsonl`. A failed attempt restores the previous metadata but its record
stays, so corrections remain visible. The successful attempt is recorded before the inventory hashes
are sealed, so the command that produced the final state is itself covered by the inventory it seals.

## Promotion

The run that implements a Gate closes its checkpoint at `READY_FOR_REVIEW`. `GATE_PASS` is granted by
a later, independent run, and for `schemaVersion` `2.0.0` the validator refuses `GATE_PASS` unless
`secondToolValidation.status` is `PASSED`, or `NOT_REQUIRED` with a recorded justification.

## Divergence

If Git state differs unexpectedly from the checkpoint, do not continue. Create `DIVERGENCE.md` with expected, observed, difference, and possible cause; set status `BLOCKED`; wait for reconciliation.
