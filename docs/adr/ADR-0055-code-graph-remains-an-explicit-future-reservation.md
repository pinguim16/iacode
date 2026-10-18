# ADR-0055 — Code Graph remains an explicit future reservation

Status: Accepted
Date: 2026-10-18
Owners: GATE 7 — scope boundary, not Gate 8 implementation

## Context

Gate 7 legitimately fills the Knowledge Engine reservation. The canonical next Gate is
Gate 8 — Code Graph, but its physical reservation is absent. The unchanged next-Gate scope
control fails in the complete runtime-v1 verification and causal cmd-0102.

## Decision

Declare `services/code-graph` in the canonical scope registry as owned by Gate 8. It carries
only a reservation README with the existing canonical marker. No Python project, parser,
schema, index, query, API, deployment, graph data or runtime integration is introduced.
The location is a logical component boundary; a future authorized ADR decides its deployment.
Gate 7 remains deterministic cited lexical retrieval, with no graph or project memory.

## Evidence

G7-INT-014, the original runtime-v1 report and cmd-0102 establish the missing reservation.
The unchanged scope assertion, current policy lifecycle controls and a real future-path
mutation must pass before the current guardrail is restored. This ADR predicts no test result.

## Alternatives Considered

- Remove the scope assertion or treat its current failure as approval: rejected.
- Start parsers/graph work early: outside authority and rejected.
- Reuse the completed Knowledge Engine reservation to imply graph delivery: misleading.

## Consequences

The next capability has an observable unimplemented boundary. The registry remains the source
of scope; current and historical ordering rules are unchanged. Gate 8 still requires explicit
owner authorization after mandatory independent M2 validation.

## Risks

A README is not implementation or acceptance. Future placement/deployment changes must be
visible policy/architecture changes, not silent relabelling of knowledge-index functionality.

## Reversal Strategy

An explicitly authorized future architectural change may relocate the reservation while
preserving scope tests and history. Never alter a sealed predecessor or imply Gate 8 approval.

## Related Artifacts

MASTER-PLAN.md; gate-scope.json; ADR-0053/0054; Gate7 G7-INT-014 and the M2 audit handoff.
