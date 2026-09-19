# Checkpoint Protocol

A checkpoint is a reconstructible snapshot of observable engineering state.

## Canonical statuses

`NOT_STARTED`, `BASELINING`, `IN_PROGRESS`, `BLOCKED`, `READY_FOR_REVIEW`, `REWORK_REQUIRED`, `READY_FOR_RED_TEAM`, `GATE_PASS`, `GATE_FAIL`.

## Required events

Create or finalize a checkpoint before a Gate, after baseline, after a material architecture decision or milestone, before and after destructive change, on important failure, before switching tools, before ending a session or likely context exhaustion, before merge, after Red Team, and at Gate closure.

## Required contents

Each checkpoint contains status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. `LATEST.md` points textually to the last checkpoint accepted by validation.

## Commit semantics

Git commits cannot embed their own hash. To avoid an unverifiable self-reference, `currentCommit` and `finalCommit` may use the canonical symbolic value `HEAD`; validation resolves it to the currently checked-out commit. `UNBORN` is allowed only before a first commit. Exact 40-character commit IDs are compared literally. The final report delivered to a user provides the resolved final commit.

Self-hashes in `FILES.json` are omitted because changing that file changes its own hash. Other hashes are included when useful and stable.

## Divergence

If Git state differs unexpectedly from the checkpoint, do not continue. Create `DIVERGENCE.md` with expected, observed, difference, and possible cause; set status `BLOCKED`; wait for reconciliation.

