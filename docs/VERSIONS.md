# Pinned versions

Every version the Foundation runs on, in one place, so "what are we on?" has one answer.

Nothing here floats. There is no `latest`, no `stable` and no unpinned base image: two builds of the
same commit must produce the same stack, and a floating tag means they do not.
`infra/tests/test_compose_definition.py` enforces that on the compose file and on every Dockerfile,
so this document cannot drift into describing something the stack is not.

Nothing here is an alpha, a beta, a release candidate or a nightly.

## How to change a version

1. Edit the direct choice — `infra/compose/docker-compose.yml`, `apps/api/requirements.txt` or
   `apps/web/package.json`.
2. Regenerate the locks: `python scripts/iacode/lock_dependencies.py`.
3. Rebuild and verify: `python scripts/iacode/verify.py`.
4. Update this table.

## Runtimes

| Component | Version | Where it is pinned |
|---|---|---|
| Python (API, worker, tooling) | 3.13.15 | `apps/api/Dockerfile`, `services/orchestrator/Dockerfile` |
| Node (frontend toolchain only) | 22.23.2 | `apps/web/Dockerfile` |
| npm | 12.0.2 | `apps/web/Dockerfile` |
| Docker client (sandbox service only) | 29.6.1, SHA-256 `b0df4a43…b29f` of the static archive | `services/sandbox/Dockerfile` |
| Sandbox base image | `python:3.13.15-slim-bookworm` by digest `sha256:2325bb28…5e26` | `services/sandbox/images/iacode-dev/Dockerfile` |
| Git (sandbox image) | `1:2.39.5-0+deb12u3` | `services/sandbox/images/iacode-dev/Dockerfile` |

The sandbox image `iacode/sandbox-iacode-dev` is tagged with the first sixteen characters of the
SHA-256 of its inputs and labelled with the whole digest; `scripts/iacode/sandbox_image.py` builds
it, and the sandbox service refuses an image whose label names other inputs.

The frontend toolchain runs only inside its image. Nothing about the repository requires Node on the
developer's machine, which is deliberate: the environment this was built on has Node 18, and the
Angular toolchain needs 22.

## Local packages

Versioned together, because they are one repository and a version skew between them would be
a skew nobody could observe. Each is installed into the images that need it, from source,
with `--no-deps`, so the dependency lock stays authoritative.

| Package | Version | What it owns |
|---|---|---|
| `packages/common` | 0.1.0 | UUIDv7 and credential redaction |
| `packages/contracts` | 0.1.0 | the shapes that cross a process boundary, and the agent runtime vocabulary |
| `packages/persistence` | 0.1.0 | the declarative schema, shared by the API and the worker |
| `packages/telemetry` | 0.1.0 | the logging contract and the ambient correlation context |
| `services/model-gateway` | 0.1.0 | provider-neutral model invocation |
| `services/agent-runtime` | 0.1.0 | the agent runtime: lifecycle, protocol, budgets, tool boundary |
| `services/orchestrator` | 0.1.0 | the Temporal worker and the agent run workflow |
| `services/sandbox` | 0.1.0 | the sandbox: policy-isolated execution of agent tools |

## Services

| Service | Image | Version |
|---|---|---|
| PostgreSQL (with pgvector) | `pgvector/pgvector` | `0.8.6-pg17` — PostgreSQL 17, pgvector 0.8.6 |
| Redis | `redis` | `8.2.10-alpine` |
| MinIO | `quay.io/minio/minio` | `RELEASE.2025-09-07T16-13-09Z` |
| MinIO client | `quay.io/minio/mc` | `RELEASE.2025-08-13T08-35-41Z` |
| Temporal | `temporalio/auto-setup` | `1.29.7` |
| Temporal UI | `temporalio/ui` | `2.54.1` |
| Prometheus | `prom/prometheus` | `v3.5.5` (the 3.5 long-term-support line) |
| Grafana | `grafana/grafana` | `13.0.9` |
| nginx (serves the web shell) | `nginx` | `1.30.5-alpine-slim` (the stable line) |

MinIO is pulled from `quay.io` rather than Docker Hub because that is where MinIO publishes it.

## Backend libraries

Direct choices in `apps/api/requirements.txt`; the full resolved set, including every transitive
package, in `apps/api/requirements.lock.txt`. The images install the lock.

| Library | Version | What it is for |
|---|---|---|
| FastAPI | 0.141.1 | the API framework |
| Uvicorn | 0.53.0 | the ASGI server |
| Pydantic | 2.13.5 | contracts and validation |
| pydantic-settings | 2.15.0 | typed configuration |
| SQLAlchemy | 2.0.54 | the persistence layer |
| Alembic | 1.20.0 | migrations |
| asyncpg | 0.31.0 | the asynchronous PostgreSQL driver the application uses |
| psycopg | 3.3.6 | the synchronous driver Alembic uses; see `apps/api/migrations/env.py` |
| redis | 8.1.0 | the cache client |
| minio | 7.2.20 | the object-storage client |
| temporalio | 1.33.0 | the workflow SDK, in the API and in the worker |
| prometheus-client | 0.26.0 | the metrics instruments |
| httpx | 0.28.1 | the HTTP client the Model Gateway calls providers with, and the test client's transport |
| pytest | 9.1.1 | the backend test runner |
| pytest-asyncio | 1.4.0 | asynchronous test support |
| ruff | 0.16.8 | lint and static analysis |

`httpx` became a production dependency in Gate 1. It was already resolved into the lock as a
transitive dependency of the FastAPI test client; listing it directly is the difference between a
dependency we chose and one we inherited.

## First-party packages

Installed from the repository, versioned together, and pinned by exact version in every consumer.

| Package | Version | Consumed by |
|---|---|---|
| `iacode-common` | 0.1.0 | the API, the worker, the gateway |
| `iacode-contracts` | 0.1.0 | the API |
| `iacode-telemetry` | 0.1.0 | the API, the worker, the gateway |
| `iacode-model-gateway` | 0.1.0 | the API |

## Frontend libraries

Direct choices in `apps/web/package.json`, all exact; the resolved set in
`apps/web/package-lock.json`, which `npm ci` installs.

| Library | Version |
|---|---|
| Angular (`common`, `compiler`, `core`, `forms`, `platform-browser`, `router`) | 22.1.7 |
| Angular build and CLI | 22.1.8 |
| TypeScript | 6.0.3 |
| Vitest | 4.1.11 |
| jsdom | 28.1.0 |
| RxJS | 7.8.2 |
| Prettier | 3.9.8 |

TypeScript is 6.0.3, not the newest release: Angular 22 constrains the compiler version it supports,
and taking a newer one would mean running the framework outside the range it is tested against.

## What the developer's machine needs

| Requirement | Why |
|---|---|
| Docker with Compose v2 | every service and every build runs in a container |
| Python 3.12 or newer | the operational tooling and the development ledger |
| Git | the ledger records repository state |

Nothing else. No Node, no PostgreSQL client, no Python packages installed on the host: the
operational tooling is standard library only, and everything else happens inside an image.
