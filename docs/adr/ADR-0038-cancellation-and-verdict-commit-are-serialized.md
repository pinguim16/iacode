# ADR-0038 — Cancellation and verdict commit are serialized

Status: Accepted
Date: 2026-10-15
Owners: GATE 4 — Quality Engine

## Context

The internal audit reproduced accepted CANCELLING at sandbox completion without an in-memory signal.
The watcher stopped before the result write; the store correctly refused success, but the workflow
failed instead of reaching CANCELLED. Reading durable state alone also leaves a race before the
write. After all checks pass, cancellation can race immutable verdict commitment as well.

## Decision

Re-read authoritative state after activity completion and before final derivation. If an activity
fails while the durable run is CANCELLING, finish cancellation and cleanup; propagate the failure
unchanged when cancellation was not accepted. Cancellation is an explicit fail-closed input to
verdict derivation. Both stores refuse a non-FAIL verdict once cancellation has been accepted.

Cancellation acceptance and immutable verdict commitment share the run-row lock in PostgreSQL.
If cancellation wins, verdict commitment must be FAIL; a stale PASS derivation is refused and the
workflow resumes the cancellation path. If verdict commitment wins while the run is still
finalizing, cancellation is refused with CANCELLATION_WINDOW_CLOSED (HTTP 409) before any event
or signal. An already-terminal run returns its existing state idempotently. The
already committed verdict is never overwritten. The memory store enforces the same semantics.

## Consequences

Accepted cancellation cannot strand a run at a result, transition or verdict persistence boundary.
Cancellation has a precise end: immutable verdict commitment, before the final terminal envelope
transition. Operators receive a conflict for requests that arrive after that point, not a false
acknowledgment. Unrelated activity failures remain observable. Existing immutable result facts are
not rewritten to simulate cancellation.

## Alternatives considered

Another durable read without a persistence invariant was rejected because it merely moves the race.
Overwriting a committed verdict was rejected because it destroys evidence. Allowing success into a
CANCELLING run or reporting successful cancellation without cleanup was rejected as false evidence.

## Reversal

A future atomic finalization protocol can replace the barrier only with equivalent positive,
adversarial, database-concurrency and live lifecycle proof. Historical evidence stays unchanged.
