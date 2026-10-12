# Decisions

## D-001 — Judge the sealed subject and write a successor verdict

The immutable subject is `GATE-4-CP-0005` at its canonical tag. Independent evidence, attestation
and verdict belong to `GATE-4-CP-0006`; the subject is never rewritten or re-tagged.

## D-002 — One complete verifier invocation is the promotion evidence

The required 42-stage run is executed once in a fresh published clone. A failed integral run cannot
be superseded by a selective rerun. Observation waits inside the product policy are not retries.

## D-003 — Preserve shared developer state while proving isolation

The audit snapshots any Compose project named `iacode` before the run and compares it afterwards.
The verifier must use and remove only its checkout-owned project.

## D-004 — Keep synthetic secrets out of durable evidence

Credential-shaped markers are assembled only in memory. Reports store reason codes, booleans,
counts and non-reversible digests, never the marker value.

## D-005 — Classify independence precisely

This is `FRESH_SESSION_INDEPENDENT_AUDIT`: independent of the implementing run but not a cross-tool
audit. `crossToolValidation` remains `NOT_AVAILABLE`, and M2 remains `PENDING`.
