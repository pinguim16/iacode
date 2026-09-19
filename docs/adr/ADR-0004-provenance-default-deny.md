# ADR-0004 — Provenance and training rights default to deny

Status: ACCEPTED
Date: 2026-09-19
Owners: IACode maintainers

## Context

Stored artifacts may have unclear ownership or provider restrictions.

## Decision

Require provenance and keep training and distillation disallowed until explicit evidence authorizes them.

## Evidence

- Storage does not prove training rights.
- External model output must not be treated as automatically trainable.

## Alternatives Considered

- Allow training unless prohibited.
- Track provenance only when exporting datasets.

## Consequences

Dataset eligibility requires affirmative rights review.

## Risks

Useful data remains ineligible until evidence is collected.

## Reversal Strategy

Change rights only per artifact with explicit evidence and policy review.

## Related Artifacts

`.iacode/policies/provenance-policy.md`, `.iacode/schemas/provenance.schema.json`.

