# M2 consolidation - Gates 4 through 7

## Verdict boundary and authoritative state

This is the implementing session's consolidation, not an independent milestone attestation.
The current delivery state and executed evidence belong to
[Gate7 STATE](GATE-7-CP-0001/STATE.json), [steps](GATE-7-CP-0001/STEPS.json) and
[command ledger](GATE-7-CP-0001/COMMANDS.jsonl). Actual terminal state and sealing are established
only by canonical tool records and the checkpoint tag, not predicted by this preseal document.
A successful implementing handoff must be sealed
READY_FOR_REVIEW, with independent review and Red Team PENDING, second-tool PENDING_MANUAL,
M2 PENDING and external attestation NONE. None of those independent verdicts is supplied here.
Gate8 is neither implemented nor authorized by this document.

## Accumulated delivery and immutable owners

| Gate | Sealed owner or current implementing owner | Responsibility |
|---|---|---|
| 4 | [GATE-4-CP-0010](GATE-4-CP-0010/STATE.json), INTERNAL_GATE_PASS | Derived quality evidence, anti-forgery and immutable review reconstruction. |
| 5 | [GATE-5-CP-0001](GATE-5-CP-0001/STATE.json), INTERNAL_GATE_PASS | Actual VS Code/native and CLI transport, consent, persistent recovery and runtime integration. |
| 6 | [GATE-6-CP-0001](GATE-6-CP-0001/STATE.json), INTERNAL_GATE_PASS | Governed Experience Store, source validation, immutable permissions and finite retention. |
| 7 | [GATE-7-CP-0001](GATE-7-CP-0001/STATE.json), current implementing delivery | Rights-qualified persistent lexical knowledge, exact citations, invalidation and M2 handoff. |

The canonical tags are `iacode-checkpoints/` followed by each checkpoint ID. Historical verdicts
remain unchanged. The checkpoint chain anchors all sealed predecessors; it does not rewrite a
subject into an independent approval. Failed Gate7 runtime-v1/v2/v3 tags remain immutable.

## Cross-Gate integration and architecture

Quality remains an owning runtime-derived decision: clients and knowledge sources cannot submit
tool results, approvals or quality verdicts. VS Code and CLI use the authenticated bounded runtime
transport and explicit source consent; accepted-response loss retains stable reconciliation
identities instead of automatically repeating effects. Experience capture validates the actual
source/quality evidence. Storage permission never becomes RAG, training or distillation permission.

Knowledge initially consumes an empty-by-default operator-curated source registry. An admitted
artifact has exact project/source/revision/content identity and explicit reviewed storage/RAG
permission. The actual owning storage-only experience remains RAG-ineligible. Parameterized
PostgreSQL inverted matching returns bounded deterministic lexical results with exact original
source spans, digests and citations. No embedding service, answer synthesis, source instruction
execution, code graph, project memory or training authority is introduced.

Publication, chunks and minimal audit facts commit atomically. Stable request/source identity,
per-source serialization and immutable material prevent duplicate or mixed publication. Reads
revalidate current source/grant/index facts; corruption or unavailable dependencies are explicit
refusals, not empty successful search. Withdrawal, source/revision change and expiry invalidate
delivery immediately. The owned finite sweeper physically purges primary payload/index content;
restart/retry/reindex cannot renew the original ceiling or resurrect withdrawal.

## Requirements and completeness

The current [canonical Gate7 checklist](../GATE-7-CHECKLIST.md) has48 rows. The latest actual
complete preflight/derivation yields150 applicable lessons and198 total requirements,
including197 mandatory rows. Actual cmd-0258 binds all198 requirements after the complete current
runtime and functional proof. Audit-only cmd-0279 then verifies198/198 complete,100 percent
implementation/evidence coverage, zero partial and zero missing, strictly after whole Green Keeper.
The [matrix](GATE-7-CP-0001/REQUIREMENTS-MATRIX.json),
[completeness report](GATE-7-CP-0001/COMPLETENESS-REPORT.json) and
[closure requirements](GATE-7-CP-0001/CLOSURE-REQUIREMENTS.json) own these observations. No smaller
set is selected by a delivery argument; the completeness role did not implement corrections.

## Execution, regressions and non-additive counts

The actual published runtime-v1 invocation cmd-0099 completed all49 non-fast stages:48 PASS,
one FAIL. The root suite reported896 tests, five failures and six errors. This invocation is
FAILED, not partial acceptance. Exact original producer bytes are retained in
[the failed-attempt manifest](GATE-7-CP-0001/attempts/RUNTIME-V1-FAILED-FULL-MANIFEST.json).
Its actual owned cleanup and preservation of unrelated container identities remain observations,
not a replacement for the failed mandatory suite.

Current targeted evidence includes actual domain/schema, API, real PostgreSQL/HTTP/migration and
owned live provider/sandbox/quality/experience/knowledge workflows. Cmd-0123 passes all35 current
Gate7 root controls; cmd-0125 passes read-only helper style checks. Targeted local passes, prior
Gate counts, verifier stages and78 live observations must not be added together as distinct test
cases. Final counts must be derived from the canonical physical collections and actual successful
complete processes, with shared run IDs deduplicated. The current [TESTS](GATE-7-CP-0001/TESTS.json),
[QUALITY](GATE-7-CP-0001/QUALITY.json) and command ledger retain those distinctions.

The completed runtime-v2 cmd-0143 is also FAIL: all49 stages execute,46 PASS and3 FAIL.
Its root producer reports942 tests with two immutable-review reconstruction errors; quality-iacode
outlives the900-second observer while still legally RUNNING, and the portability attackT escapes.
Exact originals and isolation/cleanup observations are retained in
[the v2 failed-attempt manifest](GATE-7-CP-0001/attempts/RUNTIME-V2-FAILED-FULL-MANIFEST.json).
Neither passing fragments nor retained cleanup observations turn that run into acceptance.

Current rework binds four versioned root build/verification inputs without changing legacy
subjects, uses child-only Git long-path handling, observes the unchanged canonical quality deadline,
and consumes every canonical producer from its verified durable original. Cmd-0160 passes all60
current Gate7 cases, cmd-0161 passes unchanged whole mandatory lint, and cmd-0162 passes explicit
read-only helper quality. These describe that local epoch, not current whole acceptance.

Completed runtime-v3 cmd-0180 executes49 stages,48 PASS/1 native FAIL. Its root suite, both quality
stages, actual desktop/experience/knowledge workflows and isolation/cleanup pass, but none can
promote the failed invocation. Exact originals are retained in
[the v3 manifest](GATE-7-CP-0001/attempts/RUNTIME-V3-FAILED-FULL-MANIFEST.json).
Successful-stage stdout was not retained, so detailed portability attack flags are not invented
from the aggregate quality-false-pass stage PASS. The formal fresh battery remains required.

Native rework retains51 inert original contexts, rejected/inconclusive hypotheses and actual
cmd-0195 failure. ADR-0060 keeps exact ownership/physical signals and total10s, permits1s natural
exit within it, samples the clock before success and opts out of external crash/telemetry only
in generated native hosts. Causal0188/0210 failures remain;0211 passes10 native controls,0213
all152 owning Gate5/6/7 cases,0214 helper quality,0215 whole unchanged lint and0217 two fresh
uninstrumented installation/trust/profile-removal runs on final strict source. No historical
Windows/Crashpad cause or universal OS guarantee is claimed. Cmd-0218 validates151 active
lessons/148 locally guarded. Literal NUL publication staging preserves every declared path
beyond the Windows aggregate command-line bound; actual positive/adverse0191 passes.

Public immutable runtime-v4 is3bffae5ea19653f752f171fbc1b7f7cc5973e17d at
`iacode-subjects/GATE-7-CP-0001-runtime-v4`. Actual cmd-0255 completes one non-fast public-clone
invocation:49/49 PASS, no retries or merged fragments. Its clone and owned Compose resources are
removed, shared resources and unrelated identities/running states are preserved, and the clone's
Git state stays clean. All23 safe original producers are retained by
[the exact capture manifest](GATE-7-CP-0001/attempts/FULL-PRODUCER-d869942c643b-MANIFEST.json).
The measured source fingerprint remains
`1a949f03f8cec67ce47aa37ddbb9b9447208d31c43ad6124795cb3d23c354117`.

Actual functional0257 covers35/35 canonical criteria in7 groups; whole Green Keeper262-277
passes16/16 with zero remaining failures; audit-only completeness279 verifies198/198. Fresh
post-control internal Red Team281 defends145/145 with VALID control and zero escapes, including
the detailed portabilityT flags that earlier aggregate stdout could not establish. Historical
failed candidates remain failed; no fragment fills a missing premise. Actual full clean-clone
closure mirror287 evaluates all18 dimensions:16 PASS,2 canonically derived NOT_APPLICABLE,0 FAIL.
All35 anchored tags resolve and all35 sealed predecessors validate under current tooling from
published history. The whole root suite, compileall, lessons, integrity and completeness actually
pass in a fresh clone. See [the exact mirror report](GATE-7-CP-0001/M2-INTERNAL-MIRROR.json) and
[its dimension-by-dimension record](GATE-7-CP-0001/M2-INTERNAL-MIRROR.md).
Final handoff and actual canonical seal/publication remain subsequent operations at this
observation. Their actual records and canonical tag, never this prose, establish their outcome.

## Findings, lessons and executable guardrails

The [current findings](GATE-7-CP-0001/FINDINGS.json) retain original failures and recurrence
history. Confirmed causes include current registry membership, a missing current metadata adapter,
UTF-8 re-emission, public documentation identifiers, the next Gate's reservation boundary,
minimal fixture ownership, framework lifecycle diagnostics and actual producer-byte capture.
An unchecked source preimage and a zero-exit shell with absent digest output are explicitly
refused as evidence. Repeated guarded classes are escalated, never quietly reset.

The canonical [memory](../../.iacode/memory/LESSONS.md),
[guard registry](../../.iacode/memory/guardrails/registry.json) and
[Gate7 retrospective](../../.iacode/memory/retrospectives/GATE-7-CP-0001.md) own current status.
GUARDED requires executed controls, not prose. Actual positive/adverse tests preserve inherited
assertions, exercise newly registered gate growth/removal/downgrade, keep retained-contract
broken-link refusal, and test running/failed/empty/mismatched source observations. Exact safe
originals are archived before consumers or temporary-owner cleanup can fail.

## Structural decisions

The [ADR index](../adr/README.md) preserves earlier M2 decisions. Gate7 adds
[ADR-0053](../adr/ADR-0053-knowledge-requires-content-bound-source-permission.md) for source-bound
rights, [ADR-0054](../adr/ADR-0054-knowledge-indexes-are-rebuildable-cited-projections.md) for
rebuildable cited lexical projections, [ADR-0055](../adr/ADR-0055-code-graph-remains-an-explicit-future-reservation.md)
for a RESERVED-only next boundary,
[ADR-0056](../adr/ADR-0056-minimal-protocol-fixtures-inherit-only-control-contracts.md) for
minimal protocol fixture control ownership,
[ADR-0057](../adr/ADR-0057-build-and-verification-root-inputs-follow-subject-versioned-assurance.md)
for subject-versioned build/verification root inputs,
[ADR-0058](../adr/ADR-0058-immutable-review-git-reads-use-child-scoped-long-path-handling.md)
for exact immutable reads with child-scoped Git handling,
[ADR-0059](../adr/ADR-0059-full-verifier-consumers-use-complete-canonical-archived-producers.md)
for complete canonical raw-producer consumption, and
[ADR-0060](../adr/ADR-0060-native-drain-allows-natural-exit-within-the-existing-deadline.md)
for strict owned physical drainage and bounded red native observations. No production control, promotion denominator or
historical tag is weakened to obtain a green result.

## Red Team and closure audit

Fresh internal Red Team cmd-0281 runs after whole Green Keeper and audit-only completeness. Its
nine actual process receipts pass with unchanged source; all inherited attacks remain, alongside
real knowledge domain/API/SQL/live controls. The145/145 defended attacks include a VALID clean/null
control and detailedT: deterministic, portable, categories, declaration and stale-digest refusal
all true. Safe exact original producers and process logs are retained before interpretation.
See [the report](GATE-7-CP-0001/M2-INTERNAL-RED-TEAM.json),
[the inherited original projection](GATE-7-CP-0001/M2-INHERITED-RED-TEAM.json) and
[process/original references](GATE-7-CP-0001/RED-TEAM-EXECUTIONS.json).
Same-session role separation is not independence. The full closure mirror287 covers every
canonically applicable dimension, history compatibility and actual clean-clone execution.
Its MIR-002/MIR-003 sets are empty only because the audit registry names no corrective audit
delivery/mandatory corrective attack for this checkpoint; the exact derivation is retained.
Those two NOT_APPLICABLE results are not counted as passing checks and do not waive the fresh
internal145-attack battery or the later independent M2 audit. Exact terminal transport remains
the canonical sealer's subsequent operation. No reduced scope or synthetic PASS substitutes
for these controls.

## Risks, operational debt and recovery

Permission evidence is structurally validated, not a legal-title oracle. The curator root,
operator/database and UTC clock remain trusted. Digests are not signatures or anonymization;
checks are not an atomic protocol with an arbitrary external author changing source files.
Lexical retrieval is not semantic relevance or answer correctness. Finite capacity/dependency
refusals and operational lifecycle failures remain observable. Primary purge does not prove
erasure from every backup; restore must reapply current grants, withdrawals, versions and time
before exposure. See the [Knowledge Engine runbook](../runbooks/KNOWLEDGE-ENGINE.md) and
[current risks](GATE-7-CP-0001/RISKS.md).

Docker/WSL and unrelated applications must not be restarted or stopped for these controls.
Cleanup is confined to newly created, exact verified ownership namespaces, with observed removal
and unrelated-container preservation. The four historically policy-refused temporary targets in
[Gate6 risks](GATE-6-CP-0001/RISKS.md) remain responsible-owner manual cleanup only; no alternative
API may retry them. No historical PID, fixed-name archival helper or sealed subject may be replayed.

## Provenance, reuse rights and observed model usage

Implementation is OpenAI-assisted project engineering work with locally generated evidence.
The exact model ID of this implementing session is not exposed and is not invented. Live
acceptance records the actually configured provider/model in its own producer evidence; observed
synthetic validation calls do not license user/provider content for reuse. Aggregate token cost,
billing and wall-clock totals across reused/overlapping runs are not available and are not
estimated here. See [provenance](GATE-7-CP-0001/PROVENANCE.json) and the actual command ledger.
Engineering evidence and operational sources retain denied RAG/training/distillation rights unless
their owning explicit evidence independently authorizes a particular use. Fixture-only grants
authorize only their isolated synthetic corpus. No secrets or private chain-of-thought are stored.

## Required independent M2 closure

After actual Gate7 sealing, a later separate audit checkpoint must review the milestone as a
whole: accumulated requirements, architecture, integration, regressions, documentation, lessons,
guardrails, risks and all per-Gate blind spots. It must perform fresh independent review, independent
Red Team, independent functional proof and G4-F-004 reconstruction. The latter starts from
[the original finding](GATE-4-CP-0008/FINDINGS.json) and
[the corrective closure](GATE-4-CP-0009/G4-CP-0008-FINDINGS-CLOSURE.json), reconstructing declared
review bytes from their exact immutable transported subjects, not trusting a copied declaration.
The current tools must also reconstruct the final Gate7 immutable review archive from a fresh
public clone and validate all sealed predecessors without modifying them.

Second-tool validation remains a separate manual/cross-tool obligation. A fresh-session
MILESTONE_INDEPENDENT_AUDIT_PASS is not MILESTONE_EXTERNAL_PASS, and neither substitutes for the
other. Findings return to a new implementing checkpoint; the sealed subject is never rewritten
to make it approved. Only actual independent milestone closure and explicit subsequent authority
can allow crossing M2 into Gate8. See [milestone validation](../MILESTONE-VALIDATION.md).
