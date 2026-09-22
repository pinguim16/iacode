# Red Team Report — GATE 2 — AGENT RUNTIME

Result: `RED_TEAM_PASS`

- Checkpoint: `GATE-2-CP-0002`
- Generated: `2026-09-22T21:27:34Z`
- Source: scripts/development-ledger/gate2_red_team.py with gate2_runtime_attacks.py — the internal adversarial battery of GATE 2 — AGENT RUNTIME, executed against the delivery
- Attacks: 22/22 defended

## Null-mutation control

Result: `VALID`

the unmutated fixture is accepted by every control this battery mutates: the runtime executes an unmutated run (the unmutated path runs, answers, records, parses, transitions, pauses on a tool, resumes and accepts an ordinary payload and budget); the scope control accepts the real tree (no violation); the canonical requirement set parses and mirrors (137 row(s)); the declared agents and teams are readable (4 profile(s), 2 team(s))

Without this the battery would prove nothing: a runtime that refused every request would
look perfectly defended. The unmutated path goes through the identical code and is
accepted before any mutation runs.

## Findings

None.

## Attacks

| Attack | Category | Target | Mutation | Expected | Observed | Result |
|---|---|---|---|---|---|---|
| `G2-A` | mandatory | state machine | apply every transition out of SUCCEEDED, FAILED and CANCELLED through the real state machine | every one is refused and a terminal run stays terminal | every terminal move was refused; 36 forbidden transitions in total | `DEFENDED` |
| `G2-B` | mandatory | budgets | run a real engine with an agent that answers MESSAGE for ever | the run ends with BUDGET_EXCEEDED at the configured turn limit | the run stopped after 3 turn(s) with BUDGET_EXCEEDED | `DEFENDED` |
| `G2-C` | mandatory | agent protocol | run a real engine with a model that never produces a valid envelope | one repair is attempted and the second refusal ends the run | one repair was attempted and the second refusal ended the run | `DEFENDED` |
| `G2-D` | mandatory | budgets | run a turn that needs a repair and read the ledger | the repair is counted as a model call like any other | the repair was charged like any other call | `DEFENDED` |
| `G2-E` | mandatory | agent protocol | parse every one of them with the real parser | none is read as an answer | all 14 malformed outputs were refused | `DEFENDED` |
| `G2-F` | mandatory | tool execution | run a real engine whose agent requests shell.exec with a destructive command | the request is stored as data, the run pauses, and nothing executes | the hostile command was stored verbatim as data, the run paused, and nothing in the engine can execute anything | `DEFENDED` |
| `G2-G` | mandatory | tool execution | run a real engine whose agent requests a tool outside its allowed actions | the request is refused before anything is persisted | the request was refused before anything was stored | `DEFENDED` |
| `G2-H` | mandatory | cancellation | cancel a run that is waiting for a tool and let the wait return | the run reaches CANCELLED and makes no further call | the cancelled run made no further call and reached a terminal state | `DEFENDED` |
| `G2-I` | mandatory | cancellation | request cancellation and execute a run whose agent would loop for ever | no model call is made after the cancellation | no model call was made once cancellation was requested | `DEFENDED` |
| `G2-J` | mandatory | event log | append every recorded event a second time through the real store contract | the log is unchanged and its sequence stays monotonic and unique | 6 events, replayed, stayed 6 in sequence order | `DEFENDED` |
| `G2-K` | mandatory | privacy | append an event payload carrying each forbidden key, including nested | every one is refused rather than truncated | every forbidden payload key was refused, at any depth | `DEFENDED` |
| `G2-L` | mandatory | prompt separation | assemble a context and build a real turn from a task that claims to override the protocol | the task stays in the user channel and never reaches the instructions | the task stayed in the user channel, inside its labelled block | `DEFENDED` |
| `G2-M` | mandatory | isolation | execute two real engines concurrently with different tasks | neither run sees the other's task, events or result | two concurrent runs shared no task, no event and no result | `DEFENDED` |
| `G2-N` | mandatory | provider boundary | read every module of the installed runtime package and look for a provider or an adapter | no module names a provider or imports the gateway implementation | 18 runtime modules name no provider and import no adapter, and the identical scan detects a module that does both | `DEFENDED` |
| `G2-O` | mandatory | gateway boundary | close the model port and execute a real run | no inference happens at all and the run fails with a gateway error | closing the one port stopped every inference the run could make | `DEFENDED` |
| `G2-P` | mandatory | observability | record every instrument with a task as the label value | the published labels are the permitted set and every value is bounded | labels are ['agent', 'error_type', 'service', 'team'] and every value is bounded, so content cannot become a time series | `DEFENDED` |
| `G2-Q` | mandatory | limits | run real engines with payloads far above the configured limits | each one is refused before anything is stored or sent | 3 oversized payloads were refused before anything was stored | `DEFENDED` |
| `G2-R` | mandatory | budgets | construct budgets with zero, negative and absurd limits | every one is refused at validation | every zero, negative and absurd limit was refused at validation | `DEFENDED` |
| `G2-S` | mandatory | budgets | record an absent usage against a run with a token budget | the budget becomes unenforceable and says so, rather than counting zero | an absent usage made the token budget unenforceable and said so | `DEFENDED` |
| `G2-T` | mandatory | gate scope | plant an executor in services/sandbox and run the real scope control | the control refuses the delivery, naming the reserved path | the scope control refused it: services/sandbox is reserved for GATE 3 but carries executor.py | `DEFENDED` |
| `G2-U` | mandatory | durability | scan the real workflow for a clock, a random value, a database or a network call, and run the identical scan over a module that has them | the workflow has none and the scan detects the mutated module | the workflow reads no clock, no randomness and no database, and the check detects a module that does (random, random.random, time.time) | `DEFENDED` |
| `G2-V` | mandatory | delivery assurance | plant a failing test in the agent runtime suite on disk and run the real gate | the gate builds the image first and reports the failure | the gate rebuilt and failed on the planted test: [iacode] AGENT_RUNTIME_TESTS=FAIL | `DEFENDED` |

## What each attack means

### G2-A — A finished run is asked to run again.

- Mutation: apply every transition out of SUCCEEDED, FAILED and CANCELLED through the real state machine
- Expected defence: every one is refused and a terminal run stays terminal
- Observed: every terminal move was refused; 36 forbidden transitions in total
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/states.py`, `test:RunStateMachineTests`

### G2-B — An agent that never finishes, against a run that must stop.

- Mutation: run a real engine with an agent that answers MESSAGE for ever
- Expected defence: the run ends with BUDGET_EXCEEDED at the configured turn limit
- Observed: the run stopped after 3 turn(s) with BUDGET_EXCEEDED
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`, `test:test_budget_exhaustion_ends_the_run`

### G2-C — An agent that answers with rubbish for ever.

- Mutation: run a real engine with a model that never produces a valid envelope
- Expected defence: one repair is attempted and the second refusal ends the run
- Observed: one repair was attempted and the second refusal ended the run
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `test:test_two_invalid_outputs_fail_the_run`

### G2-D — A repair that is not charged makes one turn cost two invisibly.

- Mutation: run a turn that needs a repair and read the ledger
- Expected defence: the repair is counted as a model call like any other
- Observed: the repair was charged like any other call
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_repair_counts_against_the_budget`

### G2-E — Fourteen shapes of nearly-right output.

- Mutation: parse every one of them with the real parser
- Expected defence: none is read as an answer
- Observed: all 14 malformed outputs were refused
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `test:test_invalid_envelope_is_not_accepted_silently`

### G2-F — An agent asks for a shell, with a command that would destroy the machine.

- Mutation: run a real engine whose agent requests shell.exec with a destructive command
- Expected defence: the request is stored as data, the run pauses, and nothing executes
- Observed: the hostile command was stored verbatim as data, the run paused, and nothing in the engine can execute anything
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:ToolExecutionBoundaryTests`

### G2-G — An agent asks for a tool its profile does not permit.

- Mutation: run a real engine whose agent requests a tool outside its allowed actions
- Expected defence: the request is refused before anything is persisted
- Observed: the request was refused before anything was stored
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/profiles.py`, `test:test_tool_request_outside_allowed_actions_is_refused`

### G2-H — A cancelled run is woken by a tool result.

- Mutation: cancel a run that is waiting for a tool and let the wait return
- Expected defence: the run reaches CANCELLED and makes no further call
- Observed: the cancelled run made no further call and reached a terminal state
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_cancel_while_waiting_for_tool`

### G2-I — A cancelled run keeps calling the model.

- Mutation: request cancellation and execute a run whose agent would loop for ever
- Expected defence: no model call is made after the cancellation
- Observed: no model call was made once cancellation was requested
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_no_model_call_after_cancellation`

### G2-J — The history is replayed to forge extra events.

- Mutation: append every recorded event a second time through the real store contract
- Expected defence: the log is unchanged and its sequence stays monotonic and unique
- Observed: 6 events, replayed, stayed 6 in sequence order
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`, `test:test_duplicate_append_does_not_duplicate_the_event`

### G2-K — A prompt, a transcript or a credential is written into the run's history.

- Mutation: append an event payload carrying each forbidden key, including nested
- Expected defence: every one is refused rather than truncated
- Observed: every forbidden payload key was refused, at any depth
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/events.py`, `test:test_event_payload_carries_no_private_reasoning`

### G2-L — A task written to look like a platform instruction.

- Mutation: assemble a context and build a real turn from a task that claims to override the protocol
- Expected defence: the task stays in the user channel and never reaches the instructions
- Observed: the task stayed in the user channel, inside its labelled block
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/context.py`, `test:test_task_never_enters_the_system_channel`

### G2-M — Two runs at once, reading each other's task and history.

- Mutation: execute two real engines concurrently with different tasks
- Expected defence: neither run sees the other's task, events or result
- Observed: two concurrent runs shared no task, no event and no result
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:ConcurrentRunIsolationTests`

### G2-N — The runtime reaches a provider directly.

- Mutation: read every module of the installed runtime package and look for a provider or an adapter
- Expected defence: no module names a provider or imports the gateway implementation
- Observed: 18 runtime modules name no provider and import no adapter, and the identical scan detects a module that does both
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`, `test:test_no_provider_specific_name_escapes_the_runtime`

### G2-O — An inference escapes the one port the runtime has.

- Mutation: close the model port and execute a real run
- Expected defence: no inference happens at all and the run fails with a gateway error
- Observed: closing the one port stopped every inference the run could make
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/ports.py`, `test:test_every_inference_goes_through_the_gateway`

### G2-P — A task becomes a Prometheus label.

- Mutation: record every instrument with a task as the label value
- Expected defence: the published labels are the permitted set and every value is bounded
- Observed: labels are ['agent', 'error_type', 'service', 'team'] and every value is bounded, so content cannot become a time series
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/telemetry.py`, `test:test_no_metric_label_carries_content`

### G2-Q — An unbounded task, tool argument set and agent answer.

- Mutation: run real engines with payloads far above the configured limits
- Expected defence: each one is refused before anything is stored or sent
- Observed: 3 oversized payloads were refused before anything was stored
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/limits.py`, `test:PayloadLimitTests`

### G2-R — A run configured with no bound at all.

- Mutation: construct budgets with zero, negative and absurd limits
- Expected defence: every one is refused at validation
- Observed: every zero, negative and absurd limit was refused at validation
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`, `test:test_absurd_budget_is_refused`

### G2-S — A token budget enforced against usage the provider never reported.

- Mutation: record an absent usage against a run with a token budget
- Expected defence: the budget becomes unenforceable and says so, rather than counting zero
- Observed: an absent usage made the token budget unenforceable and said so
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`, `test:test_token_budget_is_unenforceable_without_usage`

### G2-T — The sandbox is started early, because the tool request is already there.

- Mutation: plant an executor in services/sandbox and run the real scope control
- Expected defence: the control refuses the delivery, naming the reserved path
- Observed: the scope control refused it: services/sandbox is reserved for GATE 3 but carries executor.py
- Evidence: `file:.iacode/policies/gate-scope.json`, `test:Gate2ScopeTests`

### G2-U — Workflow code that cannot be replayed.

- Mutation: scan the real workflow for a clock, a random value, a database or a network call, and run the identical scan over a module that has them
- Expected defence: the workflow has none and the scan detects the mutated module
- Observed: the workflow reads no clock, no randomness and no database, and the check detects a module that does (random, random.random, time.time)
- Evidence: `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `test:WorkflowDeterminismTests`

### G2-V — The new mandatory gate measures an image nobody rebuilt.

- Mutation: plant a failing test in the agent runtime suite on disk and run the real gate
- Expected defence: the gate builds the image first and reports the failure
- Observed: the gate rebuilt and failed on the planted test: [iacode] AGENT_RUNTIME_TESTS=FAIL
- Evidence: `file:scripts/iacode/gates/agent_runtime_tests.py`, `file:scripts/iacode/compose.py`
