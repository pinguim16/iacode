# Plan — Gate 4 fresh-session independent final audit

Audit checkpoint `GATE-4-CP-0006`. Immutable subject: sealed checkpoint `GATE-4-CP-0005`,
canonical tag `refs/tags/iacode-checkpoints/GATE-4-CP-0005`, sealed commit
`c631270e49c095a9777825c0bc18818694c07ffb`, and content commit
`cac77ddef9c351ce828442d9312db69083aab81e`.

This is an audit-only run. It will not implement corrections. Allowed writes are this audit
checkpoint, its attestation, the integrity anchor owed to the sealed subject, `LATEST.md`, and the
generated review bundle outside Git.

## Independence and attribution

- Role: Gate 4 independent reviewer and Red Team in a later fresh session.
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
| G4A-01 | Subject identity and immutability | Local and remote branch/tag, subject state, sealed commit, content commit and tree agree; the subject remains unchanged. |
| G4A-02 | Subject anchor | This successor anchors the subject tag, commit and tree into the canonical chain. |
| G4A-03 | Review bundle identity | The handed-off ZIP matches its declared digest and size and passes CRC, safe-path, uniqueness, manifest, checksum, mandatory-file and secret validation. |
| G4A-04 | Bundle determinism and portability | Two independent builds from a detached transport clone are byte-identical and validate without local-only inputs. |
| G4A-05 | Published detached validity | A transport clone checks out the subject tag detached and validates without local object-store or worktree state. |
| G4A-06 | Historical compatibility | Every sealed predecessor and evidence commit remains valid and reachable from published refs. |
| G4A-07 | Canonical requirement denominator | The subject's 221 rows and the audit's 200 rows match independently derived canonical sources as sets. |
| G4A-08 | Requirement evidence | Every subject requirement is complete with resolvable evidence; no mandatory row is partial, missing or silently inapplicable. |
| G4A-09 | Quality architecture | Contracts, detection, planning, sandbox execution, evidence immutability, verdict derivation and lifecycle remain closed, deterministic and fail-closed. |
| G4A-10 | Cross-Gate integration | Gate 4 preserves the Model Gateway, Agent Runtime and Sandbox boundaries and Gates 0–3 regressions remain green. |
| G4A-11 | Full published verification | One invocation in a fresh published clone executes all 42 canonical stages in order and passes 42/42. |
| G4A-12 | No hidden rerun | `invocationCount=1`, `retryCount=0`, `verifierRerun=false`; no isolated stage result supersedes the integral run. |
| G4A-13 | Historical infra/smoke order | `stack`, `integration`, `infra`, `smoke` remain contiguous and both `infra` and `smoke` pass in the integral run. |
| G4A-14 | Compose isolation | The verifier uses an owned project distinct from `iacode`, Docker-allocated ports and checkout-owned builds for the whole run. |
| G4A-15 | Cleanup and shared-project preservation | Pre/post cleanup pass, the owned project is removed, and any shared project named `iacode` remains unchanged. |
| G4A-16 | G4-F-002 closure | The prior 40/42 order/state failure does not recur under the exact full-run criterion and its guardrails are effective. |
| G4A-17 | G4-F-001 closure | Canonical scanner ownership and exact serialized-byte pre-persistence containment remain effective. |
| G4A-18 | G4-X7 marker containment | Marker input yields sanitized `ERROR`, derived `FAIL`, zero objects, zero metadata records, no valid evidence and no marker disclosure. |
| G4A-19 | Scanner unavailable | Scanner failure occurs before lookup or write and yields sanitized `ERROR`, `FAIL`, zero objects and zero metadata records. |
| G4A-20 | Legacy object | A pre-existing secret-bearing object is rescanned after read, refused and cannot support a verdict. |
| G4A-21 | Independent Red Team A–T | All 20 mandatory attacks execute over valid controls with zero escapes; Q is unchanged and the denominator is not reduced. |
| G4A-22 | Test denominator | The current canonical counted denominator is at least 1701 and every discovered counted execution passes without double counting. |
| G4A-23 | Guardrail denominator | The current canonical denominator is at least 97 and every guardrail resolves, is tested and is effective with zero recurrence failure. |
| G4A-24 | Lessons and recurrence | All lessons validate; UTF-8, wrapper schema, ledger invalidation and Compose isolation controls execute, including the G4-F-002 recurrence class. |
| G4A-25 | Wrapper schema | The publisher consumes the verifier's canonical result field and rejects contradictory aliases without rerunning the verifier. |
| G4A-26 | Ledger auto-invalidation | Changes in assurance scope stale prior Green Keeper, completeness, Red Team and mirror evidence as policy requires. |
| G4A-27 | Security and dependencies | Secret, dependency, injection, isolation and telemetry controls pass without narrowed sources or unavailable-source false PASS. |
| G4A-28 | Documentation and architecture | Architecture, ADRs, runbooks, development and version docs agree with executed behavior and preserve Gate boundaries. |
| G4A-29 | Review-bundle content | Checkpoint, changeset, tests, migrations, schemas, policies, documentation and Git state are complete and secret-clean. |
| G4A-30 | Audit checkpoint assurance | The audit's Green Keeper, completeness, internal controls, inventory, provenance, integrity and secret scan pass. |
| G4A-31 | Independent review | Code, architecture, maintainability, regressions, evidence and docs have Critical=0, High=0 and no unresolved blocker. |
| G4A-32 | Second-tool/session validation | Attribution names this fresh audit session and only evidence executed here; no internal subject verdict is relabelled independent. |
| G4A-33 | Audit attestation | A new attestation names the sealed subject and this audit checkpoint; the subject is not rewritten. |
| G4A-34 | Gate verdict | Only if G4A-01–G4A-33 pass, review is `APPROVED`, Red Team is `RED_TEAM_PASS`, `secondToolValidation` is `PASSED`, and this checkpoint reaches `GATE_PASS`. |

## Execution order

1. Anchor the sealed subject and reproduce identity, publication, bundle and detached validation.
2. Review the accumulated Gate 4 architecture, implementation, requirements, evidence and docs.
3. Execute the independent G4-X7, scanner-failure and legacy-object probe.
4. Execute the complete verifier once in a clean published clone and preserve the integral result.
5. Execute the independent A–T Red Team and rederive tests, requirements, lessons and guardrails.
6. Validate deterministic portable review transport and every historical checkpoint.
7. Derive the review verdict and write either a passing attestation or formal findings.
8. Complete the audit checkpoint's mandatory assurance, finalize, commit, seal, tag, publish and
   verify remote synchronization. Do not start Gate 5.

## Stop and continuation rules

- Any failed stage in the one full verifier is preserved and yields `REWORK_REQUIRED`; no selective
  rerun can replace it.
- A real Critical or High finding, escaped mandatory attack, incomplete requirement, unavailable
  scanner, persisted marker, valid recovery of rejected bytes, leaked marker, guardrail recurrence,
  or red mandatory gate yields `REWORK_REQUIRED` or `BLOCKED`; no product correction is made here.
- Unexpected Git/state divergence produces `DIVERGENCE.md` and `BLOCKED`; history is not rewritten.
- Gate 5 is never started regardless of the verdict.
