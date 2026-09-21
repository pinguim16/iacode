# Milestone Report — M0 / Development control plane

Milestone: `M0`
Gates in the group: `SETUP-00`
Subject of this audit: `SETUP-00-CP-0008` at `c53f4c59a77870414324efa6b5f61b35d26c5090`
Audit checkpoint: `SETUP-00-CP-0009`
Verdict: `REWORK_REQUIRED`

## The independence of this audit, stated exactly

| Property | Value |
|---|---|
| Mechanism | `FRESH_SESSION_INDEPENDENT_AUDIT` |
| Fresh session | `true` — no memory of the run that produced `SETUP-00-CP-0008` |
| Same tool as the implementer | `true` — Claude Code 2.1.195 |
| Same provider as the implementer | `true` — Anthropic |
| Same model family as the implementer | `true` — `claude-opus-5` |
| `crossToolValidation` | `NOT_AVAILABLE` |
| `freshSessionIndependentAudit` | executed; see the verdict below |

The owner authorised a fresh Claude Code session to perform the final `M0` audit because Codex
cannot currently execute the flow. That authorisation permits the mechanism above. It does not
permit describing this audit as cross-tool validation, and this report does not.

The canonical policy was checked before relying on that authorisation, because an audit that
quietly re-reads a rule to fit itself is worth nothing. `docs/MILESTONE-VALIDATION.md` requires an
*independent tool*, a verdict *derived* from an attestation, and an attestation authored by a
different sealed checkpoint. `scripts/development-ledger/attestation.py` enforces exactly that: a
different `auditCheckpoint`, sealed under its own tag and present in the integrity chain. Nothing in
the policy or the implementation requires a different vendor. The same-tool, same-provider
limitation is therefore a real reduction in independence, recorded here, and not a violation of a
canonical rule. No `PROCESS_BLOCKER` arises from it, and no governance document was changed by this
audit.

What this audit does *not* have is the property that made `SETUP-00-CP-0007` valuable: a different
tool, with different blind spots, reading the same repository. That is a genuine limitation of this
verdict, whichever way it had gone.

## Scope executed

| Dimension | Result |
|---|---|
| Audit matrix rows | 183, every row complete with evidence |
| Canonical SETUP-00 requirements | 71 re-derived; 69 confirmed, 2 not confirmed |
| Expected versus declared requirement set of the subject | 131 = 131, 0 missing, 0 unexpected, 0 duplicated |
| `SETUP-00-CP-0007` findings | 11/11 closed, each regression test read and executed |
| Mandatory `A`–`Z` attacks | 26/26 defended, re-executed by this auditor's harness |
| Additional attacks | 26/26 defended |
| Previously bypassed guardrails | 4/4 defended, original bypass and a variation each |
| Delivery-assurance scenarios | 33/33 refused as designed, over an accepted baseline |
| History and tag integrity scenarios | 7/7 refused; 7 sealed checkpoints intact read-only |
| External attestation probes | 15/15 behaved correctly; the positive path does not |
| Preflight freshness scenarios | 6/6 |
| Full suite in a clean clone of the sealed commit | 306/306 |
| Full suite in the working repository after anchoring the predecessor | 305/306, finding CP9-F-002 |
| Mandatory validators | all green |
| Findings | 5: two CRITICAL, three LOW |

## Accumulated completeness of `M0`

`M0` contains one Gate, so accumulated completeness is the SETUP-00 checklist itself. The audit
re-parsed all 71 rows and recorded a verdict per row in `REQUIREMENTS-MATRIX.json`:

- 69 `COMPLETE`;
- 7d.4 `PARTIAL` — the external attestation control refuses every forgery and accepts no legitimate
  case that can actually exist, which is finding `CP9-F-001`;
- 7d.8 `PARTIAL` — the integrity chain is correct and defended every mutation, but its verifying
  test is bound to a literal checkpoint name, so anchoring the sealed predecessor, which the
  protocol requires, turns the mandatory suite red; that is finding `CP9-F-002`.

Coverage 97.18 per cent. Evidence coverage over the confirmed rows is total.

## Integration between Gates

`M0` has one Gate, so the integration question becomes the relationship between the sealed
checkpoints. That chain was examined directly rather than through a report: all seven anchors in
`.iacode/anchors/checkpoint-chain.json` resolve to the tag, commit and tree they claim, every
`anchorHash` recomputes from its own fields, and every link matches its predecessor. Seven mutations
of that chain, run in temporary repositories, were all refused.

`SETUP-00-CP-0008` is not anchored, by design, because a checkpoint cannot anchor its own tag. This
audit checkpoint anchors it, which is the first time that architecture has been exercised by a
successor, and it works: `verify_integrity.py --rebuild` produces an eighth anchor over the sealed
tag, commit and tree without touching `SETUP-00-CP-0008`, and the chain then verifies with this
checkpoint excluded as the one being sealed.

## Regression position

The suite is 306 for 306 in a clean detached clone of the sealed commit, and 306 for 306 in a fresh
fixture clone. No test was skipped, weakened or edited by this audit. Two red results observed
during the audit were in the audit's own harness, are classified `AUDIT_ENVIRONMENT`, and were
repaired in the harness only.

One regression is present rather than latent. `docs/CHECKPOINT-PROTOCOL.md` requires a successor to
anchor its sealed predecessor; doing so took the suite in this repository from 306 for 306 to 305
for 306, because `IntegrityAnchorTests` excludes `SETUP-00-CP-0008` by literal and therefore
swallows the error one of its own assertions depends on. This audit recorded the red result rather
than editing the test, so this checkpoint's `tests`, `unitTests` and `integrationTests` results are
`FAIL`. That is finding `CP9-F-002`.

## Architecture

`ADR-0010` is sound and its trust model is stated honestly, including the residual limit that an
actor controlling the repository can recompute the chain. The load-bearing idea of the corrective
delivery — a control may not take its scope, its denominator or its verdict from the thing it
constrains — is implemented consistently across the gate registry, the expected requirement set,
the preflight fingerprint, the derived counts and the attestation.

The architectural defect this audit found is of the same family, one level up: the attestation
refuses to take its verdict from the delivery, correctly, but it also requires the delivery's own
commit to contain the attestation about that commit. A rule that cannot be satisfied is not a
stricter rule; it is an unreachable state.

## Lessons and guardrails

23 lessons, 22 `GUARDED`, 1 `CONFIRMED`. The one `CONFIRMED` lesson, `LSN-0013`, is honestly not
guarded: no automated control in this repository can observe an arbitrary machine's installation
state.

Every `GUARDED` lesson resolves the whole way down — lesson, named guardrail, registry entry that
names the lesson back, a control that exists, verifying tests that exist in the discovered suite,
and an execution of those tests. 22 guardrails, 22 resolved, 22 tested, 22 effective, 0 unresolved
guardrail failures. Those numbers were recomputed by this auditor from `.iacode/memory/` and the
discovered suite, and only then compared with `guardrail_effectiveness()` and with `STATE.json`; all
three agree.

Six guardrail failures are recorded and all six name `SETUP-00-CP-0008` as the repairing checkpoint:
`LSN-0005`, `LSN-0007`, `LSN-0008`, `LSN-0009`, `LSN-0010`, `LSN-0012`. That is a superset of the
four the previous audit named, which is the right direction.

The recurrence machinery behaves as documented: a repeat against a `GUARDED` lesson escalates
severity, records a `GUARDRAIL_FAILURE`, and reopens the lesson to `CONFIRMED`; validation refuses
`GUARDED` while the failure is unresolved and accepts it again once the failure names the repairing
checkpoint.

`trainingAllowed` is `false` for all 23 lessons.

## Cost and model usage

| Item | Value |
|---|---|
| Tool | Claude Code 2.1.195, desktop application |
| Provider | Anthropic |
| Model | `claude-opus-5` |
| Effort | not exposed by the tool; not invented |
| Token accounting | not exposed by the tool |
| Longest measured execution | the full suite in a clean clone, 242.7 s |
| Other measured executions | 53 finding regression tests 76.3 s; suite in a fixture clone 346.3 s; new-surface classes 57.0 s |

## Outstanding debt

- `CP9-F-001` and `CP9-F-002` must be repaired before `M0` can close. `CP9-F-002` is the more
  urgent of the two in practice, because it leaves the mandatory suite red right now.
- The three `LOW` findings are cosmetic but each is an instance of a class the project already
  guards against elsewhere.
- `M0` has never been validated by a different tool since `SETUP-00-CP-0007` failed. When Codex can
  execute the flow again, a cross-tool audit remains worth running.
- The lesson preflight assumes an implementing delivery: several of its derived requirements, such
  as a readiness status with an empty `blockedBy`, cannot apply to an audit checkpoint. This audit
  therefore did not run a Gate preflight, because the Gate did not start here; the SETUP-00
  preflight sealed in `SETUP-00-CP-0008` was recomputed and found fresh instead.

## Provenance and rights

Every artifact in this checkpoint was produced from this repository by this audit. No third-party
content was introduced. `trainingAllowed` is `false` throughout.

## Gate results

| Gate | Result |
|---|---|
| Full suite, clean clone of the sealed commit | `PASS` (306/306) |
| Full suite, working repository after anchoring the predecessor | `FAIL` (305/306) |
| Static analysis | `PASS` |
| Checkpoint validation of the subject | `PASS` |
| Lesson validation | `PASS` (23 lessons, 22 guarded) |
| Integrity chain | `PASS` (7 anchors, all consistent) |
| Delivery completeness of the subject | `PASS` (131/131, 100.00/100.00) |
| Derived counts | `PASS` (18 comparisons, 0 mismatches) |
| Documentation links | `PASS` (39/39) |
| Command auditability | `PASS` (60 records, 0 unbound, 6/6 safe replays reproduce) |
| Mandatory Red Team battery | `PASS` (26/26) |
| Additional Red Team battery | `PASS` (26/26) |
| Canonical requirement set of the subject | `PASS` (131 = 131) |
| SETUP-00 checklist | `FAIL` (69/71; 7d.4 and 7d.8 not confirmed) |
| External milestone verdict mechanism | `FAIL` (`CP9-F-001`) |
| Suite durability past the protocol's own next step | `FAIL` (`CP9-F-002`) |
| Cross-tool milestone validation | `NOT_AVAILABLE` |
| Fresh-session independent audit | `FAILED` |
| `M0` / SETUP-00 | `REWORK_REQUIRED` |

## Decision

No averaging is permitted. The delivery is close, and most of it is confirmed by execution rather
than by assertion, but a milestone cannot pass while the control that makes its verdict derivable
has no reachable positive path, and while carrying out the protocol's own next step leaves the
mandatory suite red.

`M0` is `REWORK_REQUIRED`. `SETUP-00` is `REWORK_REQUIRED`. Gate 0 remains `BLOCKED`.
