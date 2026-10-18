# ADR-0054 — Knowledge indexes are rebuildable cited projections

Status: Accepted
Date: 2026-10-18
Owners: GATE 7 — Knowledge Engine

## Context

An index can outlive a grant, mix revisions or return stale text after restart. Deterministic
builds alone do not prove current permission, useful retrieval, citation integrity or recovery.

## Decision

Use a provider-neutral in-process domain library with shared closed contracts/source/store ports.
The API owns actual source adapters, PostgreSQL transactions, authenticated project scope and
bounded retention lifecycle. No new deployment, graph, project memory, tool, provider call,
uncited synthesis, training or execution/verdict authority is introduced.

Derive bounded exact text spans and deterministic Unicode lexical tokens. Material identity binds
project/source/revision/content/grant digests and index policy/version, separately from time and
first observer. PostgreSQL stores immutable metadata/chunks and an actual parameterized inverted
index. One transaction publishes chunks plus minimal audit facts; per-source serialization keeps
concurrent versions and retries coherent. No production memory fallback or fixed answers.

Search bounds query/candidate/result/byte work and orders relevance/ties deterministically.
Capacity/dependency failures are not empty success. Every excerpt carries exact source/revision/
raw digest, text coordinates, chunk digest and grant digest. It is cited evidence, not an
instruction, confidence estimate or verdict. Predefined varied-corpus expectations measure
relevance and exact citations through actual persistent HTTP retrieval.

Delivery verifies current source/grant/time/index and re-derives persisted integrity. Corruption
or stale versions cannot manufacture valid excerpts. Revocation, source change/removal, expiry,
supersession and withdrawal deny old results before sweeping. Policy/source changes require an
actual new projection, never a relabelled old index.

Consumed finite retention and an owned bounded sweeper physically purge primary chunks/payloads.
Finite minimal tombstones cover maximum source recapture age so retries cannot reset retention
or resurrect a withdrawn revision. Sources, experiences, quality evidence and other projects
remain untouched. Restore reconciles current grants/withdrawals/revisions/time before exposure;
primary deletion is not global backup erasure.

## Alternatives considered

- Embedding-only opaque matches add complexity without necessity for initial bounded retrieval.
- Cached excerpts without current validation would keep revoked content accessible.
- A second authoritative source body or production memory fallback would hide persistence failure.
- In-place content updates would conceal which exact revision a citation identified.

## Consequences, evidence and limits

Retrieval is lexical, not semantic question answering. Token normalization never changes cited
source coordinates. Overload explicitly refuses instead of hiding incomplete green results.
Constraints/re-derivation do not protect against a hostile administrator; clock/source publication
remain trusted operating inputs. Real migrations up/down/autogenerate, matching/ranking, races,
rollback, citations, corruption, drift/rebuild, restart, purge and cross-Gate preservation must
execute before acceptance. This ADR does not claim those tests have already passed.

## Reversal and related artifacts

Ports allow later extraction/richer retrieval under versioned contracts and real rebuilds, with
unchanged rights/citation boundaries. See ADR-0053, ADR-0051, GATE-7-CHECKLIST.md and M2 handoff
policy. This implementing session cannot approve its own milestone.
