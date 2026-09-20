# Next

## Required next action

Independent validation by Codex.

Expected flow:

```text
SETUP-00-CP-0005
        |
        v
Codex review
        |
        v
Codex Red Team
        |
        v
new review checkpoint
        |
        v
GATE_PASS or REWORK_REQUIRED
```

Codex reviews this checkpoint against the CP-0004 findings, the requirements matrix, and the new
delivery gates, then records the outcome in a new checkpoint. On approval that checkpoint sets
`secondToolValidation.status` to `PASSED` with tool, provider, model exposure, and timestamp, and may
close `SETUP-00` as `GATE_PASS`. Otherwise it records `FAILED` with reproducible evidence and the
Gate returns to `REWORK_REQUIRED`.

Do not modify or retag `SETUP-00-CP-0001`, `SETUP-00-CP-0002`, `SETUP-00-CP-0003`,
`SETUP-00-CP-0004`, or this checkpoint.

## Next Gate

`GATE 0 — FOUNDATION` remains blocked. It requires `SETUP-00` to be `GATE_PASS` and an explicit
authorization, and it was not started by this run.
