# Handoff

Current Gate: SETUP-00
Current Status: READY_FOR_REVIEW

Last valid commit: c2eea150de9c97cfab5429d1e1eb3d5285e585f7
Current branch: main

Checkpoint schema version: `3.0.0`. Base checkpoint: `SETUP-00-CP-0004` at
`c2eea150de9c97cfab5429d1e1eb3d5285e585f7`. Final reference:
`refs/tags/iacode-checkpoints/SETUP-00-CP-0005`, to be resolved with `git rev-parse`.

## Objective

Correct every finding of the independent Codex validation recorded in `SETUP-00-CP-0004`, and make
two delivery-assurance controls mandatory for every future IACode delivery, so the independent tool
never again has to discover an unimplemented requirement, a forgotten prompt item, missing
documentation, a red test, a red quality gate, a partial artifact, or absent evidence.

## What was completed

- R3.1 and RT-02 — Every finalization attempt is recorded, including one refused by a precondition
  before the operation runs. The record carries the evaluated preconditions with observed values,
  `result = PRECONDITION_REJECTED`, a documented `resultCode`, a `failureReason`, and no fabricated
  exit code. Covered by `FinalizationAttemptRecordingTests`.
- R3.2 — Recorded commands are executable from their declared working directory. The finalizer now
  records `python scripts/development-ledger/finalize_checkpoint.py ...`, and validation rejects a
  bare script name or a path that does not resolve. Covered by `CommandReproducibilityTests`.
- RT-01 — `READY_FOR_REVIEW`, `READY_FOR_RED_TEAM`, and `GATE_PASS` are refused while `blockedBy` is
  non-empty, in every schema version; `BLOCKED` now requires a stated blocker. Reproduced end to end
  through the real finalizer and validator by `ResealedBlockerFixtureTests`.
- RT-02 — Command records carry identifier, timestamp, runtime, working directory, command, sanitized
  arguments, referenced inputs, repository commit, purpose, canonical result, exit or result code,
  duration, and stream artifacts. `record_command.py` produces them.
- Test Rework / Green Keeper: canonical contract, Claude adapter, Codex adoption through `AGENTS.md`,
  `green_keeper.py`, `REWORK-LOG.jsonl`, its schema, and the `GREEN_KEEPER_GATE`.
- Delivery Completeness Validator: canonical contract, Claude adapter, Codex adoption through
  `AGENTS.md`, `check_completeness.py`, `COMPLETENESS-REPORT.json` and `.md`, their schemas, and the
  `DELIVERY_COMPLETENESS_GATE`.
- Both gates are preconditions of `READY_FOR_REVIEW`, recomputed by the validator rather than
  trusted, and `independentReview` and `redTeam` must still be `PENDING`.
- The eleven-step delivery order is mandatory in eight governing documents.
- The suite grew from 75 to 131 tests.

## What was NOT completed

The independent review, the independent Red Team, and any Gate verdict. `secondToolValidation` remains
`PENDING_MANUAL`. Gate 0 remains unimplemented and unauthorized. The secret detector's scope was
deliberately left unchanged.

## Current repository state

Branch `main`, clean after the sealing commit, base commit
`c2eea150de9c97cfab5429d1e1eb3d5285e585f7`, final commit bound by
`refs/tags/iacode-checkpoints/SETUP-00-CP-0005`. `STATE.json` records the exact values.

## Files changed

See `FILES.json`, verified against the real change set since the base commit with content hashes. In
summary: seven ledger scripts and their README, eight schemas, the test suite, two canonical role
contracts and two Claude adapters, one new ADR, eight governing documents, `LATEST.md`, and this
checkpoint.

## Important decisions

See `DECISIONS.md` and ADR-0008. The load-bearing ones: extract requirements before implementing;
version the format instead of rewriting history; treat a refusal as an attempt; apply the status and
blocker invariant to every version; recompute gates instead of trusting them; and forbid the
implementing run from certifying itself.

## Tests executed

`python -m unittest discover -s tests` — 131 tests, 0 failures, recorded in `TESTS.json` and
`COMMANDS.jsonl`. `python -m compileall -q scripts tests` — exit 0.
`python scripts/development-ledger/validate_checkpoint.py` — `CHECKPOINT_VALID`. Every gate run is in
`REWORK-LOG.jsonl` with its ledger evidence.

## Known failures

Recorded in `REWORK-LOG.jsonl` and `COMMANDS.jsonl`: the first Green Keeper cycle failed on
checkpoint validation while the inventory was still undeclared, and a suite run failed because a
lifecycle fixture did not ship the ledger tooling whose path it recorded. Both were repaired at the
cause and re-executed. Any nonzero exit in `COMMANDS.jsonl` belongs to one of those cycles or to a
recorded finalization attempt.

## Known risks

See `RISKS.md`, especially the still-pending cross-tool validation, the emulated role separation, the
judgement calls behind `NOT_APPLICABLE` and external blockers, and the unchanged secret-detector
scope.

## Do not repeat

Do not modify or retag any sealed checkpoint. Do not treat this run's Green Keeper or completeness
audit as independent verification. Do not grant `GATE_PASS` from the run that implemented the change.
Do not record a `PASS` without resolvable evidence, a readiness status with a blocker, or a command
that cannot run from its declared working directory. Do not start Gate 0.

## Required next action

Codex performs the independent review and Red Team described in `NEXT.md` and records the verdict in
a new checkpoint.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/SETUP-00-CHECKLIST.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/QUALITY-GATES.md`,
   `docs/HANDOFF-PROTOCOL.md`, `docs/DEFINITION-OF-DONE.md`, `docs/checkpoints/LATEST.md`, and this
   complete checkpoint, including `REQUIREMENTS-MATRIX.md` and `COMPLETENESS-REPORT.md`.
2. Read ADR-0008 for the reasoning behind schema `3.0.0` and the two gates.
3. Run the validation commands below and compare the observed Git state with `STATE.json`.
4. Review `git diff c2eea150de9c97cfab5429d1e1eb3d5285e585f7..refs/tags/iacode-checkpoints/SETUP-00-CP-0005`.
5. Re-run the CP-0004 reproductions listed under verification below, plus your own attacks.
6. Record the verdict in a new checkpoint that sets `secondToolValidation`. Never edit this one.

## Validation commands

- `git status --short --branch`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0005`
- `python scripts/development-ledger/validate_checkpoint.py`
- `python -m unittest discover -s tests`
- `python -m compileall -q scripts tests`
- `python scripts/development-ledger/check_completeness.py`
- `git diff --check c2eea150de9c97cfab5429d1e1eb3d5285e585f7 HEAD`

## How to verify each CP-0004 finding

- R3.1 and RT-02, early refusal recorded: from a clean clone detached at the CP-0005 tag, count the
  records in `docs/checkpoints/SETUP-00-CP-0005/COMMANDS.jsonl`, run
  `python scripts/development-ledger/finalize_checkpoint.py --status READY_FOR_REVIEW --commit-ref refs/tags/iacode-checkpoints/SETUP-00-CP-0005`,
  observe exit `2`, and count again. The count must grow by one and the new record must read
  `result = PRECONDITION_REJECTED`, `resultCode = E_DETACHED_HEAD`, `exitCode = null`. Automated as
  `FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`.
- R3.2, executable command strings: every record in this checkpoint's ledger starts with an explicit
  runtime, and each `.py` token resolves from the repository root. Automated as
  `CommandReproducibilityTests` and
  `FinalizationAttemptRecordingTests.test_recorded_finalizer_command_is_executable_from_its_working_directory`.
- RT-01, blocker with readiness: in a clean clone, set `blockedBy` to a non-empty list, finalize for
  `READY_FOR_REVIEW`, reseal, and validate. Finalization and validation must both refuse with
  `incompatible with a non-empty blockedBy`. Automated as `ResealedBlockerFixtureTests`.
- Delivery gates: `DeliveryAssuranceGateTests` covers a green delivery and each way of faking one.
  `DeliveryLifecycleTests` runs the whole mandatory order end to end in an isolated repository.
- Historical immutability: `HistoricalCheckpointCompatibilityTests` validates clean clones detached
  at all four sealed tags under this tooling.

## Criteria for PASS

Every CP-0004 finding corrected with executable evidence; requirement coverage total with every
evidence reference resolving; both new gates `PASS` and recomputed as such; the suite green with no
regression; the four sealed checkpoints still validating; the RT-01 and RT-02 reproductions now
refused; the checkpoint valid; the handoff reproducible without this session; no sealed artifact
modified; no Gate 0 work present.

## Criteria for REWORK_REQUIRED

Any finding not actually corrected; any regression; any sealed checkpoint made invalid or modified;
any `PASS` without resolvable evidence; any gate assertable without earning it; any requirement whose
recorded status overstates reality; any attack that escapes and is not documented as an accepted
limit with its rationale; any inconsistency between `STATE.json`, the matrix, the reports, the
ledger, and the repository.

## Stop conditions

Stop on unexpected Git divergence, on a failing validation, on any need to modify a sealed
checkpoint, on secret exposure, or on any request to begin Gate 0 without authorization.
