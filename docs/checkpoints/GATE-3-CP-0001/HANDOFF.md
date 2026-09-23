# Handoff

Current Gate: GATE-3
Current Status: INTERNAL_GATE_PASS

Last valid commit: 89818afe7d78ff857712a436d4ea0c6772eced79
Current branch: main

## Objective

Deliver `GATE 3 — SANDBOX + TOOL EXECUTION`, the last Gate of `M1`: the layer that executes the tool
requests of the Agent Runtime with real isolation, and nothing on the host. Carry the five defects
Gate 2 handed over, and develop in public at `pinguim16/iacode` with atomic commits pushed while
green.

## What was completed

- **Public history.** The authorised remote, a full-history secret scan before the first push
  (`cmd-0005`, clean), a staged scan before every push, atomic commits pushed to `origin/main`, no
  rewrite of published history (`ADR-0024`).
- **Phase 0.** The five inherited defects repaired test-first: ledger replayability (fix A), one
  guardrail resolution function (B), the lesson index as the render of the memory (C), the terminal
  stream draining every page (D), the ADR index and its test (E).
- **The sandbox service** (`services/sandbox/`): versioned contracts, a canonical tool policy, an
  explicit registry of 12 tools, one path resolver, a patch applier that applies all or nothing, an
  in-container helper that kills every process a tool leaves, disposable hardened sibling containers
  per run, content-addressed images, sessions and executions in the database, artifacts in MinIO,
  recovery and a bounded sweeper, metrics and logs (`ADR-0025`, `ADR-0026`, `ADR-0027`).
- **Agent Runtime integration.** A stage whose agent names a sandbox policy has its tool requests
  executed in the run's sandbox and resumes on the persisted result; the coding team (planner,
  developer, code reviewer) and its profiles; the run page shows the tools executed.
- **Evidence on the real engine.** The sandbox suite (140 cases), four recorded scenarios — coding
  with a host sentinel, timeout, cancellation, recovery (`cmd-0071` to `cmd-0074`) — and the internal
  Red Team, 25 of 25 with a valid control.
- **Findings repaired as they were found.** `G3-F-001` to `G3-F-004` (`DECISIONS.md`), each with a
  lesson (`LSN-0051` to `LSN-0054`) and, where a control exists, a guardrail (`GRD-0053` to
  `GRD-0055`).
- **The canonical specification** `docs/GATE-3-CHECKLIST.md` (139 rows) and 53 lesson requirements:
  192 requirements, all complete with resolvable evidence.

## What was NOT completed

Nothing this Gate specifies. The optional live-model smoke through the sandbox (prompt section 120)
was not run; the deterministic scenarios are the required evidence. `M1` is ready for its
fresh-session audit and reads `PENDING` until that audit (`DECISIONS.md` D-12).

## Current repository state

See `STATE.json`. `FILES.json` declares every path the Gate changed against
`d4a3998ce745dcbfcf6a8498f267ee302834543f`, each with its reason, and the recorded hashes describe
the committed content.

## Files changed

See `FILES.json`.

## Important decisions

See `DECISIONS.md` (D-01 to D-13) and `ADR-0024` to `ADR-0027`.

## Tests executed

| Suite | Cases | Result | Evidence |
|---|---|---|---|
| Control-plane suite (`tests/`) | 689 | PASS | `cmd-0107` |
| Image suites: API, gateway and agent runtime (623) and sandbox, integration included (141) | 764 | PASS | `cmd-0100` |
| Live infrastructure suite | 49 | PASS | `cmd-0106` |
| **Total** | **1,502 of 1,502 discovered** | **PASS** | `TESTS.json`, `COUNTS.json` |

Beside the counted suites: the frontend build and suite, 49 cases (`cmd-0116`); the four sandbox
scenarios (`cmd-0071` to `cmd-0074`); the full verification, 31 of 31 stages (`cmd-0105`); the
Green Keeper, 12 of 12 mandatory gates in one cycle (`cmd-0107` to `cmd-0118`); the internal Red
Team, 25 of 25 with a valid control (`cmd-0119`); the completeness audit, 192 of 192 (`cmd-0123`);
and the internal mirror audit, `PASS` (`cmd-0126`).

## Known failures

None open. The failures of the Gate are recorded, not hidden: the first coding run (`G3-F-003`),
the first Red Team run (`cmd-0079`, `G3-F-004`), the lint gate left red by commits 12 and 13
(`G3-F-002`), and `cmd-0031` (`D-02`). Each was repaired before a passing run counted.

## Known risks

See `RISKS.md`. The one to keep in view: the sandbox service holds the container engine's socket
(`R-G3-001`).

## Do not repeat

- Do not run a tool anywhere but inside a sandbox, and do not mount a host path, the engine's socket
  or a credential into one.
- Do not let two processes spell the same payload separately; name it once in the contract.
- Do not push without running the gates the change reaches — the lint gate and the repository-wide
  scans included.
- Do not start GATE 4 before the `M1` audit and the owner's authorization.

## Required next action

`M1 FRESH-SESSION MILESTONE AUDIT`, in a new session. See `NEXT.md`.

## Exact continuation sequence

1. `python scripts/development-ledger/validate_checkpoint.py`
2. `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD` against
   `STATE.json`
3. `python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0001`
4. The milestone audit, in its own checkpoint, as `NEXT.md` states. No GATE 4 work.

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
python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0001
```

## Stop conditions

- GATE 4 work of any kind before the `M1` audit and the owner's explicit authorization.
- Any claim that this delivery's internal mirror or internal Red Team is independent validation: it
  is not, and `M1` stays `PENDING` until the fresh-session audit.
- A tool executed anywhere but inside a sandbox, or a sandbox given a host path, the engine's socket,
  a network it was not granted or a credential.
- A commit that is not on `origin/main`, a rewrite of published history, or a moved tag.
- Any mandatory gate red: repair it, never weaken it.
