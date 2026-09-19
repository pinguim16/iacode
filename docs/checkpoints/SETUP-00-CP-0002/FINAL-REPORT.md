# SETUP-00 Correction Final Report

## Status

`GATE_PASS`

The user's correction was confirmed: Claude Code is installed. The earlier bare-command failure was caused by PATH resolution, not absence of the executable.

## Environment

Windows NT `10.0.26200.0`; Python `3.13.15`; Git `2.52.0.windows.1`; branch `main`; base checkpoint commit `0cb4f246b555a6304ca6dbce1c8e97c80b527ef9`.

Claude Code `2.1.195` is at `C:/Users/cesar/.local/bin/claude.exe`; version `2.1.187` is also bundled at `C:/Users/cesar/AppData/Local/Claude-3p/claude-code/2.1.187/claude.exe`. The current process PATH does not resolve bare `claude`.

## Tool / Model / Effort

The correction was performed with Codex Desktop and `codex-cli 0.155.0-alpha.9`, provider OpenAI, GPT-5 family as system-reported. Exact Codex model identifier, desktop host version, and active effort were not exposed and were not invented.

Claude was invoked with `--effort xhigh`, but authentication stopped execution before a model call. No Claude model or provider execution metadata is claimed.

## Deliverables

Ten verified `.claude/agents/*.md` adapters, corrected Claude capability/instruction/architecture documentation, updated ADR evidence, three adapter contract tests, exact sanitized cold-start evidence, independent review, Red Team remediation and PASS evidence, and this reconstructible correction checkpoint.

## Files Created

The ten Claude project-agent adapters and all `SETUP-00-CP-0002` ledger artifacts are listed in `FILES.json` relative to the CP-0001 base.

## Files Modified

`CLAUDE.md`, `docs/ARCHITECTURE.md`, `docs/TOOL-CAPABILITIES.md`, `docs/adr/ADR-0003-tool-neutral-agents.md`, `docs/checkpoints/LATEST.md`, and `tests/test_development_ledger.py` were modified. The sealed CP-0001 checkpoint was not modified.

## Validation

The checkpoint validator returned `CHECKPOINT_VALID`; Git whitespace checks passed; the file manifest exactly matched every path changed from the base with no missing or extra entry.

## Tests

`python -m unittest discover -s tests` passed 37 of 37 tests: the existing 34 ledger tests plus three Claude adapter parity, frontmatter, and canonical-delegation tests.

## Red Team

`RED_TEAM_PASS`. The initial review identified incomplete file inventory, premature finish time, and insufficient cold-start command evidence. All three were corrected and independently rechecked; no unresolved inconsistency or sensitive-value exposure remained.

## Known Risks

Genuine Claude resume validation remains pending because the installation is unauthenticated. The detecting process still cannot resolve bare `claude`, two installed versions exist, adapter formats can evolve, and no runtime capability exists beyond SETUP-00.

## Remaining Work

Optionally authenticate Claude Code outside repository scope and perform the procedure in `RESUME-VALIDATION.md`, recording it in a new checkpoint. Runtime work may begin only in a separately authorized Gate 0.

## Handoff Readiness

Repository controls, tests, documentation, independent review, Red Team review, and immutable checkpoint closure are complete. The authentication-blocked Claude run is explicitly excluded from PASS evidence.

## Next Gate

`GATE 0 — FOUNDATION`

It is permitted only after explicit user authorization and a new pre-Gate checkpoint. Gate 0 was not implemented by this correction.

## Evidence

- `TESTS.json`, `QUALITY.json`, `PROVENANCE.json`, `FILES.json`, and `COMMANDS.jsonl`.
- `CLAUDE-COLD-START.md`, `REVIEW-REPORT.md`, `RED-TEAM-REPORT.md`, and `RESUME-VALIDATION.md`.
- `python scripts/development-ledger/validate_checkpoint.py`.
- `python -m unittest discover -s tests`.
- Final reference: `refs/tags/iacode-checkpoints/SETUP-00-CP-0002` (resolve with `git rev-parse`).
