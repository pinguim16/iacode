# Handoff

Current Gate: SETUP-00
Current Status: GATE_PASS

Last valid commit: 0cb4f246b555a6304ca6dbce1c8e97c80b527ef9
Current branch: main

## Objective

Correct the Claude Code installation record and add verified Claude Code adapters without altering the sealed prior checkpoint or advancing the project Gate.

## What was completed

- Located Claude Code `2.1.195` at `C:/Users/cesar/.local/bin/claude.exe` and documented the PATH cause of the earlier false negative.
- Verified local CLI support for agents, hooks, MCP, permissions, settings, and effort controls.
- Added ten `.claude/agents/*.md` adapters mapped one-to-one to `.iacode/agents/`.
- Added and executed adapter parity/frontmatter/canonical-delegation tests as part of the 37-test suite.
- Attempted a non-interactive cold start from a clean clone; the executable ran but stopped because no Claude account is authenticated.
- Captured the exact second cold-start invocation, zero-token/model-use result, and unchanged clone status in `CLAUDE-COLD-START.md`.
- Received independent `APPROVED` review and `RED_TEAM_PASS` after remediating the initial ledger findings.
- Preserved `SETUP-00-CP-0001` and its immutable tag unchanged.

## What was NOT completed

Genuine Claude model execution and cross-provider resume validation. Authentication is machine/user state and was not changed. Gate 0 remains unimplemented and unauthorized.

## Current repository state

Branch `main`; base commit `0cb4f246b555a6304ca6dbce1c8e97c80b527ef9`. The final correction commit and checkpoint tag are recorded by `STATE.json` after finalization.

## Files changed

See `FILES.json`; current canonical docs, adapter tests, ten Claude agent adapters, and this correction checkpoint changed.

## Important decisions

The sealed prior checkpoint is historical; PATH lookup failure is not absence; provider-neutral role contracts remain canonical; second-tool validation stays blocked on authentication.

## Tests executed

`python -m unittest discover -s tests` — 37 passed, 0 failed. Independent review returned `APPROVED`; the final Red Team rerun returned `RED_TEAM_PASS`; checkpoint validation returned `CHECKPOINT_VALID`.

## Known failures

The Claude cold-start process exited before a model call with `Not logged in`. This is an expected external authentication blocker, not a repository test failure.

## Known risks

See `RISKS.md`, especially PATH resolution, multiple installed versions, and pending authenticated cross-tool validation.

## Do not repeat

Do not repeat PATH-only installation detection. Do not edit `SETUP-00-CP-0001`, invent Claude execution metadata, or describe the authentication-blocked run as cross-tool PASS.

## Required next action

Await explicit Gate 0 authorization, or authenticate Claude Code outside repository scope and create a new checkpoint for genuine second-tool validation.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`, `docs/checkpoints/LATEST.md`, and this complete checkpoint.
2. Run the checkpoint validator and compare Git state to `STATE.json`.
3. For optional Claude validation, confirm `& 'C:/Users/cesar/.local/bin/claude.exe' auth status` reports an authenticated account.
4. Clone the sealed repository into a new temporary directory and run Claude non-interactively with repository-only context.
5. Record results in a new checkpoint; never mutate this sealed checkpoint.

## Validation commands

- `python scripts/development-ledger/validate_checkpoint.py`
- `python -m unittest discover -s tests`
- `& 'C:/Users/cesar/.local/bin/claude.exe' --version`
- `& 'C:/Users/cesar/.local/bin/claude.exe' auth status`

## Stop conditions

Stop on divergence, failed validation, unauthenticated Claude status, unexpected writes in a validation clone, secret exposure, or missing authorization for the next Gate.
