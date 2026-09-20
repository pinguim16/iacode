# Next

## Required next action

`CODEX FINAL M0 INDEPENDENT AUDIT`.

One independent audit of `SETUP-00-CP-0008`, covering the eleven `M0-F-0NN` findings of
`SETUP-00-CP-0007`, the twenty-six mandatory A-Z attacks, the additional attacks, and SETUP-00 as a
whole. `HANDOFF.md` carries the exact reproduction commands, one per control.

If the audit approves, it records its verdict in a new audit checkpoint and writes an external audit
attestation under `.iacode/attestations/`. Only that attestation can produce
`MILESTONE_EXTERNAL_PASS`; this checkpoint cannot, and does not claim to.

## Next Gate

`GATE 0 — FOUNDATION` remains `BLOCKED`. It requires the `M0` milestone audit to pass, explicit
authorization, and a new pre-Gate checkpoint whose first action is the lesson preflight. No Gate 0
work exists in this change set.
