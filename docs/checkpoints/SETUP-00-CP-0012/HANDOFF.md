# Handoff

Current Gate: SETUP-00
Current Status: READY_FOR_REVIEW

Last valid commit: 98a9f4ca83d538e9610844086ca74b7ff32492e1
Current branch: main

Checkpoint schema version: `3.2.0`. Base checkpoint: `SETUP-00-CP-0011` at
`98a9f4ca83d538e9610844086ca74b7ff32492e1`. Final reference:
`refs/tags/iacode-checkpoints/SETUP-00-CP-0012`, to be resolved with `git rev-parse`.

## Objective

Close `CP11-F-001`, the single critical finding of the fresh-session independent `M0` audit recorded
in `SETUP-00-CP-0011`, so that a checkpoint which corrects no audit can obtain a passing internal
mirror through the shipped tooling, and hand the result to a new `M0` audit. Gate 0 is not started.

## What was completed

- `CP11-F-001` closed. An audit control now tells an empty applicable set from a missing required
  set: the first is `NOT_APPLICABLE` with a reason, an expected count of zero and the canonical
  source the emptiness was derived from; the second is still `FAIL`.
- The reverse escape closed with it: an unjustified inapplicable dimension, one carrying items, one
  counted as a pass, one under the older report version, and one declared over work the audit
  registry still names are all refused, by the auditor and again by checkpoint validation.
- The two states the audit executed are now both reachable: a checkpoint that corrects no audit
  passes its mirror, and the first delivery of the next Gate reaches `READY_FOR_REVIEW`.
- The positive simulation executes `m0_mirror_audit.py` instead of writing the artifact it would
  have produced, which is how the defect survived a green rehearsal.
- The sealed audit reports of all three independent audits parse, without moving the parse of the
  two earlier ones.
- The engineering memory records the lesson, three new guardrails, and the `GUARDRAIL_FAILURE` of
  this recurrence against `LSN-0024` and `LSN-0029`, resolved here.
- `CLAUDE.md` records the permanent language rule for responses to the user.

## What was NOT completed

No Gate 0 work. `M0` has not passed: a milestone verdict is carried by a separate audit checkpoint
about a sealed subject, and this delivery is the subject. `independentReview` and `redTeam` are
`PENDING`, and `secondToolValidation` is `PENDING_MANUAL`, because an implementing run may not
record its own independent verdict.

Twenty-five *additional* attacks of the sealed `SETUP-00-CP-0011` battery were not re-executed.
They are not mandatory, and `AFFECTED-RED-TEAM.json` names each one rather than leaving the gap
implicit.

## Current repository state

Branch `main`, base commit `98a9f4ca83d538e9610844086ca74b7ff32492e1`, final commit bound by
`refs/tags/iacode-checkpoints/SETUP-00-CP-0012`. `STATE.json` records the exact values.

## Files changed

See `FILES.json` and `DIFF-SUMMARY.md`. No sealed checkpoint was modified, no historical tag was
moved and no commit was rewritten.

## Important decisions

See `DECISIONS.md`. The load-bearing ones: an empty applicable set is a first-class outcome and
justifies itself; the applicable set is derived from canonical sources that no delivery can shrink;
a simulation runs the control it reports; and the audit was registered because the protocol requires
it, not because registration is the fix.

## Tests executed

`python -m unittest discover -s tests`, with the result object read directly: 410 discovered, 410
run, 0 failures, 0 errors, 0 skipped. The same suite was executed again as the mandatory `tests`
gate of the Green Keeper cycle, and again in a clean clone. Also `python -m compileall -q scripts
tests`, `validate_lessons.py`, `verify_integrity.py`, `derive_counts.py`, `check_completeness.py`,
`derive_requirements.py`, `milestone_status.py`, `promotion_simulation.py`,
`successor_durability.py`, `mirror_semantics_validation.py`, `gate_transition_simulation.py`,
`affected_red_team.py`, `m0_red_team.py`, `m0_mirror_audit.py --clean-clone` and
`validate_checkpoint.py`.

## Known failures

None outstanding. Two recorded failures remain in `COMMANDS.jsonl` and one `STILL_RED` cycle remains
in `REWORK-LOG.jsonl`, deliberately: a failed attempt keeps its record so corrections stay visible.
The `STILL_RED` cycle is the one that found the declared change set incomplete after the
completeness control was corrected; cycle three is `GREEN` over the full canonical mandatory set.

## Known risks

See `RISKS.md`. Especially: registering the audit gives this delivery work to close and could mask a
repair that only works when there is work, which is why the repair is proven where there is nothing
to close; `NOT_APPLICABLE` is a new state that must not become a bypass; and the verdict of this
delivery is internal.

## Do not repeat

Do not close a finding by writing the artifact a control would have produced; run the control. Do
not treat an unreadable report as a report with nothing in it. Do not let a control be stricter than
the policy it enforces: an empty applicable set and a delivery's own local requirement are both
legitimate states, and refusing them is the same defect twice.

## Required next action

Request a fresh-session independent `M0` audit of this checkpoint, as described in `NEXT.md`. Gate 0
stays blocked.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`,
   `docs/DEFINITION-OF-DONE.md`, `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`,
   `docs/checkpoints/LATEST.md` and this complete checkpoint.
2. Read `CP11-FINDINGS-CLOSURE.md` and the sealed `SETUP-00-CP-0011/REVIEW-REPORT.md`, in that
   order, and verify the closure against the sealed report rather than against the record.
3. Run the validation commands below and compare the observed Git state with `STATE.json`.
4. Follow `NEXT.md`.

## Validation commands

- `git status --short --branch`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0012`
- `python scripts/development-ledger/validate_checkpoint.py`
- `python scripts/development-ledger/validate_lessons.py`
- `python scripts/development-ledger/verify_integrity.py`
- `python scripts/development-ledger/derive_counts.py`
- `python scripts/development-ledger/check_completeness.py`
- `python scripts/development-ledger/derive_requirements.py`
- `python scripts/development-ledger/milestone_status.py --milestone M0` — expect
  `MILESTONE_NOT_PASSED` with no attestation for this delivery; the verdict belongs to the audit
  that follows it, and its absence is the honest state, not a failure
- `python scripts/development-ledger/mirror_semantics_validation.py`
- `python scripts/development-ledger/gate_transition_simulation.py`
- `python scripts/development-ledger/promotion_simulation.py`
- `python scripts/development-ledger/successor_durability.py`
- `python scripts/development-ledger/affected_red_team.py`
- `python scripts/development-ledger/m0_red_team.py`
- `python scripts/development-ledger/m0_mirror_audit.py --clean-clone`
- `python docs/checkpoints/SETUP-00-CP-0012/audit-harness/final_internal_audit.py`
- `python -m compileall -q scripts tests`
- `python -m unittest discover -s tests`

## Stop conditions

Stop on unexpected Git divergence, on a failing validation, on any need to modify a sealed
checkpoint or move a historical tag, on secret exposure, and on any attempt to begin Gate 0 while
`M0` has not passed.
