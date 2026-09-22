# Diff Summary — GATE-2-CP-0001

Measured against `4de6b2fb191ab3e7d7879fe81b5a72ce454829b2`, the sealed tip of `GATE-1-CP-0001`.

| Measure | Value |
|---|---|
| Tracked files changed | 42 (+2283 / -130) |
| New files outside the checkpoint | 79 (15,636 lines) |
| New checkpoint evidence files | 22 |
| Files moved | 3 (`apps/api/.../db/{base,models,engine}.py` → `packages/persistence/`) |

## What was added

**`packages/contracts/src/iacode_contracts/agent_runtime.py`** — the one vocabulary the runtime, the
database and the API all derive from: run states, allowed transitions, event types, signal names,
and the wire shapes of the public API. No credential field and no address field appears in any
request model.

**`packages/persistence/`** — the shared schema, extracted from `apps/api`. `base.py`, `models.py`
and `engine.py` moved with `git mv` so their history follows them. Five new tables — `agent_teams`,
`run_events`, `tool_requests`, `tool_results`, and the evolved `agent_runs` — plus the widened
`RUN_STATUSES` vocabulary. `apps/api/.../db/engine.py` stays as a thin delegation, so every Gate 0
and Gate 1 call site is unchanged.

**`services/agent-runtime/`** — the runtime library: the turn engine, the envelope protocol, the
context assembler, budgets and limits, the profile registry, the gateway HTTP client, the store
adapter, telemetry and the service façade. 19 modules, no I/O in the engine, no provider SDK
anywhere. 209 test cases beside it.

**`services/orchestrator/src/iacode_orchestrator/{agent_runtime,workflows/agent_run.py}`** — the
durable half: eleven activities that satisfy the runtime's `Effects` protocol, and the workflow that
sequences them, holds the `tool_result` and `cancel` signals, and bounds the run by its deadline. A
second Worker on `agent_runtime_task_queue`, with its own metrics port.

**`services/orchestrator/rehearsal/`** — the scenario harness, mounted at `/app/rehearsal` and
therefore unreachable from `PYTHONPATH=/app/src`. One scripted model activity and eight
subcommands. This is what makes an agent that asks for a tool exist in a Gate where no shipped
profile may have one.

**`apps/api/src/iacode_api/routes/agent_runs.py`** — eight endpoints: create, list, detail, events,
the SSE stream with `Last-Event-ID` resume, cancel, submit a tool result, and the two catalogues.

**`apps/api/migrations/versions/0003_agent_runtime.py`** — the schema change, reversible, with the
CHECK/UNIQUE naming asymmetry stated where the code is.

**`agents/`** — four profiles, two teams, four prompt files, and a README that consumes the
directory's Gate 2 reservation. Every profile declares `allowedActions: []`.

**`apps/web/src/app/agent-runtime/`** — the operational page, its service, and two specs.

**`scripts/`** — one quality gate (`gates/agent_runtime_tests.py`), one live smoke
(`agent_runtime_smoke.py`), three scenarios (durability, cancellation, deadline), and the Gate's Red
Team pair (`gate2_red_team.py`, `gate2_runtime_attacks.py`).

**`tests/test_gate2_agent_runtime.py`** — 71 repository-level cases: the canonical specification
mirror, the mandatory gate set, the scope, the boundary scans with their null controls, workflow
determinism, the persistence contract, the declared agents, the documentation and ADRs, the live
smoke contract, frontend safety, source integrity, scenario readiness and migration naming.

## What was changed

`.iacode/policies/{gate-scope,test-suites,quality-gates,canonical-requirements}.json` — the Gate's
authorized directories, the counted suites, the eleventh mandatory gate, and the 137-row mirror of
`docs/GATE-2-CHECKLIST.md`.

`infra/compose/{docker-compose.yml,.env.example}`, `infra/prometheus/prometheus.yml`, both
Dockerfiles, both `pyproject.toml` files, `apps/api/.../config.py`, `lifespan.py`, `main.py`,
`workflows/client.py` — the runtime's settings, its dependencies, its scrape target and its
workflow entry points.

`scripts/iacode/verify.py` — four new stages. `scripts/iacode/image_tests.py` — the runtime image.

`START-HERE.md`, `README.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/VERSIONS.md`,
`agents/README.md`, and three new ADRs.

## What was deliberately not changed

No sandbox, no executor, no shell, no filesystem tool, no Git tool. `services/sandbox/` is untouched
and remains reserved for GATE 3. No milestone artifact was written: `M1` stays `PENDING`.
