# Handoff

Current Gate: GATE-2
Current Status: BLOCKED

Last valid commit: 4de6b2fb191ab3e7d7879fe81b5a72ce454829b2
Current branch: main

## Objective

Deliver the Agent Runtime: a task becomes a durable run, a run selects a profile or a team,
assembles its context, calls **only** the Model Gateway, executes a sequence of agents, persists its
state and its events, survives a worker restart, respects its limits, can be cancelled, streams what
happens, produces a final result, and — when an agent asks for a tool — records the request, pauses,
and **executes nothing**.

## What was completed

Everything the Gate specifies except three requirements that need a live model call.

- `packages/contracts/.../agent_runtime.py` — one vocabulary for the run states, the transitions,
  the event types, the signal names and the public wire shapes.
- `packages/persistence/` — the schema three processes share, extracted from `apps/api` with its
  history intact. Five new tables; the API keeps a thin delegation so no Gate 0 or Gate 1 call site
  changed.
- `services/agent-runtime/` — the turn engine behind ports, the envelope protocol with exactly one
  repair, the context channels, budgets and limits, the profile registry, the gateway HTTP client,
  the store adapter, telemetry and the service façade. No I/O in the engine, no provider SDK
  anywhere, no module that could execute anything.
- `services/orchestrator/` — eleven activities, the durable workflow, the tool-result and cancel
  signals, the wall-clock deadline, and a second Worker with its own metrics port.
- `apps/api/.../routes/agent_runs.py` — eight endpoints including a resumable SSE stream.
- `agents/` — four profiles and two teams, every profile with `allowedActions: []`.
- `apps/web/src/app/agent-runtime/` — the operational page, which offers no control that would
  execute a tool.
- `apps/api/migrations/versions/0003_agent_runtime.py` — applied and reversed against a disposable
  database.
- Three scenarios against the real stack: a run waiting for a tool survives a real container
  restart; a paused run is cancelled, stays cancelled and refuses a late result; a run that is alive
  and going nowhere is ended at its deadline and the store records why.
- Six lessons and six guardrails, and one recurrence recorded against `LSN-0038`.

## What was NOT completed

Checklist rows 19.1, 19.2 and 19.5: the live single-agent run, the live planner-reviewer run, and
the live provenance evidence. See `STATUS.md` for the blocker and `NEXT.md` for the exact sequence
that closes them.

## Current repository state

See `STATE.json`. The tree is dirty at handoff time only in the sense that this checkpoint is the
change; `FILES.json` declares every path and the recorded hashes describe the committed content.

## Files changed

See `FILES.json`: 109 created, 42 modified, 2 deleted, each with the reason it changed.

## Important decisions

See `DECISIONS.md` and `ADR-0020`, `ADR-0021`, `ADR-0022`.

## Tests executed

| Suite | Cases | Result | Evidence |
|---|---|---|---|
| Ledger and Gate suites | 569 | PASS | `python -m unittest discover -s tests` |
| Image suites (API, gateway, agent runtime) | 603 | PASS | `python scripts/iacode/image_tests.py` |
| Live infrastructure suite | 48 | PASS | `python -m unittest discover -s infra/tests` |
| **Total** | **1,220 / 1,220 discovered** | **PASS** | `TESTS.json`, `COUNTS.json` |

## Known failures

**The provider's quota is exhausted.** Every paid DevWorld model answers `429 RATE_LIMITED` with
`retryAfterSeconds` ≈ 52,600; the free tier answers `503 PROVIDER_UNAVAILABLE`. Gate 1's own
`gateway_smoke.py` fails identically, which places the condition in the provider. This is the
Gate's only blocker.

**Eight findings were raised against this delivery and repaired**, `G2-F-001` to `G2-F-008`. The
most serious, `G2-F-008`, was a wall-clock deadline that fired exactly on time and recorded nothing:
the workflow died with `Activity cancelled` while the run row stayed `RUNNING` for ever. Only the
scenario could see it.

## Known risks

See `RISKS.md`.

## Do not repeat

- Do not substitute the smoke model to make a live check pass. It is configuration and the decision
  belongs to the operator.
- Do not enforce a limit with a timeout that cancels the task doing the enforcing. `LSN-0046`.
- Do not write a boundary scan that reads prose, and do not ship one without a control that fires on
  a mutated module. `LSN-0044`.
- Do not declare readiness while `blockedBy` is non-empty.

## Required next action

Re-run the two live smokes once the provider quota resets. See `NEXT.md` for the exact commands.

## Exact continuation sequence

1. `python scripts/development-ledger/validate_checkpoint.py`
2. `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD` against
   `STATE.json`
3. The two commands in `NEXT.md`
4. `derive_requirements.py --write`, `check_completeness.py --write`, `m0_mirror_audit.py --write`
5. `green_keeper.py` until every mandatory gate is green
6. `finalize_checkpoint.py --status INTERNAL_GATE_PASS`, commit, `seal_checkpoint.py`

## Validation commands

```bash
python scripts/development-ledger/validate_checkpoint.py
```

```bash
python scripts/development-ledger/green_keeper.py
```

```bash
python scripts/iacode/verify.py --report var/verify-report.json
```

## Stop conditions

- The configured smoke model still will not answer: the Gate stays `BLOCKED`.
- Any mandatory gate is red: repair it, never weaken it.
- GATE 3 work of any kind: not authorized.
- Any claim that this delivery's internal mirror or internal Red Team is independent validation: it
  is not, and `M1` stays `PENDING` until a fresh session audits it after GATE 3.
