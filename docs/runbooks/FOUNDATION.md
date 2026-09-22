# Runbook — the Foundation stack

Everything an operator does to the Gate 0 stack, and what to check when something is wrong.

The commands are the same on Windows and on POSIX. They are Python driving Docker, not shell
scripts, because Windows is the primary development environment here.

## Before anything

| Requirement | Check |
|---|---|
| Docker with Compose v2 | `docker compose version` |
| Python 3.12+ | `python --version` |
| Git | `git --version` |

Nothing else has to be installed. Everything the Foundation runs happens inside a container.

## First run on a new machine

```bash
python scripts/iacode/bootstrap_env.py
python scripts/iacode/stack.py up --build
python scripts/iacode/smoke.py
```

`bootstrap_env.py` derives `infra/compose/.env` from the committed example and generates the local
credentials. That file is ignored by Git and is the only place a real credential lives; the
generated values are never printed, only their names.

`stack.py up` builds what is missing, starts everything and **waits for real health** rather than
returning as soon as Compose has launched the containers. The first run pulls images and builds
three of them, so expect several minutes; afterwards it is well under a minute.

`smoke.py` proves the stack works, which is a different question from whether it started. It checks
the API, the web shell, every dependency, both Prometheus targets, Grafana, and executes a real
Temporal workflow through the worker.

## Where everything is

Ports come from `infra/compose/.env` and every one is configurable, because more than one stack
routinely runs on a development machine. The defaults:

| Service | Address | Notes |
|---|---|---|
| API | <http://localhost:18080> | `/health`, `/ready`, `/version`, `/metrics`, `/docs` |
| Web shell | <http://localhost:18081> | the Foundation status page |
| Grafana | <http://localhost:13000> | user `admin`; the password is `IACODE_GRAFANA_PASSWORD` in `.env` |
| Prometheus | <http://localhost:19090> | `/targets` shows the scrape state |
| Temporal UI | <http://localhost:18233> | workflow history |
| MinIO console | <http://localhost:19001> | user and password are the `IACODE_MINIO_ROOT_*` values |
| PostgreSQL | `localhost:15432` | database `iacode` |
| Redis | `localhost:16379` | |

Every one binds to `127.0.0.1` only. A development stack on `0.0.0.0` is an unauthenticated
database on whatever network the machine is attached to.

## Daily operations

| What | Command |
|---|---|
| Start | `python scripts/iacode/stack.py up` |
| Start, rebuilding the images | `python scripts/iacode/stack.py up --build` |
| Stop, keeping the data | `python scripts/iacode/stack.py down` |
| Restart | `python scripts/iacode/stack.py restart` |
| What is running | `python scripts/iacode/stack.py status` |
| Reset — **deletes every volume** | `python scripts/iacode/stack.py reset --yes` |
| Logs for one service | `docker compose --project-directory infra/compose --env-file infra/compose/.env logs -f api` |

`reset` destroys the database and the object storage. It requires `--yes` for that reason.

## Checking health

```bash
curl http://localhost:18080/health
curl -i http://localhost:18080/ready
curl http://localhost:18080/version
```

The two are not the same question:

**`/health`** is about the process. It contacts nothing, so it stays `UP` while PostgreSQL is
restarting. A liveness probe that failed when a dependency failed would ask the orchestrator to
restart a perfectly healthy process, turning a recoverable outage into a restart loop.

**`/ready`** is about the work. It probes PostgreSQL, Redis, MinIO and Temporal for real, and
answers **503** with `NOT_READY` when any of them is unavailable. The payload names the dependency
and says why its probe failed, so "not ready" is never a guessing game.

`/version` reports the running version, the commit the image was built from and the configuration
profile. It carries no configuration value and no credential.

## Migrations

The stack migrates on every start: the `migrate` job runs to completion, and the API is not allowed
to start until it has succeeded. A failed migration therefore stops the API from starting rather
than letting it serve requests against a schema that is not there.

| What | Command |
|---|---|
| Apply what is outstanding | `python scripts/iacode/migrate.py upgrade` |
| What the database is at | `python scripts/iacode/migrate.py current` |
| What exists to apply | `python scripts/iacode/migrate.py history` |
| Does the model match the schema? | `python scripts/iacode/migrate.py check` |

`check` is the one worth running after changing a model: it compares the declared model with the
migrated schema and fails when a migration is missing. Without it, the change works in development
against an old database and fails on the first fresh installation.

To add a migration, change `apps/api/src/iacode_api/db/models.py`, then:

```bash
docker compose --project-directory infra/compose --env-file infra/compose/.env run --rm --no-deps --entrypoint "" --user root -v "$PWD/apps/api/migrations/versions:/app/migrations/versions" migrate alembic revision --autogenerate -m "what changed"
```

Review what it generated. Autogenerate is a good first draft and not a substitute for reading the
migration. Never edit a migration that has been applied anywhere; add a new one.

## Observability

Grafana comes up with the Prometheus datasource and the **IACode Foundation** dashboard already
provisioned, because both are files in `infra/grafana/`. A dashboard changed in the browser is lost
on the next restart with no trace of what it was — edit the JSON instead.

The dashboard answers four questions: is each dependency up, how much traffic, how slow, and how
many failures. The worker panel reads the Temporal SDK's own instruments, so a worker that is
connected but not polling shows as a flat zero while everything else looks healthy.

Check Prometheus is actually scraping at <http://localhost:19090/targets>. Both `iacode-api` and
`iacode-worker` should be `up`.

## Smoke checks

```bash
python scripts/iacode/smoke.py          # everything, readable
python scripts/iacode/smoke.py --json   # the same, machine-readable
```

The last two checks are the interesting ones: they start a real Temporal workflow and assert that
the activity ran **in the worker process**, reporting facts only the worker can know. A smoke check
that returned a constant would pass while the worker was dead.

## Verifying the whole Gate

```bash
python scripts/iacode/verify.py --list    # the stages
python scripts/iacode/verify.py --fast    # everything that does not restart the stack
python scripts/iacode/verify.py           # everything, including a fresh installation
```

On Windows, `.\verify.ps1` does the same thing.

The full run ends with a fresh installation, which deletes every volume and rebuilds from nothing.
That is the claim this Gate actually makes, so it is verified rather than assumed.

## When something is wrong

**A service will not become healthy.** `python scripts/iacode/stack.py status` shows which one.
Then read its log: `docker compose --project-directory infra/compose --env-file infra/compose/.env
logs <service>`. `stack.py up` fails loudly with the container's own output rather than waiting
forever.

**`/ready` says `NOT_READY`.** The payload names the dependency and carries the probe's error,
redacted. Check that container first.

**Temporal takes a long time on first start.** It provisions its schema on first boot, which is
slower than anything else in the stack. The worker retries its connection for
`IACODE_WORKER_CONNECT_TIMEOUT_SECONDS` (180 by default) rather than crash-looping.

**Stopping PostgreSQL also takes Temporal down.** That is expected and declared: Temporal persists
into the same PostgreSQL server, in its own databases. See
[ADR-0014](../adr/ADR-0014-one-postgresql-server-for-the-foundation.md), and
`scripts/iacode/scenarios/dependency_failure.py`, which asserts exactly this blast radius.

**The frontend shows "Backend unreachable".** The page is served independently of the API, so that
panel means the API is down or the configured address is wrong — not that the frontend failed. The
address is in `config.json`, written at container start from `IACODE_WEB_API_BASE_URL`; check it at
<http://localhost:18081/config.json>.

**A port is already in use.** Change the corresponding `IACODE_*_PORT` in `infra/compose/.env` and
start again. Every published port is a variable for this reason.

**The database is in a state you want gone.** `python scripts/iacode/stack.py reset --yes` deletes
every volume and `up` rebuilds from nothing. Take a backup first if anything in there matters:
[BACKUP-RESTORE.md](BACKUP-RESTORE.md).

## What is not here

Gate 0 is the Foundation. There is no model gateway, no agent runtime, no sandbox, no retrieval and
no training: those belong to later Gates, and the directories reserved for them contain a README
saying so and nothing else. See [docs/MASTER-PLAN.md](../MASTER-PLAN.md).
