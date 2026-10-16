# Handoff

Current Gate: GATE-4
Current Status: IN_PROGRESS

Last valid commit: ff2814f7d7bf06fa8a99858b958daf3f22197496
Current branch: main

## Objective

Internally audit sealed CP0009, correct genuine Gate 4 defects and establish a truthful internal
closure under the owner's explicitly authorized milestone cadence before starting Gate 5.

## What was completed

CP0009 validated at entry without divergence. Lesson preflight and canonical derivation ran before
correction. The cancellation race was reproduced, escalated as a guarded recurrence and repaired
with durable reconciliation and a serialized verdict barrier. ADR-0037/0038 and their index record
the cadence and lifecycle decisions. Targeted contracts, rebuilt evaluator, lint, real PostgreSQL
serialization and live cancellation/cleanup proof passed. Commands and reports carry the evidence.

## What was NOT completed

V3 is now completed PASS: cmd-0299, 42/42 stages, 6500.5 seconds, all isolation checks green and
temporary clone removed. Cmd-0300 archived its five reports unchanged under attempts/published-v3.
The active-v3 descriptions below are historical. This passing older subject cannot approve the
later program-state changes; complete published v4 verification and all final assurance remain due.

Published immutable v3 (0b1fa85) is executing in its untouched remote clone, but cannot approve the
later resumability correction. Cmd-0266 exposed missing current steps; ADR-0045 corrects live-state
storage/status/identity, and nine real CLI/Git controls pass (cmd-0273). Preserve v3's actual result
after it completes and publish a new subject for full current-source verification. No product or
driver inputs in the active clone are edited; no concurrent Docker proof runs. Current obligations
derive to 220; Gate 5 remains unstarted until the complete corrected internal closure is sealed.

The full published verifier, fresh ordered Green Keeper, completeness, internal A-T Red Team,
clean-clone mirror, terminal internal closure, sealing and publication remain pending. Gate 5 has
not started. Independent M2 review, independent Red Team and second-tool validation remain pending.
The v2 verifier completed FAIL with 41/42 stages green and ten root failures across 801 cases.
All five reports are archived unchanged in attempts/published-v2. A same-session all-32-anchor
component probe reproduced nine collection incompatibilities; policy 1.1.0 now retains historical
semantics while keeping current exclusions strict. Cmd-0197 reproduced the exact published-v2
UTF-8 failure and cmd-0198 passed all 29 current Foundation controls after correction.
Actual current-tool validation passed all 32 canonical published tags (cmd-0202). G4-INT-017,
G4-INT-019 and G4-INT-021 are fixed pending final assurance; v2 remains failed and cannot be promoted.

G4-INT-022's stale wrapper write is corrected. Five current-checkpoint boundary controls passed,
and actual validation in a complete owned copy refused the legacy wrapper but accepted the current
one (cmd-0225). The copy was removed. The local broad run completed FAIL: 812 loaded cases and five
mixed-epoch refusals after a late source/registry edit (LOCAL-ROOT-REGRESSION.json). The new published full verifier and fresh
Green Keeper must execute the complete latest suite before final closure.

ADR-0044 binds both process owners to pre-execution input digests. Both real rewriting/stable
controls pass (cmd-0236); cmd-0200 remains qualified and non-successful, without invented launch
bytes. The selected cmd-0238/0239 memory runs refused a stale generated LESSONS.md; regenerate it
before fresh diagnostics. No partial or selected green result may promote any failed broad run.

The regenerated index is valid (cmd-0240); the complete selected set of 27 memory-policy, command
binding and provenance controls passed in one fresh process (cmd-0246). Final-source transport,
collection, metadata, input-snapshot and failure-diagnostic modules passed (cmd-0241 through 0245).
Their causal greens do not replace full v3 verification or the ordered closure sequence.

## Current repository state

This is a deliberate dirty IN_PROGRESS successor on main, based on sealed CP0009 at ff2814f7.
STATE.json binds HEAD while implementing. FILES.json declares the full delta before validation.
No sealed CP0009 file is changed and no canonical tag is moved.

## Files changed

See FILES.json.

## Important decisions

See DECISIONS.md.

## Tests executed

Cmd-0011: Gate 4 contract suite passed. Cmd-0012: memory-policy controls passed. Cmd-0013:
rebuilt evaluator suite passed. Cmd-0015: Python and frontend lint passed. Cmd-0016: actual SQL
arrival-order/concurrency controls and live terminal cancellation with cleanup passed.

## Known failures

Cmd-0005 reproduced LATE_RESULT at cancellation completion. Cmd-0009 exposed a new fixture's
missing default in its canonical verdict digest; cmd-0013 subsequently passed. Cmd-0014 refused
overlong new test lines; cmd-0015 subsequently passed without weakening lint. Cmd-0007/0008 were
pre-execution filename refusals, followed by successful replayable glob invocations. All remain
preserved. FINDINGS.json and Engineering Memory classify these observations.

## Known risks

See RISKS.md.

## Corrective evidence update

- Published v1 subject remains 33c3f42c0d5faf112c3e037a55006dd750c4bfe1, tagged
  iacode-subjects/GATE-4-CP-0010-internal-corrective-v1. It is not the corrected final subject.
- The completed v1 execution has a red root suite and a red quality-iacode stage. Its
  bounded V1-POLLING-FAILURE.json proves a FAILED Temporal workflow caused by a cancelled durable
  polling read while the API remained RUNNING. All reports are archived in attempts/published-v1;
  VERIFICATION-ATTEMPT-ARCHIVE.json binds their unchanged bytes. Its 40 of 42 green stages do not
  approve the corrected subject.
- ADR-0039 implements first-durable-boundary output containment, including full decoded streams,
  provisioning diagnostics, nested JSON and JSON records mixed with ordinary tool output.
- ADR-0040 fixes static counts/evidence that included uncollected live input projects; no actual
  regression or functional input is removed. ADR-0041 fixes typed polling cleanup and handle lifetime.
- Rebuilt evaluator: 83 passed, 6 integration deselected (cmd-0094). Sandbox: 165 passed,
  8 integration deselected (cmd-0114). API: 145 passed (cmd-0134). Lint: PASS (cmd-0148).
- Cmd-0119 passed the current 34-step real output proof, SQL integration, decoded Temporal history,
  MinIO absence, clean controls before/after refusals and owned cleanup; shared resources unchanged.
  Failed attempts 1, 2 and 4 and superseded passing attempt 3 remain separate artifacts.
- The publication scanner now consumes the identical bounded transport views; five positive and
  negative controls passed (cmd-0155). Two decoded historical alphabet-sequence redaction markers
  were reviewed only by exact kind/component digest, with sanitized AST provenance. The full
  strengthened history scan passed with zero blocking findings (cmd-0149).
- ADR-0042 versions internal-verdict semantics in live policy 2.4.0. Both affected sealed legacy
  subjects passed current-tool remote-clone validation with unchanged Git state (cmd-0140).
- Cmd-0156 passed all 35 selected promotion and memory-policy controls, including the honest sealed
  subject/audit sequence and refusal to substitute a fresh-session audit for external validation.
- The latest derived set contains 105 canonical and 114 applicable lesson obligations. Requirements
  are not marked complete until the corrected immutable-subject verifier passes.
- Functional acceptance now derives the original twelve requirements plus mandatory output
  containment. The guarded writer complete_functional_acceptance.py may run only after a new
  complete published execution passes. No acceptance verdict has been generated prematurely.

No final Gate verdict is asserted by these targeted executions. The requirement matrix remains
derived but uncompleted until the corrected immutable-subject verifier passes.

## Do not repeat

Do not edit CP0009, assert same-session independence, mark M2 PASSED, reduce a denominator,
reuse red verifier stages, hide a failure, alter product timeouts, or mix Gate 5 into a Gate 4 commit.

## Required next action

Follow PLAN.md and NEXT.md: finish all internal corrective assurance, then seal a valid
INTERNAL_GATE_PASS before starting the explicitly authorized Gate 5 separately.

## Exact continuation sequence

The corrected immutable v2 subject is published at 4c53e4f788adc24e1b9cd9f581a7dc0d0f3c1340 with
tag iacode-subjects/GATE-4-CP-0010-internal-corrective-v2. Its single full remote-clone verifier is
completed FAIL and archived. All ten failure causes have causal reproductions; retain every red result, complete
versioned collection and scanner metadata proofs, then publish a new immutable subject and execute
all 42 stages in one non-fast invocation. A publication or targeted control is not approval.
Cmd-0162/VALIDATION-PERFORMANCE.json captured nonblocking stack frames in credential scanning during
bundle reconstruction and digest/size verification. The profiler was temporary and content-verified;
no locals or tested-code changes were made. This does not assert a passing or independent verdict.

After the complete passing execution, bind requirements to evidence, execute fresh Green Keeper,
completeness, internal Red Team and the full clean-clone mirror in that order. Finalize internal
closure, commit, seal, push and validate from a fresh published checkout. Then create Gate 5's own
checkpoint, specification and requirement set before its implementation.

## Validation commands

During implementation: `python docs/checkpoints/GATE-4-CP-0010/audit-harness/declare_inventory.py`,
then `python docs/checkpoints/GATE-4-CP-0010/audit-harness/run_checkpoint_validation.py`.
After commit/seal: `python scripts/development-ledger/validate_checkpoint.py` and
`python scripts/development-ledger/verify_integrity.py`; publication additionally requires
`python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-4-CP-0010`.

## Stop conditions

Stop on unexpected Git divergence, an unresolved external blocker, red mandatory control, stale
assurance, a reconstruction mismatch, secret finding, false independent claim or premature Gate 5 work.
