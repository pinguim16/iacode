# Knowledge Engine

The [canonical checkpoint](../checkpoints/LATEST.md) owns executed delivery status. Gate7's internal
delivery is prepared for a separate independent M2 audit; this runbook is not a passing verdict.
Read [ADR-0053](../adr/ADR-0053-knowledge-requires-content-bound-source-permission.md) and
[ADR-0054](../adr/ADR-0054-knowledge-indexes-are-rebuildable-cited-projections.md) for the trust model.

## Sources and explicit permission

The image ships an empty `.iacode/knowledge-sources/registry.json`. Storage consent, an authenticated
runtime user and Gate authorization do not grant RAG rights. Current Gate6 experiences have
unverified ownership/unknown licenses and false RAG/training/distillation permissions. The knowledge
adapter validates their actual project/source/integrity/retention, then denies their reuse. No
downstream grant edits the immutable original experience.

A curated source deployment is read-only and controlled by its responsible operator. Keep actual
payloads/grants outside the public checkout/build context; the narrow default artifact/grant paths
are ignored as a defence, not an instruction to publish their registry. Configure the API's
`IACODE_KNOWLEDGE_SOURCE_ROOT` to a container-visible root and mount the owned deployment there
read-only through an explicit deployment override. No HTTP endpoint selects a root/path or uploads
grants. Do not restart Docker or another application to configure this; an API deployment/restart
is a separately controlled operator action, not authority granted by this runbook.

The root contains a closed `registry.json`, `artifacts/*.json` and `grants/*.json` (nested safe
relative paths are permitted). One registry entry binds projectId, sourceId, revision,
artifactPath, sourceDigest, grantPath and grantDigest. Digests are SHA256 of the exact raw files,
not reserialized approximations. There is only one current revision per project/source pair.

CuratedArtifact contains schemaVersion, the fixed curated-project-knowledge classification,
createdAt, title and text. It is not a prompt/provider response/transcript upload. SourceGrant
contains its version/fixed kind, grantId, exact project/source/revision/digest, ownership/license,
reviewing authority, reviewable evidence, reviewed boolean, ACTIVE/REVOKED status, explicit
storageAllowed/ragAllowed, false trainingAllowed/distillationAllowed, validFrom and validUntil.
Use the actual shared models/schema rather than invent extra fields. The operator must possess and
retain real rights evidence: structural validation does not verify legal title or sign grants.
Unknown/blank ownership/license/authority/evidence, denial, expiry/revocation or inconsistent digests
refuse. Isolated synthetic validation grants authorize those fixtures only, not actual user data.

## Authentication and endpoints

Every operation requires a configured finite desktop capability and the existing signed runtime
transport. Header names/version come from `iacode_contracts.desktop.PROTOCOL`; compute signatures
with `iacode_common.desktop_auth.signed_headers` and verify response signatures. Never copy a key
into source, a URL, a log or this document. See [desktop security](DESKTOP-CLIENTS.md). Legacy
unauthenticated runtime mode cannot reach knowledge. Project UUIDs scope every query and effect;
a mismatched identity cannot disclose or delete another project's data.

All paths begin `/api/v1/knowledge/projects/{projectId}`:

| Method / suffix | Meaning |
|---|---|
| POST `/ingestions` | Select sourceKind, sourceId, revision, explicit boolean storageConsent, stable idempotencyKey and optional bounded retentionSeconds. No source body/path/grant/verdict is accepted. |
| POST `/search` | Closed JSON query and optional limit; no query persistence or echo. Returns results/outcome/ranking and an untrusted-content marker. |
| GET `/documents` | Bounded active permitted summaries; optional limit and project-bound cursor. Follow nextCursor even if a permission-filtered page is empty. |
| GET `/documents/{documentId}` | Revalidate current source, rights, expiry, body/index integrity and return the complete document envelope. |
| GET `/documents/{documentId}/export` | Same validation and content, machine-readable JSON attachment. |
| GET `/documents/{documentId}/chunks/{chunkId}` | Resolve the exact current citation/excerpt, not a caller-supplied quote. |
| DELETE `/documents/{documentId}` | Idempotent authenticated withdrawal and physical primary payload/index removal; sources remain intact. |

Reuse one stable ingestion key after a lost/unauthenticated/uncertain response; do not automatically
repeat a mutation under a fresh identity. Conflicting requests are refused. A new request cannot
renew retention or resurrect a withdrawn/expired source revision. Source/grant/policy changes
require actual reindexing with valid current consent and a new identity, and never widen the old
revision's retention ceiling. Reusing a revision for different artifact bytes is a conflict.

## Derivation, search and citations

Text is never rewritten into a generated summary. Exact chunks reconstruct the source `/text`;
coordinates are Unicode codepoints, start inclusive/end exclusive. Original CRLF/Unicode remain
in excerpts. Only index tokens use NFKC/casefold and Unicode word matching; tokens are a unique
sorted set. The actual Unicode database version is part of the index fingerprint; a changed
normalizer requires a real rebuild. JavaScript consumers must interpret coordinates as codepoints,
not UTF-16 code units. Oversized tokens/chunks/bodies fail rather than being silently truncated.

An actual PostgreSQL GIN inverted index matches parameterized query tokens within project scope.
Every bounded current document and index is checked before matching, including no-match queries.
Ranking is descending distinct-token overlap, then shorter span, source identity, ordinal and
document identity. It is lexical relevance, not semantic answer synthesis or calibrated confidence.
The validation corpus supplies predefined relevant/irrelevant expectations, not an invented score.

Each hit has exact excerpt, matched tokens/overlap score and a citation binding document/source/
revision/raw digest/grant digest/chunk digest/text coordinates. It is untrusted evidence, never
instructions, a tool callback, an approval or a quality verdict. No model/network executor is
called by retrieval. Inspect/resolve current citations instead of trusting copied old text.

## Limits, errors and observability

The consumed `.iacode/policies/knowledge-policy.json` fixes hard bounded source/registry/body,
chunk/token/query/candidate/result/page/response work, retention windows, batch/interval and
operation timeout. A request may lower allowed retention, never widen policy. Response capacity
covers the complete document envelope; SQL JSON rendering has a separately bounded receiver.
Capacity exhaustion, stale index and dependency/scanner failures are explicit refusals, not empty
success or silently partial search. A valid no-match returns NO_PERMITTED_MATCH with no excerpt.

Responses/errors are no-store JSON with bounded codes and generated correlation. Authentication
replay/expiry, wrong project/cursor, missing consent, invalid types/unknown fields, revoked rights,
source drift and corruption refuse. Dependency/timeout messages do not echo SQL, paths, query text,
source content, credentials or exception strings. Access logs retain method/scoped route/status,
not targets/query payloads. Canonical credential scanning and all known authorization forms run
before source-derived persistence and delivery; scanner failure is itself a refusal.

## Invalidation, retention, restart and restore

Changing/removing the current source or grant, revoking/expiring permission, withdrawing a document
or reaching its retention deadline immediately denies old delivery without waiting for a sweep.
Do not rewrite old content or pretend its digest is the new revision. Publish the intended registry
and exact artifact/grant files coherently; mixed reads fail closed. Reindex valid current sources;
old publication stays unavailable until a new projection actually commits.

The API owns a delayed bounded sweeper with observed errors and awaited shutdown. It purges expired/
invalidated primary bodies/index rows atomically, retains minimal source/request/digest/state audit
tombstones for a finite policy window and later removes only tombstones outside recapture age.
Withdrawal never deletes an experience, task, artifact, quality source or unrelated project.

Restart uses actual persisted state, not a memory fallback. On restore, isolate the restored database
and source deployment, reconcile current grants/withdrawals/revisions and actual UTC time before
exposing HTTP. Do not treat an old backup as renewed consent. Do not restore a withdrawn revision
without its deletion history. Primary purge is not instant erasure of separate backups, source
records or external copies. Trusted local operator/database/clock assumptions remain explicit.

## Validation and troubleshooting

`python scripts/iacode/gates/knowledge_tests.py` rebuilds and runs the complete domain suite/schema
comparison. The counted API integration suite uses actual disposable PostgreSQL databases and
authenticated HTTP for migrations, transactions, GIN matching, citations, races, corruption,
withdrawal and recovery. The full non-fast verifier must additionally run isolated live acceptance
and every inherited provider/sandbox/quality/client/experience control. Unit doubles are not proof
of SQL or actual runtime operation. Follow checkpoint evidence for what has really executed.

For missing matches, inspect current permission/source revision and actual document expiry/index
policy first. A missing/unavailable source is not permission to serve a cached quote. Correct an
actual source/rights/dependency problem, reindex when required, and rerun the full affected proof.
Never turn off scanners/authentication, widen a deadline to hide a defect, erase failure reports,
prune global Docker state or stop other applications to manufacture acceptance.
