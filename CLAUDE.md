# Claude Code Project Instructions

This file is a Claude Code adapter for the same canonical contracts used by Codex. It adds no independent policy. Project subagents in `.claude/agents/` map one-to-one to the canonical role definitions in `.iacode/agents/`.

## Before any alteration

1. Read `START-HERE.md`.
2. Read `docs/DEVELOPMENT-CONTRACT.md`.
3. Read `docs/MASTER-PLAN.md`.
4. Read `docs/checkpoints/LATEST.md` and the complete checkpoint it identifies.
5. Run `python scripts/development-ledger/validate_checkpoint.py`.
6. Confirm `git status --short --branch`, `git branch --show-current`, and `git rev-parse HEAD` against `STATE.json`.
7. On unexpected divergence, stop, create `DIVERGENCE.md`, mark the run `BLOCKED`, and do not repair it silently.
8. Only then modify files within the authorized Gate.

## Language of the responses to the user

Every response Claude Code gives the user in this project is written in Brazilian Portuguese:
progress updates, questions, messages during execution, findings as they are presented to the user,
summaries, final reports and the textual handoff addressed to the user. Claude never switches the
user-facing response to another language on its own initiative; it changes language only when the
user explicitly asks for it.

The repository artifacts themselves stay in English, because they are the tool-neutral contract both
adapters read and because the tooling parses them. The rule governs what Claude says to the user, not
what the delivery writes to disk, and it never licenses translating a sealed checkpoint or any other
historical artifact.

Within a Portuguese response the following stay literal, because changing them would break them:
code, class names, file names, commands, paths, enumerations, canonical statuses, JSON and schema
fields, test names, APIs and identifiers.

## Mandatory working contract

- Follow `.iacode/agents/` as the canonical role specification.
- Require observable evidence for PASS; do not accept another agent's assertion as evidence.
- Do not use partial implementations, functional placeholders, production fakes, swallowed errors, disabled checks, or weakened tests.
- Record concise decisions and evidence, never private chain-of-thought or secrets.
- Create ADRs for structural decisions and maintain the Engineering Ledger.
- Default `trainingAllowed` to `false` without explicit rights evidence.
- Do not force push, hard reset, destructively clean, or rewrite history without explicit authorization and a preceding checkpoint.
- Do not mix or advance Gates without authorization.
- Close an implementing run at `READY_FOR_REVIEW`; never grant `GATE_PASS` to your own work. An independent run records `secondToolValidation` and decides the Gate.
- Declare every changed path in `FILES.json` before finalizing; the tooling binds the hashes but never invents a declaration.
- Follow the mandatory delivery order and skip no step: lesson preflight, requirement derivation, baseline, plan, implementation, test and quality, Green Keeper, Delivery Completeness Validator, internal Red Team, Milestone Closure Auditor, `READY_FOR_REVIEW`, independent review, Red Team, `GATE_PASS`.
- Derive the requirement set with `python scripts/development-ledger/derive_requirements.py --write`; the canonical checklist, the lesson preflight and the open audit findings decide it, never the delivery.
- Never narrow a mandatory gate set, a denominator or a promotion rule by an argument; those come from policy.
- Never record an internal verdict as independent validation. A milestone verdict is derived from an audit attestation that a later audit checkpoint wrote about a sealed subject; the subject is never rewritten to become approved. `MILESTONE_INDEPENDENT_AUDIT_PASS` records a fresh-session audit and `MILESTONE_EXTERNAL_PASS` a cross-tool one, and neither mechanism may take the other's status.
- Seal with `python scripts/development-ledger/seal_checkpoint.py` so the final validation describes the committed content, and anchor every sealed predecessor in `.iacode/anchors/checkpoint-chain.json`.
- Extract every requirement into `REQUIREMENTS-MATRIX.json` before implementing. A requirement that exists only in the session is not a requirement.
- Run `python scripts/development-ledger/green_keeper.py` until every mandatory gate is green; never delete, skip, or weaken a check to get there. A real external blocker yields `BLOCKED`, never `READY_FOR_REVIEW`.
- Run `python scripts/development-ledger/check_completeness.py --write` before handoff and repair every gap it reports.
- Record every command with `python scripts/development-ledger/record_command.py` so the ledger stays reproducible, and never claim readiness while `blockedBy` is non-empty.

## Subagent roles for delivery assurance

`.claude/agents/test-rework-greenkeeper.md` may change code to repair a failing gate.
`.claude/agents/delivery-completeness-validator.md` audits only and must never implement or silently correct.
Keep the two roles and their artifacts separate even when they run in the same session, and do not describe an emulated separation as independence.

## Before ending work

Update/finalize the checkpoint, validate it, record Git state, update `LATEST.md`, and provide exact handoff and next-action instructions.

Claude Code `2.1.195` was detected at `C:/Users/cesar/.local/bin/claude.exe` during the SETUP-00 correction checkpoint. That directory was not on the detecting process's `PATH`, which caused the earlier false negative. The project adapters use the verified `.claude/agents/*.md` format. No Claude-specific hook or MCP dependency is required by SETUP-00.

## Engineering memory and validation cadence

- Run `python scripts/development-ledger/lesson_preflight.py --gate <gate> --scope <scope> --write` before the Gate starts, and carry every derived `LESSON-REQ-` requirement into the matrix.
- Turn a confirmed failure into a lesson, and an important lesson into an automated guardrail. A lesson is `GUARDED` only when a test, validator, lint rule, policy, schema, invariant or automated check prevents recurrence; documentation alone is never enough.
- Treat a repeat of a guarded failure class as a `GUARDRAIL_FAILURE` and investigate the control, not only the defect.
- The memory in `.iacode/memory/` belongs to the project, not to the user. Never store personal preferences, chain-of-thought or secrets there.
- Close an intermediate Gate at `INTERNAL_GATE_PASS`. External independent validation is due once per milestone and produces `MILESTONE_EXTERNAL_PASS`; never describe an internal verdict as an external one. Requesting an early audit requires `externalAuditRequired` with a recorded trigger.
- Produce the Gate retrospective from `.iacode/templates/retrospective/TEMPLATE.md`.
