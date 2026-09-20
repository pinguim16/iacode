# Next

## Required next action

Independent validation by Codex.

Expected flow:

```text
SETUP-00-CP-0003
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

Codex performs the review and the Red Team against this checkpoint, then records the outcome in a new
checkpoint. If it approves, that new checkpoint sets `secondToolValidation.status` to `PASSED` with
tool, provider, model exposure, and timestamp, and may close `SETUP-00` as `GATE_PASS`. If it does
not, it records `FAILED` with reproducible evidence and the Gate returns to `REWORK_REQUIRED`.

This checkpoint must not be modified or retagged, and neither may `SETUP-00-CP-0001` or
`SETUP-00-CP-0002`.

## Next Gate

`GATE 0 — FOUNDATION` remains blocked. It requires `SETUP-00` to be `GATE_PASS` and an explicit
authorization, and it was not started by this run.
