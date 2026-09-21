# Next

## Required next action

`CORRECT CP11-F-001 AND REQUEST A NEW M0 AUDIT`.

`M0` did not pass. `SETUP-00` returns to the implementer and `GATE 0 — FOUNDATION` stays `BLOCKED`.
This checkpoint is the audit; it is never rewritten, and the correction belongs in a new delivery
checkpoint, `SETUP-00-CP-0012`.

## The finding

`CP11-F-001`, `CRITICAL`: the internal mirror audit reports `FAIL` for any checkpoint that corrects
no audit, because `MIR-002` and `MIR-003` treat "nothing to audit" as a failure instead of as
`NOT_APPLICABLE`, and `validate_checkpoint` requires a passing mirror for every positive terminal
status. The consequence was executed, not predicted: this audit cannot close at
`MILESTONE_INDEPENDENT_AUDIT_PASS`, and the first `GATE 0` delivery cannot reach
`READY_FOR_REVIEW`.

`REVIEW-REPORT.md` carries the root cause, the acceptance criteria and the regression scenario.
`AUDIT-EXECUTIONS.json` carries the executions under `mirrorReachability`.

## The corrective delivery

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/DEFINITION-OF-DONE.md`,
   `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`, `docs/checkpoints/LATEST.md` and
   this complete checkpoint, `REVIEW-REPORT.md` first.
2. Register this audit in `.iacode/policies/audit-registry.json` with `auditId` `M0-CP-0011`,
   `auditCheckpoint` `SETUP-00-CP-0011`, `subjectCheckpoint` `SETUP-00-CP-0010`, the commit its tag
   resolves to, `correctiveCheckpoint` `SETUP-00-CP-0012`, `reviewReport`
   `docs/checkpoints/SETUP-00-CP-0011/REVIEW-REPORT.md`, `redTeamReport`
   `docs/checkpoints/SETUP-00-CP-0011/RED-TEAM-REPORT.md` and a `findingsClosureFile`. The finding
   and the mandatory attacks are then re-parsed from the sealed reports, so the expected requirement
   set of the corrective delivery cannot be shrunk. Registering the audit also makes the mirror
   audit of that delivery satisfiable, which is a side effect and not the fix: the fix is that a
   delivery which corrects nothing must also be able to pass.
3. Open `SETUP-00-CP-0012`, run the lesson preflight, derive the requirement set, and follow the
   whole mandatory delivery order.
4. Close `CP11-F-001` with the regression scenario the review names: a test that creates a
   checkpoint with no open audit in a disposable clone, runs the mirror audit over it, and asserts a
   `PASS` with the two checks recorded as `NOT_APPLICABLE` with reasons; and a positive-path
   simulation that produces the mirror report by executing the tool rather than by writing it.
5. Record the recurrence. `LSN-0024` and `LSN-0029` are both `GUARDED` and both classes repeated, so
   this is a `GUARDRAIL_FAILURE` against each: investigate the controls, not only the defect.
   `promotion_simulation.py` rehearsed the audit checkpoint reaching a milestone status while
   writing the mirror artifact by hand, which is exactly how the rehearsal passed and the real path
   stayed blocked.
6. Assess the five observations in `AUDIT-EXECUTIONS.json`. None requires action; each records the
   condition that would make it a finding.
7. Close at `READY_FOR_REVIEW` and request a new fresh-session independent `M0` audit, which authors
   its own checkpoint, anchors `SETUP-00-CP-0012`, and writes its attestation about it.

## What must not happen

- Do not rewrite, re-tag or re-seal this checkpoint or any sealed predecessor.
- Do not close the finding by writing the mirror artifact by hand; that is how it escaped.
- Do not record an internal verdict as independent validation, and do not describe a same-tool audit
  as cross-tool validation.
- Do not begin Gate 0.

## Next Gate

`GATE 0 — FOUNDATION`: `BLOCKED`. It requires a passing `M0` audit, explicit authorization, and a
new pre-Gate checkpoint. No Gate 0 work exists in this change set and none was started.
