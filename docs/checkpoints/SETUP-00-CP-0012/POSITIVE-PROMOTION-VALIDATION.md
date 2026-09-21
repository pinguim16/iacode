# Positive Promotion Validation

Result: `PASS`

- Simulation: positive milestone promotion
- Closes: `CP9-F-001`
- Generated: `2026-09-21T12:39:02Z`
- Subject: `SETUP-00-CP-0001` at `94637e07282ef7d1c5d5d6fdc99f6d5cae3952be` (`READY_FOR_REVIEW`)
- Audit checkpoint: `SETUP-00-CP-0002` at `ae854775067fbaceeec3cc23522bde3380e75b85` (`MILESTONE_INDEPENDENT_AUDIT_PASS`)
- Attestation: `.iacode/attestations/M0-AUDIT-OF-SETUP-00-CP-0001.json`
- Derived milestone verdict: `PASSED`

Every row below was executed in a disposable repository built by
`scripts/development-ledger/promotion_fixture.py`; nothing here is asserted.

| Check | Expectation | Observed | Result |
|---|---|---|---|
| `POS-001` | the subject checkpoint is delivered and sealed under its canonical tag | SETUP-00-CP-0001 sealed at 94637e07282ef7d1c5d5d6fdc99f6d5cae3952be | `PASS` |
| `POS-002` | a second checkpoint is authored as the audit and validates as sealed | SETUP-00-CP-0002: CHECKPOINT_VALID | `PASS` |
| `POS-003` | the audit checkpoint carries a milestone verdict status | MILESTONE_INDEPENDENT_AUDIT_PASS | `PASS` |
| `POS-004` | the milestone verdict is derived from the repository as PASSED | PASSED; 1 accepted attestation(s) | `PASS` |
| `POS-005` | the subject is not rewritten, re-tagged or re-sealed by its own audit | commit, tree and STATE.json unchanged: True; subject status still READY_FOR_REVIEW | `PASS` |
| `POS-006` | no attestation names the commit of the tree that contains it | the attestation binds subjectCommit only, resolved from the subject's canonical tag | `PASS` |
| `POS-007` | the integrity chain verifies after the audit checkpoint is sealed | no divergence | `PASS` |
| `POS-008` | the internal mirror audit of every checkpoint in this simulation was produced by executing m0_mirror_audit.py, not by writing its artifact | SETUP-00-CP-0001: python scripts/development-ledger/m0_mirror_audit.py --write --checkpoint C:\Users\cesar\AppData\Local\Temp\iacode-promotion-wy7f5ykd\promotion\docs\checkpoints\SETUP-00-CP-0001 exit=0 -> PASS 16/18; SETUP-00-CP-0002: python scripts/development-ledger/m0_mirror_audit.py --write --checkpoint C:\Users\cesar\AppData\Local\Temp\iacode-promotion-wy7f5ykd\promotion\docs\checkpoints\SETUP-00-CP-0002 exit=0 -> PASS 16/18 | `PASS` |
| `POS-009` | a checkpoint that corrects no audit reaches a passing mirror with its empty dimensions recorded as NOT_APPLICABLE and justified | SETUP-00-CP-0001: MIR-002=NOT_APPLICABLE, MIR-003=NOT_APPLICABLE; SETUP-00-CP-0002: MIR-002=NOT_APPLICABLE, MIR-003=NOT_APPLICABLE | `PASS` |

Passed: `9` of `9` checks.
