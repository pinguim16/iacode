# ADR-0051 — Retention tombstones prevent experience resurrection

Status: Accepted
Date: 2026-10-17
Owners: GATE 6 — Experience Store

## Context

Deleting a payload while leaving unrestricted recapture resets its privacy clock. Keeping a full
payload as an audit log is not deletion, and hiding an expired row until an occasional manual sweep
does not provide automatic finite primary retention. Restart and parallel requests must not weaken this.

## Decision

A consumed closed policy defines finite capture-age, default/maximum payload retention, bounded
batch size, automatic sweep interval and finite minimal tombstone retention. Policy validation
requires tombstones to cover the whole permitted recapture-age window. No request can widen policy.

Every current experience binds one project and original source-run identity, immutable content,
initial expiry and stable request digest. Conflicting retries fail; a different request identifier
cannot overwrite, renew or recreate an already captured source. Reads/listings/exports reject
expired or withdrawn data immediately, independently of sweep timing.

An owned background task purges expired primary payloads atomically in bounded batches, retaining
only safe project/source/request identifiers, digest, state and deletion time with minimal audit
facts. Explicit withdrawal follows the same authenticated project-bound, idempotent terminal path.
Neither path deletes task runs, snapshots, quality records or another project's data. Tombstone
garbage collection is finite; by that time the original source is too old to capture again.

Legacy unvalidated rows are quarantined, not silently enrolled in a new payload-deletion policy.
Their migration behavior and responsible operational handling are explicit in the runbook. No legacy
data is exposed by current APIs or asserted to satisfy the current schema.

## Evidence and verification

Required tests cover exact clock boundaries, monotonic terminal states, concurrent capture/purge,
duplicate withdrawal, payload absence in actual PostgreSQL, bounded sweep, task failure/shutdown,
real restart, legacy migration and source preservation. Real acceptance and adversarial null-control
results are required before approval; the existence of this ADR is not proof they passed.

## Alternatives considered

- Only filtering expired reads was rejected: primary payloads would remain indefinitely.
- Deleting every identity immediately was rejected: retries/new identifiers could resurrect content.
- Permanent full audit copies were rejected: they would defeat retention.
- A new external scheduler was rejected: the current API lifecycle can own one bounded observable
  sweeper; multiple API instances use database locking rather than a process-global singleton.

## Consequences and risks

Primary deletion does not instantly erase separate backups or source-domain evidence. Backup access,
retention, deletion records and restore reconciliation must be documented and tested where governed;
no claim of global erasure is made. A restored old backup must not be treated as fresh consent and
must replay retained withdrawals before exposure. Captured metadata/digests are not anonymization.
Retention assumes the trusted runtime UTC clock, just as the existing finite capability does.

## Reversal strategy and related artifacts

Changing retention or the tombstone/capture-age relation requires a versioned policy and migration
with adversarial historical/recovery controls. It may shorten availability, never silently resurrect
or extend an existing payload. See ADR-0050, GATE-6-CHECKLIST.md and the Experience Store runbook.
