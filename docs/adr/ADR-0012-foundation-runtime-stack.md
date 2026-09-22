# ADR-0012 — The Foundation runtime stack

Status: Accepted
Date: 2026-09-21
Owners: GATE 0 — Foundation

## Context

`docs/MASTER-PLAN.md` names Gate 0's deliverable as "chosen stack, build, package layout,
configuration contract, CI baseline, tests". The stack was named in the Gate 0 authorization —
Python and FastAPI, Angular, PostgreSQL, Redis, MinIO, Temporal, Prometheus and Grafana, on Docker
Compose — with the instruction not to change it without a real need.

This ADR records that the stack was adopted as named, and the choices *inside* it that the
instruction left open: which component plays which role, and where the boundaries between them are.
Those are the decisions a later Gate will be constrained by, and the ones a reader will otherwise
have to reconstruct from the compose file.

One boundary shaped everything else: Gate 0 builds a **foundation**, not a small version of the
product. Every component is present because a later Gate needs it to exist, and none of them has
behaviour beyond proving it works.

## Decision

**FastAPI serves the API.** It is the Python framework with first-class async support, a request
contract that is the same object as the validation (`pydantic`), and OpenAPI from the same
declaration. The API is asynchronous throughout, because every one of its dependencies is
I/O-bound.

**PostgreSQL is the system of record**, through SQLAlchemy 2 with `asyncpg`, with Alembic for
migrations. The schema is created by migrations from the first commit, never by
`metadata.create_all`: a project that starts without migrations acquires them after its first
production schema change, which is the worst possible moment.

**Redis is a cache, and nothing else yet.** No queue, no rate limiter, no cache-aside helper: the
shape of those is decided by the component that needs them, and an abstraction invented now would
be worked around rather than used. It has no volume, because a cache that survives a restart hides
the cold-start behaviour the application has to handle anyway.

**MinIO is object storage**, with one bucket created by an idempotent bootstrap. The Artifact
Service is Gate 6's; this Gate proves the bytes survive a write, a read and a delete.

**Temporal provides durable execution**, with the worker as a **separate process** in
`services/orchestrator`. A worker inside the API would tie workflow execution to the
request-serving process's lifetime: restarting the API to deploy a route change would interrupt
running workflows, and a worker busy with activities would compete with request handling for the
same event loop. One smoke workflow exists, and it stays as small as it is.

**Angular is the web shell**, built and served as static files behind nginx. The backend address is
**not** compiled into the bundle; `config.json` is written from the container's environment at
start-up, so one image runs against any backend.

**Prometheus and Grafana are provisioned from files.** A datasource an operator has to add by hand
is a step that gets skipped, and a dashboard edited in a browser is lost on the next restart with
no trace of what it was.

**Docker Compose is the local runtime**, with health conditions rather than sleeps for start-up
ordering, named volumes for durable state, and every published port bound to `127.0.0.1` and taken
from configuration.

## Evidence

- The stack runs: `python scripts/iacode/smoke.py` reports 18 of 18 checks, including a real
  Temporal workflow executed by the worker.
- It installs from nothing: `scripts/iacode/scenarios/fresh_install.py` deletes every volume and
  reaches a healthy, migrated, smoke-clean stack.
- The declarations are checked rather than described: `infra/tests/test_compose_definition.py`.
- The versions are pinned and recorded: `docs/VERSIONS.md`.

## Alternatives Considered

**Celery or RQ instead of Temporal.** Both are task queues; neither is durable execution. Gate 2's
agent runtime needs workflows that survive a process restart and can be inspected after the fact,
which is the property Temporal has and a queue does not. The cost is a heavier local stack, paid
once here rather than as a migration in Gate 2.

**SQLite for local development.** It would remove a container, and it would mean the Gate 0
foundation did not exercise the database the product uses. `JSONB`, `pgvector` and the constraint
behaviour the schema depends on are all PostgreSQL. Local-first does not mean different-locally.

**Running the frontend on the host.** Rejected because the toolchain needs Node 22 and the primary
development environment has Node 18. Building in a container makes the frontend reproducible and
removes Node from the list of things a contributor must install.

**Creating the schema with `metadata.create_all` and adding Alembic later.** Faster today, and it
guarantees that the first real schema change happens without a migration path.

## Consequences

- Docker is a hard requirement of this repository. It is not optional tooling: every service, every
  build and every gate runs in a container. `docs/VERSIONS.md` states it.
- The local stack is nine long-running containers. That is the cost of exercising the real
  components rather than substitutes.
- Later Gates inherit these boundaries. Gate 1 adds a provider behind the model gateway; it does
  not get to choose a different database.
- The persistence contract exists before the behaviour that uses it, so Gate 1 and Gate 2 add rows
  rather than tables.

## Risks

- **The stack is heavy for a laptop.** Mitigated by binding everything to loopback, keeping the
  images small and making `verify.py --fast` skip the stages that restart the stack.
- **Temporal is a large dependency for one smoke workflow.** Accepted deliberately: the alternative
  is discovering in Gate 2 that the queue chosen here cannot do durable execution.
- **Nine containers is a lot of version surface.** Mitigated by pinning every one, recording them
  in `docs/VERSIONS.md`, and testing that nothing floats.

## Reversal Strategy

Each component is reachable through one module — `db/engine.py`, `cache/client.py`,
`storage/client.py`, `workflows/client.py` — and nothing else in the application talks to it
directly. Replacing one means rewriting that module and its readiness probe. The schema is the
expensive part to reverse, which is why the database choice is the one most worth being sure about.

## Related Artifacts

- `docs/GATE-0-CHECKLIST.md`
- `docs/VERSIONS.md`
- `infra/compose/docker-compose.yml`
- [ADR-0013](ADR-0013-pgvector-prepared-not-used.md)
- [ADR-0014](ADR-0014-one-postgresql-server-for-the-foundation.md)
