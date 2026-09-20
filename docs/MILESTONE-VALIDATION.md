# Milestone Validation

External independent validation is expensive and it is not the project's first line of defence. Every
delivery passes the internal controls first. External audit then happens once per milestone, over a
group of Gates, rather than after each Gate.

## Internal is not external

Two distinct statuses exist so the difference can never be blurred:

| Status | Meaning | Who grants it |
|---|---|---|
| `INTERNAL_GATE_PASS` | The Gate satisfied the project's own controls: green gates, total requirement coverage, a valid checkpoint. | The implementing run's own controls, after the Green Keeper and the Delivery Completeness Validator. |
| `MILESTONE_EXTERNAL_PASS` | An independent tool audited the milestone as a whole and approved it. | The external auditor, recorded in `secondToolValidation` and `milestone`. |

An internal verdict is never described as independent external validation. Validation refuses
`MILESTONE_EXTERNAL_PASS` unless `milestone.status` is `PASSED` and `secondToolValidation.status` is
`PASSED`, and it refuses an `INTERNAL_GATE_PASS` that tries to carry an external verdict.

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
