# Plan — SETUP-00 final closure

## Objective

Correct every finding of the independent `M0` audit recorded in `SETUP-00-CP-0007`, defend every
attack it ran, and reduce the next external audit to confirmation rather than discovery. This
checkpoint is corrective only. It starts no Gate 0 work and modifies no sealed checkpoint.

## Authorized scope

`SETUP-00`. Base commit `502c554575f717c1d57290e4f4aafa575e41170e`, the `SETUP-00-CP-0007` tag.
Checkpoint schema version `3.2.0`.

## Requirement set

`119` requirements, derived rather than transcribed, by
`python scripts/development-ledger/derive_requirements.py`:

| Source | Count | Origin |
|---|---|---|
| SETUP | 59 | every row of `docs/SETUP-00-CHECKLIST.md`, re-parsed |
| AUDIT_FINDING | 11 | every `M0-F-0NN` heading of the sealed CP-0007 review report |
| AUDIT_ATTACK | 26 | every mandatory A–Z row of the sealed CP-0007 Red Team report |
| LESSON | 23 | every lesson the mandatory preflight selected |

`CLOSURE-REQUIREMENTS.json` carries the closure view; `REQUIREMENTS-MATRIX.json` carries the
schema-bound matrix the delivery gates audit. The two are generated together and cannot disagree.

## Architecture of the corrections

| Finding | Correction |
|---|---|
| M0-F-001 | One promotion invariant evaluated for every positive terminal status. |
| M0-F-002 | External PASS derived from an attestation authored by a different sealed checkpoint. |
| M0-F-003 | Preflight bound to `STATE.gate` and to an input fingerprint recomputed at validation. |
| M0-F-004 | Every lesson control and evidence reference resolved; whole-object secret scan. |
| M0-F-005 | Closed mandatory gate registry; the caller may extend a run, never shrink it. |
| M0-F-006 | Expected requirement identifier set derived from canonical sources and compared exactly. |
| M0-F-007 | Hash-linked checkpoint anchor chain over tag, commit and tree. |
| M0-F-008 | Every aggregate cross-checked, including `mandatory`, plus derived counts. |
| M0-F-009 | Recorded commands bind their declared inputs by content hash. |
| M0-F-010 | Monotonic, post-commit sealing with a recorded clean-tree validation of the sealed commit. |
| M0-F-011 | Lesson provenance resolved against the checkpoint it cites. |

## Delivery order

1. Cold start and baseline. 2. Engineering memory updated with what the audit proved.
3. Lesson preflight. 4. Requirement derivation. 5. Implementation. 6. Tests, including a negative
test per escaped attack. 7. Green Keeper until every mandatory gate is green. 8. Delivery
Completeness to `100.00%`. 9. Internal Red Team over all `26` mandatory attacks plus the new
surfaces. 10. `M0` internal mirror audit. 11. `READY_FOR_REVIEW`, then the external `M0` audit.

Any red result at steps 6 to 10 returns the delivery to step 5 and the whole cycle runs again.

## Verification

`python -m unittest discover -s tests`,
`python scripts/development-ledger/validate_lessons.py`,
`python scripts/development-ledger/verify_integrity.py`,
`python scripts/development-ledger/check_completeness.py`,
`python scripts/development-ledger/m0_red_team.py`,
`python scripts/development-ledger/m0_mirror_audit.py`,
`python scripts/development-ledger/validate_checkpoint.py`, and a clean-clone run of all of them.

## Stop conditions

Stop on unexpected Git divergence, on any need to modify a sealed checkpoint or move a historical
tag, on a finding that cannot be closed, on an attack that still escapes, on a stale gate result,
or on any request to begin Gate 0 without authorization.
