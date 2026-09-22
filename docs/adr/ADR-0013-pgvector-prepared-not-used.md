# ADR-0013 — pgvector is prepared, not used

Status: Accepted
Date: 2026-09-21
Owners: GATE 0 — Foundation

## Context

Retrieval belongs to `GATE 7 — Knowledge Engine`. The Gate 0 authorization asks for pgvector to be
"prepared at the level the future architecture needs", and explicitly forbids a fake embeddings
feature. Those two constraints leave a narrow band between doing nothing and doing too much, and
this ADR records where in that band the Gate landed.

Three options were actually available:

1. use the plain PostgreSQL image and add the extension in Gate 7;
2. use the pgvector image and create the extension now;
3. use the pgvector image, create the extension, and add a vector column.

## Decision

**Option 2.** The stack runs `pgvector/pgvector:0.8.6-pg17`, and the first migration executes
`CREATE EXTENSION IF NOT EXISTS vector`. No vector column is defined, no embedding is computed and
no retrieval code exists.

Option 1 was rejected because it defers an *engine* decision. Adding the extension later is not a
migration, it is a change of base image: the plain `postgres` image does not have the shared library,
so Gate 7 would have to rebuild the database container and re-verify the stack before writing a line
of retrieval code. Taking the pgvector image now costs nothing — it is the PostgreSQL image plus one
extension — and turns that into a column addition.

Option 3 was rejected because the embedding dimension is a retrieval decision. `vector(768)` and
`vector(1536)` are different columns, the choice follows from a model Gate 1 has not selected, and
declaring one now would freeze a guess into the schema. Changing it later means rewriting every row.

Creating the extension is the part that is knowable now. Choosing a dimension is not.

## Evidence

- `apps/api/migrations/versions/0001_foundation_schema.py` creates and drops the extension.
- `apps/api/tests/integration/test_pgvector_extension_is_available` reads `pg_extension` against
  the running database, so the preparation is a checked fact rather than a plan.
- No `vector` column exists in `apps/api/src/iacode_api/db/models.py`.

## Alternatives Considered

See the three options above; each is recorded with why it was not taken.

## Consequences

- Gate 7 adds a column and an index to an existing database, with no change to the image or to the
  stack.
- The Foundation carries an unused extension. It occupies catalogue space and nothing else.
- The migration's `downgrade` drops the extension, so the migration stays reversible.

## Risks

- **The extension could rot unnoticed**, being unused until Gate 7. Mitigated by the integration
  test, which fails the moment the extension stops being there — which is what would happen if
  somebody swapped the image back to plain `postgres`.
- **A later Gate might want a different vector implementation.** Dropping an unused extension is
  one line.

## Reversal Strategy

Remove the two `op.execute` lines from the first migration and change the image in
`infra/compose/docker-compose.yml`. Nothing depends on either.

## Related Artifacts

- [ADR-0012](ADR-0012-foundation-runtime-stack.md)
- `docs/GATE-0-CHECKLIST.md` row 5.9
- `docs/MASTER-PLAN.md`, `GATE 7 — Knowledge Engine`
