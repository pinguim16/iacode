# Requirements Matrix - GATE-2-CP-0002

Expected set derived by: `policies.expected_requirement_refs over docs/GATE-2-CHECKLIST.md, .iacode/policies/canonical-requirements.json, .iacode/policies/audit-registry.json and LESSON-PREFLIGHT.json`.

| ID | Anchor | Mandatory | Status | Requirement | Source |
|---|---|---|---|---|---|
| `REQ-0001` | `canonical:GATE-2#1.1` | yes | `COMPLETE` | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. | docs/GATE-2-CHECKLIST.md row 1.1 |
| `REQ-0002` | `canonical:GATE-2#1.2` | yes | `COMPLETE` | The closed mandatory gate registry carries every executable gate this Gate introduces. | docs/GATE-2-CHECKLIST.md row 1.2 |
| `REQ-0003` | `canonical:GATE-2#1.3` | yes | `COMPLETE` | Every test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence. | docs/GATE-2-CHECKLIST.md row 1.3 |
| `REQ-0004` | `canonical:GATE-2#1.4` | yes | `COMPLETE` | The internal Red Team battery of this Gate is executable, scoped to the Agent Runtime, and records a null-mutation control. | docs/GATE-2-CHECKLIST.md row 1.4 |
| `REQ-0005` | `canonical:GATE-2#1.5` | yes | `COMPLETE` | The reservation of the agent definition directory is consumed by the Gate that owns it, and the scope registry keeps constraining every path still owned by a later Gate. | docs/GATE-2-CHECKLIST.md row 1.5 |
| `REQ-0006` | `canonical:GATE-2#1.6` | yes | `COMPLETE` | One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack. | docs/GATE-2-CHECKLIST.md row 1.6 |
| `REQ-0007` | `canonical:GATE-2#2.1` | yes | `COMPLETE` | The agent runtime is a provider-neutral library with its own contracts, and the boundary decision is recorded rather than implied. | docs/GATE-2-CHECKLIST.md row 2.1 |
| `REQ-0008` | `canonical:GATE-2#2.2` | yes | `COMPLETE` | The runtime declares the persistence, model and clock ports it needs and imports no web application module, so the dependency points inward. | docs/GATE-2-CHECKLIST.md row 2.2 |
| `REQ-0009` | `canonical:GATE-2#2.3` | yes | `COMPLETE` | The runtime reaches a model only through the Model Gateway contract: no provider adapter, no provider client, no provider address and no credential exists inside it. | docs/GATE-2-CHECKLIST.md row 2.3 |
| `REQ-0010` | `canonical:GATE-2#2.4` | yes | `COMPLETE` | The runtime owns no retry policy, circuit breaker, fallback chain or provider selection of its own; those belong to the gateway. | docs/GATE-2-CHECKLIST.md row 2.4 |
| `REQ-0011` | `canonical:GATE-2#2.5` | yes | `COMPLETE` | No later-Gate capability — tool execution, sandboxing, retrieval, experience storage, quality scoring or training — is implemented, simulated or faked here. | docs/GATE-2-CHECKLIST.md row 2.5 |
| `REQ-0012` | `canonical:GATE-2#2.6` | yes | `COMPLETE` | The persistence layer is a shared package the API and the worker both depend on, so one authoritative schema definition serves both processes. | docs/GATE-2-CHECKLIST.md row 2.6 |
| `REQ-0013` | `canonical:GATE-2#2.7` | yes | `COMPLETE` | The agent definition directory stops declaring itself reserved and describes what this Gate delivered. | docs/GATE-2-CHECKLIST.md row 2.7 |
| `REQ-0014` | `canonical:GATE-2#3.1` | yes | `COMPLETE` | This Gate adds its schema through a new migration and edits no migration that has already been applied. | docs/GATE-2-CHECKLIST.md row 3.1 |
| `REQ-0015` | `canonical:GATE-2#3.2` | yes | `COMPLETE` | The existing task, run, agent and agent-run entities are evolved rather than duplicated; no parallel table is created for a capability an existing table already carries. | docs/GATE-2-CHECKLIST.md row 3.2 |
| `REQ-0016` | `canonical:GATE-2#3.3` | yes | `COMPLETE` | A database created from nothing reaches the head revision by running every migration in order. | docs/GATE-2-CHECKLIST.md row 3.3 |
| `REQ-0017` | `canonical:GATE-2#3.4` | yes | `COMPLETE` | A database at the Gate 1 revision upgrades to this Gate's head without losing the rows it already holds. | docs/GATE-2-CHECKLIST.md row 3.4 |
| `REQ-0018` | `canonical:GATE-2#3.5` | yes | `COMPLETE` | The run state vocabulary the database accepts is derived from one authoritative definition rather than written twice. | docs/GATE-2-CHECKLIST.md row 3.5 |
| `REQ-0019` | `canonical:GATE-2#3.6` | yes | `COMPLETE` | The run event log is append-only: it carries a creation time, no update time, and no code path rewrites a stored event. | docs/GATE-2-CHECKLIST.md row 3.6 |
| `REQ-0020` | `canonical:GATE-2#3.7` | yes | `COMPLETE` | A tool request and its result are separate persisted rows, and a request can carry at most one result. | docs/GATE-2-CHECKLIST.md row 3.7 |
| `REQ-0021` | `canonical:GATE-2#3.8` | yes | `COMPLETE` | Agent and team profiles are persisted with their version, and a row an operator has customised is not overwritten by a later bootstrap. | docs/GATE-2-CHECKLIST.md row 3.8 |
| `REQ-0022` | `canonical:GATE-2#3.9` | yes | `COMPLETE` | An agent run names the model calls that served it, and aggregate usage is derived from them rather than counted a second time. | docs/GATE-2-CHECKLIST.md row 3.9 |
| `REQ-0023` | `canonical:GATE-2#3.10` | yes | `COMPLETE` | The task content the workflow needs to continue is persisted, and the difference from the gateway's metadata-only record is documented rather than implied. | docs/GATE-2-CHECKLIST.md row 3.10 |
| `REQ-0024` | `canonical:GATE-2#4.1` | yes | `COMPLETE` | The run lifecycle is an explicit state machine over exactly the declared states, and no state exists that the contract does not name. | docs/GATE-2-CHECKLIST.md row 4.1 |
| `REQ-0025` | `canonical:GATE-2#4.2` | yes | `COMPLETE` | A transition happens only when the transition table allows it. | docs/GATE-2-CHECKLIST.md row 4.2 |
| `REQ-0026` | `canonical:GATE-2#4.3` | yes | `COMPLETE` | An impossible transition is refused with a typed error rather than silently applied. | docs/GATE-2-CHECKLIST.md row 4.3 |
| `REQ-0027` | `canonical:GATE-2#4.4` | yes | `COMPLETE` | A terminal state is terminal: no transition leaves `SUCCEEDED`, `FAILED` or `CANCELLED`. | docs/GATE-2-CHECKLIST.md row 4.4 |
| `REQ-0028` | `canonical:GATE-2#4.5` | yes | `COMPLETE` | Re-running a task creates a new run; a terminal run is never resumed in place. | docs/GATE-2-CHECKLIST.md row 4.5 |
| `REQ-0029` | `canonical:GATE-2#4.6` | yes | `COMPLETE` | Every accepted state change records an event, so the history explains the state. | docs/GATE-2-CHECKLIST.md row 4.6 |
| `REQ-0030` | `canonical:GATE-2#4.7` | yes | `COMPLETE` | The state machine is one definition, used by the API, the workflow and the store alike. | docs/GATE-2-CHECKLIST.md row 4.7 |
| `REQ-0031` | `canonical:GATE-2#5.1` | yes | `COMPLETE` | The event vocabulary covers run creation and start, agent start and completion, model call start and completion, tool request and tool result, and the three terminal outcomes. | docs/GATE-2-CHECKLIST.md row 5.1 |
| `REQ-0032` | `canonical:GATE-2#5.2` | yes | `COMPLETE` | Events of one run carry a monotonic sequence number assigned by the store, so their order is deterministic. | docs/GATE-2-CHECKLIST.md row 5.2 |
| `REQ-0033` | `canonical:GATE-2#5.3` | yes | `COMPLETE` | A recorded event is never rewritten; a correction is a new event. | docs/GATE-2-CHECKLIST.md row 5.3 |
| `REQ-0034` | `canonical:GATE-2#5.4` | yes | `COMPLETE` | A retried append does not create a second event for the same occurrence. | docs/GATE-2-CHECKLIST.md row 5.4 |
| `REQ-0035` | `canonical:GATE-2#5.5` | yes | `COMPLETE` | An event payload carries a short verifiable summary and never a model's private reasoning or a raw prompt. | docs/GATE-2-CHECKLIST.md row 5.5 |
| `REQ-0036` | `canonical:GATE-2#5.6` | yes | `COMPLETE` | An event payload larger than the configured bound is refused rather than persisted. | docs/GATE-2-CHECKLIST.md row 5.6 |
| `REQ-0037` | `canonical:GATE-2#6.1` | yes | `COMPLETE` | An agent profile is a versioned contract carrying identity, role, description, prompt template, default route, turn limit, permitted actions and an enabled flag. | docs/GATE-2-CHECKLIST.md row 6.1 |
| `REQ-0038` | `canonical:GATE-2#6.2` | yes | `COMPLETE` | The builtin profiles are exactly the four this Gate needs to prove the runtime, and no profile exists for a capability the Gate does not exercise. | docs/GATE-2-CHECKLIST.md row 6.2 |
| `REQ-0039` | `canonical:GATE-2#6.3` | yes | `COMPLETE` | Profiles are loaded from the repository, enumerable through the runtime, and validated when they are loaded. | docs/GATE-2-CHECKLIST.md row 6.3 |
| `REQ-0040` | `canonical:GATE-2#6.4` | yes | `COMPLETE` | Loading the builtin profiles is idempotent: running it twice changes nothing the second time. | docs/GATE-2-CHECKLIST.md row 6.4 |
| `REQ-0041` | `canonical:GATE-2#6.5` | yes | `COMPLETE` | Prompt templates are versioned files under the agent definition directory, not strings concatenated across the code. | docs/GATE-2-CHECKLIST.md row 6.5 |
| `REQ-0042` | `canonical:GATE-2#6.6` | yes | `COMPLETE` | An agent run records the profile version and the prompt template hash that produced it, so its behaviour can be reproduced. | docs/GATE-2-CHECKLIST.md row 6.6 |
| `REQ-0043` | `canonical:GATE-2#6.7` | yes | `COMPLETE` | Prompt assembly keeps runtime instructions, role instructions, task content and tool results in separate labelled channels. | docs/GATE-2-CHECKLIST.md row 6.7 |
| `REQ-0044` | `canonical:GATE-2#6.8` | yes | `COMPLETE` | The user's task is carried in the user channel and is never concatenated into the system instructions. | docs/GATE-2-CHECKLIST.md row 6.8 |
| `REQ-0045` | `canonical:GATE-2#6.9` | yes | `COMPLETE` | Every executed step records run, task, agent, agent run, timestamps, model call identity, provider, model, template version and result status — and no private reasoning. | docs/GATE-2-CHECKLIST.md row 6.9 |
| `REQ-0046` | `canonical:GATE-2#6.10` | yes | `COMPLETE` | A profile declares the actions it may request, and a tool request outside that set is refused instead of persisted. | docs/GATE-2-CHECKLIST.md row 6.10 |
| `REQ-0047` | `canonical:GATE-2#7.1` | yes | `COMPLETE` | A team profile is a versioned, ordered list of stages, each naming an agent profile, its input mapping and the name of its output. | docs/GATE-2-CHECKLIST.md row 7.1 |
| `REQ-0048` | `canonical:GATE-2#7.2` | yes | `COMPLETE` | Two builtin teams exist: one single-agent and one two-stage planner and reviewer. | docs/GATE-2-CHECKLIST.md row 7.2 |
| `REQ-0049` | `canonical:GATE-2#7.3` | yes | `COMPLETE` | Team composition is configuration. Nothing in this Gate invents a team, and no model decides which agents run. | docs/GATE-2-CHECKLIST.md row 7.3 |
| `REQ-0050` | `canonical:GATE-2#7.4` | yes | `COMPLETE` | Stages execute in the order the profile declares, and each stage's output becomes explicit, named context for the next. | docs/GATE-2-CHECKLIST.md row 7.4 |
| `REQ-0051` | `canonical:GATE-2#7.5` | yes | `COMPLETE` | A previous stage's output reaches the next stage as a labelled artifact and never as an instruction. | docs/GATE-2-CHECKLIST.md row 7.5 |
| `REQ-0052` | `canonical:GATE-2#7.6` | yes | `COMPLETE` | A team run produces one agent run per stage, in order, with separate outputs. | docs/GATE-2-CHECKLIST.md row 7.6 |
| `REQ-0053` | `canonical:GATE-2#8.1` | yes | `COMPLETE` | A turn produces exactly one of a final answer, a message or a tool request. | docs/GATE-2-CHECKLIST.md row 8.1 |
| `REQ-0054` | `canonical:GATE-2#8.2` | yes | `COMPLETE` | The envelope carries an explicit version and is documented, so a consumer can detect an incompatible change instead of discovering one. | docs/GATE-2-CHECKLIST.md row 8.2 |
| `REQ-0055` | `canonical:GATE-2#8.3` | yes | `COMPLETE` | The parser is strict: an output that does not conform is rejected rather than partially accepted. | docs/GATE-2-CHECKLIST.md row 8.3 |
| `REQ-0056` | `canonical:GATE-2#8.4` | yes | `COMPLETE` | Native structured output is requested only from a model whose capability is known; otherwise the envelope is validated JSON text produced by the same contract. | docs/GATE-2-CHECKLIST.md row 8.4 |
| `REQ-0057` | `canonical:GATE-2#8.5` | yes | `COMPLETE` | No capability is asserted on a model's behalf to make a turn work. | docs/GATE-2-CHECKLIST.md row 8.5 |
| `REQ-0058` | `canonical:GATE-2#8.6` | yes | `COMPLETE` | At most one repair attempt follows an invalid turn, and it happens through the Model Gateway like any other call. | docs/GATE-2-CHECKLIST.md row 8.6 |
| `REQ-0059` | `canonical:GATE-2#8.7` | yes | `COMPLETE` | A repair call counts against the run's budget and is recorded as a repair rather than hidden. | docs/GATE-2-CHECKLIST.md row 8.7 |
| `REQ-0060` | `canonical:GATE-2#8.8` | yes | `COMPLETE` | A second invalid output ends the run with a normalised invalid-output error rather than looping. | docs/GATE-2-CHECKLIST.md row 8.8 |
| `REQ-0061` | `canonical:GATE-2#9.1` | yes | `COMPLETE` | Every inference this Gate performs travels through the Model Gateway client port and through nothing else. | docs/GATE-2-CHECKLIST.md row 9.1 |
| `REQ-0062` | `canonical:GATE-2#9.2` | yes | `COMPLETE` | A run may carry a route alias or an explicit model, and the gateway decides whether it can be served. | docs/GATE-2-CHECKLIST.md row 9.2 |
| `REQ-0063` | `canonical:GATE-2#9.3` | yes | `COMPLETE` | A run that names neither uses the configured default, and the runtime never picks a provider itself. | docs/GATE-2-CHECKLIST.md row 9.3 |
| `REQ-0064` | `canonical:GATE-2#9.4` | yes | `COMPLETE` | Every model call is attributed to the agent run that caused it. | docs/GATE-2-CHECKLIST.md row 9.4 |
| `REQ-0065` | `canonical:GATE-2#9.5` | yes | `COMPLETE` | A definitive gateway failure ends the run with a normalised error; the run never stays `RUNNING` for ever. | docs/GATE-2-CHECKLIST.md row 9.5 |
| `REQ-0066` | `canonical:GATE-2#9.6` | yes | `COMPLETE` | The runtime does not repeat a whole model call the gateway has already exhausted its own retries on. | docs/GATE-2-CHECKLIST.md row 9.6 |
| `REQ-0067` | `canonical:GATE-2#9.7` | yes | `COMPLETE` | Cost the gateway does not know is reported as unknown and never as zero. | docs/GATE-2-CHECKLIST.md row 9.7 |
| `REQ-0068` | `canonical:GATE-2#9.8` | yes | `COMPLETE` | A request the model's context cannot hold produces an explicit error rather than a silent truncation of the task. | docs/GATE-2-CHECKLIST.md row 9.8 |
| `REQ-0069` | `canonical:GATE-2#10.1` | yes | `COMPLETE` | A tool request is a persisted contract carrying identity, run, agent, name, arguments, creation time and a status from the declared vocabulary. | docs/GATE-2-CHECKLIST.md row 10.1 |
| `REQ-0070` | `canonical:GATE-2#10.2` | yes | `COMPLETE` | A tool result is a contract carrying the request it answers, a status, an output, an error and metadata. | docs/GATE-2-CHECKLIST.md row 10.2 |
| `REQ-0071` | `canonical:GATE-2#10.3` | yes | `COMPLETE` | A tool request turn persists the request, records the event and moves the run to `WAITING_FOR_TOOL`. | docs/GATE-2-CHECKLIST.md row 10.3 |
| `REQ-0072` | `canonical:GATE-2#10.4` | yes | `COMPLETE` | A paused run performs no further model call until a result arrives. | docs/GATE-2-CHECKLIST.md row 10.4 |
| `REQ-0073` | `canonical:GATE-2#10.5` | yes | `COMPLETE` | A tool name is data. Nothing in this Gate interprets it as a command, a path or an executable. | docs/GATE-2-CHECKLIST.md row 10.5 |
| `REQ-0074` | `canonical:GATE-2#10.6` | yes | `COMPLETE` | A matching tool result is persisted, recorded as an event and resumes the run. | docs/GATE-2-CHECKLIST.md row 10.6 |
| `REQ-0075` | `canonical:GATE-2#10.7` | yes | `COMPLETE` | The same tool result delivered twice resolves the request once and resumes the run once. | docs/GATE-2-CHECKLIST.md row 10.7 |
| `REQ-0076` | `canonical:GATE-2#10.8` | yes | `COMPLETE` | A tool result naming another run or an unknown request is refused. | docs/GATE-2-CHECKLIST.md row 10.8 |
| `REQ-0077` | `canonical:GATE-2#10.9` | yes | `COMPLETE` | A tool result that arrives after the run reached a terminal state is refused. | docs/GATE-2-CHECKLIST.md row 10.9 |
| `REQ-0078` | `canonical:GATE-2#10.10` | yes | `COMPLETE` | Waiting for a tool has its own configurable timeout, separate from the run deadline, and reaching it ends the run explicitly. | docs/GATE-2-CHECKLIST.md row 10.10 |
| `REQ-0079` | `canonical:GATE-2#10.11` | yes | `COMPLETE` | An automated control proves the runtime boundary contains no process, shell, filesystem-mutating or version-control execution path, and the control is a property of the boundary rather than of one file. | docs/GATE-2-CHECKLIST.md row 10.11 |
| `REQ-0080` | `canonical:GATE-2#10.12` | yes | `COMPLETE` | The division of labour with the next Gate is documented: this Gate persists and pauses, the next one executes. | docs/GATE-2-CHECKLIST.md row 10.12 |
| `REQ-0081` | `canonical:GATE-2#11.1` | yes | `COMPLETE` | Every run carries a maximum turn count, a maximum model-call count and a wall-clock deadline. | docs/GATE-2-CHECKLIST.md row 11.1 |
| `REQ-0082` | `canonical:GATE-2#11.2` | yes | `COMPLETE` | A token budget is enforced when the provider reports usage and recorded as unenforceable when it does not, rather than invented. | docs/GATE-2-CHECKLIST.md row 11.2 |
| `REQ-0083` | `canonical:GATE-2#11.3` | yes | `COMPLETE` | A budget that is zero, negative or absurd is refused when the run is validated. | docs/GATE-2-CHECKLIST.md row 11.3 |
| `REQ-0084` | `canonical:GATE-2#11.4` | yes | `COMPLETE` | Reaching any budget ends the run with a normalised budget error. | docs/GATE-2-CHECKLIST.md row 11.4 |
| `REQ-0085` | `canonical:GATE-2#11.5` | yes | `COMPLETE` | No model call happens after a budget is exhausted. | docs/GATE-2-CHECKLIST.md row 11.5 |
| `REQ-0086` | `canonical:GATE-2#11.6` | yes | `COMPLETE` | Every call to the gateway counts against the model-call budget, including a repair. | docs/GATE-2-CHECKLIST.md row 11.6 |
| `REQ-0087` | `canonical:GATE-2#11.7` | yes | `COMPLETE` | A run cannot execute an unbounded number of turns, and a run that outlives its deadline is ended rather than left running. | docs/GATE-2-CHECKLIST.md row 11.7 |
| `REQ-0088` | `canonical:GATE-2#12.1` | yes | `COMPLETE` | A run can be cancelled through the API while it is executing. | docs/GATE-2-CHECKLIST.md row 12.1 |
| `REQ-0089` | `canonical:GATE-2#12.2` | yes | `COMPLETE` | Cancellation reaches the durable workflow and stops it rather than only marking a row. | docs/GATE-2-CHECKLIST.md row 12.2 |
| `REQ-0090` | `canonical:GATE-2#12.3` | yes | `COMPLETE` | A cancelled run is terminal and records the cancellation event. | docs/GATE-2-CHECKLIST.md row 12.3 |
| `REQ-0091` | `canonical:GATE-2#12.4` | yes | `COMPLETE` | A run waiting for a tool can be cancelled, and a tool result that arrives afterwards is refused. | docs/GATE-2-CHECKLIST.md row 12.4 |
| `REQ-0092` | `canonical:GATE-2#12.5` | yes | `COMPLETE` | No model call happens after a run is cancelled. | docs/GATE-2-CHECKLIST.md row 12.5 |
| `REQ-0093` | `canonical:GATE-2#13.1` | yes | `COMPLETE` | Temporal is the durable execution engine, and no second scheduler or background orchestration loop competes with it. | docs/GATE-2-CHECKLIST.md row 13.1 |
| `REQ-0094` | `canonical:GATE-2#13.2` | yes | `COMPLETE` | Workflow code stays deterministic: every external effect — model call, persistence, notification — happens in an activity. | docs/GATE-2-CHECKLIST.md row 13.2 |
| `REQ-0095` | `canonical:GATE-2#13.3` | yes | `COMPLETE` | A worker restart while a run waits for a tool preserves the run, and the run resumes and completes when the result arrives. | docs/GATE-2-CHECKLIST.md row 13.3 |
| `REQ-0096` | `canonical:GATE-2#13.4` | yes | `COMPLETE` | An API restart does not lose a run in progress: the state lives in the store and in the workflow, never in process memory. | docs/GATE-2-CHECKLIST.md row 13.4 |
| `REQ-0097` | `canonical:GATE-2#13.5` | yes | `COMPLETE` | The workflow receives a frozen plan, so editing a profile while a run executes cannot change what that run is doing. | docs/GATE-2-CHECKLIST.md row 13.5 |
| `REQ-0098` | `canonical:GATE-2#14.1` | yes | `COMPLETE` | A versioned API creates a run, reads it, lists runs, streams its events, cancels it and accepts a tool result. | docs/GATE-2-CHECKLIST.md row 14.1 |
| `REQ-0099` | `canonical:GATE-2#14.2` | yes | `COMPLETE` | Creation answers immediately with the run identifier, its state and its creation time, without holding the request open for the run. | docs/GATE-2-CHECKLIST.md row 14.2 |
| `REQ-0100` | `canonical:GATE-2#14.3` | yes | `COMPLETE` | Creation accepts no provider credential and no provider address. | docs/GATE-2-CHECKLIST.md row 14.3 |
| `REQ-0101` | `canonical:GATE-2#14.4` | yes | `COMPLETE` | A run's status carries its state, current stage, timestamps, budget consumption, final result when there is one and error summary when there is one. | docs/GATE-2-CHECKLIST.md row 14.4 |
| `REQ-0102` | `canonical:GATE-2#14.5` | yes | `COMPLETE` | A failed run answers with an error type, a safe message, the stage that failed and the correlation identifier, and never with a traceback. | docs/GATE-2-CHECKLIST.md row 14.5 |
| `REQ-0103` | `canonical:GATE-2#14.6` | yes | `COMPLETE` | Run events are readable as a page and as a live stream. | docs/GATE-2-CHECKLIST.md row 14.6 |
| `REQ-0104` | `canonical:GATE-2#14.7` | yes | `COMPLETE` | A consumer that reconnects with a cursor receives exactly the events that follow it. | docs/GATE-2-CHECKLIST.md row 14.7 |
| `REQ-0105` | `canonical:GATE-2#14.8` | yes | `COMPLETE` | Reconnecting or retrying a read creates no new event. | docs/GATE-2-CHECKLIST.md row 14.8 |
| `REQ-0106` | `canonical:GATE-2#14.9` | yes | `COMPLETE` | The available agent profiles and team profiles are enumerable through the API. | docs/GATE-2-CHECKLIST.md row 14.9 |
| `REQ-0107` | `canonical:GATE-2#14.10` | yes | `COMPLETE` | Task input size is bounded by configuration and an oversized task is refused rather than stored. | docs/GATE-2-CHECKLIST.md row 14.10 |
| `REQ-0108` | `canonical:GATE-2#15.1` | yes | `COMPLETE` | A creation request repeated with the same idempotency key returns the run the first one created. | docs/GATE-2-CHECKLIST.md row 15.1 |
| `REQ-0109` | `canonical:GATE-2#15.2` | yes | `COMPLETE` | A creation request with a different key creates a different run. | docs/GATE-2-CHECKLIST.md row 15.2 |
| `REQ-0110` | `canonical:GATE-2#15.3` | yes | `COMPLETE` | Two runs execute at the same time without sharing state, context or events. | docs/GATE-2-CHECKLIST.md row 15.3 |
| `REQ-0111` | `canonical:GATE-2#15.4` | yes | `COMPLETE` | One task may carry two independent runs with separate results and separate events. | docs/GATE-2-CHECKLIST.md row 15.4 |
| `REQ-0112` | `canonical:GATE-2#15.5` | yes | `COMPLETE` | Identifiers use the strategy the repository already defines rather than a second format. | docs/GATE-2-CHECKLIST.md row 15.5 |
| `REQ-0113` | `canonical:GATE-2#16.1` | yes | `COMPLETE` | The runtime publishes the declared instruments for runs, turns, failures, waiting runs, budget exhaustions and cancellations. | docs/GATE-2-CHECKLIST.md row 16.1 |
| `REQ-0114` | `canonical:GATE-2#16.2` | yes | `COMPLETE` | No metric label carries a task, a prompt, a response or tool arguments, and every label is low cardinality. | docs/GATE-2-CHECKLIST.md row 16.2 |
| `REQ-0115` | `canonical:GATE-2#16.3` | yes | `COMPLETE` | Structured logs carry correlation, task, run, agent, agent run, stage, event type, model call and status when those exist. | docs/GATE-2-CHECKLIST.md row 16.3 |
| `REQ-0116` | `canonical:GATE-2#16.4` | yes | `COMPLETE` | No log record carries the whole task by default, and a secret nested inside a payload is redacted. | docs/GATE-2-CHECKLIST.md row 16.4 |
| `REQ-0117` | `canonical:GATE-2#17.1` | yes | `COMPLETE` | An operational page creates a run from a written task, a chosen team and an optional route or model. | docs/GATE-2-CHECKLIST.md row 17.1 |
| `REQ-0118` | `canonical:GATE-2#17.2` | yes | `COMPLETE` | The page follows the run's state and its events as they happen. | docs/GATE-2-CHECKLIST.md row 17.2 |
| `REQ-0119` | `canonical:GATE-2#17.3` | yes | `COMPLETE` | The page shows the final result of a successful run and the safe failure summary of a failed one. | docs/GATE-2-CHECKLIST.md row 17.3 |
| `REQ-0120` | `canonical:GATE-2#17.4` | yes | `COMPLETE` | The page can cancel a run that is executing. | docs/GATE-2-CHECKLIST.md row 17.4 |
| `REQ-0121` | `canonical:GATE-2#17.5` | yes | `COMPLETE` | A run waiting for a tool is shown as waiting, with the tool name and the pending status, and the page offers nothing that would execute it. | docs/GATE-2-CHECKLIST.md row 17.5 |
| `REQ-0122` | `canonical:GATE-2#17.6` | yes | `COMPLETE` | Model output is rendered as text, never as trusted markup. | docs/GATE-2-CHECKLIST.md row 17.6 |
| `REQ-0123` | `canonical:GATE-2#18.1` | yes | `COMPLETE` | No provider credential reaches the runtime, the store, a log record, a metric or the browser. | docs/GATE-2-CHECKLIST.md row 18.1 |
| `REQ-0124` | `canonical:GATE-2#18.2` | yes | `COMPLETE` | Tool arguments, agent output and tool results are bounded by configuration, and an oversized payload is refused. | docs/GATE-2-CHECKLIST.md row 18.2 |
| `REQ-0125` | `canonical:GATE-2#18.3` | yes | `COMPLETE` | Nothing this Gate persists becomes training data: rights default to denial and no run, event or result is marked otherwise. | docs/GATE-2-CHECKLIST.md row 18.3 |
| `REQ-0126` | `canonical:GATE-2#18.4` | yes | `COMPLETE` | The runtime asks for no private reasoning and stores none; what it keeps are short verifiable summaries. | docs/GATE-2-CHECKLIST.md row 18.4 |
| `REQ-0127` | `canonical:GATE-2#19.1` | yes | `COMPLETE` | A single-agent run executes live, through the Model Gateway, against the configured provider, and succeeds. | docs/GATE-2-CHECKLIST.md row 19.1 |
| `REQ-0128` | `canonical:GATE-2#19.2` | yes | `COMPLETE` | A planner and reviewer run executes live, in order, with separate outputs and the reviewer receiving the planner's output. | docs/GATE-2-CHECKLIST.md row 19.2 |
| `REQ-0129` | `canonical:GATE-2#19.3` | yes | `COMPLETE` | The live check uses an explicitly configured model and fails clearly when that model is not in the catalog, rather than substituting one. | docs/GATE-2-CHECKLIST.md row 19.3 |
| `REQ-0130` | `canonical:GATE-2#19.4` | yes | `COMPLETE` | The live check reports `BLOCKED` rather than `FAIL` when the local configuration carries no credential, and names the variable that is missing. | docs/GATE-2-CHECKLIST.md row 19.4 |
| `REQ-0131` | `canonical:GATE-2#19.5` | yes | `COMPLETE` | The live evidence records model provenance — provider, model, endpoint, model call identity — and no prompt or completion. | docs/GATE-2-CHECKLIST.md row 19.5 |
| `REQ-0132` | `canonical:GATE-2#20.1` | yes | `COMPLETE` | The repository's one verification command covers this Gate, in its targeted and its full mode. | docs/GATE-2-CHECKLIST.md row 20.1 |
| `REQ-0133` | `canonical:GATE-2#20.2` | yes | `COMPLETE` | A runbook documents starting the runtime, creating a run, following it, cancelling it, tool requests and results, budgets, the live smoke and troubleshooting. | docs/GATE-2-CHECKLIST.md row 20.2 |
| `REQ-0134` | `canonical:GATE-2#20.3` | yes | `COMPLETE` | The architecture, development, version and entry documents describe what this Gate delivered rather than what was planned. | docs/GATE-2-CHECKLIST.md row 20.3 |
| `REQ-0135` | `canonical:GATE-2#20.4` | yes | `COMPLETE` | The structural decisions of this Gate are recorded as ADRs. | docs/GATE-2-CHECKLIST.md row 20.4 |
| `REQ-0136` | `canonical:GATE-2#20.5` | yes | `COMPLETE` | The Gate produces its retrospective from the canonical template. | docs/GATE-2-CHECKLIST.md row 20.5 |
| `REQ-0137` | `canonical:GATE-2#20.6` | yes | `COMPLETE` | The Gate closes at the project's own internal verdict and starts no part of the Gate that follows it. | docs/GATE-2-CHECKLIST.md row 20.6 |
| `LESSON-REQ-0001` | `lesson:LSN-0001` | yes | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag | LESSON-PREFLIGHT.json LESSON-REQ-0001 |
| `LESSON-REQ-0002` | `lesson:LSN-0002` | yes | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion | LESSON-PREFLIGHT.json LESSON-REQ-0002 |
| `LESSON-REQ-0003` | `lesson:LSN-0003` | yes | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution | LESSON-PREFLIGHT.json LESSON-REQ-0003 |
| `LESSON-REQ-0004` | `lesson:LSN-0004` | yes | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked | LESSON-PREFLIGHT.json LESSON-REQ-0004 |
| `LESSON-REQ-0005` | `lesson:LSN-0005` | yes | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement | LESSON-PREFLIGHT.json LESSON-REQ-0005 |
| `LESSON-REQ-0006` | `lesson:LSN-0006` | yes | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it | LESSON-PREFLIGHT.json LESSON-REQ-0006 |
| `LESSON-REQ-0007` | `lesson:LSN-0007` | yes | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work | LESSON-PREFLIGHT.json LESSON-REQ-0007 |
| `LESSON-REQ-0008` | `lesson:LSN-0008` | yes | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff | LESSON-PREFLIGHT.json LESSON-REQ-0008 |
| `LESSON-REQ-0009` | `lesson:LSN-0009` | yes | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check | LESSON-PREFLIGHT.json LESSON-REQ-0009 |
| `LESSON-REQ-0010` | `lesson:LSN-0010` | yes | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable | LESSON-PREFLIGHT.json LESSON-REQ-0010 |
| `LESSON-REQ-0011` | `lesson:LSN-0011` | yes | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters | LESSON-PREFLIGHT.json LESSON-REQ-0011 |
| `LESSON-REQ-0012` | `lesson:LSN-0012` | yes | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them | LESSON-PREFLIGHT.json LESSON-REQ-0012 |
| `LESSON-REQ-0013` | `lesson:LSN-0013` | no | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup | LESSON-PREFLIGHT.json LESSON-REQ-0013 |
| `LESSON-REQ-0014` | `lesson:LSN-0014` | yes | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run | LESSON-PREFLIGHT.json LESSON-REQ-0014 |
| `LESSON-REQ-0015` | `lesson:LSN-0015` | yes | `COMPLETE` | Verify every positive terminal status needs one shared promotion invariant | LESSON-PREFLIGHT.json LESSON-REQ-0015 |
| `LESSON-REQ-0016` | `lesson:LSN-0016` | yes | `COMPLETE` | Verify a mandatory set must be closed by policy, never chosen by the caller | LESSON-PREFLIGHT.json LESSON-REQ-0016 |
| `LESSON-REQ-0017` | `lesson:LSN-0017` | yes | `COMPLETE` | Verify a completeness denominator must come from a source the delivery does not own | LESSON-PREFLIGHT.json LESSON-REQ-0017 |
| `LESSON-REQ-0018` | `lesson:LSN-0018` | yes | `COMPLETE` | Verify a structured reference must be resolved, not merely well typed | LESSON-PREFLIGHT.json LESSON-REQ-0018 |
| `LESSON-REQ-0019` | `lesson:LSN-0019` | yes | `COMPLETE` | Verify a derived artifact must carry a fingerprint of the inputs that produced it | LESSON-PREFLIGHT.json LESSON-REQ-0019 |
| `LESSON-REQ-0020` | `lesson:LSN-0020` | yes | `COMPLETE` | Verify evidence produced from a dirty tree needs immutable input identity | LESSON-PREFLIGHT.json LESSON-REQ-0020 |
| `LESSON-REQ-0021` | `lesson:LSN-0021` | yes | `COMPLETE` | Verify sealed history needs an anchor outside the content it describes | LESSON-PREFLIGHT.json LESSON-REQ-0021 |
| `LESSON-REQ-0022` | `lesson:LSN-0022` | yes | `COMPLETE` | Verify an authoritative count must be derived once, never maintained by hand twice | LESSON-PREFLIGHT.json LESSON-REQ-0022 |
| `LESSON-REQ-0023` | `lesson:LSN-0023` | yes | `COMPLETE` | Verify a lesson must cite a source that actually records the finding it claims | LESSON-PREFLIGHT.json LESSON-REQ-0023 |
| `LESSON-REQ-0024` | `lesson:LSN-0024` | yes | `COMPLETE` | Verify a control is finished only when its positive path has been executed, not only its refusals | LESSON-PREFLIGHT.json LESSON-REQ-0024 |
| `LESSON-REQ-0025` | `lesson:LSN-0025` | yes | `COMPLETE` | Verify a generic guardrail derives repository state instead of naming today's checkpoint | LESSON-PREFLIGHT.json LESSON-REQ-0025 |
| `LESSON-REQ-0026` | `lesson:LSN-0026` | yes | `COMPLETE` | Verify an adversarial battery without a null-mutation control proves nothing | LESSON-PREFLIGHT.json LESSON-REQ-0026 |
| `LESSON-REQ-0027` | `lesson:LSN-0027` | yes | `COMPLETE` | Verify a lesson's prose may record a residual limit but may never contradict its status | LESSON-PREFLIGHT.json LESSON-REQ-0027 |
| `LESSON-REQ-0028` | `lesson:LSN-0028` | yes | `COMPLETE` | Verify a configuration key that no code reads is a defect, not documentation | LESSON-PREFLIGHT.json LESSON-REQ-0028 |
| `LESSON-REQ-0029` | `lesson:LSN-0029` | yes | `COMPLETE` | Verify a required protocol transition must never turn a mandatory gate red | LESSON-PREFLIGHT.json LESSON-REQ-0029 |
| `LESSON-REQ-0030` | `lesson:LSN-0031` | yes | `COMPLETE` | Verify an empty applicable set is not a missing required set, and a control must tell them apart | LESSON-PREFLIGHT.json LESSON-REQ-0030 |
| `LESSON-REQ-0031` | `lesson:LSN-0032` | yes | `COMPLETE` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts | LESSON-PREFLIGHT.json LESSON-REQ-0031 |
| `LESSON-REQ-0032` | `lesson:LSN-0033` | yes | `COMPLETE` | Verify a value bound in middleware is absent in the handlers that run outside it | LESSON-PREFLIGHT.json LESSON-REQ-0032 |
| `LESSON-REQ-0033` | `lesson:LSN-0034` | yes | `COMPLETE` | Verify re-deriving what the framework already computed diverges from the framework | LESSON-PREFLIGHT.json LESSON-REQ-0033 |
| `LESSON-REQ-0034` | `lesson:LSN-0035` | yes | `COMPLETE` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work | LESSON-PREFLIGHT.json LESSON-REQ-0034 |
| `LESSON-REQ-0035` | `lesson:LSN-0036` | yes | `COMPLETE` | Verify a gate that runs inside an image measures the image, not the source | LESSON-PREFLIGHT.json LESSON-REQ-0035 |
| `LESSON-REQ-0036` | `lesson:LSN-0037` | yes | `COMPLETE` | Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves | LESSON-PREFLIGHT.json LESSON-REQ-0036 |
| `LESSON-REQ-0037` | `lesson:LSN-0038` | yes | `COMPLETE` | Verify two representations of one concept in one module disagree, and the safer one loses | LESSON-PREFLIGHT.json LESSON-REQ-0037 |
| `LESSON-REQ-0038` | `lesson:LSN-0039` | yes | `COMPLETE` | Verify a test that writes to the operational database leaves production data behind | LESSON-PREFLIGHT.json LESSON-REQ-0038 |
| `LESSON-REQ-0039` | `lesson:LSN-0040` | yes | `COMPLETE` | Verify a control that judges sealed history only runs once a successor anchors it | LESSON-PREFLIGHT.json LESSON-REQ-0039 |
| `LESSON-REQ-0040` | `lesson:LSN-0041` | yes | `COMPLETE` | Verify an editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing | LESSON-PREFLIGHT.json LESSON-REQ-0040 |
| `LESSON-REQ-0041` | `lesson:LSN-0042` | yes | `COMPLETE` | Verify a naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone | LESSON-PREFLIGHT.json LESSON-REQ-0041 |
| `LESSON-REQ-0042` | `lesson:LSN-0043` | yes | `COMPLETE` | Verify a log line is not evidence that another process is ready | LESSON-PREFLIGHT.json LESSON-REQ-0042 |
| `LESSON-REQ-0043` | `lesson:LSN-0044` | yes | `COMPLETE` | Verify a boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module | LESSON-PREFLIGHT.json LESSON-REQ-0043 |
| `LESSON-REQ-0044` | `lesson:LSN-0045` | yes | `COMPLETE` | Verify a counted test suite must declare its cases statically, because the denominator is read from the source | LESSON-PREFLIGHT.json LESSON-REQ-0044 |
| `LESSON-REQ-0045` | `lesson:LSN-0046` | yes | `COMPLETE` | Verify a timeout that cancels the task it runs in leaves nothing able to record what happened | LESSON-PREFLIGHT.json LESSON-REQ-0045 |
| `LESSON-REQ-0046` | `lesson:LSN-0047` | yes | `COMPLETE` | Verify a refusal that misnames the defect spends the only repair on the wrong correction | LESSON-PREFLIGHT.json LESSON-REQ-0046 |
| `LESSON-REQ-0047` | `lesson:LSN-0048` | yes | `COMPLETE` | Verify a state and the event that explains it, written in two commits, are written event first | LESSON-PREFLIGHT.json LESSON-REQ-0047 |
| `LESSON-REQ-0048` | `lesson:LSN-0049` | yes | `COMPLETE` | Verify a metric read the instant after the call that moved it is read before the scrape that carries it | LESSON-PREFLIGHT.json LESSON-REQ-0048 |
| `LESSON-REQ-0049` | `lesson:LSN-0050` | yes | `COMPLETE` | Verify a checkpoint sealed without naming its own tag cannot be validated from that tag | LESSON-PREFLIGHT.json LESSON-REQ-0049 |
