# Handoff

Current Gate: GATE-3
Current Status: READY_FOR_REVIEW

Last valid commit: bd1de7fd2d0b34342c7d0f83a558bd81c63c1100
Current branch: main

## Objective

The corrective delivery of the fresh-session `M1` audit `GATE-3-CP-0002` (`M1-CP-0002`,
`REWORK_REQUIRED`): close `M1-F-003` (HIGH), `M1-F-001` and `M1-F-002` (MEDIUM), without changing the
architecture, without new scope and without `GATE 4`, and hand the corrected milestone to a new
fresh-session audit.

## What was completed

- **`M1-F-003`.** Three replaced closure commits named by sealed evidence — not one — are kept by
  published lightweight tags under `refs/tags/iacode-preserved/` (owner-authorised, `DECISIONS.md`
  D-01), each naming exactly its commit, pushed without force. The property is now the rule: every
  commit a checkpoint's evidence names must be reachable from a published reference; one
  definition in `ledger_common` (`published_reachability`, `published_clone`); every control over
  sealed history clones the published history; `remote_sync.py` checks every evidence tag;
  ADR-0028. Recorded as a `GUARDRAIL_FAILURE` of `GRD-0042` (`LSN-0040`) and resolved here. A clone
  of the remote passed the full verification and validated every sealed `M1` checkpoint.
- **`M1-F-001`.** The exact envelope of every kind, `tool.name` and `tool.arguments` included, is
  rendered from `envelope_schema()` into the runtime instructions and the repair; the tool object
  is closed. The owner's configured model made eleven valid tool requests, all executed in the
  sandbox, with no repair.
- **`M1-F-002`.** A tool request records its executor; a result is accepted only from that
  executor's path; a forged result is refused `403 TOOL_RESULT_ORIGIN_REFUSED` during and after
  the sandbox's execution, the stored result stays the sandbox's and the agent sees it; the
  audit's null control and mutation are a verification stage.
- The audit registered, `GATE-3-CP-0002` anchored (19 anchors), two new lessons and guardrails,
  one recurrence recorded, the Red Team's two new attacks, the findings closure (3/3).

## What was NOT completed

Nothing the mandate asked for. `M1` is **not passed**: that is a new fresh-session audit's verdict,
not this delivery's. `GATE 4` was not started.

## Current repository state

See `STATE.json`. `FILES.json` declares every path changed against
`3a526925cf653ffaa9497cff628d08d50424271a` with its reason.

## Files changed

See `FILES.json` and `DIFF-SUMMARY.md`.

## Important decisions

See `DECISIONS.md` (D-01 to D-12) and ADR-0028, the ADR-0022 amendment.

## Tests executed

See `TESTS.json`, `COUNTS.json`, `VERIFICATION-REPORT.json` and `CLEAN-CLONE-REPORT.json`.

## Known failures

None open. Recorded and repaired, not hidden: `cmd-0025` (guardrail failure recorded before its
repair, D-04), `cmd-0030` (harness subject, D-06), `cmd-0034` (a kind spelled by hand), `cmd-0040`
(stale preflight and codepage captures, D-09), `cmd-0052` (lint gate red after `3101d31`, D-09).

## Known risks

See `RISKS.md`. For the owner: rotate the credential of `R-G2-009`; GitGuardian's report on
`7d57721` matched deliberately fake values in the audit harness, and no real credential of this
machine appears anywhere in the history (`SECRET-EXPOSURE-CHECK.json`).

## Do not repeat

- Do not judge sealed history from a clone of the local path: clone the remote or use
  `ledger_common.published_clone`.
- Do not replace a commit a ledger record already names; if it happens, preserve it with a
  published tag under `refs/tags/iacode-preserved/`, never by rewriting the record.
- Do not push before the lint gate (`LSN-0054`).
- Do not accept a result from a door the request's owner did not open.

## Required next action

`M1 FRESH-SESSION REAUDIT`, in a new session. See `NEXT.md`.

## Exact continuation sequence

1. `python scripts/development-ledger/validate_checkpoint.py`
2. `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD` against
   `STATE.json`
3. `python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0003`
4. `python scripts/development-ledger/milestone_status.py --milestone M1` (expected: not passed)
5. The fresh-session audit, in its own checkpoint, as `NEXT.md` states. No `GATE 4` work.

## Validation commands

```bash
python scripts/development-ledger/validate_checkpoint.py
```

```bash
python scripts/development-ledger/validate_lessons.py
```

```bash
python scripts/development-ledger/verify_integrity.py
```

```bash
python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0003
```

## Stop conditions

- Any `GATE 4` work before `M1` passes a fresh-session audit and the owner authorises it.
- Any change to this sealed checkpoint, its tag, or a preserved tag.
- A claim that this implementing run's internal verdicts are independent validation.
