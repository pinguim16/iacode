# ADR-0014 — One PostgreSQL server for the Foundation, two sets of databases

Status: Accepted
Date: 2026-09-21
Owners: GATE 0 — Foundation

## Context

Temporal needs a persistent store. The Foundation already runs PostgreSQL as its system of record.
Either Temporal shares that server or the stack runs a second database container.

The Gate 0 authorization says not to add infrastructure the Foundation does not need, and also that
the auxiliary services a distribution genuinely requires are in scope. Temporal genuinely requires a
database; a second container for it is a judgement call, not an obligation.

## Decision

**One PostgreSQL server, three databases.** `iacode` is ours; `temporal` and `temporal_visibility`
are Temporal's, created by `infra/postgres/initdb/10-temporal-databases.sql` before Temporal's
auto-setup runs.

Separate databases rather than separate schemas in one database, because that is what makes the
backup clean: `pg_dump --dbname=iacode` produces the system of record and nothing else, with no
filter that could drift as Temporal's internal tables change.

The consequence is a real one and it is **declared rather than discovered**: stopping PostgreSQL
takes Temporal down with it. `scripts/iacode/scenarios/dependency_failure.py` encodes the expected
blast radius per service and asserts it, so this coupling is a checked fact — and so the narrow
cases stay meaningful: stopping Redis must take nothing else with it, and the scenario fails if it
ever does.

## Evidence

- `infra/postgres/initdb/10-temporal-databases.sql` creates both databases idempotently.
- `infra/tests/test_running_stack.py::test_the_temporal_databases_exist_beside_ours` reads
  `pg_database` and asserts all three exist.
- `scripts/iacode/scenarios/dependency_failure.py` declares `postgres -> {postgres, temporal}` and
  asserts the observed set matches exactly.
- `scripts/iacode/backup.py` dumps only `iacode`, and says why in its module docstring.

## Alternatives Considered

**A dedicated `temporal-postgres` container.** It removes the coupling, at the cost of a tenth
container, a second volume, a second set of credentials and a second thing to back up or explain
why not. The coupling it removes is visible in a local development stack and irrelevant to
correctness: when PostgreSQL is down the application cannot accept work either.

**Temporal's SQLite store.** Supported for development, and it would make the local stack diverge
from anything a later Gate could deploy, which is the divergence this Gate exists to avoid.

**One database with separate schemas.** Fewer objects, and it makes the backup a filtered dump —
exactly the kind of filter that silently stops matching when the other party adds a table.

## Consequences

- Nine long-running containers instead of ten.
- Stopping or losing PostgreSQL stops Temporal. Declared, asserted and documented in the runbook.
- The backup covers the system of record and deliberately not workflow history, which is Temporal's
  to rebuild. Restoring workflow history into a running cluster is a way to corrupt one.
- Both parties share a connection budget. At Foundation scale this is not a constraint; if it ever
  becomes one, the reversal is small.

## Risks

- **Temporal's schema churn lives in our server.** Contained by the database boundary: an upgrade
  migrates `temporal`, never `iacode`.
- **A restore of the whole server would need care.** Not a procedure this Gate offers: the restore
  targets one database by name.

## Reversal Strategy

Add a `temporal-postgres` service, point Temporal's `POSTGRES_SEEDS` at it, and delete the init
script. Temporal rebuilds its schema on first boot, so no data has to be migrated. The blast-radius
map in the dependency-failure scenario then becomes `postgres -> {postgres}` and the scenario proves
the change took effect.

## Related Artifacts

- [ADR-0012](ADR-0012-foundation-runtime-stack.md)
- `docs/runbooks/BACKUP-RESTORE.md`
- `docs/runbooks/FOUNDATION.md`
