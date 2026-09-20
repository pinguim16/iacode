# Next

## Required next action

`CODEX M0 INDEPENDENT AUDIT` — a single milestone audit, not two separate reviews.

Scope of the audit:

```text
SETUP-00-CP-0005  +  SETUP-00-CP-0006  +  SETUP-00 as a whole
                          |
                          v
                 Codex milestone review
                          |
                          v
                   Codex Red Team
                          |
                          v
              new milestone checkpoint (M0)
                          |
                          v
        MILESTONE_EXTERNAL_PASS or REWORK_REQUIRED
```

`SETUP-00-CP-0005` corrected the CP-0004 findings and added the delivery-assurance gates.
`SETUP-00-CP-0006` adds the engineering memory, the mandatory lesson preflight, and the milestone
validation policy. Both are internal deliveries and neither has been externally validated. Auditing
them together as milestone `M0` avoids an unnecessary external cycle and matches the cadence this
checkpoint establishes.

Codex evaluates `M0` as a whole: accumulated requirement completeness across both checkpoints,
integration between the delivery gates and the memory controls, architecture, regressions, quality
evidence, documentation, the lessons and guardrails, the Red Team position, and any inconsistency
that per-checkpoint validation could not see.

The verdict is recorded in a new milestone checkpoint that sets `secondToolValidation` and
`milestone.status`. Do not modify or retag `SETUP-00-CP-0001` through `SETUP-00-CP-0006`.

## Next Gate

`GATE 0 — FOUNDATION` remains blocked. It requires the `M0` milestone audit to pass, plus explicit
authorization and a new pre-Gate checkpoint whose first action is the lesson preflight. No Gate 0
work exists in this change set.
