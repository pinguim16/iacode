# Checkpoint Protocol

A checkpoint is a reconstructible snapshot of observable engineering state.

## Canonical statuses

`NOT_STARTED`, `BASELINING`, `IN_PROGRESS`, `BLOCKED`, `READY_FOR_REVIEW`, `REWORK_REQUIRED`, `READY_FOR_RED_TEAM`, `GATE_PASS`, `GATE_FAIL`.

## Required events

Create or finalize a checkpoint before a Gate, after baseline, after a material architecture decision or milestone, before and after destructive change, on important failure, before switching tools, before ending a session or likely context exhaustion, before merge, after Red Team, and at Gate closure.

## Required contents

Each checkpoint contains status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. `LATEST.md` points textually to the last checkpoint accepted by validation.

## Commit semantics

Git commits cannot embed their own hash. Work-in-progress checkpoints may use the canonical symbolic value `HEAD`, which validation resolves to the checked-out commit. Any handoff-ready or terminal state (`READY_FOR_REVIEW`, `READY_FOR_RED_TEAM`, `GATE_PASS`, or `GATE_FAIL`) must instead use an immutable namespaced reference such as `refs/tags/iacode-checkpoints/SETUP-00-CP-0001`, created at the checkpoint commit after that commit exists. Validation resolves the tag and requires it to equal the checked-out commit. `UNBORN` is allowed only before a first commit; exact 40-character commit IDs are compared literally. The final report delivered to a user provides the resolved hash.

Self-hashes in `FILES.json` are omitted because changing that file changes its own hash. Other hashes are included when useful and stable. Text hashes use UTF-8 with line endings normalized to LF so validation remains portable across Git checkouts.

## Divergence

If Git state differs unexpectedly from the checkpoint, do not continue. Create `DIVERGENCE.md` with expected, observed, difference, and possible cause; set status `BLOCKED`; wait for reconciliation.
