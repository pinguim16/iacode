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

## Memory policy 2.0.0

`.iacode/memory/POLICY.json` declares which rules the memory is read under. Under `2.0.0`:

- every preventive control reference is resolved: a `test` must exist in the discovered suite, an
  `invariant` must be defined in the tooling, and a path-shaped control must exist in the repository;
- every evidence reference must resolve to an existing, non-empty repository file;
- every lesson's provenance must resolve: the checkpoint it cites must exist, and every finding
  identifier it names must appear in the recorded evidence of a checkpoint it names;
- the whole lesson object is scanned for secrets at any depth, not a fixed list of fields;
- a `GUARDED` lesson must name at least one guardrail in `.iacode/memory/guardrails/registry.json`,
  and the registry entry must name the lesson back and list the tests that fail when the control is
  removed.

A memory without `POLICY.json` is read under the original `1.0.0` rules, which is how sealed
checkpoints keep validating under their own version.

`POLICY.json` is itself validated against `.iacode/schemas/memory-policy.schema.json`, which is
closed: a key the implementation does not read cannot be declared there. The guardrail registry lives
at the fixed path `.iacode/memory/guardrails/registry.json`, resolved by
`lessons.guardrail_registry_path` and by nothing else. The policy used to advertise a relocatable
registry path that no code consulted, so re-pointing it changed nothing while promising that it
would; a configuration key with no consumer is a defect, not documentation.

A lesson's prose records the residual limit of its control and never restates its status: validation
refuses a `GUARDED` lesson whose notes say it is not guarded.

## The guardrail registry

A guardrail records what the control is, where it lives, which lessons it guards, which tests verify
it, and what removing it would allow. `guardrail_effectiveness` measures rather than assumes:

- `guardrailsTotal`, `guardrailsResolved`, `guardrailsTested`, `guardrailsEffective`, and
  `guardrailFailures`.

A delivery cannot be offered while a guardrail is unresolved, untested, or carries an unresolved
`GUARDRAIL_FAILURE`. A guardrail failure is resolved by naming the checkpoint that repaired the
control, which is the only way a reopened lesson returns to `GUARDED`.

## Preflight freshness

The preflight assumes an implementing delivery. Some derived requirements — an empty `blockedBy`
at a readiness status, for instance — do not describe a run that audits rather than implements, and
an audit checkpoint legitimately records blockers. Until the preflight takes a delivery role, an
audit run records which derived requirements describe it and which describe an implementing delivery,
and lessons that constrain audits only are scoped to the `independent-audit` scope.

A preflight records `inputsFingerprint`, a digest of the canonical memory, the guardrail registry,
the lesson schema, the selection policy version and the Gate inputs. Validation recomputes the
fingerprint and reproduces the selection. A preflight generated for another Gate is refused outright.
Freshness is a computation, never a timestamp.
