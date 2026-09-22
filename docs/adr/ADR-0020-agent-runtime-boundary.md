# ADR-0020 — The agent runtime is a library, Temporal is its durable engine, and the schema is shared

Status: Accepted
Date: 2026-09-22
Owners: GATE 2 — Agent Runtime

## Context

`docs/GATE-2-CHECKLIST.md` rows 2.1, 2.2, 2.6, 13.1 and 13.2 require the runtime to be
provider-neutral, to declare its ports so the dependency points inward, to share one schema
definition with the worker, to use Temporal as its only durable engine, and to keep workflow code
deterministic. The decision behind all five is one decision, so it is recorded once.

Three questions had to be answered together.

**Where does the behaviour live?** A run is created by the API and executed by the Temporal worker.
Putting the loop in the worker would make it unreachable from a test that has no Temporal; putting
it in the API would make the API execute runs, which is exactly the coupling
[ADR-0012](ADR-0012-foundation-runtime-stack.md) separated the worker to avoid.

**Where does the schema live?** Both processes read `task_runs`, `agent_runs`, `run_events`,
`tool_requests` and `model_calls`. Gate 0 put the ORM inside `apps/api`, which was correct when
only the API read it. With a second reader the options were a second ORM in the worker, the worker
importing the web application, or a shared package.

**How does the runtime reach a model?** Gate 1 built one boundary for that, with its own retries,
circuit breaker and fallback chain. The runtime could compose that library in process — which means
composing a provider registry, a catalog store and a credential resolution path inside the worker —
or call the boundary's published HTTP contract.

## Decision

**A library in `services/agent-runtime/`, composed by both processes. The schema moves to
`packages/persistence`. Temporal is the durable engine and the workflow holds no logic. The runtime
reaches a model through the gateway's published contract and imports no gateway code.**

Concretely:

- `iacode_agent_runtime` is a Python package with its own `pyproject.toml`, installed into the API
  image and the worker image. It has no process, no port and no database of its own.
- It declares `AgentRunStore`, `ModelClient` and `Clock` as ports. The API supplies a SQL store; the
  worker supplies the same store and an HTTP model client; the suite supplies doubles.
- It depends on `iacode-common`, `iacode-contracts`, `iacode-persistence`, `iacode-telemetry`,
  `httpx`, `pydantic` and `prometheus-client`. It does **not** depend on `iacode-api`,
  `iacode-orchestrator`, `fastapi`, `temporalio` or `iacode-model-gateway`.
- `packages/persistence` owns the declarative base, the ORM and the engine helpers. The engine takes
  values rather than a settings object, so neither process has to import the other's configuration
  model. `apps/api/migrations` still owns Alembic, because a migration directory belongs to one
  deployable unit.
- `AgentRunWorkflow` in `services/orchestrator` drives the runtime's engine, supplying its effects
  as activities. The workflow contains activity invocations, signal handlers, queries and
  arithmetic over the frozen plan — and nothing else.
- Every inference is one `POST /api/v1/gateway/infer`. The runtime speaks the wire shapes in
  `iacode_contracts.gateway` and never imports `iacode_model_gateway`.

## Consequences

**The turn loop is testable without Temporal, a provider or a database.** The runtime's own suite
exercises stages, budgets, the repair, the tool pause, cancellation and isolation against doubles,
in an image that has no workflow engine. What passes there is what runs in the workflow, because the
workflow adds no logic of its own.

**Workflow determinism is structural rather than careful.** There is nothing in the workflow to make
non-deterministic: the clock, the randomness, the identifiers and every write are effects. A
control-plane scan asserts it and carries a null control — a module that reads a clock, which the
same scan detects.

**One schema, two readers, no drift.** A column added to `packages/persistence` is visible to both
processes at once, and a control-plane test refuses a `__tablename__` declared anywhere else in the
tree.

**"The runtime never reaches a provider" became a property of the dependency graph.** There is no
provider adapter one import away, no credential to resolve and no address to hold, so the claim is
checked by reading imports rather than by reviewing intent.

**The cost is a network hop per turn.** The worker calls the API rather than a library in its own
process. It buys the boundary: the gateway's retries, circuit breaker and fallback chain are applied
once, in one place, with one set of tests, and a failure arrives already classified. A call that
cannot reach the gateway is a classified `GATEWAY_ERROR` rather than a stack trace, and the activity
that made it is retried by Temporal like any other.

**The API now depends on `iacode-agent-runtime`.** It composes the registry and the service to
create and read runs. It does not execute one: nothing in the request-serving process runs a turn.

**Reversal path.** Composing the gateway in process inside the worker would remove the hop. It would
require the worker to carry the provider policy, the catalog store and the credential resolution,
and it would put a provider adapter one import away from the runtime — so it is a decision to
revisit only if the hop becomes a measured problem, and it is recorded here as available rather than
as planned.

## Alternatives considered

**The loop inside the workflow.** Rejected: workflow code cannot be exercised without Temporal, and
a loop written there is a loop no fast test covers. The determinism requirement would also have
turned every helper into a place where a clock read could hide.

**A second ORM in the worker.** Rejected outright. `.iacode/memory/lessons.jsonl` records the class:
one classification written twice grows a value in one copy that the other does not have, and the
disagreement surfaces as a constraint violation rather than as a failing test.

**The worker importing `iacode_api`.** Rejected: the dependency points the wrong way, and the
worker would inherit a web framework to read four tables.

**Composing the gateway in process in the worker.** Rejected for this Gate. It is the reversal path
above, and it trades a provable boundary for a network hop nobody has measured.
