# ADR-0042 — Internal verdict semantics follow subject policy

Status: Accepted
Date: 2026-10-15
Owners: GATE 4 — Delivery assurance

## Context

The complete v1 verifier rejected three sealed historical checkpoints under the new internal-verdict
guard. Their declared memory policies used the Red Team field for an internal battery; applying
today's meaning retroactively invalidated immutable history. The history test correctly remained red.

## Decision

Memory policy 2.4.0 carries the strict distinction: INTERNAL_GATE_PASS cannot claim independent
review approval or an independent Red Team verdict. Earlier subject policies retain their own field
semantics. The live repository declares 2.4.0 and a mandatory regression refuses a downgrade; no
invocation selects policy. Unknown policy versions remain schema errors. The pre-existing refusal
of secondToolValidation PASSED on an internal verdict remains unconditional.

## Consequences

Historical seals are neither rewritten nor granted independence. Current internal and independent
verdicts remain separate. Positive legacy compatibility, negative current-policy claims, the live
policy invariant and actual historical-tag validation all have to pass before closure.
