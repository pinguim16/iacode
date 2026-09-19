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

## Mandatory working contract

- Follow `.iacode/agents/` as the canonical role specification.
- Require observable evidence for PASS; do not accept another agent's assertion as evidence.
- Do not use partial implementations, functional placeholders, production fakes, swallowed errors, disabled checks, or weakened tests.
- Record concise decisions and evidence, never private chain-of-thought or secrets.
- Create ADRs for structural decisions and maintain the Engineering Ledger.
- Default `trainingAllowed` to `false` without explicit rights evidence.
- Do not force push, hard reset, destructively clean, or rewrite history without explicit authorization and a preceding checkpoint.
- Do not mix or advance Gates without authorization.

## Before ending work

Update/finalize the checkpoint, validate it, record Git state, update `LATEST.md`, and provide exact handoff and next-action instructions.

Claude Code `2.1.195` was detected at `C:/Users/cesar/.local/bin/claude.exe` during the SETUP-00 correction checkpoint. That directory was not on the detecting process's `PATH`, which caused the earlier false negative. The project adapters use the verified `.claude/agents/*.md` format. No Claude-specific hook or MCP dependency is required by SETUP-00.
