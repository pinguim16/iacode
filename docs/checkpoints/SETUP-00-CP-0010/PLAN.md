# Plan

## Objective

Close every finding of the fresh-session `M0` audit sealed as `SETUP-00-CP-0009`, and make a
milestone PASS reachable by an honest sequence of repository states. Gate 0 is not started.

## Authorized scope

`SETUP-00` only. The corrective delivery owns the product code, the tests, the schemas, the policies,
the engineering memory, the governing documents and this checkpoint. No sealed checkpoint, historical
tag or audit report is modified.

## Sequence executed

1. Cold start: read the canonical entry points and the complete `SETUP-00-CP-0009` checkpoint,
   including its review report, Red Team report, audit matrix, executions and lesson candidates.
2. Baseline: Git state, checkpoint validation, integrity, lessons, counts, static analysis and the
   full suite, recorded with the known `CP9-F-002` failure visible rather than hidden.
3. Lesson preflight for this Gate, then requirement derivation into `REQUIREMENTS-MATRIX.json` and
   `CLOSURE-REQUIREMENTS.json` before any product change.
4. `CP9-F-001`: separate the subject checkpoint from its auditor. The verdict moves to the audit
   checkpoint, which names an already sealed subject and the commit its canonical tag resolves to;
   the attestation never names its own commit; the milestone verdict is derived, never asserted; and
   the status vocabulary gains `MILESTONE_INDEPENDENT_AUDIT_PASS` so a same-tool audit is not
   described as external. Recorded as [ADR-0011](../../adr/ADR-0011-audit-checkpoint-carries-the-verdict.md).
5. `CP9-F-002`: one derived rule, `anchors.pending_anchor_exclusion`, for the CLI, the validator and
   the suite, plus a succession simulation that advances a sealed chain and re-checks every state.
6. `CP9-F-003`: remove the stale cardinality, decide and document that a count in a source comment or
   docstring is never evidence, and enforce it in the suite. Recorded as a recurrence of `LSN-0022`.
7. `CP9-F-004`: make the lesson note describe the residual limit, and refuse the contradiction.
8. `CP9-F-005`: remove the unread policy key, document the fixed registry path, and validate the
   policy document against a closed schema.
9. Prevent the defects `SETUP-00-CP-0009` disclosed about itself: deduplicate test-run counts, refuse
   a count larger than what exists, and require a null-mutation control in every adversarial battery.
10. Engineering memory: assess the eight lesson candidates, register the lessons and guardrails,
    record the guardrail failure and its repair, and regenerate the preflight.
11. Positive paths, executed: `promotion_simulation.py` and `successor_durability.py`.
12. Delivery order: Green Keeper, Delivery Completeness Validator, internal Red Team, Milestone
    Closure Auditor, clean clone, then `READY_FOR_REVIEW`.

## Verification

`python -m unittest discover -s tests`, `validate_checkpoint.py`, `validate_lessons.py`,
`verify_integrity.py`, `derive_counts.py`, `check_completeness.py`, `green_keeper.py`,
`m0_red_team.py`, `m0_mirror_audit.py`, `promotion_simulation.py`, `successor_durability.py`,
`milestone_status.py`, `python -m compileall -q scripts tests`, `git diff --check`.

## Stop conditions

An open finding, a red mandatory gate, an unreachable positive path, a stale gate result, a
guardrail failure left unresolved, any need to modify a sealed checkpoint or move a historical tag,
or any request to begin Gate 0 without authorization.
