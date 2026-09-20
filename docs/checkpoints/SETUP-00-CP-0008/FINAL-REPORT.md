# SETUP-00 Final Closure Report

## Status

`READY_FOR_REVIEW`

This run corrects every finding of the independent `M0` audit recorded in `SETUP-00-CP-0007`. It grants no Gate verdict and carries no external attestation. `SETUP-00` stays open until the final Codex `M0` independent audit, and `GATE 0` stays blocked.

## Environment

Windows NT `10.0.26200`; Python `3.13.15`; Git `2.52.0.windows.1`; branch `main`; base commit `502c554575f717c1d57290e4f4aafa575e41170e`, which is `refs/tags/iacode-checkpoints/SETUP-00-CP-0007`. No remote is configured. Checkpoint schema version `3.2.0`.

## Tool / Model / Effort

Claude Code desktop application, Code tab, provider Anthropic, model `claude-opus-5`. The detected Claude Code executable reports `2.1.195`; the desktop host version is not exposed to the session. The active effort value is not exposed to the session and was not invented.

## Deliverables

The canonical policy sources; the derivation library; the integrity anchor chain and its verifier; the external audit attestation mechanism; the requirement derivation, count derivation, sealing, internal Red Team and internal mirror audit tools; the shared promotion invariant; the closed mandatory gate set; resolved lesson claims and a guardrail registry with measured effectiveness; preflight fingerprints; input-bound command records; ADR-0010; the extended canonical checklist; the Milestone Closure Auditor role and its adapter; and this checkpoint.

## Files Created

`.iacode/policies/quality-gates.json`, `canonical-requirements.json`, `audit-registry.json`; `.iacode/anchors/checkpoint-chain.json`; `.iacode/attestations/README.md`; `.iacode/memory/POLICY.json` and `guardrails/registry.json`; `.iacode/agents/m0-closure-auditor.md` and its Claude Code adapter; ten schemas; `scripts/development-ledger/policies.py`, `anchors.py`, `attestation.py`, `derive_requirements.py`, `derive_counts.py`, `verify_integrity.py`, `seal_checkpoint.py`, `m0_red_team.py`, `m0_mirror_audit.py`; `docs/adr/ADR-0010-milestone-closure-controls.md`; and every artifact of `docs/checkpoints/SETUP-00-CP-0008/`. `FILES.json` lists each path with its reason and hash.

## Files Modified

`scripts/development-ledger/validate_checkpoint.py`, `ledger_common.py`, `lessons.py`, `delivery_assurance.py`, `green_keeper.py`, `check_completeness.py`, `finalize_checkpoint.py`, `new_checkpoint.py`, `record_command.py`, `lesson_preflight.py` and `README.md`; nine schemas; `tests/test_development_ledger.py`; `.iacode/memory/lessons.jsonl` and `LESSONS.md`; `docs/SETUP-00-CHECKLIST.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/QUALITY-GATES.md`, `docs/MILESTONE-VALIDATION.md`, `docs/ENGINEERING-MEMORY.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/DEFINITION-OF-DONE.md`, `docs/HANDOFF-PROTOCOL.md`, `START-HERE.md`, `AGENTS.md`, `CLAUDE.md` and `docs/checkpoints/LATEST.md`. No sealed checkpoint was touched and no historical tag was moved.

## Validation

Canonical SETUP requirements: `131/131 REQUIREMENTS` complete, coverage `100.00`, evidence coverage `100.00`, over an expected set of `131` derived from the canonical sources rather than declared by this delivery.

`CP-0007` findings: `11/11 FINDINGS` closed, each with a root cause, an implementation, a regression test, a negative test and a verification command.

Engineering memory: `LESSONS_VALID`, `22/23 LESSONS` guarded, `22/22 GUARDRAILS` effective, `0` unresolved guardrail failures.

Checkpoint integrity: `7` sealed checkpoints anchored and verified.

`python scripts/development-ledger/validate_checkpoint.py` returned `CHECKPOINT_VALID`, and the corrected tooling was run against clean clones detached at every sealed tag, returning `CHECKPOINT_VALID` for each, so five coexisting schema rule sets did not invalidate sealed history.

## Tests

`python -m unittest discover -s tests` passed `306/306 TESTS`: `224` unit cases and `82` integration cases. `python -m compileall -q scripts tests` returned 0. New coverage includes a regression and a negative test for every finding, a test for every escaped attack, and an end-to-end rehearsal of the sealing workflow.

## Red Team

The independent Red Team is `NOT_EXECUTED` as a Gate dimension; it belongs to the Codex `M0` audit. This delivery executed its own battery against a disposable clone: `46/46 ATTACKS` defended, of which `26/26` are the mandatory A-Z attacks of the sealed `CP-0007` report, re-parsed from that report rather than transcribed. The result is internal quality assurance and is not recorded as an independent verdict.
The internal mirror audit reproduced the milestone dimensions and reported `PASS` over `18/18` checks. It is internal quality assurance, declared as such in its own `independence` field, and the validator refuses any attempt to record it as an external verdict.


## Known Risks

See `RISKS.md`. The principal ones: the final `M0` audit is pending; the integrity anchors and the external attestation are tamper-evident within the local trust model rather than cryptographic; a checkpoint cannot anchor its own tag, so this one is anchored by its successor; the internal Red Team and the mirror audit are not independent validation; and the attack battery attacks a faithful model of the sealed state rather than the seal itself.

## Remaining Work

The final Codex `M0` independent audit, then an external audit attestation and a milestone checkpoint recording `secondToolValidation` and `milestone.status`.

## Handoff Readiness

`HANDOFF.md` carries the commit, branch, tag, schema version, the scope of the audit, a verification recipe per control, exact reproduction commands, PASS criteria and `REWORK_REQUIRED` criteria, and is executable without this session. `NEXT.md` requests one audit.

## Next Gate

`GATE 0 — FOUNDATION` remains blocked. It requires the `M0` milestone audit to pass, plus explicit authorization and a new pre-Gate checkpoint whose first action is the lesson preflight. No Gate 0 work exists in this change set.

## Evidence

- `CLOSURE-REQUIREMENTS.json`, `REQUIREMENTS-MATRIX.json`, `COMPLETENESS-REPORT.json`, `CP7-FINDINGS-CLOSURE.json`, `M0-INTERNAL-RED-TEAM.json`, `M0-INTERNAL-MIRROR.json`, `COUNTS.json`, `LESSON-PREFLIGHT.json`, `REWORK-LOG.jsonl`, `TESTS.json`, `QUALITY.json`, `PROVENANCE.json`, `FILES.json` and `COMMANDS.jsonl`.
- `.iacode/anchors/checkpoint-chain.json`, `.iacode/memory/guardrails/registry.json` and `.iacode/memory/lessons.jsonl`.
- `docs/adr/ADR-0010-milestone-closure-controls.md`.
- The mandatory gate set actually executed: `tests, staticAnalysis, lessons, integrity, checkpointValidation`, recorded in `REWORK-LOG.jsonl` across `11` cycle(s).
- Final reference: `refs/tags/iacode-checkpoints/SETUP-00-CP-0008`, resolvable with `git rev-parse`.
