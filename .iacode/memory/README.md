# IACode Engineering Memory

This directory is the project's memory of what its own engineering has learned. It belongs to the
IACode engineering organization. It is **not** the user's personal memory, it holds no personal
preferences, and it is not a place to record anyone's private reasoning.

Its purpose is narrow and testable: stop the same class of failure from happening twice.

## The principle

**An important lesson must become a guardrail.** Writing something down is the weakest possible
control, because it depends on a future run remembering to read it. The order of preference is:

1. an automated control that makes the failure impossible or immediately visible;
2. a recorded lesson that a mandatory preflight forces the next Gate to answer;
3. prose.

A lesson is marked `GUARDED` only when at least one control of kind `test`, `validator`, `lint`,
`policy`, `schema`, `invariant`, or `automated-check` prevents recurrence. Documentation alone never
justifies `GUARDED`, and `validate_lessons.py` enforces that.

## Layout

| Path | Contents |
|---|---|
| `lessons.jsonl` | The authoritative machine-readable memory, one lesson per line. |
| `LESSONS.md` | Rendered index of `lessons.jsonl`. Regenerate it; never edit it by hand. |
| `patterns/` | Practices that repeatedly worked, with the evidence that they did. |
| `anti-patterns/` | Practices that repeatedly failed, with the evidence that they did. |
| `incidents/` | Narrative records of individual failures that deserve more than a lesson row. |
| `guardrails/` | How a lesson became an automated control, and what breaks if the control is removed. |
| `retrospectives/` | One retrospective per completed Gate. |

## Lifecycle

```text
OBSERVED -> CONFIRMED -> GUARDED
                     \-> SUPERSEDED / RETIRED
```

`OBSERVED` is a candidate: something failed and was recorded. `CONFIRMED` means the root cause is
understood and the resolution is real. `GUARDED` means an automated control now prevents it.
`SUPERSEDED` points at the lesson that replaced it. `RETIRED` no longer applies and produces no
requirement.

## Recurrence

Every lesson carries a `recurrenceKey`, a fingerprint of the failure class rather than of one
occurrence. When the same class happens again, `recurrenceCount` increases. If that happens while the
lesson was `GUARDED`, the repeat is recorded as a `GUARDRAIL_FAILURE`, the severity is escalated, and
the lesson returns to `CONFIRMED`, because a guardrail that let the failure through is itself a
defect that needs investigation.

## How the memory is used

```text
lesson  ->  lesson preflight  ->  derived requirement  ->  evidence  ->  validation
```

Before a Gate starts, `lesson_preflight.py` selects the lessons that constrain it and writes
`LESSON-PREFLIGHT.json` and `LESSON-PREFLIGHT.md` into the checkpoint. Each applicable lesson becomes
a `LESSON-REQ-` requirement in that Gate's `REQUIREMENTS-MATRIX.json`. The Delivery Completeness
Validator fails the delivery when a derived requirement is absent or unevidenced, so a lesson cannot
be quietly ignored.

## Tools

```text
python scripts/development-ledger/validate_lessons.py --render-index
python scripts/development-ledger/lesson_preflight.py --gate "GATE 0" --scope runtime --write
python scripts/development-ledger/extract_lessons.py --write
```

## Rules

- No secrets and no credentials; the validator scans every lesson field.
- No private chain-of-thought. Record symptom, root cause, resolution, prevention, and evidence.
- `trainingAllowed` is `false` by default and may only be true with a recorded rights justification.
- Every lesson cites evidence that exists in this repository.
- Lessons are never invented. A lesson describes something that actually happened here.

See [docs/ENGINEERING-MEMORY.md](../../docs/ENGINEERING-MEMORY.md) for the contract and
[docs/MILESTONE-VALIDATION.md](../../docs/MILESTONE-VALIDATION.md) for how memory feeds the audit
cadence.
