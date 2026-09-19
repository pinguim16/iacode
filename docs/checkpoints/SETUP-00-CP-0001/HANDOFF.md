# Handoff

Current Gate: SETUP-00 — Development Control Plane
Current Status: GATE_PASS

Last valid commit: resolve `refs/tags/iacode-checkpoints/SETUP-00-CP-0001` with Git.
Current branch: main

## Objective

Preserve the completed SETUP-00 control plane and permit Gate 0 only after explicit user authorization.

## What was completed

The tool-neutral control plane, agent contracts, schemas, templates, policies, protocols, prompts, checkpoint lifecycle, secret redaction, automated validation, independent review, adversarial testing, cold-start simulation, and final evidence were completed.

## What was NOT completed

Gate 0 and every runtime capability remain unimplemented. Genuine resume validation by Claude Code or another provider remains `PENDING_MANUAL` because Claude Code is not installed.

## Current repository state

The final checkpoint is intended to be clean on branch `main`; its namespaced checkpoint tag must resolve to the checked-out commit. `STATE.json` and the validator are authoritative.

## Files changed

All tracked files were created from the `EMPTY_PROJECT` baseline for SETUP-00. `FILES.json` contains the complete canonical inventory and portable SHA-256 hashes, except its documented self-hash.

## Important decisions

Documentation is first-class, checkpoints are validated, agents are tool-neutral, training rights default to deny, Git work is Gate-bound, and handoff-ready checkpoints use immutable tag anchors.

## Tests executed

`python -m unittest discover -s tests -v` passed 34 tests: 29 validator/redactor unit cases and 5 isolated lifecycle/integration cases. Python compilation and Git whitespace checks also passed.

## Known failures

No unresolved mandatory SETUP-00 failure remains. Genuine second-tool/provider validation is explicitly pending manual execution as permitted by the cold-start requirement.

## Known risks

The standard-library validator implements only schema keywords used by this repository; secret patterns require maintenance; tool adapters can drift; and no runtime capability exists. See `RISKS.md`.

## Do not repeat

Do not recreate SETUP-00, move or overwrite checkpoint tags, bypass validation, invent unavailable tool support, or implement Gate 0 without explicit authorization.

## Required next action

Wait for explicit user authorization to begin `GATE 0 — FOUNDATION`. Before any change, execute the continuation protocol and create a new Gate 0 checkpoint.

## Exact continuation sequence

1. Read `START-HERE.md`, the Development Contract, Master Plan, LATEST pointer, and this entire checkpoint.
2. Run checkpoint validation and compare branch, tag-resolved commit, and dirty state.
3. Run the validation commands below.
4. If any divergence exists, create `DIVERGENCE.md`, set `BLOCKED`, and stop.
5. Confirm explicit authorization for Gate 0.
6. Create the pre-Gate checkpoint and baseline; do not reuse this closed checkpoint as a work log.

## Validation commands

```text
python scripts/development-ledger/validate_checkpoint.py
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
git diff --check HEAD^ HEAD
git status --short --branch
git branch --show-current
git rev-parse HEAD
git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0001
```

## Stop conditions

Stop on validator/test failure, tag/HEAD mismatch, dirty or divergent Git state, missing authorization, secret detection, rights uncertainty, or any request that crosses the authorized Gate.
