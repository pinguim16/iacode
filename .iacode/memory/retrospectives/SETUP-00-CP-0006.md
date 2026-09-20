# Retrospective — SETUP-00 / SETUP-00-CP-0006

Scope: the checkpoint that introduced the engineering memory, the lesson preflight, and the milestone
validation cadence. Observations and evidence only; no chain-of-thought and no secrets.

## What went well

- The delivery-assurance gates introduced by `SETUP-00-CP-0005` worked on their first real reuse.
  The Green Keeper caught every red state of this delivery before any handoff, and the completeness
  audit refused the matrix until it was total.
- Version dispatch again allowed a substantial format change without touching sealed history. All
  five sealed checkpoints still validate, proven by `HistoricalCheckpointCompatibilityTests`.
- Writing the requirements matrix before implementation kept the scope of a large prompt explicit;
  nothing had to be reconstructed from memory of the instructions at the end.
- Seeding the memory from sealed checkpoints rather than from recollection produced fourteen lessons
  that each cite a specific finding, and twelve of them already had a real control to point at.

## What failed

Recorded in `REWORK-LOG.jsonl` with root causes. Three distinct causes appeared: a provenance field
that had to be a string, a test carrying a secret-shaped literal that the repository scan correctly
flagged, and state that did not yet record the preflight counts. Each was repaired at the cause.

The completeness audit also failed its first run, because two requirements cited the report that the
run itself writes. It passed on the next run, once the artifact existed. That is the same
self-reference class as `LSN-0011`, so this delivery exercised that lesson as a live constraint
rather than as a historical note: the audit found a real gap, returned it to the implementer, and was
re-run, which is exactly the loop the process prescribes.

## What repeated

`LSN-0011`, the self-reference hazard, applied directly to the new lesson and milestone controls
while they were being written. It was `GUARDED` before this Gate and the guardrail held: the control
design was adjusted before the delivery, not after an auditor found it. No `GUARDRAIL_FAILURE` was
recorded in this Gate.

## What was learned

- A memory only becomes a control when something fails without it. The preflight, not `LESSONS.md`,
  is what makes a lesson unavoidable.
- The distinction between an internal verdict and an external one has to be a status, not a wording
  convention. Two statuses cannot be blurred in a sentence the way one status plus an adjective can.
- A lesson that cannot be guarded is still worth keeping, provided the preflight forces the next Gate
  to answer it. `LSN-0013` and `LSN-0014` are deliberately `CONFIRMED` for that reason.

## What should become a guardrail

| Item | Control | Kind | Where | Removing it would allow |
|---|---|---|---|---|
| A lesson claimed as guarded with no real control | `validate_lessons.py` preventive-control rule | validator | `scripts/development-ledger/lessons.py` | Documentation to masquerade as prevention. |
| A selected lesson dropped from the matrix | derived-requirement check in the completeness audit | automated-check | `scripts/development-ledger/delivery_assurance.py` | A Gate to ignore a known failure class. |
| An internal verdict presented as external | `INTERNAL_GATE_PASS` versus `MILESTONE_EXTERNAL_PASS` | invariant | `validate_checkpoint.py` | Self-certification by vocabulary. |
| An unjustified early external audit | `externalAuditRequired` plus a recorded trigger | invariant | `validate_checkpoint.py` | The cadence to be abandoned case by case. |

All four were implemented in this Gate and are covered by tests.

## New lessons

| Lesson | Status | Guarded by |
|---|---|---|
| `LSN-0001` … `LSN-0012` | `GUARDED` | Named tests and validator behaviour, listed in `.iacode/memory/guardrails/README.md`. |
| `LSN-0013` | `CONFIRMED` | Not guarded: an arbitrary machine's installation state cannot be observed from this repository. Carried by the preflight. |
| `LSN-0014` | `CONFIRMED` | Not guarded: an artifact cannot prove that a record was written at execution time. Carried by the preflight. |

All fourteen are seeded from findings already recorded in `SETUP-00-CP-0001` through
`SETUP-00-CP-0005`. None was invented for this Gate.

## Updated lessons

| Lesson | Change | Reason |
|---|---|---|
| _none_ | — | This Gate created the memory; no earlier lesson existed to update. |

## Retired lessons

| Lesson | Superseded by | Reason |
|---|---|---|
| _none_ | — | No lesson has stopped applying yet. |
