# Runbook — backup and restore

A backup that has never been restored is a hope. This runbook covers both halves, and the
verification that proves the pair works.

## What is backed up, and what is not

| Component | Backed up | Why |
|---|---|---|
| The `iacode` database | yes | the system of record; it cannot be rebuilt |
| The artifact bucket | yes | object storage; it cannot be rebuilt |
| Temporal's databases | **no** | Temporal's to rebuild. Restoring workflow history into a running cluster is not a recovery procedure, it is a way to corrupt one |
| Redis | **no** | a cache. Losing it costs a cold start, which the application handles anyway |
| Prometheus and Grafana data | **no** | metrics history and Grafana's own state. The dashboards and the datasource are files in this repository, so the useful part is already in Git |

## Taking a backup

```bash
python scripts/iacode/backup.py
python scripts/iacode/backup.py --keep 5 --label before-upgrade
```

The stack must be running: the backup goes through the live PostgreSQL and MinIO containers.

Each run writes a directory under `var/backups/` named for the instant it started:

```text
var/backups/20260921T203754Z/
├── manifest.json      what was backed up, with a SHA-256 of each part
├── postgres.dump      pg_dump in PostgreSQL's custom format
└── minio/             a mirror of the artifact bucket
```

Three properties worth knowing:

**A partial backup is a failure.** If either component fails, the run exits non-zero and the
manifest records `FAILED` with the reason. A backup that half-succeeded and exited zero is worse
than no backup, because it will be trusted on the day it is needed.

**No credential is written into the output.** The manifest says what was backed up, never how the
tooling authenticated, and everything it writes passes through the redactor. Attaching a manifest
to a ticket is safe.

**`--keep` prunes.** The newest N backups survive; older ones are deleted. The default is 7. This
is the whole retention policy: a scheduler, offsite copies and lifecycle rules are operations
concerns that Gate 0 has no environment to exercise, and pretending otherwise would be a feature
nobody could test. Scheduling `backup.py` is the supported way to automate it.

## Verifying that a restore actually works

```bash
python scripts/iacode/backup_restore_check.py
```

This is the check that matters, and it is part of `verify.py`. It:

1. writes a synthetic row and a synthetic object;
2. takes a backup;
3. **deletes** the row and the object that were just backed up;
4. restores into a database and a bucket created for this run;
5. reads the synthetic data back and compares it;
6. confirms the live copies are still gone, so the check did not quietly restore over the working
   database;
7. deletes everything it created.

Nothing real is destroyed: the restore targets a disposable database and a disposable bucket. A
verification that overwrote the working database would be one nobody dares to run, which is the
same as not having one.

## Restoring for real

```bash
python scripts/iacode/restore.py var/backups/20260921T203754Z --yes
```

**This is destructive.** It drops and recreates the target database and mirrors the backup over the
bucket, so `--yes` is required.

Before touching anything it reads the manifest and refuses a backup recorded as incomplete, then
verifies every recorded SHA-256. Restoring a corrupted dump over a working database turns one
problem into two.

To restore somewhere safe instead — which is what you want if the goal is to look at old data
rather than to recover:

```bash
python scripts/iacode/restore.py var/backups/20260921T203754Z \
  --database iacode_inspection --bucket iacode-inspection --yes
```

`--skip-objects` restores only the database.

### A real recovery

1. Stop the API and the worker so nothing writes during the restore:
   `docker compose --project-directory infra/compose --env-file infra/compose/.env stop api worker`
2. Restore: `python scripts/iacode/restore.py <backup> --yes`
3. Bring the migrations up to date, in case the backup predates the current schema:
   `python scripts/iacode/migrate.py upgrade`
4. Start again: `python scripts/iacode/stack.py up`
5. Confirm: `python scripts/iacode/smoke.py`

Step 3 is the one that gets forgotten. A backup restored from before a schema change leaves the
database at the old revision, and the application expects the new one.

## When it fails

**"psql: FATAL: database is being accessed by other users".** Something still holds a connection.
The restore terminates other sessions before dropping the database, so this means a new one was
opened in between: stop the API and the worker first.

**"does not match its recorded checksum".** The backup is corrupt. Do not force it; use an earlier
one. This check exists precisely so a corrupt dump is not written over working data.

**"records result='FAILED'".** The backup never completed. The manifest's `components` array says
which part failed and why.

**The restore succeeds but the application misbehaves.** Check
`python scripts/iacode/migrate.py current` against what the code expects. See step 3 above.
