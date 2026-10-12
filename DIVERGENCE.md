# Divergence

Run status: `BLOCKED`

## Findings

### G4-F-003 — HIGH — Published checkpoint evidence names a non-transportable input

The sealed `GATE-4-CP-0006` command ledger declares
`.git/gate4-cp0006-pre-red-retry.zip` as an input. That path existed only in the producing
repository's Git metadata and is absent from a transport clone, so the published checkpoint cannot
be validated from its canonical tag.

## Expected state

The published canonical checkpoint `GATE-4-CP-0006` must validate from a fresh transport clone at
`refs/tags/iacode-checkpoints/GATE-4-CP-0006`.

## Observed state

- Local `main`, `origin/main`, and the canonical tag all resolve to
  `dfa2871c4fcecf9eedd7df9f135a5cfcdebce9d5`.
- Local post-commit validation and integrity validation passed.
- A fresh clone from `https://github.com/pinguim16/iacode.git`, detached at the canonical tag,
  returned `CHECKPOINT_INVALID`.
- The exact failure is `COMMANDS.jsonl:61: recorded input does not exist:
  .git/gate4-cp0006-pre-red-retry.zip`.

## Cause

The audit recorded a direct review-bundle validation command with an ignored `.git/` archive as a
declared input. The archive existed locally when the command ran but is intentionally absent from
published transport. The command result is preserved truthfully, but its input declaration makes
the sealed checkpoint non-portable.

## Consequence

`GATE-4-CP-0006` cannot serve as the canonical published Gate 4 verdict. No `GATE_PASS` claim is
made from this run, and Gate 5 was not started.

## Required reconciliation

Create a successor Gate 4 checkpoint that records this publication defect, replaces the temporary
archive input with repository-carried evidence, repeats all mandatory assurance needed by policy,
seals without rewriting history, publishes a new canonical tag, and validates that tag from a fresh
remote transport clone. Do not move or delete the existing tag.
