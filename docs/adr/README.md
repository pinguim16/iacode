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
| [ADR-0025](ADR-0025-sandbox-isolation-boundary.md) | Agent tools execute in disposable hardened containers, driven by one controller | Accepted |
| [ADR-0026](ADR-0026-workspace-lifecycle.md) | A workspace belongs to one run, lives in memory, and is recovered from the store | Accepted |
| [ADR-0027](ADR-0027-tool-execution-policy.md) | What a tool may do is canonical policy, and the agent can neither choose nor change it | Accepted |
| [ADR-0028](ADR-0028-sealed-evidence-is-judged-from-the-published-history.md) | Sealed evidence is judged from the published history | Accepted |
| [ADR-0029](ADR-0029-quality-execution-boundary.md) | Quality plans execute through stack-specific content-addressed sandboxes | Accepted |
| [ADR-0030](ADR-0030-quality-evidence-and-verdict-immutability.md) | Quality evidence and verdicts are immutable derived facts | Accepted |
| [ADR-0031](ADR-0031-project-profiles-select-closed-quality-runners.md) | Project profiles select closed policy-owned quality runners | Accepted |
| [ADR-0032](ADR-0032-quality-evidence-is-scanned-before-durable-commit.md) | Quality evidence is scanned before durable commit | Accepted |
| [ADR-0033](ADR-0033-verification-runtime-is-owned-by-one-checkout.md) | A verification runtime is owned by one checkout | Accepted |
| [ADR-0034](ADR-0034-command-inputs-must-cross-git-transport.md) | Command inputs must cross Git transport | Accepted |
| [ADR-0035](ADR-0035-review-bundles-bind-immutable-content.md) | Review bundles bind immutable content | Accepted |
| [ADR-0036](ADR-0036-pre-seal-validation-binds-an-explicit-subject.md) | Pre-seal validation binds an explicit subject | Accepted |
| [ADR-0037](ADR-0037-intermediate-gates-use-internal-closure.md) | Intermediate Gates use internal closure | Accepted |
| [ADR-0038](ADR-0038-cancellation-and-verdict-commit-are-serialized.md) | Cancellation and verdict commit are serialized | Accepted |
| [ADR-0039](ADR-0039-sandbox-output-is-scanned-before-durable-delivery.md) | Sandbox output is scanned before durable delivery | Accepted |
| [ADR-0040](ADR-0040-test-counts-follow-policy-bound-collection.md) | Test counts follow policy-bound collection | Accepted |
| [ADR-0041](ADR-0041-polling-cleanup-preserves-completed-checks.md) | Polling cleanup preserves completed checks | Accepted |
| [ADR-0042](ADR-0042-internal-verdict-semantics-follow-subject-policy.md) | Internal verdict semantics follow subject policy | Accepted |
| [ADR-0043](ADR-0043-collection-semantics-follow-subject-policy.md) | Collection semantics follow subject policy | Accepted |
| [ADR-0044](ADR-0044-process-recorders-bind-launch-inputs.md) | Process recorders bind launch inputs | Accepted |
| [ADR-0045](ADR-0045-live-program-state-is-generated-after-git-boundaries.md) | Live program state is generated after Git boundaries | Accepted |
| [ADR-0046](ADR-0046-desktop-clients-are-authenticated-runtime-adapters.md) | Desktop clients are authenticated runtime adapters | Accepted |
| [ADR-0047](ADR-0047-native-client-suites-and-packages-are-explicit.md) | Native client suites and packages are explicit | Accepted |
| [ADR-0048](ADR-0048-native-recovery-proofs-use-persistent-owned-hosts.md) | Native recovery proofs use persistent owned hosts | Accepted |
| [ADR-0049](ADR-0049-root-assurance-inputs-follow-subject-policy.md) | Root assurance inputs follow subject policy | Accepted |
| [ADR-0050](ADR-0050-experiences-are-source-bound-consented-facts.md) | Experiences are source-bound consented facts | Accepted |
| [ADR-0051](ADR-0051-retention-tombstones-prevent-experience-resurrection.md) | Retention tombstones prevent experience resurrection | Accepted |
