# ADR-0030 — Quality evidence and verdicts are immutable derived facts

Status: Accepted
Date: 2026-10-09
Owners: GATE 4 — Quality Engine

## Context

A quality verdict is promotion evidence. If command output, findings, results or the verdict can be
edited after execution, a later reader cannot distinguish a genuine run from a repaired record.
Keeping complete output in PostgreSQL would also create an unbounded secret-bearing data path, and
creating one object per reproduction would waste storage while making identical evidence look
different.

Infrastructure retries add a second constraint: plans, callbacks, events and verdict derivations
may be delivered more than once. Retry behavior must return the fact already recorded, while a
different payload using the same identity must be refused.

## Decision

PostgreSQL stores immutable plans, checks, results, findings, evidence references, verdicts and
ordered run events. Only the quality run envelope changes state and timestamps. Every mutable state
transition appends and flushes its explaining event before changing the state in the same
transaction. Closed database constraints, foreign keys and idempotency keys defend the invariant
independently of the service path.

Complete evidence bytes use the existing MinIO artifact store under a SHA-256-derived key. The
database records size, media type, producer, source digests, retention and rights, with training
and distillation denied by default. A run owns its own immutable evidence reference, while multiple
runs may point to the same content-addressed artifact. Resolution downloads and re-hashes the bytes
before they can support a verdict; missing or changed bytes do not resolve.

Verdicts are pure outputs of the frozen plan, terminal results and resolved evidence set. Their
digest is canonical and is checked before first persistence. A second derivation may equal the
stored verdict or invalidate the run; it never overwrites the row. Reproduction creates a distinct
run over the original plan and snapshot. Comparison digests include semantic outcomes, findings
and evidence digests, but exclude run identifiers, sandbox identifiers, timing and duration so a
genuine replay can match without pretending to be the original occurrence.

## Consequences

Evidence metadata and bytes require two stores and an integrity check on every use. Identical bytes
are stored once, but their per-run references remain auditable. Results cannot arrive before a run
is running or after cancellation begins, and a callback from another owner or origin is refused.
Schema changes are more deliberate because immutable facts cannot be backfilled by rewriting
history.

The bounded database summaries remain useful for operators, while full output never becomes a
column, metric label or log field. Reproduction can expose environmental nondeterminism without
altering either execution.

## Alternatives considered

Mutable result and verdict rows were rejected because a correction would erase the fact under
review. Storing output directly in PostgreSQL was rejected because size and secret exposure would
become properties of every read path. One evidence row and artifact per digest globally was
rejected because it could not attribute the same bytes to a new reproduction run. Comparing the
entire serialized result was rejected because new run IDs, timestamps and sandbox IDs necessarily
differ even when the observable outcome is identical.
