# Plan

## Objective

Give the Development Control Plane a permanent engineering memory that turns confirmed failures into
automated guardrails, make a lesson preflight mandatory before every Gate, wire lessons into the
requirements matrix, and replace per-Gate external validation with a milestone audit cadence. Close at
`READY_FOR_REVIEW`. Do not start Gate 0.

## Baseline

Recorded before any change: branch `main`, `HEAD = 276645b4498a0e58a1bf38979b5e078669dbb380`, clean
worktree, `CHECKPOINT_VALID`, `python -m unittest discover -s tests` 131 of 131 passing in 99.651s,
`python -m compileall -q scripts tests` exit 0, and `check_completeness.py` reporting
`DELIVERY_COMPLETENESS_GATE=PASS` at total coverage for the sealed `SETUP-00-CP-0005`.

## Requirements

The authoritative scope is `REQUIREMENTS-MATRIX.json`, written before implementation with 33
requirements extracted from the authorizing prompt and the governing documents. Lesson-derived
`LESSON-REQ-` requirements are appended once the memory exists, because they are produced by the
preflight from the lessons this checkpoint creates; that ordering is a property of the first delivery
that introduces the memory and is recorded in `DECISIONS.md`.

## Steps

1. Create `.iacode/memory/` with its README, the human index, the machine-readable `lessons.jsonl`,
   and the pattern, anti-pattern, incident, guardrail, and retrospective directories.
2. Add `lesson.schema.json` and `lesson-preflight.schema.json`, covering the mandated fields, the
   five statuses, the sixteen categories, recurrence, provenance, and training denied by default.
3. Add `validate_lessons.py`, `extract_lessons.py`, and `lesson_preflight.py`, and make lesson
   validation part of the Green Keeper gate set.
4. Populate the initial memory strictly from facts confirmed by `SETUP-00-CP-0001` through
   `SETUP-00-CP-0005`, with each lesson naming its historical evidence and, when it is `GUARDED`, the
   automated control that now prevents it.
5. Run the preflight for this Gate, turn its applicable lessons into `LESSON-REQ-` requirements, and
   make the completeness audit fail when a derived requirement is absent from the matrix.
6. Introduce the milestone validation policy: the `M0` to `M6` grouping, the
   `INTERNAL_GATE_PASS` and `MILESTONE_EXTERNAL_PASS` statuses, the milestone checkpoint contents,
   and `externalAuditRequired` with a recorded reason for an extraordinary audit.
7. Bind the new blocks to checkpoint `schemaVersion` `3.1.0` so `3.0.0` and every sealed checkpoint
   keep the rules they were written against.
8. Update the governing documents, add `docs/ENGINEERING-MEMORY.md` and
   `docs/MILESTONE-VALIDATION.md`, update the seven affected canonical agent contracts, and record an
   ADR.
9. Add the mandated regressions, run the Green Keeper until green, run the Delivery Completeness
   Validator until coverage is total, then finalize, commit, tag, and validate.

## Probable files

`.iacode/memory/**`, `.iacode/schemas/*.json`, `.iacode/agents/*.md`, `.iacode/templates/**`,
`scripts/development-ledger/*.py`, `tests/test_development_ledger.py`, `docs/ENGINEERING-MEMORY.md`,
`docs/MILESTONE-VALIDATION.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
`docs/ROADMAP.md`, `docs/QUALITY-GATES.md`, `docs/DEFINITION-OF-DONE.md`,
`docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`, `docs/SETUP-00-CHECKLIST.md`,
`START-HERE.md`, `AGENTS.md`, `CLAUDE.md`, a new ADR, and this checkpoint.

## Success criteria

Every requirement `COMPLETE` with resolvable evidence; lesson-derived requirements present and
satisfied; the lesson validator green; both delivery gates `PASS`; the suite green with no
regression; the five sealed checkpoints still validating; checkpoint valid at `READY_FOR_REVIEW`;
`NEXT.md` requesting a single `M0` audit.

## Tests

The existing 131 plus the seventeen mandated cases for lesson schema validity, invalid lessons,
duplicate identifiers, `GUARDED` without preventive evidence, secrets in a lesson, training denied by
default, recurrence increments, preflight selection and rejection, derived requirement generation,
missing derived requirement blocking completeness, retired lessons producing no requirement, milestone
grouping, intermediate Gates not requiring Codex, milestones requiring external validation,
extraordinary audits requiring a justification, and historical checkpoints remaining valid.

## Risks

A memory can become a document nobody reads; a lesson can be marked guarded without a real control; a
milestone cadence can delay the discovery of a systemic defect; new schema blocks can invalidate
sealed checkpoints. Each is addressed by machine-checked preventive evidence, by derived requirements
that must be satisfied, by the extraordinary audit trigger, and by version dispatch with regression
coverage over every sealed tag.

## Stop conditions

Stop on unexpected Git divergence, on any need to modify a sealed checkpoint, on a red gate that
cannot be repaired inside SETUP-00 scope, on secret exposure, or on any request to begin Gate 0.
