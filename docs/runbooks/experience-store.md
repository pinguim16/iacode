# Experience Store operations (Gate 6)

Status and executed acceptance are recorded in [LATEST](../checkpoints/LATEST.md). This runbook is
an operating contract, not a Gate PASS or independent M2 attestation. Gate 7 remains reserved.

## Authentication and consent

Every endpoint below requires the configured finite desktop capability and the existing byte-exact
HMAC request/response protocol with timestamp and durable Redis replay protection. Supply its value
through the protected operator environment, never a URL, task, file, command argument or log. Legacy
development mode deliberately returns `AUTHENTICATED_RUNTIME_REQUIRED` without data/SQL access.
One trusted local operator capability is not multi-tenant user/RBAC authentication.

The pre-effect/delivery scanner protects actual configured HMAC/provider keys and storage/database/
Redis passwords, including the declared encoded forms. A public MinIO account identity is not itself
a bearer secret; no word is globally exempted. Canonical unknown-secret shape detection still runs,
and a public word is still refused if it is also an actual configured password or bearer value.

`GET /api/v1/experiences/sources/{taskRunId}` discovers the actual project/run identities and
current eligibility facts. It does not capture anything. Select a completed `SUCCEEDED`, `FAILED`
or `CANCELLED` task; missing, active, too old or cross-project sources cannot be captured.
Quality is optional and explicitly unknown when omitted. When selected, it must be terminal, own
this task or be unowned, and match its immutable workspace snapshot. All evidence is re-read,
bounded, scanned and hashed; the verdict is reconstructed using the frozen quality rules.

Before POST, inform the operator that the exact task/project's bounded operational facts, provider/
model observations, commands' digests, snapshot references, status and quality evidence references
will be stored until the initial expiry. Neither a prompt, answer, private reasoning, raw provider
response, environment values, source files nor tool output is copied. Unknown ownership/license
means no RAG/training/distillation permission. A capture cannot assert that a human reviewed code.

Source queries use explicit consumed-column projections with unexpected lazy loads refused;
task/agent answers, event payloads and unneeded metadata do not enter the adapter. Required
workspace/command JSON byte totals are bounded in PostgreSQL before transfer, and snapshot rights
are checked through exact typed permission scalars rather than loading unrelated metadata.

## API

All operations use `/api/v1/experiences`. UUIDs are canonical lowercase; unknown body/query fields,
duplicate fields, nonfinite numbers, invalid UTF-8, invalid types and oversized/deep inputs fail
closed. Errors contain only a fixed code and a generated correlation ID, never rejected values.

- `POST /projects/{projectId}`: `taskRunId`, optional `qualityRunId`, exact boolean
  `storageConsent: true`, a stable UUID `idempotencyKey`, optional integer `retentionSeconds`.
  No arbitrary body, annotation, fact, verdict or rights grant is accepted. Returns 201 for first
  capture or 200 for an identical replay, with identity, content digest, initial expiry and document.
- `GET /projects/{projectId}/{experienceId}`: verified current document and envelope.
- `GET /projects/{projectId}/{experienceId}/export`: the same machine-readable JSON, attachment
  `experience.json`, with `Cache-Control: no-store`. Exports never grant additional rights.
- `GET /projects/{projectId}?limit=25&cursor=...`: bounded ordered summaries. Continue with the exact
  returned project-bound cursor; an empty final page is valid. Full payloads are not embedded.
- `DELETE /projects/{projectId}/{experienceId}`: idempotent storage withdrawal. It returns only the
  minimal terminal envelope, physically clears the primary body/summary and never deletes sources.

Read/list/export `use=storage` is the only allowed purpose. Any other use, including `rag`,
`training`, `distillation` or an unknown purpose, returns 403 without content. Wrong project IDs
cannot read or mutate a record; a wrong project cursor cannot enumerate another scope.
Never automatically replay an uncertain mutating request with a fresh key. An identical original
key returns the same still-active record/expiry; conflicting parameters return 409. A different
key for the same source also conflicts. Expired/deleted content returns 410 and cannot be renewed.

## Policy and primary retention

The versioned consumed policy is [experience-policy.json](../../.iacode/policies/experience-policy.json):
30-day default, 90-day maximum payload retention and capture age, 90-day minimal tombstones, a
30-second owned sweep, batch 100, at most 1000 facts/category, 256 KiB normalized document,
4096-byte capture request and 50 summaries/page. Requests may shorten, never widen those limits.
Every stored expiry is immutable even if the default changes later. Trusted runtime UTC is the
clock authority. At `now >= expiresAt`, access is denied regardless of sweep scheduling.

Each API instance owns and awaits its retention task. Startup creates clients without dependency
I/O; the first sweep is delayed by the policy interval. SQL locking/`SKIP LOCKED` coordinates
instances. A failed sweep emits `RETENTION_STORE_UNAVAILABLE` with type-only safe diagnostics and
is retried at the next bounded interval. Investigate actual PostgreSQL readiness and that log;
do not disable retention, widen expiry or mark an unavailable store healthy.

Purge replaces body with `{}`, summary with empty text, denies all permissions, retains only
identities/digests/state/time plus payload-free audit kinds. After the tombstone window and capture
window are both past, bounded GC removes the tombstone and its audit rows. Task/snapshot/quality
records have their own domain retention: this is not global erasure or anonymization.

## Legacy, restart, backups and safe restore

Migration 0007 evolves the original table. Preexisting rows remain schema 0/`LEGACY`, with their
original identity/body/rights preserved; current APIs cannot expose or promote them. The owner must
inventory and govern them separately before any explicit disposal. They are not silently enrolled
in current consent or retention, and do not satisfy the new schema. Downgrade is a maintenance
operation, never a live rollback that promises continued Gate 6 behavior.

Restart loads the same immutable SQL facts and original expiry. Reads revalidate schema/digest,
lineage and actual evidence; missing/corrupt/unavailable sources fail closed. Never repair a body
or rights in place, disable the immutable trigger operationally, substitute another source, or
manufacture a PASS. Correct the owned source dependency or withdraw the affected record.

Primary withdrawal does not erase separate backups, exports or original source evidence. Backup
access and finite disposal are the responsible operator's obligations. Keep a restricted minimal
withdrawal inventory (project, experience, source, original digest, terminal state/time) separately
from each older backup for at least its entire restore lifetime. This repository does not claim an
old offline backup can discover a later withdrawal by itself.

Before exposing any restored database: keep API/network consumers stopped, verify backup integrity,
upgrade schema, reconcile every retained withdrawal against the exact project/source/digest,
reapply deletion and the consumed current expiry policy, verify primary body absence and denied
reads, and only then restore authenticated traffic. A restored ACTIVE row is not fresh consent.
If the complete post-backup withdrawal inventory is unavailable, do not expose restored experience
data; retain the isolation and obtain owner direction. Never restore over the operational database
as a test. Rehearse only against an explicitly owned disposable target and preserve source rows.

## Troubleshooting and limits

Use fixed error codes plus generated correlation ID. `SOURCE_*`, `QUALITY_*` and
`STORED_*` refusals are not permission grants. Reconcile exact identities and evidence without
copying raw source/error text into logs. Unknown effort, Git commit, reviews and case counts are
honest limits, not missing values to fill from current configuration. No endpoint runs a tool,
calls a model, submits a verdict, performs knowledge retrieval or trains a model.
