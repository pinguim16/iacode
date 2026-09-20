# Diff Summary

- Added the canonical policy sources the delivery does not own: `.iacode/policies/quality-gates.json`
  (the closed mandatory gate registry), `.iacode/policies/canonical-requirements.json` (the
  machine-readable mirror of the Gate checklist) and `.iacode/policies/audit-registry.json` (the
  independent audits whose findings are open).
- Added `scripts/development-ledger/policies.py`, which re-parses the Gate checklist and the sealed
  audit reports and derives the mandatory gate set and the expected requirement set.
- Added `scripts/development-ledger/anchors.py`, `verify_integrity.py` and
  `.iacode/anchors/checkpoint-chain.json`: a hash-linked chain over every sealed checkpoint's tag,
  commit and tree, verified as a mandatory gate.
- Added `scripts/development-ledger/attestation.py`, `.iacode/attestations/` and the external audit
  attestation schema, so an external milestone verdict is derived from an audit checkpoint rather
  than asserted by the delivery.
- Added `derive_requirements.py`, `derive_counts.py`, `seal_checkpoint.py`, `m0_red_team.py` and
  `m0_mirror_audit.py`, and the schemas for their artifacts.
- Replaced the `READY_FOR_REVIEW`-only promotion rules with one invariant evaluated for every
  positive terminal status, and added the status-specific requirements on top of it.
- Made the Green Keeper derive its mandatory set from policy, record the set it was measured
  against with per-gate command evidence, and stamp the scope fingerprint of the content it judged.
- Made the completeness audit compare the declared requirement set with the derived expected set
  exactly, cross-check every aggregate including `mandatory`, and record its own freshness.
- Made the lesson preflight carry an input fingerprint, bound it to `STATE.gate`, and made
  validation recompute both the fingerprint and the selection.
- Made the memory resolve what a lesson claims: every control reference, every evidence path and
  every provenance locator, with a recursive secret scan over the whole lesson object.
- Added the guardrail registry, bound every `GUARDED` lesson to it, and made guardrail
  effectiveness a measured value that blocks a delivery when a control is unresolved or untested.
- Bound every recorded command's declared inputs by content hash, and made a clean-tree claim
  provable against the declared commit.
- Made sealing monotonic and post-commit: the content commit is validated with a clean worktree,
  that run is recorded against it, and the evidence commit may contain nothing else.
- Derived every evidential count into `COUNTS.json` and made a contradicting Markdown claim a
  validation error.
- Added the Milestone Closure Auditor role, its Claude Code adapter, and the internal mirror audit
  it executes; neither it nor the internal Red Team may be recorded as external validation.
- Introduced checkpoint `schemaVersion` `3.2.0`, matrix and completeness report `2.0.0`, preflight
  `2.0.0` and engineering memory policy `2.0.0`, with version dispatch so every sealed checkpoint
  keeps validating under its own version's rules.
- Recorded six `GUARDRAIL_FAILURE` entries for the controls the audit bypassed, repaired each one,
  and returned the lessons to `GUARDED` only against a registered, tested guardrail. Added nine
  lessons from the audit and corrected the provenance locators the audit found inaccurate.
- Extended the canonical Gate checklist with the closure controls, added ADR-0010, and restated the
  mandatory delivery order in every governing document and both tool adapters.
- The suite grew to cover every finding and every attack, including a negative test per escape and
  an end-to-end rehearsal of the new sealing workflow.
