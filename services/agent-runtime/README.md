# Agent runtime

Delivered by `GATE 2 — AGENT RUNTIME`. A provider-neutral library: the run state machine, the event
log, the agent and team profiles, the turn protocol, context assembly, budgets, the tool-request
lifecycle and the engine that drives them.

It is a **library**, not a service. Two processes compose it: the API creates and reads runs, and
the Temporal worker in [`../orchestrator`](../orchestrator) executes them. The dependency points
inward — the runtime declares the persistence, model and clock ports it needs and imports neither
web framework nor workflow SDK — which is what lets both processes use it and what makes the
boundary assertable rather than aspirational.

## What it does not do

**It executes nothing.** An agent that asks for a tool gets its request persisted and the run
paused at `WAITING_FOR_TOOL`. There is no shell here, no filesystem mutation, no Git, no container
and no browser, and `ToolExecutionBoundaryTests` proves it over the whole boundary rather than over
one file. Execution is `GATE 3 — SANDBOX`.

**It never reaches a provider.** Every inference goes to the Model Gateway's published HTTP
contract. This package does not import `iacode_model_gateway` at all: it speaks the shared wire
shapes in `iacode_contracts.gateway`, so there is no provider adapter, no provider address and no
credential anywhere in it to misuse.

**It owns no resilience policy.** Retries, timeouts, the circuit breaker, the fallback chain and
provider selection are Gate 1 contracts with their own tests. A second implementation here would be
a second answer that can disagree with the first.

Operating it: [docs/runbooks/AGENT-RUNTIME.md](../../docs/runbooks/AGENT-RUNTIME.md). The decisions:
[ADR-0020](../../docs/adr/ADR-0020-agent-runtime-boundary.md),
[ADR-0021](../../docs/adr/ADR-0021-tool-execution-boundary.md),
[ADR-0022](../../docs/adr/ADR-0022-agent-output-envelope.md).
