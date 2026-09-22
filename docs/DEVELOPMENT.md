# Development

How to work on IACode on a new machine, end to end.

`docs/runbooks/FOUNDATION.md` is the operator's view: start, stop, check, recover. This is the
contributor's view: where the code is, how to change it, and what has to be green before a change
is finished.

## What you need

| Requirement | Why |
|---|---|
| Docker with Compose v2 | every service, every build and every gate runs in a container |
| Python 3.12 or newer | the operational tooling and the development ledger |
| Git | the ledger records repository state |

That is the whole list. No Node, no PostgreSQL client, no `pip install` on the host: the tooling is
standard library only and everything else happens inside an image. The frontend toolchain needs
Node 22 and runs in its own container, so the Node version on your machine is irrelevant.

## First run

```bash
python scripts/iacode/bootstrap_env.py
python scripts/iacode/stack.py up --build
python scripts/iacode/smoke.py
```

Expect several minutes the first time: three images are built and nine are pulled. After that,
starting takes well under a minute.

## Where the code is

```text
apps/api/                  the FastAPI application
  src/iacode_api/          configuration, lifecycle, routes, persistence, clients
  migrations/              Alembic; the schema is only ever created by these
  tests/unit/              no external service; the mandatory gate runs these
  tests/integration/       the real PostgreSQL, Redis, MinIO and Temporal
apps/web/                  the Angular shell
services/orchestrator/     the Temporal worker and the smoke workflow
packages/common/           UUIDv7 and credential redaction
packages/contracts/        the response shapes that cross a process boundary
packages/telemetry/        the logging contract and the ambient correlation context
services/model-gateway/    the provider-neutral model boundary: contracts, adapters, catalog,
  src/                     routing, resilience, telemetry; it imports no application
  tests/                   its own suite, deterministic, with no network and no stack
infra/compose/             the stack
infra/tests/               what the infrastructure declares, and the live configuration
scripts/iacode/            operational tooling: stack, migrate, backup, restore, verify, scenarios
scripts/development-ledger/ the SETUP-00 control plane; sealed, and not yours to change casually
```

A directory under `services/`, `agents/`, `training/`, `evaluation/` or `datasets/` that contains
only a README is **reserved for a later Gate**. `.iacode/policies/gate-scope.json` says which Gate
owns it, and the internal mirror audit fails a delivery that puts an implementation there.

## Changing the backend

Edit under `apps/api/src/`, then:

```bash
python scripts/iacode/gates/api_tests.py                      # unit suite, no stack needed
python scripts/iacode/stack.py up --build                     # rebuild and restart
python scripts/iacode/smoke.py                                # prove it still works
```

The image is rebuilt on `up --build`; there is no live-reload mount, because a container that runs
different code from the image it was built from is a container whose behaviour nobody can
reproduce.

### Changing the schema

1. Edit `apps/api/src/iacode_api/db/models.py`.
2. Generate the migration — see `docs/runbooks/FOUNDATION.md` for the exact command.
3. **Read what it generated.** Autogenerate is a first draft.
4. `python scripts/iacode/migrate.py check` — it fails when the model and the schema disagree.

Never edit a migration that has been applied anywhere. Add a new one.

### Adding configuration

Add the field to `apps/api/src/iacode_api/config.py`, document it in `infra/compose/.env.example`,
and pass it through in `infra/compose/docker-compose.yml`.

Then use it. `test_every_declared_key_is_read_somewhere` reads the application source and fails on a
field nothing consumes: a configuration key with no reader promises behaviour that does not exist.
It caught exactly that during this Gate.

Also add it to `settings_for_tests`, which must supply every field — that is what keeps a test from
inheriting a value from the shell it happens to run in.

## Changing the frontend

```bash
python scripts/iacode/gates/web_tests.py     # production build and the suite, in the container
```

The backend address is never written in the code. It is read from `config.json`, which the web
container writes from its environment at start-up, so one image runs against any backend.

## Changing the worker

`services/orchestrator/`. It shares the dependency lock with the API deliberately: the two sides of
a workflow contract drifting apart surfaces as a deserialisation error inside an activity, which is
a bad way to learn about a version mismatch.

## Before you call a change finished

```bash
python scripts/iacode/verify.py --fast
```

Ten mandatory gates, the stack, the integration suite, the live infrastructure suite, the smoke
check, a verified backup-and-restore cycle and a dependency scan. `--fast` stops before the stages
that restart the stack and delete volumes.

The full run — `python scripts/iacode/verify.py`, or `.\verify.ps1` on Windows — adds the restart
scenario, the dependency-failure scenario and a complete installation from no volumes at all. That
is what the Gate is verified by.

The mandatory gate set comes from `.iacode/policies/quality-gates.json`. The verification reads that
file rather than carrying its own list, so a gate added to the registry is covered immediately.

## Conventions worth knowing

**Liveness and readiness answer different questions.** `/health` touches nothing and stays `UP`
while a dependency is down. `/ready` probes every mandatory dependency and answers 503 when one
fails. Do not make `/health` smarter.

**A failure tells the caller a safe summary and the operator the truth.** The error contract returns
a stable code, a safe message and the correlation identifier; the traceback goes to the log. A
driver error routinely quotes the connection string it failed on, and that string carries a
password.

**Log fields that have no value are absent, not null.** Gate 0 has no `taskId`, `runId` or
`agentId`, so records do not carry them. A field that is always null teaches readers to ignore it
before it ever means anything.

**Metrics are labelled with the route template, never the URL.** One time series per identifier is
the standard way to take down a Prometheus.

**Integration is proved against the real service.** `docs/DEVELOPMENT-CONTRACT.md` forbids a mock
where the test stack has the real thing.

**A test that writes to the stack's own database cleans up after itself.** The store tests use the
real PostgreSQL on purpose, and a fixture left behind is a row in the operational catalog. See
`apps/api/tests/integration/test_gateway_persistence.py`, where an invariant also asserts the
catalog holds no provider the policy does not declare.

**A gate that measures inside an image builds that image first.** Otherwise it reports on whatever
was baked into the last build, which is how a red test survived a green gate for an entire Gate.
`compose.build_service` exists for this, and a control-plane test enforces it.

**Nothing above the gateway names a provider.** Ask for `provider:model` or a route alias. A
provider name in a provider-neutral module fails the boundary scan.

## The development ledger

Changes are delivered through Gates, with a checkpoint that records what was done and the evidence
for it. Read `START-HERE.md` before changing anything under `docs/checkpoints/`, `.iacode/` or
`scripts/development-ledger/`.

```bash
python scripts/development-ledger/validate_checkpoint.py
python -m unittest discover -s tests
```
