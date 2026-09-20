# Handoff

Current Gate: SETUP-00
Current Status: READY_FOR_REVIEW

Last valid commit: ae563f860856e3ce5ca9ec6e94b6202ed7e4a4e4
Current branch: main

Checkpoint schema version: `2.0.0`. Base checkpoint: `SETUP-00-CP-0002` at
`ae563f860856e3ce5ca9ec6e94b6202ed7e4a4e4`. Final reference:
`refs/tags/iacode-checkpoints/SETUP-00-CP-0003`, to be resolved with `git rev-parse`.

## Objective

Correct the six defects that an independent Claude Code review found in the sealed `SETUP-00-CP-0002`,
without modifying any sealed checkpoint and without starting Gate 0, and hand the result to Codex for
the independent verdict.

## What was completed

- R1 — Detached `HEAD` no longer produces a false negative. Validation accepts a detached checkout only
  at the checkpoint's own canonical tag, with a clean worktree and an exact tag-to-`HEAD` match; a
  wrong branch, wrong commit, moved tag, or dirty tree still fails, and finalization refuses a
  detached `HEAD`.
- R2 — The file inventory of a delta checkpoint is recomputed from Git and must match `FILES.json`
  exactly, with `hashAfter` on added and modified paths and `hashBefore` on modified and deleted
  paths. `FILES.json` is the only self-referential exclusion, declared in code and justified in
  ADR-0006.
- R3 — Every finalization attempt appends its own record with its exit code; failures keep their
  record and a sanitized reason summary; the successful attempt is recorded before the hashes seal.
- R4 — Cross-tool validation is the structured `secondToolValidation` object in `STATE.json`. The
  hardcoded `SECOND_TOOL_VALIDATION = PENDING_MANUAL` requirement now binds only `1.0.0` checkpoints.
- R5 — `docs/SETUP-00-CHECKLIST.md` is the in-repository SETUP-00 specification, referenced by the
  Master Plan and the start protocol.
- R6 — Static analysis was re-executed and recorded, and a `PASS` in a `2.0.0` `QUALITY.json` now
  requires a resolvable evidence reference.
- Schema `2.0.0` was introduced with version-dispatched validation, and both sealed checkpoints were
  proven to still validate under the corrected tooling.
- The suite grew from 37 to 75 tests, including the regressions listed below.

## What was NOT completed

Genuine cross-tool validation, the independent review, the independent Red Team, and any Gate verdict.
The CLI installation at `C:/Users/cesar/.local/bin/claude.exe` is still unauthenticated; machine
authentication was not changed. Gate 0 remains unimplemented and unauthorized. The secret detector's
scope was deliberately left unchanged.

## Current repository state

Branch `main`, clean after the sealing commit, base commit
`ae563f860856e3ce5ca9ec6e94b6202ed7e4a4e4`, final commit bound by
`refs/tags/iacode-checkpoints/SETUP-00-CP-0003`. `STATE.json` records the exact values.

## Files changed

See `FILES.json`, which is now verified against the real change set since the base commit, including
content hashes. In summary: the four ledger scripts and their README, five schemas, the test suite,
the new SETUP-00 checklist, two new ADRs, six protocol or specification documents, both tool adapters,
the detected capabilities document, `LATEST.md`, and this checkpoint.

## Important decisions

See `DECISIONS.md`, ADR-0006, and ADR-0007. The load-bearing ones: version the format instead of
rewriting history; bind the inventory to Git rather than to an assertion; make finalization
observable; replace prose status with structured state; and forbid the implementing run from granting
its own Gate.

## Tests executed

`python -m unittest discover -s tests` — 75 tests, 0 failures, recorded in `TESTS.json` and
`COMMANDS.jsonl`. `python -m compileall -q scripts tests` — exit 0. The adversarial battery in
`RED-TEAM-DEV-REPORT.md` was executed against isolated copies and clones outside the repository.

## Known failures

All recorded in `COMMANDS.jsonl` with their exit codes:

- `cmd-0008` and `cmd-0009`: suite runs that failed while the lifecycle test still predated the new
  inventory contract, and while `docs/SETUP-00-CHECKLIST.md` did not yet exist.
- `cmd-0013`, `cmd-0017`, and `cmd-0018`: validation runs that failed before the inventory was
  declared, after the ledger grew past the declared hash, and on a self-referential evidence
  reference. Each was corrected before the next attempt.
- `cmd-0021`: the deliberate correction cycle described below.

Two finalization attempts also failed with exit 1 during the sealing rehearsal, which ran in an
isolated copy outside the repository; those records lived and died with that fixture and are
described in `RED-TEAM-DEV-REPORT.md`, not in this ledger. The finalizations recorded here are the
real ones.

## Known risks

See `RISKS.md`, especially the still-pending cross-tool validation, the `NOT_REQUIRED` escape hatch,
the dependence of the inventory on tag immutability, and the unchanged secret-detector scope.

## Do not repeat

Do not modify or retag `SETUP-00-CP-0001`, `SETUP-00-CP-0002`, or this checkpoint. Do not treat this
run's self-review or development Red Team as independent verification. Do not grant `GATE_PASS` from
the run that implemented the change. Do not declare a `PASS` without a resolvable evidence reference.
Do not start Gate 0 without an explicit authorization and a `GATE_PASS` on SETUP-00.

## Required next action

Codex performs the independent review and Red Team described in `NEXT.md` and records the verdict in a
new checkpoint.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/SETUP-00-CHECKLIST.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/QUALITY-GATES.md`,
   `docs/HANDOFF-PROTOCOL.md`, `docs/DEFINITION-OF-DONE.md`, `docs/checkpoints/LATEST.md`, and this
   complete checkpoint.
2. Read ADR-0006 and ADR-0007, which carry the reasoning for the schema change.
3. Run the validation commands below and compare the observed Git state with `STATE.json`.
4. Review the diff `git diff ae563f860856e3ce5ca9ec6e94b6202ed7e4a4e4..refs/tags/iacode-checkpoints/SETUP-00-CP-0003`.
5. Re-run the reproducible attacks listed in `RED-TEAM-DEV-REPORT.md` against an isolated clone, and
   add your own.
6. Record the verdict in a new checkpoint that sets `secondToolValidation`. Never edit this one.

## Validation commands

- `git status --short --branch`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0003`
- `python scripts/development-ledger/validate_checkpoint.py`
- `python -m unittest discover -s tests`
- `python -m compileall -q scripts tests`
- `git diff --check ae563f860856e3ce5ca9ec6e94b6202ed7e4a4e4 HEAD`
- From a clean clone, detached at the checkpoint tag:
  `git clone --no-local <repo> <tmp>; git -C <tmp> checkout --detach refs/tags/iacode-checkpoints/SETUP-00-CP-0003; python <tmp>/scripts/development-ledger/validate_checkpoint.py`

## Criteria for PASS

All six findings corrected with executable evidence; the full suite green with no regression; both
sealed checkpoints still validating under the corrected tooling; the inventory attacks detected; the
checkpoint valid; the handoff reproducible without this session; no sealed artifact modified; no Gate 0
work present.

## Criteria for REWORK_REQUIRED

Any finding not actually corrected; any regression; any sealed checkpoint made invalid or modified; any
`PASS` without resolvable evidence; any attack that still escapes detection and is not documented as an
accepted limit with its rationale; any inconsistency between `STATE.json`, the ledger, and the
repository.

## Stop conditions

Stop on unexpected Git divergence, on a failing validation, on any need to modify a sealed checkpoint,
on secret exposure, or on any request to begin Gate 0 without authorization.
