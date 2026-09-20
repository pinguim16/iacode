# Patterns

Practices that repeatedly worked, each with the evidence that they did.

A pattern is added only after it has survived at least two deliveries, and it names the checkpoints
that demonstrate it. A pattern is not an aspiration.

## version-dispatched-control-evolution

Control-plane rules evolve while sealed history does not. Binding new rules to a new `schemaVersion`
and dispatching validation on the declared version let `SETUP-00-CP-0003`, `CP-0005` and `CP-0006`
tighten controls three times without invalidating a single sealed checkpoint.

Evidence: `docs/adr/ADR-0007-checkpoint-schema-2-and-independent-promotion.md`,
`docs/adr/ADR-0008-delivery-assurance-gates.md`, `HistoricalCheckpointCompatibilityTests`.

## recompute-instead-of-trust

Every control that was expressed as a stored claim was eventually found to be wrong. Every control
that recomputes the claim from the repository held. The file inventory, the completeness audit and
the gate consistency checks all recompute.

Evidence: `docs/checkpoints/SETUP-00-CP-0004/REVIEW-REPORT.md`, `DeltaInventoryTests`,
`DeliveryAssuranceGateTests`.

## count-independent-records

A record that enumerates its own corrections needs another correction to stay accurate. Stating the
mechanism instead of the instances reaches a fixed point.

Evidence: `docs/checkpoints/SETUP-00-CP-0003/DECISIONS.md`,
`docs/checkpoints/SETUP-00-CP-0005/DECISIONS.md`.
