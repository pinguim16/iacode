# ADR-0002 — Use validated repository checkpoints

Status: ACCEPTED
Date: 2026-09-19
Owners: IACode maintainers

## Context

Tool switches and interruptions require a trustworthy continuation point.

## Decision

Use structured checkpoint directories, a textual `LATEST.md` pointer, schemas, and an executable validator.

## Evidence

- Windows-compatible textual pointers avoid symlink assumptions.
- Negative tests can prove corruption is detected.

## Alternatives Considered

- Chat-only handoff.
- A single mutable status document.

## Consequences

Each milestone and handoff has explicit evidence and validation overhead.

## Risks

Commit self-reference and self-hashing require documented symbolic semantics.

## Reversal Strategy

Migrate through a versioned schema and preserve old checkpoint readers during transition.

## Related Artifacts

`docs/CHECKPOINT-PROTOCOL.md`, `.iacode/schemas/checkpoint.schema.json`.

