# Milestone Report — M0, Development control plane

- Milestone: `M0`
- Gates: `SETUP-00`
- Subject: `SETUP-00-CP-0012`, sealed at `3f730dca1a12245ee8fdf8dfad7a523ed5c1c186`
- Audit checkpoint: `SETUP-00-CP-0013`
- Attestation: `.iacode/attestations/M0-CP-0013.json`
- Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT`
- Cross-tool validation: `NOT_AVAILABLE`
- Verdict: **`MILESTONE_INDEPENDENT_AUDIT_PASS`**

## What the verdict is, and what it is not

`M0` passed a **fresh-session independent audit**: a session with no memory of the implementing run
audited the milestone and approved it. The tool, the provider and the model are the implementing
run's, so this is not cross-tool validation and it is not recorded as one. The attestation records
`crossToolValidation: NOT_AVAILABLE`, that mechanism authorises only
`MILESTONE_INDEPENDENT_AUDIT_PASS`, and validation refuses `MILESTONE_EXTERNAL_PASS` derived from
it — which this audit executed as an attack rather than assumed.

The verdict is **derived**, not asserted. `milestone_status.py --milestone M0` re-verifies the
attestation against the subject it names, the auditor that wrote it, and the four results that make
a milestone pass, from a clean checkout, and exits non-zero when no valid attestation supports a
`PASS`.

## The four results the derivation requires

| Result | Value | Where it comes from |
|---|---|---|
| Review | `APPROVED` | `REVIEW-REPORT.md`; `CP11-F-001` `CLOSED`, no new finding |
| Red Team | `RED_TEAM_PASS` | `M0-INTERNAL-RED-TEAM.json`; 26 of 26 defended over two accepted null-mutation controls |
| Completeness | `100.0` | `COMPLETENESS-REPORT.json`; the anchored declared set equals an independently derived expected set exactly |
| Evidence coverage | `100.0` | every evidence reference of this checkpoint and of the subject resolves |
| Tests | `PASS` | the whole discovered suite, in the working tree and again in a clean clone at the subject tag |

## What closed the milestone

`SETUP-00-CP-0011` returned the milestone for rework over one critical finding: a delivery that
corrects no audit could not obtain a passing internal mirror, so the protocol's own next step was
unreachable. `SETUP-00-CP-0012` closed it by making an empty applicable set a first-class outcome
that justifies itself, while a missing required set stays a failure.

This audit did not read that claim. It executed the real `m0_mirror_audit.py` over six applicability
states in disposable clones, executed the Gate 0 transition, the positive promotion and the successor
durability simulations, and attacked the reverse escape the repair could have opened in twenty-six
scenarios. The detail is in `REVIEW-REPORT.md`.

The clearest evidence is structural rather than argumentative: **this audit checkpoint is itself a
delivery that corrects no audit**. No registered audit names `SETUP-00-CP-0013` as its corrective
delivery, so its own applicable set is empty, its own mirror records the two registry-bound
dimensions as `NOT_APPLICABLE` with their justification, and it reaches a positive terminal status.
Under the defect this checkpoint could not have existed in a valid state.

## Gates included and their verdicts

| Gate | Verdict | Where |
|---|---|---|
| `SETUP-00` | closed by this milestone audit | `SETUP-00-CP-0012` delivered it at `READY_FOR_REVIEW`; this checkpoint carries the verdict |

`SETUP-00` is the only Gate of `M0`, so the Gate closes with the milestone rather than at
`INTERNAL_GATE_PASS` first.

## The audit history of this milestone

| Audit | Subject | Mechanism | Verdict |
|---|---|---|---|
| `M0-CP-0007` | `SETUP-00-CP-0006` | cross-tool, Codex Desktop | `REWORK_REQUIRED`, 11 findings |
| `M0-CP-0009` | `SETUP-00-CP-0008` | fresh session | `REWORK_REQUIRED`, 5 findings |
| `M0-CP-0011` | `SETUP-00-CP-0010` | fresh session | `REWORK_REQUIRED`, 1 critical finding |
| `M0-CP-0013` | `SETUP-00-CP-0012` | fresh session | **`APPROVED`** |

Seventeen findings were raised across three independent audits and all seventeen are closed. Each
closure was re-verified here against the sealed report that raised it rather than against the record
that claims it.

## Lessons, guardrails and the Red Team position

31 lessons, 29 `GUARDED` and 2 `CONFIRMED`. 32 guardrails, every one resolving to a real control and
naming verifying tests that exist; all 72 `verifiedBy` references resolve. No guardrail failure is
unresolved. The recurrence that `CP11-F-001` represented is filed as a `GUARDRAIL_FAILURE` against
the lessons whose classes recurred, `LSN-0024` and `LSN-0029`, resolved in `SETUP-00-CP-0012`, with
`GRD-0031` and `GRD-0032` as the new controls; the genuinely new class became `LSN-0031`.

The delivery's own battery reports 73 of 73 defended with 38 of 38 mandatory, which this audit
re-executed rather than accepted. This audit's own battery reports 26 of 26.

## Outstanding risk carried into M1

- Independence is of the session, not of the tool. Recorded structurally, not described.
- The trust model is structural rather than cryptographic; signed attestations remain available.
- `NOT_APPLICABLE` is a new state whose misuse is refused today but whose use should be watched.
- `GATE 0` has no canonical requirement specification yet. Authoring it is that Gate's first
  deliverable.

The full list, with what would turn each into a defect, is in `RISKS.md`.

## Decision

`M0` — **`PASSED`** by `MILESTONE_INDEPENDENT_AUDIT_PASS`.
`SETUP-00` — closed.
`GATE 0 — FOUNDATION` — `AUTHORIZED`, not started, and not begun by this checkpoint.
