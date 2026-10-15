# ADR-0041 — Polling cleanup preserves completed checks

Status: Accepted
Date: 2026-10-15
Owners: GATE 4 — Quality Engine lifecycle

## Context

A real positive control once stopped after its first result. Its original ephemeral history was
not retained, so that specific incident cannot be reconstructed. A deterministic regression then
reproduced a matching lifecycle failure: a completed sandbox check cancels its polling watcher
while the watcher awaits a durable read. The pinned SDK's actual await implementation was observed
returning ActivityError with a CancelledError cause, not asyncio.CancelledError. The old join
propagated that expected cleanup cancellation and discarded the completed check.

The same published v1 subject subsequently reproduced it on the real Temporal server: its workflow
was FAILED on a cancelled iacode_quality_read_run activity while the API envelope remained RUNNING.
The bounded observation is preserved in
[V1-POLLING-FAILURE.json](../checkpoints/GATE-4-CP-0010/V1-POLLING-FAILURE.json), without history payloads.

The SDK exposes the underlying activity error through its public
[cause property](https://python.temporal.io/temporalio.exceptions.ActivityError.html).
The audit harness exercises pinned SDK internals only as evidence; product code uses public types.

## Decision

When this workflow explicitly requests cancellation of its watcher, joining the watcher accepts
an ActivityError only if its direct cause is Temporal CancelledError. Asyncio task cancellation
keeps its existing handling. A watcher already completed before that request, an unrelated read
failure, or any other cause still propagates. This cleanup does not set operator cancellation,
rewrite a result, or change a verdict. The completed check continues through normal recording.

A durable read can also complete after the active handle was cleared. Accepted cancellation still
sets the authoritative flag, but a no-longer-active handle is not dereferenced or cancelled.

## Consequences

Both cancellation representations are covered by behavioral regression, alongside a negative
control for unrelated read errors. Real clean/adverse flows and the complete verifier still have
to pass. The earlier timeout is preserved; the matching deterministic defect is not represented
as a recovered original history or as independent review.
