# Status

BLOCKED

## Why

The Agent Runtime is delivered and every deterministic control over it is green. Three requirements
cannot be satisfied in this session, and all three need the same thing: one live model call.

`docs/GATE-2-CHECKLIST.md` rows 19.1, 19.2 and 19.5 require a run executed live, through the Model
Gateway, against the configured provider. Every paid model in the DevWorld catalogue answers
`429 RATE_LIMITED` with a `retryAfterSeconds` of roughly 52,600 — about 14.6 hours — and the free
tier answers `503 PROVIDER_UNAVAILABLE` for all but one very slow model. `IACODE_GATEWAY_SMOKE_MODEL`
names the model and is never substituted, because `GATE-1-CP-0001` recorded that decision and both
smoke scripts enforce it.

The condition is the provider's, not this delivery's: `scripts/iacode/gateway_smoke.py`, which
belongs to the previous Gate and passed when that Gate closed, fails now in exactly the same way.

A Gate does not reach `INTERNAL_GATE_PASS` with an unsatisfied mandatory requirement, and a real
external blocker is recorded as `BLOCKED` rather than dressed as readiness. Nothing was weakened,
skipped or substituted to avoid this status.

## What is green

- 1,220 of 1,220 discovered test cases executed and passed, across the ledger suite, the three
  image suites and the live infrastructure suite.
- 11 of 11 mandatory gates.
- 22 of 22 internal Red Team attacks defended, with the null-mutation control valid.
- 22 of 25 verification stages, the three failures being the two live smokes and the checkpoint
  validation that only settles after the delivery commit.
- Durability, cancellation and the deadline, each proven against a real Temporal server with a real
  container restart.
- 179 of 182 requirements complete, with 100% of the evidence references resolving.

## What is not

- Requirement 19.1 — a single-agent run executed live.
- Requirement 19.2 — a planner-and-reviewer run executed live.
- Requirement 19.5 — the live evidence recording model provenance.
