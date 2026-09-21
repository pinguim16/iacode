# Handoff

Current Gate: SETUP-00
Current Status: REWORK_REQUIRED

Last valid commit: 90b67a7e0a11179465bc5c92dee22c78da36801f
Current branch: main

Checkpoint schema version: `3.2.0`. Base checkpoint: `SETUP-00-CP-0010` at
`90b67a7e0a11179465bc5c92dee22c78da36801f`. Final reference:
`refs/tags/iacode-checkpoints/SETUP-00-CP-0011`, to be resolved with `git rev-parse`.

## Objective

Audit `SETUP-00-CP-0010` as the `M0` milestone delivery, from a session with no memory of the run
that produced it, and record the verdict here rather than in the checkpoint being judged.

## What was completed

- The five `SETUP-00-CP-0009` findings, verified closed against the implementation and the executed
  tests rather than against the closure record.
- The positive milestone promotion, proven reachable end to end: the subject is anchored here, the
  attestation is written here, and in a sealed snapshot of this checkpoint the verdict derives as
  `MILESTONE_PASSED`. In the real repository the attestation records the real verdict, so the same
  derivation correctly refuses to promote on it.
- Successor durability, re-executed across three sealed states and then performed for real.
- The whole suite, in the working repository and in a clean clone detached at the subject tag.
- Every canonical mandatory validator, in both environments.
- The Green Keeper verdict, the completeness audit, the engineering memory, the guardrail
  effectiveness and the lesson preflight, recomputed independently.
- The integrity chain, re-derived from Git by a reimplementation that does not use `anchors.py`.
- The mandatory attack battery, the internal mirror audit, and an adversarial battery this audit
  wrote, over a mandatory null-mutation control.
- The tenth integrity anchor, which this checkpoint owed its sealed predecessor.

## What was NOT completed

No product code was changed, because an auditor does not repair the delivery it judges. The
milestone did not pass: `CP11-F-001` is open. Gate 0 is `BLOCKED` and no Gate 0 artifact exists in
this change set.

## Current repository state

Branch `main`, clean after the sealing commits, base commit
`90b67a7e0a11179465bc5c92dee22c78da36801f`, final commit bound by
`refs/tags/iacode-checkpoints/SETUP-00-CP-0011`. `STATE.json` records the exact values.

## Files changed

See `FILES.json` and `DIFF-SUMMARY.md`. Outside this checkpoint, only the integrity chain, the new
attestation and `LATEST.md`. No sealed checkpoint was modified and no historical tag was moved.

## Important decisions

See `DECISIONS.md`. The load-bearing ones: the verdict belongs to this checkpoint and the subject
stays immutable; independence is recorded at its real strength and never inflated; and every number
this audit reports was re-derived rather than read from the delivery.

## Tests executed

`python -m unittest discover -s tests`, in the working repository and in a clean clone detached at
the subject tag, with the result object read directly so passes, failures, errors and skips are
separated. The forty-two regression and negative tests the closure record names were additionally
executed by identifier in both environments. Also `python -m compileall -q scripts tests`,
`validate_lessons.py`, `verify_integrity.py`, `derive_counts.py`, `check_completeness.py`,
`derive_requirements.py`, `milestone_status.py`, `promotion_simulation.py`,
`successor_durability.py`, `affected_red_team.py`, `m0_red_team.py`,
`m0_mirror_audit.py --clean-clone`, `validate_checkpoint.py` and `git diff --check`.

## Known failures

One finding, `CP11-F-001`, and one deliberately kept failing artifact: `M0-INTERNAL-MIRROR.json` in
this checkpoint records the failing mirror run, because it is the evidence of the finding.

Two conditional test skips are recorded with their causes in `AUDIT-EXECUTIONS.json`; both are
guards on repository state and neither is a failure. One audit-environment result is recorded and
classified: re-running `green_keeper.py` against a sealed checkpoint appends to its closed ledger and
is refused for that reason, so the recorded verdict was verified by re-executing the five mandatory
gate commands individually instead. Two defects in this audit's own instruments were found,
corrected and recorded; neither changed a product result.

## Known risks

See `RISKS.md`. Especially: this verdict is independent of the implementing run and not of the tool;
the trust model of a milestone verdict is structural rather than cryptographic; and the open finding
blocks the next delivery as well as this audit.

## Do not repeat

Do not describe a same-tool audit as cross-tool validation. Do not re-run a delivery gate against
sealed content and read the resulting refusal as a defect of the delivery. Do not report a passing
count measured in one environment as if it held in another. Do not let an audit harness result stand
without a product execution or an independent recomputation behind it.

## Required next action

Correct `CP11-F-001` in a new delivery checkpoint and request a new fresh-session independent `M0`
audit, as described in `NEXT.md`. Gate 0 stays blocked.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`,
   `docs/DEFINITION-OF-DONE.md`, `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`,
   `docs/checkpoints/LATEST.md` and this complete checkpoint.
2. Read `MILESTONE-REPORT.md` and `REVIEW-REPORT.md` for the verdict and what supports it.
3. Run the validation commands below and compare the observed Git state with `STATE.json`.
4. Follow `NEXT.md`, which names the corrective delivery and what it must close.

## Validation commands

- `git status --short --branch`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0011`
- `python scripts/development-ledger/validate_checkpoint.py`
- `python scripts/development-ledger/validate_lessons.py`
- `python scripts/development-ledger/verify_integrity.py`
- `python scripts/development-ledger/derive_counts.py`
- `python scripts/development-ledger/check_completeness.py`
- `python scripts/development-ledger/derive_requirements.py`
- `python scripts/development-ledger/milestone_status.py --milestone M0` — expect
  `MILESTONE_NOT_PASSED`, rejecting `.iacode/attestations/M0-CP-0011.json` because its
  `reviewResult` is `REWORK_REQUIRED`; that is the honest state, not a failure
- `python -m compileall -q scripts tests`
- `python -m unittest discover -s tests`
- `python docs/checkpoints/SETUP-00-CP-0011/audit-harness/derive_expected.py --root . --checkpoint SETUP-00-CP-0010`
- `python docs/checkpoints/SETUP-00-CP-0011/audit-harness/resolve_evidence.py --root . --checkpoint SETUP-00-CP-0010`

## Stop conditions

Stop on unexpected Git divergence, on a failing validation, on any need to modify a sealed
checkpoint or move a historical tag, on secret exposure, and on any attempt to begin Gate 0 while
`M0` is `REWORK_REQUIRED`.
