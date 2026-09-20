# Handoff

Current Gate: SETUP-00
Current Status: READY_FOR_REVIEW

Last valid commit: 502c554575f717c1d57290e4f4aafa575e41170e
Current branch: main

Checkpoint schema version: `3.2.0`. Base checkpoint: `SETUP-00-CP-0007` at
`502c554575f717c1d57290e4f4aafa575e41170e`. Final reference:
`refs/tags/iacode-checkpoints/SETUP-00-CP-0008`, to be resolved with `git rev-parse`.

## Objective

Close `M0`. Correct every finding of the independent audit recorded in `SETUP-00-CP-0007`, defend
every attack it ran, and reduce the next external audit to confirmation rather than discovery.

## What was completed

- All eleven `M0-F-0NN` findings closed, each with a root cause, an implementation, a regression
  test, a negative test and a verification command, recorded in `CP7-FINDINGS-CLOSURE.json`.
- The full mandatory attack battery executed against a disposable clone, alongside the additional
  attacks and new attacks for every surface this checkpoint introduces, recorded in
  `M0-INTERNAL-RED-TEAM.json`.
- One promotion invariant for every positive terminal status.
- A closed mandatory gate registry; `--gates` can only extend a run.
- An expected requirement set derived from the canonical checklist, the lesson preflight and the
  sealed audit reports, compared exactly with the declared set.
- External milestone verdicts derived from an audit attestation authored by a different sealed
  checkpoint.
- Preflight input fingerprints, Gate binding, and staleness decided by recomputation.
- Every lesson control, evidence path and provenance locator resolved; a recursive secret scan.
- A guardrail registry with measured effectiveness; six reopened guardrails repaired and re-guarded.
- A hash-linked integrity anchor chain over every sealed checkpoint, verified as a mandatory gate.
- Derived counts, cross-checked wherever a report states them.
- Monotonic, post-commit sealing with a recorded clean-tree validation of the sealed content.
- An internal mirror of the milestone audit, declared as internal quality assurance.
- ADR-0010, the extended canonical checklist, and the delivery order restated everywhere.

## What was NOT completed

The final `M0` external audit, the independent review, the independent Red Team, and any Gate
verdict. `secondToolValidation` remains `PENDING_MANUAL`, `milestone.status` remains `PENDING`, and
`.iacode/attestations/` holds no attestation. Gate 0 remains unimplemented and unauthorized.

## Current repository state

Branch `main`, clean after the sealing commits, base commit
`502c554575f717c1d57290e4f4aafa575e41170e`, final commit bound by
`refs/tags/iacode-checkpoints/SETUP-00-CP-0008`. `STATE.json` records the exact values.

## Files changed

See `FILES.json`, verified against the real change set since the base commit with content hashes.
`DIFF-SUMMARY.md` summarizes it. No sealed checkpoint was modified and no historical tag was moved.

## Important decisions

See `DECISIONS.md` and ADR-0010. The load-bearing one: a control may not take its scope, its
denominator or its verdict from the thing it constrains.

## Tests executed

`python -m unittest discover -s tests`, `python -m compileall -q scripts tests`,
`python scripts/development-ledger/validate_lessons.py`,
`python scripts/development-ledger/verify_integrity.py`,
`python scripts/development-ledger/validate_checkpoint.py`. Every gate run is in `REWORK-LOG.jsonl`
with its ledger evidence, and every count is in `COUNTS.json`.

## Known failures

Recorded in `REWORK-LOG.jsonl` and `COMMANDS.jsonl`. Any nonzero exit in `COMMANDS.jsonl` belongs to
a recorded rework cycle or a recorded finalization attempt; each was repaired at the cause and
re-executed. No check was weakened to obtain a green result.

## Known risks

See `RISKS.md`, especially: the external audit is pending; the anchors and the attestation are
tamper-evident rather than cryptographic; a checkpoint cannot anchor its own tag; and the internal
Red Team and mirror audit are not independent validation.

## Do not repeat

Do not let a control take its scope from its caller, its denominator from the set it audits, or its
verdict from the delivery it judges. Do not record an internal verdict as external validation. Do
not modify or retag a sealed checkpoint. Do not mark a lesson `GUARDED` without a registered,
tested guardrail. Do not start Gate 0.

## Required next action

One final Codex `M0` independent audit of this checkpoint, as described in `NEXT.md`.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/SETUP-00-CHECKLIST.md`, `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`,
   `docs/HANDOFF-PROTOCOL.md`, `docs/DEFINITION-OF-DONE.md`, `docs/ENGINEERING-MEMORY.md`,
   `docs/MILESTONE-VALIDATION.md`, `docs/checkpoints/LATEST.md`, and this complete checkpoint.
2. Read `docs/adr/ADR-0010-milestone-closure-controls.md` for the reasoning and the trust model.
3. Read `SETUP-00-CP-0007` in full; this checkpoint is its corrective delivery.
4. Run the validation commands below and compare the observed Git state with `STATE.json`.
5. Review `git diff 502c554575f717c1d57290e4f4aafa575e41170e..refs/tags/iacode-checkpoints/SETUP-00-CP-0008`.
6. Run the per-control verification recipes below, then your own attacks.
7. Record the verdict in a new audit checkpoint. If it approves, write the external attestation into
   `.iacode/attestations/` as described in `docs/MILESTONE-VALIDATION.md`. Never edit a sealed
   checkpoint.

## Validation commands

- `git status --short --branch`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0008`
- `python scripts/development-ledger/validate_checkpoint.py`
- `python scripts/development-ledger/validate_lessons.py`
- `python scripts/development-ledger/verify_integrity.py`
- `python scripts/development-ledger/check_completeness.py`
- `python scripts/development-ledger/derive_requirements.py`
- `python scripts/development-ledger/derive_counts.py`
- `python scripts/development-ledger/m0_red_team.py`
- `python scripts/development-ledger/m0_mirror_audit.py --clean-clone`
- `python -m unittest discover -s tests`
- `python -m compileall -q scripts tests`
- `git diff --check 502c554575f717c1d57290e4f4aafa575e41170e HEAD`

## How to verify each control

- **M0-F-001, promotion invariant.** Set `STATE.status` to `MILESTONE_EXTERNAL_PASS` and
  `greenKeeper.status` to `FAIL` in a clone; validation must refuse. Automated as
  `PromotionInvariantTests`; attack `AF`.
- **M0-F-002, external PASS.** Fill `secondToolValidation` with complete attribution and set
  `milestone.status=PASSED`; validation must refuse for want of an attestation. Then write an
  attestation whose `auditCheckpoint` is this checkpoint; it must be refused as self-attestation.
  Automated as `ExternalAttestationTests`; attacks `Q`, `R`, `S`, `AI`, `AJ`, `AK`.
- **M0-F-003, preflight freshness.** Retire a lesson in `.iacode/memory/lessons.jsonl` and validate;
  the preflight must be reported `STALE`. Change `STATE.gate` to `GATE 1`; the preflight must be
  refused as belonging to another Gate. Automated as `PreflightFreshnessTests`; attacks `U`, `AE`.
- **M0-F-004, resolved claims.** Point a `GUARDED` lesson's control at a nonexistent test, point its
  evidence at a nonexistent file, and put a secret-shaped value in `prevention.description`; each
  must be refused, and the secret must not appear in the output. Automated as
  `LessonResolutionTests`; attacks `AB`, `AC`, `AD`.
- **M0-F-005, closed mandatory set.** Run `python scripts/development-ledger/green_keeper.py
  --gates ""` with a genuinely failing test; the full mandatory set must still run and the gate must
  be `FAIL`. Then empty `requiredGates` in the last cycle and validate; it must be refused.
  Automated as `MandatoryGatePolicyTests`; attacks `V`, `AG`.
- **M0-F-006, denominator.** Delete a requirement from `REQUIREMENTS-MATRIX.json` and
  `CLOSURE-REQUIREMENTS.json`, recompute every stored count, and validate; the derived expected set
  must report the missing anchor. Automated as `ExpectedRequirementSetTests`; attack `C`.
- **M0-F-007, history.** Move a historical tag, or rewrite a sealed predecessor and move its tag,
  then run `verify_integrity.py`; both must be refused. Automated as `IntegrityAnchorTests`; attacks
  `I`, `J`, `AR`.
- **M0-F-008, aggregates.** Change `STATE.requirementsMatrix.mandatory`, or a number in
  `COUNTS.json`, or write an impossible test count in the canonical `N/M TESTS` form into a checkpoint
  report; each must be refused.
  Automated as `DerivedCountTests` and
  `ExpectedRequirementSetTests.test_the_state_mandatory_count_is_cross_checked`; attacks `AA`, `AL`,
  `AM`.
- **M0-F-009, replay context.** Remove `inputsDigest` from a record in `COMMANDS.jsonl` and
  validate; it must be refused. Automated as `CommandInputBindingTests`; attack `AS`.
- **M0-F-010, seal chronology.** Remove the `post-commit-validation` record, or set a command
  timestamp later than `RUN-METADATA.finishedAt`; each must be refused. Automated as
  `SealChronologyTests` and `DeliveryLifecycleTests`; attack `AT`.
- **M0-F-011, lesson provenance.** Point a lesson's `source.finding` at an identifier that appears
  in no checkpoint it names; it must be refused. Automated as `LessonProvenanceTests`.
- **Guardrails.** Delete a control listed in `.iacode/memory/guardrails/registry.json`, or point a
  `verifiedBy` entry at a nonexistent test; the memory must become invalid and the delivery must be
  refused. Automated as `GuardrailRegistryTests` and `GuardrailEffectivenessGateTests`; attack `AQ`.
- **Internal assurance.** Mark one attack `ESCAPED` in `M0-INTERNAL-RED-TEAM.json`, or one check
  `FAIL` in `M0-INTERNAL-MIRROR.json`, while keeping the overall result positive; both must be
  refused. Automated as `InternalAssuranceTests`; attacks `AO`, `AP`.
- **Findings closure.** Set one finding to `OPEN` in `CP7-FINDINGS-CLOSURE.json`; the delivery must
  be refused. Automated as `FindingsClosureTests`; attack `AN`.
- **Historical immutability.** Clean clones detached at every sealed tag must validate. Automated as
  `HistoricalCheckpointCompatibilityTests` and `HistoricalClosureCompatibilityTests`.

## Criteria for PASS

Every canonical requirement complete with resolvable evidence; the declared requirement set equal to
the derived expected set; every `M0` finding closed; every mandatory attack defended; both delivery
gates `PASS` and fresh; the internal Red Team and mirror audit `PASS` and fresh; every guardrail
resolved, tested and without an unresolved failure; the integrity chain verified with every sealed
predecessor anchored; the suite green with no regression; every sealed checkpoint still validating;
the checkpoint valid; the handoff reproducible without this session; no sealed artifact modified; no
Gate 0 work present.

## Criteria for REWORK_REQUIRED

Any finding still open; any mandatory attack that escapes; any control whose scope, denominator or
verdict still comes from the thing it constrains; any internal verdict presented as external; any
stale gate result accepted; any count that contradicts its derivation; any guardrail that cannot be
resolved or is not verified by a test; any sealed checkpoint made invalid; any inconsistency between
`STATE.json`, the matrix, the preflight, the reports, the ledger and the repository.

## Stop conditions

Stop on unexpected Git divergence, on a failing validation, on any need to modify a sealed
checkpoint or move a historical tag, on secret exposure, or on any request to begin Gate 0 without
authorization.
