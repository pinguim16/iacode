# Plan — M1 final fresh-session independent audit

Audit checkpoint `GATE-3-CP-0006`. Immutable subject: sealed checkpoint
`GATE-3-CP-0005`, canonical tag `refs/tags/iacode-checkpoints/GATE-3-CP-0005`, commit
`3ef2bf77ddbddd378d35f5c4d32f2d90d42fc97d`, and every sealed M1 predecessor on which it
depends. The scope is the complete M1 milestone: Gate 0 Foundation, Gate 1 Model Gateway, Gate 2
Agent Runtime, and Gate 3 Sandbox.

This is an audit-only run. It may write this audit checkpoint, the attestation, the integrity anchor
owed to the subject, the audit registry only if required by canonical policy, `LATEST.md`, and the
review bundle outside the sealed subject. It may not change product code, tests, policy, the sealed
subject, a historical tag, or start Gate 4.

## Independence and attribution

- Role: M1 milestone independent auditor.
- Tool: Codex desktop application.
- Provider: OpenAI.
- Model: GPT-5, as exposed by the active Codex runtime contract.
- Fresh session: true; this task was created separately from the implementing session.
- Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT`.
- Cross-tool validation: `NOT_AVAILABLE` in this task; no different tool/provider is exposed to this
  auditing session. This mechanism may author `MILESTONE_INDEPENDENT_AUDIT_PASS` only, never
  `MILESTONE_EXTERNAL_PASS`.

## Frozen audit criteria

These criteria were fixed before substantive audit execution. Results may populate them, but this
run may not add, remove, narrow, waive, or weaken a criterion after observing results. A newly
discovered Critical or High violation of an existing requirement remains blocking.

| ID | Criterion | Required evidence and acceptance |
|---|---|---|
| AM-01 | Subject identity and immutability | The canonical subject tag resolves locally and remotely to the same exact commit; the subject tree and tag are never changed. |
| AM-02 | Local subject validity | `validate_checkpoint.py`, lesson validation and integrity validation pass before audit execution. |
| AM-03 | Published history | A fresh transport clone of `https://github.com/pinguim16/iacode.git` validates every sealed M1 checkpoint detached at its canonical tag; no evidence depends on a local-only object. |
| AM-04 | Remote synchronization | `origin/main`, the subject tag, every M1 checkpoint tag and every required preserved-evidence tag are published and resolve correctly. |
| AM-05 | Unpublished-evidence negative control | In a disposable clone/fixture, removing the only published reference to named evidence makes validation fail; restoring publication makes it pass. Real tags are never changed. |
| AM-06 | Fresh dependency security | A new live scan reaches both mandatory npm and PyPI advisory sources over the resolved lock graphs; unavailable or cached-only sources do not pass; Critical = 0 and High = 0. |
| AM-07 | Dependency graph reality | The npm and Python scanners evaluate resolved lock/dependency graphs, including the former M1-F-004 transitive chains, not only direct manifests. |
| AM-08 | Full verification | `scripts/iacode/verify.py --keep-going` executes now and every mandatory stage passes; stage command, exit code, duration, result and artifacts are recorded. |
| AM-09 | Count integrity | Current discovered test counts are derived without double counting and every executed suite passes. |
| AM-10 | Foundation functional path | Fresh startup, configuration, database, migrations, API/readiness, dependency behavior, backup/restore, restart and fresh install execute successfully. |
| AM-11 | Configured Model Gateway | A real request traverses the Model Gateway to the configured provider/model, returns a normalized response and provenance; the auditor does not call the provider directly or silently substitute a model. |
| AM-12 | Agent Runtime functional path | A real AgentRun traverses create, queue, Temporal, agent, gateway, persisted events and terminal completion. |
| AM-13 | Cross-Gate tool path | A real Task traverses Agent Runtime, Model Gateway, model-produced ToolRequest, Sandbox execution, authoritative ToolResult, Agent Runtime and final result with no host execution. |
| AM-14 | Live ToolRequest contract | The configured model receives the canonical tool schema and emits the canonical `tool.name` / `tool.arguments` equivalent without an artificial repair being the only success path. |
| AM-15 | Forged ToolResult defense | Manual/external results for a SANDBOX-owned request are refused during and after execution; the stored and consumed result remains the Sandbox result. |
| AM-16 | Sandbox filesystem isolation | Workspace isolation, cross-run isolation, traversal, absolute path, drive/UNC, null-byte and symlink escapes are independently attacked and defended. |
| AM-17 | Sandbox privilege boundary | Tool execution occurs only inside the sandbox; host execution is absent; unknown tools, policy escalation, mounts, privileges and engine endpoints are refused. |
| AM-18 | Host secret isolation | A synthetic host sentinel secret is not observable inside an executed sandbox; no real secret is used as evidence. |
| AM-19 | Network boundary | Under `network=none`, safe external egress probes fail and only the authorized network profile behavior is available. |
| AM-20 | Resource, timeout and cleanup | CPU/memory/process/output/workspace limits, timeout, whole-process-tree cleanup, cancellation and orphan cleanup hold under live attacks. |
| AM-21 | R-G3-001 | The controller engine-socket risk retains all documented controls; no agent input, ToolRequest or external API input can become an arbitrary engine operation. Otherwise severity is High or Critical. |
| AM-22 | Durability | Worker restart, API/service restart, persisted state recovery, events and ToolResult flow remain correct; no run stays `RUNNING` indefinitely. |
| AM-23 | SSE terminal drain | A terminal run with more events than one page drains every event after the cursor with no silent truncation. |
| AM-24 | Secret and public-history scans | Repository, staged/publish-bound content and complete history scans report no real secret; any fixture allowance is policy-backed. |
| AM-25 | Documentation and runbooks | Foundation, gateway, runtime, sandbox, startup and verification instructions reproduce the system and agree with current behavior. |
| AM-26 | Engineering Memory | Lessons, index, preflight, guardrail registry and effectiveness validate; unresolved guardrail failures = 0 and no guarded failure class recurs undetected. |
| AM-27 | Accumulated M1 completeness | Gates 0–3 requirements and evidence are 100%; `PARTIAL = 0`, `MISSING = 0`, `UNPROVEN = 0`, and references resolve from sealed published content. |
| AM-28 | Independent Red Team | A fresh milestone battery attacks published-history false PASS, dependency false PASS, direct-provider bypass, forged ToolResult, host execution, workspace/symlink/cross-run escapes, secret/engine/network exposure, policy escalation, timeout/cancel bypass and attestation forgery. The equivalent null control is `VALID` before any defense is credited. |
| AM-29 | Findings threshold | Critical = 0 and High = 0. Every finding carries ID, severity, requirement, observation, reproduction, expected, observed, evidence, impact, recommended correction and status; the auditor implements none. |
| AM-30 | Audit-checkpoint assurance | The audit checkpoint itself passes Green Keeper, completeness, internal Red Team/mirror where applicable, secret scan, checkpoint validation, integrity, canonical sealing and remote synchronization. |
| AM-31 | Attestation and derived verdict | Only if AM-01–AM-30 all pass, a canonical attestation about the sealed subject records truthful tool/provider/model/session/mechanism/results and `milestone_status.py` derives `MILESTONE_INDEPENDENT_AUDIT_PASS`. |
| AM-32 | Review bundle | The required review ZIP includes all mandated audit evidence; archive CRC, manifest, checksums, mandatory files and secret scan validate into the adjacent review-validation JSON. |

## Execution order

1. Complete the audit checkpoint baseline, anchor, preflight and derived requirement set.
2. Validate and inventory every sealed subject from local and published history.
3. Execute the fresh dependency scans and full verification.
4. Execute the configured-model, Agent Runtime and cross-Gate live flows.
5. Execute sandbox, forged-result, published-evidence, R-G3-001, durability, SSE and secret regressions.
6. Execute the independent Red Team with a valid null control.
7. Audit accumulated M1 completeness, documentation, memory, counts, risks and findings.
8. Derive the review verdict; if it passes, write the attestation.
9. Run Green Keeper, completeness, internal audit controls and final checkpoint validation.
10. Declare every changed path, finalize, commit, seal, push branch and canonical tag, derive milestone
    status, then build and validate the review ZIP.

## Stop and continuation rules

- A real Critical or High product/security finding produces `REWORK_REQUIRED`; no product repair is
  made here. Non-destructive checks may continue only when canonical policy permits, so the audit
  consolidates all safe findings in one round.
- An unavailable mandatory advisory source or required external service produces `BLOCKED` or the
  policy's exact external-blocker status, never PASS.
- Any untrusted path to an arbitrary engine operation is Critical and triggers the policy stop.
- Any unexpected Git/state divergence produces `DIVERGENCE.md` and `BLOCKED`; history is never
  rewritten or reconciled silently.
- Gate 4 is never started in this session, regardless of verdict.
