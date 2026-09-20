# Handoff

Current Gate: SETUP-00
Current Status: READY_FOR_REVIEW

Last valid commit: 276645b4498a0e58a1bf38979b5e078669dbb380
Current branch: main

Checkpoint schema version: `3.1.0`. Base checkpoint: `SETUP-00-CP-0005` at
`276645b4498a0e58a1bf38979b5e078669dbb380`. Final reference:
`refs/tags/iacode-checkpoints/SETUP-00-CP-0006`, to be resolved with `git rev-parse`.

## Objective

Give the control plane a permanent engineering memory that turns confirmed failures into automated
guardrails, make a lesson preflight mandatory before every Gate, wire lessons into the requirements
matrix, and replace per-Gate external validation with a milestone audit cadence.

## What was completed

- Engineering memory at `.iacode/memory/`, organizational rather than personal, with the lesson
  schema, the rendered index, and the patterns, anti-patterns, incidents, guardrails and
  retrospectives directories.
- Fourteen lessons seeded strictly from findings recorded in the five sealed checkpoints. Twelve are
  `GUARDED` by named automated controls; two are `CONFIRMED` because nothing in this repository can
  observe them, and they are carried by the preflight instead.
- `GUARDED` requires a real preventive control. Documentation alone is rejected by
  `validate_lessons.py`.
- Recurrence: a repeat increments `recurrenceCount`, and a repeat against a `GUARDED` lesson records
  a `GUARDRAIL_FAILURE`, escalates severity and reopens the lesson.
- Mandatory lesson preflight writing `LESSON-PREFLIGHT.json` and `.md`, deriving a `LESSON-REQ-`
  requirement per applicable lesson. A missing derived requirement is a blocking completeness
  finding.
- Lesson extraction from recorded delivery evidence, never stronger than `OBSERVED`.
- Lesson validation added to the Green Keeper gate set.
- Milestone validation policy: `M0` to `M6`, the `INTERNAL_GATE_PASS` and `MILESTONE_EXTERNAL_PASS`
  statuses, the milestone checkpoint contents, the auditor role, and `externalAuditRequired` with a
  recorded trigger.
- Checkpoint `schemaVersion` `3.1.0` with version dispatch; all five sealed checkpoints still
  validate.
- Retrospective template and this Gate's retrospective.
- The suite grew from 131 to 181 tests.

## What was NOT completed

The `M0` external audit, the independent review, the independent Red Team, and any Gate verdict.
`secondToolValidation` remains `PENDING_MANUAL` and `milestone.status` remains `PENDING`. Gate 0
remains unimplemented and unauthorized. The secret detector's scope was deliberately left unchanged.

## Current repository state

Branch `main`, clean after the sealing commit, base commit
`276645b4498a0e58a1bf38979b5e078669dbb380`, final commit bound by
`refs/tags/iacode-checkpoints/SETUP-00-CP-0006`. `STATE.json` records the exact values.

## Files changed

See `FILES.json`, verified against the real change set since the base commit with content hashes. In
summary: the engineering memory tree, four lesson tools, three extended ledger tools, five schemas
including two new ones, the test suite, seven canonical agent contracts, two new documents, nine
updated governing documents, one new ADR, `LATEST.md`, and this checkpoint.

## Important decisions

See `DECISIONS.md` and ADR-0009. The load-bearing ones: the memory belongs to the project; memory is
not enough, so a lesson must become a guardrail; a lesson reaches the work as a requirement rather
than as reading; external validation is grouped into milestones; and internal approval is a different
status from external approval.

## Tests executed

`python -m unittest discover -s tests` — 181 tests, 0 failures, recorded in `TESTS.json` and
`COMMANDS.jsonl`. `python -m compileall -q scripts tests` — exit 0.
`python scripts/development-ledger/validate_lessons.py` — `LESSONS_VALID`.
`python scripts/development-ledger/validate_checkpoint.py` — `CHECKPOINT_VALID`. Every gate run is
in `REWORK-LOG.jsonl` with its ledger evidence.

## Known failures

Recorded in `REWORK-LOG.jsonl` and `COMMANDS.jsonl` with root causes. Any nonzero exit in
`COMMANDS.jsonl` belongs to a recorded rework cycle or to a recorded finalization attempt; each was
repaired at the cause and re-executed.

## Known risks

See `RISKS.md`, especially the pending `M0` audit, the delay a milestone cadence can introduce, the
two lessons that cannot be guarded, and the emulated role separation.

## Do not repeat

Do not modify or retag any sealed checkpoint. Do not mark a lesson `GUARDED` without a real control.
Do not skip the lesson preflight. Do not describe an internal verdict as independent external
validation. Do not request an extraordinary audit without a recorded trigger. Do not start Gate 0.

## Required next action

A single Codex `M0` milestone audit covering `SETUP-00-CP-0005`, this checkpoint, and SETUP-00 as a
whole, as described in `NEXT.md`.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/SETUP-00-CHECKLIST.md`, `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`,
   `docs/CHECKPOINT-PROTOCOL.md`, `docs/QUALITY-GATES.md`, `docs/HANDOFF-PROTOCOL.md`,
   `docs/DEFINITION-OF-DONE.md`, `docs/checkpoints/LATEST.md`, and this complete checkpoint.
2. Read `SETUP-00-CP-0005` in full; the `M0` audit covers both checkpoints.
3. Read ADR-0008 and ADR-0009 for the reasoning behind the delivery gates and the memory policy.
4. Run the validation commands below and compare the observed Git state with `STATE.json`.
5. Review `git diff 276645b4498a0e58a1bf38979b5e078669dbb380..refs/tags/iacode-checkpoints/SETUP-00-CP-0006`.
6. Run the milestone verification recipes below, plus your own attacks.
7. Record the verdict in a new milestone checkpoint that sets `secondToolValidation` and
   `milestone.status`. Never edit a sealed checkpoint.

## Validation commands

- `git status --short --branch`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0006`
- `python scripts/development-ledger/validate_checkpoint.py`
- `python scripts/development-ledger/validate_lessons.py`
- `python scripts/development-ledger/check_completeness.py`
- `python -m unittest discover -s tests`
- `python -m compileall -q scripts tests`
- `git diff --check 276645b4498a0e58a1bf38979b5e078669dbb380 HEAD`

## How to verify the M0 scope

- Memory integrity: `validate_lessons.py` must report `LESSONS_VALID`. Set any `GUARDED` lesson's
  `prevention` to a documentation-only control and confirm it is rejected. Automated as
  `LessonValidationTests`.
- Guardrail claims: every `GUARDED` lesson names a control in `.iacode/memory/guardrails/README.md`.
  Delete one of those controls and confirm a test fails.
- Preflight enforcement: remove a `LESSON-REQ-` entry from `REQUIREMENTS-MATRIX.json` and rerun
  `check_completeness.py`; it must report a blocking finding. Automated as
  `DerivedRequirementCompletenessTests`.
- Cadence: `requires_external_validation` must be false for an intermediate Gate and true for a
  milestone-closing Gate. Automated as `MilestoneValidationPolicyTests`.
- Vocabulary: a `MILESTONE_EXTERNAL_PASS` without a passed cross-tool validation, and an
  `INTERNAL_GATE_PASS` carrying one, must both be refused. Automated as
  `MemoryPolicyValidationTests`.
- Historical immutability: clean clones detached at all five sealed tags must validate. Automated as
  `HistoricalCheckpointCompatibilityTests`.
- CP-0005 findings: the R3, RT-01 and RT-02 recipes in `SETUP-00-CP-0005/HANDOFF.md` still apply and
  should be re-run as part of the milestone.

## Criteria for PASS

Both checkpoints' requirements complete with resolvable evidence; the memory valid with every
`GUARDED` lesson backed by a real control; the preflight enforced through derived requirements; the
cadence and verdict vocabulary enforced; both delivery gates `PASS`; the suite green with no
regression; the five sealed checkpoints still validating; the checkpoint valid; the handoff
reproducible without this session; no sealed artifact modified; no Gate 0 work present.

## Criteria for REWORK_REQUIRED

Any lesson marked `GUARDED` without a real control; any selected lesson absent from the matrix; any
requirement whose recorded status overstates reality; any internal verdict presented as external; any
extraordinary audit without a recorded trigger; any regression; any sealed checkpoint made invalid;
any inconsistency between `STATE.json`, the matrix, the preflight, the reports, the ledger and the
repository; or any integration defect between the delivery gates and the memory controls.

## Stop conditions

Stop on unexpected Git divergence, on a failing validation, on any need to modify a sealed
checkpoint, on secret exposure, or on any request to begin Gate 0 without authorization.
