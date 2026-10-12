# ADR-0035 — Review bundles bind immutable content

Status: Accepted
Date: 2026-10-12
Owners: GATE 4 — Quality Engine

## Context

The CP0008 fresh-session audit rebuilt CP0007's review archive twice from its sealed published tag.
Those two archives were valid and byte-identical to each other, but neither matched the digest or
size CP0007 declared. The old producer read mutable working-tree and live remote state, and the
declaration was written before finalization and sealing changed checkpoint files. The archive was
deterministic for one observation, but the declaration did not identify bytes recoverable from an
immutable subject.

A declaration cannot be embedded in the byte stream whose digest it declares: changing the
declaration changes the digest recursively. The protocol therefore needs an explicit content/evidence
boundary rather than an implicit timing convention.

## Decision

Checkpoint schema `3.4.0` defines the review archive over an immutable Git content commit. The
producer reads checkpoint and repository bytes from Git objects at that commit, derives its
changeset against the checkpoint's recorded base commit, and adds tracked tests, migrations, schemas
and policies as canonical review context. It does not read working-tree dirt, live refs or observation
timestamps into the payload.

`REVIEW-BUNDLE-VALIDATION.json` is the one excluded checkpoint file. It is a seal-evidence sidecar
that names the content commit and tree and declares the archive digest, size and entry count. The
exclusion is exact and validator-enforced.

Sealing clones through non-local Git transport, checks out the content commit detached, and uses the
producer carried by that commit to build and validate the archive twice. The seal is refused unless
the outputs are byte-identical. The declaration and reconstruction command record are then added by
the permitted evidence commit before the canonical tag is created. Validation independently rebuilds
the declared subject twice and compares both outputs with the declaration. Historical schemas retain
their original interpretation.

Pre-seal published subjects use `refs/tags/iacode-subjects/`. They are exact inputs to verification,
not sealed-evidence retention. `refs/tags/iacode-preserved/` remains reserved for historical commits
that a sealed checkpoint's evidence names and whose removal would make that checkpoint invalid.

## Consequences

A schema `3.4.0` checkpoint cannot reach or retain `READY_FOR_REVIEW` with a mutable, missing, stale
or non-reconstructible review declaration. A reviewer can recover the declared bytes from the named
commit without trusting the producer's working tree or current remote state. The generated ZIP
remains outside source control, while its exact identity and reconstruction subject are sealed.

The canonical checkpoint tag resolves to the later evidence commit, not the content commit named by
the declaration. Seal chronology therefore permits the sidecar as a fourth evidence-only file and
permits no other product or policy change.

Reconstruction is more expensive because it deliberately crosses Git transport and runs twice at
seal time and during validation. That cost is accepted: determinism without recoverability is not a
review transport guarantee.

## Alternatives considered

Declaring a pre-finalization working-tree archive was rejected because later checkpoint writes change
its payload. Embedding the declaration in the archive was rejected as mathematically self-referential.
Hashing only the product changes and omitting the checkpoint was rejected because review evidence is
part of the Gate subject. Trusting one local rebuild was rejected because it does not prove transport
or byte determinism. Reusing `refs/tags/iacode-preserved/` for an unfinished verification subject
was rejected because every reference in that namespace is intentionally load-bearing for a sealed
checkpoint. Rewriting CP0007 was rejected because sealed subjects remain immutable.
