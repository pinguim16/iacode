# Closure Requirements - GATE-7-CP-0001

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/GATE-7-CHECKLIST.md, the canonical GATE-7 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

## Requirements

| ID | Source | Anchor | Mandatory | Implementation | Final | Description |
|---|---|---|---|---|---|---|
| `REQ-0001` | GATE_SPECIFICATION | `canonical:GATE-7#1.1` | yes | `PARTIAL` | `PARTIAL` | A separately authorized checkpoint starts after valid sealed Gate 6 internal closure and anchors every sealed predecessor without rewriting history. |
| `REQ-0002` | GATE_SPECIFICATION | `canonical:GATE-7#1.2` | yes | `PARTIAL` | `PARTIAL` | The checklist and registry agree exactly; all canonical, lesson and audit requirements are extracted before baseline and implementation. |
| `REQ-0003` | GATE_SPECIFICATION | `canonical:GATE-7#1.3` | yes | `PARTIAL` | `PARTIAL` | Structural ADRs define source authority, rights, derivation/index identity, persistence, citations, invalidation and recovery before behavior changes. |
| `REQ-0004` | GATE_SPECIFICATION | `canonical:GATE-7#1.4` | yes | `PARTIAL` | `PARTIAL` | The provider-neutral knowledge library uses shared closed contracts and declared source/store ports; it has no provider, host/tool execution, graph, memory or training authority. |
| `REQ-0005` | GATE_SPECIFICATION | `canonical:GATE-7#1.5` | yes | `PARTIAL` | `PARTIAL` | All inherited gates, suites and full-verifier stages remain; complete knowledge build/tests and live acceptance are added to their canonical registries. |
| `REQ-0006` | GATE_SPECIFICATION | `canonical:GATE-7#2.1` | yes | `PARTIAL` | `PARTIAL` | Ingestion selects an exact project/source/revision and stable request identity; callers cannot submit replacement source text, arbitrary paths/URLs, rights or quality verdicts. |
| `REQ-0007` | GATE_SPECIFICATION | `canonical:GATE-7#2.2` | yes | `PARTIAL` | `PARTIAL` | Curated source admission consumes a closed operator-controlled registry with project, source identity, exact content digest, ownership, license, explicit storage/RAG grants, evidence and finite validity. |
| `REQ-0008` | GATE_SPECIFICATION | `canonical:GATE-7#2.3` | yes | `PARTIAL` | `PARTIAL` | Unknown, denied, missing, expired, revoked, conflicting or mismatched source permission fails closed before any index effect or disclosure; training/distillation remain denied. |
| `REQ-0009` | GATE_SPECIFICATION | `canonical:GATE-7#2.4` | yes | `PARTIAL` | `PARTIAL` | Existing experiences are admitted only through their owning validation and effective permissions; storage-only, withdrawn, expired, corrupt or cross-project experiences cannot support knowledge. |
| `REQ-0010` | GATE_SPECIFICATION | `canonical:GATE-7#2.5` | yes | `PARTIAL` | `PARTIAL` | Every contributor's permissions and provenance constrain the derived document, all chunks and exports; no derived permission exceeds a source grant. |
| `REQ-0011` | GATE_SPECIFICATION | `canonical:GATE-7#2.6` | yes | `PARTIAL` | `PARTIAL` | Source resolution is bounded and confined to the configured curated root; traversal, symlinks/reparse escape, nonregular files, missing/changed bytes and invalid UTF-8 are refused without network fetch or execution. |
| `REQ-0012` | GATE_SPECIFICATION | `canonical:GATE-7#2.7` | yes | `PARTIAL` | `PARTIAL` | Full exact normalized source, derived records and delivered payloads are scanned with canonical credential detection and known authorization forms; scanner failure refuses safely. |
| `REQ-0013` | GATE_SPECIFICATION | `canonical:GATE-7#2.8` | yes | `PARTIAL` | `PARTIAL` | Private/transcript fields, prompts, provider answers and runtime secrets are not admitted or echoed in knowledge, diagnostics, audit facts or errors. Source content is untrusted data, never instructions or authority. |
| `REQ-0014` | GATE_SPECIFICATION | `canonical:GATE-7#3.1` | yes | `PARTIAL` | `PARTIAL` | Versioned closed schemas define source identity, provenance, document/chunk/index version, exact digests, citations, query and results; unknown fields and ambiguous JSON are refused. |
| `REQ-0015` | GATE_SPECIFICATION | `canonical:GATE-7#3.2` | yes | `PARTIAL` | `PARTIAL` | Consumed policy bounds request/source/result bytes, types, nesting, text/chunks/tokens, query size, result count, candidate work and retention; callers cannot widen ceilings. |
| `REQ-0016` | GATE_SPECIFICATION | `canonical:GATE-7#3.3` | yes | `PARTIAL` | `PARTIAL` | Deterministic derivation preserves exact source spans and hashes, handles Unicode/line endings explicitly and records the transformation version without inventing summaries or facts. |
| `REQ-0017` | GATE_SPECIFICATION | `canonical:GATE-7#3.4` | yes | `PARTIAL` | `PARTIAL` | Index identity binds source revision/digest, grant/provenance and derivation policy; restart/retry cannot silently change identity, duplicate chunks or rewrite immutable content. |
| `REQ-0018` | GATE_SPECIFICATION | `canonical:GATE-7#3.5` | yes | `PARTIAL` | `PARTIAL` | Actual persistent inverted indexing supports bounded parameterized lexical matching, deterministic relevance ordering and stable ties; no fixed response or production in-memory fallback is used. |
| `REQ-0019` | GATE_SPECIFICATION | `canonical:GATE-7#3.6` | yes | `PARTIAL` | `PARTIAL` | Empty/no-match queries and invalid/oversized inputs have explicit semantics; capacity or dependency failures cannot masquerade as a successful empty result or silently partial search. |
| `REQ-0020` | GATE_SPECIFICATION | `canonical:GATE-7#4.1` | yes | `PARTIAL` | `PARTIAL` | Alembic and ORM agree on the real PostgreSQL knowledge schema, ownership, constraints and indexes; up/down/from-zero/autogenerate preserve inherited data. |
| `REQ-0021` | GATE_SPECIFICATION | `canonical:GATE-7#4.2` | yes | `PARTIAL` | `PARTIAL` | Source admission, immutable document/chunks/index and minimal audit fact commit atomically; failed validation or dependency/write failure leaves no partial publication. |
| `REQ-0022` | GATE_SPECIFICATION | `canonical:GATE-7#4.3` | yes | `PARTIAL` | `PARTIAL` | Stable request/source identity makes accepted-response-loss and concurrent retries idempotent; conflicting retries are refused and cannot reset retention or resurrect withdrawn revisions. |
| `REQ-0023` | GATE_SPECIFICATION | `canonical:GATE-7#4.4` | yes | `PARTIAL` | `PARTIAL` | Persisted body, digest, chunk spans/tokens, source/grant and envelope are revalidated before delivery; direct database corruption cannot yield valid retrieval or citation. |
| `REQ-0024` | GATE_SPECIFICATION | `canonical:GATE-7#4.5` | yes | `PARTIAL` | `PARTIAL` | Restart/rebuild preserves truthful current revisions, rights and index version; stale or incompatible index is unavailable until an actual valid rebuild, never silently served. |
| `REQ-0025` | GATE_SPECIFICATION | `canonical:GATE-7#5.1` | yes | `PARTIAL` | `PARTIAL` | Every ingestion, inspect/list, search, citation/export and invalidation requires configured authenticated runtime transport; alternate unauthenticated paths cannot reach effects/data. |
| `REQ-0026` | GATE_SPECIFICATION | `canonical:GATE-7#5.2` | yes | `PARTIAL` | `PARTIAL` | Every lookup/index/query/citation is project-bound before data access; cross-project identifiers and enumeration cannot disclose content, digests or modify state. |
| `REQ-0027` | GATE_SPECIFICATION | `canonical:GATE-7#5.3` | yes | `PARTIAL` | `PARTIAL` | Every returned knowledge excerpt has a resolvable exact source/revision/content digest, chunk digest and source span; no output can omit/fabricate a citation or outrun its source rights. |
| `REQ-0028` | GATE_SPECIFICATION | `canonical:GATE-7#5.4` | yes | `PARTIAL` | `PARTIAL` | Retrieval is measured against a versioned varied corpus and predefined relevant/irrelevant expectations; bounded relevance and deterministic ranking are demonstrated, not asserted. |
| `REQ-0029` | GATE_SPECIFICATION | `canonical:GATE-7#5.5` | yes | `PARTIAL` | `PARTIAL` | Queries do not become durable content or sensitive logs; stable bounded errors/correlation never expose input, paths, credentials, exception text or SQL. |
| `REQ-0030` | GATE_SPECIFICATION | `canonical:GATE-7#5.6` | yes | `PARTIAL` | `PARTIAL` | Knowledge is cited untrusted evidence only; it cannot submit a tool result, change a quality verdict, widen an approval or execute host/source instructions. |
| `REQ-0031` | GATE_SPECIFICATION | `canonical:GATE-7#6.1` | yes | `PARTIAL` | `PARTIAL` | Revocation, source change/removal, expiry and explicit withdrawal immediately deny stale index/citation use independently of background sweeping. |
| `REQ-0032` | GATE_SPECIFICATION | `canonical:GATE-7#6.2` | yes | `PARTIAL` | `PARTIAL` | Replacing a source revision atomically invalidates the prior publication; superseded excerpts never mix with the new revision and stable retries preserve terminal facts. |
| `REQ-0033` | GATE_SPECIFICATION | `canonical:GATE-7#6.3` | yes | `PARTIAL` | `PARTIAL` | Finite consumed retention and an owned bounded automatic sweeper physically purge primary knowledge/chunk payloads and retain only finite minimal safe tombstones/audit facts. |
| `REQ-0034` | GATE_SPECIFICATION | `canonical:GATE-7#6.4` | yes | `PARTIAL` | `PARTIAL` | Authenticated project-bound invalidation/withdrawal is idempotent and does not delete sources, experiences, quality evidence or another project's records. |
| `REQ-0035` | GATE_SPECIFICATION | `canonical:GATE-7#6.5` | yes | `PARTIAL` | `PARTIAL` | Dependency/sweeper failures and shutdown are observable and bounded; restore must reconcile current grants, withdrawals, source versions and time before exposure. |
| `REQ-0036` | GATE_SPECIFICATION | `canonical:GATE-7#7.1` | yes | `PARTIAL` | `PARTIAL` | Fresh actual-stack acceptance admits a rights-qualified validation corpus, indexes real persisted content, measures retrieval and resolves exact citations through authenticated HTTP. |
| `REQ-0037` | GATE_SPECIFICATION | `canonical:GATE-7#7.2` | yes | `PARTIAL` | `PARTIAL` | Live proof exercises restart, replay, denied Gate 6 reuse, cross-project/auth attacks, current-source invalidation, retention/withdrawal, corrupt recovery and unchanged inherited resources. |
| `REQ-0038` | GATE_SPECIFICATION | `canonical:GATE-7#7.3` | yes | `PARTIAL` | `PARTIAL` | Every test owns its namespace/resources and observes cleanup; no global Docker/editor state or other applications are changed. |
| `REQ-0039` | GATE_SPECIFICATION | `canonical:GATE-7#7.4` | yes | `PARTIAL` | `PARTIAL` | One complete non-fast verifier invocation at an exact published immutable subject includes every inherited/new mandatory stage; partial reruns or stale producers cannot produce PASS. |
| `REQ-0040` | GATE_SPECIFICATION | `canonical:GATE-7#7.5` | yes | `PARTIAL` | `PARTIAL` | Safe exact producer bytes, subject/fingerprint/process identities and actual cleanup outcomes survive fallible postprocessing; original failures remain immutable and transported byte-exactly. |
| `REQ-0041` | GATE_SPECIFICATION | `canonical:GATE-7#8.1` | yes | `PARTIAL` | `PARTIAL` | Runbooks document sources/grants, default denial, index/search/citations, all endpoints/auth, invalidation/rebuild, retention/restore, privacy, ranking and operational limits. |
| `REQ-0042` | GATE_SPECIFICATION | `canonical:GATE-7#8.2` | yes | `PARTIAL` | `PARTIAL` | All selected lessons and requirements have specific implementation, executed positive/adverse tests, documentation and resolvable evidence without false PASS or waived controls. |
| `REQ-0043` | GATE_SPECIFICATION | `canonical:GATE-7#8.3` | yes | `NOT_STARTED` | `NOT_STARTED` | Complete test/quality, whole Green Keeper, total completeness, fresh internal Red Team/VALID null control and full clean-clone closure mirror pass in order against unchanged source. |
| `REQ-0044` | GATE_SPECIFICATION | `canonical:GATE-7#8.4` | yes | `PARTIAL` | `PARTIAL` | Current tooling validates all sealed predecessors and successor/promotion positive paths; no historical subject, tag, denominator or promotion rule is rewritten. |
| `REQ-0045` | GATE_SPECIFICATION | `canonical:GATE-7#8.5` | yes | `NOT_STARTED` | `NOT_STARTED` | A milestone consolidation covers Gates 4–7, integration, requirements, tests, regressions, lessons/guards, ADRs, risks/debt, provenance and observed cost/model usage without invented figures. |
| `REQ-0046` | GATE_SPECIFICATION | `canonical:GATE-7#8.6` | yes | `PARTIAL` | `PARTIAL` | All changed paths are declared before finalization; commands, counts, provenance, retrospective, risks and exact continuation are truthful and reproducible. |
| `REQ-0047` | GATE_SPECIFICATION | `canonical:GATE-7#8.7` | yes | `NOT_STARTED` | `NOT_STARTED` | Canonical finalization, Gate 7-only committed content, post-commit sealing, publication and exact immutable review reconstruction actually succeed. |
| `REQ-0048` | GATE_SPECIFICATION | `canonical:GATE-7#8.8` | yes | `PARTIAL` | `PARTIAL` | The milestone delivery is sealed READY_FOR_REVIEW with no blockers; independent review/Red Team stay PENDING, second-tool PENDING_MANUAL and M2 PENDING. No self-attestation or Gate 8 advance occurs. |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | yes | `PARTIAL` | `PARTIAL` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a required protocol transition must never turn a mandatory gate red |
| `LESSON-REQ-0030` | LESSON | `lesson:LSN-0031` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an empty applicable set is not a missing required set, and a control must tell them apart |
| `LESSON-REQ-0031` | LESSON | `lesson:LSN-0032` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts |
| `LESSON-REQ-0032` | LESSON | `lesson:LSN-0033` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a value bound in middleware is absent in the handlers that run outside it |
| `LESSON-REQ-0033` | LESSON | `lesson:LSN-0034` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify re-deriving what the framework already computed diverges from the framework |
| `LESSON-REQ-0034` | LESSON | `lesson:LSN-0035` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work |
| `LESSON-REQ-0035` | LESSON | `lesson:LSN-0036` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a gate that runs inside an image measures the image, not the source |
| `LESSON-REQ-0036` | LESSON | `lesson:LSN-0037` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves |
| `LESSON-REQ-0037` | LESSON | `lesson:LSN-0038` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify two representations of one concept in one module disagree, and the safer one loses |
| `LESSON-REQ-0038` | LESSON | `lesson:LSN-0039` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a test that writes to the operational database leaves production data behind |
| `LESSON-REQ-0039` | LESSON | `lesson:LSN-0040` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a control that judges sealed history only runs once a successor anchors it |
| `LESSON-REQ-0040` | LESSON | `lesson:LSN-0041` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing |
| `LESSON-REQ-0041` | LESSON | `lesson:LSN-0042` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone |
| `LESSON-REQ-0042` | LESSON | `lesson:LSN-0043` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a log line is not evidence that another process is ready |
| `LESSON-REQ-0043` | LESSON | `lesson:LSN-0044` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module |
| `LESSON-REQ-0044` | LESSON | `lesson:LSN-0045` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a counted test suite must declare its cases statically, because the denominator is read from the source |
| `LESSON-REQ-0045` | LESSON | `lesson:LSN-0046` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a timeout that cancels the task it runs in leaves nothing able to record what happened |
| `LESSON-REQ-0046` | LESSON | `lesson:LSN-0047` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a refusal that misnames the defect spends the only repair on the wrong correction |
| `LESSON-REQ-0047` | LESSON | `lesson:LSN-0048` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a state and the event that explains it, written in two commits, are written event first |
| `LESSON-REQ-0048` | LESSON | `lesson:LSN-0049` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a metric read the instant after the call that moved it is read before the scrape that carries it |
| `LESSON-REQ-0049` | LESSON | `lesson:LSN-0050` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a checkpoint sealed without naming its own tag cannot be validated from that tag |
| `LESSON-REQ-0050` | LESSON | `lesson:LSN-0051` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a payload one service bounds for another must be bounded as the receiver measures it |
| `LESSON-REQ-0051` | LESSON | `lesson:LSN-0052` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both |
| `LESSON-REQ-0052` | LESSON | `lesson:LSN-0053` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a process sweep that reads what a forking process holds waits on the processes it has to kill |
| `LESSON-REQ-0053` | LESSON | `lesson:LSN-0054` | no | `NOT_STARTED` | `NOT_STARTED` | Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote |
| `LESSON-REQ-0054` | LESSON | `lesson:LSN-0055` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a contract a model must follow has to reach the model, rendered from the definition the parser enforces |
| `LESSON-REQ-0055` | LESSON | `lesson:LSN-0056` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a result is accepted only from the executor that owns the request, decided when the request is created |
| `LESSON-REQ-0056` | LESSON | `lesson:LSN-0057` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a pinned lock can become unsafe without changing, so advisory state is live evidence |
| `LESSON-REQ-0057` | LESSON | `lesson:LSN-0058` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify container health does not prove Docker Desktop host-port forwarding |
| `LESSON-REQ-0058` | LESSON | `lesson:LSN-0059` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a lesson exclusion must declare the scope it excludes |
| `LESSON-REQ-0059` | LESSON | `lesson:LSN-0060` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify parent and child facts without an ORM relationship require an explicit flush boundary |
| `LESSON-REQ-0060` | LESSON | `lesson:LSN-0061` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify cancellation completion must not bypass cleanup acknowledgement |
| `LESSON-REQ-0061` | LESSON | `lesson:LSN-0062` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify provenance digests are a set even when their sources are distinct |
| `LESSON-REQ-0062` | LESSON | `lesson:LSN-0063` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an identity shared across services must satisfy the strictest persistence type and remain stable |
| `LESSON-REQ-0063` | LESSON | `lesson:LSN-0064` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a shared execution resource needs an explicit exclusive owner for every owning domain |
| `LESSON-REQ-0064` | LESSON | `lesson:LSN-0065` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a shared execution identifier must not be written into a foreign key owned by another domain |
| `LESSON-REQ-0065` | LESSON | `lesson:LSN-0066` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify immutable content identity excludes observation time and the first observer |
| `LESSON-REQ-0066` | LESSON | `lesson:LSN-0067` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify cancellation semantics must survive orchestration-library exception wrapping |
| `LESSON-REQ-0067` | LESSON | `lesson:LSN-0068` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a bounded parser must apply each content limit only to content it interprets |
| `LESSON-REQ-0068` | LESSON | `lesson:LSN-0069` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a polyglot plan binds each check to both its project root and its toolchain |
| `LESSON-REQ-0069` | LESSON | `lesson:LSN-0070` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify project discovery must separate deployable roots, nested fixtures and check applicability |
| `LESSON-REQ-0070` | LESSON | `lesson:LSN-0071` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify every quality image must provision snapshots on its oldest runtime and prepare each isolated check |
| `LESSON-REQ-0071` | LESSON | `lesson:LSN-0072` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify secret findings and reviewed false positives must share one policy-owned taxonomy |
| `LESSON-REQ-0072` | LESSON | `lesson:LSN-0073` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify the canonical lint denominator must cover every detected project root |
| `LESSON-REQ-0073` | LESSON | `lesson:LSN-0074` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an importable source tree is not an installed or repository-configured test environment |
| `LESSON-REQ-0074` | LESSON | `lesson:LSN-0075` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify offline package installation requires its build backend inside the quality image |
| `LESSON-REQ-0075` | LESSON | `lesson:LSN-0076` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify projected nested configuration requires an explicit monorepo root |
| `LESSON-REQ-0076` | LESSON | `lesson:LSN-0077` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify harness wait bounds must reflect workload size without changing product deadlines |
| `LESSON-REQ-0077` | LESSON | `lesson:LSN-0078` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence recorders must resolve caller-supplied commit references before execution |
| `LESSON-REQ-0078` | LESSON | `lesson:LSN-0079` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify test discovery and the unit runner must cover the same project scope |
| `LESSON-REQ-0079` | LESSON | `lesson:LSN-0080` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a failed verification stage must not leave an older PASS report addressable |
| `LESSON-REQ-0080` | LESSON | `lesson:LSN-0081` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify canonical requirement evidence must name a test the repository actually discovers |
| `LESSON-REQ-0081` | LESSON | `lesson:LSN-0082` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify engineering memory cannot depend on an ephemeral generated report |
| `LESSON-REQ-0082` | LESSON | `lesson:LSN-0083` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a command that decodes captured UTF-8 must also configure the stream that re-emits it |
| `LESSON-REQ-0083` | LESSON | `lesson:LSN-0084` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a historical Gate documentation test must derive the current entry-point state |
| `LESSON-REQ-0084` | LESSON | `lesson:LSN-0085` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a source-based control must assert syntax semantics rather than formatter layout |
| `LESSON-REQ-0085` | LESSON | `lesson:LSN-0086` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a subprocess assertion must preserve the exit code when both streams are empty |
| `LESSON-REQ-0086` | LESSON | `lesson:LSN-0087` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a rehearsal worker must register every workflow activity boundary |
| `LESSON-REQ-0087` | LESSON | `lesson:LSN-0088` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a test inside a built image can consume only inputs copied into that image |
| `LESSON-REQ-0088` | LESSON | `lesson:LSN-0089` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify domain not-applicability and operational failure need distinct orchestration outcomes |
| `LESSON-REQ-0089` | LESSON | `lesson:LSN-0090` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a clean-clone control must use only versioned configuration inputs |
| `LESSON-REQ-0090` | LESSON | `lesson:LSN-0091` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify secret detection must run on the exact bytes at the durable evidence boundary |
| `LESSON-REQ-0091` | LESSON | `lesson:LSN-0092` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify canonical audit parsers must consume every bounded sealed report rendering |
| `LESSON-REQ-0092` | LESSON | `lesson:LSN-0093` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify disposable control repositories must carry every imported repository package |
| `LESSON-REQ-0093` | LESSON | `lesson:LSN-0094` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a review bundle must include unchanged canonical artifact categories |
| `LESSON-REQ-0094` | LESSON | `lesson:LSN-0095` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a complete verifier must own its Compose runtime by checkout |
| `LESSON-REQ-0095` | LESSON | `lesson:LSN-0096` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence publishers must consume the producer's canonical result schema |
| `LESSON-REQ-0096` | LESSON | `lesson:LSN-0097` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a review-bundle declaration must bind an immutable reconstruction subject |
| `LESSON-REQ-0097` | LESSON | `lesson:LSN-0098` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify accepted cancellation must be enforced from durable state across activity boundaries |
| `LESSON-REQ-0098` | LESSON | `lesson:LSN-0099` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a refused subject is an attempted input, not executed commit evidence |
| `LESSON-REQ-0099` | LESSON | `lesson:LSN-0100` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify pre-seal detached validation must bind the explicit subject namespace |
| `LESSON-REQ-0100` | LESSON | `lesson:LSN-0101` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a structural record and its canonical index are one atomic change |
| `LESSON-REQ-0101` | LESSON | `lesson:LSN-0102` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify assurance denominators must derive category counts from the current source set |
| `LESSON-REQ-0102` | LESSON | `lesson:LSN-0103` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify adversarial fixtures must hash the complete validated contract |
| `LESSON-REQ-0103` | LESSON | `lesson:LSN-0104` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify intermediate closure and independent validation must have unambiguous contracts |
| `LESSON-REQ-0104` | LESSON | `lesson:LSN-0105` | yes | `PARTIAL` | `PARTIAL` | Verify new behavioral tests must satisfy the unchanged source-quality contract |
| `LESSON-REQ-0105` | LESSON | `lesson:LSN-0106` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a security repair must execute at the causal output boundary, not a similarly shaped branch |
| `LESSON-REQ-0106` | LESSON | `lesson:LSN-0107` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify an adversarial marker must satisfy the canonical detector before it can judge containment |
| `LESSON-REQ-0107` | LESSON | `lesson:LSN-0108` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify evidence timestamp transport must preserve RFC3339 rather than a shell locale rendering |
| `LESSON-REQ-0108` | LESSON | `lesson:LSN-0109` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify regression counts and evidence must exclude only policy-bound live input repositories |
| `LESSON-REQ-0109` | LESSON | `lesson:LSN-0110` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a timed-out live proof retains bounded diagnostics before owned cleanup |
| `LESSON-REQ-0110` | LESSON | `lesson:LSN-0111` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify polling watcher cleanup must preserve completed checks and accepted cancellation |
| `LESSON-REQ-0111` | LESSON | `lesson:LSN-0112` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify canonical scanner consumers must share transport decoding, not only patterns |
| `LESSON-REQ-0112` | LESSON | `lesson:LSN-0113` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify stronger delivery controls must follow the immutable subject policy version |
| `LESSON-REQ-0113` | LESSON | `lesson:LSN-0114` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify transport line metadata must not repeatedly scan the source prefix |
| `LESSON-REQ-0114` | LESSON | `lesson:LSN-0115` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a failing full verifier retains every bounded case identifier beyond its output tail |
| `LESSON-REQ-0115` | LESSON | `lesson:LSN-0116` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a live resumability pointer is generated after Git boundaries, not committed into its own subject |
| `LESSON-REQ-0116` | LESSON | `lesson:LSN-0117` | yes | `PARTIAL` | `PARTIAL` | Verify an architecture rollup must not contradict the delivered capability described below it |
| `LESSON-REQ-0117` | LESSON | `lesson:LSN-0118` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify post-response validation failures must preserve an accepted mutation's uncertain outcome |
| `LESSON-REQ-0118` | LESSON | `lesson:LSN-0119` | yes | `PARTIAL` | `PARTIAL` | Verify a clean publication scan does not replace the stricter checkpoint secret scan |
| `LESSON-REQ-0119` | LESSON | `lesson:LSN-0120` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify native installation proofs must resolve the installed CLI entrypoint |
| `LESSON-REQ-0120` | LESSON | `lesson:LSN-0121` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify standard-library host probes must not initialize application dependency graphs |
| `LESSON-REQ-0121` | LESSON | `lesson:LSN-0122` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify engine-allocated host ports must be rediscovered after container restart |
| `LESSON-REQ-0122` | LESSON | `lesson:LSN-0123` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify consent binds workspace identity, not an uncanonicalized path spelling |
| `LESSON-REQ-0123` | LESSON | `lesson:LSN-0124` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify durable editor recovery must not use an in-memory test host |
| `LESSON-REQ-0124` | LESSON | `lesson:LSN-0125` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify native parent exit is not proof of process and profile cleanup |
| `LESSON-REQ-0125` | LESSON | `lesson:LSN-0126` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify known authentication material is not domain or presentation data |
| `LESSON-REQ-0126` | LESSON | `lesson:LSN-0127` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify fresh runtime health does not initialize an operator-managed model catalog |
| `LESSON-REQ-0127` | LESSON | `lesson:LSN-0128` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify adversarial premises must use the actual public contract |
| `LESSON-REQ-0128` | LESSON | `lesson:LSN-0129` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify repeated cancellation must preserve an already cancelled terminal result |
| `LESSON-REQ-0129` | LESSON | `lesson:LSN-0130` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify executable export line endings belong to the source and packaging contract |
| `LESSON-REQ-0130` | LESSON | `lesson:LSN-0131` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify raw evidence digests require byte-preserving Git export, not text normalization |
| `LESSON-REQ-0131` | LESSON | `lesson:LSN-0132` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify owned Git clones need read-only-aware cleanup, not native-profile lock retry |
| `LESSON-REQ-0132` | LESSON | `lesson:LSN-0133` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify shared field names do not imply shared schema types |
| `LESSON-REQ-0133` | LESSON | `lesson:LSN-0134` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify configuration classifiers consume decoded values, not dotenv quote syntax |
| `LESSON-REQ-0134` | LESSON | `lesson:LSN-0135` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify capture producer evidence before fallible interpretation or owned cleanup |
| `LESSON-REQ-0135` | LESSON | `lesson:LSN-0136` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify strict JSON validation loses transport context |
| `LESSON-REQ-0136` | LESSON | `lesson:LSN-0137` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify sQL text interprets inline JSON colons as bindings |
| `LESSON-REQ-0137` | LESSON | `lesson:LSN-0138` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify secret projection distinguishes public identities from authorization secrets |
| `LESSON-REQ-0138` | LESSON | `lesson:LSN-0139` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify privacy projection begins in the source query |
| `LESSON-REQ-0139` | LESSON | `lesson:LSN-0140` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify summaries preserve canonical continuation structure |
| `LESSON-REQ-0140` | LESSON | `lesson:LSN-0141` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify preflight checks honor every declared applicability dimension |
| `LESSON-REQ-0141` | LESSON | `lesson:LSN-0142` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify local Engine recovery keeps transport and cleanup scoped |
| `LESSON-REQ-0142` | LESSON | `lesson:LSN-0143` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify management recovery is not complete runtime capability |
| `LESSON-REQ-0143` | LESSON | `lesson:LSN-0144` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify raw archived observations retain original context rather than becoming active relocated documents |
| `LESSON-REQ-0144` | LESSON | `lesson:LSN-0145` | yes | `PARTIAL` | `PARTIAL` | Verify a new persistent capability must extend the explicit structural contract, not bypass its exact inventory |
| `LESSON-REQ-0145` | LESSON | `lesson:LSN-0146` | yes | `PARTIAL` | `PARTIAL` | Verify a completed command record is not proof that its producing process has exited |
| `LESSON-REQ-0146` | LESSON | `lesson:LSN-0147` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify framework lifecycle errors need bounded identities as well as test methods |
| `LESSON-REQ-0147` | LESSON | `lesson:LSN-0148` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify minimal protocol fixtures inherit control contracts, never deployment-owned source data |
| `LESSON-REQ-0148` | LESSON | `lesson:LSN-0149` | yes | `NOT_STARTED` | `NOT_STARTED` | Verify a shell exit zero is not a produced digest or verified original evidence |

## Evidence

### REQ-0001 - canonical:GATE-7#1.1

- Source reference: docs/GATE-7-CHECKLIST.md row 1.1
- Description: A separately authorized checkpoint starts after valid sealed Gate 6 internal closure and anchors every sealed predecessor without rewriting history.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0002 - canonical:GATE-7#1.2

- Source reference: docs/GATE-7-CHECKLIST.md row 1.2
- Description: The checklist and registry agree exactly; all canonical, lesson and audit requirements are extracted before baseline and implementation.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0003 - canonical:GATE-7#1.3

- Source reference: docs/GATE-7-CHECKLIST.md row 1.3
- Description: Structural ADRs define source authority, rights, derivation/index identity, persistence, citations, invalidation and recovery before behavior changes.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0004 - canonical:GATE-7#1.4

- Source reference: docs/GATE-7-CHECKLIST.md row 1.4
- Description: The provider-neutral knowledge library uses shared closed contracts and declared source/store ports; it has no provider, host/tool execution, graph, memory or training authority.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0005 - canonical:GATE-7#1.5

- Source reference: docs/GATE-7-CHECKLIST.md row 1.5
- Description: All inherited gates, suites and full-verifier stages remain; complete knowledge build/tests and live acceptance are added to their canonical registries.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0006 - canonical:GATE-7#2.1

- Source reference: docs/GATE-7-CHECKLIST.md row 2.1
- Description: Ingestion selects an exact project/source/revision and stable request identity; callers cannot submit replacement source text, arbitrary paths/URLs, rights or quality verdicts.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0007 - canonical:GATE-7#2.2

- Source reference: docs/GATE-7-CHECKLIST.md row 2.2
- Description: Curated source admission consumes a closed operator-controlled registry with project, source identity, exact content digest, ownership, license, explicit storage/RAG grants, evidence and finite validity.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0008 - canonical:GATE-7#2.3

- Source reference: docs/GATE-7-CHECKLIST.md row 2.3
- Description: Unknown, denied, missing, expired, revoked, conflicting or mismatched source permission fails closed before any index effect or disclosure; training/distillation remain denied.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0009 - canonical:GATE-7#2.4

- Source reference: docs/GATE-7-CHECKLIST.md row 2.4
- Description: Existing experiences are admitted only through their owning validation and effective permissions; storage-only, withdrawn, expired, corrupt or cross-project experiences cannot support knowledge.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0010 - canonical:GATE-7#2.5

- Source reference: docs/GATE-7-CHECKLIST.md row 2.5
- Description: Every contributor's permissions and provenance constrain the derived document, all chunks and exports; no derived permission exceeds a source grant.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0011 - canonical:GATE-7#2.6

- Source reference: docs/GATE-7-CHECKLIST.md row 2.6
- Description: Source resolution is bounded and confined to the configured curated root; traversal, symlinks/reparse escape, nonregular files, missing/changed bytes and invalid UTF-8 are refused without network fetch or execution.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0012 - canonical:GATE-7#2.7

- Source reference: docs/GATE-7-CHECKLIST.md row 2.7
- Description: Full exact normalized source, derived records and delivered payloads are scanned with canonical credential detection and known authorization forms; scanner failure refuses safely.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0013 - canonical:GATE-7#2.8

- Source reference: docs/GATE-7-CHECKLIST.md row 2.8
- Description: Private/transcript fields, prompts, provider answers and runtime secrets are not admitted or echoed in knowledge, diagnostics, audit facts or errors. Source content is untrusted data, never instructions or authority.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0014 - canonical:GATE-7#3.1

- Source reference: docs/GATE-7-CHECKLIST.md row 3.1
- Description: Versioned closed schemas define source identity, provenance, document/chunk/index version, exact digests, citations, query and results; unknown fields and ambiguous JSON are refused.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0015 - canonical:GATE-7#3.2

- Source reference: docs/GATE-7-CHECKLIST.md row 3.2
- Description: Consumed policy bounds request/source/result bytes, types, nesting, text/chunks/tokens, query size, result count, candidate work and retention; callers cannot widen ceilings.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0016 - canonical:GATE-7#3.3

- Source reference: docs/GATE-7-CHECKLIST.md row 3.3
- Description: Deterministic derivation preserves exact source spans and hashes, handles Unicode/line endings explicitly and records the transformation version without inventing summaries or facts.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0017 - canonical:GATE-7#3.4

- Source reference: docs/GATE-7-CHECKLIST.md row 3.4
- Description: Index identity binds source revision/digest, grant/provenance and derivation policy; restart/retry cannot silently change identity, duplicate chunks or rewrite immutable content.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0018 - canonical:GATE-7#3.5

- Source reference: docs/GATE-7-CHECKLIST.md row 3.5
- Description: Actual persistent inverted indexing supports bounded parameterized lexical matching, deterministic relevance ordering and stable ties; no fixed response or production in-memory fallback is used.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0019 - canonical:GATE-7#3.6

- Source reference: docs/GATE-7-CHECKLIST.md row 3.6
- Description: Empty/no-match queries and invalid/oversized inputs have explicit semantics; capacity or dependency failures cannot masquerade as a successful empty result or silently partial search.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0020 - canonical:GATE-7#4.1

- Source reference: docs/GATE-7-CHECKLIST.md row 4.1
- Description: Alembic and ORM agree on the real PostgreSQL knowledge schema, ownership, constraints and indexes; up/down/from-zero/autogenerate preserve inherited data.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0021 - canonical:GATE-7#4.2

- Source reference: docs/GATE-7-CHECKLIST.md row 4.2
- Description: Source admission, immutable document/chunks/index and minimal audit fact commit atomically; failed validation or dependency/write failure leaves no partial publication.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0022 - canonical:GATE-7#4.3

- Source reference: docs/GATE-7-CHECKLIST.md row 4.3
- Description: Stable request/source identity makes accepted-response-loss and concurrent retries idempotent; conflicting retries are refused and cannot reset retention or resurrect withdrawn revisions.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0023 - canonical:GATE-7#4.4

- Source reference: docs/GATE-7-CHECKLIST.md row 4.4
- Description: Persisted body, digest, chunk spans/tokens, source/grant and envelope are revalidated before delivery; direct database corruption cannot yield valid retrieval or citation.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0024 - canonical:GATE-7#4.5

- Source reference: docs/GATE-7-CHECKLIST.md row 4.5
- Description: Restart/rebuild preserves truthful current revisions, rights and index version; stale or incompatible index is unavailable until an actual valid rebuild, never silently served.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0025 - canonical:GATE-7#5.1

- Source reference: docs/GATE-7-CHECKLIST.md row 5.1
- Description: Every ingestion, inspect/list, search, citation/export and invalidation requires configured authenticated runtime transport; alternate unauthenticated paths cannot reach effects/data.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0026 - canonical:GATE-7#5.2

- Source reference: docs/GATE-7-CHECKLIST.md row 5.2
- Description: Every lookup/index/query/citation is project-bound before data access; cross-project identifiers and enumeration cannot disclose content, digests or modify state.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0027 - canonical:GATE-7#5.3

- Source reference: docs/GATE-7-CHECKLIST.md row 5.3
- Description: Every returned knowledge excerpt has a resolvable exact source/revision/content digest, chunk digest and source span; no output can omit/fabricate a citation or outrun its source rights.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0028 - canonical:GATE-7#5.4

- Source reference: docs/GATE-7-CHECKLIST.md row 5.4
- Description: Retrieval is measured against a versioned varied corpus and predefined relevant/irrelevant expectations; bounded relevance and deterministic ranking are demonstrated, not asserted.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0029 - canonical:GATE-7#5.5

- Source reference: docs/GATE-7-CHECKLIST.md row 5.5
- Description: Queries do not become durable content or sensitive logs; stable bounded errors/correlation never expose input, paths, credentials, exception text or SQL.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0030 - canonical:GATE-7#5.6

- Source reference: docs/GATE-7-CHECKLIST.md row 5.6
- Description: Knowledge is cited untrusted evidence only; it cannot submit a tool result, change a quality verdict, widen an approval or execute host/source instructions.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0031 - canonical:GATE-7#6.1

- Source reference: docs/GATE-7-CHECKLIST.md row 6.1
- Description: Revocation, source change/removal, expiry and explicit withdrawal immediately deny stale index/citation use independently of background sweeping.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0032 - canonical:GATE-7#6.2

- Source reference: docs/GATE-7-CHECKLIST.md row 6.2
- Description: Replacing a source revision atomically invalidates the prior publication; superseded excerpts never mix with the new revision and stable retries preserve terminal facts.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0033 - canonical:GATE-7#6.3

- Source reference: docs/GATE-7-CHECKLIST.md row 6.3
- Description: Finite consumed retention and an owned bounded automatic sweeper physically purge primary knowledge/chunk payloads and retain only finite minimal safe tombstones/audit facts.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0034 - canonical:GATE-7#6.4

- Source reference: docs/GATE-7-CHECKLIST.md row 6.4
- Description: Authenticated project-bound invalidation/withdrawal is idempotent and does not delete sources, experiences, quality evidence or another project's records.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0035 - canonical:GATE-7#6.5

- Source reference: docs/GATE-7-CHECKLIST.md row 6.5
- Description: Dependency/sweeper failures and shutdown are observable and bounded; restore must reconcile current grants, withdrawals, source versions and time before exposure.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: `command:cmd-0055`, `command:cmd-0042`, `command:cmd-0081`
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0036 - canonical:GATE-7#7.1

- Source reference: docs/GATE-7-CHECKLIST.md row 7.1
- Description: Fresh actual-stack acceptance admits a rights-qualified validation corpus, indexes real persisted content, measures retrieval and resolves exact citations through authenticated HTTP.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0037 - canonical:GATE-7#7.2

- Source reference: docs/GATE-7-CHECKLIST.md row 7.2
- Description: Live proof exercises restart, replay, denied Gate 6 reuse, cross-project/auth attacks, current-source invalidation, retention/withdrawal, corrupt recovery and unchanged inherited resources.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0038 - canonical:GATE-7#7.3

- Source reference: docs/GATE-7-CHECKLIST.md row 7.3
- Description: Every test owns its namespace/resources and observes cleanup; no global Docker/editor state or other applications are changed.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0039 - canonical:GATE-7#7.4

- Source reference: docs/GATE-7-CHECKLIST.md row 7.4
- Description: One complete non-fast verifier invocation at an exact published immutable subject includes every inherited/new mandatory stage; partial reruns or stale producers cannot produce PASS.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0040 - canonical:GATE-7#7.5

- Source reference: docs/GATE-7-CHECKLIST.md row 7.5
- Description: Safe exact producer bytes, subject/fingerprint/process identities and actual cleanup outcomes survive fallible postprocessing; original failures remain immutable and transported byte-exactly.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0041 - canonical:GATE-7#8.1

- Source reference: docs/GATE-7-CHECKLIST.md row 8.1
- Description: Runbooks document sources/grants, default denial, index/search/citations, all endpoints/auth, invalidation/rebuild, retention/restore, privacy, ranking and operational limits.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0042 - canonical:GATE-7#8.2

- Source reference: docs/GATE-7-CHECKLIST.md row 8.2
- Description: All selected lessons and requirements have specific implementation, executed positive/adverse tests, documentation and resolvable evidence without false PASS or waived controls.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0043 - canonical:GATE-7#8.3

- Source reference: docs/GATE-7-CHECKLIST.md row 8.3
- Description: Complete test/quality, whole Green Keeper, total completeness, fresh internal Red Team/VALID null control and full clean-clone closure mirror pass in order against unchanged source.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0044 - canonical:GATE-7#8.4

- Source reference: docs/GATE-7-CHECKLIST.md row 8.4
- Description: Current tooling validates all sealed predecessors and successor/promotion positive paths; no historical subject, tag, denominator or promotion rule is rewritten.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0045 - canonical:GATE-7#8.5

- Source reference: docs/GATE-7-CHECKLIST.md row 8.5
- Description: A milestone consolidation covers Gates 4–7, integration, requirements, tests, regressions, lessons/guards, ADRs, risks/debt, provenance and observed cost/model usage without invented figures.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0046 - canonical:GATE-7#8.6

- Source reference: docs/GATE-7-CHECKLIST.md row 8.6
- Description: All changed paths are declared before finalization; commands, counts, provenance, retrospective, risks and exact continuation are truthful and reproducible.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### REQ-0047 - canonical:GATE-7#8.7

- Source reference: docs/GATE-7-CHECKLIST.md row 8.7
- Description: Canonical finalization, Gate 7-only committed content, post-commit sealing, publication and exact immutable review reconstruction actually succeed.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0048 - canonical:GATE-7#8.8

- Source reference: docs/GATE-7-CHECKLIST.md row 8.8
- Description: The milestone delivery is sealed READY_FOR_REVIEW with no blockers; independent review/Red Team stay PENDING, second-tool PENDING_MANUAL and M2 PENDING. No self-attestation or Gate 8 advance occurs.
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0013 - lesson:LSN-0013

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0013
- Description: Verify an installed capability must be detected by resolved path, not by a bare command lookup
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0024 - lesson:LSN-0024

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0024
- Description: Verify a control is finished only when its positive path has been executed, not only its refusals
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0025 - lesson:LSN-0025

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0025
- Description: Verify a generic guardrail derives repository state instead of naming today's checkpoint
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0026 - lesson:LSN-0026

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0026
- Description: Verify an adversarial battery without a null-mutation control proves nothing
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0027 - lesson:LSN-0027

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0027
- Description: Verify a lesson's prose may record a residual limit but may never contradict its status
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0028 - lesson:LSN-0028

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0028
- Description: Verify a configuration key that no code reads is a defect, not documentation
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0029 - lesson:LSN-0029

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0029
- Description: Verify a required protocol transition must never turn a mandatory gate red
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0030 - lesson:LSN-0031

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0030
- Description: Verify an empty applicable set is not a missing required set, and a control must tell them apart
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0031 - lesson:LSN-0032

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0031
- Description: Verify a control written while one Gate was the only Gate stops being a control when the next one starts
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0032 - lesson:LSN-0033

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0032
- Description: Verify a value bound in middleware is absent in the handlers that run outside it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0033 - lesson:LSN-0034

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0033
- Description: Verify re-deriving what the framework already computed diverges from the framework
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0034 - lesson:LSN-0035

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0034
- Description: Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0035 - lesson:LSN-0036

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0035
- Description: Verify a gate that runs inside an image measures the image, not the source
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0036 - lesson:LSN-0037

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0036
- Description: Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0037 - lesson:LSN-0038

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0037
- Description: Verify two representations of one concept in one module disagree, and the safer one loses
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0038 - lesson:LSN-0039

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0038
- Description: Verify a test that writes to the operational database leaves production data behind
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0039 - lesson:LSN-0040

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0039
- Description: Verify a control that judges sealed history only runs once a successor anchors it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0040 - lesson:LSN-0041

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0040
- Description: Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0041 - lesson:LSN-0042

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0041
- Description: Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0042 - lesson:LSN-0043

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0042
- Description: Verify a log line is not evidence that another process is ready
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0043 - lesson:LSN-0044

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0043
- Description: Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0044 - lesson:LSN-0045

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0044
- Description: Verify a counted test suite must declare its cases statically, because the denominator is read from the source
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0045 - lesson:LSN-0046

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0045
- Description: Verify a timeout that cancels the task it runs in leaves nothing able to record what happened
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0046 - lesson:LSN-0047

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0046
- Description: Verify a refusal that misnames the defect spends the only repair on the wrong correction
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0047 - lesson:LSN-0048

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0047
- Description: Verify a state and the event that explains it, written in two commits, are written event first
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0048 - lesson:LSN-0049

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0048
- Description: Verify a metric read the instant after the call that moved it is read before the scrape that carries it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0049 - lesson:LSN-0050

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0049
- Description: Verify a checkpoint sealed without naming its own tag cannot be validated from that tag
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0050 - lesson:LSN-0051

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0050
- Description: Verify a payload one service bounds for another must be bounded as the receiver measures it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0051 - lesson:LSN-0052

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0051
- Description: Verify two processes that meet on a queue must name what crosses it once, and a real run must exercise both
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0052 - lesson:LSN-0053

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0052
- Description: Verify a process sweep that reads what a forking process holds waits on the processes it has to kill
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0053 - lesson:LSN-0054

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0053
- Description: Verify a pre-push check narrower than the change's reach lets a red gate reach the public remote
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0054 - lesson:LSN-0055

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0054
- Description: Verify a contract a model must follow has to reach the model, rendered from the definition the parser enforces
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0055 - lesson:LSN-0056

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0055
- Description: Verify a result is accepted only from the executor that owns the request, decided when the request is created
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0056 - lesson:LSN-0057

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0056
- Description: Verify a pinned lock can become unsafe without changing, so advisory state is live evidence
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0057 - lesson:LSN-0058

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0057
- Description: Verify container health does not prove Docker Desktop host-port forwarding
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0058 - lesson:LSN-0059

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0058
- Description: Verify a lesson exclusion must declare the scope it excludes
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0059 - lesson:LSN-0060

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0059
- Description: Verify parent and child facts without an ORM relationship require an explicit flush boundary
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0060 - lesson:LSN-0061

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0060
- Description: Verify cancellation completion must not bypass cleanup acknowledgement
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0061 - lesson:LSN-0062

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0061
- Description: Verify provenance digests are a set even when their sources are distinct
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0062 - lesson:LSN-0063

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0062
- Description: Verify an identity shared across services must satisfy the strictest persistence type and remain stable
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0063 - lesson:LSN-0064

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0063
- Description: Verify a shared execution resource needs an explicit exclusive owner for every owning domain
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0064 - lesson:LSN-0065

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0064
- Description: Verify a shared execution identifier must not be written into a foreign key owned by another domain
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0065 - lesson:LSN-0066

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0065
- Description: Verify immutable content identity excludes observation time and the first observer
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0066 - lesson:LSN-0067

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0066
- Description: Verify cancellation semantics must survive orchestration-library exception wrapping
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0067 - lesson:LSN-0068

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0067
- Description: Verify a bounded parser must apply each content limit only to content it interprets
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0068 - lesson:LSN-0069

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0068
- Description: Verify a polyglot plan binds each check to both its project root and its toolchain
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0069 - lesson:LSN-0070

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0069
- Description: Verify project discovery must separate deployable roots, nested fixtures and check applicability
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0070 - lesson:LSN-0071

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0070
- Description: Verify every quality image must provision snapshots on its oldest runtime and prepare each isolated check
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0071 - lesson:LSN-0072

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0071
- Description: Verify secret findings and reviewed false positives must share one policy-owned taxonomy
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0072 - lesson:LSN-0073

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0072
- Description: Verify the canonical lint denominator must cover every detected project root
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0073 - lesson:LSN-0074

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0073
- Description: Verify an importable source tree is not an installed or repository-configured test environment
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0074 - lesson:LSN-0075

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0074
- Description: Verify offline package installation requires its build backend inside the quality image
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0075 - lesson:LSN-0076

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0075
- Description: Verify projected nested configuration requires an explicit monorepo root
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0076 - lesson:LSN-0077

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0076
- Description: Verify harness wait bounds must reflect workload size without changing product deadlines
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0077 - lesson:LSN-0078

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0077
- Description: Verify evidence recorders must resolve caller-supplied commit references before execution
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0078 - lesson:LSN-0079

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0078
- Description: Verify test discovery and the unit runner must cover the same project scope
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0079 - lesson:LSN-0080

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0079
- Description: Verify a failed verification stage must not leave an older PASS report addressable
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0080 - lesson:LSN-0081

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0080
- Description: Verify canonical requirement evidence must name a test the repository actually discovers
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0081 - lesson:LSN-0082

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0081
- Description: Verify engineering memory cannot depend on an ephemeral generated report
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0082 - lesson:LSN-0083

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0082
- Description: Verify a command that decodes captured UTF-8 must also configure the stream that re-emits it
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0083 - lesson:LSN-0084

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0083
- Description: Verify a historical Gate documentation test must derive the current entry-point state
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0084 - lesson:LSN-0085

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0084
- Description: Verify a source-based control must assert syntax semantics rather than formatter layout
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0085 - lesson:LSN-0086

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0085
- Description: Verify a subprocess assertion must preserve the exit code when both streams are empty
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0086 - lesson:LSN-0087

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0086
- Description: Verify a rehearsal worker must register every workflow activity boundary
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0087 - lesson:LSN-0088

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0087
- Description: Verify a test inside a built image can consume only inputs copied into that image
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0088 - lesson:LSN-0089

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0088
- Description: Verify domain not-applicability and operational failure need distinct orchestration outcomes
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0089 - lesson:LSN-0090

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0089
- Description: Verify a clean-clone control must use only versioned configuration inputs
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0090 - lesson:LSN-0091

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0090
- Description: Verify secret detection must run on the exact bytes at the durable evidence boundary
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0091 - lesson:LSN-0092

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0091
- Description: Verify canonical audit parsers must consume every bounded sealed report rendering
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0092 - lesson:LSN-0093

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0092
- Description: Verify disposable control repositories must carry every imported repository package
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0093 - lesson:LSN-0094

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0093
- Description: Verify a review bundle must include unchanged canonical artifact categories
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0094 - lesson:LSN-0095

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0094
- Description: Verify a complete verifier must own its Compose runtime by checkout
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0095 - lesson:LSN-0096

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0095
- Description: Verify evidence publishers must consume the producer's canonical result schema
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0096 - lesson:LSN-0097

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0096
- Description: Verify a review-bundle declaration must bind an immutable reconstruction subject
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0097 - lesson:LSN-0098

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0097
- Description: Verify accepted cancellation must be enforced from durable state across activity boundaries
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0098 - lesson:LSN-0099

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0098
- Description: Verify a refused subject is an attempted input, not executed commit evidence
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0099 - lesson:LSN-0100

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0099
- Description: Verify pre-seal detached validation must bind the explicit subject namespace
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0100 - lesson:LSN-0101

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0100
- Description: Verify a structural record and its canonical index are one atomic change
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0101 - lesson:LSN-0102

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0101
- Description: Verify assurance denominators must derive category counts from the current source set
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0102 - lesson:LSN-0103

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0102
- Description: Verify adversarial fixtures must hash the complete validated contract
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0103 - lesson:LSN-0104

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0103
- Description: Verify intermediate closure and independent validation must have unambiguous contracts
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0104 - lesson:LSN-0105

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0104
- Description: Verify new behavioral tests must satisfy the unchanged source-quality contract
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0105 - lesson:LSN-0106

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0105
- Description: Verify a security repair must execute at the causal output boundary, not a similarly shaped branch
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0106 - lesson:LSN-0107

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0106
- Description: Verify an adversarial marker must satisfy the canonical detector before it can judge containment
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0107 - lesson:LSN-0108

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0107
- Description: Verify evidence timestamp transport must preserve RFC3339 rather than a shell locale rendering
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0108 - lesson:LSN-0109

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0108
- Description: Verify regression counts and evidence must exclude only policy-bound live input repositories
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0109 - lesson:LSN-0110

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0109
- Description: Verify a timed-out live proof retains bounded diagnostics before owned cleanup
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0110 - lesson:LSN-0111

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0110
- Description: Verify polling watcher cleanup must preserve completed checks and accepted cancellation
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0111 - lesson:LSN-0112

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0111
- Description: Verify canonical scanner consumers must share transport decoding, not only patterns
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0112 - lesson:LSN-0113

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0112
- Description: Verify stronger delivery controls must follow the immutable subject policy version
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0113 - lesson:LSN-0114

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0113
- Description: Verify transport line metadata must not repeatedly scan the source prefix
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0114 - lesson:LSN-0115

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0114
- Description: Verify a failing full verifier retains every bounded case identifier beyond its output tail
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0115 - lesson:LSN-0116

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0115
- Description: Verify a live resumability pointer is generated after Git boundaries, not committed into its own subject
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0116 - lesson:LSN-0117

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0116
- Description: Verify an architecture rollup must not contradict the delivered capability described below it
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0117 - lesson:LSN-0118

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0117
- Description: Verify post-response validation failures must preserve an accepted mutation's uncertain outcome
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0118 - lesson:LSN-0119

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0118
- Description: Verify a clean publication scan does not replace the stricter checkpoint secret scan
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0119 - lesson:LSN-0120

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0119
- Description: Verify native installation proofs must resolve the installed CLI entrypoint
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0120 - lesson:LSN-0121

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0120
- Description: Verify standard-library host probes must not initialize application dependency graphs
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0121 - lesson:LSN-0122

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0121
- Description: Verify engine-allocated host ports must be rediscovered after container restart
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0122 - lesson:LSN-0123

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0122
- Description: Verify consent binds workspace identity, not an uncanonicalized path spelling
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0123 - lesson:LSN-0124

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0123
- Description: Verify durable editor recovery must not use an in-memory test host
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0124 - lesson:LSN-0125

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0124
- Description: Verify native parent exit is not proof of process and profile cleanup
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0125 - lesson:LSN-0126

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0125
- Description: Verify known authentication material is not domain or presentation data
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0126 - lesson:LSN-0127

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0126
- Description: Verify fresh runtime health does not initialize an operator-managed model catalog
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0127 - lesson:LSN-0128

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0127
- Description: Verify adversarial premises must use the actual public contract
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0128 - lesson:LSN-0129

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0128
- Description: Verify repeated cancellation must preserve an already cancelled terminal result
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0129 - lesson:LSN-0130

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0129
- Description: Verify executable export line endings belong to the source and packaging contract
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0130 - lesson:LSN-0131

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0130
- Description: Verify raw evidence digests require byte-preserving Git export, not text normalization
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0131 - lesson:LSN-0132

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0131
- Description: Verify owned Git clones need read-only-aware cleanup, not native-profile lock retry
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0132 - lesson:LSN-0133

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0132
- Description: Verify shared field names do not imply shared schema types
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0133 - lesson:LSN-0134

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0133
- Description: Verify configuration classifiers consume decoded values, not dotenv quote syntax
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0134 - lesson:LSN-0135

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0134
- Description: Verify capture producer evidence before fallible interpretation or owned cleanup
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0135 - lesson:LSN-0136

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0135
- Description: Verify strict JSON validation loses transport context
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0136 - lesson:LSN-0137

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0136
- Description: Verify sQL text interprets inline JSON colons as bindings
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0137 - lesson:LSN-0138

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0137
- Description: Verify secret projection distinguishes public identities from authorization secrets
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0138 - lesson:LSN-0139

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0138
- Description: Verify privacy projection begins in the source query
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0139 - lesson:LSN-0140

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0139
- Description: Verify summaries preserve canonical continuation structure
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0140 - lesson:LSN-0141

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0140
- Description: Verify preflight checks honor every declared applicability dimension
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0141 - lesson:LSN-0142

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0141
- Description: Verify local Engine recovery keeps transport and cleanup scoped
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0142 - lesson:LSN-0143

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0142
- Description: Verify management recovery is not complete runtime capability
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0143 - lesson:LSN-0144

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0143
- Description: Verify raw archived observations retain original context rather than becoming active relocated documents
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0144 - lesson:LSN-0145

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0144
- Description: Verify a new persistent capability must extend the explicit structural contract, not bypass its exact inventory
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0145 - lesson:LSN-0146

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0145
- Description: Verify a completed command record is not proof that its producing process has exited
- Implementation: `file:services/knowledge/src/iacode_knowledge/domain.py`, `file:apps/api/src/iacode_api/knowledge/store.py`
- Test: _none_
- Negative test: _none_
- Documentation: `checkpoint:PLAN.md`, `checkpoint:CURRENT-PROGRESS.json`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0146 - lesson:LSN-0147

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0146
- Description: Verify framework lifecycle errors need bounded identities as well as test methods
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0147 - lesson:LSN-0148

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0147
- Description: Verify minimal protocol fixtures inherit control contracts, never deployment-owned source data
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0148 - lesson:LSN-0149

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0148
- Description: Verify a shell exit zero is not a produced digest or verified original evidence
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_
