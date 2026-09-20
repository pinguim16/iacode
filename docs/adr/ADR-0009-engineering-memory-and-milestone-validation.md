# ADR-0009 — Engineering memory, guardrails, and milestone validation cadence

Status: ACCEPTED
Date: 2026-09-20
Owners: IACode maintainers

## Context

SETUP-00 corrected the same shape of defect three times. `SETUP-00-CP-0002` recorded a capability as
absent because one lookup mechanism failed. `SETUP-00-CP-0003` found five controls that the protocol
documents described and nothing enforced. `SETUP-00-CP-0004`, the first genuinely independent audit,
found two more of exactly that kind and returned `REWORK_REQUIRED`.

Two problems are visible in that history.

The first is that the project had no memory. Each correction was learned inside one run and survived
only as prose in a sealed checkpoint that nothing forced a later run to read. A documented rule that
nobody is required to consult is indistinguishable from no rule.

The second is cadence. Calling the external auditor after every Gate is expensive, and it was
producing findings the project could have caught itself. With the delivery-assurance gates of
`SETUP-00-CP-0005` in place, the internal controls are strong enough to carry a Gate, and the
external audit is better spent on a group of Gates where integration problems actually live.

## Decision

### An engineering memory that belongs to the project

`.iacode/memory/` holds lessons, patterns, anti-patterns, incidents, guardrails and retrospectives.
It is organizational knowledge, not the user's personal memory, and it holds no preferences, no
profile and no private reasoning. Every lesson cites evidence that exists in this repository, and
lessons are never invented.

### Memory is not enough: a lesson must become a guardrail

The stated order of preference is an automated control first, a preflight-enforced lesson second,
prose last. A lesson reaches `GUARDED` only when a control of kind `test`, `validator`, `lint`,
`policy`, `schema`, `invariant` or `automated-check` prevents recurrence, and `validate_lessons.py`
rejects a `GUARDED` lesson whose only prevention is documentation. Twelve of the fourteen initial
lessons are guarded by named tests and validator behaviour; the two that cannot be observed from this
repository stay `CONFIRMED` and are carried by the preflight instead.

### Recurrence is measured, and a guardrail failure is itself a defect

Each lesson carries a `recurrenceKey` fingerprinting the failure class. A repeat increments the
count; a repeat against a `GUARDED` lesson records a `GUARDRAIL_FAILURE`, escalates severity, and
returns the lesson to `CONFIRMED`. Validation refuses to leave such a lesson marked `GUARDED`,
because a control that let its failure through needs investigation rather than a counter.

### The preflight makes memory mandatory

Before a Gate starts, `lesson_preflight.py` selects the applicable lessons and derives a
`LESSON-REQ-` requirement from each. Those requirements enter the Gate's matrix, and the completeness
audit fails the delivery when one is absent. This is what turns memory from a document into a
control: a lesson cannot be ignored without failing a gate.

### External validation is per milestone, not per Gate

Gates are grouped into `M0` to `M6`. An intermediate Gate closes at `INTERNAL_GATE_PASS` on the
project's own controls. The Gate that closes a milestone produces a milestone checkpoint covering the
whole group, and the external tool audits that as the independent auditor. `MILESTONE_EXTERNAL_PASS`
is a separate status so an internal verdict can never be presented as an external one. An
extraordinary audit before the milestone is possible only through `externalAuditRequired` with a
reason naming a recorded trigger.

### Version dispatch again

All of this binds to `schemaVersion` `3.1.0`. `1.0.0`, `2.0.0` and `3.0.0` keep the rules they were
sealed under, and the regression suite validates clean clones detached at all five sealed tags.

## Alternatives Considered

- Keep lessons only in prose. Rejected: that is the failure mode being corrected.
- Let the extractor promote candidates automatically. Rejected: `GUARDED` requires a control that no
  tool can invent, and automatic promotion would manufacture false confidence.
- Keep per-Gate external validation. Rejected as expensive and misdirected once the internal gates
  exist; integration defects are visible across a milestone, not inside one Gate.
- Drop external validation entirely now that internal controls are strong. Rejected: every serious
  finding so far came from the independent run, and self-certification is already prohibited.
- Reuse `GATE_PASS` for internal approval. Rejected: the ambiguity between internal and external
  approval is exactly what the two new statuses remove.

## Consequences

A Gate costs a preflight and a retrospective. A failure now has a durable, machine-checked
consequence. The external auditor sees fewer, larger deliveries, and is asked about integration
rather than about red tests. The memory itself becomes an asset with rights metadata, denied for
training by default.

## Risks

A memory can grow into noise; the preflight's applicability filters and the `RETIRED` status exist to
bound it. A lesson can be marked guarded against a weak control; the control must be a named
reference, and a recurrence reopens the lesson. A milestone cadence can delay the discovery of a
systemic defect by up to four Gates; the extraordinary-audit trigger exists for the categories where
that delay is unacceptable. The two roles that run the internal gates are still emulated inside one
session, which is recorded rather than described as independence.

## Reversal Strategy

Issue a further schema version. Sealed checkpoints are never rewritten, so reversal never rewrites
history. Retiring the memory would mean retiring the guardrails that depend on it, which the tests
would immediately expose.

## Related Artifacts

`.iacode/memory/`, `.iacode/schemas/lesson.schema.json`,
`.iacode/schemas/lesson-preflight.schema.json`, `.iacode/templates/retrospective/TEMPLATE.md`,
`scripts/development-ledger/lessons.py`, `validate_lessons.py`, `lesson_preflight.py`,
`extract_lessons.py`, `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`,
`docs/CHECKPOINT-PROTOCOL.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`.
