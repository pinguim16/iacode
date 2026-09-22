# Architecture Decision Records

The index of every structural decision the repository has recorded. Each record states its
context, the decision, its consequences and the alternatives it rejected; this page states only
which records exist, what each one is called and whether it is in force.

A new ADR adds its row here in the same commit. `AdrIndexTests` derives the expected rows from
the records themselves, so a record missing from the index, a row naming a record that does not
exist, or a title or status that disagrees with its record fails the suite.

| ADR | Title | Status |
|---|---|---|
| [ADR-0001](ADR-0001-documentation-first-class.md) | Documentation is a first-class artifact | Accepted |
| [ADR-0002](ADR-0002-checkpoint-protocol.md) | Use validated repository checkpoints | Accepted |
| [ADR-0003](ADR-0003-tool-neutral-agents.md) | Canonical tool-neutral agent definitions | Accepted |
| [ADR-0004](ADR-0004-provenance-default-deny.md) | Provenance and training rights default to deny | Accepted |
| [ADR-0005](ADR-0005-git-gate-workflow.md) | Gate-bound Git workflow | Accepted |
| [ADR-0006](ADR-0006-checkpoint-inventory-binding.md) | Bind the checkpoint file inventory to the repository | Accepted |
| [ADR-0007](ADR-0007-checkpoint-schema-2-and-independent-promotion.md) | Checkpoint schema 2.0.0, structured cross-tool validation, and independent promotion | Accepted |
| [ADR-0008](ADR-0008-delivery-assurance-gates.md) | Delivery assurance gates and checkpoint schema 3.0.0 | Accepted |
| [ADR-0009](ADR-0009-engineering-memory-and-milestone-validation.md) | Engineering memory, guardrails, and milestone validation cadence | Accepted |
| [ADR-0010](ADR-0010-milestone-closure-controls.md) | Milestone closure controls | Accepted |
| [ADR-0011](ADR-0011-audit-checkpoint-carries-the-verdict.md) | The audit checkpoint carries the milestone verdict | Accepted |
| [ADR-0012](ADR-0012-foundation-runtime-stack.md) | The Foundation runtime stack | Accepted |
| [ADR-0013](ADR-0013-pgvector-prepared-not-used.md) | pgvector is prepared, not used | Accepted |
| [ADR-0014](ADR-0014-one-postgresql-server-for-the-foundation.md) | One PostgreSQL server for the Foundation, two sets of databases | Accepted |
| [ADR-0015](ADR-0015-opentelemetry-deferred.md) | OpenTelemetry is deferred to the Gate that needs traces | Accepted |
| [ADR-0016](ADR-0016-model-gateway-boundary.md) | The Model Gateway is an in-process library with its dependencies pointing inward | Accepted |
| [ADR-0017](ADR-0017-capabilities-are-tri-state.md) | A capability is tri-state and carries its provenance | Accepted |
| [ADR-0018](ADR-0018-streaming-commitment-point.md) | A stream commits to one model at its first delivered event | Accepted |
| [ADR-0019](ADR-0019-credentials-are-named-not-stored.md) | Policy names the credential; only the environment holds it | Accepted |
| [ADR-0020](ADR-0020-agent-runtime-boundary.md) | The agent runtime is a library, Temporal is its durable engine, and the schema is shared | Accepted |
| [ADR-0021](ADR-0021-tool-execution-boundary.md) | A tool request is recorded and waited on; execution belongs to GATE 3 | Accepted |
| [ADR-0022](ADR-0022-agent-output-envelope.md) | An agent turn is one versioned envelope, parsed strictly, with exactly one repair | Accepted |
| [ADR-0023](ADR-0023-sealed-checkpoint-binds-its-own-tag.md) | A sealed checkpoint is bound to its own canonical tag | Accepted |
| [ADR-0024](ADR-0024-public-remote-and-atomic-commits.md) | A public remote, atomic commits and a push per advance | Accepted |
