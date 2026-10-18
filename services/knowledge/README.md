# Knowledge Engine

Gate 7 defines a provider-neutral in-process domain with explicit source/store ports, closed wire
contracts and the existing canonical secret scanner. Acceptance belongs to
[the checkpoint](../../docs/checkpoints/LATEST.md), not this module's presence. Independent M2 audit
is mandatory; there is no self-attestation or Gate8 authorization.

Sources are project-bound curated artifacts whose exact bytes have explicit reviewed storage/RAG
grants. The default registry is empty. Source paths and grants are deployment-owned, not HTTP
input. Existing storage-only experiences are checked by their owning service and remain denied for
RAG. Training/distillation remain false; synthetic validation rights do not apply to actual data.

Derivation preserves original text and exact Unicode coordinates while normalizing only lexical
tokens. Immutable material binds source/revision, raw/grant/policy digests and exact chunks. The API
owns real PostgreSQL transactions/indexes, authentication and retention; there is no provider call,
embedding requirement, production memory fallback, graph, raw transcript upload or tool execution.

Search validates bounded current publications/indexes before matching and returns deterministic
ranked exact cited untrusted excerpts, never synthesized facts or confidence. Current source/grant/
expiry and persisted integrity are checked before delivery. Revocation, change, missing sources,
corruption, stale policy and withdrawal cannot expose old data. Capacity/dependency failure is
explicit, not partial/empty success. Real reindexing preserves the original retention ceiling.

Owned finite sweeps purge primary bodies/chunks and later minimal tombstones; source/evidence and
separate backups have distinct ownership. Restoration must reconcile withdrawals and current
grants/time before exposure. See [the runbook](../../docs/runbooks/KNOWLEDGE-ENGINE.md),
[ADR-0053](../../docs/adr/ADR-0053-knowledge-requires-content-bound-source-permission.md) and
[ADR-0054](../../docs/adr/ADR-0054-knowledge-indexes-are-rebuildable-cited-projections.md).

`python scripts/iacode/gates/knowledge_tests.py` rebuilds the owning API image and executes the
complete domain suite/schema check. Actual SQL/HTTP/migration, varied-corpus retrieval and isolated
live acceptance are separate required evidence; unit doubles never replace them.
