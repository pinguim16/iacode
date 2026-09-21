# Diff Summary

- Separated the delivery from its auditor in `scripts/development-ledger/attestation.py`: an
  attestation is written by the audit checkpoint about an already sealed subject, it names the
  commit that subject's canonical tag resolves to, and it never names its own commit. The subject is
  never rewritten, re-tagged or re-sealed to become approved. This is the repair for `CP9-F-001`,
  recorded as [ADR-0011](../../adr/ADR-0011-audit-checkpoint-carries-the-verdict.md).
- Added `milestone_status.py`, which derives a milestone verdict from the repository, and made
  `validate_checkpoint.py` verify the attestation against the subject a checkpoint *names* rather
  than against the checkpoint being validated.
- Added the status `MILESTONE_INDEPENDENT_AUDIT_PASS` and bound each audit mechanism to the status
  its evidence supports: a fresh-session audit may not take the cross-tool status.
- Added `promotion_fixture.py`, `promotion_simulation.py` and `successor_durability.py`, which
  execute the two positive paths in disposable repositories and record what they observed.
- Replaced the literal checkpoint exclusion in the integrity guardrail with two derived rules in
  `anchors.py`: `pending_anchor_exclusion` for verification and `rebuild_exclusion` for
  construction. `verify_integrity.py`, `validate_checkpoint.py` and the suite now ask the same
  helper. This is the repair for `CP9-F-002`.
- Made `derive_counts.py` count one physical test execution once, and made validation refuse a
  count larger than what exists, which is the `610 of 306` shape `SETUP-00-CP-0009` disclosed.
- Required a null-mutation control in every adversarial battery: the report schema carries it,
  `m0_red_team.py` records the control it ran, and validation refuses a report without one.
- Extended the derived-count control to the comments and docstrings of `scripts/` and `tests/`, and
  recorded the policy decision in `docs/QUALITY-GATES.md`: a count in prose is not evidence. This is
  the repair for `CP9-F-003`, recorded as a recurrence of `LSN-0022`.
- Made memory validation refuse a `GUARDED` lesson whose notes say it is not guarded, and rewrote
  `LSN-0014`'s note as the residual limit of its control (`CP9-F-004`).
- Removed the unread `guardrailRegistry` key, closed the memory policy schema, and validated the
  policy document like every other governing document (`CP9-F-005`).
- Made the audit-derived sources follow the registry: `derive_requirements.py` names the reports of
  the audit it corrects, `policies.parse_attacks` decides the battery from the report section rather
  than the table shape and accepts both sealed renderings, and the Red Team and mirror audits derive
  their victims and their evidence names.
- Registered the `M0-CP-0009` audit, added three canonical checklist rows for the new controls, and
  mirrored them into `.iacode/policies/canonical-requirements.json`.
- Registered seven lessons and seven guardrails, recorded the `LSN-0022` guardrail failure and its
  repair, and assessed all eight `SETUP-00-CP-0009` lesson candidates.
- Anchored `SETUP-00-CP-0009` in the integrity chain, which its own checkpoint could not do.
- Added `affected_red_team.py`, so an adversarial position is reported by derived, non-overlapping
  categories instead of hand-maintained totals.
- Made `new_checkpoint.py` and `ledger_common.write_json` write text with normalized line endings,
  so every artifact the tooling produces is byte-identical to the same content written elsewhere.

No sealed checkpoint, historical tag or audit report was modified. No Gate 0 runtime exists in this
change set.
