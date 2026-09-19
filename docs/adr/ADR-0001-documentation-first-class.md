# ADR-0001 — Documentation is a first-class artifact

Status: ACCEPTED
Date: 2026-09-19
Owners: IACode maintainers

## Context

Multiple tools must continue work without conversation memory.

## Decision

Versioned documentation and the Engineering Ledger are required implementation outputs.

## Evidence

- Tool sessions do not share guaranteed memory.
- Requirements, tests, and state must be independently reconstructible.

## Alternatives Considered

- Depend on chat transcripts.
- Maintain informal external notes.

## Consequences

Changes require documentation evidence; reviews include consistency checks.

## Risks

Documentation may drift unless validation and review enforce it.

## Reversal Strategy

Replace the ledger only with another versioned, validated, equally reconstructible system.

## Related Artifacts

`docs/DEVELOPMENT-CONTRACT.md`, `.iacode/policies/documentation-policy.md`.

