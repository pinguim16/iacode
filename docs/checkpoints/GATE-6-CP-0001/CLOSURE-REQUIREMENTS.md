# Closure Requirements - GATE-6-CP-0001

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/GATE-6-CHECKLIST.md, the canonical GATE-6 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

## Requirements

| ID | Source | Anchor | Mandatory | Implementation | Final | Description |
|---|---|---|---|---|---|---|
| `REQ-0001` | GATE_SPECIFICATION | `canonical:GATE-6#1.1` | yes | `COMPLETE` | `PARTIAL` | A separately authorized Gate 6 checkpoint starts only after valid sealed Gate 5 internal closure, preserves every predecessor and anchors the newest seal. |
| `REQ-0002` | GATE_SPECIFICATION | `canonical:GATE-6#1.2` | yes | `COMPLETE` | `PARTIAL` | The canonical checklist and registry agree exactly, and all lesson/audit-derived requirements are extracted before baseline and implementation. |
| `REQ-0003` | GATE_SPECIFICATION | `canonical:GATE-6#1.3` | yes | `COMPLETE` | `PARTIAL` | Structural ADRs define the experience boundary, authoritative storage, schema evolution, access, rights and retention before behavior changes. |
| `REQ-0004` | GATE_SPECIFICATION | `canonical:GATE-6#1.4` | yes | `COMPLETE` | `PARTIAL` | Experience logic depends on shared contracts and declared ports, not provider adapters, host execution, a container engine or a later knowledge/training service. |
| `REQ-0005` | GATE_SPECIFICATION | `canonical:GATE-6#1.5` | yes | `COMPLETE` | `PARTIAL` | Every inherited mandatory quality gate and counted suite remains; experience-specific build/tests are mandatory and canonically registered. |
| `REQ-0006` | GATE_SPECIFICATION | `canonical:GATE-6#1.6` | yes | `COMPLETE` | `PARTIAL` | Gate 7 and later reservations remain unimplemented; experience persistence neither grants RAG/training authority nor changes independent milestone verdicts. |
| `REQ-0007` | GATE_SPECIFICATION | `canonical:GATE-6#2.1` | yes | `COMPLETE` | `PARTIAL` | A versioned, closed experience schema defines task, environment, provider/model/effort observations, repository/base identity, trajectory summary, actions, tools, commands, files, attempts, failures, corrections, tests, quality, reviews, final result, provenance and eligibility. |
| `REQ-0008` | GATE_SPECIFICATION | `canonical:GATE-6#2.2` | yes | `COMPLETE` | `PARTIAL` | Experience content consists only of bounded observable facts and source references; prompts, raw provider responses, credentials, hidden reasoning and arbitrary transcript fields are excluded. |
| `REQ-0009` | GATE_SPECIFICATION | `canonical:GATE-6#2.3` | yes | `COMPLETE` | `PARTIAL` | Unobserved provider/model/effort/review information remains explicitly unknown or absent, never fabricated from configuration, a plan or an implementer assertion. |
| `REQ-0010` | GATE_SPECIFICATION | `canonical:GATE-6#2.4` | yes | `COMPLETE` | `PARTIAL` | Identities, timestamps, enums, numeric types, UTF-8, nesting, collection lengths and total encoded bytes are strictly bounded; unknown fields and ambiguous JSON fail closed. |
| `REQ-0011` | GATE_SPECIFICATION | `canonical:GATE-6#2.5` | yes | `COMPLETE` | `PARTIAL` | Only authorized completed source runs and their matching immutable quality/snapshot evidence may support capture; running, missing, cross-project or mismatched inputs are refused. |
| `REQ-0012` | GATE_SPECIFICATION | `canonical:GATE-6#2.6` | yes | `COMPLETE` | `PARTIAL` | Source facts, hashes, parent identities and failure outcomes remain traceable; no caller may submit a quality verdict or replace trusted source facts. |
| `REQ-0013` | GATE_SPECIFICATION | `canonical:GATE-6#3.1` | yes | `COMPLETE` | `PARTIAL` | Every stored experience requires explicit informed storage consent for the exact project and source; omission, rejection or a conflicting retry causes no capture. |
| `REQ-0014` | GATE_SPECIFICATION | `canonical:GATE-6#3.2` | yes | `COMPLETE` | `PARTIAL` | Provenance records source type, provider/model when observed, ownership, license, all four storage/reuse permissions, evidence and limits. |
| `REQ-0015` | GATE_SPECIFICATION | `canonical:GATE-6#3.3` | yes | `COMPLETE` | `PARTIAL` | Unknown ownership/license or unproven permissions cannot yield a positive RAG, training or distillation grant; raw external output never becomes trainable by storage. |
| `REQ-0016` | GATE_SPECIFICATION | `canonical:GATE-6#3.4` | yes | `COMPLETE` | `PARTIAL` | Effective permissions cannot exceed any contributing source permission, and provenance/rights remain bound to the exact stored content and export. |
| `REQ-0017` | GATE_SPECIFICATION | `canonical:GATE-6#3.5` | yes | `COMPLETE` | `PARTIAL` | Canonical credential detection scans complete exact normalized content before durable effects and again before delivery; matches and scanner failure produce sanitized refusal. |
| `REQ-0018` | GATE_SPECIFICATION | `canonical:GATE-6#3.6` | yes | `COMPLETE` | `PARTIAL` | Known runtime authorization material and forbidden private/transcript fields cannot enter content, metadata, summaries, diagnostics, audit payloads, errors or exports. |
| `REQ-0019` | GATE_SPECIFICATION | `canonical:GATE-6#3.7` | yes | `COMPLETE` | `PARTIAL` | Denied and unknown reuse requests fail closed without data disclosure; no endpoint performs knowledge retrieval, training or distillation. |
| `REQ-0020` | GATE_SPECIFICATION | `canonical:GATE-6#4.1` | yes | `COMPLETE` | `PARTIAL` | Alembic evolves the existing experiences persistence contract rather than introducing an unrelated shadow store; ORM and actual PostgreSQL schema agree. |
| `REQ-0021` | GATE_SPECIFICATION | `canonical:GATE-6#4.2` | yes | `COMPLETE` | `PARTIAL` | Schema migration preserves identity, rights and lineage of legacy rows without silently treating unvalidated payloads as current valid experiences. |
| `REQ-0022` | GATE_SPECIFICATION | `canonical:GATE-6#4.3` | yes | `COMPLETE` | `PARTIAL` | Content, schema version, provenance and digest form one immutable captured fact; unauthorized updates and direct persistence corruption cannot produce a valid delivered record. |
| `REQ-0023` | GATE_SPECIFICATION | `canonical:GATE-6#4.4` | yes | `COMPLETE` | `PARTIAL` | Capture and its bounded audit fact commit atomically; failed validation, unavailable dependencies and rolled-back writes leave no partial experience. |
| `REQ-0024` | GATE_SPECIFICATION | `canonical:GATE-6#4.5` | yes | `COMPLETE` | `PARTIAL` | Stable request identity makes accepted-response-loss and concurrent retries idempotent; conflicting content is refused rather than silently overwritten. |
| `REQ-0025` | GATE_SPECIFICATION | `canonical:GATE-6#4.6` | yes | `COMPLETE` | `PARTIAL` | New request identifiers cannot silently resurrect revoked/deleted/expired content or reset its retention clock; repeated mutations preserve truthful terminal state. |
| `REQ-0026` | GATE_SPECIFICATION | `canonical:GATE-6#5.1` | yes | `COMPLETE` | `PARTIAL` | All experience operations require actual configured runtime authentication; no unauthenticated legacy alternate path reaches experience data or effects. |
| `REQ-0027` | GATE_SPECIFICATION | `canonical:GATE-6#5.2` | yes | `COMPLETE` | `PARTIAL` | Project/source identity scopes every read, list, export, withdrawal and deletion; a mismatched project cannot disclose or modify an experience. |
| `REQ-0028` | GATE_SPECIFICATION | `canonical:GATE-6#5.3` | yes | `COMPLETE` | `PARTIAL` | Capture, inspect, list and machine-readable export round-trip actual persisted content and hashes, without deriving success from an in-memory fake. |
| `REQ-0029` | GATE_SPECIFICATION | `canonical:GATE-6#5.4` | yes | `COMPLETE` | `PARTIAL` | Listing is deterministically ordered, bounded and resumable with a validated project-bound cursor; invalid cursors and enumeration cannot bypass access/retention. |
| `REQ-0030` | GATE_SPECIFICATION | `canonical:GATE-6#5.5` | yes | `COMPLETE` | `PARTIAL` | Errors use stable bounded reason codes and observable correlation without echoing rejected content, credentials, database details or exception strings. |
| `REQ-0031` | GATE_SPECIFICATION | `canonical:GATE-6#5.6` | yes | `COMPLETE` | `PARTIAL` | Requests and responses preserve the existing authenticated transport and source boundaries; clients and agents cannot gain host execution or verdict authority. |
| `REQ-0032` | GATE_SPECIFICATION | `canonical:GATE-6#6.1` | yes | `COMPLETE` | `PARTIAL` | A versioned consumed policy sets finite retention defaults/maxima, bounded processing and explicit operational limits; a caller cannot widen canonical ceilings. |
| `REQ-0033` | GATE_SPECIFICATION | `canonical:GATE-6#6.2` | yes | `COMPLETE` | `PARTIAL` | Expired or storage-withdrawn content is immediately unavailable to reads, listings, exports and reuse, independently of the next physical sweep. |
| `REQ-0034` | GATE_SPECIFICATION | `canonical:GATE-6#6.3` | yes | `COMPLETE` | `PARTIAL` | Owned automatic retention processing physically removes expired primary payloads in bounded atomic batches and records only minimal non-sensitive deletion evidence. |
| `REQ-0035` | GATE_SPECIFICATION | `canonical:GATE-6#6.4` | yes | `COMPLETE` | `PARTIAL` | Explicit withdrawal/deletion is authenticated, project-bound and idempotent; it cannot delete source runs, quality evidence or unrelated project data. |
| `REQ-0036` | GATE_SPECIFICATION | `canonical:GATE-6#6.5` | yes | `COMPLETE` | `PARTIAL` | Runtime restart preserves records, idempotency and rights; corrupt schema/content/provenance or unavailable source evidence fails closed after recovery. |
| `REQ-0037` | GATE_SPECIFICATION | `canonical:GATE-6#6.6` | yes | `COMPLETE` | `PARTIAL` | Background tasks and dependency failures have explicit bounded lifecycle, observable errors and owned shutdown; storage/backup deletion limits and safe restore procedure are documented. |
| `REQ-0038` | GATE_SPECIFICATION | `canonical:GATE-6#7.1` | yes | `COMPLETE` | `PARTIAL` | Actual fresh-stack acceptance captures a real completed governed task and quality result with observed provider/tool lineage and persisted rights, then reads/lists/exports matching bytes. |
| `REQ-0039` | GATE_SPECIFICATION | `canonical:GATE-6#7.2` | yes | `COMPLETE` | `PARTIAL` | Live acceptance proves restart, stable retry, retention expiry, deletion and unchanged source resources through the actual API and database. |
| `REQ-0040` | GATE_SPECIFICATION | `canonical:GATE-6#7.3` | yes | `COMPLETE` | `PARTIAL` | Live adverse controls attack authentication, project mismatch, denied reuse, secret/private ingress, forged facts, corruption and resurrection beside a valid clean control. |
| `REQ-0041` | GATE_SPECIFICATION | `canonical:GATE-6#7.4` | yes | `COMPLETE` | `PARTIAL` | New integration tests own their runtime namespace, fixtures and temporary resources; operational identities/source bytes stay unchanged and cleanup is observed. |
| `REQ-0042` | GATE_SPECIFICATION | `canonical:GATE-6#7.5` | yes | `COMPLETE` | `PARTIAL` | Every mandatory new experience scenario joins the full non-fast verifier without dropping inherited stages; failed reruns cannot reuse stale PASS artifacts. |
| `REQ-0043` | GATE_SPECIFICATION | `canonical:GATE-6#7.6` | yes | `COMPLETE` | `PARTIAL` | Functional reports bind the actual immutable subject, exact source fingerprint and process outcomes; available safe producer bytes survive fallible postprocessing/cleanup. |
| `REQ-0044` | GATE_SPECIFICATION | `canonical:GATE-6#8.1` | yes | `COMPLETE` | `PARTIAL` | Runbooks document capture/consent, authentication, all endpoints, schema/lineage/rights, retention, withdrawal, recovery, limits and troubleshooting without exposing configuration values. |
| `REQ-0045` | GATE_SPECIFICATION | `canonical:GATE-6#8.2` | yes | `COMPLETE` | `PARTIAL` | All selected lessons and requirements have truthful requirement-specific implementation, executed positive/adverse tests and resolvable evidence. |
| `REQ-0046` | GATE_SPECIFICATION | `canonical:GATE-6#8.3` | yes | `COMPLETE` | `PARTIAL` | Full current test/quality verification, every mandatory Green Keeper gate, total completeness, fresh internal Red Team/null control and complete clean-clone mirror pass in order against unchanged source. |
| `REQ-0047` | GATE_SPECIFICATION | `canonical:GATE-6#8.4` | yes | `COMPLETE` | `PARTIAL` | Current tooling validates every sealed predecessor; dynamic/current scope and fixed historical fixtures retain distinct owners and successor transitions remain valid. |
| `REQ-0048` | GATE_SPECIFICATION | `canonical:GATE-6#8.5` | yes | `COMPLETE` | `PARTIAL` | Every changed path is declared before finalization; counts, command inputs, provenance, risks, retrospective and resumable handoff remain truthful. |
| `REQ-0049` | GATE_SPECIFICATION | `canonical:GATE-6#8.6` | yes | `COMPLETE` | `PARTIAL` | Canonical finalization, a Gate 6-only commit, post-commit seal and immutable archive reconstruction actually succeed; sealed history is never rewritten. |
| `REQ-0050` | GATE_SPECIFICATION | `canonical:GATE-6#8.7` | yes | `COMPLETE` | `PARTIAL` | Intermediate closure records only INTERNAL_GATE_PASS with no blockers; independent fields are justified NOT_REQUIRED here, M2 stays PENDING and second-tool validation stays PENDING_MANUAL. |
| `REQ-0051` | GATE_SPECIFICATION | `canonical:GATE-6#8.8` | yes | `COMPLETE` | `PARTIAL` | Gate 7 is not started without separate explicit owner authorization and a valid sealed Gate 6 predecessor; independent audit is reserved for M2 closure. |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | yes | `COMPLETE` | `PARTIAL` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | yes | `COMPLETE` | `PARTIAL` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | yes | `COMPLETE` | `PARTIAL` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | yes | `COMPLETE` | `PARTIAL` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | yes | `COMPLETE` | `PARTIAL` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | yes | `COMPLETE` | `PARTIAL` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | yes | `COMPLETE` | `PARTIAL` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | yes | `COMPLETE` | `PARTIAL` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | yes | `COMPLETE` | `PARTIAL` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | yes | `COMPLETE` | `PARTIAL` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | yes | `COMPLETE` | `PARTIAL` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | yes | `COMPLETE` | `PARTIAL` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | yes | `COMPLETE` | `PARTIAL` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | yes | `COMPLETE` | `PARTIAL` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | yes | `COMPLETE` | `PARTIAL` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | yes | `COMPLETE` | `PARTIAL` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | yes | `COMPLETE` | `PARTIAL` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | yes | `COMPLETE` | `PARTIAL` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | yes | `COMPLETE` | `PARTIAL` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | yes | `COMPLETE` | `PARTIAL` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | yes | `COMPLETE` | `PARTIAL` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | yes | `COMPLETE` | `PARTIAL` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | yes | `COMPLETE` | `PARTIAL` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | yes | `COMPLETE` | `PARTIAL` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | yes | `COMPLETE` | `PARTIAL` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | yes | `COMPLETE` | `PARTIAL` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | yes | `COMPLETE` | `PARTIAL` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | yes | `COMPLETE` | `PARTIAL` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | yes | `COMPLETE` | `PARTIAL` | Verify a required protocol transition must never turn a mandatory gate red |
| `LESSON-REQ-0030` | LESSON | `lesson:LSN-0031` | yes | `COMPLETE` | `PARTIAL` | Verify an empty applicable set is not a missing required set, and a control must tell them apart |
| `LESSON-REQ-0031` | LESSON | `lesson:LSN-0032` | yes | `COMPLETE` | `PARTIAL` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts |
| `LESSON-REQ-0032` | LESSON | `lesson:LSN-0033` | yes | `COMPLETE` | `PARTIAL` | Verify a value bound in middleware is absent in the handlers that run outside it |
| `LESSON-REQ-0033` | LESSON | `lesson:LSN-0034` | yes | `COMPLETE` | `PARTIAL` | Verify re-deriving what the framework already computed diverges from the framework |
| `LESSON-REQ-0034` | LESSON | `lesson:LSN-0035` | yes | `COMPLETE` | `PARTIAL` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work |
| `LESSON-REQ-0035` | LESSON | `lesson:LSN-0036` | yes | `COMPLETE` | `PARTIAL` | Verify a gate that runs inside an image measures the image, not the source |
| `LESSON-REQ-0036` | LESSON | `lesson:LSN-0037` | yes | `COMPLETE` | `PARTIAL` | Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves |
| `LESSON-REQ-0037` | LESSON | `lesson:LSN-0038` | yes | `COMPLETE` | `PARTIAL` | Verify two representations of one concept in one module disagree, and the safer one loses |
| `LESSON-REQ-0038` | LESSON | `lesson:LSN-0039` | yes | `COMPLETE` | `PARTIAL` | Verify a test that writes to the operational database leaves production data behind |
| `LESSON-REQ-0039` | LESSON | `lesson:LSN-0040` | yes | `COMPLETE` | `PARTIAL` | Verify a control that judges sealed history only runs once a successor anchors it |
| `LESSON-REQ-0040` | LESSON | `lesson:LSN-0041` | yes | `COMPLETE` | `PARTIAL` | Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing |
| `LESSON-REQ-0041` | LESSON | `lesson:LSN-0042` | yes | `COMPLETE` | `PARTIAL` | Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone |
| `LESSON-REQ-0042` | LESSON | `lesson:LSN-0043` | yes | `COMPLETE` | `PARTIAL` | Verify a log line is not evidence that another process is ready |
| `LESSON-REQ-0043` | LESSON | `lesson:LSN-0044` | yes | `COMPLETE` | `PARTIAL` | Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module |
| `LESSON-REQ-0044` | LESSON | `lesson:LSN-0045` | yes | `COMPLETE` | `PARTIAL` | Verify a counted test suite must declare its cases statically, because the denominator is read from the source |
| `LESSON-REQ-0045` | LESSON | `lesson:LSN-0046` | yes | `COMPLETE` | `PARTIAL` | Verify a timeout that cancels the task it runs in leaves nothing able to record what happened |
| `LESSON-REQ-0046` | LESSON | `lesson:LSN-0047` | yes | `COMPLETE` | `PARTIAL` | Verify a refusal that misnames the defect spends the only repair on the wrong correction |
| `LESSON-REQ-0047` | LESSON | `lesson:LSN-0048` | yes | `COMPLETE` | `PARTIAL` | Verify a state and the event that explains it, written in two commits, are written event first |
| `LESSON-REQ-0048` | LESSON | `lesson:LSN-0049` | yes | `COMPLETE` | `PARTIAL` | Verify a metric read the instant after the call that moved it is read before the scrape that carries it |
| `LESSON-REQ-0049` | LESSON | `lesson:LSN-0050` | yes | `COMPLETE` | `PARTIAL` | Verify a checkpoint sealed without naming its own tag cannot be validated from that tag |
| `LESSON-REQ-0050` | LESSON | `lesson:LSN-0051` | yes | `COMPLETE` | `PARTIAL` | Verify a payload one service bounds for another must be bounded as the receiver measures it |
| `LESSON-REQ-0051` | LESSON | `lesson:LSN-0052` | yes | `COMPLETE` | `PARTIAL` | Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both |
| `LESSON-REQ-0052` | LESSON | `lesson:LSN-0053` | yes | `COMPLETE` | `PARTIAL` | Verify a process sweep that reads what a forking process holds waits on the processes it has to kill |
| `LESSON-REQ-0053` | LESSON | `lesson:LSN-0054` | no | `COMPLETE` | `PARTIAL` | Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote |
| `LESSON-REQ-0054` | LESSON | `lesson:LSN-0055` | yes | `COMPLETE` | `PARTIAL` | Verify a contract a model must follow has to reach the model, rendered from the definition the parser enforces |
| `LESSON-REQ-0055` | LESSON | `lesson:LSN-0056` | yes | `COMPLETE` | `PARTIAL` | Verify a result is accepted only from the executor that owns the request, decided when the request is created |
| `LESSON-REQ-0056` | LESSON | `lesson:LSN-0057` | yes | `COMPLETE` | `PARTIAL` | Verify a pinned lock can become unsafe without changing, so advisory state is live evidence |
| `LESSON-REQ-0057` | LESSON | `lesson:LSN-0058` | yes | `COMPLETE` | `PARTIAL` | Verify container health does not prove Docker Desktop host-port forwarding |
| `LESSON-REQ-0058` | LESSON | `lesson:LSN-0059` | yes | `COMPLETE` | `PARTIAL` | Verify a lesson exclusion must declare the scope it excludes |
| `LESSON-REQ-0059` | LESSON | `lesson:LSN-0060` | yes | `COMPLETE` | `PARTIAL` | Verify parent and child facts without an ORM relationship require an explicit flush boundary |
| `LESSON-REQ-0060` | LESSON | `lesson:LSN-0061` | yes | `COMPLETE` | `PARTIAL` | Verify cancellation completion must not bypass cleanup acknowledgement |
| `LESSON-REQ-0061` | LESSON | `lesson:LSN-0062` | yes | `COMPLETE` | `PARTIAL` | Verify provenance digests are a set even when their sources are distinct |
| `LESSON-REQ-0062` | LESSON | `lesson:LSN-0063` | yes | `COMPLETE` | `PARTIAL` | Verify an identity shared across services must satisfy the strictest persistence type and remain stable |
| `LESSON-REQ-0063` | LESSON | `lesson:LSN-0064` | yes | `COMPLETE` | `PARTIAL` | Verify a shared execution resource needs an explicit exclusive owner for every owning domain |
| `LESSON-REQ-0064` | LESSON | `lesson:LSN-0065` | yes | `COMPLETE` | `PARTIAL` | Verify a shared execution identifier must not be written into a foreign key owned by another domain |
| `LESSON-REQ-0065` | LESSON | `lesson:LSN-0066` | yes | `COMPLETE` | `PARTIAL` | Verify immutable content identity excludes observation time and the first observer |
| `LESSON-REQ-0066` | LESSON | `lesson:LSN-0067` | yes | `COMPLETE` | `PARTIAL` | Verify cancellation semantics must survive orchestration-library exception wrapping |
| `LESSON-REQ-0067` | LESSON | `lesson:LSN-0068` | yes | `COMPLETE` | `PARTIAL` | Verify a bounded parser must apply each content limit only to content it interprets |
| `LESSON-REQ-0068` | LESSON | `lesson:LSN-0069` | yes | `COMPLETE` | `PARTIAL` | Verify a polyglot plan binds each check to both its project root and its toolchain |
| `LESSON-REQ-0069` | LESSON | `lesson:LSN-0070` | yes | `COMPLETE` | `PARTIAL` | Verify project discovery must separate deployable roots, nested fixtures and check applicability |
| `LESSON-REQ-0070` | LESSON | `lesson:LSN-0071` | yes | `COMPLETE` | `PARTIAL` | Verify every quality image must provision snapshots on its oldest runtime and prepare each isolated check |
| `LESSON-REQ-0071` | LESSON | `lesson:LSN-0072` | yes | `COMPLETE` | `PARTIAL` | Verify secret findings and reviewed false positives must share one policy-owned taxonomy |
| `LESSON-REQ-0072` | LESSON | `lesson:LSN-0073` | yes | `COMPLETE` | `PARTIAL` | Verify the canonical lint denominator must cover every detected project root |
| `LESSON-REQ-0073` | LESSON | `lesson:LSN-0074` | yes | `COMPLETE` | `PARTIAL` | Verify an importable source tree is not an installed or repository-configured test environment |
| `LESSON-REQ-0074` | LESSON | `lesson:LSN-0075` | yes | `COMPLETE` | `PARTIAL` | Verify offline package installation requires its build backend inside the quality image |
| `LESSON-REQ-0075` | LESSON | `lesson:LSN-0076` | yes | `COMPLETE` | `PARTIAL` | Verify projected nested configuration requires an explicit monorepo root |
| `LESSON-REQ-0076` | LESSON | `lesson:LSN-0077` | yes | `COMPLETE` | `PARTIAL` | Verify harness wait bounds must reflect workload size without changing product deadlines |
| `LESSON-REQ-0077` | LESSON | `lesson:LSN-0078` | yes | `COMPLETE` | `PARTIAL` | Verify evidence recorders must resolve caller-supplied commit references before execution |
| `LESSON-REQ-0078` | LESSON | `lesson:LSN-0079` | yes | `COMPLETE` | `PARTIAL` | Verify test discovery and the unit runner must cover the same project scope |
| `LESSON-REQ-0079` | LESSON | `lesson:LSN-0080` | yes | `COMPLETE` | `PARTIAL` | Verify a failed verification stage must not leave an older PASS report addressable |
| `LESSON-REQ-0080` | LESSON | `lesson:LSN-0081` | yes | `COMPLETE` | `PARTIAL` | Verify canonical requirement evidence must name a test the repository actually discovers |
| `LESSON-REQ-0081` | LESSON | `lesson:LSN-0082` | yes | `COMPLETE` | `PARTIAL` | Verify engineering memory cannot depend on an ephemeral generated report |
| `LESSON-REQ-0082` | LESSON | `lesson:LSN-0083` | yes | `COMPLETE` | `PARTIAL` | Verify a command that decodes captured UTF-8 must also configure the stream that re-emits it |
| `LESSON-REQ-0083` | LESSON | `lesson:LSN-0084` | yes | `COMPLETE` | `PARTIAL` | Verify a historical Gate documentation test must derive the current entry-point state |
| `LESSON-REQ-0084` | LESSON | `lesson:LSN-0085` | yes | `COMPLETE` | `PARTIAL` | Verify a source-based control must assert syntax semantics rather than formatter layout |
| `LESSON-REQ-0085` | LESSON | `lesson:LSN-0086` | yes | `COMPLETE` | `PARTIAL` | Verify a subprocess assertion must preserve the exit code when both streams are empty |
| `LESSON-REQ-0086` | LESSON | `lesson:LSN-0087` | yes | `COMPLETE` | `PARTIAL` | Verify a rehearsal worker must register every workflow activity boundary |
| `LESSON-REQ-0087` | LESSON | `lesson:LSN-0088` | yes | `COMPLETE` | `PARTIAL` | Verify a test inside a built image can consume only inputs copied into that image |
| `LESSON-REQ-0088` | LESSON | `lesson:LSN-0089` | yes | `COMPLETE` | `PARTIAL` | Verify domain not-applicability and operational failure need distinct orchestration outcomes |
| `LESSON-REQ-0089` | LESSON | `lesson:LSN-0090` | yes | `COMPLETE` | `PARTIAL` | Verify a clean-clone control must use only versioned configuration inputs |
| `LESSON-REQ-0090` | LESSON | `lesson:LSN-0091` | yes | `COMPLETE` | `PARTIAL` | Verify secret detection must run on the exact bytes at the durable evidence boundary |
| `LESSON-REQ-0091` | LESSON | `lesson:LSN-0092` | yes | `COMPLETE` | `PARTIAL` | Verify canonical audit parsers must consume every bounded sealed report rendering |
| `LESSON-REQ-0092` | LESSON | `lesson:LSN-0093` | yes | `COMPLETE` | `PARTIAL` | Verify disposable control repositories must carry every imported repository package |
| `LESSON-REQ-0093` | LESSON | `lesson:LSN-0094` | yes | `COMPLETE` | `PARTIAL` | Verify a review bundle must include unchanged canonical artifact categories |
| `LESSON-REQ-0094` | LESSON | `lesson:LSN-0095` | yes | `COMPLETE` | `PARTIAL` | Verify a complete verifier must own its Compose runtime by checkout |
| `LESSON-REQ-0095` | LESSON | `lesson:LSN-0096` | yes | `COMPLETE` | `PARTIAL` | Verify evidence publishers must consume the producer's canonical result schema |
| `LESSON-REQ-0096` | LESSON | `lesson:LSN-0097` | yes | `COMPLETE` | `PARTIAL` | Verify a review-bundle declaration must bind an immutable reconstruction subject |
| `LESSON-REQ-0097` | LESSON | `lesson:LSN-0098` | yes | `COMPLETE` | `PARTIAL` | Verify accepted cancellation must be enforced from durable state across activity boundaries |
| `LESSON-REQ-0098` | LESSON | `lesson:LSN-0099` | yes | `COMPLETE` | `PARTIAL` | Verify a refused subject is an attempted input, not executed commit evidence |
| `LESSON-REQ-0099` | LESSON | `lesson:LSN-0100` | yes | `COMPLETE` | `PARTIAL` | Verify pre-seal detached validation must bind the explicit subject namespace |
| `LESSON-REQ-0100` | LESSON | `lesson:LSN-0101` | yes | `COMPLETE` | `PARTIAL` | Verify a structural record and its canonical index are one atomic change |
| `LESSON-REQ-0101` | LESSON | `lesson:LSN-0102` | yes | `COMPLETE` | `PARTIAL` | Verify assurance denominators must derive category counts from the current source set |
| `LESSON-REQ-0102` | LESSON | `lesson:LSN-0103` | yes | `COMPLETE` | `PARTIAL` | Verify adversarial fixtures must hash the complete validated contract |
| `LESSON-REQ-0103` | LESSON | `lesson:LSN-0104` | yes | `COMPLETE` | `PARTIAL` | Verify intermediate closure and independent validation must have unambiguous contracts |
| `LESSON-REQ-0104` | LESSON | `lesson:LSN-0105` | yes | `COMPLETE` | `PARTIAL` | Verify new behavioral tests must satisfy the unchanged source-quality contract |
| `LESSON-REQ-0105` | LESSON | `lesson:LSN-0106` | yes | `COMPLETE` | `PARTIAL` | Verify a security repair must execute at the causal output boundary, not a similarly shaped branch |
| `LESSON-REQ-0106` | LESSON | `lesson:LSN-0107` | yes | `COMPLETE` | `PARTIAL` | Verify an adversarial marker must satisfy the canonical detector before it can judge containment |
| `LESSON-REQ-0107` | LESSON | `lesson:LSN-0108` | yes | `COMPLETE` | `PARTIAL` | Verify evidence timestamp transport must preserve RFC3339 rather than a shell locale rendering |
| `LESSON-REQ-0108` | LESSON | `lesson:LSN-0109` | yes | `COMPLETE` | `PARTIAL` | Verify regression counts and evidence must exclude only policy-bound live input repositories |
| `LESSON-REQ-0109` | LESSON | `lesson:LSN-0110` | yes | `COMPLETE` | `PARTIAL` | Verify a timed-out live proof retains bounded diagnostics before owned cleanup |
| `LESSON-REQ-0110` | LESSON | `lesson:LSN-0111` | yes | `COMPLETE` | `PARTIAL` | Verify polling watcher cleanup must preserve completed checks and accepted cancellation |
| `LESSON-REQ-0111` | LESSON | `lesson:LSN-0112` | yes | `COMPLETE` | `PARTIAL` | Verify canonical scanner consumers must share transport decoding, not only patterns |
| `LESSON-REQ-0112` | LESSON | `lesson:LSN-0113` | yes | `COMPLETE` | `PARTIAL` | Verify stronger delivery controls must follow the immutable subject policy version |
| `LESSON-REQ-0113` | LESSON | `lesson:LSN-0114` | yes | `COMPLETE` | `PARTIAL` | Verify transport line metadata must not repeatedly scan the source prefix |
| `LESSON-REQ-0114` | LESSON | `lesson:LSN-0115` | yes | `COMPLETE` | `PARTIAL` | Verify a failing full verifier retains every bounded case identifier beyond its output tail |
| `LESSON-REQ-0115` | LESSON | `lesson:LSN-0116` | yes | `COMPLETE` | `PARTIAL` | Verify a live resumability pointer is generated after Git boundaries, not committed into its own subject |
| `LESSON-REQ-0116` | LESSON | `lesson:LSN-0117` | yes | `COMPLETE` | `PARTIAL` | Verify an architecture rollup must not contradict the delivered capability described below it |
| `LESSON-REQ-0117` | LESSON | `lesson:LSN-0118` | yes | `COMPLETE` | `PARTIAL` | Verify post-response validation failures must preserve an accepted mutation's uncertain outcome |
| `LESSON-REQ-0118` | LESSON | `lesson:LSN-0119` | yes | `COMPLETE` | `PARTIAL` | Verify a clean publication scan does not replace the stricter checkpoint secret scan |
| `LESSON-REQ-0119` | LESSON | `lesson:LSN-0120` | yes | `COMPLETE` | `PARTIAL` | Verify native installation proofs must resolve the installed CLI entrypoint |
| `LESSON-REQ-0120` | LESSON | `lesson:LSN-0121` | yes | `COMPLETE` | `PARTIAL` | Verify standard-library host probes must not initialize application dependency graphs |
| `LESSON-REQ-0121` | LESSON | `lesson:LSN-0122` | yes | `COMPLETE` | `PARTIAL` | Verify engine-allocated host ports must be rediscovered after container restart |
| `LESSON-REQ-0122` | LESSON | `lesson:LSN-0123` | yes | `COMPLETE` | `PARTIAL` | Verify consent binds workspace identity, not an uncanonicalized path spelling |
| `LESSON-REQ-0123` | LESSON | `lesson:LSN-0124` | yes | `COMPLETE` | `PARTIAL` | Verify durable editor recovery must not use an in-memory test host |
| `LESSON-REQ-0124` | LESSON | `lesson:LSN-0125` | yes | `COMPLETE` | `PARTIAL` | Verify native parent exit is not proof of process and profile cleanup |
| `LESSON-REQ-0125` | LESSON | `lesson:LSN-0126` | yes | `COMPLETE` | `PARTIAL` | Verify known authentication material is not domain or presentation data |
| `LESSON-REQ-0126` | LESSON | `lesson:LSN-0127` | yes | `COMPLETE` | `PARTIAL` | Verify fresh runtime health does not initialize an operator-managed model catalog |
| `LESSON-REQ-0127` | LESSON | `lesson:LSN-0128` | yes | `COMPLETE` | `PARTIAL` | Verify adversarial premises must use the actual public contract |
| `LESSON-REQ-0128` | LESSON | `lesson:LSN-0129` | yes | `COMPLETE` | `PARTIAL` | Verify repeated cancellation must preserve an already cancelled terminal result |
| `LESSON-REQ-0129` | LESSON | `lesson:LSN-0130` | yes | `COMPLETE` | `PARTIAL` | Verify executable export line endings belong to the source and packaging contract |
| `LESSON-REQ-0130` | LESSON | `lesson:LSN-0131` | yes | `COMPLETE` | `PARTIAL` | Verify raw evidence digests require byte-preserving Git export, not text normalization |
| `LESSON-REQ-0131` | LESSON | `lesson:LSN-0132` | yes | `COMPLETE` | `PARTIAL` | Verify owned Git clones need read-only-aware cleanup, not native-profile lock retry |
| `LESSON-REQ-0132` | LESSON | `lesson:LSN-0133` | yes | `COMPLETE` | `PARTIAL` | Verify shared field names do not imply shared schema types |
| `LESSON-REQ-0133` | LESSON | `lesson:LSN-0134` | yes | `COMPLETE` | `PARTIAL` | Verify configuration classifiers consume decoded values, not dotenv quote syntax |
| `LESSON-REQ-0134` | LESSON | `lesson:LSN-0135` | yes | `COMPLETE` | `PARTIAL` | Verify capture producer evidence before fallible interpretation or owned cleanup |
| `LESSON-REQ-0135` | LESSON | `lesson:LSN-0136` | yes | `COMPLETE` | `PARTIAL` | Verify strict JSON validation loses transport context |
| `LESSON-REQ-0136` | LESSON | `lesson:LSN-0137` | yes | `COMPLETE` | `PARTIAL` | Verify sQL text interprets inline JSON colons as bindings |
| `LESSON-REQ-0137` | LESSON | `lesson:LSN-0138` | yes | `COMPLETE` | `PARTIAL` | Verify secret projection distinguishes public identities from authorization secrets |
| `LESSON-REQ-0138` | LESSON | `lesson:LSN-0139` | yes | `COMPLETE` | `PARTIAL` | Verify privacy projection begins in the source query |
| `LESSON-REQ-0139` | LESSON | `lesson:LSN-0140` | yes | `COMPLETE` | `PARTIAL` | Verify summaries preserve canonical continuation structure |
| `LESSON-REQ-0140` | LESSON | `lesson:LSN-0141` | yes | `COMPLETE` | `PARTIAL` | Verify preflight checks honor every declared applicability dimension |
| `LESSON-REQ-0141` | LESSON | `lesson:LSN-0142` | yes | `COMPLETE` | `PARTIAL` | Verify local Engine recovery keeps transport and cleanup scoped |
| `LESSON-REQ-0142` | LESSON | `lesson:LSN-0143` | yes | `COMPLETE` | `PARTIAL` | Verify management recovery is not complete runtime capability |
| `LESSON-REQ-0143` | LESSON | `lesson:LSN-0144` | yes | `NOT_STARTED` | `PARTIAL` | Verify raw archived observations retain original context rather than becoming active relocated documents |

## Evidence

### REQ-0001 - canonical:GATE-6#1.1

- Source reference: docs/GATE-6-CHECKLIST.md row 1.1
- Description: A separately authorized Gate 6 checkpoint starts only after valid sealed Gate 5 internal closure, preserves every predecessor and anchors the newest seal.
- Implementation: `file:docs/checkpoints/GATE-6-CP-0001/AUTHORIZATION.md`, `file:.iacode/anchors/checkpoint-chain.json`
- Test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate0_foundation.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate0_foundation.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/DEVELOPMENT-CONTRACT.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0002 - canonical:GATE-6#1.2

- Source reference: docs/GATE-6-CHECKLIST.md row 1.2
- Description: The canonical checklist and registry agree exactly, and all lesson/audit-derived requirements are extracted before baseline and implementation.
- Implementation: `file:docs/GATE-6-CHECKLIST.md`, `file:.iacode/policies/canonical-requirements.json`, `file:scripts/development-ledger/derive_requirements.py`
- Test: `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0003 - canonical:GATE-6#1.3

- Source reference: docs/GATE-6-CHECKLIST.md row 1.3
- Description: Structural ADRs define the experience boundary, authoritative storage, schema evolution, access, rights and retention before behavior changes.
- Implementation: `file:docs/adr/ADR-0050-experiences-are-source-bound-consented-facts.md`, `file:docs/adr/ADR-0051-retention-tombstones-prevent-experience-resurrection.md`
- Test: `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0004 - canonical:GATE-6#1.4

- Source reference: docs/GATE-6-CHECKLIST.md row 1.4
- Description: Experience logic depends on shared contracts and declared ports, not provider adapters, host execution, a container engine or a later knowledge/training service.
- Implementation: `file:services/experience/src/iacode_experience/domain.py`, `file:packages/contracts/src/iacode_contracts/experience.py`
- Test: `file:tests/test_gate6_experience.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0005 - canonical:GATE-6#1.5

- Source reference: docs/GATE-6-CHECKLIST.md row 1.5
- Description: Every inherited mandatory quality gate and counted suite remains; experience-specific build/tests are mandatory and canonically registered.
- Implementation: `file:.iacode/policies/quality-gates.json`, `file:.iacode/policies/test-suites.json`, `file:scripts/iacode/gates/experience_tests.py`
- Test: `file:tests/test_gate6_experience.py`, `file:tests/test_test_suite_input_repositories.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:tests/test_test_suite_input_repositories.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0006 - canonical:GATE-6#1.6

- Source reference: docs/GATE-6-CHECKLIST.md row 1.6
- Description: Gate 7 and later reservations remain unimplemented; experience persistence neither grants RAG/training authority nor changes independent milestone verdicts.
- Implementation: `file:.iacode/policies/gate-scope.json`, `file:docs/checkpoints/GATE-6-CP-0001/AUTHORIZATION.md`
- Test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate0_foundation.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate0_foundation.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/MASTER-PLAN.md`, `file:docs/MILESTONE-VALIDATION.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0007 - canonical:GATE-6#2.1

- Source reference: docs/GATE-6-CHECKLIST.md row 2.1
- Description: A versioned, closed experience schema defines task, environment, provider/model/effort observations, repository/base identity, trajectory summary, actions, tools, commands, files, attempts, failures, corrections, tests, quality, reviews, final result, provenance and eligibility.
- Implementation: `file:packages/contracts/src/iacode_contracts/experience.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:.iacode/schemas/experience.schema.json`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0008 - canonical:GATE-6#2.2

- Source reference: docs/GATE-6-CHECKLIST.md row 2.2
- Description: Experience content consists only of bounded observable facts and source references; prompts, raw provider responses, credentials, hidden reasoning and arbitrary transcript fields are excluded.
- Implementation: `file:services/experience/src/iacode_experience/domain.py`, `file:packages/contracts/src/iacode_contracts/experience.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:apps/api/src/iacode_api/routes/experiences.py`, `file:apps/api/src/iacode_api/experience/runtime.py`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0009 - canonical:GATE-6#2.3

- Source reference: docs/GATE-6-CHECKLIST.md row 2.3
- Description: Unobserved provider/model/effort/review information remains explicitly unknown or absent, never fabricated from configuration, a plan or an implementer assertion.
- Implementation: `file:packages/contracts/src/iacode_contracts/experience.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:.iacode/schemas/experience.schema.json`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0010 - canonical:GATE-6#2.4

- Source reference: docs/GATE-6-CHECKLIST.md row 2.4
- Description: Identities, timestamps, enums, numeric types, UTF-8, nesting, collection lengths and total encoded bytes are strictly bounded; unknown fields and ambiguous JSON fail closed.
- Implementation: `file:services/experience/src/iacode_experience/domain.py`, `file:packages/contracts/src/iacode_contracts/experience.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:apps/api/src/iacode_api/routes/experiences.py`, `file:apps/api/src/iacode_api/experience/runtime.py`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0011 - canonical:GATE-6#2.5

- Source reference: docs/GATE-6-CHECKLIST.md row 2.5
- Description: Only authorized completed source runs and their matching immutable quality/snapshot evidence may support capture; running, missing, cross-project or mismatched inputs are refused.
- Implementation: `file:apps/api/src/iacode_api/experience/sources.py`, `file:packages/contracts/src/iacode_contracts/experience.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0012 - canonical:GATE-6#2.6

- Source reference: docs/GATE-6-CHECKLIST.md row 2.6
- Description: Source facts, hashes, parent identities and failure outcomes remain traceable; no caller may submit a quality verdict or replace trusted source facts.
- Implementation: `file:apps/api/src/iacode_api/experience/sources.py`, `file:packages/contracts/src/iacode_contracts/experience.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0013 - canonical:GATE-6#3.1

- Source reference: docs/GATE-6-CHECKLIST.md row 3.1
- Description: Every stored experience requires explicit informed storage consent for the exact project and source; omission, rejection or a conflicting retry causes no capture.
- Implementation: `file:apps/api/src/iacode_api/routes/experiences.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:apps/api/src/iacode_api/experience/store.py`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0014 - canonical:GATE-6#3.2

- Source reference: docs/GATE-6-CHECKLIST.md row 3.2
- Description: Provenance records source type, provider/model when observed, ownership, license, all four storage/reuse permissions, evidence and limits.
- Implementation: `file:packages/contracts/src/iacode_contracts/experience.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0015 - canonical:GATE-6#3.3

- Source reference: docs/GATE-6-CHECKLIST.md row 3.3
- Description: Unknown ownership/license or unproven permissions cannot yield a positive RAG, training or distillation grant; raw external output never becomes trainable by storage.
- Implementation: `file:packages/contracts/src/iacode_contracts/experience.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0016 - canonical:GATE-6#3.4

- Source reference: docs/GATE-6-CHECKLIST.md row 3.4
- Description: Effective permissions cannot exceed any contributing source permission, and provenance/rights remain bound to the exact stored content and export.
- Implementation: `file:packages/contracts/src/iacode_contracts/experience.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0017 - canonical:GATE-6#3.5

- Source reference: docs/GATE-6-CHECKLIST.md row 3.5
- Description: Canonical credential detection scans complete exact normalized content before durable effects and again before delivery; matches and scanner failure produce sanitized refusal.
- Implementation: `file:services/experience/src/iacode_experience/domain.py`, `file:packages/contracts/src/iacode_contracts/experience.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:apps/api/src/iacode_api/routes/experiences.py`, `file:apps/api/src/iacode_api/experience/runtime.py`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0018 - canonical:GATE-6#3.6

- Source reference: docs/GATE-6-CHECKLIST.md row 3.6
- Description: Known runtime authorization material and forbidden private/transcript fields cannot enter content, metadata, summaries, diagnostics, audit payloads, errors or exports.
- Implementation: `file:services/experience/src/iacode_experience/domain.py`, `file:packages/contracts/src/iacode_contracts/experience.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:apps/api/src/iacode_api/routes/experiences.py`, `file:apps/api/src/iacode_api/experience/runtime.py`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0019 - canonical:GATE-6#3.7

- Source reference: docs/GATE-6-CHECKLIST.md row 3.7
- Description: Denied and unknown reuse requests fail closed without data disclosure; no endpoint performs knowledge retrieval, training or distillation.
- Implementation: `file:apps/api/src/iacode_api/routes/experiences.py`, `file:packages/contracts/src/iacode_contracts/experience.py`
- Test: `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0020 - canonical:GATE-6#4.1

- Source reference: docs/GATE-6-CHECKLIST.md row 4.1
- Description: Alembic evolves the existing experiences persistence contract rather than introducing an unrelated shadow store; ORM and actual PostgreSQL schema agree.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`, `file:apps/api/migrations/versions/0007_experience_store.py`, `file:apps/api/src/iacode_api/experience/store.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/integration/test_migrations.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/integration/test_migrations.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0021 - canonical:GATE-6#4.2

- Source reference: docs/GATE-6-CHECKLIST.md row 4.2
- Description: Schema migration preserves identity, rights and lineage of legacy rows without silently treating unvalidated payloads as current valid experiences.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`, `file:apps/api/migrations/versions/0007_experience_store.py`, `file:apps/api/src/iacode_api/experience/store.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/integration/test_migrations.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/integration/test_migrations.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0022 - canonical:GATE-6#4.3

- Source reference: docs/GATE-6-CHECKLIST.md row 4.3
- Description: Content, schema version, provenance and digest form one immutable captured fact; unauthorized updates and direct persistence corruption cannot produce a valid delivered record.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`, `file:apps/api/migrations/versions/0007_experience_store.py`, `file:apps/api/src/iacode_api/experience/store.py`, `file:services/experience/src/iacode_experience/domain.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0023 - canonical:GATE-6#4.4

- Source reference: docs/GATE-6-CHECKLIST.md row 4.4
- Description: Capture and its bounded audit fact commit atomically; failed validation, unavailable dependencies and rolled-back writes leave no partial experience.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`, `file:apps/api/migrations/versions/0007_experience_store.py`, `file:apps/api/src/iacode_api/experience/store.py`, `file:services/experience/src/iacode_experience/domain.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0024 - canonical:GATE-6#4.5

- Source reference: docs/GATE-6-CHECKLIST.md row 4.5
- Description: Stable request identity makes accepted-response-loss and concurrent retries idempotent; conflicting content is refused rather than silently overwritten.
- Implementation: `file:apps/api/src/iacode_api/experience/store.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:scripts/iacode/scenarios/experience_store_e2e.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `file:tests/test_gate6_experience.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0025 - canonical:GATE-6#4.6

- Source reference: docs/GATE-6-CHECKLIST.md row 4.6
- Description: New request identifiers cannot silently resurrect revoked/deleted/expired content or reset its retention clock; repeated mutations preserve truthful terminal state.
- Implementation: `file:apps/api/src/iacode_api/experience/store.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:scripts/iacode/scenarios/experience_store_e2e.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `file:tests/test_gate6_experience.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0026 - canonical:GATE-6#5.1

- Source reference: docs/GATE-6-CHECKLIST.md row 5.1
- Description: All experience operations require actual configured runtime authentication; no unauthenticated legacy alternate path reaches experience data or effects.
- Implementation: `file:apps/api/src/iacode_api/routes/experiences.py`, `file:apps/api/src/iacode_api/experience/runtime.py`, `file:apps/api/src/iacode_api/middleware/desktop_auth.py`
- Test: `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_desktop_api.py`
- Negative test: `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_desktop_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0027 - canonical:GATE-6#5.2

- Source reference: docs/GATE-6-CHECKLIST.md row 5.2
- Description: Project/source identity scopes every read, list, export, withdrawal and deletion; a mismatched project cannot disclose or modify an experience.
- Implementation: `file:apps/api/src/iacode_api/routes/experiences.py`, `file:apps/api/src/iacode_api/experience/store.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:scripts/iacode/scenarios/experience_store_e2e.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0028 - canonical:GATE-6#5.3

- Source reference: docs/GATE-6-CHECKLIST.md row 5.3
- Description: Capture, inspect, list and machine-readable export round-trip actual persisted content and hashes, without deriving success from an in-memory fake.
- Implementation: `file:apps/api/src/iacode_api/routes/experiences.py`, `file:apps/api/src/iacode_api/experience/store.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:scripts/iacode/scenarios/experience_store_e2e.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0029 - canonical:GATE-6#5.4

- Source reference: docs/GATE-6-CHECKLIST.md row 5.4
- Description: Listing is deterministically ordered, bounded and resumable with a validated project-bound cursor; invalid cursors and enumeration cannot bypass access/retention.
- Implementation: `file:apps/api/src/iacode_api/routes/experiences.py`, `file:apps/api/src/iacode_api/experience/store.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:scripts/iacode/scenarios/experience_store_e2e.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0030 - canonical:GATE-6#5.5

- Source reference: docs/GATE-6-CHECKLIST.md row 5.5
- Description: Errors use stable bounded reason codes and observable correlation without echoing rejected content, credentials, database details or exception strings.
- Implementation: `file:apps/api/src/iacode_api/routes/experiences.py`, `file:packages/telemetry/src/iacode_telemetry/logging.py`, `file:apps/api/src/iacode_api/middleware/correlation.py`
- Test: `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0031 - canonical:GATE-6#5.6

- Source reference: docs/GATE-6-CHECKLIST.md row 5.6
- Description: Requests and responses preserve the existing authenticated transport and source boundaries; clients and agents cannot gain host execution or verdict authority.
- Implementation: `file:apps/api/src/iacode_api/routes/experiences.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:packages/contracts/src/iacode_contracts/desktop_protocol.json`
- Test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/unit/test_desktop_api.py`, `file:apps/cli/tests/core.test.cjs`
- Negative test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/unit/test_desktop_api.py`, `file:apps/cli/tests/core.test.cjs`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0032 - canonical:GATE-6#6.1

- Source reference: docs/GATE-6-CHECKLIST.md row 6.1
- Description: A versioned consumed policy sets finite retention defaults/maxima, bounded processing and explicit operational limits; a caller cannot widen canonical ceilings.
- Implementation: `file:.iacode/policies/experience-policy.json`, `file:services/experience/src/iacode_experience/domain.py`
- Test: `file:tests/test_gate6_experience.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0033 - canonical:GATE-6#6.2

- Source reference: docs/GATE-6-CHECKLIST.md row 6.2
- Description: Expired or storage-withdrawn content is immediately unavailable to reads, listings, exports and reuse, independently of the next physical sweep.
- Implementation: `file:services/experience/src/iacode_experience/domain.py`, `file:apps/api/src/iacode_api/experience/store.py`, `file:apps/api/src/iacode_api/routes/experiences.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0034 - canonical:GATE-6#6.3

- Source reference: docs/GATE-6-CHECKLIST.md row 6.3
- Description: Owned automatic retention processing physically removes expired primary payloads in bounded atomic batches and records only minimal non-sensitive deletion evidence.
- Implementation: `file:apps/api/src/iacode_api/experience/runtime.py`, `file:apps/api/src/iacode_api/experience/store.py`, `file:apps/api/migrations/versions/0007_experience_store.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0035 - canonical:GATE-6#6.4

- Source reference: docs/GATE-6-CHECKLIST.md row 6.4
- Description: Explicit withdrawal/deletion is authenticated, project-bound and idempotent; it cannot delete source runs, quality evidence or unrelated project data.
- Implementation: `file:services/experience/src/iacode_experience/domain.py`, `file:apps/api/src/iacode_api/experience/store.py`, `file:apps/api/src/iacode_api/routes/experiences.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0036 - canonical:GATE-6#6.5

- Source reference: docs/GATE-6-CHECKLIST.md row 6.5
- Description: Runtime restart preserves records, idempotency and rights; corrupt schema/content/provenance or unavailable source evidence fails closed after recovery.
- Implementation: `file:apps/api/src/iacode_api/experience/store.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:apps/api/src/iacode_api/experience/sources.py`, `file:scripts/iacode/scenarios/experience_store_e2e.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0037 - canonical:GATE-6#6.6

- Source reference: docs/GATE-6-CHECKLIST.md row 6.6
- Description: Background tasks and dependency failures have explicit bounded lifecycle, observable errors and owned shutdown; storage/backup deletion limits and safe restore procedure are documented.
- Implementation: `file:apps/api/src/iacode_api/experience/runtime.py`, `file:apps/api/src/iacode_api/routes/experiences.py`, `file:docs/runbooks/experience-store.md`
- Test: `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0038 - canonical:GATE-6#7.1

- Source reference: docs/GATE-6-CHECKLIST.md row 7.1
- Description: Actual fresh-stack acceptance captures a real completed governed task and quality result with observed provider/tool lineage and persisted rights, then reads/lists/exports matching bytes.
- Implementation: `file:scripts/iacode/scenarios/experience_store_e2e.py`, `file:scripts/iacode/scenarios/experience_source_adversary.py`, `file:scripts/iacode/desktop_test_support.py`
- Test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0039 - canonical:GATE-6#7.2

- Source reference: docs/GATE-6-CHECKLIST.md row 7.2
- Description: Live acceptance proves restart, stable retry, retention expiry, deletion and unchanged source resources through the actual API and database.
- Implementation: `file:scripts/iacode/scenarios/experience_store_e2e.py`, `file:scripts/iacode/scenarios/experience_source_adversary.py`, `file:scripts/iacode/desktop_test_support.py`
- Test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0040 - canonical:GATE-6#7.3

- Source reference: docs/GATE-6-CHECKLIST.md row 7.3
- Description: Live adverse controls attack authentication, project mismatch, denied reuse, secret/private ingress, forged facts, corruption and resurrection beside a valid clean control.
- Implementation: `file:scripts/iacode/scenarios/experience_store_e2e.py`, `file:scripts/iacode/scenarios/experience_source_adversary.py`, `file:scripts/iacode/desktop_test_support.py`
- Test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0041 - canonical:GATE-6#7.4

- Source reference: docs/GATE-6-CHECKLIST.md row 7.4
- Description: New integration tests own their runtime namespace, fixtures and temporary resources; operational identities/source bytes stay unchanged and cleanup is observed.
- Implementation: `file:scripts/iacode/scenarios/experience_store_e2e.py`, `file:scripts/iacode/scenarios/experience_source_adversary.py`, `file:scripts/iacode/desktop_test_support.py`
- Test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/unit/test_experience_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0042 - canonical:GATE-6#7.5

- Source reference: docs/GATE-6-CHECKLIST.md row 7.5
- Description: Every mandatory new experience scenario joins the full non-fast verifier without dropping inherited stages; failed reruns cannot reuse stale PASS artifacts.
- Implementation: `file:scripts/iacode/verify.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/run_full_verification.py`, `file:.gitattributes`
- Test: `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0043 - canonical:GATE-6#7.6

- Source reference: docs/GATE-6-CHECKLIST.md row 7.6
- Description: Functional reports bind the actual immutable subject, exact source fingerprint and process outcomes; available safe producer bytes survive fallible postprocessing/cleanup.
- Implementation: `file:scripts/iacode/verify.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/run_full_verification.py`, `file:.gitattributes`
- Test: `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0044 - canonical:GATE-6#8.1

- Source reference: docs/GATE-6-CHECKLIST.md row 8.1
- Description: Runbooks document capture/consent, authentication, all endpoints, schema/lineage/rights, retention, withdrawal, recovery, limits and troubleshooting without exposing configuration values.
- Implementation: `file:docs/runbooks/experience-store.md`, `file:services/experience/README.md`, `file:docs/ARCHITECTURE.md`
- Test: `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0045 - canonical:GATE-6#8.2

- Source reference: docs/GATE-6-CHECKLIST.md row 8.2
- Description: All selected lessons and requirements have truthful requirement-specific implementation, executed positive/adverse tests and resolvable evidence.
- Implementation: `file:scripts/development-ledger/derive_requirements.py`, `file:scripts/development-ledger/check_completeness.py`, `file:scripts/development-ledger/derive_counts.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/declare_inventory.py`
- Test: `file:tests/test_development_ledger.py`, `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_development_ledger.py`, `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/DEVELOPMENT-CONTRACT.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0046 - canonical:GATE-6#8.3

- Source reference: docs/GATE-6-CHECKLIST.md row 8.3
- Description: Full current test/quality verification, every mandatory Green Keeper gate, total completeness, fresh internal Red Team/null control and complete clean-clone mirror pass in order against unchanged source.
- Implementation: `file:scripts/iacode/verify.py`, `file:scripts/development-ledger/green_keeper.py`, `file:scripts/development-ledger/m0_mirror_audit.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/run_full_verification.py`
- Test: `file:tests/test_development_ledger.py`, `file:tests/test_gate4_quality_engine.py`, `file:tests/test_gate5_clients.py`, `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_development_ledger.py`, `file:tests/test_gate4_quality_engine.py`, `file:tests/test_gate5_clients.py`, `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0047 - canonical:GATE-6#8.4

- Source reference: docs/GATE-6-CHECKLIST.md row 8.4
- Description: Current tooling validates every sealed predecessor; dynamic/current scope and fixed historical fixtures retain distinct owners and successor transitions remain valid.
- Implementation: `file:scripts/iacode/verify.py`, `file:scripts/development-ledger/green_keeper.py`, `file:scripts/development-ledger/m0_mirror_audit.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/run_full_verification.py`
- Test: `file:tests/test_development_ledger.py`, `file:tests/test_gate4_quality_engine.py`, `file:tests/test_gate5_clients.py`, `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_development_ledger.py`, `file:tests/test_gate4_quality_engine.py`, `file:tests/test_gate5_clients.py`, `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/runbooks/experience-store.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0048 - canonical:GATE-6#8.5

- Source reference: docs/GATE-6-CHECKLIST.md row 8.5
- Description: Every changed path is declared before finalization; counts, command inputs, provenance, risks, retrospective and resumable handoff remain truthful.
- Implementation: `file:scripts/development-ledger/derive_requirements.py`, `file:scripts/development-ledger/check_completeness.py`, `file:scripts/development-ledger/derive_counts.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/declare_inventory.py`, `file:.iacode/memory/retrospectives/GATE-6-CP-0001.md`
- Test: `file:tests/test_development_ledger.py`, `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_development_ledger.py`, `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/DEVELOPMENT-CONTRACT.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0049 - canonical:GATE-6#8.6

- Source reference: docs/GATE-6-CHECKLIST.md row 8.6
- Description: Canonical finalization, a Gate 6-only commit, post-commit seal and immutable archive reconstruction actually succeed; sealed history is never rewritten.
- Implementation: `file:scripts/development-ledger/seal_checkpoint.py`, `file:scripts/development-ledger/review_bundle.py`
- Test: `file:tests/test_development_ledger.py`, `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_development_ledger.py`, `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0050 - canonical:GATE-6#8.7

- Source reference: docs/GATE-6-CHECKLIST.md row 8.7
- Description: Intermediate closure records only INTERNAL_GATE_PASS with no blockers; independent fields are justified NOT_REQUIRED here, M2 stays PENDING and second-tool validation stays PENDING_MANUAL.
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`, `file:docs/checkpoints/GATE-6-CP-0001/STATE.json`
- Test: `file:tests/test_gate4_quality_engine.py`, `file:tests/test_development_ledger.py`
- Negative test: `file:tests/test_gate4_quality_engine.py`, `file:tests/test_development_ledger.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/MILESTONE-VALIDATION.md`, `file:docs/adr/ADR-0037-intermediate-gates-use-internal-closure.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### REQ-0051 - canonical:GATE-6#8.8

- Source reference: docs/GATE-6-CHECKLIST.md row 8.8
- Description: Gate 7 is not started without separate explicit owner authorization and a valid sealed Gate 6 predecessor; independent audit is reserved for M2 closure.
- Implementation: `file:.iacode/policies/gate-scope.json`, `file:docs/checkpoints/GATE-6-CP-0001/AUTHORIZATION.md`
- Test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate0_foundation.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate0_foundation.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/MASTER-PLAN.md`, `file:docs/MILESTONE-VALIDATION.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/validate_serial_bookkeeping.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/run_checkpoint_validation.py`
- Test: `file:tests/test_gate6_experience.py`, `file:tests/test_in_progress_metadata.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:tests/test_in_progress_metadata.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: `file:.iacode/memory/POLICY.json`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/policies.py`, `file:.iacode/policies/test-suites.json`
- Test: `test:test_live_policy_requires_strict_internal_verdict_semantics`, `test:test_legacy_internal_red_team_fields_keep_their_subject_policy_semantics`, `test:test_every_sealed_checkpoint_validates_from_its_own_tag`, `test:TestSuiteInputRepositoriesTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0042-internal-verdict-semantics-follow-subject-policy.md`, `file:docs/adr/ADR-0043-collection-semantics-follow-subject-policy.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0013 - lesson:LSN-0013

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0013
- Description: Verify an installed capability must be detected by resolved path, not by a bare command lookup
- Implementation: `file:scripts/development-ledger/review_bundle.py`, `file:scripts/development-ledger/seal_checkpoint.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/record_command.py`, `file:services/evaluator/src/iacode_evaluator/workflow.py`, `file:.iacode/schemas/checkpoint.schema.json`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_immutable_subject_rebuilds_are_byte_identical_and_exclude_only_the_sidecar`, `test:test_declared_digest_and_size_are_rebuilt_not_trusted`, `test:test_pending_declaration_is_allowed_only_before_handoff_or_inside_sealing`, `test:test_full_delivery_assurance_flow_reaches_ready_for_review`, `test:test_cancellation_is_rechecked_after_dispatch_before_activity_start`, `test:test_durable_cancelling_state_stops_an_active_sandbox_activity`, `test:test_a_signal_flag_set_before_handle_assignment_still_cancels_the_activity`, `test:test_accepted_cancellation_wins_over_a_racing_success_response`, `test:test_inputs_are_canonicalized_and_an_unknown_subject_is_refused`, `test:test_in_progress_symbolic_head_validates_from_its_matching_subject_tag`, `test:test_subject_tag_never_substitutes_for_a_sealed_checkpoint_tag`, `test:test_the_index_lists_every_record_with_its_title_and_status`, `test:test_a_record_missing_from_the_index_is_detected`, `test:test_gate_consistency_is_provisional_while_work_is_in_progress`, `test:test_green_keeper_declares_its_in_progress_evidence_dirty_before_validation`, `test:test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test:test_the_refresh_has_one_definition`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0009/BASELINE-BUNDLE-AUDIT.json`, `test:test_declared_digest_and_size_are_rebuilt_not_trusted`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:docs/adr/ADR-0035-review-bundles-bind-immutable-content.md`, `file:docs/adr/ADR-0036-pre-seal-validation-binds-an-explicit-subject.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/TOOL-CAPABILITIES.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: `file:scripts/development-ledger/lessons.py`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `file:tests/test_development_ledger.py`, `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_development_ledger.py`, `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: `file:scripts/development-ledger/record_command.py`, `file:scripts/development-ledger/green_keeper.py`
- Test: `test:CommandInputSnapshotTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMAND-INPUT-BINDING-QUALIFICATION.json`
- Documentation: `file:docs/adr/ADR-0044-process-recorders-bind-launch-inputs.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0024 - lesson:LSN-0024

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0024
- Description: Verify a control is finished only when its positive path has been executed, not only its refusals
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0025 - lesson:LSN-0025

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0025
- Description: Verify a generic guardrail derives repository state instead of naming today's checkpoint
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0026 - lesson:LSN-0026

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0026
- Description: Verify an adversarial battery without a null-mutation control proves nothing
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0027 - lesson:LSN-0027

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0027
- Description: Verify a lesson's prose may record a residual limit but may never contradict its status
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0028 - lesson:LSN-0028

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0028
- Description: Verify a configuration key that no code reads is a defect, not documentation
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0029 - lesson:LSN-0029

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0029
- Description: Verify a required protocol transition must never turn a mandatory gate red
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0030 - lesson:LSN-0031

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0030
- Description: Verify an empty applicable set is not a missing required set, and a control must tell them apart
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0031 - lesson:LSN-0032

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0031
- Description: Verify a control written while one Gate was the only Gate stops being a control when the next one starts
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0032 - lesson:LSN-0033

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0032
- Description: Verify a value bound in middleware is absent in the handlers that run outside it
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0033 - lesson:LSN-0034

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0033
- Description: Verify re-deriving what the framework already computed diverges from the framework
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0034 - lesson:LSN-0035

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0034
- Description: Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work
- Implementation: `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/capture_blocked_attempt.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/observe_restarted_engine.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/recover_owned_verification.py`, `file:scripts/development-ledger/ledger_common.py`
- Test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate0_foundation.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate0_foundation.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0035 - lesson:LSN-0036

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0035
- Description: Verify a gate that runs inside an image measures the image, not the source
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0036 - lesson:LSN-0037

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0036
- Description: Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves
- Implementation: `file:scripts/development-ledger/policies.py`, `file:tests/test_gate3_sandbox.py`
- Test: `file:tests/test_gate3_sandbox.py`, `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate3_sandbox.py`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0037 - lesson:LSN-0038

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0037
- Description: Verify two representations of one concept in one module disagree, and the safer one loses
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0038 - lesson:LSN-0039

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0038
- Description: Verify a test that writes to the operational database leaves production data behind
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0039 - lesson:LSN-0040

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0039
- Description: Verify a control that judges sealed history only runs once a successor anchors it
- Implementation: `file:scripts/development-ledger/ledger_common.py`, `file:scripts/development-ledger/record_command.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:.iacode/schemas/checkpoint.schema.json`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_git_metadata_is_local_even_though_git_check_ignore_does_not_classify_it`, `test:test_schema_3_3_refuses_a_digest_bound_git_metadata_input`, `test:test_schema_3_3_refuses_an_ignored_input_even_when_it_exists`, `test:test_the_recorder_excludes_git_metadata_and_refuses_it_when_explicit`, `test:test_a_nontransport_input_refusal_is_recomputed_from_its_precondition`, `test:test_a_fabricated_nontransport_input_refusal_is_rejected`, `test:test_the_first_transport_refusal_record_keeps_valid_legacy_classification`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0007/CP0006-REMOTE-TRANSPORT-BASELINE.json`, `file:docs/checkpoints/GATE-4-CP-0007/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:DIVERGENCE.md`, `file:docs/adr/ADR-0034-command-inputs-must-cross-git-transport.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0040 - lesson:LSN-0041

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0040
- Description: Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0041 - lesson:LSN-0042

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0041
- Description: Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`, `file:apps/api/migrations/versions/0007_experience_store.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/integration/test_migrations.py`, `file:apps/api/tests/unit/test_domain_model.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `file:apps/api/tests/integration/test_migrations.py`, `file:apps/api/tests/unit/test_domain_model.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0042 - lesson:LSN-0043

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0042
- Description: Verify a log line is not evidence that another process is ready
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0043 - lesson:LSN-0044

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0043
- Description: Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0044 - lesson:LSN-0045

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0044
- Description: Verify a counted test suite must declare its cases statically, because the denominator is read from the source
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0045 - lesson:LSN-0046

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0045
- Description: Verify a timeout that cancels the task it runs in leaves nothing able to record what happened
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0046 - lesson:LSN-0047

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0046
- Description: Verify a refusal that misnames the defect spends the only repair on the wrong correction
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0047 - lesson:LSN-0048

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0047
- Description: Verify a state and the event that explains it, written in two commits, are written event first
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0048 - lesson:LSN-0049

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0048
- Description: Verify a metric read the instant after the call that moved it is read before the scrape that carries it
- Implementation: `file:scripts/iacode/observability.py`, `file:infra/tests/test_running_stack.py`, `file:scripts/iacode/smoke.py`, `file:infra/prometheus/prometheus.yml`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_prometheus_observation_waits_on_the_versioned_scrape_cycle`, `file:docs/checkpoints/GATE-4-CP-0005/ORDER-ISOLATION-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0005/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0004/VERIFICATION-REPORT.json`, `file:docs/checkpoints/GATE-4-CP-0004/CLEAN-CLONE-REPORT.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:docs/adr/ADR-0033-verification-runtime-is-owned-by-one-checkout.md`, `file:docs/runbooks/QUALITY-ENGINE.md`, `file:docs/checkpoints/GATE-4-CP-0005/BASELINE.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0049 - lesson:LSN-0050

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0049
- Description: Verify a checkpoint sealed without naming its own tag cannot be validated from that tag
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0050 - lesson:LSN-0051

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0050
- Description: Verify a payload one service bounds for another must be bounded as the receiver measures it
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0051 - lesson:LSN-0052

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0051
- Description: Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0052 - lesson:LSN-0053

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0052
- Description: Verify a process sweep that reads what a forking process holds waits on the processes it has to kill
- Implementation: `file:services/sandbox/src/iacode_sandbox/helper.py`, `file:services/sandbox/tests/test_sandbox_helper.py`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_the_sweep_waits_for_zombies_to_be_reaped_before_returning`, `test:test_a_fork_bomb_that_detaches_leaves_a_sandbox_that_still_answers`, `file:docs/checkpoints/GATE-4-CP-0003/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0053 - lesson:LSN-0054

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0053
- Description: Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0054 - lesson:LSN-0055

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0054
- Description: Verify a contract a model must follow has to reach the model, rendered from the definition the parser enforces
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0055 - lesson:LSN-0056

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0055
- Description: Verify a result is accepted only from the executor that owns the request, decided when the request is created
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0056 - lesson:LSN-0057

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0056
- Description: Verify a pinned lock can become unsafe without changing, so advisory state is live evidence
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0057 - lesson:LSN-0058

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0057
- Description: Verify container health does not prove Docker Desktop host-port forwarding
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0058 - lesson:LSN-0059

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0058
- Description: Verify a lesson exclusion must declare the scope it excludes
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0059 - lesson:LSN-0060

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0059
- Description: Verify parent and child facts without an ORM relationship require an explicit flush boundary
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0060 - lesson:LSN-0061

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0060
- Description: Verify cancellation completion must not bypass cleanup acknowledgement
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0061 - lesson:LSN-0062

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0061
- Description: Verify provenance digests are a set even when their sources are distinct
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0062 - lesson:LSN-0063

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0062
- Description: Verify an identity shared across services must satisfy the strictest persistence type and remain stable
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0063 - lesson:LSN-0064

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0063
- Description: Verify a shared execution resource needs an explicit exclusive owner for every owning domain
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0064 - lesson:LSN-0065

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0064
- Description: Verify a shared execution identifier must not be written into a foreign key owned by another domain
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0065 - lesson:LSN-0066

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0065
- Description: Verify immutable content identity excludes observation time and the first observer
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0066 - lesson:LSN-0067

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0066
- Description: Verify cancellation semantics must survive orchestration-library exception wrapping
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0067 - lesson:LSN-0068

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0067
- Description: Verify a bounded parser must apply each content limit only to content it interprets
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0068 - lesson:LSN-0069

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0068
- Description: Verify a polyglot plan binds each check to both its project root and its toolchain
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0069 - lesson:LSN-0070

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0069
- Description: Verify project discovery must separate deployable roots, nested fixtures and check applicability
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0070 - lesson:LSN-0071

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0070
- Description: Verify every quality image must provision snapshots on its oldest runtime and prepare each isolated check
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0071 - lesson:LSN-0072

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0071
- Description: Verify secret findings and reviewed false positives must share one policy-owned taxonomy
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0072 - lesson:LSN-0073

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0072
- Description: Verify the canonical lint denominator must cover every detected project root
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0073 - lesson:LSN-0074

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0073
- Description: Verify an importable source tree is not an installed or repository-configured test environment
- Implementation: `file:apps/api/tests/unit/test_desktop_api.py`
- Test: `file:apps/api/tests/unit/test_desktop_api.py`, `file:services/sandbox/tests/test_quality_images.py`
- Negative test: `file:apps/api/tests/unit/test_desktop_api.py`, `file:services/sandbox/tests/test_quality_images.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0074 - lesson:LSN-0075

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0074
- Description: Verify offline package installation requires its build backend inside the quality image
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0075 - lesson:LSN-0076

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0075
- Description: Verify projected nested configuration requires an explicit monorepo root
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0076 - lesson:LSN-0077

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0076
- Description: Verify harness wait bounds must reflect workload size without changing product deadlines
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0077 - lesson:LSN-0078

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0077
- Description: Verify evidence recorders must resolve caller-supplied commit references before execution
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0078 - lesson:LSN-0079

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0078
- Description: Verify test discovery and the unit runner must cover the same project scope
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0079 - lesson:LSN-0080

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0079
- Description: Verify a failed verification stage must not leave an older PASS report addressable
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`, `file:scripts/iacode/scenarios/desktop_e2e.py`, `file:scripts/iacode/scenarios/experience_store_e2e.py`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`, `file:tests/test_gate5_clients.py`, `file:tests/test_gate6_experience.py`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `checkpoint:FINDINGS.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0080 - lesson:LSN-0081

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0080
- Description: Verify canonical requirement evidence must name a test the repository actually discovers
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0081 - lesson:LSN-0082

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0081
- Description: Verify engineering memory cannot depend on an ephemeral generated report
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0082 - lesson:LSN-0083

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0082
- Description: Verify a command that decodes captured UTF-8 must also configure the stream that re-emits it
- Implementation: `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/capture_blocked_attempt.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/observe_restarted_engine.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/recover_owned_verification.py`, `file:scripts/development-ledger/ledger_common.py`
- Test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate0_foundation.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate0_foundation.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0083 - lesson:LSN-0084

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0083
- Description: Verify a historical Gate documentation test must derive the current entry-point state
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`, `file:tests/test_gate5_clients.py`, `file:tests/test_gate6_experience.py`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`, `file:tests/test_gate5_clients.py`, `file:tests/test_gate6_experience.py`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `checkpoint:FINDINGS.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0084 - lesson:LSN-0085

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0084
- Description: Verify a source-based control must assert syntax semantics rather than formatter layout
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0085 - lesson:LSN-0086

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0085
- Description: Verify a subprocess assertion must preserve the exit code when both streams are empty
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0086 - lesson:LSN-0087

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0086
- Description: Verify a rehearsal worker must register every workflow activity boundary
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0087 - lesson:LSN-0088

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0087
- Description: Verify a test inside a built image can consume only inputs copied into that image
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0088 - lesson:LSN-0089

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0088
- Description: Verify domain not-applicability and operational failure need distinct orchestration outcomes
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `file:docs/checkpoints/GATE-4-CP-0001/TESTS.json`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0089 - lesson:LSN-0090

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0089
- Description: Verify a clean-clone control must use only versioned configuration inputs
- Implementation: `file:tests/test_gate4_quality_engine.py`, `file:infra/compose/.env.example`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_the_evaluator_service_has_no_engine_socket_or_host_project_mount`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0090 - lesson:LSN-0091

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0090
- Description: Verify secret detection must run on the exact bytes at the durable evidence boundary
- Implementation: `file:services/sandbox/src/iacode_sandbox/output_security.py`, `file:services/sandbox/src/iacode_sandbox/service.py`, `file:packages/common/src/iacode_common/secret_scanning.py`, `file:scripts/iacode/scenarios/quality_engine_e2e.py`, `file:scripts/development-ledger/secret_scan.py`
- Test: `test:test_canonical_secret_output_is_rejected_before_durable_delivery`, `test:test_canonical_secret_output_never_becomes_the_activity_response`, `test:test_canonical_secret_output_workspace_diagnostic_never_reaches_session_record`, `test:test_json_escaped_secret_is_refused_before_persistence_and_after_legacy_read`, `test:test_live_output_control_timeout_retains_bounded_diagnostics_and_stays_red`, `test:PublicationTransportScanningTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0039-sandbox-output-is-scanned-before-durable-delivery.md`, `file:docs/checkpoints/GATE-4-CP-0010/HISTORICAL-SCAN-REVIEW.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0091 - lesson:LSN-0092

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0091
- Description: Verify canonical audit parsers must consume every bounded sealed report rendering
- Implementation: `file:scripts/development-ledger/policies.py`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_a_blocking_finding_paragraph_in_a_sealed_audit_is_parsed`, `test:test_blocking_finding_prose_is_bounded_to_its_section`, `test:test_a_report_whose_findings_cannot_be_parsed_is_refused_rather_than_read_as_empty`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0092 - lesson:LSN-0093

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0092
- Description: Verify disposable control repositories must carry every imported repository package
- Implementation: `file:scripts/development-ledger/promotion_fixture.py`, `file:tests/test_development_ledger.py`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_disposable_ledger_runtime_carries_its_canonical_scanner_dependency`, `test:test_repaired_gate_is_reported_as_green_in_a_new_cycle`, `test:test_full_delivery_assurance_flow_reaches_ready_for_review`, `file:docs/checkpoints/GATE-4-CP-0003/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0093 - lesson:LSN-0094

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0093
- Description: Verify a review bundle must include unchanged canonical artifact categories
- Implementation: `file:scripts/development-ledger/review_bundle.py`, `file:tests/test_gate4_quality_engine.py`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_review_context_includes_unchanged_migrations_schemas_and_policies`, `file:docs/checkpoints/GATE-4-CP-0003/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0094 - lesson:LSN-0095

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0094
- Description: Verify a complete verifier must own its Compose runtime by checkout
- Implementation: `file:scripts/iacode/verify.py`, `file:scripts/iacode/compose.py`, `file:scripts/iacode/observability.py`, `file:infra/tests/test_running_stack.py`, `file:scripts/iacode/smoke.py`, `file:scripts/iacode/scenarios/verification_order_isolation.py`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_full_verification_uses_a_checkout_owned_compose_project_and_dynamic_ports`, `test:test_each_stage_receives_the_frozen_verification_environment`, `test:test_cleanup_refuses_the_shared_developer_project`, `test:test_live_stack_stage_builds_every_image_before_it_is_exercised`, `test:test_prometheus_observation_waits_on_the_versioned_scrape_cycle`, `test:test_order_isolation_probe_preserves_the_historical_contiguous_stage_order`, `file:docs/checkpoints/GATE-4-CP-0005/ORDER-ISOLATION-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0004/VERIFICATION-REPORT.json`, `file:docs/checkpoints/GATE-4-CP-0004/CLEAN-CLONE-REPORT.json`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:docs/adr/ADR-0033-verification-runtime-is-owned-by-one-checkout.md`, `file:docs/runbooks/QUALITY-ENGINE.md`, `file:docs/checkpoints/GATE-4-CP-0005/BASELINE.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0095 - lesson:LSN-0096

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0095
- Description: Verify evidence publishers must consume the producer's canonical result schema
- Implementation: `file:docs/checkpoints/GATE-4-CP-0005/RUN-PUBLISHED-FULL-VERIFICATION.py`, `file:docs/checkpoints/GATE-4-CP-0006/FINAL-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_published_full_verification_counts_the_canonical_result_field`, `test:test_published_report_reconciliation_allows_only_the_generated_report`, `file:docs/checkpoints/GATE-4-CP-0005/COMMANDS.jsonl`, `file:.iacode/memory/retrospectives/GATE-4-CP-0005.md`, `file:docs/checkpoints/GATE-4-CP-0007/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0006/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0006/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0006/G4-X7-INDEPENDENT-PROBE.json`, `file:docs/checkpoints/GATE-4-CP-0007/M2-INTERNAL-RED-TEAM.json`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:.iacode/memory/retrospectives/GATE-4-CP-0005.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0096 - lesson:LSN-0097

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0096
- Description: Verify a review-bundle declaration must bind an immutable reconstruction subject
- Implementation: `file:scripts/development-ledger/review_bundle.py`, `file:scripts/development-ledger/seal_checkpoint.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/record_command.py`, `file:services/evaluator/src/iacode_evaluator/workflow.py`, `file:.iacode/schemas/checkpoint.schema.json`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_immutable_subject_rebuilds_are_byte_identical_and_exclude_only_the_sidecar`, `test:test_declared_digest_and_size_are_rebuilt_not_trusted`, `test:test_pending_declaration_is_allowed_only_before_handoff_or_inside_sealing`, `test:test_full_delivery_assurance_flow_reaches_ready_for_review`, `test:test_cancellation_is_rechecked_after_dispatch_before_activity_start`, `test:test_durable_cancelling_state_stops_an_active_sandbox_activity`, `test:test_a_signal_flag_set_before_handle_assignment_still_cancels_the_activity`, `test:test_accepted_cancellation_wins_over_a_racing_success_response`, `test:test_inputs_are_canonicalized_and_an_unknown_subject_is_refused`, `test:test_in_progress_symbolic_head_validates_from_its_matching_subject_tag`, `test:test_subject_tag_never_substitutes_for_a_sealed_checkpoint_tag`, `test:test_the_index_lists_every_record_with_its_title_and_status`, `test:test_a_record_missing_from_the_index_is_detected`, `test:test_gate_consistency_is_provisional_while_work_is_in_progress`, `test:test_green_keeper_declares_its_in_progress_evidence_dirty_before_validation`, `test:test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test:test_the_refresh_has_one_definition`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0009/BASELINE-BUNDLE-AUDIT.json`, `test:test_declared_digest_and_size_are_rebuilt_not_trusted`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:docs/adr/ADR-0035-review-bundles-bind-immutable-content.md`, `file:docs/adr/ADR-0036-pre-seal-validation-binds-an-explicit-subject.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/TOOL-CAPABILITIES.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0097 - lesson:LSN-0098

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0097
- Description: Verify accepted cancellation must be enforced from durable state across activity boundaries
- Implementation: `file:services/evaluator/src/iacode_evaluator/workflow.py`, `file:services/evaluator/src/iacode_evaluator/store.py`, `file:services/evaluator/src/iacode_evaluator/verdict.py`
- Test: `test:test_durable_cancellation_at_activity_completion_finishes_without_a_signal`, `test:test_durable_cancellation_during_result_write_finishes_without_a_signal`, `test:test_durable_cancellation_during_verdict_write_finishes_without_a_signal`, `test:test_concurrent_cancellation_and_verdict_have_one_winner`, `test:test_unrelated_activity_failure_is_not_hidden_as_cancellation`, `test:test_cancellation_preserves_the_digest_of_an_already_failing_derivation`, `test:test_completed_check_joins_cancelled_durable_read_without_cancelling_run`, `test:test_unrelated_watcher_failure_is_not_hidden_by_join_cleanup`, `test:test_precompleted_watcher_cancellation_is_not_claimed_as_own_cleanup`, `test:test_durable_read_completion_after_handle_clear_keeps_cancellation_authoritative`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0038-cancellation-and-verdict-commit-are-serialized.md`, `file:docs/adr/ADR-0041-polling-cleanup-preserves-completed-checks.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0098 - lesson:LSN-0099

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0098
- Description: Verify a refused subject is an attempted input, not executed commit evidence
- Implementation: `file:scripts/development-ledger/review_bundle.py`, `file:scripts/development-ledger/seal_checkpoint.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/record_command.py`, `file:services/evaluator/src/iacode_evaluator/workflow.py`, `file:.iacode/schemas/checkpoint.schema.json`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_immutable_subject_rebuilds_are_byte_identical_and_exclude_only_the_sidecar`, `test:test_declared_digest_and_size_are_rebuilt_not_trusted`, `test:test_pending_declaration_is_allowed_only_before_handoff_or_inside_sealing`, `test:test_full_delivery_assurance_flow_reaches_ready_for_review`, `test:test_cancellation_is_rechecked_after_dispatch_before_activity_start`, `test:test_durable_cancelling_state_stops_an_active_sandbox_activity`, `test:test_a_signal_flag_set_before_handle_assignment_still_cancels_the_activity`, `test:test_accepted_cancellation_wins_over_a_racing_success_response`, `test:test_inputs_are_canonicalized_and_an_unknown_subject_is_refused`, `test:test_in_progress_symbolic_head_validates_from_its_matching_subject_tag`, `test:test_subject_tag_never_substitutes_for_a_sealed_checkpoint_tag`, `test:test_the_index_lists_every_record_with_its_title_and_status`, `test:test_a_record_missing_from_the_index_is_detected`, `test:test_gate_consistency_is_provisional_while_work_is_in_progress`, `test:test_green_keeper_declares_its_in_progress_evidence_dirty_before_validation`, `test:test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test:test_the_refresh_has_one_definition`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0009/BASELINE-BUNDLE-AUDIT.json`, `test:test_declared_digest_and_size_are_rebuilt_not_trusted`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:docs/adr/ADR-0035-review-bundles-bind-immutable-content.md`, `file:docs/adr/ADR-0036-pre-seal-validation-binds-an-explicit-subject.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/TOOL-CAPABILITIES.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0099 - lesson:LSN-0100

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0099
- Description: Verify pre-seal detached validation must bind the explicit subject namespace
- Implementation: `file:scripts/development-ledger/review_bundle.py`, `file:scripts/development-ledger/seal_checkpoint.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/record_command.py`, `file:services/evaluator/src/iacode_evaluator/workflow.py`, `file:.iacode/schemas/checkpoint.schema.json`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_immutable_subject_rebuilds_are_byte_identical_and_exclude_only_the_sidecar`, `test:test_declared_digest_and_size_are_rebuilt_not_trusted`, `test:test_pending_declaration_is_allowed_only_before_handoff_or_inside_sealing`, `test:test_full_delivery_assurance_flow_reaches_ready_for_review`, `test:test_cancellation_is_rechecked_after_dispatch_before_activity_start`, `test:test_durable_cancelling_state_stops_an_active_sandbox_activity`, `test:test_a_signal_flag_set_before_handle_assignment_still_cancels_the_activity`, `test:test_accepted_cancellation_wins_over_a_racing_success_response`, `test:test_inputs_are_canonicalized_and_an_unknown_subject_is_refused`, `test:test_in_progress_symbolic_head_validates_from_its_matching_subject_tag`, `test:test_subject_tag_never_substitutes_for_a_sealed_checkpoint_tag`, `test:test_the_index_lists_every_record_with_its_title_and_status`, `test:test_a_record_missing_from_the_index_is_detected`, `test:test_gate_consistency_is_provisional_while_work_is_in_progress`, `test:test_green_keeper_declares_its_in_progress_evidence_dirty_before_validation`, `test:test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test:test_the_refresh_has_one_definition`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0009/BASELINE-BUNDLE-AUDIT.json`, `test:test_declared_digest_and_size_are_rebuilt_not_trusted`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:docs/adr/ADR-0035-review-bundles-bind-immutable-content.md`, `file:docs/adr/ADR-0036-pre-seal-validation-binds-an-explicit-subject.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/TOOL-CAPABILITIES.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0100 - lesson:LSN-0101

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0100
- Description: Verify a structural record and its canonical index are one atomic change
- Implementation: `file:scripts/development-ledger/review_bundle.py`, `file:scripts/development-ledger/seal_checkpoint.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/record_command.py`, `file:services/evaluator/src/iacode_evaluator/workflow.py`, `file:.iacode/schemas/checkpoint.schema.json`, `file:docs/checkpoints/GATE-4-CP-0007/FINAL-REPORT.md`
- Test: `test:test_immutable_subject_rebuilds_are_byte_identical_and_exclude_only_the_sidecar`, `test:test_declared_digest_and_size_are_rebuilt_not_trusted`, `test:test_pending_declaration_is_allowed_only_before_handoff_or_inside_sealing`, `test:test_full_delivery_assurance_flow_reaches_ready_for_review`, `test:test_cancellation_is_rechecked_after_dispatch_before_activity_start`, `test:test_durable_cancelling_state_stops_an_active_sandbox_activity`, `test:test_a_signal_flag_set_before_handle_assignment_still_cancels_the_activity`, `test:test_accepted_cancellation_wins_over_a_racing_success_response`, `test:test_inputs_are_canonicalized_and_an_unknown_subject_is_refused`, `test:test_in_progress_symbolic_head_validates_from_its_matching_subject_tag`, `test:test_subject_tag_never_substitutes_for_a_sealed_checkpoint_tag`, `test:test_the_index_lists_every_record_with_its_title_and_status`, `test:test_a_record_missing_from_the_index_is_detected`, `test:test_gate_consistency_is_provisional_while_work_is_in_progress`, `test:test_green_keeper_declares_its_in_progress_evidence_dirty_before_validation`, `test:test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test:test_the_refresh_has_one_definition`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY.json`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0009/BASELINE-BUNDLE-AUDIT.json`, `test:test_declared_digest_and_size_are_rebuilt_not_trusted`, `file:docs/checkpoints/GATE-4-CP-0009/M2-INTERNAL-RED-TEAM.json`
- Documentation: `file:docs/adr/ADR-0035-review-bundles-bind-immutable-content.md`, `file:docs/adr/ADR-0036-pre-seal-validation-binds-an-explicit-subject.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/TOOL-CAPABILITIES.md`, `file:docs/GATE-4-CHECKLIST.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0101 - lesson:LSN-0102

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0101
- Description: Verify assurance denominators must derive category counts from the current source set
- Implementation: `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/run_full_verification.py`, `file:scripts/iacode/verify.py`
- Test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate5_clients.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0102 - lesson:LSN-0103

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0102
- Description: Verify adversarial fixtures must hash the complete validated contract
- Implementation: `file:services/evaluator/tests/test_persistence.py`, `file:scripts/iacode/gates/lint.py`
- Test: `test:test_verdict_before_cancellation_refuses_late_acceptance`, `test:test_mandatory_lint_covers_every_python_project_root`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/DECISIONS.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0103 - lesson:LSN-0104

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0103
- Description: Verify intermediate closure and independent validation must have unambiguous contracts
- Implementation: `file:docs/DEVELOPMENT-CONTRACT.md`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:test_internal_closure_cannot_claim_independent_review_or_red_team`, `test:test_internal_closure_leaves_independent_milestone_validation_pending`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/MILESTONE-VALIDATION.md`, `file:docs/adr/ADR-0037-intermediate-gates-use-internal-closure.md`, `file:docs/checkpoints/GATE-4-CP-0010/AUTHORIZATION.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0104 - lesson:LSN-0105

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0104
- Description: Verify new behavioral tests must satisfy the unchanged source-quality contract
- Implementation: `file:scripts/iacode/gates/lint.py`, `file:apps/api/src/iacode_api/experience/runtime.py`, `file:apps/api/src/iacode_api/routes/experiences.py`, `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/unit/test_experience_api.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:apps/api/tests/unit/test_experience_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0105 - lesson:LSN-0106

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0105
- Description: Verify a security repair must execute at the causal output boundary, not a similarly shaped branch
- Implementation: `file:services/sandbox/src/iacode_sandbox/output_security.py`, `file:services/sandbox/src/iacode_sandbox/service.py`, `file:packages/common/src/iacode_common/secret_scanning.py`, `file:scripts/iacode/scenarios/quality_engine_e2e.py`, `file:scripts/development-ledger/secret_scan.py`
- Test: `test:test_canonical_secret_output_is_rejected_before_durable_delivery`, `test:test_canonical_secret_output_never_becomes_the_activity_response`, `test:test_canonical_secret_output_workspace_diagnostic_never_reaches_session_record`, `test:test_json_escaped_secret_is_refused_before_persistence_and_after_legacy_read`, `test:test_live_output_control_timeout_retains_bounded_diagnostics_and_stays_red`, `test:PublicationTransportScanningTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0039-sandbox-output-is-scanned-before-durable-delivery.md`, `file:docs/checkpoints/GATE-4-CP-0010/HISTORICAL-SCAN-REVIEW.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0106 - lesson:LSN-0107

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0106
- Description: Verify an adversarial marker must satisfy the canonical detector before it can judge containment
- Implementation: `file:services/sandbox/src/iacode_sandbox/output_security.py`, `file:services/sandbox/src/iacode_sandbox/service.py`, `file:packages/common/src/iacode_common/secret_scanning.py`, `file:scripts/iacode/scenarios/quality_engine_e2e.py`, `file:scripts/development-ledger/secret_scan.py`
- Test: `test:test_canonical_secret_output_is_rejected_before_durable_delivery`, `test:test_canonical_secret_output_never_becomes_the_activity_response`, `test:test_canonical_secret_output_workspace_diagnostic_never_reaches_session_record`, `test:test_json_escaped_secret_is_refused_before_persistence_and_after_legacy_read`, `test:test_live_output_control_timeout_retains_bounded_diagnostics_and_stays_red`, `test:PublicationTransportScanningTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0039-sandbox-output-is-scanned-before-durable-delivery.md`, `file:docs/checkpoints/GATE-4-CP-0010/HISTORICAL-SCAN-REVIEW.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0107 - lesson:LSN-0108

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0107
- Description: Verify evidence timestamp transport must preserve RFC3339 rather than a shell locale rendering
- Implementation: `file:scripts/development-ledger/ledger_common.py`
- Test: `test:test_lesson_timestamp_transport_rejects_locale_rendering`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0108 - lesson:LSN-0109

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0108
- Description: Verify regression counts and evidence must exclude only policy-bound live input repositories
- Implementation: `file:scripts/development-ledger/policies.py`, `file:.iacode/policies/test-suites.json`
- Test: `test:TestSuiteInputRepositoriesTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0040-test-counts-follow-policy-bound-collection.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0109 - lesson:LSN-0110

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0109
- Description: Verify a timed-out live proof retains bounded diagnostics before owned cleanup
- Implementation: `file:services/sandbox/src/iacode_sandbox/output_security.py`, `file:services/sandbox/src/iacode_sandbox/service.py`, `file:packages/common/src/iacode_common/secret_scanning.py`, `file:scripts/iacode/scenarios/quality_engine_e2e.py`, `file:scripts/development-ledger/secret_scan.py`
- Test: `test:test_canonical_secret_output_is_rejected_before_durable_delivery`, `test:test_canonical_secret_output_never_becomes_the_activity_response`, `test:test_canonical_secret_output_workspace_diagnostic_never_reaches_session_record`, `test:test_json_escaped_secret_is_refused_before_persistence_and_after_legacy_read`, `test:test_live_output_control_timeout_retains_bounded_diagnostics_and_stays_red`, `test:PublicationTransportScanningTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0039-sandbox-output-is-scanned-before-durable-delivery.md`, `file:docs/checkpoints/GATE-4-CP-0010/HISTORICAL-SCAN-REVIEW.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0110 - lesson:LSN-0111

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0110
- Description: Verify polling watcher cleanup must preserve completed checks and accepted cancellation
- Implementation: `file:services/evaluator/src/iacode_evaluator/workflow.py`, `file:services/evaluator/src/iacode_evaluator/store.py`, `file:services/evaluator/src/iacode_evaluator/verdict.py`
- Test: `test:test_durable_cancellation_at_activity_completion_finishes_without_a_signal`, `test:test_durable_cancellation_during_result_write_finishes_without_a_signal`, `test:test_durable_cancellation_during_verdict_write_finishes_without_a_signal`, `test:test_concurrent_cancellation_and_verdict_have_one_winner`, `test:test_unrelated_activity_failure_is_not_hidden_as_cancellation`, `test:test_cancellation_preserves_the_digest_of_an_already_failing_derivation`, `test:test_completed_check_joins_cancelled_durable_read_without_cancelling_run`, `test:test_unrelated_watcher_failure_is_not_hidden_by_join_cleanup`, `test:test_precompleted_watcher_cancellation_is_not_claimed_as_own_cleanup`, `test:test_durable_read_completion_after_handle_clear_keeps_cancellation_authoritative`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0038-cancellation-and-verdict-commit-are-serialized.md`, `file:docs/adr/ADR-0041-polling-cleanup-preserves-completed-checks.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0111 - lesson:LSN-0112

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0111
- Description: Verify canonical scanner consumers must share transport decoding, not only patterns
- Implementation: `file:services/sandbox/src/iacode_sandbox/output_security.py`, `file:services/sandbox/src/iacode_sandbox/service.py`, `file:packages/common/src/iacode_common/secret_scanning.py`, `file:scripts/iacode/scenarios/quality_engine_e2e.py`, `file:scripts/development-ledger/secret_scan.py`
- Test: `test:test_canonical_secret_output_is_rejected_before_durable_delivery`, `test:test_canonical_secret_output_never_becomes_the_activity_response`, `test:test_canonical_secret_output_workspace_diagnostic_never_reaches_session_record`, `test:test_json_escaped_secret_is_refused_before_persistence_and_after_legacy_read`, `test:test_live_output_control_timeout_retains_bounded_diagnostics_and_stays_red`, `test:PublicationTransportScanningTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0039-sandbox-output-is-scanned-before-durable-delivery.md`, `file:docs/checkpoints/GATE-4-CP-0010/HISTORICAL-SCAN-REVIEW.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0112 - lesson:LSN-0113

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0112
- Description: Verify stronger delivery controls must follow the immutable subject policy version
- Implementation: `file:.iacode/memory/POLICY.json`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/policies.py`, `file:.iacode/policies/test-suites.json`
- Test: `test:test_live_policy_requires_strict_internal_verdict_semantics`, `test:test_legacy_internal_red_team_fields_keep_their_subject_policy_semantics`, `test:test_every_sealed_checkpoint_validates_from_its_own_tag`, `test:TestSuiteInputRepositoriesTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0042-internal-verdict-semantics-follow-subject-policy.md`, `file:docs/adr/ADR-0043-collection-semantics-follow-subject-policy.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0113 - lesson:LSN-0114

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0113
- Description: Verify transport line metadata must not repeatedly scan the source prefix
- Implementation: `file:packages/common/src/iacode_common/secret_scanning.py`
- Test: `test:test_fragment_carrier_lines_count_each_source_range_at_most_once`, `test:test_json_error_line_index_matches_builtin_string_coordinates`, `test:test_indexed_decoder_errors_keep_original_messages_and_coordinates`, `test:test_interleaved_fragments_keep_their_distinct_carrier_lines`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/adr/ADR-0039-sandbox-output-is-scanned-before-durable-delivery.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0114 - lesson:LSN-0115

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0114
- Description: Verify a failing full verifier retains every bounded case identifier beyond its output tail
- Implementation: `file:scripts/iacode/verify.py`
- Test: `test:VerifierFailureDiagnosticsTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/checkpoints/GATE-4-CP-0010/DECISIONS.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0115 - lesson:LSN-0116

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0115
- Description: Verify a live resumability pointer is generated after Git boundaries, not committed into its own subject
- Implementation: `file:scripts/development-ledger/program_state.py`, `file:.iacode/policies/program-state.json`, `file:.iacode/schemas/program-state.schema.json`, `file:docs/checkpoints/GATE-4-CP-0010/STEPS.json`
- Test: `test:LiveProgramStateTests`, `test:ProgramStateTests`
- Negative test: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`
- Documentation: `file:docs/program/README.md`, `file:docs/adr/ADR-0045-live-program-state-is-generated-after-git-boundaries.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0116 - lesson:LSN-0117

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0116
- Description: Verify an architecture rollup must not contradict the delivered capability described below it
- Implementation: `file:docs/ARCHITECTURE.md`
- Test: `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0117 - lesson:LSN-0118

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0117
- Description: Verify post-response validation failures must preserve an accepted mutation's uncertain outcome
- Implementation: `file:apps/cli/src/client.cjs`, `file:apps/vscode-extension/src/extension.cjs`
- Test: `file:apps/cli/tests/core.test.cjs`, `file:tests/test_gate5_clients.py`
- Negative test: `file:apps/cli/tests/core.test.cjs`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0118 - lesson:LSN-0119

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0118
- Description: Verify a clean publication scan does not replace the stricter checkpoint secret scan
- Implementation: `file:scripts/development-ledger/validate_lessons.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:packages/common/src/iacode_common/secret_scanning.py`, `file:docs/checkpoints/GATE-6-CP-0001/STRICT-MEMORY-FINDING.json`
- Test: `file:tests/test_gate5_clients.py`, `file:apps/api/tests/unit/test_desktop_api.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:apps/api/tests/unit/test_desktop_api.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0119 - lesson:LSN-0120

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0119
- Description: Verify native installation proofs must resolve the installed CLI entrypoint
- Implementation: `file:scripts/iacode/native_editor.py`
- Test: `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0120 - lesson:LSN-0121

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0120
- Description: Verify standard-library host probes must not initialize application dependency graphs
- Implementation: `file:scripts/iacode/desktop_test_support.py`
- Test: `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0121 - lesson:LSN-0122

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0121
- Description: Verify engine-allocated host ports must be rediscovered after container restart
- Implementation: `file:scripts/iacode/desktop_test_support.py`, `file:scripts/iacode/scenarios/desktop_e2e.py`
- Test: `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0122 - lesson:LSN-0123

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0122
- Description: Verify consent binds workspace identity, not an uncanonicalized path spelling
- Implementation: `file:apps/vscode-extension/src/extension.cjs`
- Test: `file:apps/vscode-extension/tests/extension.test.cjs`, `file:tests/test_gate5_clients.py`
- Negative test: `file:apps/vscode-extension/tests/extension.test.cjs`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0123 - lesson:LSN-0124

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0123
- Description: Verify durable editor recovery must not use an in-memory test host
- Implementation: `file:scripts/iacode/native_editor.py`, `file:apps/vscode-extension/host-tests/driver.cjs`
- Test: `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0124 - lesson:LSN-0125

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0124
- Description: Verify native parent exit is not proof of process and profile cleanup
- Implementation: `file:scripts/iacode/native_process.py`, `file:scripts/iacode/native_editor.py`, `file:docs/adr/ADR-0052-native-cleanup-failures-retain-observed-diagnostics.md`
- Test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate5_clients.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0125 - lesson:LSN-0126

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0125
- Description: Verify known authentication material is not domain or presentation data
- Implementation: `file:services/experience/src/iacode_experience/domain.py`, `file:apps/api/src/iacode_api/middleware/desktop_auth.py`
- Test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/cli/tests/core.test.cjs`
- Negative test: `file:services/experience/tests/test_contract.py`, `file:apps/api/tests/unit/test_experience_api.py`, `file:apps/cli/tests/core.test.cjs`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0126 - lesson:LSN-0127

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0126
- Description: Verify fresh runtime health does not initialize an operator-managed model catalog
- Implementation: `file:scripts/iacode/scenarios/desktop_e2e.py`, `file:scripts/iacode/desktop_test_support.py`
- Test: `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0127 - lesson:LSN-0128

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0127
- Description: Verify adversarial premises must use the actual public contract
- Implementation: `file:scripts/iacode/scenarios/desktop_e2e.py`, `file:scripts/iacode/desktop_test_support.py`
- Test: `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0128 - lesson:LSN-0129

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0128
- Description: Verify repeated cancellation must preserve an already cancelled terminal result
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`
- Test: `file:services/agent-runtime/tests/test_cancellation_store.py`
- Negative test: `file:services/agent-runtime/tests/test_cancellation_store.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0129 - lesson:LSN-0130

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0129
- Description: Verify executable export line endings belong to the source and packaging contract
- Implementation: `file:.gitattributes`, `file:scripts/iacode/build_clients.py`
- Test: `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0130 - lesson:LSN-0131

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0130
- Description: Verify raw evidence digests require byte-preserving Git export, not text normalization
- Implementation: `file:.gitattributes`
- Test: `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0131 - lesson:LSN-0132

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0131
- Description: Verify owned Git clones need read-only-aware cleanup, not native-profile lock retry
- Implementation: `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/run_full_verification.py`
- Test: `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0132 - lesson:LSN-0133

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0132
- Description: Verify shared field names do not imply shared schema types
- Implementation: `file:.iacode/schemas/provenance.schema.json`, `file:docs/checkpoints/GATE-5-CP-0001/PROVENANCE.json`
- Test: `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0133 - lesson:LSN-0134

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0133
- Description: Verify configuration classifiers consume decoded values, not dotenv quote syntax
- Implementation: `file:scripts/iacode/compose.py`
- Test: `file:tests/test_gate5_clients.py`, `file:tests/test_gate1_model_gateway.py`, `file:infra/tests/test_compose_definition.py`, `file:infra/tests/test_backup_tooling.py`
- Negative test: `file:tests/test_gate5_clients.py`, `file:tests/test_gate1_model_gateway.py`, `file:infra/tests/test_compose_definition.py`, `file:infra/tests/test_backup_tooling.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-5-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0134 - lesson:LSN-0135

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0134
- Description: Verify capture producer evidence before fallible interpretation or owned cleanup
- Implementation: `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/run_full_verification.py`
- Test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate5_clients.py`
- Negative test: `file:tests/test_gate6_experience.py`, `file:tests/test_gate5_clients.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0135 - lesson:LSN-0136

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0135
- Description: Verify strict JSON validation loses transport context
- Implementation: `file:packages/contracts/src/iacode_contracts/experience.py`, `file:services/experience/src/iacode_experience/domain.py`
- Test: `file:services/experience/tests/test_contract.py`
- Negative test: `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0136 - lesson:LSN-0137

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0136
- Description: Verify sQL text interprets inline JSON colons as bindings
- Implementation: `file:apps/api/tests/integration/test_experience_store.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0137 - lesson:LSN-0138

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0137
- Description: Verify secret projection distinguishes public identities from authorization secrets
- Implementation: `file:apps/api/src/iacode_api/experience/runtime.py`, `file:services/experience/src/iacode_experience/domain.py`, `file:apps/api/src/iacode_api/experience/sources.py`
- Test: `file:apps/api/tests/unit/test_experience_api.py`, `file:services/experience/tests/test_contract.py`
- Negative test: `file:apps/api/tests/unit/test_experience_api.py`, `file:services/experience/tests/test_contract.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0138 - lesson:LSN-0139

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0138
- Description: Verify privacy projection begins in the source query
- Implementation: `file:apps/api/src/iacode_api/experience/sources.py`
- Test: `file:apps/api/tests/integration/test_experience_store.py`
- Negative test: `file:apps/api/tests/integration/test_experience_store.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0139 - lesson:LSN-0140

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0139
- Description: Verify summaries preserve canonical continuation structure
- Implementation: `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/assemble_source_ready.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/render_local_handoff.py`
- Test: `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0140 - lesson:LSN-0141

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0140
- Description: Verify preflight checks honor every declared applicability dimension
- Implementation: `file:tests/test_development_ledger.py`
- Test: `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0141 - lesson:LSN-0142

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0141
- Description: Verify local Engine recovery keeps transport and cleanup scoped
- Implementation: `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/with_local_engine.py`, `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/recover_owned_verification.py`
- Test: `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0142 - lesson:LSN-0143

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0142
- Description: Verify management recovery is not complete runtime capability
- Implementation: `file:docs/checkpoints/GATE-6-CP-0001/audit-harness/run_full_verification.py`, `file:scripts/iacode/gates/lint.py`
- Test: `file:tests/test_gate6_experience.py`
- Negative test: `file:tests/test_gate6_experience.py`, `checkpoint:FINDINGS.json`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/checkpoints/GATE-6-CP-0001/PLAN.md`
- Validation: _none_
- Guardrail: `file:.iacode/memory/guardrails/registry.json`

### LESSON-REQ-0143 - lesson:LSN-0144

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0143
- Description: Verify raw archived observations retain original context rather than becoming active relocated documents
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_
