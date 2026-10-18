# GATE 7 — Knowledge Engine Checklist

This canonical specification expands MASTER-PLAN.md: derive, index and retrieve governed reusable
knowledge with citations and invalidation. The registry mirrors every ordered row before behavior
is implemented. Requirements are the union of these rows, the lesson preflight and applicable audit
obligations. Presence of code is not acceptance. Gate 7 closes M2; its implementing delivery is
READY_FOR_REVIEW, never an independent milestone approval. Gate 8 and later remain out of scope.

Storage is not RAG permission. Gate 6 storage-only experiences retain their original immutable
rights and cannot be laundered through this engine. Initial positive sources are curated immutable
project artifacts with explicit operator-reviewed, content-bound storage/RAG grants. The engine
does not fetch arbitrary URLs, execute source instructions, synthesize uncited answers or train.

## 1. Entry and architecture

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 1.1 | A separately authorized checkpoint starts after valid sealed Gate 6 internal closure and anchors every sealed predecessor without rewriting history. | `docs/checkpoints`, `.iacode/anchors/checkpoint-chain.json` | Entry and integrity verification. |
| 1.2 | The checklist and registry agree exactly; all canonical, lesson and audit requirements are extracted before baseline and implementation. | `docs/GATE-7-CHECKLIST.md`, `.iacode/policies/canonical-requirements.json` | Derivation and specification controls. |
| 1.3 | Structural ADRs define source authority, rights, derivation/index identity, persistence, citations, invalidation and recovery before behavior changes. | `docs/adr`, `docs/ARCHITECTURE.md` | Architecture and boundary controls. |
| 1.4 | The provider-neutral knowledge library uses shared closed contracts and declared source/store ports; it has no provider, host/tool execution, graph, memory or training authority. | `services/knowledge`, `packages/contracts` | Executed architectural positive/adverse controls. |
| 1.5 | All inherited gates, suites and full-verifier stages remain; complete knowledge build/tests and live acceptance are added to their canonical registries. | `.iacode/policies`, `scripts/iacode` | Registry/collection agreement and complete verification. |

## 2. Source admission and rights

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 2.1 | Ingestion selects an exact project/source/revision and stable request identity; callers cannot submit replacement source text, arbitrary paths/URLs, rights or quality verdicts. | `packages/contracts`, `apps/api`, `services/knowledge` | FUNCTIONAL-ACCEPTANCE.json; Closed ingress and zero-effect refusal. |
| 2.2 | Curated source admission consumes a closed operator-controlled registry with project, source identity, exact content digest, ownership, license, explicit storage/RAG grants, evidence and finite validity. | `.iacode/policies`, `services/knowledge` | FUNCTIONAL-ACCEPTANCE.json; Actual permitted-source capture and grant mutations. |
| 2.3 | Unknown, denied, missing, expired, revoked, conflicting or mismatched source permission fails closed before any index effect or disclosure; training/distillation remain denied. | `services/knowledge`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Complete rights adversaries and durable absence. |
| 2.4 | Existing experiences are admitted only through their owning validation and effective permissions; storage-only, withdrawn, expired, corrupt or cross-project experiences cannot support knowledge. | `apps/api`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Actual Gate 6 source boundary and unchanged rights. |
| 2.5 | Every contributor's permissions and provenance constrain the derived document, all chunks and exports; no derived permission exceeds a source grant. | `services/knowledge`, `packages/contracts` | FUNCTIONAL-ACCEPTANCE.json; Restrictive propagation and tamper controls. |
| 2.6 | Source resolution is bounded and confined to the configured curated root; traversal, symlinks/reparse escape, nonregular files, missing/changed bytes and invalid UTF-8 are refused without network fetch or execution. | `services/knowledge`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Real source-resolution attacks and clean control. |
| 2.7 | Full exact normalized source, derived records and delivered payloads are scanned with canonical credential detection and known authorization forms; scanner failure refuses safely. | `packages/common`, `services/knowledge` | FUNCTIONAL-ACCEPTANCE.json; Raw/encoded/scanner-failure controls before persistence and delivery. |
| 2.8 | Private/transcript fields, prompts, provider answers and runtime secrets are not admitted or echoed in knowledge, diagnostics, audit facts or errors. Source content is untrusted data, never instructions or authority. | `services/knowledge`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Privacy and instruction-boundary attacks. |

## 3. Contracts, derivation and indexing

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 3.1 | Versioned closed schemas define source identity, provenance, document/chunk/index version, exact digests, citations, query and results; unknown fields and ambiguous JSON are refused. | `packages/contracts`, `.iacode/schemas` | FUNCTIONAL-ACCEPTANCE.json; JSON round-trip and adverse schema tests. |
| 3.2 | Consumed policy bounds request/source/result bytes, types, nesting, text/chunks/tokens, query size, result count, candidate work and retention; callers cannot widen ceilings. | `.iacode/policies`, `services/knowledge` | FUNCTIONAL-ACCEPTANCE.json; Policy-key consumption and boundary cases. |
| 3.3 | Deterministic derivation preserves exact source spans and hashes, handles Unicode/line endings explicitly and records the transformation version without inventing summaries or facts. | `services/knowledge` | FUNCTIONAL-ACCEPTANCE.json; Repeated derivation and exact-span controls. |
| 3.4 | Index identity binds source revision/digest, grant/provenance and derivation policy; restart/retry cannot silently change identity, duplicate chunks or rewrite immutable content. | `services/knowledge`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Replay, concurrency and drift tests. |
| 3.5 | Actual persistent inverted indexing supports bounded parameterized lexical matching, deterministic relevance ordering and stable ties; no fixed response or production in-memory fallback is used. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Actual PostgreSQL retrieval over a varied corpus. |
| 3.6 | Empty/no-match queries and invalid/oversized inputs have explicit semantics; capacity or dependency failures cannot masquerade as a successful empty result or silently partial search. | `services/knowledge`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Positive no-match and capacity/dependency negatives. |

## 4. Persistence and recovery

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 4.1 | Alembic and ORM agree on the real PostgreSQL knowledge schema, ownership, constraints and indexes; up/down/from-zero/autogenerate preserve inherited data. | `packages/persistence`, `apps/api/migrations` | FUNCTIONAL-ACCEPTANCE.json; Actual migration/reversibility and cross-Gate preservation. |
| 4.2 | Source admission, immutable document/chunks/index and minimal audit fact commit atomically; failed validation or dependency/write failure leaves no partial publication. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Rollback and durable-absence controls. |
| 4.3 | Stable request/source identity makes accepted-response-loss and concurrent retries idempotent; conflicting retries are refused and cannot reset retention or resurrect withdrawn revisions. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Actual concurrent/restart/loss/terminal tests. |
| 4.4 | Persisted body, digest, chunk spans/tokens, source/grant and envelope are revalidated before delivery; direct database corruption cannot yield valid retrieval or citation. | `services/knowledge`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Actual corrupt-storage/refused-recovery controls. |
| 4.5 | Restart/rebuild preserves truthful current revisions, rights and index version; stale or incompatible index is unavailable until an actual valid rebuild, never silently served. | `services/knowledge`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Persistent restart, policy/index drift and rebuild proof. |

## 5. Retrieval, citations and access

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 5.1 | Every ingestion, inspect/list, search, citation/export and invalidation requires configured authenticated runtime transport; alternate unauthenticated paths cannot reach effects/data. | `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Valid auth plus absent/invalid/expired/replayed controls. |
| 5.2 | Every lookup/index/query/citation is project-bound before data access; cross-project identifiers and enumeration cannot disclose content, digests or modify state. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Actual project-isolation and zero-effect attacks. |
| 5.3 | Every returned knowledge excerpt has a resolvable exact source/revision/content digest, chunk digest and source span; no output can omit/fabricate a citation or outrun its source rights. | `packages/contracts`, `services/knowledge` | FUNCTIONAL-ACCEPTANCE.json; Exact citation round-trip and forgery controls. |
| 5.4 | Retrieval is measured against a versioned varied corpus and predefined relevant/irrelevant expectations; bounded relevance and deterministic ranking are demonstrated, not asserted. | `services/knowledge/tests`, `scripts/iacode/scenarios` | FUNCTIONAL-ACCEPTANCE.json; Actual measured retrieval report. |
| 5.5 | Queries do not become durable content or sensitive logs; stable bounded errors/correlation never expose input, paths, credentials, exception text or SQL. | `apps/api`, `packages/telemetry` | FUNCTIONAL-ACCEPTANCE.json; Actual logs and adverse HTTP observations. |
| 5.6 | Knowledge is cited untrusted evidence only; it cannot submit a tool result, change a quality verdict, widen an approval or execute host/source instructions. | `services/knowledge`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Authority/instruction attacks and inherited runtime regressions. |

## 6. Invalidation and retention

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 6.1 | Revocation, source change/removal, expiry and explicit withdrawal immediately deny stale index/citation use independently of background sweeping. | `services/knowledge`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Actual source/grant/clock mutation attacks. |
| 6.2 | Replacing a source revision atomically invalidates the prior publication; superseded excerpts never mix with the new revision and stable retries preserve terminal facts. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Concurrent revision and stale-citation controls. |
| 6.3 | Finite consumed retention and an owned bounded automatic sweeper physically purge primary knowledge/chunk payloads and retain only finite minimal safe tombstones/audit facts. | `apps/api`, `packages/persistence`, `.iacode/policies` | FUNCTIONAL-ACCEPTANCE.json; Actual automatic purge and durable absence. |
| 6.4 | Authenticated project-bound invalidation/withdrawal is idempotent and does not delete sources, experiences, quality evidence or another project's records. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Source preservation and repeated withdrawal. |
| 6.5 | Dependency/sweeper failures and shutdown are observable and bounded; restore must reconcile current grants, withdrawals, source versions and time before exposure. | `apps/api`, `docs/runbooks` | FUNCTIONAL-ACCEPTANCE.json; Actual failure/recovery/lifecycle and documented backup limits. |

## 7. Functional and adversarial verification

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7.1 | Fresh actual-stack acceptance admits a rights-qualified validation corpus, indexes real persisted content, measures retrieval and resolves exact citations through authenticated HTTP. | `scripts/iacode/scenarios` | FUNCTIONAL-ACCEPTANCE.json and original producer report. |
| 7.2 | Live proof exercises restart, replay, denied Gate 6 reuse, cross-project/auth attacks, current-source invalidation, retention/withdrawal, corrupt recovery and unchanged inherited resources. | `scripts/iacode/scenarios` | FUNCTIONAL-ACCEPTANCE.json; Actual lifecycle/adverse observations. |
| 7.3 | Every test owns its namespace/resources and observes cleanup; no global Docker/editor state or other applications are changed. | `scripts/iacode`, `apps/api/tests` | FUNCTIONAL-ACCEPTANCE.json; Before/after identity and cleanup receipts. |
| 7.4 | One complete non-fast verifier invocation at an exact published immutable subject includes every inherited/new mandatory stage; partial reruns or stale producers cannot produce PASS. | `scripts/iacode/verify.py`, `docs/checkpoints` | FUNCTIONAL-ACCEPTANCE.json; Current immutable complete verification. |
| 7.5 | Safe exact producer bytes, subject/fingerprint/process identities and actual cleanup outcomes survive fallible postprocessing; original failures remain immutable and transported byte-exactly. | `scripts/iacode`, `docs/checkpoints` | FUNCTIONAL-ACCEPTANCE.json; Raw preservation and actual Git transport. |

## 8. M2 delivery and handoff

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 8.1 | Runbooks document sources/grants, default denial, index/search/citations, all endpoints/auth, invalidation/rebuild, retention/restore, privacy, ranking and operational limits. | `docs/runbooks`, `services/knowledge/README.md` | Documentation and link controls. |
| 8.2 | All selected lessons and requirements have specific implementation, executed positive/adverse tests, documentation and resolvable evidence without false PASS or waived controls. | `docs/checkpoints`, `.iacode/memory` | Canonical completeness and memory validation. |
| 8.3 | Complete test/quality, whole Green Keeper, total completeness, fresh internal Red Team/VALID null control and full clean-clone closure mirror pass in order against unchanged source. | `docs/checkpoints` | Actual ordered internal assurance. |
| 8.4 | Current tooling validates all sealed predecessors and successor/promotion positive paths; no historical subject, tag, denominator or promotion rule is rewritten. | `tests`, `scripts/development-ledger` | Historical compatibility and protocol transition proof. |
| 8.5 | A milestone consolidation covers Gates 4–7, integration, requirements, tests, regressions, lessons/guards, ADRs, risks/debt, provenance and observed cost/model usage without invented figures. | `docs/checkpoints/M2-CONSOLIDATION.md` | Complete internal milestone evidence and audit handoff. |
| 8.6 | All changed paths are declared before finalization; commands, counts, provenance, retrospective, risks and exact continuation are truthful and reproducible. | `docs/checkpoints`, `.iacode/memory` | Serialized inventory/count/checkpoint validation. |
| 8.7 | Canonical finalization, Gate 7-only committed content, post-commit sealing, publication and exact immutable review reconstruction actually succeed. | `scripts/development-ledger`, `docs/checkpoints` | Actual seal and public transport/archive validation. |
| 8.8 | The milestone delivery is sealed READY_FOR_REVIEW with no blockers; independent review/Red Team stay PENDING, second-tool PENDING_MANUAL and M2 PENDING. No self-attestation or Gate 8 advance occurs. | `docs/checkpoints/STATE.json`, `AUTHORIZATION.md` | Positive/adverse readiness and milestone-boundary controls. |
