# SETUP-00 Final Report

## Status

`GATE_PASS`

## Environment

Windows 11 Pro 64-bit 10.0.26200; Python 3.13.15; Git 2.52.0.windows.1; branch `main`; baseline `EMPTY_PROJECT`.

## Tool / Model / Effort

Codex Desktop with `codex-cli 0.155.0-alpha.9`, OpenAI, GPT-5 family as system-reported. Exact model identifier, desktop host version, and active effort were not exposed and were not invented. Claude Code was not installed.

## Deliverables

Canonical agents, eight schemas, templates, policies, adapters, architecture and Gate documentation, five ADRs, continuation/review/Red Team prompts, Development Ledger scripts, secret redaction, 34 automated tests, cold-start evidence, provenance, handoff, and a reconstructible checkpoint.

## Files Created

All tracked files listed in `FILES.json` were created from the empty baseline. The manifest covers hidden canonical files and uses portable LF-normalized SHA-256 hashes; the manifest's own hash is intentionally omitted as self-referential.

## Files Modified

No file existed at baseline. Review-driven corrections are preserved in Git history and described by `REVIEW-REPORT.md` and `RED-TEAM-REPORT.md`.

## Validation

The checkpoint validator passed on clean, tag-anchored candidates. All eight schemas load; required files, cross-file invariants, Git state, tags, hashes, status, metadata, provenance, quality, handoff, next action, decoded content, and repository-wide secret patterns are checked.

## Tests

`python -m unittest discover -s tests -v` passed 34/34: 29 unit and adversarial validator/redactor cases plus 5 isolated lifecycle/integration cases. `compileall` and Git whitespace checks passed.

## Red Team

`RED_TEAM_PASS`. Three adversarial rounds found and drove correction of false PASS paths; the final round and independent review left no unresolved finding. Destructive cases used temporary repositories.

## Known Risks

Genuine second-tool/provider resume validation is `PENDING_MANUAL`; schema keyword support is intentionally bounded; secret patterns require maintenance; adapters can drift; and no runtime capability exists.

## Remaining Work

Optionally perform the exact manual Claude Code procedure in `RESUME-VALIDATION.md`. Runtime work begins only in a separately authorized Gate 0.

## Handoff Readiness

Repository-only cold start succeeded with Codex, the complete handoff is present, all automated controls pass, and the closing checkpoint uses a namespaced immutable Git tag. Cross-provider validation is truthfully marked pending rather than claimed.

## Next Gate

`GATE 0 — FOUNDATION`

It is permitted only after explicit user authorization and a new pre-Gate checkpoint. Gate 0 was not implemented by SETUP-00.

## Evidence

- `TESTS.json`, `QUALITY.json`, `PROVENANCE.json`, and `COMMANDS.jsonl`.
- `REVIEW-REPORT.md`, `RED-TEAM-REPORT.md`, and `RESUME-VALIDATION.md`.
- `python scripts/development-ledger/validate_checkpoint.py`.
- `python -m unittest discover -s tests -v`.
- Final reference: `refs/tags/iacode-checkpoints/SETUP-00-CP-0001` (resolve with `git rev-parse`).
