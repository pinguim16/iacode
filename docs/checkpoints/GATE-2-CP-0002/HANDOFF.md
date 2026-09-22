# Handoff

Current Gate: GATE-2
Current Status: INTERNAL_GATE_PASS

Last valid commit: 424650d58167422cda08ebd580cc70fe75433668
Current branch: main

## Objective

Close GATE 2 — AGENT RUNTIME from `GATE-2-CP-0001`, sealed `BLOCKED`, by obtaining the live evidence
rows 19.1, 19.2 and 19.5 require, and by nothing else: no new Gate, no new architecture.

## What was completed

- The live evidence, against `openai:gpt-4o-mini` by the operator's decision: the gateway smoke `cmd-0005`, the agent runtime smoke `cmd-0006`, the persisted provenance `cmd-0007`.
- `G2-F-009`: a wrong-typed `content` is refused as `content-not-a-string`, and the runtime contract
  states that `content` is one JSON string. `LSN-0047`, `GRD-0049`.
- `G2-F-010`: every terminal path writes the terminal event before the terminal state, and the API
  records `RUN_FAILED` for a workflow that could not start. `LSN-0048`, `GRD-0050`.
- `G2-F-011`: three diagnostic records nobody could replay were taken out of the ledger on the
  operator's decision and kept verbatim in `DECISIONS.md`; the probe is now
  `scripts/iacode/agent_envelope_probe.py` (`cmd-0008`). A recurrence of `LSN-0010`.
- `G2-F-012`: the live gateway smoke waits for the Prometheus scrape instead of racing it.
  `LSN-0049`, `GRD-0051`.
- `G2-F-013`: a sealed checkpoint that kept the symbolic `HEAD` is bound to its own canonical tag,
  and the seal tool refuses a state that does not name its own tag. `ADR-0023`, `LSN-0050`, `GRD-0052`.
- `G2-F-014`: the Foundation smoke waits for both Prometheus targets, the fresh-installation
  scenario names the smoke checks that fail, and `GRD-0051` is a scan of every Prometheus reader. A
  `GUARDRAIL_FAILURE` against `LSN-0049`, resolved here.
- `GATE-2-CP-0001` anchored in the integrity chain (`cmd-0002`); the requirement set derived for
  this checkpoint: 186, all complete.

## What was NOT completed

Nothing this Gate specifies. The route-level fallback from DevWorld to OpenAI was not configured:
GATE 1 row 7.8 keeps every route empty, and that is a separate decision. `M1` is `PENDING` until a
fresh session audits it after GATE 3.

## Current repository state

See `STATE.json`. `FILES.json` declares every path the closure changed against the sealed commit
`424650d58167422cda08ebd580cc70fe75433668`, and the recorded hashes describe the committed content.

## Files changed

See `FILES.json`, each path with the reason it changed.

## Important decisions

See `DECISIONS.md`: why a second checkpoint, the decisions taken at closure, the findings, and the
records made against the sealed `GATE-2-CP-0001`.

## Tests executed

| Suite | Cases | Result | Evidence |
|---|---|---|---|
| Ledger and Gate suites | 578 | PASS | `cmd-0056` |
| Image suites (API, gateway, agent runtime) | 606 | PASS | `cmd-0013` |
| Live infrastructure suite | 48 | PASS | `cmd-0014` |
| **Total** | **1,232 / 1,232 discovered** | **PASS** | `TESTS.json`, `COUNTS.json` |

One ledger case skips itself and is counted as executed without failure, as every run of this suite has counted it: `Gate2AdrTests.test_the_index_lists_them`, because `docs/adr/README.md` does not exist, so it has never asserted anything; see `R-G2-012`.

## Known failures

None open. The live failures of the closure are recorded, not hidden: the first team run and the
second single run, in the records made against `GATE-2-CP-0001` (`DECISIONS.md`), and this
checkpoint's first gateway smoke, `cmd-0004`. Each was a defect and each was repaired before a
passing run counted.

## Known risks

See `RISKS.md`. The one that needs the operator: an OpenAI credential was shared in a chat
transcript during the closure. It never entered the repository; rotate it.

## Do not repeat

- Do not substitute the smoke model to make a live check pass. It is configuration and the decision
  belongs to the operator.
- Do not retry a live run until it is green. Every failure of this closure was a real defect.
- Do not edit a sealed checkpoint. Its successor closes it.
- Do not refuse a wrong-typed value with the sentence for a missing one. `LSN-0047`.
- Do not commit a state before the event that explains it. `LSN-0048`.
- Do not record a command whose script is not in the repository. `LSN-0010`.
- Do not read a metric before the scrape that carries it, anywhere. `LSN-0049`.
- Do not report a failure by its count; name what failed.
- Do not seal a checkpoint whose state does not name its own tag. `LSN-0050`.

## Required next action

Obtain the owner's explicit authorization for GATE 3 — SANDBOX. See `NEXT.md`.

## Exact continuation sequence

1. `python scripts/development-ledger/validate_checkpoint.py`
2. `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD` against
   `STATE.json`
3. With authorization only: the GATE 3 checkpoint and its lesson preflight, as `NEXT.md` states.

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

## Stop conditions

- GATE 3 work of any kind without the owner's explicit authorization.
- Any claim that this delivery's internal mirror or internal Red Team is independent validation: it
  is not, and `M1` stays `PENDING` until a fresh session audits it after GATE 3.
- Any mandatory gate red: repair it, never weaken it.
