# Positive Promotion Validation

Result: `PASS`

- Simulation: positive milestone promotion
- Closes: `CP9-F-001`
- Generated: `2026-09-21T05:40:32Z`
- Subject: `SETUP-00-CP-0001` at `5ad046d317b29a9eb7cee8178e44cf1e3d4e1092` (`READY_FOR_REVIEW`)
- Audit checkpoint: `SETUP-00-CP-0002` at `5386a4420d920561b8a5bc393043c5dd6dfefa3a` (`MILESTONE_INDEPENDENT_AUDIT_PASS`)
- Attestation: `.iacode/attestations/M0-AUDIT-OF-SETUP-00-CP-0001.json`
- Derived milestone verdict: `PASSED`

Every row below was executed in a disposable repository built by
`scripts/development-ledger/promotion_fixture.py`; nothing here is asserted.

| Check | Expectation | Observed | Result |
|---|---|---|---|
| `POS-001` | the subject checkpoint is delivered and sealed under its canonical tag | SETUP-00-CP-0001 sealed at 5ad046d317b29a9eb7cee8178e44cf1e3d4e1092 | `PASS` |
| `POS-002` | a second checkpoint is authored as the audit and validates as sealed | SETUP-00-CP-0002: CHECKPOINT_VALID | `PASS` |
| `POS-003` | the audit checkpoint carries a milestone verdict status | MILESTONE_INDEPENDENT_AUDIT_PASS | `PASS` |
| `POS-004` | the milestone verdict is derived from the repository as PASSED | PASSED; 1 accepted attestation(s) | `PASS` |
| `POS-005` | the subject is not rewritten, re-tagged or re-sealed by its own audit | commit, tree and STATE.json unchanged: True; subject status still READY_FOR_REVIEW | `PASS` |
| `POS-006` | no attestation names the commit of the tree that contains it | the attestation binds subjectCommit only, resolved from the subject's canonical tag | `PASS` |
| `POS-007` | the integrity chain verifies after the audit checkpoint is sealed | no divergence | `PASS` |

Passed: `7` of `7` checks.
