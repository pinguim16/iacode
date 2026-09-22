# Baseline — GATE-2-CP-0001

The state this Gate starts from, observed rather than assumed.

## Predecessor

`GATE 1 — MODEL GATEWAY`, checkpoint `GATE-1-CP-0001`, status `INTERNAL_GATE_PASS`, sealed under
`refs/tags/iacode-checkpoints/GATE-1-CP-0001` at commit
`4de6b2fb191ab3e7d7879fe81b5a72ce454829b2`.

Before any file of this Gate was changed, the predecessor was validated from the working tree:

| Command | Result |
|---|---|
| `python scripts/development-ledger/validate_checkpoint.py` | `CHECKPOINT_VALID` |
| `python scripts/development-ledger/validate_lessons.py` | `LESSONS_VALID total=40 active=40 guarded=38` |
| `python scripts/development-ledger/verify_integrity.py` | `INTEGRITY_VALID anchors=14 latest=SETUP-00-CP-0013` |

`M1` is `PENDING` and covers Gates 0 to 3. It is audited after Gate 3, so this Gate closes on the
project's own controls.

The observed Git state agreed with `STATE.json`: branch `main`, head
`4de6b2fb191ab3e7d7879fe81b5a72ce454829b2`, clean worktree. No divergence was found, so no
`DIVERGENCE.md` exists.

The first recorded validation inside this checkpoint (`cmd-0002`) exits `1`, and that is the honest
record of a work-in-progress checkpoint: `FILES.json` is empty until the inventory is declared and
`STATE.json` still carries the preflight and anchor defaults the skeleton was created with. The
record stays because a refused attempt is evidence too; the validation that describes the delivered
content is recorded at the end of the run.

## What this Gate inherits

**A provider-neutral boundary it can call without knowing a provider exists.** `ModelGateway` takes
a `GatewayRequest` and returns a `GatewayResponse`, and it owns retries, timeouts, the circuit
breaker, the fallback chain and provider selection. The agent runtime must not reimplement any of
them.

**A catalog whose capabilities are honest and mostly unknown.** Every DevWorld model reports
`tools`, `vision`, `structured-output` and `reasoning` as `UNKNOWN`, because the provider publishes
nothing about them. The router refuses an unknown capability rather than guessing. The agent
protocol therefore cannot depend on native structured output; it uses JSON text validated locally
by the same contract, and uses the native capability only where a model declares it.

**Tool calls that are normalised and never executed.** The gateway turns a provider's tool call into
`ToolCall` and stops there.

**Twelve structural tables.** `tasks`, `task_runs`, `agents`, `agent_runs`, `model_calls` and
`tool_calls` already exist, created by Gate 0 as a persistence contract. This Gate evolves them and
adds what the runtime needs; it creates no parallel entity.

**A Temporal worker with one smoke workflow.** `services/orchestrator` runs as its own process,
polls the `iacode-foundation` task queue and exposes the SDK's own metrics. The smoke workflow stays
exactly as small as it is; the agent workflow is added beside it.

## Measured starting point

| Suite | Cases at baseline |
|---|---|
| Control plane (`python -m unittest discover -s tests`) | 491 |
| Backend and gateway (pytest inside the API image) | 354 |
| Infrastructure (`python -m unittest discover -s infra/tests`) | 48 |
| Frontend (Vitest inside the toolchain image) | 30 |

Ten mandatory gates are registered in `.iacode/policies/quality-gates.json`: `tests`,
`staticAnalysis`, `lessons`, `integrity`, `checkpointValidation`, `apiTests`, `gatewayTests`,
`webTests`, `lint`, `infraDefinition`.

## Constraints this Gate accepted before starting

- Gate 2 executes no tool. A tool request is persisted and the run pauses; Gate 3 executes.
- Nothing reserved for a later Gate may be implemented: `services/sandbox`, `services/evaluator`,
  `services/experience`, `services/knowledge`, `services/training`, `apps/cli`,
  `apps/vscode-extension`, `training`, `evaluation`, `datasets`.
- The provider credential lives only in `infra/compose/.env`, which Git ignores. It is never
  displayed, printed, copied, versioned, put in a report or persisted.
- `M1` stays `PENDING`. No independent, fresh-session or cross-tool verdict may be claimed here.
