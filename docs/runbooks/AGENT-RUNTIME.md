# Runbook — Agent Runtime

Everything an operator does with `GATE 2 — AGENT RUNTIME`: starting it, creating a run, following
it, cancelling it, answering a tool request, reading what a run cost, and what to do when something
is wrong.

One sentence first, because it governs everything below. **The runtime executes no tool.** An
agent that asks for one has its request recorded and the run pauses at `WAITING_FOR_TOOL` —
[ADR-0021](../adr/ADR-0021-tool-execution-boundary.md). Since `GATE 3`, a stage whose agent names a
sandbox policy has the request executed in the run's sandbox, as an activity on the sandbox's own
queue, and the run resumes with the result; any other stage still waits for a result delivered
through the API. The sandbox is operated through [SANDBOX.md](SANDBOX.md).

## Starting the runtime

The runtime is not a service of its own. It is a library the API composes to create and read runs
and the Temporal worker composes to execute them, so starting the stack starts it:

```bash
python scripts/iacode/stack.py up --build
```

What has to be true before a run can succeed:

| Condition | How to check it |
|---|---|
| The worker is polling the agent queue | `docker compose logs worker` shows `agentRuntimeTaskQueue` |
| The database is at the head revision | `python scripts/iacode/migrate.py current` |
| A provider is configured and reachable | `curl -s localhost:18080/api/v1/gateway/health` |
| The catalog has been synchronised at least once | the same answer's `catalogSize` is not `0` |
| A default model or a route is configured | the same answer's `defaultModel` |

The declared agents and teams are read from `agents/` and written into the database the first time a
run is created in a process. The write is idempotent and never overwrites a row an operator has
marked `customised`, so an edit you make in the database survives a restart and an edit you make in
`agents/` is picked up by the next run.

## Creating a run

```bash
curl -s -X POST localhost:18080/api/v1/agent-runs \
  -H 'Content-Type: application/json' \
  -d '{"task": "Reply with exactly: IACODE_AGENT_OK", "team": "single-agent"}'
```

The answer is immediate — `202`, a run identifier and a state — because a run can take minutes and
an endpoint that waited for one would be a timeout.

| Field | Meaning |
|---|---|
| `task` | what IACode is being asked to do. Bounded by `IACODE_AGENT_RUNTIME_MAX_TASK_BYTES`. |
| `team` | `single-agent` or `planner-reviewer`; `GET /api/v1/agent-teams` lists them |
| `route` or `model` | optional. A configured route alias, or an explicit `provider:model`. Never both. |
| `maxTurns`, `maxModelCalls`, `maxDurationSeconds`, `maxTotalTokens`, `toolWaitTimeoutSeconds` | optional limits, lower than the configured defaults |
| `idempotencyKey` | optional. The same key returns the run the first request created. |

There is deliberately no field for a provider address, an API key or a header. An address a request
can supply is an address an attacker can supply; both come from administrative configuration and
from nowhere else.

The operational page is at <http://localhost:18081/agent-runtime>. It does the same thing with a
form, and it shows the same states.

## Following a run

```bash
curl -s localhost:18080/api/v1/agent-runs/$RUN | python -m json.tool
curl -s "localhost:18080/api/v1/agent-runs/$RUN/events?after=0"
curl -N  "localhost:18080/api/v1/agent-runs/$RUN/events/stream"
```

The stream is Server-Sent Events. Every frame carries the sequence the store assigned as its
`id:`, so a consumer that reconnects with `Last-Event-ID` — which a browser's `EventSource` sends
by itself — resumes from exactly where it stopped. Reading creates no event, and reconnecting
duplicates none.

The states a run moves through:

```text
CREATED -> QUEUED -> RUNNING -> SUCCEEDED
                        |  \-> FAILED
                        |  \-> CANCELLED
                        \-> WAITING_FOR_TOOL -> RUNNING
```

`SUCCEEDED`, `FAILED` and `CANCELLED` are terminal. A terminal run is never resumed: another attempt
is another run.

## Cancelling a run

```bash
curl -s -X POST localhost:18080/api/v1/agent-runs/$RUN/cancel
```

The request is recorded first and the workflow is signalled second, so a run whose signal is lost
still stops at its next checkpoint. A cancelled run makes no further model call, closes every tool
request nobody will answer, and refuses a tool result that arrives afterwards.

## Tool requests

When an agent asks for a tool the run pauses and the request appears on the run:

```bash
curl -s localhost:18080/api/v1/agent-runs/$RUN | python -c \
  "import json,sys; print(json.load(sys.stdin)['pendingToolRequest'])"
```

What happens, precisely: the name is checked against the agent profile's permitted actions, the
arguments are bounded, the request is written to `tool_requests`, a `TOOL_REQUESTED` event is
recorded, and the run moves to `WAITING_FOR_TOOL`. **The name is never resolved to a command, a
path or an import, and no process is started.**

A stage with a sandbox policy — the `developer` and `code-reviewer` of the `coding` team — never
waits for anyone: the workflow dispatches the request to the sandbox, persists the result through
the same store validation the endpoint below uses, and resumes. A stage without one waits for a
result delivered through the API, exactly as it did in `GATE 2`.

## Tool results

For a stage without a sandbox policy, a result is delivered through the API by whatever is
authorised to execute — a test fixture or the durability rehearsal:

```bash
curl -s -X POST localhost:18080/api/v1/agent-runs/$RUN/tool-results \
  -H 'Content-Type: application/json' \
  -d '{"toolRequestId": "…", "status": "SUCCEEDED", "output": {"body": "…"}}'
```

It is validated against the database before the workflow hears about it. Five shapes are refused:

| Shape | Answer |
|---|---|
| a request that does not exist | `409 TOOL_RESULT_INVALID` |
| a request belonging to another run | `409 TOOL_RESULT_INVALID` |
| a request the sandbox owns (a stage with a sandbox policy) | `403 TOOL_RESULT_ORIGIN_REFUSED` |
| a request that is no longer pending | `409 TOOL_RESULT_INVALID` |
| a run that has already finished | `409 TOOL_RESULT_INVALID` |

The origin of a result is the endpoint's, fixed in code — `EXTERNAL` — and a submission cannot name
one. A sandboxed stage's request is answered only by the sandbox, through the workflow's internal
activity; see [SANDBOX.md](SANDBOX.md) (`M1-F-002`).

The same result delivered twice is not a refusal: it resolves the request once and resumes the run
once, because the uniqueness constraint on `tool_results` is the mechanism rather than the
discipline of the code above it.

## Budgets

Every run carries limits, and a run is never allowed to be unbounded:

| Limit | Default | What it stops |
|---|---|---|
| `maxTurns` | `IACODE_AGENT_RUNTIME_MAX_TURNS` | an agent loop |
| `maxModelCalls` | `IACODE_AGENT_RUNTIME_MAX_MODEL_CALLS` | the spend; a repair counts |
| `maxDurationSeconds` | `IACODE_AGENT_RUNTIME_MAX_DURATION_SECONDS` | a run that is alive and going nowhere |
| `toolWaitTimeoutSeconds` | `IACODE_AGENT_RUNTIME_TOOL_WAIT_TIMEOUT_SECONDS` | a pause nobody answers |
| `maxTotalTokens` | not set | the token spend, **when the provider reports usage** |

The ledger is debited before the call it pays for, so a run can never make a call it cannot afford.
A provider that reports no usage makes the token budget **unenforceable**, and the run says so
(`budget.tokensEnforceable` is `false`) rather than counting zero. Reaching any limit ends the run
with `BUDGET_EXCEEDED`.

## What a run costs

`summary.cost` is `UNKNOWN` unless the gateway knows the price of every call the run made. Zero
would be a different claim, and usually a wrong one. `summary.totalTokens` is derived from the
`model_calls` rows the gateway wrote, which is the authoritative source; the runtime keeps no second
count of its own.

## The live smoke

```bash
python scripts/iacode/agent_runtime_smoke.py
python scripts/iacode/agent_runtime_smoke.py --report var/agent-runtime-smoke.json
```

One single-agent run and one planner-and-reviewer run against the configured provider, through the
gateway — three model calls in total, short prompts, a low output cap.

It needs `IACODE_DEVWORLD_BASE_URL`, `IACODE_DEVWORLD_API_KEY` and `IACODE_GATEWAY_SMOKE_MODEL` in
`infra/compose/.env`, which Git ignores. Without them it exits `BLOCKED` (code `2`) and names the
variable that is missing. It never degrades into a `PASS`, and it never substitutes the configured
model for another one: spending on a model nobody authorised is a decision nobody made.

## The two scenarios

```bash
python scripts/iacode/scenarios/agent_runtime_durability.py
python scripts/iacode/scenarios/agent_runtime_cancellation.py
```

The first proves that a run waiting for a tool survives a **real** worker restart: it starts a
rehearsal worker as its own container, drives a run to `WAITING_FOR_TOOL`, runs `docker restart` on
that container, delivers the result and watches the run resume and finish. The second proves that a
paused run can be cancelled, stays cancelled, and refuses a late result.

Both use the real workflow, the real persistence and the stack's own Temporal. The only substitution
is the model, which answers from a script — see
[`services/orchestrator/rehearsal/README.md`](../../services/orchestrator/rehearsal/README.md) for
why that is the honest way to get an agent that asks for a tool in a Gate where no shipped profile
may have one.

## What is persisted, and what is not

This is the difference between this Gate's records and the gateway's, and it is deliberate:

| Table | Holds | Does not hold |
|---|---|---|
| `model_calls` | who was called, how long, how many tokens, what it cost | anything the call said. There is no column that could. |
| `tasks` | the instruction IACode was given | — |
| `task_runs` | the run's own final answer, its budget and its error | a prompt, a provider payload, a transcript |
| `agent_runs` | which profile and which prompt hash produced the stage, and its output | a model's private reasoning |
| `run_events` | short verifiable facts about each moment | a prompt, a completion, a credential — an event payload refuses those keys outright |

The run keeps the task and the answer because the workflow cannot resume without the first and the
page cannot render after a restart without the second. That is local operational persistence, not a
transcript of a provider exchange.

Nothing this Gate persists is training-eligible. `training_allowed` is `false` at the database
level and nothing in the runtime sets it.

## Troubleshooting

**A run stays `QUEUED`.** The worker is not polling the agent queue. Check
`docker compose logs worker` for `agentRuntimeTaskQueue`, and check that
`IACODE_AGENT_RUNTIME_TASK_QUEUE` is the same value for the API and the worker — the compose file
gives both the same variable for exactly this reason.

**A run fails immediately with `GATEWAY_ERROR`.** The message carries the gateway's own
classification. `the default model … is not in the catalog` means the catalog has not been
synchronised: `POST /api/v1/gateway/models/sync`. `the provider rate limited the request` or `the
provider is unavailable` is the provider, not the runtime; `python scripts/iacode/gateway_smoke.py`
will say the same thing about a plain inference.

**A run fails with `INVALID_AGENT_OUTPUT`.** The model answered with something that is not the
envelope, twice — once directly and once after a corrective call. Look at the `RUN_NOTE` event: it
records why the first answer was rejected. A model that cannot produce one JSON object is a model
to route away from, not a parser to loosen.

**A run fails with `BUDGET_EXCEEDED`.** It reached a limit it was created with. The `details` name
which one. Raise it on the next run rather than on the running one: a budget is frozen when the run
is created, deliberately.

**A run fails with `TOOL_WAIT_TIMEOUT`.** It asked for a tool and nothing answered. In this Gate
that is expected for any profile that permits an action, because there is no executor.

**A run fails with `WORKFLOW_ERROR`.** Temporal refused the start. The run is marked `FAILED` with
that reason rather than left at `CREATED`, so check Temporal's health and the task queue name.

**A run is `FAILED` and you want the detail.** The response carries an error type, a safe message,
the stage that failed and the correlation identifier. The traceback is in the API's log under that
identifier; it is never in the response, because a traceback quotes paths and sometimes connection
strings.

**Events stop arriving but the run is still going.** A proxy dropped the idle connection. The stream
sends a keep-alive comment every fifteen seconds for exactly this; reconnecting with
`Last-Event-ID` resumes without losing or duplicating anything.

**The page shows nothing under Teams.** The API could not read `agents/`. Check
`IACODE_REPOSITORY_ROOT` — it is `/app` inside both images, which is where the definitions are
copied.

## What this runtime does not do

No tool execution of its own: files, a shell and local Git exist only inside the sandbox of
[SANDBOX.md](SANDBOX.md). No browser. No retrieval, no experience store, no quality scoring, no
training. No dynamic team composition: a
team is configuration, and no model decides which agents run.

Operating the model boundary underneath it: [MODEL-GATEWAY.md](MODEL-GATEWAY.md). Operating the
stack underneath that: [FOUNDATION.md](FOUNDATION.md).
