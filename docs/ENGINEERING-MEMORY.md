# Engineering Memory

The IACode engineering memory is the project's record of what its own engineering has learned. It
lives in [.iacode/memory/](../.iacode/memory/README.md), it belongs to the engineering organization,
and it is not the user's personal memory. It holds no preferences, no profile, and no private
reasoning.

Its only purpose is to stop the same class of failure from happening twice.

## Memory is not enough

**An important lesson must become a guardrail.** A written lesson depends on a future run
remembering to read it, and that dependency has already failed in this project: `SETUP-00-CP-0004`
found two controls that the protocol documents described as working and that nothing enforced. The
order of preference is therefore fixed:

1. an automated control that makes the failure impossible or immediately visible;
2. a recorded lesson that the mandatory preflight forces the next Gate to answer;
3. prose.

No control may rest on someone remembering to open `LESSONS.md`. A lesson reaches `GUARDED` only when
at least one control of kind `test`, `validator`, `lint`, `policy`, `schema`, `invariant` or
`automated-check` prevents recurrence, and `validate_lessons.py` rejects any `GUARDED` lesson that
offers only documentation.

## Lesson contract

Each lesson is one line of `.iacode/memory/lessons.jsonl`, validated against
`.iacode/schemas/lesson.schema.json`, and carries the identifier, title, category, severity, source
Gate, checkpoint and finding, symptom, root cause, resolution, prevention controls, evidence,
applicability, status, recurrence key, recurrence count, timestamps, provenance, and training
eligibility.

Categories: `architecture`, `implementation`, `testing`, `quality`, `security`, `documentation`,
`tooling`, `git`, `checkpoint`, `process`, `provider`, `model-behavior`, `training`, `data`,
`performance`, `environment`.

Rules:

- Evidence must exist in this repository. A lesson is never invented.
- No secret and no chain-of-thought. The validator scans every lesson field.
- `trainingAllowed` is `false` by default and requires a recorded rights justification to be true.

## Lifecycle

```text
OBSERVED -> CONFIRMED -> GUARDED
                     \-> SUPERSEDED / RETIRED
```

`OBSERVED` is a candidate produced from recorded evidence. `CONFIRMED` means the root cause is
understood and the resolution is real. `GUARDED` means an automated control now prevents it.
`SUPERSEDED` names its successor. `RETIRED` no longer applies. A `SUPERSEDED` or `RETIRED` lesson
produces no requirement.

Promotion is never automatic. `extract_lessons.py` may only create `OBSERVED` candidates.

## Recurrence and guardrail failure

Every lesson carries a `recurrenceKey`, a fingerprint of the failure class rather than of a single
occurrence. A repeat increments `recurrenceCount`. If the lesson was `GUARDED` when the repeat
happened, the repeat is recorded as a `GUARDRAIL_FAILURE`, severity is escalated, and the lesson
returns to `CONFIRMED`. A guardrail that let its failure through is itself a defect, and validation
refuses to leave such a lesson marked `GUARDED`.

## Preflight: how memory reaches the work

```text
lesson  ->  lesson preflight  ->  derived requirement  ->  evidence  ->  validation
```

Before a Gate begins, the Engineering Lead runs:

```text
python scripts/development-ledger/lesson_preflight.py --gate "GATE 0" --scope runtime --write
```

The preflight writes `LESSON-PREFLIGHT.json` and `LESSON-PREFLIGHT.md` into the checkpoint. For every
applicable lesson it records why it applies, the required check, the required evidence, and a derived
`LESSON-REQ-` identifier. Those identifiers must appear in that Gate's `REQUIREMENTS-MATRIX.json`;
the Delivery Completeness Validator fails the delivery when one is absent, so a lesson cannot be
quietly skipped.

A `3.1.0` checkpoint records the preflight in `STATE.json`, and validation checks that the recorded
counts match the artifact.

## Retrospectives

Every completed Gate produces a retrospective from
[.iacode/templates/retrospective/TEMPLATE.md](../.iacode/templates/retrospective/TEMPLATE.md), stored
in `.iacode/memory/retrospectives/`. It records what went well, what failed, what repeated, what was
learned, what should become a guardrail, and which lessons were created, updated or retired.

## Tools

| Command | Purpose |
|---|---|
| `python scripts/development-ledger/validate_lessons.py --render-index` | Validate the memory and regenerate `LESSONS.md`. |
| `python scripts/development-ledger/lesson_preflight.py --gate G --scope S --write` | Select applicable lessons and derive requirements. |
| `python scripts/development-ledger/extract_lessons.py --write` | Produce `OBSERVED` candidates from recorded delivery evidence. |

Lesson validation is part of the Green Keeper gate set, so a broken memory is a red delivery.

## Roles

The Engineering Lead runs the preflight, the Planner turns its output into plan items, the
Implementer consults the applicable checks, the Green Keeper records failures as lesson candidates,
the Delivery Completeness Validator confirms that lesson-derived requirements were satisfied, the
Historian records lessons and retrospectives, and the Reviewer looks for recurrence. The canonical
contracts are in [.iacode/agents/](../.iacode/agents/).
