# Handoff

Current Gate: SETUP-00
Current Status: READY_FOR_REVIEW

Last valid commit: 28c2b487baf216d3745bb6c5a25a5b8aa7274a9e
Current branch: main

Checkpoint schema version: `3.2.0`. Base checkpoint: `SETUP-00-CP-0009` at
`28c2b487baf216d3745bb6c5a25a5b8aa7274a9e`. Final reference:
`refs/tags/iacode-checkpoints/SETUP-00-CP-0010`, to be resolved with `git rev-parse`.

## Objective

Close every finding of the fresh-session `M0` audit sealed as `SETUP-00-CP-0009`, and make a
milestone PASS reachable by an honest sequence of repository states. Gate 0 is not started.

## What was completed

- `CP9-F-001`: the milestone verdict now belongs to the audit checkpoint, which names an already
  sealed subject and the commit that subject's canonical tag resolves to. The attestation never
  names its own commit, the subject is never rewritten, and the verdict is derived by
  `milestone_status.py`. The whole promotion is executed end to end by `promotion_simulation.py`.
- `CP9-F-002`: the checkpoint whose anchor is still owed is derived by `anchors`, and the CLI, the
  validator and the suite ask the same helper. `successor_durability.py` seals three checkpoints in
  succession and re-runs the integrity controls at every state.
- `CP9-F-003`: the stale cardinality is gone, the policy decision is recorded in
  `docs/QUALITY-GATES.md`, and the suite refuses a count written in a comment or a docstring.
  Recorded as a recurrence of `LSN-0022` with its guardrail failure resolved here.
- `CP9-F-004`: `LSN-0014` records the residual limit of its control, and a `GUARDED` lesson that
  calls itself unguarded is refused.
- `CP9-F-005`: the unread policy key is removed, the registry path is documented as fixed, and the
  memory policy document is validated against a closed schema.
- The defects `SETUP-00-CP-0009` disclosed about itself are prevented: one physical test execution
  counts once, a count larger than what exists is refused, every adversarial battery records its
  null-mutation control, and adversarial totals are reported by derived, non-overlapping categories.
- Eight lesson candidates assessed, seven lessons and seven guardrails registered, the preflight
  regenerated, and the Gate retrospective written.
- `SETUP-00-CP-0009` anchored in the integrity chain, which its own checkpoint could not do.

## What was NOT completed

The independent review, the independent Red Team and any Gate verdict. `secondToolValidation` is
`PENDING_MANUAL`, `milestone.status` is `PENDING`, and `.iacode/attestations/` holds no attestation:
this delivery is the subject of the next audit, not its author. Gate 0 remains unimplemented and
unauthorized.

## Current repository state

Branch `main`, clean after the sealing commits, base commit
`28c2b487baf216d3745bb6c5a25a5b8aa7274a9e`, final commit bound by
`refs/tags/iacode-checkpoints/SETUP-00-CP-0010`. `STATE.json` records the exact values.

## Files changed

See `FILES.json`, verified against the real change set since the base commit with content hashes,
and `DIFF-SUMMARY.md`. No sealed checkpoint was modified and no historical tag was moved.

## Important decisions

See `DECISIONS.md` and
[ADR-0011](../../adr/ADR-0011-audit-checkpoint-carries-the-verdict.md). The load-bearing one: a
verdict belongs to the checkpoint that performed the audit, not to the delivery it judges, and a
control is finished only when its positive path has been executed.

## Tests executed

`python -m unittest discover -s tests`, recorded once because it is one execution covering the unit
and integration categories. `COUNTS.json` carries the derived result and `TESTS.json` records the
`runId` that makes the deduplication visible. Also `python -m compileall -q scripts tests`,
`validate_lessons.py`, `verify_integrity.py`, `check_completeness.py`, `derive_counts.py`,
`derive_requirements.py`, `m0_red_team.py`, `m0_mirror_audit.py --clean-clone`,
`promotion_simulation.py`, `successor_durability.py`, `affected_red_team.py`,
`milestone_status.py` and `git diff --check`.

## Known failures

None at handoff. The baseline of this delivery inherited the red `tests` gate the audit reported as
`CP9-F-002`; it was repaired by deriving the rule, never by editing an assertion, and the repair is
recorded in `REWORK-LOG.jsonl`.

## Known risks

See `RISKS.md`. Especially: the trust model of a milestone verdict is structural, not cryptographic;
nothing in this checkpoint is independent validation; and the accepted independence for the next
audit is session independence, not tool independence.

## Do not repeat

Do not treat a control as finished when only its refusals are executed. Do not name a historical
checkpoint inside a generic guard, test or policy. Do not add the same physical test run to itself.
Do not believe an adversarial battery that has no null-mutation control. Do not declare a
configuration key that no code reads. Do not describe a same-tool audit as cross-tool validation.

## Required next action

The fresh-session independent `M0` audit described in `NEXT.md`. The auditor authors its own
checkpoint, anchors this one, writes the attestation about it, and closes at
`MILESTONE_INDEPENDENT_AUDIT_PASS` or `REWORK_REQUIRED`. This checkpoint is never rewritten.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/SETUP-00-CHECKLIST.md`, `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`,
   `docs/HANDOFF-PROTOCOL.md`, `docs/DEFINITION-OF-DONE.md`, `docs/ENGINEERING-MEMORY.md`,
   `docs/MILESTONE-VALIDATION.md`, `docs/checkpoints/LATEST.md`, and this complete checkpoint.
2. Read `CP9-FINDINGS-CLOSURE.md` first: it carries, per finding, the root cause, the
   implementation, the regression tests, the negative tests and the verification command.
3. Run the validation commands below and compare the observed Git state with `STATE.json`.
4. Audit this checkpoint from a clean clone detached at its canonical tag.
5. Follow `NEXT.md` to record the verdict in your own checkpoint.

## Validation commands

- `git status --short --branch`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0010`
- `python scripts/development-ledger/validate_checkpoint.py`
- `python scripts/development-ledger/validate_lessons.py`
- `python scripts/development-ledger/verify_integrity.py`
- `python scripts/development-ledger/derive_counts.py`
- `python scripts/development-ledger/check_completeness.py`
- `python scripts/development-ledger/derive_requirements.py`
- `python scripts/development-ledger/milestone_status.py --milestone M0` — expect
  `MILESTONE_NOT_PASSED` until an audit attestation exists; that is the honest state, not a failure
- `python scripts/development-ledger/promotion_simulation.py`
- `python scripts/development-ledger/successor_durability.py`
- `python scripts/development-ledger/m0_red_team.py`
- `python scripts/development-ledger/m0_mirror_audit.py --clean-clone`
- `python scripts/development-ledger/affected_red_team.py`
- `python -m compileall -q scripts tests`
- `python -m unittest discover -s tests`
- `git diff --check 28c2b487baf216d3745bb6c5a25a5b8aa7274a9e HEAD`

## Stop conditions

Stop on unexpected Git divergence, on a failing validation, on any need to modify a sealed
checkpoint or move a historical tag, on secret exposure, or on any request to begin Gate 0 without
authorization.
