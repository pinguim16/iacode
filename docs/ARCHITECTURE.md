# Architecture

## Current state

Two things exist: the **SETUP-00 development control plane** and the **Gate 0 Foundation runtime**.

No model gateway, agent runtime, sandbox, quality runtime, IDE integration, memory system, learning
engine or training pipeline has been implemented. The directories reserved for them contain a README
declaring the reservation and nothing else, and `.iacode/policies/gate-scope.json` records which
Gate owns each one. The internal mirror audit fails a delivery that puts an implementation there, so
this statement is a checked fact rather than a claim.

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

### Packages

| Package | What it owns | Why it is separate |
|---|---|---|
| `packages/common` | UUIDv7, redaction | needed by every process; depends on nothing but the standard library |
| `packages/contracts` | the response shapes | a promise to callers the producer does not control |
| `packages/telemetry` | the logging contract, the ambient context | one contract, every component |

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

Pinned versions: [VERSIONS.md](VERSIONS.md). Operating it: [runbooks/FOUNDATION.md](runbooks/FOUNDATION.md).

## Planned runtime boundaries

Later Gates establish, in order, a model gateway, an agent runtime, a sandbox, a quality engine and
VS Code integration. Later releases add experience, knowledge, code graph, project memory, gap
detection, research, skills, dataset production, model training, evaluation, shadow mode, promotion
and autonomous learning.

These are plans, not current capabilities. See [MASTER-PLAN.md](MASTER-PLAN.md) for prerequisites
and acceptance conditions.
