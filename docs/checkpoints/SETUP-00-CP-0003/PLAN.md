# Plan

## Objective

Correct six defects found by an independent Claude Code review of the sealed `SETUP-00-CP-0002`
without modifying any sealed checkpoint, without rewriting history, and without starting Gate 0.
The checkpoint closes at `READY_FOR_REVIEW`; only a later independent Codex run may grant `GATE_PASS`.

## Baseline

Recorded before any change: branch `main`, `HEAD = ae563f860856e3ce5ca9ec6e94b6202ed7e4a4e4`,
clean worktree, no remote, `validate_checkpoint.py` returned `CHECKPOINT_VALID`,
`python -m unittest discover -s tests` passed 37 of 37, `compileall` returned 0.

## Steps

1. Introduce checkpoint schema version `2.0.0` alongside `1.0.0`. New rules bind only to `2.0.0`;
   sealed `1.0.0` checkpoints keep the rules that applied when they were written.
2. R1 — Accept a detached `HEAD` only when the worktree is clean, `HEAD` equals the resolved
   `currentCommit`, and the checkpoint's canonical tag exists and resolves to that same commit.
   Keep the branch identity requirement when `HEAD` is attached.
3. R2 — Enforce the file inventory for delta checkpoints. Compute the real change set between
   `baseCommit` and the validated tree and require `FILES.json` to match it exactly, with
   `hashAfter` for added files, `hashBefore` and `hashAfter` for modified files, and `hashBefore`
   for deleted files. Document the single self-referential exclusion in an ADR.
4. R3 — Make finalization observable. Every finalization attempt appends its own sanitized record
   with its exit code to `COMMANDS.jsonl`; failures stay recorded; the successful attempt is
   recorded before the manifest hashes are sealed so the final state is reproducible.
5. R4 — Replace the hardcoded `SECOND_TOOL_VALIDATION = PENDING_MANUAL` text requirement with a
   structured `secondToolValidation` object in `STATE.json` carrying an explicit status.
6. R5 — Create `docs/SETUP-00-CHECKLIST.md` as the in-repository SETUP-00 specification and point
   `MASTER-PLAN.md` and the start protocol at it.
7. R6 — Re-execute static analysis and record it; require every `PASS` in a `2.0.0`
   `QUALITY.json` to carry resolvable evidence references.
8. Add regression tests for every item above, re-run the full suite, and re-run the adversarial
   battery, including the three attacks that previously escaped detection.
9. Update the protocol documents, ADRs, and tool adapters, then finalize, commit, tag, and validate.

## Probable files

`scripts/development-ledger/*.py`, `.iacode/schemas/*.json`, `tests/test_development_ledger.py`,
`docs/SETUP-00-CHECKLIST.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/QUALITY-GATES.md`,
`docs/HANDOFF-PROTOCOL.md`, `docs/DEFINITION-OF-DONE.md`, `docs/MASTER-PLAN.md`,
`docs/TOOL-CAPABILITIES.md`, `START-HERE.md`, `AGENTS.md`, `CLAUDE.md`, new ADRs, and this checkpoint.

## Success criteria

All six findings corrected with executable evidence; the previously undetected inventory attacks
detected; the full suite green with no regression; sealed checkpoints still validate under the new
tooling; checkpoint valid at `READY_FOR_REVIEW`; handoff executable by Codex without this session.

## Tests

Existing 37 tests plus regressions for detached-HEAD validity and invalidity, delta inventory
completeness and hash binding, finalization recording, cross-tool validation states, checklist
presence and link resolution, and quality evidence references.

## Risks

Schema evolution can break sealed checkpoints; inventory hashing can become self-referential;
finalization recording can become circular; over-broad detached-HEAD acceptance can weaken the
commit anchor. Each is addressed by an explicit rule plus a regression test.

## Stop conditions

Stop on unexpected Git divergence, on any need to modify a sealed checkpoint, on a failing test that
cannot be corrected inside SETUP-00 scope, on secret exposure, or on any request to begin Gate 0.
