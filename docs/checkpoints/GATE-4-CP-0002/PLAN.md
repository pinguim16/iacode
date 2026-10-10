# Plan — Gate 4 fresh-session independent audit

Audit checkpoint `GATE-4-CP-0002`. Immutable subject: sealed checkpoint `GATE-4-CP-0001`, canonical
tag `refs/tags/iacode-checkpoints/GATE-4-CP-0001`, commit
`70a22e824705f414e0c295bbdf89187db9b391f7`, and sealed bundle
`artifacts/review/GATE-4-CP-0001-sealed.zip` at SHA-256
`af98bb766d34beaf82f1d9963fc77377816a3cad9a850671313c528ea8701df7`.

This is an audit-only run. It may write this audit checkpoint, the attestation about the sealed
subject, the integrity anchor owed to that subject, `LATEST.md`, and post-seal review artifacts. It
may not change product code, tests, policies, engineering-memory source, the sealed subject, any
historical tag, or start Gate 5.

## Independence and attribution

- Role: Gate 4 independent reviewer and Red Team, in a new session.
- Tool: Codex desktop application.
- Provider: OpenAI.
- Model: GPT-5 family as exposed by this task; exact runtime variant is not exposed to repository
  code and will not be invented.
- Fresh session: true; this task was created separately from the implementing session.
- Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT`.
- Cross-tool validation: `NOT_AVAILABLE`; this audit is independent of the implementing run, not
  independent of the tool, and it cannot claim `MILESTONE_EXTERNAL_PASS`.
- Scope of verdict: Gate 4 only. M2 remains pending because Gates 5–7 are outside this audit and are
  not implemented.

## Frozen audit criteria

The criteria below are fixed before substantive execution. Results may populate them but may not
remove, narrow, waive, or weaken them after observation.

| ID | Criterion | Required evidence and acceptance |
|---|---|---|
| G4A-01 | Subject identity and immutability | Local and remote canonical tag, subject status, exact commit and tree agree; the subject remains byte-for-byte unchanged. |
| G4A-02 | Sealed bundle identity | The supplied ZIP exists at the expected SHA-256 and passes CRC, safe-path, manifest, checksum, mandatory-file and secret validation. |
| G4A-03 | Local checkpoint validity | Subject checkpoint validation, integrity validation, lesson validation and remote synchronization pass before audit execution. |
| G4A-04 | Published detached validity | A transport clone of the authorised remote checks out the subject tag detached and validates without access to uncommitted or local-only repository state. |
| G4A-05 | Historical compatibility | Every sealed predecessor remains resolvable and valid under the current controls; every evidence commit is reachable from a published reference. |
| G4A-06 | Canonical denominator | The subject's 194 rows and this audit's independently derived 195 rows match their canonical Gate, lesson and audit-policy sources as sets, not only as counts. |
| G4A-07 | Requirement evidence | Every mandatory requirement is complete with resolvable implementation, test, negative-test, documentation, validation and guardrail evidence where required. |
| G4A-08 | Quality contracts | Closed, versioned quality models reject missing, extra, wrong-typed, duplicate, contradictory and unsupported values with truthful reasons and round-trip without loss. |
| G4A-09 | Detection and planning | Python, Node, TypeScript, Angular, Maven, Gradle, multi-root and non-applicable cases derive deterministic frozen plans without untrusted scope expansion. |
| G4A-10 | Sandbox-only runners | Every project command uses a pinned, content-addressed, no-network Gate 3 sandbox profile; no host, API, worker or evaluator process executes project code. |
| G4A-11 | Evidence immutability | Evidence bytes and references are content-bound, provenance-complete, secret-scanned, immutable and re-hashed before verdict use. |
| G4A-12 | Verdict derivation | Missing, denied, failed, cancelled, timed-out, unknown, contradictory, stale or unresolved mandatory results derive FAIL; callers cannot submit a PASS verdict. |
| G4A-13 | Durable lifecycle | Planning, queueing, execution, persistence, restart recovery, idempotency, cancellation and timeout ordering remain durable and fail closed. |
| G4A-14 | Ownership and origin | Agent-run ownership and sandbox-origin checks refuse early, late, cross-owner and forged results before storage or workflow signalling. |
| G4A-15 | API and Agent Runtime integration | Bounded plan/result data traverse the real API, Temporal workflow, Agent Runtime and sandbox boundaries without prose overriding a quality failure. |
| G4A-16 | Passing functional path | A passing fixture traverses the real complete stack and derives PASS with stored evidence. |
| G4A-17 | Failing functional path | A failing fixture traverses the same path and preserves the failed check, finding and evidence while deriving FAIL. |
| G4A-18 | IACode self-evaluation | The committed subject tree is evaluated by its canonical profile and agrees with repository mandatory gates. |
| G4A-19 | Reproduction | Stored inputs reproduce the same plan identity and equivalent results under a distinct run identity without rewriting the original. |
| G4A-20 | Recovery, cancellation and timeout | Live restart, cancellation and policy deadline scenarios reach truthful terminal states after sandbox cleanup with no duplicate result. |
| G4A-21 | Cross-Gate regression | Gate 0–3 foundation, Model Gateway, Agent Runtime and Sandbox integration remain green under the Gate 4 tree. |
| G4A-22 | Full clean-clone verification | The complete non-fast verifier runs in a fresh transport clone of the subject and every one of its 42 stages passes. |
| G4A-23 | Test and count integrity | Counted suites are rediscovered without double counting; every discovered test passes and stored counts equal their owning artifacts. |
| G4A-24 | Security and dependency position | Secret scans, dependency scans, injection boundaries, filesystem/network/process isolation and low-cardinality telemetry controls pass without narrowed sources. |
| G4A-25 | Documentation and architecture | Architecture, ADRs, runbooks, development, version, entry and model-usage documents agree with executed behavior and preserve Gate boundaries. |
| G4A-26 | Lessons and guardrails | The preflight is fresh, all applicable lessons appear in the matrix, every `GUARDED` lesson resolves to an effective control, and no guardrail failure is present. |
| G4A-27 | Independent review | Code, architecture, maintainability, regressions, evidence and docs are reviewed; Critical=0, High=0, with no blocking unresolved finding. |
| G4A-28 | Independent Red Team | The mandatory false-PASS battery and additional bundle, evidence, origin, timeout, cancellation and policy attacks execute over a valid null control with zero escapes. |
| G4A-29 | Green Keeper | All policy-owned mandatory gates execute after audit artifacts that affect assurance are written and pass with zero remaining failure. |
| G4A-30 | Delivery completeness | The 195-row audit matrix has 100% coverage, 100% evidence coverage, zero PARTIAL and zero MISSING; functional evidence resolves. |
| G4A-31 | Closure mirror and checkpoint integrity | The clean-clone Milestone Closure Auditor, checkpoint validation, counts, provenance, inventory, secret scan, anchor chain and remote state all pass for the audit checkpoint. |
| G4A-32 | Attestation and Gate verdict | Only if G4A-01–G4A-31 pass, a later-checkpoint attestation truthfully names the sealed subject and this run records independent review, Red Team and `GATE_PASS`; M2 remains pending and Gate 5 does not start. |

## Execution order

1. Finish baseline, anchor the sealed subject, run the lesson preflight and derive requirements.
2. Validate subject identity, bundle, published history, detached checkout and historical evidence.
3. Review the Gate 4 architecture and the complete 194-row subject evidence set.
4. Run the complete 42-stage verification in a clean published clone and preserve its raw report.
5. Reproduce the Gate 4 functional, recovery, cancellation, timeout and false-PASS evidence.
6. Execute the independent Red Team over a valid null control and consolidate findings.
7. Audit documentation, memory, guardrails, counts, provenance, risks and cross-Gate integration.
8. Derive the independent review verdict; if it passes, write the attestation about the sealed
   subject before final assurance.
9. Run Green Keeper, Delivery Completeness Validator, internal Red Team and clean-clone Milestone
   Closure Auditor over the audit checkpoint itself.
10. Declare every changed path, finalize, commit, seal, validate detached, push branch and tag,
    confirm remote synchronization and build the final review archive.

## Stop and continuation rules

- A Critical or High finding, escaped mandatory attack, incomplete requirement or failing mandatory
  gate produces `REWORK_REQUIRED` or `BLOCKED`; no product correction is made in this audit.
- An unavailable required service or source produces the policy's blocking status, never PASS.
- A LOW finding may be recorded as non-blocking only when it contradicts no frozen acceptance
  criterion and the auditor implements no correction.
- Unexpected Git/state divergence produces `DIVERGENCE.md` and `BLOCKED`; history is not rewritten.
- Gate 5 is never started in this session, regardless of verdict.
