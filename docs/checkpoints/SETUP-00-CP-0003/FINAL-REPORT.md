# SETUP-00 Corrective Run Final Report

## Status

`READY_FOR_REVIEW`

This run corrected six defects found in the sealed `SETUP-00-CP-0002`. It does not grant a Gate
verdict. `SETUP-00` stays open until an independent Codex run performs the review and Red Team and
records `secondToolValidation`.

## Environment

Windows NT `10.0.26200.0`; Python `3.13.15`; Git `2.52.0.windows.1`; branch `main`; base commit
`ae563f860856e3ce5ca9ec6e94b6202ed7e4a4e4`, which is `refs/tags/iacode-checkpoints/SETUP-00-CP-0002`.
No remote is configured. Checkpoint schema version `2.0.0`.

## Tool / Model / Effort

Claude Code desktop application, Code tab, provider Anthropic, model `claude-opus-5`. The detected
Claude Code executable reports `2.1.195`; the desktop host version is not exposed to the session.
`XHIGH` effort was requested by the operator; the active effort value is not exposed to the session
and was not invented. The separate CLI installation at `C:/Users/cesar/.local/bin/claude.exe` reported
`loggedIn: false` again on 2026-09-20 and was not used to execute this work.

## Deliverables

Version-dispatched checkpoint validation with `schemaVersion` `2.0.0`; detached-`HEAD` binding;
Git-derived file inventory with content hashes; recorded finalization; structured cross-tool
validation state; evidence-referenced quality results; the in-repository `docs/SETUP-00-CHECKLIST.md`;
two ADRs; updated protocol documents and tool adapters; a suite grown from 37 to 75 tests; a
reproducible adversarial battery; and this checkpoint.

## Files Created

`docs/SETUP-00-CHECKLIST.md`, `docs/adr/ADR-0006-checkpoint-inventory-binding.md`,
`docs/adr/ADR-0007-checkpoint-schema-2-and-independent-promotion.md`, and every artifact of
`docs/checkpoints/SETUP-00-CP-0003/`. `FILES.json` lists each path with its reason and content hash.

## Files Modified

The three ledger scripts plus `new_checkpoint.py` and the tooling README; the checkpoint, quality,
command, test-result, and provenance schemas; `tests/test_development_ledger.py`; `START-HERE.md`,
`AGENTS.md`, `CLAUDE.md`, `docs/MASTER-PLAN.md`, `docs/CHECKPOINT-PROTOCOL.md`,
`docs/QUALITY-GATES.md`, `docs/HANDOFF-PROTOCOL.md`, `docs/DEFINITION-OF-DONE.md`,
`docs/TOOL-CAPABILITIES.md`, and `docs/checkpoints/LATEST.md`. Neither sealed checkpoint was touched.

## Validation

`python scripts/development-ledger/validate_checkpoint.py` returned `CHECKPOINT_VALID`. Finalization
re-validated the checkpoint before and after recording its own success. The corrected validator was
also run against clean clones detached at `SETUP-00-CP-0001` and `SETUP-00-CP-0002`, returning
`CHECKPOINT_VALID` for both, so the schema change did not invalidate sealed history.

## Tests

`python -m unittest discover -s tests` passed 75 of 75: 53 unit cases and 22 isolated Git and
subprocess cases. `python -m compileall -q scripts tests` returned 0. Per finding: R1 adds six
detached and attached binding cases, R2 adds eight inventory cases, R3 adds two finalization ledger
cases, R4 adds nine cross-tool validation state cases, R5 adds two checklist and documentation link
cases, and R6 adds nine quality evidence cases. Two historical compatibility cases cover the sealed
checkpoints.

## Red Team

`NOT_EXECUTED` as a Gate dimension. The independent Red Team belongs to Codex and has not run. This
run recorded a non-independent development battery in `RED-TEAM-DEV-REPORT.md`: 17 attacks, all
detected, including the three that previously returned `CHECKPOINT_VALID` against
`SETUP-00-CP-0002` — a removed inventory entry, a silently altered tracked file, and a deleted
adapter. Five supported modes were confirmed to stay valid. The battery also caught a defect in this
run's own work, recorded rather than hidden.

## Known Risks

See `RISKS.md`. The principal ones: cross-tool validation is still `PENDING_MANUAL`; `NOT_REQUIRED`
remains an escape hatch constrained only by a justification; the inventory depends on tag immutability;
and the secret detector's documented scope was deliberately left unchanged.

## Remaining Work

Independent Codex review and Red Team, then a new checkpoint recording `secondToolValidation` and the
Gate verdict. Optionally, authenticate the Claude Code CLI outside repository scope to complete the
clean-clone CLI cold start that `SETUP-00-CP-0002` left blocked.

## Handoff Readiness

`HANDOFF.md` carries the commit, branch, tag, schema version, per-finding summary, exact reproduction
commands, PASS criteria, and REWORK criteria, and is executable without this session. `NEXT.md` points
at independent validation, not at Gate 0.

## Next Gate

`GATE 0 — FOUNDATION` remains blocked. It requires `SETUP-00` to reach `GATE_PASS` through an
independent run, plus explicit authorization and a new pre-Gate checkpoint. No Gate 0 work exists in
this change set.

## Evidence

- `TESTS.json`, `QUALITY.json`, `PROVENANCE.json`, `FILES.json`, and `COMMANDS.jsonl`.
- `SELF-REVIEW.md`, `RED-TEAM-DEV-REPORT.md`, and `RESUME-VALIDATION.md`, all explicitly
  non-independent.
- `docs/adr/ADR-0006-checkpoint-inventory-binding.md` and
  `docs/adr/ADR-0007-checkpoint-schema-2-and-independent-promotion.md`.
- `python scripts/development-ledger/validate_checkpoint.py` and `python -m unittest discover -s tests`.
- Final reference: `refs/tags/iacode-checkpoints/SETUP-00-CP-0003`, resolvable with `git rev-parse`.
