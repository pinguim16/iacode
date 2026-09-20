# Diff Summary

- Added checkpoint `schemaVersion` `3.0.0` with version-dispatched validation, so the four sealed
  checkpoints keep validating unchanged while the new controls bind to new deliveries.
- R3.1: every finalization attempt is now recorded, including a refusal decided by a precondition
  before the operation runs, with the evaluated preconditions, a canonical `PRECONDITION_REJECTED`
  result, a documented result code, a failure reason, and no fabricated exit code.
- R3.2 and RT-02: command records carry runtime, working directory, sanitized arguments, referenced
  inputs, repository commit, purpose, canonical result, and duration, and the recorded command starts
  with an explicit runtime whose script path resolves from the working directory.
- RT-01: readiness and blockage can no longer be claimed together, in any schema version, and
  `BLOCKED` now requires a stated blocker.
- Added the Test Rework / Green Keeper role, its adapter, `green_keeper.py`, `REWORK-LOG.jsonl`, and
  the `GREEN_KEEPER_GATE`.
- Added the Delivery Completeness Validator role, its adapter, `check_completeness.py`,
  `COMPLETENESS-REPORT.json` and `.md`, and the `DELIVERY_COMPLETENESS_GATE`.
- Added `record_command.py` and `delivery_assurance.py`, plus schemas for the requirements matrix,
  the completeness report, and the rework log.
- `READY_FOR_REVIEW` now requires both new gates to be `PASS`, total requirement coverage, no red or
  unexecuted non-independent quality dimension, an empty `blockedBy`, and a still-pending independent
  review and Red Team.
- Made the eleven-step delivery order mandatory in the development contract, quality gates, checkpoint
  protocol, handoff protocol, definition of done, `START-HERE.md`, `AGENTS.md`, and `CLAUDE.md`, and
  added the delivery assurance section to the SETUP-00 checklist.
- Added ADR-0008 and documented the three new tools in the ledger tooling README.
- The suite grew from 75 to 131 tests, including regressions for every CP-0004 finding, the thirteen
  mandated control cases, the Green Keeper harness, the full delivery lifecycle, and compatibility
  with all four sealed checkpoints.
