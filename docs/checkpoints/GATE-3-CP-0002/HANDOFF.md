# Handoff

Current Gate: GATE-3
Current Status: REWORK_REQUIRED

Last valid commit: 3bc8e9d8a94d44163d1af9325ad5b2272f71f8ed
Current branch: main

## Objective

The `M1` fresh-session milestone audit: judge `GATE 0` to `GATE 3` as a whole — their integration,
not each unit test again — from sealed content, without changing product code, and record the
verdict in an audit checkpoint of its own.

## What was completed

- Cold start; the subject `GATE-3-CP-0001` validated, anchored (18 anchors) and synchronised.
- Every sealed `M1` checkpoint validated detached at its own tag from this repository (5/5) and from
  a clone of the published remote (4/5 — `M1-F-003`).
- The full verification of this repository, 31/31 (`cmd-0012`), and a clean clone of the public
  remote: 30/31, `gate:tests` failed (`cmd-0023`, `M1-F-003`).
- One live run across every Gate — Agent Runtime, Model Gateway, Sandbox and back
  (`CROSS-GATE-LIVE.json`, `cmd-0016`).
- `R-G3-001` reviewed from proof: ten controls, 10/10, and an attack; disposition
  `ACCEPTED_LOCAL_ARCHITECTURAL_RISK` (`R-G3-001-REVIEW.json`).
- The audit's own cross-gate Red Team: 14/14 over a valid null-mutation control
  (`M1-INTERNAL-RED-TEAM.json`; the earlier runs are kept, `DECISIONS.md`).
- Three findings, each reproduced: `M1-F-003` HIGH, `M1-F-001` and `M1-F-002` MEDIUM; five
  observations; a consolidated risk register; the twenty frozen criteria computed from the artifacts
  (`FINAL-M1-AUDIT-MATRIX.json`, 16/20); the attestation `.iacode/attestations/M1-CP-0002.json`
  (`REWORK_REQUIRED`); the milestone report.

## What was NOT completed

`M1` did not pass, so `GATE 4` and `GATE 5` were not started — the owner's rule for a Critical or High
finding. The findings are not repaired here, by design: an auditor does not implement corrections.

## Current repository state

See `STATE.json`. `FILES.json` declares every path this checkpoint changed against
`3bc8e9d8a94d44163d1af9325ad5b2272f71f8ed`: the checkpoint itself, the attestation, the anchor it owed
its subject and `LATEST.md`. No product file changed.

## Files changed

See `FILES.json`.

## Important decisions

See `DECISIONS.md`.

## Tests executed

See `TESTS.json`, `COUNTS.json`, `VERIFICATION-REPORT.json` and `CLEAN-CLONE-REPORT.json`.

## Known failures

`M1-F-003`: in a clone of the published remote, `gate:tests` fails on
`test_every_sealed_checkpoint_validates_from_its_own_tag` for `GATE-1-CP-0001`. In this working
repository every mandatory gate is green, because its object store still holds the unreachable
commit the sealed record names. The failed attempts of the audit's own tooling are kept in the ledger
and explained in `DECISIONS.md`.

## Known risks

See `RISKS.md`. Two need the owner: `R-G2-009`, rotate the credential exposed outside the
repository; and keep the local reference `refs/iacode-preserved/b59d66f9f3f9`, which protects the
only copy of the commit `M1-F-003` concerns from garbage collection until the correction publishes it.

## Do not repeat

- Do not check sealed history through a clone of the local path: it carries unreachable objects.
  Clone the remote, or use `git clone --no-local`.
- Do not judge a sealed checkpoint by the validator of its own revision alone; the current
  validator applies the rules of the version the checkpoint declares.
- Do not read a live run's result as the developer's answer; a team's result is its last stage's.

## Required next action

The corrective delivery `GATE-3-CP-0003`, then a new fresh-session `M1` audit. See `NEXT.md`.

## Exact continuation sequence

1. `python scripts/development-ledger/validate_checkpoint.py`
2. `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD` against
   `STATE.json`
3. `python scripts/development-ledger/milestone_status.py --milestone M1` (expected: not passed)
4. `python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0002`
5. With the owner's authorization, open `GATE-3-CP-0003` as `NEXT.md` states.

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
python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0002
```

## Stop conditions

- Any `GATE 4` work before `M1` passes a fresh-session audit and the owner authorizes it.
- Any change to this sealed checkpoint or its tag.
- A claim that this fresh-session audit is cross-tool validation.
- A correction of `M1-F-003` that rewrites published history or moves a tag.
