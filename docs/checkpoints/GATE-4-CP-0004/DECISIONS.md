# Decisions

## D-001 — Audit the sealed successor, never rewrite it

The immutable subject is `GATE-4-CP-0003` at its canonical tag. All independent evidence and the
verdict belong to this later audit checkpoint. The subject is not modified, re-sealed or re-tagged.

## D-002 — Treat the review archive as transport, not authority

The audit verifies the handed-off archive but also rebuilds and validates it from the sealed tree.
Repository state, canonical policy and independently executed evidence remain authoritative.

## D-003 — Keep synthetic secrets out of durable evidence

Every credential-shaped marker used by the audit is assembled only in memory. Reports record
booleans, counts, reason codes and non-reversible digests, never the marker value.
