# SETUP-00 Engineering Memory Final Report

## Status

`READY_FOR_REVIEW`

This run adds a permanent engineering memory, a mandatory lesson preflight, and a milestone
validation cadence. It grants no Gate verdict. `SETUP-00` stays open until the Codex `M0` milestone
audit covering `SETUP-00-CP-0005`, this checkpoint, and SETUP-00 as a whole.

## Environment

Windows NT `10.0.26200.0`; Python `3.13.15`; Git `2.52.0.windows.1`; branch `main`; base commit
`276645b4498a0e58a1bf38979b5e078669dbb380`, which is
`refs/tags/iacode-checkpoints/SETUP-00-CP-0005`. No remote is configured. Checkpoint schema version
`3.1.0`.

## Tool / Model / Effort

Claude Code desktop application, Code tab, provider Anthropic, model `claude-opus-5`. The detected
Claude Code executable reports `2.1.195`; the desktop host version is not exposed to the session.
`XHIGH` effort was requested by the operator; the active effort value is not exposed to the session
and was not invented.

## Deliverables

The engineering memory with fourteen evidence-backed lessons; the lesson schema, preflight schema,
library, validator, extractor and preflight tools; lesson-derived requirements enforced by the
completeness audit; lesson validation inside the Green Keeper gate set; the milestone validation
policy with the `M0` to `M6` grouping, the two verdict statuses and the extraordinary-audit trigger;
checkpoint `schemaVersion` `3.1.0`; the retrospective template and this Gate's retrospective;
ADR-0009; updated agent contracts and governing documents; and this checkpoint.

## Files Created

`.iacode/memory/` in full, `.iacode/schemas/lesson.schema.json`,
`.iacode/schemas/lesson-preflight.schema.json`, `.iacode/templates/retrospective/TEMPLATE.md`,
`scripts/development-ledger/lessons.py`, `validate_lessons.py`, `lesson_preflight.py`,
`extract_lessons.py`, `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`,
`docs/adr/ADR-0009-engineering-memory-and-milestone-validation.md`, and every artifact of
`docs/checkpoints/SETUP-00-CP-0006/`. `FILES.json` lists each path with its reason and hash.

## Files Modified

`scripts/development-ledger/ledger_common.py`, `validate_checkpoint.py`, `new_checkpoint.py`,
`green_keeper.py`, `delivery_assurance.py` and `README.md`; five schemas;
`tests/test_development_ledger.py`; seven canonical agent contracts; `START-HERE.md`, `AGENTS.md`,
`CLAUDE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`, `docs/ROADMAP.md`,
`docs/QUALITY-GATES.md`, `docs/DEFINITION-OF-DONE.md`, `docs/CHECKPOINT-PROTOCOL.md`,
`docs/HANDOFF-PROTOCOL.md`, `docs/SETUP-00-CHECKLIST.md`, and `docs/checkpoints/LATEST.md`. No sealed
checkpoint was touched.

## Validation

`python scripts/development-ledger/validate_checkpoint.py` returned `CHECKPOINT_VALID`, and
`validate_lessons.py` returned `LESSONS_VALID`. Finalization re-validated the checkpoint before and
after recording its own success. The corrected validator was also run against clean clones detached
at `SETUP-00-CP-0001` through `CP-0005`, returning `CHECKPOINT_VALID` for each, so four coexisting
schema rule sets did not invalidate sealed history.

## Tests

`python -m unittest discover -s tests` passed 181 of 181, up from 131.
`python -m compileall -q scripts tests` returned 0. New coverage: six memory structure cases, eleven
lesson validation cases, four recurrence cases, seven preflight cases, two derived-requirement
completeness cases, six milestone policy cases, eleven memory policy validation cases, and two
verdict vocabulary cases, plus one additional historical compatibility case for
the fifth sealed tag.

## Red Team

`NOT_EXECUTED` as a Gate dimension. The independent Red Team belongs to the Codex `M0` audit and has
not run. The controls introduced here are covered by regressions that behave as attacks: a
documentation-only guardrail claim, a dropped lesson-derived requirement, an internal verdict
carrying an external one, and an extraordinary audit without a trigger are all refused.

## Known Risks

See `RISKS.md`. The principal ones: the `M0` audit is pending; a milestone cadence can delay
discovery of a systemic defect; two lessons cannot be guarded from this repository; the derived
requirement mechanism proves declaration and evidence, not that the evidence addresses the lesson;
and the separation between the Green Keeper and the Completeness Validator remains emulated.

## Remaining Work

The Codex `M0` independent milestone audit, then a milestone checkpoint recording
`secondToolValidation` and `milestone.status`.

## Handoff Readiness

`HANDOFF.md` carries the commit, branch, tag, schema version, the `M0` scope, per-control
verification recipes, exact reproduction commands, PASS criteria and REWORK criteria, and is
executable without this session. `NEXT.md` requests one audit, not two.

## Next Gate

`GATE 0 — FOUNDATION` remains blocked. It requires the `M0` milestone audit to pass, plus explicit
authorization and a new pre-Gate checkpoint whose first action is the lesson preflight. No Gate 0
work exists in this change set.

## Evidence

- `REQUIREMENTS-MATRIX.json`, `LESSON-PREFLIGHT.json`, `COMPLETENESS-REPORT.json`,
  `REWORK-LOG.jsonl`, `TESTS.json`, `QUALITY.json`, `PROVENANCE.json`, `FILES.json`, and
  `COMMANDS.jsonl`.
- `.iacode/memory/lessons.jsonl` and `.iacode/memory/retrospectives/SETUP-00-CP-0006.md`.
- `docs/adr/ADR-0009-engineering-memory-and-milestone-validation.md`.
- `python scripts/development-ledger/validate_checkpoint.py`,
  `python scripts/development-ledger/validate_lessons.py`,
  `python scripts/development-ledger/check_completeness.py`, and
  `python -m unittest discover -s tests`.
- Final reference: `refs/tags/iacode-checkpoints/SETUP-00-CP-0006`, resolvable with `git rev-parse`.
