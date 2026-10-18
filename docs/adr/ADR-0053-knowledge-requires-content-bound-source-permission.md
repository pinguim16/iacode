# ADR-0053 — Knowledge requires content-bound source permission

Status: Accepted
Date: 2026-10-18
Owners: GATE 7 — Knowledge Engine

## Context

Gate 6 persists observable experiences with explicit storage-only consent. Its immutable contracts
deny RAG, training and distillation. Gate 7 must retrieve useful traceable knowledge without
inventing source rights. The platform has no legal-title oracle; runtime access is not a license.

## Decision

Keep Gate 6 contracts and permissions unchanged. Experience admission uses its owning project,
integrity and retention validation, then effective RAG permission. Storage-only experiences are
rejected before index effects. A downstream grant never overrides an original denial.

The initial positive source family is a curated project artifact, not a raw model exchange or
arbitrary upload. An operator-configured read-only curated root carries a closed registry,
versioned artifacts and separate digest-bound rights evidence. Admission binds exact project,
source identity/revision/raw digest and evidence digest. Evidence names ownership, license,
reviewing authority, explicit storage/RAG permission and finite validity. Unknown/denied/expired/
revoked/inconsistent evidence rejects. Training/distillation stay false. The committed default
registry is empty; this delivery grants no reuse right to actual user/provider content.

The API accepts identities and explicit consent only, never text, paths, URLs, grants, commands
or verdicts. Resolution stays inside the configured root and rejects links/reparse escape,
nonregular/missing/oversized/invalid files. It performs no network fetch. Exact serialized source,
derived and delivered content uses the existing canonical secret detector and complete known-key
views, not copied taxonomy or exemptions. Source content is untrusted data, never instructions.

An isolated synthetic validation corpus carries explicit test-only grants to exercise the actual
implementation. Those fixtures do not classify real source ownership. There is no test fallback
inside production behavior.

## Alternatives considered

- Inferring permission from storage consent, authentication or Gate authorization was rejected.
- Retrofitting positive rights into immutable experiences would rewrite their original consent.
- Arbitrary text/URL ingestion would expand source authority and research scope unnecessarily.
- Provider embeddings add transmitted content, credentials and availability/rights boundaries;
  bounded deterministic lexical retrieval does not require them.

## Consequences, evidence and limits

Operators must actually review/deploy grants. Structural/digest checks do not prove legal title.
The configured root and local runtime/database administrator are inside the trust boundary;
hashes are not signatures or anonymization. Reads check current source/grant state before
publication, not a distributed transaction with an author who changes a file afterwards.
Real source/reuse/corruption/secret/path positive/adverse tests must execute before delivery.
This decision is not PASS evidence; GATE-7-CP-0001 owns observable executions.

## Reversal and related artifacts

A broader source family requires a closed adapter, reviewable rights and executed controls.
Signatures can strengthen this structural trust model later. See GATE-7-CHECKLIST.md, PROVENANCE.md,
ADR-0050/0051 and ADR-0054. Independent M2 approval remains a separate later run.
