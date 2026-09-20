# Plan

## Objective

Correct every finding of the independent Codex validation recorded in `SETUP-00-CP-0004`, and make
two new delivery-assurance controls mandatory for every future IACode delivery: a Test Rework / Green
Keeper role that forbids shipping anything red, and a Delivery Completeness Validator that audits the
requirements matrix before handoff. Close at `READY_FOR_REVIEW`. Do not start Gate 0.

## Baseline

Recorded before any change: branch `main`, `HEAD = c2eea150de9c97cfab5429d1e1eb3d5285e585f7`, clean
worktree, `CHECKPOINT_VALID`, `python -m unittest discover -s tests` 75 of 75 passing in 72.787s,
`python -m compileall -q scripts tests` exit 0. `SETUP-00-CP-0004` is `REWORK_REQUIRED` with
`secondToolValidation.status = FAILED`.

## Requirements

The authoritative scope is `REQUIREMENTS-MATRIX.json`, written before implementation and rendered in
`REQUIREMENTS-MATRIX.md`. It carries 38 requirements extracted from `SETUP-00-CP-0004` and from the
authorizing prompt. No requirement exists only in session memory.

## Findings being corrected

| Finding | Source | Correction |
|---|---|---|
| R3.1 / RT-02 | Early finalization refusals never reach the ledger | Record the attempt before returning, with a canonical result code instead of a fabricated exit code |
| R3.2 | Recorded command strings do not resolve from their working directory | Record the interpreter and the repository-relative script path, and validate that the first path token exists |
| RT-01 | `READY_FOR_REVIEW` validated with a non-empty `blockedBy` | Make status and blocker state a universal invariant across every schema version |
| RT-02 | Command records are not fully auditable | Require runtime, commit, purpose, inputs, sanitized arguments, and a canonical result on every record |

## Steps

1. Introduce checkpoint `schemaVersion` `3.0.0`. New rules bind to `3.0.0`; `1.0.0`, `2.0.0`, and the
   sealed checkpoints keep the rules they were written against.
2. Extend the command schema with the reproducibility fields and the canonical result vocabulary, and
   add `scripts/development-ledger/record_command.py` so compliant records are produced by tooling
   rather than by hand.
3. Record every finalization attempt, including preconditions refused before execution.
4. Enforce the status and blocker invariant for every version, and the `READY_FOR_REVIEW` invariants
   for `3.0.0`.
5. Add the canonical role contracts and adapters for the Green Keeper and the Delivery Completeness
   Validator.
6. Add `green_keeper.py` and `check_completeness.py` as the evidence harnesses for the two new gates,
   with `REWORK-LOG.jsonl` and `COMPLETENESS-REPORT.json` plus their schemas.
7. Make `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` preconditions of `READY_FOR_REVIEW` in
   the validator and in `STATE.json`.
8. Make the eleven-step delivery order mandatory across the protocol documents and both tool adapters.
9. Add the mandated regressions plus regressions for every finding, then run the full re-execution
   sequence, escalating to the Green Keeper on any red result.
10. Run the Delivery Completeness Validator until coverage is total, then finalize, commit, tag, and
    validate.

## Probable files

`scripts/development-ledger/*.py`, `.iacode/schemas/*.json`, `.iacode/agents/*.md`,
`.claude/agents/*.md`, `tests/test_development_ledger.py`, `docs/DEVELOPMENT-CONTRACT.md`,
`docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`,
`docs/DEFINITION-OF-DONE.md`, `docs/SETUP-00-CHECKLIST.md`, `START-HERE.md`, `AGENTS.md`, `CLAUDE.md`,
a new ADR, and this checkpoint.

## Success criteria

Every requirement `COMPLETE` or justified `NOT_APPLICABLE` with resolvable evidence; coverage total;
`GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` both `PASS`; suite green with no regression; the
four sealed checkpoints still validating; the RT-01 and RT-02 reproductions now failing as attacks;
checkpoint valid at `READY_FOR_REVIEW`; handoff executable by Codex without this session.

## Tests

The existing 75 plus regressions for R3.1, R3.2, RT-01, RT-02, the thirteen mandated control cases,
schema validation for the three new documents, and gate enforcement.

## Risks

Schema evolution can invalidate sealed checkpoints; the new gates can become self-referential; a
completeness audit can degenerate into self-certification; the two new roles can be described as more
independent than the tooling allows. Each is addressed by version dispatch, by machine-recomputed
evidence, by verifiable evidence references, and by explicit documentation of the emulation limits.

## Stop conditions

Stop on unexpected Git divergence, on any need to modify a sealed checkpoint, on a red gate that
cannot be corrected inside SETUP-00 scope, on secret exposure, or on any request to begin Gate 0.
