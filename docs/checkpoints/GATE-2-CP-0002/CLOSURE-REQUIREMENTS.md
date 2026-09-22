# Closure Requirements - GATE-2-CP-0002

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/GATE-2-CHECKLIST.md, the canonical GATE-2 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

## Requirements

| ID | Source | Anchor | Mandatory | Implementation | Final | Description |
|---|---|---|---|---|---|---|
| `REQ-0001` | GATE_SPECIFICATION | `canonical:GATE-2#1.1` | yes | `COMPLETE` | `COMPLETE` | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. |
| `REQ-0002` | GATE_SPECIFICATION | `canonical:GATE-2#1.2` | yes | `COMPLETE` | `COMPLETE` | The closed mandatory gate registry carries every executable gate this Gate introduces. |
| `REQ-0003` | GATE_SPECIFICATION | `canonical:GATE-2#1.3` | yes | `COMPLETE` | `COMPLETE` | Every test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence. |
| `REQ-0004` | GATE_SPECIFICATION | `canonical:GATE-2#1.4` | yes | `COMPLETE` | `COMPLETE` | The internal Red Team battery of this Gate is executable, scoped to the Agent Runtime, and records a null-mutation control. |
| `REQ-0005` | GATE_SPECIFICATION | `canonical:GATE-2#1.5` | yes | `COMPLETE` | `COMPLETE` | The reservation of the agent definition directory is consumed by the Gate that owns it, and the scope registry keeps constraining every path still owned by a later Gate. |
| `REQ-0006` | GATE_SPECIFICATION | `canonical:GATE-2#1.6` | yes | `COMPLETE` | `COMPLETE` | One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack. |
| `REQ-0007` | GATE_SPECIFICATION | `canonical:GATE-2#2.1` | yes | `COMPLETE` | `COMPLETE` | The agent runtime is a provider-neutral library with its own contracts, and the boundary decision is recorded rather than implied. |
| `REQ-0008` | GATE_SPECIFICATION | `canonical:GATE-2#2.2` | yes | `COMPLETE` | `COMPLETE` | The runtime declares the persistence, model and clock ports it needs and imports no web application module, so the dependency points inward. |
| `REQ-0009` | GATE_SPECIFICATION | `canonical:GATE-2#2.3` | yes | `COMPLETE` | `COMPLETE` | The runtime reaches a model only through the Model Gateway contract: no provider adapter, no provider client, no provider address and no credential exists inside it. |
| `REQ-0010` | GATE_SPECIFICATION | `canonical:GATE-2#2.4` | yes | `COMPLETE` | `COMPLETE` | The runtime owns no retry policy, circuit breaker, fallback chain or provider selection of its own; those belong to the gateway. |
| `REQ-0011` | GATE_SPECIFICATION | `canonical:GATE-2#2.5` | yes | `COMPLETE` | `COMPLETE` | No later-Gate capability — tool execution, sandboxing, retrieval, experience storage, quality scoring or training — is implemented, simulated or faked here. |
| `REQ-0012` | GATE_SPECIFICATION | `canonical:GATE-2#2.6` | yes | `COMPLETE` | `COMPLETE` | The persistence layer is a shared package the API and the worker both depend on, so one authoritative schema definition serves both processes. |
| `REQ-0013` | GATE_SPECIFICATION | `canonical:GATE-2#2.7` | yes | `COMPLETE` | `COMPLETE` | The agent definition directory stops declaring itself reserved and describes what this Gate delivered. |
| `REQ-0014` | GATE_SPECIFICATION | `canonical:GATE-2#3.1` | yes | `COMPLETE` | `COMPLETE` | This Gate adds its schema through a new migration and edits no migration that has already been applied. |
| `REQ-0015` | GATE_SPECIFICATION | `canonical:GATE-2#3.2` | yes | `COMPLETE` | `COMPLETE` | The existing task, run, agent and agent-run entities are evolved rather than duplicated; no parallel table is created for a capability an existing table already carries. |
| `REQ-0016` | GATE_SPECIFICATION | `canonical:GATE-2#3.3` | yes | `COMPLETE` | `COMPLETE` | A database created from nothing reaches the head revision by running every migration in order. |
| `REQ-0017` | GATE_SPECIFICATION | `canonical:GATE-2#3.4` | yes | `COMPLETE` | `COMPLETE` | A database at the Gate 1 revision upgrades to this Gate's head without losing the rows it already holds. |
| `REQ-0018` | GATE_SPECIFICATION | `canonical:GATE-2#3.5` | yes | `COMPLETE` | `COMPLETE` | The run state vocabulary the database accepts is derived from one authoritative definition rather than written twice. |
| `REQ-0019` | GATE_SPECIFICATION | `canonical:GATE-2#3.6` | yes | `COMPLETE` | `COMPLETE` | The run event log is append-only: it carries a creation time, no update time, and no code path rewrites a stored event. |
| `REQ-0020` | GATE_SPECIFICATION | `canonical:GATE-2#3.7` | yes | `COMPLETE` | `COMPLETE` | A tool request and its result are separate persisted rows, and a request can carry at most one result. |
| `REQ-0021` | GATE_SPECIFICATION | `canonical:GATE-2#3.8` | yes | `COMPLETE` | `COMPLETE` | Agent and team profiles are persisted with their version, and a row an operator has customised is not overwritten by a later bootstrap. |
| `REQ-0022` | GATE_SPECIFICATION | `canonical:GATE-2#3.9` | yes | `COMPLETE` | `COMPLETE` | An agent run names the model calls that served it, and aggregate usage is derived from them rather than counted a second time. |
| `REQ-0023` | GATE_SPECIFICATION | `canonical:GATE-2#3.10` | yes | `COMPLETE` | `COMPLETE` | The task content the workflow needs to continue is persisted, and the difference from the gateway's metadata-only record is documented rather than implied. |
| `REQ-0024` | GATE_SPECIFICATION | `canonical:GATE-2#4.1` | yes | `COMPLETE` | `COMPLETE` | The run lifecycle is an explicit state machine over exactly the declared states, and no state exists that the contract does not name. |
| `REQ-0025` | GATE_SPECIFICATION | `canonical:GATE-2#4.2` | yes | `COMPLETE` | `COMPLETE` | A transition happens only when the transition table allows it. |
| `REQ-0026` | GATE_SPECIFICATION | `canonical:GATE-2#4.3` | yes | `COMPLETE` | `COMPLETE` | An impossible transition is refused with a typed error rather than silently applied. |
| `REQ-0027` | GATE_SPECIFICATION | `canonical:GATE-2#4.4` | yes | `COMPLETE` | `COMPLETE` | A terminal state is terminal: no transition leaves `SUCCEEDED`, `FAILED` or `CANCELLED`. |
| `REQ-0028` | GATE_SPECIFICATION | `canonical:GATE-2#4.5` | yes | `COMPLETE` | `COMPLETE` | Re-running a task creates a new run; a terminal run is never resumed in place. |
| `REQ-0029` | GATE_SPECIFICATION | `canonical:GATE-2#4.6` | yes | `COMPLETE` | `COMPLETE` | Every accepted state change records an event, so the history explains the state. |
| `REQ-0030` | GATE_SPECIFICATION | `canonical:GATE-2#4.7` | yes | `COMPLETE` | `COMPLETE` | The state machine is one definition, used by the API, the workflow and the store alike. |
| `REQ-0031` | GATE_SPECIFICATION | `canonical:GATE-2#5.1` | yes | `COMPLETE` | `COMPLETE` | The event vocabulary covers run creation and start, agent start and completion, model call start and completion, tool request and tool result, and the three terminal outcomes. |
| `REQ-0032` | GATE_SPECIFICATION | `canonical:GATE-2#5.2` | yes | `COMPLETE` | `COMPLETE` | Events of one run carry a monotonic sequence number assigned by the store, so their order is deterministic. |
| `REQ-0033` | GATE_SPECIFICATION | `canonical:GATE-2#5.3` | yes | `COMPLETE` | `COMPLETE` | A recorded event is never rewritten; a correction is a new event. |
| `REQ-0034` | GATE_SPECIFICATION | `canonical:GATE-2#5.4` | yes | `COMPLETE` | `COMPLETE` | A retried append does not create a second event for the same occurrence. |
| `REQ-0035` | GATE_SPECIFICATION | `canonical:GATE-2#5.5` | yes | `COMPLETE` | `COMPLETE` | An event payload carries a short verifiable summary and never a model's private reasoning or a raw prompt. |
| `REQ-0036` | GATE_SPECIFICATION | `canonical:GATE-2#5.6` | yes | `COMPLETE` | `COMPLETE` | An event payload larger than the configured bound is refused rather than persisted. |
| `REQ-0037` | GATE_SPECIFICATION | `canonical:GATE-2#6.1` | yes | `COMPLETE` | `COMPLETE` | An agent profile is a versioned contract carrying identity, role, description, prompt template, default route, turn limit, permitted actions and an enabled flag. |
| `REQ-0038` | GATE_SPECIFICATION | `canonical:GATE-2#6.2` | yes | `COMPLETE` | `COMPLETE` | The builtin profiles are exactly the four this Gate needs to prove the runtime, and no profile exists for a capability the Gate does not exercise. |
| `REQ-0039` | GATE_SPECIFICATION | `canonical:GATE-2#6.3` | yes | `COMPLETE` | `COMPLETE` | Profiles are loaded from the repository, enumerable through the runtime, and validated when they are loaded. |
| `REQ-0040` | GATE_SPECIFICATION | `canonical:GATE-2#6.4` | yes | `COMPLETE` | `COMPLETE` | Loading the builtin profiles is idempotent: running it twice changes nothing the second time. |
| `REQ-0041` | GATE_SPECIFICATION | `canonical:GATE-2#6.5` | yes | `COMPLETE` | `COMPLETE` | Prompt templates are versioned files under the agent definition directory, not strings concatenated across the code. |
| `REQ-0042` | GATE_SPECIFICATION | `canonical:GATE-2#6.6` | yes | `COMPLETE` | `COMPLETE` | An agent run records the profile version and the prompt template hash that produced it, so its behaviour can be reproduced. |
| `REQ-0043` | GATE_SPECIFICATION | `canonical:GATE-2#6.7` | yes | `COMPLETE` | `COMPLETE` | Prompt assembly keeps runtime instructions, role instructions, task content and tool results in separate labelled channels. |
| `REQ-0044` | GATE_SPECIFICATION | `canonical:GATE-2#6.8` | yes | `COMPLETE` | `COMPLETE` | The user's task is carried in the user channel and is never concatenated into the system instructions. |
| `REQ-0045` | GATE_SPECIFICATION | `canonical:GATE-2#6.9` | yes | `COMPLETE` | `COMPLETE` | Every executed step records run, task, agent, agent run, timestamps, model call identity, provider, model, template version and result status — and no private reasoning. |
| `REQ-0046` | GATE_SPECIFICATION | `canonical:GATE-2#6.10` | yes | `COMPLETE` | `COMPLETE` | A profile declares the actions it may request, and a tool request outside that set is refused instead of persisted. |
| `REQ-0047` | GATE_SPECIFICATION | `canonical:GATE-2#7.1` | yes | `COMPLETE` | `COMPLETE` | A team profile is a versioned, ordered list of stages, each naming an agent profile, its input mapping and the name of its output. |
| `REQ-0048` | GATE_SPECIFICATION | `canonical:GATE-2#7.2` | yes | `COMPLETE` | `COMPLETE` | Two builtin teams exist: one single-agent and one two-stage planner and reviewer. |
| `REQ-0049` | GATE_SPECIFICATION | `canonical:GATE-2#7.3` | yes | `COMPLETE` | `COMPLETE` | Team composition is configuration. Nothing in this Gate invents a team, and no model decides which agents run. |
| `REQ-0050` | GATE_SPECIFICATION | `canonical:GATE-2#7.4` | yes | `COMPLETE` | `COMPLETE` | Stages execute in the order the profile declares, and each stage's output becomes explicit, named context for the next. |
| `REQ-0051` | GATE_SPECIFICATION | `canonical:GATE-2#7.5` | yes | `COMPLETE` | `COMPLETE` | A previous stage's output reaches the next stage as a labelled artifact and never as an instruction. |
| `REQ-0052` | GATE_SPECIFICATION | `canonical:GATE-2#7.6` | yes | `COMPLETE` | `COMPLETE` | A team run produces one agent run per stage, in order, with separate outputs. |
| `REQ-0053` | GATE_SPECIFICATION | `canonical:GATE-2#8.1` | yes | `COMPLETE` | `COMPLETE` | A turn produces exactly one of a final answer, a message or a tool request. |
| `REQ-0054` | GATE_SPECIFICATION | `canonical:GATE-2#8.2` | yes | `COMPLETE` | `COMPLETE` | The envelope carries an explicit version and is documented, so a consumer can detect an incompatible change instead of discovering one. |
| `REQ-0055` | GATE_SPECIFICATION | `canonical:GATE-2#8.3` | yes | `COMPLETE` | `COMPLETE` | The parser is strict: an output that does not conform is rejected rather than partially accepted. |
| `REQ-0056` | GATE_SPECIFICATION | `canonical:GATE-2#8.4` | yes | `COMPLETE` | `COMPLETE` | Native structured output is requested only from a model whose capability is known; otherwise the envelope is validated JSON text produced by the same contract. |
| `REQ-0057` | GATE_SPECIFICATION | `canonical:GATE-2#8.5` | yes | `COMPLETE` | `COMPLETE` | No capability is asserted on a model's behalf to make a turn work. |
| `REQ-0058` | GATE_SPECIFICATION | `canonical:GATE-2#8.6` | yes | `COMPLETE` | `COMPLETE` | At most one repair attempt follows an invalid turn, and it happens through the Model Gateway like any other call. |
| `REQ-0059` | GATE_SPECIFICATION | `canonical:GATE-2#8.7` | yes | `COMPLETE` | `COMPLETE` | A repair call counts against the run's budget and is recorded as a repair rather than hidden. |
| `REQ-0060` | GATE_SPECIFICATION | `canonical:GATE-2#8.8` | yes | `COMPLETE` | `COMPLETE` | A second invalid output ends the run with a normalised invalid-output error rather than looping. |
| `REQ-0061` | GATE_SPECIFICATION | `canonical:GATE-2#9.1` | yes | `COMPLETE` | `COMPLETE` | Every inference this Gate performs travels through the Model Gateway client port and through nothing else. |
| `REQ-0062` | GATE_SPECIFICATION | `canonical:GATE-2#9.2` | yes | `COMPLETE` | `COMPLETE` | A run may carry a route alias or an explicit model, and the gateway decides whether it can be served. |
| `REQ-0063` | GATE_SPECIFICATION | `canonical:GATE-2#9.3` | yes | `COMPLETE` | `COMPLETE` | A run that names neither uses the configured default, and the runtime never picks a provider itself. |
| `REQ-0064` | GATE_SPECIFICATION | `canonical:GATE-2#9.4` | yes | `COMPLETE` | `COMPLETE` | Every model call is attributed to the agent run that caused it. |
| `REQ-0065` | GATE_SPECIFICATION | `canonical:GATE-2#9.5` | yes | `COMPLETE` | `COMPLETE` | A definitive gateway failure ends the run with a normalised error; the run never stays `RUNNING` for ever. |
| `REQ-0066` | GATE_SPECIFICATION | `canonical:GATE-2#9.6` | yes | `COMPLETE` | `COMPLETE` | The runtime does not repeat a whole model call the gateway has already exhausted its own retries on. |
| `REQ-0067` | GATE_SPECIFICATION | `canonical:GATE-2#9.7` | yes | `COMPLETE` | `COMPLETE` | Cost the gateway does not know is reported as unknown and never as zero. |
| `REQ-0068` | GATE_SPECIFICATION | `canonical:GATE-2#9.8` | yes | `COMPLETE` | `COMPLETE` | A request the model's context cannot hold produces an explicit error rather than a silent truncation of the task. |
| `REQ-0069` | GATE_SPECIFICATION | `canonical:GATE-2#10.1` | yes | `COMPLETE` | `COMPLETE` | A tool request is a persisted contract carrying identity, run, agent, name, arguments, creation time and a status from the declared vocabulary. |
| `REQ-0070` | GATE_SPECIFICATION | `canonical:GATE-2#10.2` | yes | `COMPLETE` | `COMPLETE` | A tool result is a contract carrying the request it answers, a status, an output, an error and metadata. |
| `REQ-0071` | GATE_SPECIFICATION | `canonical:GATE-2#10.3` | yes | `COMPLETE` | `COMPLETE` | A tool request turn persists the request, records the event and moves the run to `WAITING_FOR_TOOL`. |
| `REQ-0072` | GATE_SPECIFICATION | `canonical:GATE-2#10.4` | yes | `COMPLETE` | `COMPLETE` | A paused run performs no further model call until a result arrives. |
| `REQ-0073` | GATE_SPECIFICATION | `canonical:GATE-2#10.5` | yes | `COMPLETE` | `COMPLETE` | A tool name is data. Nothing in this Gate interprets it as a command, a path or an executable. |
| `REQ-0074` | GATE_SPECIFICATION | `canonical:GATE-2#10.6` | yes | `COMPLETE` | `COMPLETE` | A matching tool result is persisted, recorded as an event and resumes the run. |
| `REQ-0075` | GATE_SPECIFICATION | `canonical:GATE-2#10.7` | yes | `COMPLETE` | `COMPLETE` | The same tool result delivered twice resolves the request once and resumes the run once. |
| `REQ-0076` | GATE_SPECIFICATION | `canonical:GATE-2#10.8` | yes | `COMPLETE` | `COMPLETE` | A tool result naming another run or an unknown request is refused. |
| `REQ-0077` | GATE_SPECIFICATION | `canonical:GATE-2#10.9` | yes | `COMPLETE` | `COMPLETE` | A tool result that arrives after the run reached a terminal state is refused. |
| `REQ-0078` | GATE_SPECIFICATION | `canonical:GATE-2#10.10` | yes | `COMPLETE` | `COMPLETE` | Waiting for a tool has its own configurable timeout, separate from the run deadline, and reaching it ends the run explicitly. |
| `REQ-0079` | GATE_SPECIFICATION | `canonical:GATE-2#10.11` | yes | `COMPLETE` | `COMPLETE` | An automated control proves the runtime boundary contains no process, shell, filesystem-mutating or version-control execution path, and the control is a property of the boundary rather than of one file. |
| `REQ-0080` | GATE_SPECIFICATION | `canonical:GATE-2#10.12` | yes | `COMPLETE` | `COMPLETE` | The division of labour with the next Gate is documented: this Gate persists and pauses, the next one executes. |
| `REQ-0081` | GATE_SPECIFICATION | `canonical:GATE-2#11.1` | yes | `COMPLETE` | `COMPLETE` | Every run carries a maximum turn count, a maximum model-call count and a wall-clock deadline. |
| `REQ-0082` | GATE_SPECIFICATION | `canonical:GATE-2#11.2` | yes | `COMPLETE` | `COMPLETE` | A token budget is enforced when the provider reports usage and recorded as unenforceable when it does not, rather than invented. |
| `REQ-0083` | GATE_SPECIFICATION | `canonical:GATE-2#11.3` | yes | `COMPLETE` | `COMPLETE` | A budget that is zero, negative or absurd is refused when the run is validated. |
| `REQ-0084` | GATE_SPECIFICATION | `canonical:GATE-2#11.4` | yes | `COMPLETE` | `COMPLETE` | Reaching any budget ends the run with a normalised budget error. |
| `REQ-0085` | GATE_SPECIFICATION | `canonical:GATE-2#11.5` | yes | `COMPLETE` | `COMPLETE` | No model call happens after a budget is exhausted. |
| `REQ-0086` | GATE_SPECIFICATION | `canonical:GATE-2#11.6` | yes | `COMPLETE` | `COMPLETE` | Every call to the gateway counts against the model-call budget, including a repair. |
| `REQ-0087` | GATE_SPECIFICATION | `canonical:GATE-2#11.7` | yes | `COMPLETE` | `COMPLETE` | A run cannot execute an unbounded number of turns, and a run that outlives its deadline is ended rather than left running. |
| `REQ-0088` | GATE_SPECIFICATION | `canonical:GATE-2#12.1` | yes | `COMPLETE` | `COMPLETE` | A run can be cancelled through the API while it is executing. |
| `REQ-0089` | GATE_SPECIFICATION | `canonical:GATE-2#12.2` | yes | `COMPLETE` | `COMPLETE` | Cancellation reaches the durable workflow and stops it rather than only marking a row. |
| `REQ-0090` | GATE_SPECIFICATION | `canonical:GATE-2#12.3` | yes | `COMPLETE` | `COMPLETE` | A cancelled run is terminal and records the cancellation event. |
| `REQ-0091` | GATE_SPECIFICATION | `canonical:GATE-2#12.4` | yes | `COMPLETE` | `COMPLETE` | A run waiting for a tool can be cancelled, and a tool result that arrives afterwards is refused. |
| `REQ-0092` | GATE_SPECIFICATION | `canonical:GATE-2#12.5` | yes | `COMPLETE` | `COMPLETE` | No model call happens after a run is cancelled. |
| `REQ-0093` | GATE_SPECIFICATION | `canonical:GATE-2#13.1` | yes | `COMPLETE` | `COMPLETE` | Temporal is the durable execution engine, and no second scheduler or background orchestration loop competes with it. |
| `REQ-0094` | GATE_SPECIFICATION | `canonical:GATE-2#13.2` | yes | `COMPLETE` | `COMPLETE` | Workflow code stays deterministic: every external effect — model call, persistence, notification — happens in an activity. |
| `REQ-0095` | GATE_SPECIFICATION | `canonical:GATE-2#13.3` | yes | `COMPLETE` | `COMPLETE` | A worker restart while a run waits for a tool preserves the run, and the run resumes and completes when the result arrives. |
| `REQ-0096` | GATE_SPECIFICATION | `canonical:GATE-2#13.4` | yes | `COMPLETE` | `COMPLETE` | An API restart does not lose a run in progress: the state lives in the store and in the workflow, never in process memory. |
| `REQ-0097` | GATE_SPECIFICATION | `canonical:GATE-2#13.5` | yes | `COMPLETE` | `COMPLETE` | The workflow receives a frozen plan, so editing a profile while a run executes cannot change what that run is doing. |
| `REQ-0098` | GATE_SPECIFICATION | `canonical:GATE-2#14.1` | yes | `COMPLETE` | `COMPLETE` | A versioned API creates a run, reads it, lists runs, streams its events, cancels it and accepts a tool result. |
| `REQ-0099` | GATE_SPECIFICATION | `canonical:GATE-2#14.2` | yes | `COMPLETE` | `COMPLETE` | Creation answers immediately with the run identifier, its state and its creation time, without holding the request open for the run. |
| `REQ-0100` | GATE_SPECIFICATION | `canonical:GATE-2#14.3` | yes | `COMPLETE` | `COMPLETE` | Creation accepts no provider credential and no provider address. |
| `REQ-0101` | GATE_SPECIFICATION | `canonical:GATE-2#14.4` | yes | `COMPLETE` | `COMPLETE` | A run's status carries its state, current stage, timestamps, budget consumption, final result when there is one and error summary when there is one. |
| `REQ-0102` | GATE_SPECIFICATION | `canonical:GATE-2#14.5` | yes | `COMPLETE` | `COMPLETE` | A failed run answers with an error type, a safe message, the stage that failed and the correlation identifier, and never with a traceback. |
| `REQ-0103` | GATE_SPECIFICATION | `canonical:GATE-2#14.6` | yes | `COMPLETE` | `COMPLETE` | Run events are readable as a page and as a live stream. |
| `REQ-0104` | GATE_SPECIFICATION | `canonical:GATE-2#14.7` | yes | `COMPLETE` | `COMPLETE` | A consumer that reconnects with a cursor receives exactly the events that follow it. |
| `REQ-0105` | GATE_SPECIFICATION | `canonical:GATE-2#14.8` | yes | `COMPLETE` | `COMPLETE` | Reconnecting or retrying a read creates no new event. |
| `REQ-0106` | GATE_SPECIFICATION | `canonical:GATE-2#14.9` | yes | `COMPLETE` | `COMPLETE` | The available agent profiles and team profiles are enumerable through the API. |
| `REQ-0107` | GATE_SPECIFICATION | `canonical:GATE-2#14.10` | yes | `COMPLETE` | `COMPLETE` | Task input size is bounded by configuration and an oversized task is refused rather than stored. |
| `REQ-0108` | GATE_SPECIFICATION | `canonical:GATE-2#15.1` | yes | `COMPLETE` | `COMPLETE` | A creation request repeated with the same idempotency key returns the run the first one created. |
| `REQ-0109` | GATE_SPECIFICATION | `canonical:GATE-2#15.2` | yes | `COMPLETE` | `COMPLETE` | A creation request with a different key creates a different run. |
| `REQ-0110` | GATE_SPECIFICATION | `canonical:GATE-2#15.3` | yes | `COMPLETE` | `COMPLETE` | Two runs execute at the same time without sharing state, context or events. |
| `REQ-0111` | GATE_SPECIFICATION | `canonical:GATE-2#15.4` | yes | `COMPLETE` | `COMPLETE` | One task may carry two independent runs with separate results and separate events. |
| `REQ-0112` | GATE_SPECIFICATION | `canonical:GATE-2#15.5` | yes | `COMPLETE` | `COMPLETE` | Identifiers use the strategy the repository already defines rather than a second format. |
| `REQ-0113` | GATE_SPECIFICATION | `canonical:GATE-2#16.1` | yes | `COMPLETE` | `COMPLETE` | The runtime publishes the declared instruments for runs, turns, failures, waiting runs, budget exhaustions and cancellations. |
| `REQ-0114` | GATE_SPECIFICATION | `canonical:GATE-2#16.2` | yes | `COMPLETE` | `COMPLETE` | No metric label carries a task, a prompt, a response or tool arguments, and every label is low cardinality. |
| `REQ-0115` | GATE_SPECIFICATION | `canonical:GATE-2#16.3` | yes | `COMPLETE` | `COMPLETE` | Structured logs carry correlation, task, run, agent, agent run, stage, event type, model call and status when those exist. |
| `REQ-0116` | GATE_SPECIFICATION | `canonical:GATE-2#16.4` | yes | `COMPLETE` | `COMPLETE` | No log record carries the whole task by default, and a secret nested inside a payload is redacted. |
| `REQ-0117` | GATE_SPECIFICATION | `canonical:GATE-2#17.1` | yes | `COMPLETE` | `COMPLETE` | An operational page creates a run from a written task, a chosen team and an optional route or model. |
| `REQ-0118` | GATE_SPECIFICATION | `canonical:GATE-2#17.2` | yes | `COMPLETE` | `COMPLETE` | The page follows the run's state and its events as they happen. |
| `REQ-0119` | GATE_SPECIFICATION | `canonical:GATE-2#17.3` | yes | `COMPLETE` | `COMPLETE` | The page shows the final result of a successful run and the safe failure summary of a failed one. |
| `REQ-0120` | GATE_SPECIFICATION | `canonical:GATE-2#17.4` | yes | `COMPLETE` | `COMPLETE` | The page can cancel a run that is executing. |
| `REQ-0121` | GATE_SPECIFICATION | `canonical:GATE-2#17.5` | yes | `COMPLETE` | `COMPLETE` | A run waiting for a tool is shown as waiting, with the tool name and the pending status, and the page offers nothing that would execute it. |
| `REQ-0122` | GATE_SPECIFICATION | `canonical:GATE-2#17.6` | yes | `COMPLETE` | `COMPLETE` | Model output is rendered as text, never as trusted markup. |
| `REQ-0123` | GATE_SPECIFICATION | `canonical:GATE-2#18.1` | yes | `COMPLETE` | `COMPLETE` | No provider credential reaches the runtime, the store, a log record, a metric or the browser. |
| `REQ-0124` | GATE_SPECIFICATION | `canonical:GATE-2#18.2` | yes | `COMPLETE` | `COMPLETE` | Tool arguments, agent output and tool results are bounded by configuration, and an oversized payload is refused. |
| `REQ-0125` | GATE_SPECIFICATION | `canonical:GATE-2#18.3` | yes | `COMPLETE` | `COMPLETE` | Nothing this Gate persists becomes training data: rights default to denial and no run, event or result is marked otherwise. |
| `REQ-0126` | GATE_SPECIFICATION | `canonical:GATE-2#18.4` | yes | `COMPLETE` | `COMPLETE` | The runtime asks for no private reasoning and stores none; what it keeps are short verifiable summaries. |
| `REQ-0127` | GATE_SPECIFICATION | `canonical:GATE-2#19.1` | yes | `COMPLETE` | `COMPLETE` | A single-agent run executes live, through the Model Gateway, against the configured provider, and succeeds. |
| `REQ-0128` | GATE_SPECIFICATION | `canonical:GATE-2#19.2` | yes | `COMPLETE` | `COMPLETE` | A planner and reviewer run executes live, in order, with separate outputs and the reviewer receiving the planner's output. |
| `REQ-0129` | GATE_SPECIFICATION | `canonical:GATE-2#19.3` | yes | `COMPLETE` | `COMPLETE` | The live check uses an explicitly configured model and fails clearly when that model is not in the catalog, rather than substituting one. |
| `REQ-0130` | GATE_SPECIFICATION | `canonical:GATE-2#19.4` | yes | `COMPLETE` | `COMPLETE` | The live check reports `BLOCKED` rather than `FAIL` when the local configuration carries no credential, and names the variable that is missing. |
| `REQ-0131` | GATE_SPECIFICATION | `canonical:GATE-2#19.5` | yes | `COMPLETE` | `COMPLETE` | The live evidence records model provenance — provider, model, endpoint, model call identity — and no prompt or completion. |
| `REQ-0132` | GATE_SPECIFICATION | `canonical:GATE-2#20.1` | yes | `COMPLETE` | `COMPLETE` | The repository's one verification command covers this Gate, in its targeted and its full mode. |
| `REQ-0133` | GATE_SPECIFICATION | `canonical:GATE-2#20.2` | yes | `COMPLETE` | `COMPLETE` | A runbook documents starting the runtime, creating a run, following it, cancelling it, tool requests and results, budgets, the live smoke and troubleshooting. |
| `REQ-0134` | GATE_SPECIFICATION | `canonical:GATE-2#20.3` | yes | `COMPLETE` | `COMPLETE` | The architecture, development, version and entry documents describe what this Gate delivered rather than what was planned. |
| `REQ-0135` | GATE_SPECIFICATION | `canonical:GATE-2#20.4` | yes | `COMPLETE` | `COMPLETE` | The structural decisions of this Gate are recorded as ADRs. |
| `REQ-0136` | GATE_SPECIFICATION | `canonical:GATE-2#20.5` | yes | `COMPLETE` | `COMPLETE` | The Gate produces its retrospective from the canonical template. |
| `REQ-0137` | GATE_SPECIFICATION | `canonical:GATE-2#20.6` | yes | `COMPLETE` | `COMPLETE` | The Gate closes at the project's own internal verdict and starts no part of the Gate that follows it. |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | yes | `COMPLETE` | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | yes | `COMPLETE` | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | yes | `COMPLETE` | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | yes | `COMPLETE` | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | yes | `COMPLETE` | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | yes | `COMPLETE` | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | yes | `COMPLETE` | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | yes | `COMPLETE` | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | yes | `COMPLETE` | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | yes | `COMPLETE` | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | yes | `COMPLETE` | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | yes | `COMPLETE` | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | no | `COMPLETE` | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | yes | `COMPLETE` | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | yes | `COMPLETE` | `COMPLETE` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | yes | `COMPLETE` | `COMPLETE` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | yes | `COMPLETE` | `COMPLETE` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | yes | `COMPLETE` | `COMPLETE` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | yes | `COMPLETE` | `COMPLETE` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | yes | `COMPLETE` | `COMPLETE` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | yes | `COMPLETE` | `COMPLETE` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | yes | `COMPLETE` | `COMPLETE` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | yes | `COMPLETE` | `COMPLETE` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | yes | `COMPLETE` | `COMPLETE` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | yes | `COMPLETE` | `COMPLETE` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | yes | `COMPLETE` | `COMPLETE` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | yes | `COMPLETE` | `COMPLETE` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | yes | `COMPLETE` | `COMPLETE` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | yes | `COMPLETE` | `COMPLETE` | Verify a required protocol transition must never turn a mandatory gate red |
| `LESSON-REQ-0030` | LESSON | `lesson:LSN-0031` | yes | `COMPLETE` | `COMPLETE` | Verify an empty applicable set is not a missing required set, and a control must tell them apart |
| `LESSON-REQ-0031` | LESSON | `lesson:LSN-0032` | yes | `COMPLETE` | `COMPLETE` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts |
| `LESSON-REQ-0032` | LESSON | `lesson:LSN-0033` | yes | `COMPLETE` | `COMPLETE` | Verify a value bound in middleware is absent in the handlers that run outside it |
| `LESSON-REQ-0033` | LESSON | `lesson:LSN-0034` | yes | `COMPLETE` | `COMPLETE` | Verify re-deriving what the framework already computed diverges from the framework |
| `LESSON-REQ-0034` | LESSON | `lesson:LSN-0035` | yes | `COMPLETE` | `COMPLETE` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work |
| `LESSON-REQ-0035` | LESSON | `lesson:LSN-0036` | yes | `COMPLETE` | `COMPLETE` | Verify a gate that runs inside an image measures the image, not the source |
| `LESSON-REQ-0036` | LESSON | `lesson:LSN-0037` | yes | `COMPLETE` | `COMPLETE` | Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves |
| `LESSON-REQ-0037` | LESSON | `lesson:LSN-0038` | yes | `COMPLETE` | `COMPLETE` | Verify two representations of one concept in one module disagree, and the safer one loses |
| `LESSON-REQ-0038` | LESSON | `lesson:LSN-0039` | yes | `COMPLETE` | `COMPLETE` | Verify a test that writes to the operational database leaves production data behind |
| `LESSON-REQ-0039` | LESSON | `lesson:LSN-0040` | yes | `COMPLETE` | `COMPLETE` | Verify a control that judges sealed history only runs once a successor anchors it |
| `LESSON-REQ-0040` | LESSON | `lesson:LSN-0041` | yes | `COMPLETE` | `COMPLETE` | Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing |
| `LESSON-REQ-0041` | LESSON | `lesson:LSN-0042` | yes | `COMPLETE` | `COMPLETE` | Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone |
| `LESSON-REQ-0042` | LESSON | `lesson:LSN-0043` | yes | `COMPLETE` | `COMPLETE` | Verify a log line is not evidence that another process is ready |
| `LESSON-REQ-0043` | LESSON | `lesson:LSN-0044` | yes | `COMPLETE` | `COMPLETE` | Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module |
| `LESSON-REQ-0044` | LESSON | `lesson:LSN-0045` | yes | `COMPLETE` | `COMPLETE` | Verify a counted test suite must declare its cases statically, because the denominator is read from the source |
| `LESSON-REQ-0045` | LESSON | `lesson:LSN-0046` | yes | `COMPLETE` | `COMPLETE` | Verify a timeout that cancels the task it runs in leaves nothing able to record what happened |
| `LESSON-REQ-0046` | LESSON | `lesson:LSN-0047` | yes | `COMPLETE` | `COMPLETE` | Verify a refusal that misnames the defect spends the only repair on the wrong correction |
| `LESSON-REQ-0047` | LESSON | `lesson:LSN-0048` | yes | `COMPLETE` | `COMPLETE` | Verify a state and the event that explains it, written in two commits, are written event first |
| `LESSON-REQ-0048` | LESSON | `lesson:LSN-0049` | yes | `COMPLETE` | `COMPLETE` | Verify a metric read the instant after the call that moved it is read before the scrape that carries it |
| `LESSON-REQ-0049` | LESSON | `lesson:LSN-0050` | yes | `COMPLETE` | `COMPLETE` | Verify a checkpoint sealed without naming its own tag cannot be validated from that tag |

## Evidence

### REQ-0001 - canonical:GATE-2#1.1

- Source reference: docs/GATE-2-CHECKLIST.md row 1.1
- Description: A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row.
- Implementation: `file:.iacode/policies/canonical-requirements.json`
- Test: `test:Gate2CanonicalSpecificationTests`
- Negative test: _none_
- Documentation: `file:docs/GATE-2-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0002 - canonical:GATE-2#1.2

- Source reference: docs/GATE-2-CHECKLIST.md row 1.2
- Description: The closed mandatory gate registry carries every executable gate this Gate introduces.
- Implementation: `file:.iacode/policies/quality-gates.json`
- Test: `test:Gate2MandatoryGateTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0003 - canonical:GATE-2#1.3

- Source reference: docs/GATE-2-CHECKLIST.md row 1.3
- Description: Every test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence.
- Implementation: `file:.iacode/policies/test-suites.json`
- Test: `test:Gate2TestSuiteRegistryTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0004 - canonical:GATE-2#1.4

- Source reference: docs/GATE-2-CHECKLIST.md row 1.4
- Description: The internal Red Team battery of this Gate is executable, scoped to the Agent Runtime, and records a null-mutation control.
- Implementation: `file:scripts/development-ledger/gate2_red_team.py`
- Test: `test:Gate2RedTeamHarnessTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0005 - canonical:GATE-2#1.5

- Source reference: docs/GATE-2-CHECKLIST.md row 1.5
- Description: The reservation of the agent definition directory is consumed by the Gate that owns it, and the scope registry keeps constraining every path still owned by a later Gate.
- Implementation: `file:.iacode/policies/gate-scope.json`
- Test: `test:Gate2ScopeTests`
- Negative test: _none_
- Documentation: `file:agents/README.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0006 - canonical:GATE-2#1.6

- Source reference: docs/GATE-2-CHECKLIST.md row 1.6
- Description: One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack.
- Implementation: `file:scripts/iacode/verify.py`
- Test: `test:Gate2VerificationStageTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0007 - canonical:GATE-2#2.1

- Source reference: docs/GATE-2-CHECKLIST.md row 2.1
- Description: The agent runtime is a provider-neutral library with its own contracts, and the boundary decision is recorded rather than implied.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`
- Test: `test:test_agent_runtime_package_is_importable`
- Negative test: _none_
- Documentation: `file:docs/adr/ADR-0020-agent-runtime-boundary.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0008 - canonical:GATE-2#2.2

- Source reference: docs/GATE-2-CHECKLIST.md row 2.2
- Description: The runtime declares the persistence, model and clock ports it needs and imports no web application module, so the dependency points inward.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/ports.py`
- Test: `test:test_agent_runtime_imports_no_application_module`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0009 - canonical:GATE-2#2.3

- Source reference: docs/GATE-2-CHECKLIST.md row 2.3
- Description: The runtime reaches a model only through the Model Gateway contract: no provider adapter, no provider client, no provider address and no credential exists inside it.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`, `file:.iacode/policies/providers.json`
- Test: `test:test_no_provider_specific_name_escapes_the_runtime`, `test:test_runtime_holds_no_provider_address_or_credential`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0010 - canonical:GATE-2#2.4

- Source reference: docs/GATE-2-CHECKLIST.md row 2.4
- Description: The runtime owns no retry policy, circuit breaker, fallback chain or provider selection of its own; those belong to the gateway.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`
- Test: `test:test_runtime_does_not_reimplement_gateway_resilience`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0011 - canonical:GATE-2#2.5

- Source reference: docs/GATE-2-CHECKLIST.md row 2.5
- Description: No later-Gate capability — tool execution, sandboxing, retrieval, experience storage, quality scoring or training — is implemented, simulated or faked here.
- Implementation: _none_
- Test: `test:test_no_future_gate_capability_is_implemented_in_gate_two`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0012 - canonical:GATE-2#2.6

- Source reference: docs/GATE-2-CHECKLIST.md row 2.6
- Description: The persistence layer is a shared package the API and the worker both depend on, so one authoritative schema definition serves both processes.
- Implementation: `file:packages/persistence/src/iacode_persistence/__init__.py`
- Test: `test:test_persistence_package_is_the_single_schema_definition`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0013 - canonical:GATE-2#2.7

- Source reference: docs/GATE-2-CHECKLIST.md row 2.7
- Description: The agent definition directory stops declaring itself reserved and describes what this Gate delivered.
- Implementation: _none_
- Test: `test:test_agents_readme_describes_the_delivery`
- Negative test: _none_
- Documentation: `file:agents/README.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0014 - canonical:GATE-2#3.1

- Source reference: docs/GATE-2-CHECKLIST.md row 3.1
- Description: This Gate adds its schema through a new migration and edits no migration that has already been applied.
- Implementation: `file:apps/api/migrations/versions/0003_agent_runtime.py`
- Test: `test:test_applied_migrations_are_not_edited`, `test:Gate2MigrationTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0015 - canonical:GATE-2#3.2

- Source reference: docs/GATE-2-CHECKLIST.md row 3.2
- Description: The existing task, run, agent and agent-run entities are evolved rather than duplicated; no parallel table is created for a capability an existing table already carries.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `test:test_no_parallel_entity_is_created`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0016 - canonical:GATE-2#3.3

- Source reference: docs/GATE-2-CHECKLIST.md row 3.3
- Description: A database created from nothing reaches the head revision by running every migration in order.
- Implementation: _none_
- Test: `test:test_fresh_database_reaches_head`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0017 - canonical:GATE-2#3.4

- Source reference: docs/GATE-2-CHECKLIST.md row 3.4
- Description: A database at the Gate 1 revision upgrades to this Gate's head without losing the rows it already holds.
- Implementation: `file:apps/api/migrations/versions/0003_agent_runtime.py`
- Test: `test:test_gate1_database_upgrades_to_gate2_head`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0018 - canonical:GATE-2#3.5

- Source reference: docs/GATE-2-CHECKLIST.md row 3.5
- Description: The run state vocabulary the database accepts is derived from one authoritative definition rather than written twice.
- Implementation: `file:packages/contracts/src/iacode_contracts/agent_runtime.py`
- Test: `test:Gate2MigrationTests`, `test:test_the_run_state_vocabulary_has_one_source`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0019 - canonical:GATE-2#3.6

- Source reference: docs/GATE-2-CHECKLIST.md row 3.6
- Description: The run event log is append-only: it carries a creation time, no update time, and no code path rewrites a stored event.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `test:test_run_event_log_is_append_only`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0020 - canonical:GATE-2#3.7

- Source reference: docs/GATE-2-CHECKLIST.md row 3.7
- Description: A tool request and its result are separate persisted rows, and a request can carry at most one result.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `test:test_a_tool_request_carries_at_most_one_result`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0021 - canonical:GATE-2#3.8

- Source reference: docs/GATE-2-CHECKLIST.md row 3.8
- Description: Agent and team profiles are persisted with their version, and a row an operator has customised is not overwritten by a later bootstrap.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/registry.py`
- Test: `test:test_bootstrap_does_not_overwrite_a_customised_profile`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0022 - canonical:GATE-2#3.9

- Source reference: docs/GATE-2-CHECKLIST.md row 3.9
- Description: An agent run names the model calls that served it, and aggregate usage is derived from them rather than counted a second time.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `test:test_agent_run_usage_is_derived_from_model_calls`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0023 - canonical:GATE-2#3.10

- Source reference: docs/GATE-2-CHECKLIST.md row 3.10
- Description: The task content the workflow needs to continue is persisted, and the difference from the gateway's metadata-only record is documented rather than implied.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `test:test_no_raw_provider_prompt_is_persisted`
- Negative test: _none_
- Documentation: `file:docs/runbooks/AGENT-RUNTIME.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0024 - canonical:GATE-2#4.1

- Source reference: docs/GATE-2-CHECKLIST.md row 4.1
- Description: The run lifecycle is an explicit state machine over exactly the declared states, and no state exists that the contract does not name.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/states.py`
- Test: `test:test_declared_states_are_exactly_the_contract`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0025 - canonical:GATE-2#4.2

- Source reference: docs/GATE-2-CHECKLIST.md row 4.2
- Description: A transition happens only when the transition table allows it.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/states.py`
- Test: `test:RunStateMachineTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0026 - canonical:GATE-2#4.3

- Source reference: docs/GATE-2-CHECKLIST.md row 4.3
- Description: An impossible transition is refused with a typed error rather than silently applied.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/states.py`
- Test: `test:test_impossible_transition_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0027 - canonical:GATE-2#4.4

- Source reference: docs/GATE-2-CHECKLIST.md row 4.4
- Description: A terminal state is terminal: no transition leaves `SUCCEEDED`, `FAILED` or `CANCELLED`.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/states.py`
- Test: `test:test_terminal_state_never_transitions`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0028 - canonical:GATE-2#4.5

- Source reference: docs/GATE-2-CHECKLIST.md row 4.5
- Description: Re-running a task creates a new run; a terminal run is never resumed in place.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_a_terminal_run_is_never_resumed`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0029 - canonical:GATE-2#4.6

- Source reference: docs/GATE-2-CHECKLIST.md row 4.6
- Description: Every accepted state change records an event, so the history explains the state.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_every_state_change_records_an_event`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0030 - canonical:GATE-2#4.7

- Source reference: docs/GATE-2-CHECKLIST.md row 4.7
- Description: The state machine is one definition, used by the API, the workflow and the store alike.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/states.py`
- Test: `test:test_state_machine_has_one_definition`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0031 - canonical:GATE-2#5.1

- Source reference: docs/GATE-2-CHECKLIST.md row 5.1
- Description: The event vocabulary covers run creation and start, agent start and completion, model call start and completion, tool request and tool result, and the three terminal outcomes.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/events.py`
- Test: `test:test_event_vocabulary_covers_the_declared_moments`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0032 - canonical:GATE-2#5.2

- Source reference: docs/GATE-2-CHECKLIST.md row 5.2
- Description: Events of one run carry a monotonic sequence number assigned by the store, so their order is deterministic.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`
- Test: `test:test_event_sequence_is_monotonic_per_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0033 - canonical:GATE-2#5.3

- Source reference: docs/GATE-2-CHECKLIST.md row 5.3
- Description: A recorded event is never rewritten; a correction is a new event.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`
- Test: `test:test_event_correction_is_a_new_event`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0034 - canonical:GATE-2#5.4

- Source reference: docs/GATE-2-CHECKLIST.md row 5.4
- Description: A retried append does not create a second event for the same occurrence.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`
- Test: `test:test_duplicate_append_does_not_duplicate_the_event`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0035 - canonical:GATE-2#5.5

- Source reference: docs/GATE-2-CHECKLIST.md row 5.5
- Description: An event payload carries a short verifiable summary and never a model's private reasoning or a raw prompt.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/events.py`
- Test: `test:test_event_payload_carries_no_private_reasoning`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0036 - canonical:GATE-2#5.6

- Source reference: docs/GATE-2-CHECKLIST.md row 5.6
- Description: An event payload larger than the configured bound is refused rather than persisted.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/limits.py`
- Test: `test:test_oversized_event_payload_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0037 - canonical:GATE-2#6.1

- Source reference: docs/GATE-2-CHECKLIST.md row 6.1
- Description: An agent profile is a versioned contract carrying identity, role, description, prompt template, default route, turn limit, permitted actions and an enabled flag.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/profiles.py`
- Test: `test:AgentProfileContractTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0038 - canonical:GATE-2#6.2

- Source reference: docs/GATE-2-CHECKLIST.md row 6.2
- Description: The builtin profiles are exactly the four this Gate needs to prove the runtime, and no profile exists for a capability the Gate does not exercise.
- Implementation: _none_
- Test: `test:test_builtin_profiles_are_exactly_the_declared_set`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0039 - canonical:GATE-2#6.3

- Source reference: docs/GATE-2-CHECKLIST.md row 6.3
- Description: Profiles are loaded from the repository, enumerable through the runtime, and validated when they are loaded.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/registry.py`
- Test: `test:AgentRegistryTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0040 - canonical:GATE-2#6.4

- Source reference: docs/GATE-2-CHECKLIST.md row 6.4
- Description: Loading the builtin profiles is idempotent: running it twice changes nothing the second time.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/registry.py`
- Test: `test:test_profile_bootstrap_is_idempotent`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0041 - canonical:GATE-2#6.5

- Source reference: docs/GATE-2-CHECKLIST.md row 6.5
- Description: Prompt templates are versioned files under the agent definition directory, not strings concatenated across the code.
- Implementation: _none_
- Test: `test:test_prompts_are_versioned_files`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0042 - canonical:GATE-2#6.6

- Source reference: docs/GATE-2-CHECKLIST.md row 6.6
- Description: An agent run records the profile version and the prompt template hash that produced it, so its behaviour can be reproduced.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/prompts.py`
- Test: `test:test_agent_run_records_profile_and_template_version`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0043 - canonical:GATE-2#6.7

- Source reference: docs/GATE-2-CHECKLIST.md row 6.7
- Description: Prompt assembly keeps runtime instructions, role instructions, task content and tool results in separate labelled channels.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/context.py`
- Test: `test:InstructionHierarchyTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0044 - canonical:GATE-2#6.8

- Source reference: docs/GATE-2-CHECKLIST.md row 6.8
- Description: The user's task is carried in the user channel and is never concatenated into the system instructions.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/context.py`
- Test: `test:test_task_never_enters_the_system_channel`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0045 - canonical:GATE-2#6.9

- Source reference: docs/GATE-2-CHECKLIST.md row 6.9
- Description: Every executed step records run, task, agent, agent run, timestamps, model call identity, provider, model, template version and result status — and no private reasoning.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:ProvenanceTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0046 - canonical:GATE-2#6.10

- Source reference: docs/GATE-2-CHECKLIST.md row 6.10
- Description: A profile declares the actions it may request, and a tool request outside that set is refused instead of persisted.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/profiles.py`
- Test: `test:test_tool_request_outside_allowed_actions_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0047 - canonical:GATE-2#7.1

- Source reference: docs/GATE-2-CHECKLIST.md row 7.1
- Description: A team profile is a versioned, ordered list of stages, each naming an agent profile, its input mapping and the name of its output.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/profiles.py`
- Test: `test:TeamProfileContractTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0048 - canonical:GATE-2#7.2

- Source reference: docs/GATE-2-CHECKLIST.md row 7.2
- Description: Two builtin teams exist: one single-agent and one two-stage planner and reviewer.
- Implementation: _none_
- Test: `test:test_builtin_teams_are_the_declared_set`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0049 - canonical:GATE-2#7.3

- Source reference: docs/GATE-2-CHECKLIST.md row 7.3
- Description: Team composition is configuration. Nothing in this Gate invents a team, and no model decides which agents run.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`
- Test: `test:test_team_composition_is_not_inferred`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0050 - canonical:GATE-2#7.4

- Source reference: docs/GATE-2-CHECKLIST.md row 7.4
- Description: Stages execute in the order the profile declares, and each stage's output becomes explicit, named context for the next.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:TeamExecutionTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0051 - canonical:GATE-2#7.5

- Source reference: docs/GATE-2-CHECKLIST.md row 7.5
- Description: A previous stage's output reaches the next stage as a labelled artifact and never as an instruction.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/context.py`
- Test: `test:test_previous_stage_output_is_an_artifact_not_an_instruction`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0052 - canonical:GATE-2#7.6

- Source reference: docs/GATE-2-CHECKLIST.md row 7.6
- Description: A team run produces one agent run per stage, in order, with separate outputs.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_team_run_produces_one_agent_run_per_stage`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0053 - canonical:GATE-2#8.1

- Source reference: docs/GATE-2-CHECKLIST.md row 8.1
- Description: A turn produces exactly one of a final answer, a message or a tool request.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`
- Test: `test:AgentEnvelopeTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0054 - canonical:GATE-2#8.2

- Source reference: docs/GATE-2-CHECKLIST.md row 8.2
- Description: The envelope carries an explicit version and is documented, so a consumer can detect an incompatible change instead of discovering one.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`
- Test: `test:test_envelope_version_is_declared`
- Negative test: _none_
- Documentation: `file:docs/runbooks/AGENT-RUNTIME.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0055 - canonical:GATE-2#8.3

- Source reference: docs/GATE-2-CHECKLIST.md row 8.3
- Description: The parser is strict: an output that does not conform is rejected rather than partially accepted.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`
- Test: `test:test_invalid_envelope_is_not_accepted_silently`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0056 - canonical:GATE-2#8.4

- Source reference: docs/GATE-2-CHECKLIST.md row 8.4
- Description: Native structured output is requested only from a model whose capability is known; otherwise the envelope is validated JSON text produced by the same contract.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`
- Test: `test:test_structured_output_is_used_only_when_the_capability_is_known`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0057 - canonical:GATE-2#8.5

- Source reference: docs/GATE-2-CHECKLIST.md row 8.5
- Description: No capability is asserted on a model's behalf to make a turn work.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`
- Test: `test:test_runtime_never_declares_a_capability`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0058 - canonical:GATE-2#8.6

- Source reference: docs/GATE-2-CHECKLIST.md row 8.6
- Description: At most one repair attempt follows an invalid turn, and it happens through the Model Gateway like any other call.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_repair_is_attempted_at_most_once`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0059 - canonical:GATE-2#8.7

- Source reference: docs/GATE-2-CHECKLIST.md row 8.7
- Description: A repair call counts against the run's budget and is recorded as a repair rather than hidden.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_repair_counts_against_the_budget`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0060 - canonical:GATE-2#8.8

- Source reference: docs/GATE-2-CHECKLIST.md row 8.8
- Description: A second invalid output ends the run with a normalised invalid-output error rather than looping.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_two_invalid_outputs_fail_the_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0061 - canonical:GATE-2#9.1

- Source reference: docs/GATE-2-CHECKLIST.md row 9.1
- Description: Every inference this Gate performs travels through the Model Gateway client port and through nothing else.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`
- Test: `test:test_every_inference_goes_through_the_gateway`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0062 - canonical:GATE-2#9.2

- Source reference: docs/GATE-2-CHECKLIST.md row 9.2
- Description: A run may carry a route alias or an explicit model, and the gateway decides whether it can be served.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`
- Test: `test:test_route_and_model_override_are_passed_through`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0063 - canonical:GATE-2#9.3

- Source reference: docs/GATE-2-CHECKLIST.md row 9.3
- Description: A run that names neither uses the configured default, and the runtime never picks a provider itself.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`
- Test: `test:test_runtime_never_chooses_a_provider`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0064 - canonical:GATE-2#9.4

- Source reference: docs/GATE-2-CHECKLIST.md row 9.4
- Description: Every model call is attributed to the agent run that caused it.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`
- Test: `test:test_model_call_is_attributed_to_its_agent_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0065 - canonical:GATE-2#9.5

- Source reference: docs/GATE-2-CHECKLIST.md row 9.5
- Description: A definitive gateway failure ends the run with a normalised error; the run never stays `RUNNING` for ever.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_gateway_failure_fails_the_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0066 - canonical:GATE-2#9.6

- Source reference: docs/GATE-2-CHECKLIST.md row 9.6
- Description: The runtime does not repeat a whole model call the gateway has already exhausted its own retries on.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_runtime_does_not_retry_an_exhausted_call`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0067 - canonical:GATE-2#9.7

- Source reference: docs/GATE-2-CHECKLIST.md row 9.7
- Description: Cost the gateway does not know is reported as unknown and never as zero.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`
- Test: `test:test_unknown_cost_is_unknown_not_zero`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0068 - canonical:GATE-2#9.8

- Source reference: docs/GATE-2-CHECKLIST.md row 9.8
- Description: A request the model's context cannot hold produces an explicit error rather than a silent truncation of the task.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_context_overflow_is_an_explicit_error`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0069 - canonical:GATE-2#10.1

- Source reference: docs/GATE-2-CHECKLIST.md row 10.1
- Description: A tool request is a persisted contract carrying identity, run, agent, name, arguments, creation time and a status from the declared vocabulary.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`
- Test: `test:ToolRequestContractTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0070 - canonical:GATE-2#10.2

- Source reference: docs/GATE-2-CHECKLIST.md row 10.2
- Description: A tool result is a contract carrying the request it answers, a status, an output, an error and metadata.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`
- Test: `test:ToolResultContractTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0071 - canonical:GATE-2#10.3

- Source reference: docs/GATE-2-CHECKLIST.md row 10.3
- Description: A tool request turn persists the request, records the event and moves the run to `WAITING_FOR_TOOL`.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_tool_request_pauses_the_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0072 - canonical:GATE-2#10.4

- Source reference: docs/GATE-2-CHECKLIST.md row 10.4
- Description: A paused run performs no further model call until a result arrives.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_a_waiting_run_makes_no_model_call`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0073 - canonical:GATE-2#10.5

- Source reference: docs/GATE-2-CHECKLIST.md row 10.5
- Description: A tool name is data. Nothing in this Gate interprets it as a command, a path or an executable.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`
- Test: `test:test_tool_name_is_never_interpreted`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0074 - canonical:GATE-2#10.6

- Source reference: docs/GATE-2-CHECKLIST.md row 10.6
- Description: A matching tool result is persisted, recorded as an event and resumes the run.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_tool_result_resumes_the_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0075 - canonical:GATE-2#10.7

- Source reference: docs/GATE-2-CHECKLIST.md row 10.7
- Description: The same tool result delivered twice resolves the request once and resumes the run once.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_duplicate_tool_result_is_idempotent`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0076 - canonical:GATE-2#10.8

- Source reference: docs/GATE-2-CHECKLIST.md row 10.8
- Description: A tool result naming another run or an unknown request is refused.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_tool_result_for_another_run_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0077 - canonical:GATE-2#10.9

- Source reference: docs/GATE-2-CHECKLIST.md row 10.9
- Description: A tool result that arrives after the run reached a terminal state is refused.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_tool_result_after_a_terminal_state_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0078 - canonical:GATE-2#10.10

- Source reference: docs/GATE-2-CHECKLIST.md row 10.10
- Description: Waiting for a tool has its own configurable timeout, separate from the run deadline, and reaching it ends the run explicitly.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`
- Test: `test:test_tool_wait_timeout_ends_the_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0079 - canonical:GATE-2#10.11

- Source reference: docs/GATE-2-CHECKLIST.md row 10.11
- Description: An automated control proves the runtime boundary contains no process, shell, filesystem-mutating or version-control execution path, and the control is a property of the boundary rather than of one file.
- Implementation: `file:tests/test_gate2_agent_runtime.py`
- Test: `test:ToolExecutionBoundaryTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0080 - canonical:GATE-2#10.12

- Source reference: docs/GATE-2-CHECKLIST.md row 10.12
- Description: The division of labour with the next Gate is documented: this Gate persists and pauses, the next one executes.
- Implementation: _none_
- Test: `test:test_gate_three_boundary_is_documented`
- Negative test: _none_
- Documentation: `file:docs/runbooks/AGENT-RUNTIME.md`, `file:docs/adr/ADR-0021-tool-execution-boundary.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0081 - canonical:GATE-2#11.1

- Source reference: docs/GATE-2-CHECKLIST.md row 11.1
- Description: Every run carries a maximum turn count, a maximum model-call count and a wall-clock deadline.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`
- Test: `test:BudgetContractTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0082 - canonical:GATE-2#11.2

- Source reference: docs/GATE-2-CHECKLIST.md row 11.2
- Description: A token budget is enforced when the provider reports usage and recorded as unenforceable when it does not, rather than invented.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`
- Test: `test:test_token_budget_is_unenforceable_without_usage`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0083 - canonical:GATE-2#11.3

- Source reference: docs/GATE-2-CHECKLIST.md row 11.3
- Description: A budget that is zero, negative or absurd is refused when the run is validated.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`
- Test: `test:test_absurd_budget_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0084 - canonical:GATE-2#11.4

- Source reference: docs/GATE-2-CHECKLIST.md row 11.4
- Description: Reaching any budget ends the run with a normalised budget error.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_budget_exhaustion_ends_the_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0085 - canonical:GATE-2#11.5

- Source reference: docs/GATE-2-CHECKLIST.md row 11.5
- Description: No model call happens after a budget is exhausted.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_no_call_after_budget_exhaustion`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0086 - canonical:GATE-2#11.6

- Source reference: docs/GATE-2-CHECKLIST.md row 11.6
- Description: Every call to the gateway counts against the model-call budget, including a repair.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`
- Test: `test:test_every_gateway_call_counts`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0087 - canonical:GATE-2#11.7

- Source reference: docs/GATE-2-CHECKLIST.md row 11.7
- Description: A run cannot execute an unbounded number of turns, and a run that outlives its deadline is ended rather than left running.
- Implementation: `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:scripts/iacode/scenarios/agent_runtime_deadline.py`
- Test: `test:test_a_stage_turn_limit_stops_a_loop_inside_one_stage`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0088 - canonical:GATE-2#12.1

- Source reference: docs/GATE-2-CHECKLIST.md row 12.1
- Description: A run can be cancelled through the API while it is executing.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:AgentRunApiTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0089 - canonical:GATE-2#12.2

- Source reference: docs/GATE-2-CHECKLIST.md row 12.2
- Description: Cancellation reaches the durable workflow and stops it rather than only marking a row.
- Implementation: `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:scripts/iacode/scenarios/agent_runtime_cancellation.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0090 - canonical:GATE-2#12.3

- Source reference: docs/GATE-2-CHECKLIST.md row 12.3
- Description: A cancelled run is terminal and records the cancellation event.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_cancelled_run_is_terminal_and_recorded`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0091 - canonical:GATE-2#12.4

- Source reference: docs/GATE-2-CHECKLIST.md row 12.4
- Description: A run waiting for a tool can be cancelled, and a tool result that arrives afterwards is refused.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`, `file:scripts/iacode/scenarios/agent_runtime_cancellation.py`
- Test: `test:test_cancel_while_waiting_for_tool`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0092 - canonical:GATE-2#12.5

- Source reference: docs/GATE-2-CHECKLIST.md row 12.5
- Description: No model call happens after a run is cancelled.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:test_no_model_call_after_cancellation`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0093 - canonical:GATE-2#13.1

- Source reference: docs/GATE-2-CHECKLIST.md row 13.1
- Description: Temporal is the durable execution engine, and no second scheduler or background orchestration loop competes with it.
- Implementation: `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`
- Test: `test:test_no_second_orchestrator_exists`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0094 - canonical:GATE-2#13.2

- Source reference: docs/GATE-2-CHECKLIST.md row 13.2
- Description: Workflow code stays deterministic: every external effect — model call, persistence, notification — happens in an activity.
- Implementation: `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`
- Test: `test:WorkflowDeterminismTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0095 - canonical:GATE-2#13.3

- Source reference: docs/GATE-2-CHECKLIST.md row 13.3
- Description: A worker restart while a run waits for a tool preserves the run, and the run resumes and completes when the result arrives.
- Implementation: `file:scripts/iacode/scenarios/agent_runtime_durability.py`, `file:services/orchestrator/rehearsal/durability.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0096 - canonical:GATE-2#13.4

- Source reference: docs/GATE-2-CHECKLIST.md row 13.4
- Description: An API restart does not lose a run in progress: the state lives in the store and in the workflow, never in process memory.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`, `file:scripts/iacode/scenarios/agent_runtime_durability.py`
- Test: `test:test_run_state_is_not_held_in_process_memory`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0097 - canonical:GATE-2#13.5

- Source reference: docs/GATE-2-CHECKLIST.md row 13.5
- Description: The workflow receives a frozen plan, so editing a profile while a run executes cannot change what that run is doing.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`
- Test: `test:test_workflow_plan_is_frozen_at_creation`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0098 - canonical:GATE-2#14.1

- Source reference: docs/GATE-2-CHECKLIST.md row 14.1
- Description: A versioned API creates a run, reads it, lists runs, streams its events, cancels it and accepts a tool result.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:AgentRunApiTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0099 - canonical:GATE-2#14.2

- Source reference: docs/GATE-2-CHECKLIST.md row 14.2
- Description: Creation answers immediately with the run identifier, its state and its creation time, without holding the request open for the run.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_creation_answers_immediately`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0100 - canonical:GATE-2#14.3

- Source reference: docs/GATE-2-CHECKLIST.md row 14.3
- Description: Creation accepts no provider credential and no provider address.
- Implementation: `file:packages/contracts/src/iacode_contracts/agent_runtime.py`
- Test: `test:test_creation_cannot_supply_a_credential_or_address`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0101 - canonical:GATE-2#14.4

- Source reference: docs/GATE-2-CHECKLIST.md row 14.4
- Description: A run's status carries its state, current stage, timestamps, budget consumption, final result when there is one and error summary when there is one.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_run_status_carries_the_declared_fields`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0102 - canonical:GATE-2#14.5

- Source reference: docs/GATE-2-CHECKLIST.md row 14.5
- Description: A failed run answers with an error type, a safe message, the stage that failed and the correlation identifier, and never with a traceback.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_failure_summary_is_safe`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0103 - canonical:GATE-2#14.6

- Source reference: docs/GATE-2-CHECKLIST.md row 14.6
- Description: Run events are readable as a page and as a live stream.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_events_are_readable_as_page_and_stream`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0104 - canonical:GATE-2#14.7

- Source reference: docs/GATE-2-CHECKLIST.md row 14.7
- Description: A consumer that reconnects with a cursor receives exactly the events that follow it.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_event_stream_resumes_from_a_cursor`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0105 - canonical:GATE-2#14.8

- Source reference: docs/GATE-2-CHECKLIST.md row 14.8
- Description: Reconnecting or retrying a read creates no new event.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_reconnection_creates_no_event`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0106 - canonical:GATE-2#14.9

- Source reference: docs/GATE-2-CHECKLIST.md row 14.9
- Description: The available agent profiles and team profiles are enumerable through the API.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_profiles_and_teams_are_enumerable`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0107 - canonical:GATE-2#14.10

- Source reference: docs/GATE-2-CHECKLIST.md row 14.10
- Description: Task input size is bounded by configuration and an oversized task is refused rather than stored.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/limits.py`
- Test: `test:test_oversized_task_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0108 - canonical:GATE-2#15.1

- Source reference: docs/GATE-2-CHECKLIST.md row 15.1
- Description: A creation request repeated with the same idempotency key returns the run the first one created.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_same_idempotency_key_returns_the_same_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0109 - canonical:GATE-2#15.2

- Source reference: docs/GATE-2-CHECKLIST.md row 15.2
- Description: A creation request with a different key creates a different run.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_a_different_key_creates_a_new_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0110 - canonical:GATE-2#15.3

- Source reference: docs/GATE-2-CHECKLIST.md row 15.3
- Description: Two runs execute at the same time without sharing state, context or events.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`
- Test: `test:ConcurrentRunIsolationTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0111 - canonical:GATE-2#15.4

- Source reference: docs/GATE-2-CHECKLIST.md row 15.4
- Description: One task may carry two independent runs with separate results and separate events.
- Implementation: `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_one_task_can_have_two_independent_runs`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0112 - canonical:GATE-2#15.5

- Source reference: docs/GATE-2-CHECKLIST.md row 15.5
- Description: Identifiers use the strategy the repository already defines rather than a second format.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`
- Test: `test:test_identifiers_use_the_existing_strategy`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0113 - canonical:GATE-2#16.1

- Source reference: docs/GATE-2-CHECKLIST.md row 16.1
- Description: The runtime publishes the declared instruments for runs, turns, failures, waiting runs, budget exhaustions and cancellations.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/telemetry.py`
- Test: `test:AgentRuntimeMetricsTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0114 - canonical:GATE-2#16.2

- Source reference: docs/GATE-2-CHECKLIST.md row 16.2
- Description: No metric label carries a task, a prompt, a response or tool arguments, and every label is low cardinality.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/telemetry.py`
- Test: `test:test_no_metric_label_carries_content`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0115 - canonical:GATE-2#16.3

- Source reference: docs/GATE-2-CHECKLIST.md row 16.3
- Description: Structured logs carry correlation, task, run, agent, agent run, stage, event type, model call and status when those exist.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/telemetry.py`
- Test: `test:test_logs_carry_the_declared_identifiers`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0116 - canonical:GATE-2#16.4

- Source reference: docs/GATE-2-CHECKLIST.md row 16.4
- Description: No log record carries the whole task by default, and a secret nested inside a payload is redacted.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/telemetry.py`
- Test: `test:test_nested_secret_is_redacted_in_runtime_logs`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0117 - canonical:GATE-2#17.1

- Source reference: docs/GATE-2-CHECKLIST.md row 17.1
- Description: An operational page creates a run from a written task, a chosen team and an optional route or model.
- Implementation: `file:apps/web/src/app/agent-runtime/agent-runtime.ts`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0118 - canonical:GATE-2#17.2

- Source reference: docs/GATE-2-CHECKLIST.md row 17.2
- Description: The page follows the run's state and its events as they happen.
- Implementation: `file:apps/web/src/app/agent-runtime/agent-runtime.service.ts`, `file:apps/web/src/app/agent-runtime/agent-runtime.service.spec.ts`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0119 - canonical:GATE-2#17.3

- Source reference: docs/GATE-2-CHECKLIST.md row 17.3
- Description: The page shows the final result of a successful run and the safe failure summary of a failed one.
- Implementation: `file:apps/web/src/app/agent-runtime/agent-runtime.html`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0120 - canonical:GATE-2#17.4

- Source reference: docs/GATE-2-CHECKLIST.md row 17.4
- Description: The page can cancel a run that is executing.
- Implementation: `file:apps/web/src/app/agent-runtime/agent-runtime.ts`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0121 - canonical:GATE-2#17.5

- Source reference: docs/GATE-2-CHECKLIST.md row 17.5
- Description: A run waiting for a tool is shown as waiting, with the tool name and the pending status, and the page offers nothing that would execute it.
- Implementation: `file:apps/web/src/app/agent-runtime/agent-runtime.html`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts`
- Test: `test:test_the_page_offers_nothing_that_would_execute_a_tool`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0122 - canonical:GATE-2#17.6

- Source reference: docs/GATE-2-CHECKLIST.md row 17.6
- Description: Model output is rendered as text, never as trusted markup.
- Implementation: `file:apps/web/src/app/agent-runtime/agent-runtime.html`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts`
- Test: `test:test_model_output_is_not_rendered_as_markup`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0123 - canonical:GATE-2#18.1

- Source reference: docs/GATE-2-CHECKLIST.md row 18.1
- Description: No provider credential reaches the runtime, the store, a log record, a metric or the browser.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`
- Test: `test:AgentRuntimeSecretContainmentTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0124 - canonical:GATE-2#18.2

- Source reference: docs/GATE-2-CHECKLIST.md row 18.2
- Description: Tool arguments, agent output and tool results are bounded by configuration, and an oversized payload is refused.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/limits.py`
- Test: `test:PayloadLimitTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0125 - canonical:GATE-2#18.3

- Source reference: docs/GATE-2-CHECKLIST.md row 18.3
- Description: Nothing this Gate persists becomes training data: rights default to denial and no run, event or result is marked otherwise.
- Implementation: `file:packages/persistence/src/iacode_persistence/models.py`
- Test: `test:test_nothing_this_gate_persists_is_training_eligible`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0126 - canonical:GATE-2#18.4

- Source reference: docs/GATE-2-CHECKLIST.md row 18.4
- Description: The runtime asks for no private reasoning and stores none; what it keeps are short verifiable summaries.
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`
- Test: `test:test_no_chain_of_thought_is_requested_or_stored`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0127 - canonical:GATE-2#19.1

- Source reference: docs/GATE-2-CHECKLIST.md row 19.1
- Description: A single-agent run executes live, through the Model Gateway, against the configured provider, and succeeds.
- Implementation: `file:scripts/iacode/agent_runtime_smoke.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0006`, `command:cmd-0005`
- Guardrail: _none_

### REQ-0128 - canonical:GATE-2#19.2

- Source reference: docs/GATE-2-CHECKLIST.md row 19.2
- Description: A planner and reviewer run executes live, in order, with separate outputs and the reviewer receiving the planner's output.
- Implementation: `file:scripts/iacode/agent_runtime_smoke.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0006`
- Guardrail: _none_

### REQ-0129 - canonical:GATE-2#19.3

- Source reference: docs/GATE-2-CHECKLIST.md row 19.3
- Description: The live check uses an explicitly configured model and fails clearly when that model is not in the catalog, rather than substituting one.
- Implementation: `file:scripts/iacode/agent_runtime_smoke.py`
- Test: `test:test_live_smoke_never_substitutes_a_model`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0130 - canonical:GATE-2#19.4

- Source reference: docs/GATE-2-CHECKLIST.md row 19.4
- Description: The live check reports `BLOCKED` rather than `FAIL` when the local configuration carries no credential, and names the variable that is missing.
- Implementation: `file:scripts/iacode/agent_runtime_smoke.py`
- Test: `test:test_live_smoke_blocks_without_a_credential`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0131 - canonical:GATE-2#19.5

- Source reference: docs/GATE-2-CHECKLIST.md row 19.5
- Description: The live evidence records model provenance — provider, model, endpoint, model call identity — and no prompt or completion.
- Implementation: `file:scripts/iacode/agent_runtime_smoke.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0006`, `command:cmd-0007`
- Guardrail: _none_

### REQ-0132 - canonical:GATE-2#20.1

- Source reference: docs/GATE-2-CHECKLIST.md row 20.1
- Description: The repository's one verification command covers this Gate, in its targeted and its full mode.
- Implementation: `file:scripts/iacode/verify.py`
- Test: `test:Gate2VerificationStageTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0133 - canonical:GATE-2#20.2

- Source reference: docs/GATE-2-CHECKLIST.md row 20.2
- Description: A runbook documents starting the runtime, creating a run, following it, cancelling it, tool requests and results, budgets, the live smoke and troubleshooting.
- Implementation: _none_
- Test: `test:test_agent_runtime_runbook_covers_the_declared_topics`
- Negative test: _none_
- Documentation: `file:docs/runbooks/AGENT-RUNTIME.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0134 - canonical:GATE-2#20.3

- Source reference: docs/GATE-2-CHECKLIST.md row 20.3
- Description: The architecture, development, version and entry documents describe what this Gate delivered rather than what was planned.
- Implementation: _none_
- Test: `test:Gate2DocumentationTests`
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`, `file:docs/DEVELOPMENT.md`, `file:docs/VERSIONS.md`, `file:README.md`, `file:START-HERE.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0135 - canonical:GATE-2#20.4

- Source reference: docs/GATE-2-CHECKLIST.md row 20.4
- Description: The structural decisions of this Gate are recorded as ADRs.
- Implementation: _none_
- Test: `test:Gate2AdrTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0136 - canonical:GATE-2#20.5

- Source reference: docs/GATE-2-CHECKLIST.md row 20.5
- Description: The Gate produces its retrospective from the canonical template.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:.iacode/memory/retrospectives/GATE-2-CP-0001.md`, `file:.iacode/templates/retrospective/TEMPLATE.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0137 - canonical:GATE-2#20.6

- Source reference: docs/GATE-2-CHECKLIST.md row 20.6
- Description: The Gate closes at the project's own internal verdict and starts no part of the Gate that follows it.
- Implementation: _none_
- Test: `test:Gate2ScopeTests`
- Negative test: _none_
- Documentation: `file:docs/checkpoints/GATE-2-CP-0001/STATE.json`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: _none_
- Test: `test:DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates`, `test:DetachedHeadValidationTests.test_detached_head_at_wrong_commit_fails`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: _none_
- Test: `test:DeltaInventoryTests.test_removed_manifest_entry_fails`, `test:DeltaInventoryTests.test_silent_tracked_modification_fails`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: _none_
- Test: `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: _none_
- Test: `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`, `test:ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: _none_
- Test: `test:QualityEvidenceTests.test_pass_without_evidence_fails`, `test:QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: _none_
- Test: `test:SetupChecklistTests.test_checklist_exists_and_is_referenced`, `test:SetupChecklistTests.test_documentation_links_resolve`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: _none_
- Test: `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`, `test:ExternalAttestationTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough`, `test:SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass`, `test:DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: _none_
- Test: `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`, `test:DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `test:DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: _none_
- Test: `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_the_policy_declares_a_non_empty_closed_set`, `test:GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `test:DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `test:DeliveryAssuranceGateTests.test_red_tests_block_review`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: _none_
- Test: `test:CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`, `test:CommandInputBindingTests.test_a_clean_tree_claim_is_checked_against_the_declared_commit`, `test:CommandReproducibilityTests.test_bare_script_name_is_rejected`, `test:CommandReproducibilityTests.test_unresolvable_script_path_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: _none_
- Test: `test:DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`, `test:GateRunnerTests.test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test:GateRunnerTests.test_the_refresh_has_one_definition`, `test:GateRunnerTests.test_no_other_module_executes_the_mandatory_gate_set`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: _none_
- Test: `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`, `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`, `test:HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0013 - lesson:LSN-0013

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0013
- Description: Verify an installed capability must be detected by resolved path, not by a bare command lookup
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/TOOL-CAPABILITIES.md`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: _none_
- Test: `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected`, `test:SealChronologyTests.test_a_missing_post_commit_validation_is_rejected`, `test:SealChronologyTests.test_a_dirty_tree_validation_is_not_evidence_of_a_sealed_commit`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: _none_
- Test: `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`, `test:PromotionInvariantTests.test_a_terminal_status_requires_an_independent_verdict`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: _none_
- Test: `test:MandatoryGatePolicyTests.test_a_cycle_missing_one_mandatory_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_a_mandatory_gate_that_exited_nonzero_is_rejected`, `test:MandatoryGatePolicyTests.test_a_pass_measured_before_a_source_change_is_stale`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: _none_
- Test: `test:ExpectedRequirementSetTests.test_the_expected_set_is_derived_from_the_canonical_sources`, `test:ExpectedRequirementSetTests.test_the_checklist_is_reparsed_rather_than_trusted`, `test:ExpectedRequirementSetTests.test_a_downgraded_matrix_cannot_escape_the_comparison`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: _none_
- Test: `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`, `test:LessonResolutionTests.test_an_invariant_control_must_be_defined_in_the_tooling`, `test:LessonResolutionTests.test_lesson_evidence_must_resolve`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: _none_
- Test: `test:PreflightFreshnessTests.test_a_changed_fingerprint_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_preflight_from_another_gate_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: _none_
- Test: `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically`, `test:CommandInputBindingTests.test_a_digest_that_omits_an_input_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: _none_
- Test: `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`, `test:IntegrityAnchorTests.test_a_recomputed_anchor_hash_must_match_its_fields`, `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: _none_
- Test: `test:DerivedCountTests.test_a_forged_count_is_rejected`, `test:DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_the_cardinality_of_a_derived_set`, `test:SourceCardinalityPolicyTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: _none_
- Test: `test:LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected`, `test:LessonProvenanceTests.test_a_nonexistent_checkpoint_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0024 - lesson:LSN-0024

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0024
- Description: Verify a control is finished only when its positive path has been executed, not only its refusals
- Implementation: _none_
- Test: `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0025 - lesson:LSN-0025

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0025
- Description: Verify a generic guardrail derives repository state instead of naming today's checkpoint
- Implementation: _none_
- Test: `test:IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint`, `test:SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0026 - lesson:LSN-0026

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0026
- Description: Verify an adversarial battery without a null-mutation control proves nothing
- Implementation: _none_
- Test: `test:InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected`, `test:InternalAssuranceTests.test_a_failed_null_mutation_control_cannot_produce_a_pass`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0027 - lesson:LSN-0027

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0027
- Description: Verify a lesson's prose may record a residual limit but may never contradict its status
- Implementation: _none_
- Test: `test:MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded`, `test:MemoryPolicyDocumentTests.test_the_repository_memory_has_no_status_contradiction`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0028 - lesson:LSN-0028

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0028
- Description: Verify a configuration key that no code reads is a defect, not documentation
- Implementation: _none_
- Test: `test:MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared`, `test:MemoryPolicyDocumentTests.test_the_declared_policy_validates_against_its_schema`, `test:test_configuration.test_every_declared_key_is_read_somewhere`, `test:test_configuration.test_test_settings_ignore_the_ambient_environment`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0029 - lesson:LSN-0029

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0029
- Description: Verify a required protocol transition must never turn a mandatory gate red
- Implementation: _none_
- Test: `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `test:SuccessorDurabilityTests.test_a_missing_anchor_is_still_detected_after_the_chain_advances`, `test:GateTransitionSimulationTests.test_the_first_checkpoint_of_the_next_gate_reaches_review_readiness`, `test:GateTransitionSimulationTests.test_its_mirror_audit_passes_with_the_empty_dimensions_inapplicable`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0030 - lesson:LSN-0031

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0030
- Description: Verify an empty applicable set is not a missing required set, and a control must tell them apart
- Implementation: _none_
- Test: `test:MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`, `test:MirrorApplicabilitySemanticsTests.test_a_missing_required_set_fails_rather_than_being_inapplicable`, `test:MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0031 - lesson:LSN-0032

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0031
- Description: Verify a control written while one Gate was the only Gate stops being a control when the next one starts
- Implementation: _none_
- Test: `test:Gate1ScopeTests.test_no_future_gate_capability_is_implemented`, `test:MonorepoStructureTests.test_no_future_gate_capability_is_implemented`, `test:MonorepoStructureTests.test_the_scope_control_detects_an_implementation`, `test:MonorepoStructureTests.test_the_scope_control_ignores_a_gate_that_has_already_run`, `test:ExpectedRequirementSetTests.test_expected_set_names_the_gate_specification`, `test:AssuranceScopeTests.test_assurance_scope_covers_the_runtime_source`, `test:TestSuiteRegistryTests.test_declared_suites_are_discovered`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0032 - lesson:LSN-0033

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0032
- Description: Verify a value bound in middleware is absent in the handlers that run outside it
- Implementation: _none_
- Test: `test:test_errors_and_correlation.test_internal_error_still_carries_a_correlation_identifier`, `test:test_errors_and_correlation.test_internal_error_leaks_nothing`, `test:test_errors_and_correlation.test_a_missing_route_uses_the_error_contract`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0033 - lesson:LSN-0034

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0033
- Description: Verify re-deriving what the framework already computed diverges from the framework
- Implementation: _none_
- Test: `test:test_observability.test_metrics_endpoint_exposes_request_metrics`, `test:test_observability.test_metrics_label_routes_by_template_not_by_url`, `test:PrometheusConfigurationTests.test_the_api_instruments_reach_prometheus`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0034 - lesson:LSN-0035

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0034
- Description: Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work
- Implementation: _none_
- Test: `test:SubprocessDecodingTests.test_no_capture_relies_on_the_platform_codepage`, `test:SubprocessDecodingTests.test_every_tool_that_re_emits_captured_output_configures_its_own_stream`, `test:SubprocessDecodingTests.test_the_rule_detects_a_capture_that_would_fail`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0035 - lesson:LSN-0036

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0035
- Description: Verify a gate that runs inside an image measures the image, not the source
- Implementation: _none_
- Test: `test:Gate1GuardrailTests.test_every_image_gate_builds_before_it_measures`, `test:Gate1GuardrailTests.test_the_image_gate_rule_detects_a_gate_that_would_skip_the_build`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0036 - lesson:LSN-0037

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0036
- Description: Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves
- Implementation: _none_
- Test: `test:Gate1GuardrailTests.test_no_shared_control_is_bound_to_a_gate_literal`, `test:Gate1GuardrailTests.test_the_gate_literal_rule_detects_a_bound_control`, `test:Gate1GuardrailTests.test_the_gate_literal_rule_accepts_a_derived_gate_and_a_fixture_root`, `test:Gate1GuardrailTests.test_no_control_names_a_migration_revision_literally`, `test:Gate1GuardrailTests.test_the_revision_rule_detects_a_named_head`, `test:Gate1GuardrailTests.test_the_head_revision_has_one_derivation`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0037 - lesson:LSN-0038

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0037
- Description: Verify two representations of one concept in one module disagree, and the safer one loses
- Implementation: _none_
- Test: `test:test_common_primitives.test_a_documented_placeholder_is_not_redacted`, `test:Gate1GuardrailTests.test_both_redactors_agree_on_every_value_the_example_file_carries`, `test:CredentialVocabularyTests.test_no_module_writes_its_own_credential_name_rule`, `test:CredentialVocabularyTests.test_the_rule_detects_a_second_opinion`, `test:CredentialVocabularyTests.test_the_two_questions_stay_different`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0038 - lesson:LSN-0039

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0038
- Description: Verify a test that writes to the operational database leaves production data behind
- Implementation: _none_
- Test: `test:test_gateway_persistence.test_the_operational_catalog_holds_only_providers_the_policy_declares`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0039 - lesson:LSN-0040

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0039
- Description: Verify a control that judges sealed history only runs once a successor anchors it
- Implementation: _none_
- Test: `test:RecordedInputTests.test_every_sealed_checkpoint_validates_from_its_own_tag`, `test:RecordedInputTests.test_the_recorder_never_declares_an_ignored_path_as_an_input`, `test:RecordedInputTests.test_an_ignored_input_is_bound_by_content_rather_than_by_presence`, `test:RecordedInputTests.test_an_input_the_repository_carries_is_still_required_to_exist`, `test:RecordedInputTests.test_an_ignored_input_without_a_bound_digest_is_still_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0040 - lesson:LSN-0041

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0040
- Description: Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing
- Implementation: _none_
- Test: `test:SourceIntegrityTests.test_no_source_file_carries_a_stray_control_character`, `test:SourceIntegrityTests.test_the_scan_detects_one`, `test:FrontendSafetyTests.test_the_page_offers_nothing_that_would_execute_a_tool`, `test:RepositoryToolExecutionBoundaryTests.test_the_boundary_has_something_to_scan`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0041 - lesson:LSN-0042

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0041
- Description: Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone
- Implementation: _none_
- Test: `test:Gate2MigrationTests.test_the_agent_runtime_migration_is_reversible`, `test:test_migrations.test_the_declared_model_matches_the_migrated_schema`, `test:MigrationConstraintNamingTests.test_a_check_constraint_is_created_and_dropped_by_its_bare_name`, `test:MigrationConstraintNamingTests.test_a_unique_constraint_keeps_exactly_the_name_it_was_given`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0042 - lesson:LSN-0043

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0042
- Description: Verify a log line is not evidence that another process is ready
- Implementation: _none_
- Test: `test:ScenarioReadinessTests.test_readiness_is_asked_of_temporal`, `test:ScenarioReadinessTests.test_readiness_is_not_read_from_a_log_line`, `test:ScenarioReadinessTests.test_the_harness_asks_the_server_for_the_answer`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0043 - lesson:LSN-0044

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0043
- Description: Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module
- Implementation: _none_
- Test: `test:ToolExecutionBoundaryTests.test_the_null_control_detects_a_mutation`, `test:test_boundary.test_the_provider_scan_would_catch_one`, `test:test_boundary.test_the_credential_scan_would_catch_one`, `test:RepositoryToolExecutionBoundaryTests.test_the_scan_detects_a_module_that_does_it`, `test:WorkflowDeterminismTests.test_the_determinism_scan_detects_a_module_that_breaks_it`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0044 - lesson:LSN-0045

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0044
- Description: Verify a counted test suite must declare its cases statically, because the denominator is read from the source
- Implementation: _none_
- Test: `test:CountedSuiteExpansionTests.test_no_counted_pytest_case_expands_at_run_time`, `test:CountedSuiteExpansionTests.test_the_scan_detects_an_expansion`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0045 - lesson:LSN-0046

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0045
- Description: Verify a timeout that cancels the task it runs in leaves nothing able to record what happened
- Implementation: _none_
- Test: `test:DeadlineEnforcementTests.test_the_engine_is_not_wrapped_in_wait_for`, `test:DeadlineEnforcementTests.test_the_deadline_races_an_explicit_child_task`, `test:DeadlineEnforcementTests.test_the_wait_accepts_every_way_a_cancelled_activity_surfaces`, `test:DeadlineEnforcementTests.test_the_deadline_path_writes_the_failure_down`, `test:DeadlineEnforcementTests.test_the_scenario_asserts_the_run_ended_and_said_so`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0046 - lesson:LSN-0047

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0046
- Description: Verify a refusal that misnames the defect spends the only repair on the wrong correction
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `file:services/agent-runtime/src/iacode_agent_runtime/context.py`
- Test: `test:test_content_of_the_wrong_type_is_refused_by_its_real_defect`, `test:test_the_runtime_instructions_state_that_content_is_one_string`, `test:test_invalid_envelope_is_not_accepted_silently`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0006`, `command:cmd-0008`
- Guardrail: _none_

### LESSON-REQ-0047 - lesson:LSN-0048

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0047
- Description: Verify a state and the event that explains it, written in two commits, are written event first
- Implementation: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:apps/api/src/iacode_api/routes/agent_runs.py`
- Test: `test:test_a_terminal_state_is_never_visible_before_its_terminal_event`, `test:DeadlineEnforcementTests.test_the_workflow_writes_the_terminal_event_before_the_terminal_state`, `test:test_a_workflow_that_cannot_start_fails_the_run_rather_than_leaving_it_created`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0006`
- Guardrail: _none_

### LESSON-REQ-0048 - lesson:LSN-0049

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0048
- Description: Verify a metric read the instant after the call that moved it is read before the scrape that carries it
- Implementation: `file:scripts/iacode/gateway_smoke.py`, `file:scripts/iacode/smoke.py`
- Test: `test:LiveSmokeContractTests.test_the_observability_check_waits_for_a_scrape_and_asks_only_prometheus`, `test:LiveSmokeContractTests.test_live_smoke_is_bounded_and_minimal`, `test:ObserverCycleTests.test_every_script_that_reads_prometheus_waits_for_a_scrape`, `test:ObserverCycleTests.test_the_scan_fires_on_a_read_that_does_not_wait`, `test:ObserverCycleTests.test_the_foundation_smoke_waits_for_both_targets_and_asks_only_prometheus`
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0005`, `command:cmd-0067`
- Guardrail: _none_

### LESSON-REQ-0049 - lesson:LSN-0050

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0049
- Description: Verify a checkpoint sealed without naming its own tag cannot be validated from that tag
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/seal_checkpoint.py`, `file:docs/adr/ADR-0023-sealed-checkpoint-binds-its-own-tag.md`
- Test: `test:DetachedHeadValidationTests.test_sealing_refuses_a_state_that_does_not_name_its_own_tag`, `test:DetachedHeadValidationTests.test_a_symbolic_head_validates_from_its_own_canonical_tag`, `test:DetachedHeadValidationTests.test_a_symbolic_head_away_from_its_canonical_tag_is_still_refused`, `test:RecordedInputTests.test_every_sealed_checkpoint_validates_from_its_own_tag`
- Negative test: _none_
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `command:cmd-0020`
- Guardrail: _none_
