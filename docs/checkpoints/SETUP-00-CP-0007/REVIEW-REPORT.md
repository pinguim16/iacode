# Independent Review Report — M0 / SETUP-00

Verdict: `REWORK_REQUIRED`  
Audit classification: independent cross-tool milestone audit  
Baseline: `994bab402873bc4d221c02d8c94bdebeb2b0f3cb` / `refs/tags/iacode-checkpoints/SETUP-00-CP-0006`  
Gate 0: `BLOCKED`

## Findings

### M0-F-001 — CRITICAL — positive terminal status bypasses delivery assurance

- Requirement: every positive terminal status must require Green Keeper PASS, delivery completeness PASS/100%, green mandatory quality, and no unresolved rework.
- Expected: `MILESTONE_EXTERNAL_PASS` is rejected when any mandatory assurance is red.
- Observed: `_validate_delivery_assurance` applies the strong checks only to `READY_FOR_REVIEW`; a mutated `MILESTONE_EXTERNAL_PASS` with `greenKeeper.status=FAIL` returned no error.
- Reproduction: invoke the validator helper on CP-0006 state/quality after changing only the terminal status and Green Keeper result.
- Evidence: `scripts/development-ledger/validate_checkpoint.py`; Red Team attacks R, S, V.
- Classification: `PRODUCT_DEFECT`, deterministic, not flaky or environmental.
- Acceptance: apply one shared promotion invariant to every positive status and add negative tests for each red assurance dimension.

### M0-F-002 — CRITICAL — external milestone PASS can be self-asserted on an intermediate Gate

- Requirement: only a milestone-closing Gate, or a validated extraordinary trigger, may receive external milestone PASS.
- Expected: `GATE 1`, `externalAuditRequired=false` is rejected as `MILESTONE_EXTERNAL_PASS`.
- Observed: syntactically filled second-tool metadata, `milestone.status=PASSED`, and matching status text were accepted; no external evidence, independent review PASS, Red Team PASS, auditor, or audit timestamp was required.
- Reproduction: isolated CP-0006 clone, commits `cc5c1da` and `4d9bef6`.
- Evidence: Red Team attacks Q, R, S; `scripts/development-ledger/validate_checkpoint.py`.
- Classification: `PRODUCT_DEFECT`, deterministic.
- Acceptance: enforce `requires_external_validation`, validate extraordinary triggers, require independent review and Red Team PASS, and resolve non-empty external evidence.

### M0-F-003 — CRITICAL — lesson preflight is not bound to the checkpoint Gate or canonical memory

- Requirement: preflight must be generated from the current active/applicable lessons for `STATE.gate`.
- Expected: a GATE 1 state cannot reuse SETUP-00 preflight; retiring a lesson invalidates stale active preflight.
- Observed: both mutations were accepted. State and artifact are compared to one another, but not to `STATE.gate` or a recomputation of canonical memory.
- Reproduction: Red Team attack U and direct GATE 1/SETUP-00 preflight mutation.
- Evidence: `scripts/development-ledger/validate_checkpoint.py`; `scripts/development-ledger/lesson_preflight.py`.
- Classification: `PRODUCT_DEFECT`, deterministic.
- Acceptance: bind Gate/scope to state and compare applicable lessons and derived requirement IDs with a fresh deterministic preflight.

### M0-F-004 — CRITICAL — Engineering Memory accepts forged controls, missing evidence, and nested secrets

- Requirement: `GUARDED` requires a real automated control; all evidence resolves; the complete lesson object is secret-scanned.
- Expected: nonexistent test reference, nonexistent evidence path, and a secret-shaped value in `prevention.description` are rejected.
- Observed: each independent in-memory mutation returned `errors=[]`.
- Reproduction: mutate one CP-0006 lesson at a time and call `validate_lessons`.
- Evidence: `scripts/development-ledger/lessons.py`; `AUDIT-EXECUTIONS.md`.
- Classification: `PRODUCT_DEFECT`, deterministic.
- Acceptance: recursively scan all fields, resolve evidence, resolve every preventive reference, and test all three negative cases.

### M0-F-005 — CRITICAL — Green Keeper has a vacuous PASS path

- Requirement: every mandatory gate must execute and be green; no gate may be skipped.
- Expected: an empty gate selection is rejected.
- Observed: `green_keeper.py --gates ""` exited zero and wrote `GREEN_KEEPER_GATE=PASS` with empty evidence and `commandsExecuted=[]`; the checkpoint validator accepted it, including alongside an actually failing test.
- Reproduction: isolated clone at commits `a636876` and `f707f24`.
- Evidence: Red Team attack V.
- Classification: `PRODUCT_DEFECT`, deterministic.
- Acceptance: use a closed mandatory gate set, reject empty/subset execution, require successful command evidence for every gate, and recompute the set in validation.

### M0-F-006 — CRITICAL — completeness denominator is not anchored

- Requirement: removal of a mandatory source requirement must fail completeness.
- Expected: deleting `REQ-0001` is detected even if all stored counts are recomputed.
- Observed: the matrix shrank from 47 to 46; completeness and checkpoint validation both passed at 100%.
- Reproduction: isolated Red Team commit `658819d`.
- Evidence: Red Team attack C.
- Classification: `PRODUCT_DEFECT`, deterministic.
- Acceptance: derive the required identifier set from a versioned canonical source and compare exact sets, not only the submitted denominator.

### M0-F-007 — CRITICAL — historical immutability is not anchored externally

- Requirement: sealed checkpoint directories and namespaced tags are immutable.
- Expected: moving a historical tag or rewriting a predecessor remains detectable after coordinated metadata/hash changes.
- Observed: moving tag and HEAD together validated; a CP-0005 rewrite declared in CP-0006 inventory, with refreshed hashes and moved tag, also validated.
- Reproduction: isolated commits `2adc1c5` and `23bce4d`.
- Evidence: Red Team attacks I and J.
- Classification: `PRODUCT_DEFECT`, deterministic.
- Acceptance: maintain immutable expected tag/object anchors or signed attestations outside mutable checkpoint content, and verify the full predecessor chain.

### M0-F-008 — HIGH — CP-0006 mandatory count is contradictory and accepted

- Requirement: matrix, completeness report, and state aggregates must agree.
- Expected: all three report 45 mandatory requirements.
- Observed: matrix/report compute 45 while CP-0006 `STATE.json` says 47; `CHECKPOINT_VALID` omits this comparison.
- Reproduction: count `mandatory:true` rows and compare the three artifacts.
- Evidence: CP-0006 `REQUIREMENTS-MATRIX.json`, `COMPLETENESS-REPORT.json`, `STATE.json`.
- Classification: `PRODUCT_DEFECT`, deterministic.
- Acceptance: correct the state in a new corrective checkpoint and cross-check `mandatory` in both state and report validation.

### M0-F-009 — HIGH — command records are not reproducible at their declared commits

- Requirement: command evidence must replay from its declared commit and working directory.
- Expected: sampled completed commands reproduce their recorded exit code at the recorded commit.
- Observed: CP-0006 `cmd-0012` points to an input absent at its commit and replay exits 2; CP-0005 `cmd-0028` replay at its commit exits 1. Both records were created with a dirty tree whose inputs are not content-bound.
- Reproduction: deterministic sample seed `20260920`; detached replay at each record's `commit`.
- Evidence: `AUDIT-EXECUTIONS.md`.
- Classification: `PRODUCT_DEFECT`, deterministic.
- Acceptance: bind dirty inputs by content hash or refuse evidence recording until committed; validate replay context, not only command syntax.

### M0-F-010 — HIGH — sealed finalization chronology is internally inconsistent

- Requirement: completion timestamps and final evidence must describe the sealed transition truthfully.
- Expected: run finish cannot precede its recorded finalizer; final validator evidence should bind the sealed commit/tag.
- Observed: CP-0006 `RUN-METADATA.finishedAt=16:18:07Z`, while finalizer `cmd-0019` is `16:18:10Z`; last evidence references pre-tag commit `1545416...` with a dirty tree, while the tag is `994bab4...`.
- Reproduction: compare CP-0006 run metadata, command ledger, state, and tag object.
- Evidence: CP-0006 `RUN-METADATA.json`, `COMMANDS.jsonl`, `STATE.json`.
- Classification: `PRODUCT_DEFECT`, deterministic.
- Acceptance: make sealing an atomic, monotonic, post-commit workflow and record post-tag validation at the tag commit.

### M0-F-011 — MEDIUM — one lesson source locator is inaccurate

- Requirement: every initial lesson must point to a source that actually supports its finding.
- Expected: LSN-0007 locates both cited findings accurately.
- Observed: it attributes `R4 / R7` to CP-0003; R7 is in CP-0004. The lesson is substantively supported, but the canonical locator is wrong.
- Reproduction: compare `.iacode/memory/lessons.jsonl` with CP-0003 and CP-0004 review reports.
- Evidence: CP-0004 `REVIEW-REPORT.md`.
- Classification: `PRODUCT_DEFECT`, deterministic.
- Acceptance: correct the canonical lesson provenance in a new corrective checkpoint without rewriting sealed history.

## Failure classification

All eleven findings are deterministic product defects. No environmental blocker and no flaky failure was observed. The canonical suite is green, but it does not cover these escaped invariants.

## Decision

`REWORK_REQUIRED`. Claude Code must create a new corrective SETUP-00 checkpoint. No product repair was made in this audit, and Gate 0 remains blocked.

