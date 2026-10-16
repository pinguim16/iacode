# ADR-0043 — Collection semantics follow subject policy

Status: Accepted
Date: 2026-10-16
Owners: GATE 4 — Delivery assurance

## Context

ADR-0040 introduced collection-bound input repositories without changing test-suite policy 1.0.0.
Current tooling then rejected all nine sealed Gate 4 predecessors: their pytest fixtures were
excluded at execution, but their original counting contract had no collection-bound exclusions.
The complete verifier and an all-32-anchor component probe exposed the regression. Sealed counts,
files and tags must not be rewritten to make a new rule fit.

## Decision

Canonical test-suite policy 1.1.0 owns collection-bound count and evidence exclusions. The live
policy must declare it, and a mandatory regression refuses a downgrade. New exclusion fields are
not legal under 1.0.0. A historical subject declaring 1.0.0 retains its original source enumeration;
this preserves historical meaning, not a claim that its old count equals current runner collection.
Missing fixture versions do not select legacy semantics. Unknown declared versions fail closed.
No command argument selects a policy or narrows the canonical denominator.

The portable JSON Schema declares the version/field constraint, but the repository's
standard-library structural schema checker is not used as proof of combinator enforcement.
The canonical policy loader and source enumerator independently reject new fields under 1.0.0;
both refusal paths have executed behavioral controls. No generic schema-engine change reinterprets
historical schema keywords.

## Consequences

Current runner/registry equality, exclusion containment, positive collection and refusal controls
remain mandatory. Both historical immutability lessons record an escalated guardrail recurrence.
Component compatibility is diagnostic only: actual current-tool validation of every canonical
sealed subject and the complete verifier must still pass before internal closure.
