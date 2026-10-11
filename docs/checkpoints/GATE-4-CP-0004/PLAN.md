# Plan — Gate 4 fresh-session independent re-audit

Audit checkpoint `GATE-4-CP-0004`. Immutable subject: sealed checkpoint `GATE-4-CP-0003`,
canonical tag `refs/tags/iacode-checkpoints/GATE-4-CP-0003`, sealed commit
`5d47200fde08c47b7a6410be2204b4c1b9fbadc1`, and content commit
`4d0cc8e3bb9a329e50af99cf58f01c19087c3433`.

This is an audit-only run. It will not implement corrections. Allowed writes are this audit
checkpoint, its attestation, the integrity anchor owed to the sealed subject, `LATEST.md`, and the
generated review bundle outside Git.

## Independence and attribution

- Role: Gate 4 independent reviewer and Red Team in a later session.
- Tool: Codex desktop application.
- Provider: OpenAI.
- Model: GPT-5 family as exposed by this task; no more specific runtime label will be invented.
- Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT`.
- Cross-tool validation: `NOT_AVAILABLE`; this is independent of the implementing run, not a
  cross-tool milestone audit.
- Scope: Gate 4 only. M2 remains pending and Gate 5 is not authorised.

## Frozen audit criteria

The criteria below are fixed before substantive execution. Results may populate them but may not
remove, narrow, waive or weaken them.

| ID | Criterion | Required evidence and acceptance |
|---|---|---|
| G4A-01 | Subject identity and immutability | Local and remote branch/tag, subject state, sealed commit, content commit and tree agree; the subject is unchanged. |
| G4A-02 | Review bundle identity | The handed-off ZIP matches its declared digest and size and passes CRC, safe-path, uniqueness, manifest, checksum, mandatory-file and secret validation. |
| G4A-03 | Bundle completeness | The manifest contains the complete checkpoint, truthful changeset, and canonical migrations, schemas and policies required for review. |
| G4A-04 | Bundle determinism and portability | Two independent builds from the sealed subject are byte-identical and validation passes from a transport clone without local-only inputs. |
| G4A-05 | Local checkpoint validity | Subject validation, integrity, memory and remote synchronization pass before substantive audit execution. |
| G4A-06 | Published detached validity | A transport clone checks out the subject tag detached and validates without local object-store or worktree state. |
| G4A-07 | Historical compatibility | Every sealed predecessor and evidence commit remains valid and reachable from published refs. |
| G4A-08 | Canonical denominator | The subject's 216 rows and the audit's 198 rows match independently derived canonical sources as sets. |
| G4A-09 | Requirement evidence | Every mandatory Gate and lesson requirement is complete with resolvable implementation, test, negative-test, documentation, validation and guardrail evidence where required. |
| G4A-10 | Quality contracts | Closed versioned models reject missing, extra, wrong-typed, duplicate, contradictory and unsupported values and round-trip without loss. |
| G4A-11 | Detection and planning | Supported stacks, mixed roots and non-applicable cases produce deterministic frozen plans without untrusted expansion. |
| G4A-12 | Sandbox-only runners | Every project command uses a pinned no-network Gate 3 sandbox; no host, API, worker or evaluator process executes project code. |
| G4A-13 | Evidence immutability | Evidence is content-bound, provenance-complete, immutable and re-hashed before verdict use. |
| G4A-14 | Verdict derivation | Missing, denied, failed, cancelled, timed-out, unknown, stale, contradictory or unresolved mandatory inputs derive `FAIL`; callers cannot submit `PASS`. |
| G4A-15 | Durable lifecycle | Planning, execution, persistence, restart recovery, idempotency, cancellation and timeout ordering remain durable and fail closed. |
| G4A-16 | Ownership and origin | Early, late, cross-owner and forged results are refused before storage or workflow signalling. |
| G4A-17 | API and runtime integration | Bounded quality data traverses the real API, Temporal, Agent Runtime and Sandbox boundaries without prose overriding failure. |
| G4A-18 | Functional PASS and FAIL | Passing and deliberately failing fixtures traverse the complete real path and derive truthful evidence-backed verdicts. |
| G4A-19 | IACode self-evaluation and reproduction | The sealed tree passes its canonical profile; stored inputs reproduce equivalent results under a distinct run without rewriting history. |
| G4A-20 | Recovery, cancellation and timeout | Live adverse lifecycle paths reach truthful terminal states after cleanup without duplicate results. |
| G4A-21 | Cross-Gate regression | Gates 0–3 and their integration remain green under the Gate 4 tree. |
| G4A-22 | Full clean-clone verification | The complete non-fast verifier runs in a published transport clone and every mandatory stage passes. |
| G4A-23 | Test and count integrity | Suites are rediscovered without double counting; every discovered test passes and stored counts re-derive. |
| G4A-24 | Security and dependencies | Secret, dependency, injection, isolation and telemetry controls pass without narrowed sources or unavailable-source false PASS. |
| G4A-25 | Documentation and architecture | Architecture, ADRs, runbooks, development and version docs agree with executed behavior and preserve Gate boundaries. |
| G4A-26 | Lessons and guardrails | The preflight is fresh, every applicable lesson is represented, all guarded lessons resolve to effective controls and no guardrail failure exists. |
| G4A-27 | G4-F-001 closure | The corrective implementation proves canonical scanner ownership and pre-persistence containment on exact serialized bytes. |
| G4A-28 | G4-X7 live evaluator path | A canonical synthetic marker assembled only in memory is detected before persistence; the activity returns sanitized `ERROR`, the verdict is `FAIL`, object and metadata stores remain empty, resolution provides no valid evidence, and logs/reports contain no marker value. |
| G4A-29 | Scanner failure | An unavailable or throwing scanner fails closed before any lookup, stat, upload or metadata write and produces no valid evidence. |
| G4A-30 | Legacy persisted object | A pre-existing secret-bearing object is rescanned on resolve, refused and cannot support a verdict. |
| G4A-31 | Independent review | Code, architecture, maintainability, regressions, evidence and docs have Critical=0, High=0 and no unresolved blocking finding. |
| G4A-32 | Independent Red Team | The mandatory A–Q battery and the explicit scanner/legacy/bundle attacks execute over valid null controls with zero escapes. |
| G4A-33 | Audit checkpoint assurance | Green Keeper, completeness, internal Red Team, closure mirror, inventory, provenance, checkpoint integrity, secret scan and remote state pass for the audit checkpoint. |
| G4A-34 | Gate verdict | Only if G4A-01–G4A-33 pass, the audit attestation names the sealed subject, `secondToolValidation` is `PASSED`, review is `APPROVED`, Red Team is `RED_TEAM_PASS`, and this audit checkpoint reaches `GATE_PASS`. |

## Execution order

1. Anchor the sealed subject and reproduce identity, publication, bundle and detached validation.
2. Review the accumulated Gate 4 implementation, architecture, requirements, evidence and docs.
3. Execute focused regressions and a purpose-built independent G4-X7/scanner/legacy probe.
4. Run the complete verifier and clean-clone checks, including live-service and cross-Gate paths.
5. Execute the independent Red Team over valid null controls and consolidate all findings.
6. Derive the review verdict and, only on success, write the audit attestation and Gate verdict.
7. Complete the audit's 198-row matrix, Green Keeper, completeness, internal controls, inventory,
   finalization, commit, seal, anchor/tag publication, remote verification and final bundle.

## Stop and continuation rules

- A real Critical or High finding, escaped mandatory attack, incomplete requirement or failing
  mandatory gate produces `REWORK_REQUIRED` or `BLOCKED`; no product correction is made here.
- Scanner absence or failure, any persisted prohibited marker, any valid recovery of rejected bytes,
  a leaked marker in logs/evidence, or a nonterminal evaluator workflow is blocking.
- Unexpected Git/state divergence produces `DIVERGENCE.md` and `BLOCKED`; history is not rewritten.
- Gate 5 is never started in this run regardless of verdict.
