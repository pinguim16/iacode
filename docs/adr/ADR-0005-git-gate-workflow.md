# ADR-0005 — Gate-bound Git workflow

Status: ACCEPTED
Date: 2026-09-19
Owners: IACode maintainers

## Context

History must show which evidence belongs to each Gate and protect recovery points.

## Decision

Do not mix Gates in commits; require prior-Gate PASS, explicit authorization, checkpoints around destructive actions, and non-destructive Git defaults.

## Evidence

- Gate isolation improves review and rollback.
- Destructive history operations can invalidate checkpoint evidence.

## Alternatives Considered

- Unstructured commits.
- One long-lived implementation commit across Gates.

## Consequences

Commits and handoffs are easier to audit; Gate transitions are deliberate.

## Risks

Process overhead may grow if checkpoints are not automated.

## Reversal Strategy

Adopt a replacement workflow only through an ADR and migration that preserves traceability.

## Related Artifacts

`docs/DEVELOPMENT-CONTRACT.md`, `docs/HANDOFF-PROTOCOL.md`.
