# ADR-0037 — Intermediate Gates use internal closure

Status: Accepted
Date: 2026-10-15
Owners: GATE 4 — Quality Engine

## Context

The milestone policy and ADR-0009 already group Gates 4 through 7 into M2 and distinguish
INTERNAL_GATE_PASS from independent milestone verdicts. Several older entry, handoff and Gate 4
clauses nevertheless require independent review before every successor. On 2026-10-15 the owner
explicitly requested self-review, correction and advancement to Gate 5, deferring independent audit.
CP0010/AUTHORIZATION.md records that authorization. CP0009 is already sealed and remains unchanged.

## Decision

The existing milestone cadence governs live delivery contracts. Every Gate executes lesson
preflight, requirement derivation, baseline, plan, implementation, tests, all mandatory Green Keeper
gates, total completeness, internal Red Team and the clean-clone closure mirror. A delivery offered
to an independent auditor closes READY_FOR_REVIEW. An intermediate Gate may instead close
INTERNAL_GATE_PASS after those same internal controls. This is not GATE_PASS and not an independent
verdict. The next Gate still requires explicit owner authorization and a sealed, validated prior
internal closure within the same milestone.

Independent review and independent Red Team are NOT_REQUIRED only for that intermediate checkpoint,
with a justification pointing to the pending milestone audit. secondToolValidation remains
PENDING_MANUAL and the milestone remains PENDING. A milestone boundary or an explicitly recorded
extraordinary audit cannot be crossed on an internal verdict. The separate independent audit and
attestation remain mandatory before the next milestone. Historical sealed checkpoints are judged
under their own committed contracts and never rewritten.

## Consequences

Gate 4 may be internally corrected and closed, then Gate 5 may begin in a separate checkpoint and
commit sequence. No mandatory executable gate, functional criterion, denominator or attack is
removed. The current session's controls must never be labelled independent. New findings still
return to implementation and trigger fresh assurance. M2's independent audit covers accumulated
integration and quality of Gates 4 through 7, not only its last Gate.

## Alternatives considered

Self-asserting GATE_PASS or a second-tool PASS was rejected because no independent audit occurred.
Editing or re-tagging CP0009 was rejected because sealed evidence is immutable. Keeping conflicting
live contracts was rejected because it makes authorized continuation ambiguous.

## Reversal

The owner can require extraordinary independent validation before another advance, recorded with
the policy's recognized trigger. Changing the cadence requires another visible policy decision;
an invocation or checkpoint assertion cannot change it.
