# Codex Project Instructions

This file is a Codex adapter for the canonical contracts in `.iacode/`. Repository documentation overrides session memory.

## Before any alteration

1. Read `START-HERE.md`.
2. Read `docs/DEVELOPMENT-CONTRACT.md`.
3. Read `docs/MASTER-PLAN.md`.
4. Read `docs/checkpoints/LATEST.md` and the complete checkpoint it identifies.
5. Run `python scripts/development-ledger/validate_checkpoint.py`.
6. Confirm `git status --short --branch`, `git branch --show-current`, and `git rev-parse HEAD` against `STATE.json`.
7. If the state diverges unexpectedly, stop, create `DIVERGENCE.md`, mark the run `BLOCKED`, and do not reconcile silently.
8. Only then modify files, and only within the current authorized Gate.

## Mandatory working contract

- Use the canonical role definitions in `.iacode/agents/`; tool-specific behavior must remain semantically equivalent.
- Never claim a check passed without observable evidence.
- Do not use stubs, production fakes, silent exception handling, disabled checks, or altered tests to conceal incomplete work.
- Do not record private chain-of-thought or secrets. Record concise decisions, evidence, alternatives, and consequences.
- Create ADRs for structural decisions.
- Keep the Engineering Ledger current and classify reusable artifacts using the provenance policy.
- `trainingAllowed` is `false` unless explicit rights evidence proves otherwise.
- Do not use force push, hard reset, destructive clean, or history rewriting without explicit authorization and a preceding checkpoint.
- Never mix Gates in one commit and never advance a Gate without explicit authorization.
- Close an implementing run at `READY_FOR_REVIEW`; `GATE_PASS` is granted only by a later run independent of the one that implemented the Gate, which records `secondToolValidation` in `STATE.json`.
- Declare every changed path in `FILES.json` before finalizing; `finalize_checkpoint.py` binds the hashes but never invents a declaration.
- Follow the mandatory delivery order and skip no step: requirement extraction, baseline, plan, implementation, test and quality, Green Keeper, Delivery Completeness Validator, `READY_FOR_REVIEW`, independent review, Red Team, `GATE_PASS`.
- Extract every requirement into `REQUIREMENTS-MATRIX.json` before implementing, and keep its status truthful.
- Run `python scripts/development-ledger/green_keeper.py` until every mandatory gate is green, and `python scripts/development-ledger/check_completeness.py --write` before any handoff.
- Record commands with `python scripts/development-ledger/record_command.py`; a recorded command must be executable from its declared working directory.
- Never claim `READY_FOR_REVIEW` while `blockedBy` is non-empty; a real external blocker yields `BLOCKED` with the blocker named.

## Delivery assurance roles

Codex loads the canonical role contracts directly from `.iacode/agents/`: `test-rework-greenkeeper.md`
may change code to repair a failing gate, and `delivery-completeness-validator.md` audits only and may
not implement or silently correct. Codex has no per-agent project file mechanism in this repository,
so these roles are adopted through this adapter and the canonical contracts rather than through a
subagent definition file. Keep their artifacts separate and do not describe the separation as
independence when a single session performs both.

## Before ending work

1. Update or create the current checkpoint, including commands, files, tests, quality, risks, provenance, handoff, and next action.
2. Run `python scripts/development-ledger/validate_checkpoint.py`.
3. Record the final Git state truthfully.
4. Ensure `docs/checkpoints/LATEST.md` names the last valid checkpoint.


## Engineering memory and validation cadence

- Run the lesson preflight before the Gate starts and carry every derived `LESSON-REQ-` requirement into `REQUIREMENTS-MATRIX.json`.
- A confirmed failure becomes a lesson in `.iacode/memory/`, and an important lesson becomes an automated guardrail. Documentation alone never justifies `GUARDED`.
- A repeat of a guarded failure class is a `GUARDRAIL_FAILURE`; escalate it rather than repairing it quietly.
- The memory is the project's, not the user's. No personal data, no chain-of-thought, no secrets.
- As the milestone independent auditor, evaluate the milestone as a whole: accumulated completeness, integration between Gates, architecture, regressions, quality, documentation, lessons and guardrails, Red Team, and the inconsistencies that per-Gate validation cannot see. Findings return to the implementer; do not implement corrections.
- `INTERNAL_GATE_PASS` is the project's own verdict; only `MILESTONE_EXTERNAL_PASS` records an independent one.
