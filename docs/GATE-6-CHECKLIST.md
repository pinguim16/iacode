# GATE 6 — Experience Store Checklist

This canonical specification expands Gate 6 in MASTER-PLAN.md: persist observable engineering
experiences with rights metadata, an API, versioned storage/schema, retention and access controls.
The registry mirrors these ordered mandatory rows. Derive their union with the lesson preflight
and applicable audit obligations before implementation; source presence is not acceptance.

Experience storage is not conversation capture, private reasoning storage, knowledge retrieval,
training, an agent tool executor or a new quality-verdict authority. Gate 7 remains reserved.
Unknown reuse permission is denial. Internal closure follows ADR-0037, not independent M2 approval.

## 1. Entry, scope and architecture

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 1.1 | A separately authorized Gate 6 checkpoint starts only after valid sealed Gate 5 internal closure, preserves every predecessor and anchors the newest seal. | `docs/checkpoints`, `.iacode/anchors/checkpoint-chain.json` | Entry, integrity and scope controls. |
| 1.2 | The canonical checklist and registry agree exactly, and all lesson/audit-derived requirements are extracted before baseline and implementation. | `docs/GATE-6-CHECKLIST.md`, `.iacode/policies/canonical-requirements.json` | Specification and derivation controls. |
| 1.3 | Structural ADRs define the experience boundary, authoritative storage, schema evolution, access, rights and retention before behavior changes. | `docs/adr`, `docs/ARCHITECTURE.md` | Architecture and boundary tests. |
| 1.4 | Experience logic depends on shared contracts and declared ports, not provider adapters, host execution, a container engine or a later knowledge/training service. | `services/experience`, `packages/contracts` | Executable boundary controls. |
| 1.5 | Every inherited mandatory quality gate and counted suite remains; experience-specific build/tests are mandatory and canonically registered. | `.iacode/policies/quality-gates.json`, `.iacode/policies/test-suites.json` | Registry/collection agreement and full Green Keeper. |
| 1.6 | Gate 7 and later reservations remain unimplemented; experience persistence neither grants RAG/training authority nor changes independent milestone verdicts. | `.iacode/policies/gate-scope.json`, `STATE.json` | Scope and successor controls. |

## 2. Observable experience contract

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 2.1 | A versioned, closed experience schema defines task, environment, provider/model/effort observations, repository/base identity, trajectory summary, actions, tools, commands, files, attempts, failures, corrections, tests, quality, reviews, final result, provenance and eligibility. | `packages/contracts`, `.iacode/schemas/experience.schema.json` | FUNCTIONAL-ACCEPTANCE.json; Schema round-trip and adverse cases. |
| 2.2 | Experience content consists only of bounded observable facts and source references; prompts, raw provider responses, credentials, hidden reasoning and arbitrary transcript fields are excluded. | `services/experience`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Positive capture and first-persistence refusal controls. |
| 2.3 | Unobserved provider/model/effort/review information remains explicitly unknown or absent, never fabricated from configuration, a plan or an implementer assertion. | `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Unknown-source and observed-source tests. |
| 2.4 | Identities, timestamps, enums, numeric types, UTF-8, nesting, collection lengths and total encoded bytes are strictly bounded; unknown fields and ambiguous JSON fail closed. | `packages/contracts`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Contract and HTTP negative tests. |
| 2.5 | Only authorized completed source runs and their matching immutable quality/snapshot evidence may support capture; running, missing, cross-project or mismatched inputs are refused. | `apps/api`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Real source-binding integration tests. |
| 2.6 | Source facts, hashes, parent identities and failure outcomes remain traceable; no caller may submit a quality verdict or replace trusted source facts. | `services/experience`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Forged-fact, lineage and failed-source controls. |

## 3. Safety and rights

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 3.1 | Every stored experience requires explicit informed storage consent for the exact project and source; omission, rejection or a conflicting retry causes no capture. | `apps/api`, `packages/contracts` | FUNCTIONAL-ACCEPTANCE.json; Consent and zero-effect refusal tests. |
| 3.2 | Provenance records source type, provider/model when observed, ownership, license, all four storage/reuse permissions, evidence and limits. | `services/experience`, `.iacode/policies/provenance-policy.md` | FUNCTIONAL-ACCEPTANCE.json; Complete provenance round-trip. |
| 3.3 | Unknown ownership/license or unproven permissions cannot yield a positive RAG, training or distillation grant; raw external output never becomes trainable by storage. | `services/experience`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Default-denial and forged-rights tests. |
| 3.4 | Effective permissions cannot exceed any contributing source permission, and provenance/rights remain bound to the exact stored content and export. | `services/experience`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Restrictive propagation and tamper tests. |
| 3.5 | Canonical credential detection scans complete exact normalized content before durable effects and again before delivery; matches and scanner failure produce sanitized refusal. | `packages/common`, `services/experience`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Raw/encoded adverse cases, clean control and scanner failure. |
| 3.6 | Known runtime authorization material and forbidden private/transcript fields cannot enter content, metadata, summaries, diagnostics, audit payloads, errors or exports. | `services/experience`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Pre-effect and durable-absence controls. |
| 3.7 | Denied and unknown reuse requests fail closed without data disclosure; no endpoint performs knowledge retrieval, training or distillation. | `apps/api`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Use-specific access and scope tests. |

## 4. Persistence and integrity

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 4.1 | Alembic evolves the existing experiences persistence contract rather than introducing an unrelated shadow store; ORM and actual PostgreSQL schema agree. | `packages/persistence`, `apps/api/migrations` | FUNCTIONAL-ACCEPTANCE.json; Real migration and schema integration. |
| 4.2 | Schema migration preserves identity, rights and lineage of legacy rows without silently treating unvalidated payloads as current valid experiences. | `apps/api/migrations`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Pre-migration fixture, migration and legacy-access tests. |
| 4.3 | Content, schema version, provenance and digest form one immutable captured fact; unauthorized updates and direct persistence corruption cannot produce a valid delivered record. | `packages/persistence`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Database immutability and corrupt-read controls. |
| 4.4 | Capture and its bounded audit fact commit atomically; failed validation, unavailable dependencies and rolled-back writes leave no partial experience. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Real rollback/failure and zero-residue tests. |
| 4.5 | Stable request identity makes accepted-response-loss and concurrent retries idempotent; conflicting content is refused rather than silently overwritten. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Real concurrent retry and restart tests. |
| 4.6 | New request identifiers cannot silently resurrect revoked/deleted/expired content or reset its retention clock; repeated mutations preserve truthful terminal state. | `services/experience`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Replay, resurrection and terminal tests. |

## 5. Access and API

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 5.1 | All experience operations require actual configured runtime authentication; no unauthenticated legacy alternate path reaches experience data or effects. | `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Signed clean control and absent/invalid/expired/replayed authorization. |
| 5.2 | Project/source identity scopes every read, list, export, withdrawal and deletion; a mismatched project cannot disclose or modify an experience. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Cross-project access and zero-effect controls. |
| 5.3 | Capture, inspect, list and machine-readable export round-trip actual persisted content and hashes, without deriving success from an in-memory fake. | `apps/api`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Real PostgreSQL/HTTP functional proof. |
| 5.4 | Listing is deterministically ordered, bounded and resumable with a validated project-bound cursor; invalid cursors and enumeration cannot bypass access/retention. | `apps/api`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Pagination, bounds and cursor-adversary tests. |
| 5.5 | Errors use stable bounded reason codes and observable correlation without echoing rejected content, credentials, database details or exception strings. | `apps/api`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Adverse HTTP and telemetry tests. |
| 5.6 | Requests and responses preserve the existing authenticated transport and source boundaries; clients and agents cannot gain host execution or verdict authority. | `apps/api`, `packages/contracts` | FUNCTIONAL-ACCEPTANCE.json; Inherited client/runtime regressions and boundary controls. |

## 6. Retention, withdrawal and recovery

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 6.1 | A versioned consumed policy sets finite retention defaults/maxima, bounded processing and explicit operational limits; a caller cannot widen canonical ceilings. | `.iacode/policies`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Policy consumption, malformed policy and limit controls. |
| 6.2 | Expired or storage-withdrawn content is immediately unavailable to reads, listings, exports and reuse, independently of the next physical sweep. | `services/experience`, `apps/api` | FUNCTIONAL-ACCEPTANCE.json; Clock-boundary and withdrawal tests. |
| 6.3 | Owned automatic retention processing physically removes expired primary payloads in bounded atomic batches and records only minimal non-sensitive deletion evidence. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Real sweeper, batch and durable-absence proof. |
| 6.4 | Explicit withdrawal/deletion is authenticated, project-bound and idempotent; it cannot delete source runs, quality evidence or unrelated project data. | `apps/api`, `packages/persistence` | FUNCTIONAL-ACCEPTANCE.json; Repeated deletion and source-preservation tests. |
| 6.5 | Runtime restart preserves records, idempotency and rights; corrupt schema/content/provenance or unavailable source evidence fails closed after recovery. | `apps/api`, `services/experience` | FUNCTIONAL-ACCEPTANCE.json; Real restart/recovery and corrupt-storage scenarios. |
| 6.6 | Background tasks and dependency failures have explicit bounded lifecycle, observable errors and owned shutdown; storage/backup deletion limits and safe restore procedure are documented. | `apps/api`, `docs/runbooks` | FUNCTIONAL-ACCEPTANCE.json; Lifecycle/failed-dependency tests and runbook validation. |

## 7. Functional and adversarial evidence

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7.1 | Actual fresh-stack acceptance captures a real completed governed task and quality result with observed provider/tool lineage and persisted rights, then reads/lists/exports matching bytes. | `scripts/iacode/scenarios` | FUNCTIONAL-ACCEPTANCE.json and actual producer report. |
| 7.2 | Live acceptance proves restart, stable retry, retention expiry, deletion and unchanged source resources through the actual API and database. | `scripts/iacode/scenarios` | FUNCTIONAL-ACCEPTANCE.json; Functional lifecycle/recovery observations. |
| 7.3 | Live adverse controls attack authentication, project mismatch, denied reuse, secret/private ingress, forged facts, corruption and resurrection beside a valid clean control. | `scripts/iacode/scenarios` | FUNCTIONAL-ACCEPTANCE.json; Functional and internal Red Team reports. |
| 7.4 | New integration tests own their runtime namespace, fixtures and temporary resources; operational identities/source bytes stay unchanged and cleanup is observed. | `scripts/iacode`, `apps/api/tests` | FUNCTIONAL-ACCEPTANCE.json; Isolation and cleanup receipts. |
| 7.5 | Every mandatory new experience scenario joins the full non-fast verifier without dropping inherited stages; failed reruns cannot reuse stale PASS artifacts. | `scripts/iacode/verify.py` | FUNCTIONAL-ACCEPTANCE.json; Stage/producer tests and complete immutable verification. |
| 7.6 | Functional reports bind the actual immutable subject, exact source fingerprint and process outcomes; available safe producer bytes survive fallible postprocessing/cleanup. | `scripts/iacode`, `docs/checkpoints` | FUNCTIONAL-ACCEPTANCE.json; Raw capture, exact transport and fresh report validation. |

## 8. Delivery and internal closure

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 8.1 | Runbooks document capture/consent, authentication, all endpoints, schema/lineage/rights, retention, withdrawal, recovery, limits and troubleshooting without exposing configuration values. | `docs/runbooks`, `services/experience/README.md` | Documentation and link controls. |
| 8.2 | All selected lessons and requirements have truthful requirement-specific implementation, executed positive/adverse tests and resolvable evidence. | `docs/checkpoints` | Canonical completeness and memory validation. |
| 8.3 | Full current test/quality verification, every mandatory Green Keeper gate, total completeness, fresh internal Red Team/null control and complete clean-clone mirror pass in order against unchanged source. | `docs/checkpoints`, `scripts/iacode/verify.py` | Actual complete internal assurance. |
| 8.4 | Current tooling validates every sealed predecessor; dynamic/current scope and fixed historical fixtures retain distinct owners and successor transitions remain valid. | `tests`, `scripts/development-ledger` | Current/legacy/successor and published-history proof. |
| 8.5 | Every changed path is declared before finalization; counts, command inputs, provenance, risks, retrospective and resumable handoff remain truthful. | `docs/checkpoints`, `.iacode/memory` | Serialized inventory/checkpoint and count validation. |
| 8.6 | Canonical finalization, a Gate 6-only commit, post-commit seal and immutable archive reconstruction actually succeed; sealed history is never rewritten. | `scripts/development-ledger`, `docs/checkpoints` | Actual seal and transport/archive validation. |
| 8.7 | Intermediate closure records only INTERNAL_GATE_PASS with no blockers; independent fields are justified NOT_REQUIRED here, M2 stays PENDING and second-tool validation stays PENDING_MANUAL. | `docs/checkpoints/STATE.json` | Positive/adverse internal-closure controls. |
| 8.8 | Gate 7 is not started without separate explicit owner authorization and a valid sealed Gate 6 predecessor; independent audit is reserved for M2 closure. | `docs/checkpoints/AUTHORIZATION.md`, `docs/MILESTONE-VALIDATION.md` | Scope and authority controls. |
