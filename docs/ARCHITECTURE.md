# Architecture

## Current state

Three things exist: the **SETUP-00 development control plane**, the **Gate 0 Foundation
runtime** and the **Gate 1 Model Gateway**.

No agent runtime, sandbox, quality runtime, IDE integration, memory system, learning engine or
training pipeline has been implemented. The directories reserved for them contain a README declaring
the reservation and nothing else, and `.iacode/policies/gate-scope.json` records which Gate owns
each one. The internal mirror audit fails a delivery that puts an implementation there, so this
statement is a checked fact rather than a claim.

## Control plane

The repository is the source of truth:

```text
canonical contracts (.iacode/)
            |
            +-- Codex adapter (AGENTS.md)
            +-- Claude Code adapters (CLAUDE.md, .claude/agents/)
            +-- future verified adapters
            |
            +-- Engineering Ledger (docs/checkpoints/)
            +-- validation tools (scripts/development-ledger/)
```

Canonical agent definitions are independent of any provider. Tool adapters may express supported
integration mechanisms but may not alter semantics. Checkpoints contain observable state, evidence,
provenance and continuation instructions.

## Foundation runtime

Delivered by `GATE 0 — FOUNDATION`, and running locally from `infra/compose/docker-compose.yml`.

```text
                       browser
                          |
                    ┌─────┴─────┐
                    │  web      │  Angular, built to static files, served by nginx
                    └─────┬─────┘  the backend address is read at start-up, never compiled in
                          | HTTP
                    ┌─────┴─────┐
                    │  api      │  FastAPI: /health /ready /version /metrics
                    └──┬──┬──┬──┘
           ┌───────────┘  │  └───────────┬──────────────┐
           |              |              |              |
     ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴──────┐
     │ postgres  │  │  redis    │  │  minio    │  │  temporal  │
     │ system of │  │  cache    │  │  objects  │  │  durable   │
     │ record    │  │           │  │           │  │  execution │
     └─────┬─────┘  └───────────┘  └───────────┘  └─────┬──────┘
           |  temporal's own databases live here         | task queue
           |                                       ┌─────┴──────┐
           |                                       │  worker    │  services/orchestrator
           |                                       └────────────┘
     ┌─────┴───────────────────────────────────────────────────┐
     │  prometheus  ──scrapes──>  api /metrics, worker :9100   │
     │  grafana     ──queries──>  prometheus                    │
     └──────────────────────────────────────────────────────────┘
```

### Boundaries that matter

**Liveness is not readiness.** `/health` answers "is this process alive" and contacts nothing, so a
dependency outage never makes a healthy process look dead. `/ready` answers "can it accept work",
probes every mandatory dependency for real, and returns 503 naming the one that failed. Collapsing
the two produces a restart loop the first time a database is slow.

**The worker is a separate process.** Workflow execution is not tied to the request-serving
process's lifetime, so restarting the API to deploy a route change does not interrupt running
workflows.

**The frontend is served independently of the API.** The page renders whether or not the backend is
reachable, and reports that state. A shell that fails to load when the API is down cannot tell
anyone the API is down.

**Configuration is typed and validated at start-up.** A process refuses to start with an invalid
database URL rather than discovering it on the first request.

**Credentials are redacted at the boundary.** `packages/common` redacts by key, by connection-string
shape and by text, and every log record passes through it. The call sites are supposed to keep
credentials out of log arguments; one day one of them will not.

**The model gateway is a boundary, not a service.** `services/model-gateway/` is a library the API
composes in process. It declares the storage it needs as ports and the application implements them,
so the dependency points inward and a second consumer can use the gateway without inheriting a web
application — [ADR-0016](adr/ADR-0016-model-gateway-boundary.md).

**Nothing above the gateway names a provider.** A caller asks for `provider:model` or a route alias
and receives a normalised answer. Provider-specific shapes exist only inside the three protocol
adapters, and a static scan fails the build if a provider name appears in a provider-neutral module.

**A provider credential exists only in the environment.** The versioned policy names the variable;
the value lives in `infra/compose/.env`, which Git ignores, and never leaves the API process — in
particular it never reaches the browser
— [ADR-0019](adr/ADR-0019-credentials-are-named-not-stored.md).

**The gateway stores what a call cost, never what it said.** `model_calls` has no column that can
hold a prompt, a completion or a credential, and the schema is the control rather than the
discipline of the code above it.

### Packages

| Package | What it owns | Why it is separate |
|---|---|---|
| `packages/common` | UUIDv7, redaction | needed by every process; depends on nothing but the standard library |
| `packages/contracts` | the response shapes | a promise to callers the producer does not control |
| `packages/telemetry` | the logging contract, the ambient context | one contract, every component |
| `services/model-gateway` | provider-neutral model invocation | a boundary with its own contracts; it depends on no application |

### Persistence

PostgreSQL is the system of record. The schema is created only by Alembic migrations, from the first
commit. Identifiers are UUIDv7 everywhere — globally unique and ordered by creation time, which is
what keeps index inserts from scattering across the B-tree.

The tables are a **persistence contract**, not a feature: `projects`, `repositories`, `tasks`,
`task_runs`, `agents`, `agent_runs`, `providers`, `models`, `model_calls`, `tool_calls`,
`artifacts`, `experiences`. Later Gates add rows and behaviour; none of them has to add a table to
start. Rights default to denial, so an experience cannot become training data by omission.

Entities with a lifecycle carry `created_at`, `updated_at`, `version` and `metadata`. Append-only
facts — `model_calls`, `tool_calls` — carry only `created_at`, because an `updated_at` on something
that cannot change invites code to update it.

### Observability

Structured JSON logs carrying `timestamp`, `level`, `service`, `message` and whichever of
`traceId`, `correlationId`, `requestId`, `taskId`, `runId` and `agentId` the context actually holds.
**A field with no value is absent**, never null: Gate 0 has no tasks, runs or agents, and a field
that is always null teaches readers to ignore it before it ever means anything.

Prometheus scrapes the API's request, latency and dependency instruments and the worker's Temporal
SDK instruments. Grafana starts with the datasource and the Foundation dashboard provisioned from
files. Distributed tracing is deferred to the Gate that has something to trace —
[ADR-0015](adr/ADR-0015-opentelemetry-deferred.md).

### Decisions

| Decision | ADR |
|---|---|
| The runtime stack and its boundaries | [ADR-0012](adr/ADR-0012-foundation-runtime-stack.md) |
| pgvector prepared, not used | [ADR-0013](adr/ADR-0013-pgvector-prepared-not-used.md) |
| One PostgreSQL server, separate databases for Temporal | [ADR-0014](adr/ADR-0014-one-postgresql-server-for-the-foundation.md) |
| OpenTelemetry deferred | [ADR-0015](adr/ADR-0015-opentelemetry-deferred.md) |
| The model gateway is an in-process library with dependencies pointing inward | [ADR-0016](adr/ADR-0016-model-gateway-boundary.md) |
| A capability is tri-state and carries its provenance | [ADR-0017](adr/ADR-0017-capabilities-are-tri-state.md) |
| A stream commits to one model at its first delivered event | [ADR-0018](adr/ADR-0018-streaming-commitment-point.md) |
| Policy names the credential; only the environment holds it | [ADR-0019](adr/ADR-0019-credentials-are-named-not-stored.md) |

Pinned versions: [VERSIONS.md](VERSIONS.md). Operating it: [runbooks/FOUNDATION.md](runbooks/FOUNDATION.md)
and [runbooks/MODEL-GATEWAY.md](runbooks/MODEL-GATEWAY.md).

## The model gateway

One boundary for reaching a model. Providers are declared in `.iacode/policies/providers.json`;
models are **discovered** from each provider's own API rather than maintained by hand; capabilities
are recorded as `SUPPORTED`, `UNSUPPORTED` or `UNKNOWN` with the provenance of the statement, and
the router refuses an unknown capability instead of guessing
— [ADR-0017](adr/ADR-0017-capabilities-are-tri-state.md).

A request resolves to an ordered candidate list, filtered on what the catalog says. Failures carry a
class that decides whether they may be retried and whether they may fall back; a rate limit may, an
invalid request may not. Retry uses full-jitter backoff on an injected clock, and the circuit
breaker is scoped both to a provider and to a provider-and-model pair.

Streaming commits to one model at its first delivered event: before it, retry and fallback behave as
they do for any call; after it, a failure becomes an `error` event, because the alternative is one
stream carrying two models' text — [ADR-0018](adr/ADR-0018-streaming-commitment-point.md).

What it deliberately is not: an agent runtime, a tool executor, a conversation store or a retrieval
system. It normalises a tool call; it never executes one. It records that a call happened; it never
records what the call said.

## Planned runtime boundaries

Later Gates establish, in order, an agent runtime, a sandbox, a quality engine and
VS Code integration. Later releases add experience, knowledge, code graph, project memory, gap
detection, research, skills, dataset production, model training, evaluation, shadow mode, promotion
and autonomous learning.

These are plans, not current capabilities. See [MASTER-PLAN.md](MASTER-PLAN.md) for prerequisites
and acceptance conditions.
