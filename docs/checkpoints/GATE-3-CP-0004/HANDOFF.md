# Handoff

Current Gate: GATE-3
Current Status: REWORK_REQUIRED

Last valid commit: f61f84ca7e830002db1674f1df2aca8172f6e483
Current branch: main

## Objective

Return the Critical dependency finding to an implementing run without changing product code in the auditor run.

## What was completed

Fresh-session M1 re-audit through the frozen Critical/High stop condition; sealed-subject,
published-history, full verification, independent finding reproduction, Green Keeper, test counts
and delivery completeness evidence are complete.

## What was NOT completed

Correction of `M1-F-004`, the later audit criteria intentionally skipped after the stop condition,
and a new independent M1 audit.

## Current repository state

See STATE.json.

## Files changed

See FILES.json.

## Important decisions

See DECISIONS.md.

## Tests executed

See `TESTS.json`, `VERIFICATION-REPORT.json`, `DEPENDENCY-SCAN-REPORT.json` and `REWORK-LOG.jsonl`.

## Known failures

`M1-F-004` (Critical): two Critical and four High npm advisories in the pinned frontend graph.

## Known risks

See RISKS.md.

## Do not repeat

Do not update dependencies inside this audit checkpoint. Do not suppress advisories, narrow the
severity denominator, or begin `GATE 4` before a later independent M1 PASS.

## Required next action

Open `GATE-3-CP-0005`, register `M1-CP-0004`, correct and close `M1-F-004`, and submit the sealed
correction to a new independent M1 audit.

## Exact continuation sequence

Read `FINDINGS.json`; register the sealed audit; update direct pins and `apps/web/package-lock.json`;
run the complete assurance sequence; seal and push; start a fresh independent audit.

## Validation commands

`python scripts/development-ledger/validate_checkpoint.py`

## Stop conditions

Stop on divergence, any remaining Critical/High advisory, failed validation, or any attempt to
advance `GATE 4` before M1 passes.
