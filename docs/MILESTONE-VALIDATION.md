# Milestone Validation

External independent validation is expensive and it is not the project's first line of defence. Every
delivery passes the internal controls first. External audit then happens once per milestone, over a
group of Gates, rather than after each Gate.

## Internal is not external

Three distinct statuses exist so the difference can never be blurred:

| Status | Meaning | Who grants it |
|---|---|---|
| `INTERNAL_GATE_PASS` | The Gate satisfied the project's own controls: green gates, total requirement coverage, a valid checkpoint. | The implementing run's own controls, after the Green Keeper and the Delivery Completeness Validator. |
| `MILESTONE_INDEPENDENT_AUDIT_PASS` | A session with no memory of the implementing run audited the milestone as a whole and approved it. Independent of the run; the same tool. | The auditing run, in its own audit checkpoint, derived from an attestation whose mechanism is `FRESH_SESSION_INDEPENDENT_AUDIT`. |
| `MILESTONE_EXTERNAL_PASS` | A different tool, provider or model audited the milestone as a whole and approved it. | The auditing run, in its own audit checkpoint, derived from an attestation whose mechanism is `CROSS_TOOL_INDEPENDENT_AUDIT`. |

An internal verdict is never described as independent validation, and a same-tool audit is never
described as external. Each mechanism authorises only the status its evidence supports: validation
refuses `MILESTONE_EXTERNAL_PASS` derived from a fresh-session attestation, refuses either milestone
status unless `milestone.status` and `secondToolValidation.status` are both `PASSED`, and refuses an
`INTERNAL_GATE_PASS` that tries to carry an independent verdict.

Gate authorisation follows from either accepted independent mechanism: the owner authorises
`FRESH_SESSION_INDEPENDENT_AUDIT` while cross-tool execution is operationally unavailable, and the
attestation records `crossToolValidation: NOT_AVAILABLE` so the limit stays visible instead of being
implied.

## Milestones

| Milestone | Scope | Gates |
|---|---|---|
| `M0` | Development control plane | `SETUP-00` |
| `M1` | IACode V0 foundation | `GATE 0`, `GATE 1`, `GATE 2`, `GATE 3` |
| `M2` | IACode V0 completion and experience | `GATE 4`, `GATE 5`, `GATE 6`, `GATE 7` |
| `M3` | Code graph, memory and gap detection | `GATE 8`, `GATE 9`, `GATE 10`, `GATE 11` |
| `M4` | Skills and dataset production | `GATE 12`, `GATE 13`, `GATE 14`, `GATE 15` |
| `M5` | Dataset audit and model adaptation | `GATE 16`, `GATE 17`, `GATE 18`, `GATE 19` |
| `M6` | Evaluation, shadow mode and promotion | `GATE 20`, `GATE 21`, `GATE 22`, `GATE 23` |

The grouping is also machine-readable, in `ledger_common.MILESTONES`, and
`requires_external_validation(gate)` answers whether a Gate closes a milestone. A Gate outside the
plan is treated conservatively as requiring validation.

## Cadence

```text
Gate  -> internal controls -> INTERNAL_GATE_PASS
Gate  -> internal controls -> INTERNAL_GATE_PASS
Gate  -> internal controls -> INTERNAL_GATE_PASS
Gate  -> internal controls -> INTERNAL_GATE_PASS -> milestone checkpoint
                                                 -> external audit
                                                 -> MILESTONE_EXTERNAL_PASS or REWORK_REQUIRED
```

An intermediate Gate does not call the external auditor. The last Gate of a milestone does.

## Extraordinary audit

An audit may be requested before the milestone closes, but only for a recorded reason. The checkpoint
sets `externalAuditRequired` to `true` and names the trigger in `externalAuditReason`. Validation
refuses a request with no reason, a reason that names no recognised trigger, and a reason recorded
without a request.

Recognised triggers: `security-boundary`, `sandbox-boundary`, `rights-or-provenance-change`,
`training-data-policy`, `training-execution`, `promotion-logic`, `secret-handling`,
`destructive-persistence`.

This is not a routine escape hatch. Using it without one of these reasons is a process violation.

## Milestone checkpoint

Closing a milestone creates a checkpoint that consolidates, for the whole group:

- the Gates included and their internal verdicts;
- the lessons produced, updated, guarded and retired;
- open risks;
- architecture changes and the ADRs that record them;
- the full test results and the regression position;
- cross-Gate integration evidence, not only the last Gate's evidence;
- requirements completeness across every included Gate;
- outstanding technical debt;
- provenance and rights;
- cost and model usage.

That checkpoint is what the external auditor receives.

## The auditor's role

The external tool acts as the **milestone independent auditor**. It validates accumulated
completeness, integration between Gates, architecture, regressions, quality, documentation, the
lessons and guardrails, the Red Team position, and the inconsistencies that local per-Gate validation
cannot see because each Gate looked correct on its own.

It does not implement corrections. Findings return to the implementer, which preserves the
independence that makes the audit worth running.

## A milestone verdict is derived, never asserted

The first `M0` audit proved that a checkpoint could describe itself as externally validated: filling
`secondToolValidation` with complete attribution, setting `milestone.status = PASSED` and writing
`MILESTONE_EXTERNAL_PASS` were all accepted on an intermediate Gate with the review and the Red Team
still pending.

The repair to that escape created a second one. The attestation was consumed as if it belonged to the
checkpoint being promoted, so satisfying it required a tree that contained its own commit identifier.
Every forgery was refused and no honest audit could pass: `CP9-F-001`, a control whose positive path
did not exist.

### The two objects

A delivery checkpoint and an audit checkpoint are different immutable objects, and the verdict
belongs to the second one:

```text
SUBJECT checkpoint S      delivered, sealed under its canonical tag, anchored, closed at
                          READY_FOR_REVIEW, and never rewritten again
      |
      |  audited by
      v
AUDIT checkpoint A        a later checkpoint authored by the auditing run. It anchors S, and it
                          carries .iacode/attestations/<auditId>.json naming S and the commit S's
                          tag already resolves to. Its own status is the milestone verdict.
      |
      v
MILESTONE VERDICT         derived from the repository by attestation.derive_milestone_verdict,
                          never read from a status field
```

The subject is not re-tagged, re-sealed or re-validated to become approved. An audit is something
recorded *about* sealed content, in a later checkpoint, which is why the attestation never names its
own commit: the audit checkpoint's identity is bound by its own sealing, its canonical tag and the
integrity anchor its successor records.

### What is verified

The attestation records the audit, the mechanism, whether cross-tool execution was available, the
auditing tool, provider, model and session independence, the subject checkpoint and the exact subject
commit, the audit checkpoint, and the four results that make a milestone pass: the review verdict, the
Red Team verdict, completeness with evidence coverage, and the test result.

Verification re-derives all of it and rejects an attestation when

- it names the audited checkpoint as its own auditor;
- the subject checkpoint does not exist, is not sealed under its canonical tag, is not in the
  integrity chain, or is named with a commit that tag does not resolve to;
- the audit checkpoint does not exist, or a checkpoint claims a verdict from an attestation another
  checkpoint authored;
- the subject commit is not an ancestor of the audit checkpoint's history, because an audit judges
  content that already exists;
- the mechanism is unknown, contradicts the availability it records, or does not authorise the status
  being claimed;
- the review is not `APPROVED`, the Red Team is not `RED_TEAM_PASS`, completeness or evidence
  coverage is below `100.0`, or the test result is not `PASS`.

A milestone status additionally requires a milestone-closing Gate or a recorded extraordinary
trigger. `python scripts/development-ledger/milestone_status.py --milestone M0` performs the whole
derivation from a clean checkout and exits non-zero when no valid attestation supports a PASS.

### The assurance boundary

An attestation is a repository file, so it is inside the delivery-assurance scope of the checkpoint
that writes it — the audit checkpoint, which runs its Green Keeper, completeness audit, internal Red
Team and mirror audit *after* writing it, and therefore fingerprints the content it actually seals.

It is **not** inside the subject's scope. The subject's gate results describe the tree its own tag
names, and that tree does not contain a file created later. A sealed checkpoint is validated from its
canonical tag, so adding an audit afterwards cannot make its Green Keeper, completeness, Red Team or
mirror results stale. The boundary is drawn by which tree a result describes, not by excluding
attestations from the scope, which would have hidden real staleness in the audit checkpoint itself.

### Trust model

The control is structural, not cryptographic. There is no signature and no external key: a milestone
verdict requires a second, sealed, tagged, anchored checkpoint authored as an audit of an already
sealed subject, which cannot be produced by editing `STATE.json`, `QUALITY.json` or one
`secondToolValidation` field. An actor able to create that checkpoint and its tag could still forge
the relationship. That residual limit is recorded here rather than papered over, and the upgrade to
signed attestations stays available.

## Internal assurance before the external audit

A milestone delivery runs, before handoff, the full mandatory attack battery
(`m0_red_team.py`) and a mirror of the milestone audit itself (`m0_mirror_audit.py`, the role in
`.iacode/agents/m0-closure-auditor.md`). Both write machine-readable reports with a fingerprint of
the content they judged, and both are refused when stale.

Neither is independent validation. They are authored by the implementing run, on the same tooling, in
the same session. Their purpose is to reduce the external audit to confirmation rather than
discovery, and the validator refuses any attempt to record either of them as an independent verdict.

Every adversarial battery additionally records a **null-mutation control**: the unmutated fixture run
through the identical path, which must be accepted before any refusal is attributed to the mutation
under test. A report whose control is missing or not `VALID` cannot produce a `PASS`. The second `M0`
audit's first harness reported every attack as defended while the refusals came from leftover state.

A delivery also executes the protocol's own positive paths before handoff:
`promotion_simulation.py` performs a complete two-checkpoint promotion in a disposable repository, and
`successor_durability.py` advances a sealed chain and re-checks the integrity controls at every state.
A control that only ever refuses, and a transition that only ever breaks the next delivery, are both
failures this delivery must find rather than leave for the audit.

## Findings become work

`.iacode/policies/audit-registry.json` binds an independent audit to the checkpoint that corrects it.
The findings and the mandatory attacks are re-parsed from the sealed audit reports rather than
transcribed, so the corrective delivery's expected requirement set contains one anchored requirement
per finding and per mandatory attack. A delivery cannot be offered while any of them is open.
