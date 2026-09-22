# GATE 2 — Agent Runtime Checklist

This is the canonical specification of `GATE 2 — AGENT RUNTIME`. It is the source the expected
requirement set is derived from, re-parsed at every run by `policies.canonical_requirements` and
mirrored, row for row, by `.iacode/policies/canonical-requirements.json`. A delivery for this Gate
cannot declare a smaller set, and a row cannot be dropped by editing the mirror.

The objective of the Gate is **the brain that coordinates**: a durable, observable runtime that
receives a task, creates a persistent run, selects a team of agents, assembles context, calls the
Model Gateway and nothing else, executes a sequence of agents, records every state change and every
event, survives a worker restart, enforces budgets, can be cancelled, produces a final result, and —
when an agent asks for a tool — persists the request, pauses, and waits.

The Gate deliberately does **not** execute anything. There is no shell, no filesystem mutation, no
Git, no container and no browser here. A tool request is persisted and the run pauses;
`GATE 3 — SANDBOX` is what will execute it. A component that answered a tool request with a
fabricated success would be a fake feature, which the Development Contract forbids outright.

`GATE 2` belongs to milestone `M1` and does not close it, so it ends at `INTERNAL_GATE_PASS`.

## 1. Gate specification and requirement derivation

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 1.1 | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. | `docs/GATE-2-CHECKLIST.md`, `.iacode/policies/canonical-requirements.json` | `policies.canonical_requirements` parses and mirrors the document; `Gate2CanonicalSpecificationTests`. |
| 1.2 | The closed mandatory gate registry carries every executable gate this Gate introduces. | `.iacode/policies/quality-gates.json` | A Green Keeper cycle measured against the registry's mandatory set; `Gate2MandatoryGateTests`. |
| 1.3 | Every test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence. | `.iacode/policies/test-suites.json` | `COUNTS.json` `TESTS`; `Gate2TestSuiteRegistryTests`. |
| 1.4 | The internal Red Team battery of this Gate is executable, scoped to the Agent Runtime, and records a null-mutation control. | `scripts/development-ledger/gate2_red_team.py` | `M1-INTERNAL-RED-TEAM.json` with a `VALID` `baselineControl`; `Gate2RedTeamHarnessTests`. |
| 1.5 | The reservation of the agent definition directory is consumed by the Gate that owns it, and the scope registry keeps constraining every path still owned by a later Gate. | `.iacode/policies/gate-scope.json`, `agents/README.md` | `Gate2ScopeTests`. |
| 1.6 | One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack. | `scripts/iacode/verify.py` | Verification run, targeted and full; `Gate2VerificationStageTests`. |

## 2. Runtime boundary and architecture

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 2.1 | The agent runtime is a provider-neutral library with its own contracts, and the boundary decision is recorded rather than implied. | `services/agent-runtime/src/iacode_agent_runtime/`, `docs/adr/ADR-0020-agent-runtime-boundary.md` | `test_agent_runtime_package_is_importable`; `ADR-0020`. |
| 2.2 | The runtime declares the persistence, model and clock ports it needs and imports no web application module, so the dependency points inward. | `services/agent-runtime/src/iacode_agent_runtime/ports.py` | `test_agent_runtime_imports_no_application_module`. |
| 2.3 | The runtime reaches a model only through the Model Gateway contract: no provider adapter, no provider client, no provider address and no credential exists inside it. | `services/agent-runtime/src/iacode_agent_runtime/`, `.iacode/policies/providers.json` | `test_no_provider_specific_name_escapes_the_runtime`; `test_runtime_holds_no_provider_address_or_credential`. |
| 2.4 | The runtime owns no retry policy, circuit breaker, fallback chain or provider selection of its own; those belong to the gateway. | `services/agent-runtime/src/iacode_agent_runtime/gateway_client.py` | `test_runtime_does_not_reimplement_gateway_resilience`. |
| 2.5 | No later-Gate capability — tool execution, sandboxing, retrieval, experience storage, quality scoring or training — is implemented, simulated or faked here. | the whole tree | `test_no_future_gate_capability_is_implemented_in_gate_two`. |
| 2.6 | The persistence layer is a shared package the API and the worker both depend on, so one authoritative schema definition serves both processes. | `packages/persistence/src/iacode_persistence/` | `test_persistence_package_is_the_single_schema_definition`. |
| 2.7 | The agent definition directory stops declaring itself reserved and describes what this Gate delivered. | `agents/README.md` | File content; `test_agents_readme_describes_the_delivery`. |

## 3. Persistence, migrations and the domain model

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 3.1 | This Gate adds its schema through a new migration and edits no migration that has already been applied. | `apps/api/migrations/versions/0003_agent_runtime.py` | `test_applied_migrations_are_not_edited`; `Gate2MigrationTests`. |
| 3.2 | The existing task, run, agent and agent-run entities are evolved rather than duplicated; no parallel table is created for a capability an existing table already carries. | `packages/persistence/src/iacode_persistence/models.py` | `test_no_parallel_entity_is_created`. |
| 3.3 | A database created from nothing reaches the head revision by running every migration in order. | `apps/api/migrations/` | Fresh-installation scenario; `test_fresh_database_reaches_head`. |
| 3.4 | A database at the Gate 1 revision upgrades to this Gate's head without losing the rows it already holds. | `apps/api/migrations/versions/0003_agent_runtime.py` | `test_gate1_database_upgrades_to_gate2_head`. |
| 3.5 | The run state vocabulary the database accepts is derived from one authoritative definition rather than written twice. | `packages/contracts/src/iacode_contracts/agent_runtime.py` | `Gate2MigrationTests`; `test_the_run_state_vocabulary_has_one_source`. |
| 3.6 | The run event log is append-only: it carries a creation time, no update time, and no code path rewrites a stored event. | `packages/persistence/src/iacode_persistence/models.py` | `test_run_event_log_is_append_only`. |
| 3.7 | A tool request and its result are separate persisted rows, and a request can carry at most one result. | `packages/persistence/src/iacode_persistence/models.py` | `test_a_tool_request_carries_at_most_one_result`. |
| 3.8 | Agent and team profiles are persisted with their version, and a row an operator has customised is not overwritten by a later bootstrap. | `services/agent-runtime/src/iacode_agent_runtime/registry.py` | `test_bootstrap_does_not_overwrite_a_customised_profile`. |
| 3.9 | An agent run names the model calls that served it, and aggregate usage is derived from them rather than counted a second time. | `packages/persistence/src/iacode_persistence/models.py` | `test_agent_run_usage_is_derived_from_model_calls`. |
| 3.10 | The task content the workflow needs to continue is persisted, and the difference from the gateway's metadata-only record is documented rather than implied. | `docs/runbooks/AGENT-RUNTIME.md`, `packages/persistence/src/iacode_persistence/models.py` | `test_no_raw_provider_prompt_is_persisted`; runbook section. |

## 4. The run state machine

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 4.1 | The run lifecycle is an explicit state machine over exactly the declared states, and no state exists that the contract does not name. | `services/agent-runtime/src/iacode_agent_runtime/states.py` | `test_declared_states_are_exactly_the_contract`. |
| 4.2 | A transition happens only when the transition table allows it. | `services/agent-runtime/src/iacode_agent_runtime/states.py` | `RunStateMachineTests`. |
| 4.3 | An impossible transition is refused with a typed error rather than silently applied. | `services/agent-runtime/src/iacode_agent_runtime/states.py` | `test_impossible_transition_is_refused`. |
| 4.4 | A terminal state is terminal: no transition leaves `SUCCEEDED`, `FAILED` or `CANCELLED`. | `services/agent-runtime/src/iacode_agent_runtime/states.py` | `test_terminal_state_never_transitions`. |
| 4.5 | Re-running a task creates a new run; a terminal run is never resumed in place. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_a_terminal_run_is_never_resumed`. |
| 4.6 | Every accepted state change records an event, so the history explains the state. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_every_state_change_records_an_event`. |
| 4.7 | The state machine is one definition, used by the API, the workflow and the store alike. | `services/agent-runtime/src/iacode_agent_runtime/states.py` | `test_state_machine_has_one_definition`. |

## 5. The run event log

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 5.1 | The event vocabulary covers run creation and start, agent start and completion, model call start and completion, tool request and tool result, and the three terminal outcomes. | `services/agent-runtime/src/iacode_agent_runtime/events.py` | `test_event_vocabulary_covers_the_declared_moments`. |
| 5.2 | Events of one run carry a monotonic sequence number assigned by the store, so their order is deterministic. | `services/agent-runtime/src/iacode_agent_runtime/persistence.py` | `test_event_sequence_is_monotonic_per_run`. |
| 5.3 | A recorded event is never rewritten; a correction is a new event. | `services/agent-runtime/src/iacode_agent_runtime/persistence.py` | `test_event_correction_is_a_new_event`. |
| 5.4 | A retried append does not create a second event for the same occurrence. | `services/agent-runtime/src/iacode_agent_runtime/persistence.py` | `test_duplicate_append_does_not_duplicate_the_event`. |
| 5.5 | An event payload carries a short verifiable summary and never a model's private reasoning or a raw prompt. | `services/agent-runtime/src/iacode_agent_runtime/events.py` | `test_event_payload_carries_no_private_reasoning`. |
| 5.6 | An event payload larger than the configured bound is refused rather than persisted. | `services/agent-runtime/src/iacode_agent_runtime/limits.py` | `test_oversized_event_payload_is_refused`. |

## 6. Agent profiles, prompts and provenance

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 6.1 | An agent profile is a versioned contract carrying identity, role, description, prompt template, default route, turn limit, permitted actions and an enabled flag. | `services/agent-runtime/src/iacode_agent_runtime/profiles.py` | `AgentProfileContractTests`. |
| 6.2 | The builtin profiles are exactly the four this Gate needs to prove the runtime, and no profile exists for a capability the Gate does not exercise. | `agents/profiles/` | `test_builtin_profiles_are_exactly_the_declared_set`. |
| 6.3 | Profiles are loaded from the repository, enumerable through the runtime, and validated when they are loaded. | `services/agent-runtime/src/iacode_agent_runtime/registry.py` | `AgentRegistryTests`. |
| 6.4 | Loading the builtin profiles is idempotent: running it twice changes nothing the second time. | `services/agent-runtime/src/iacode_agent_runtime/registry.py` | `test_profile_bootstrap_is_idempotent`. |
| 6.5 | Prompt templates are versioned files under the agent definition directory, not strings concatenated across the code. | `agents/prompts/` | `test_prompts_are_versioned_files`. |
| 6.6 | An agent run records the profile version and the prompt template hash that produced it, so its behaviour can be reproduced. | `services/agent-runtime/src/iacode_agent_runtime/prompts.py` | `test_agent_run_records_profile_and_template_version`. |
| 6.7 | Prompt assembly keeps runtime instructions, role instructions, task content and tool results in separate labelled channels. | `services/agent-runtime/src/iacode_agent_runtime/context.py` | `InstructionHierarchyTests`. |
| 6.8 | The user's task is carried in the user channel and is never concatenated into the system instructions. | `services/agent-runtime/src/iacode_agent_runtime/context.py` | `test_task_never_enters_the_system_channel`. |
| 6.9 | Every executed step records run, task, agent, agent run, timestamps, model call identity, provider, model, template version and result status — and no private reasoning. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `ProvenanceTests`. |
| 6.10 | A profile declares the actions it may request, and a tool request outside that set is refused instead of persisted. | `services/agent-runtime/src/iacode_agent_runtime/profiles.py` | `test_tool_request_outside_allowed_actions_is_refused`. |

## 7. Team profiles and multi-agent execution

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7.1 | A team profile is a versioned, ordered list of stages, each naming an agent profile, its input mapping and the name of its output. | `services/agent-runtime/src/iacode_agent_runtime/profiles.py` | `TeamProfileContractTests`. |
| 7.2 | Two builtin teams exist: one single-agent and one two-stage planner and reviewer. | `agents/teams/` | `test_builtin_teams_are_the_declared_set`. |
| 7.3 | Team composition is configuration. Nothing in this Gate invents a team, and no model decides which agents run. | `services/agent-runtime/src/iacode_agent_runtime/`, `agents/teams/` | `test_team_composition_is_not_inferred`. |
| 7.4 | Stages execute in the order the profile declares, and each stage's output becomes explicit, named context for the next. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `TeamExecutionTests`. |
| 7.5 | A previous stage's output reaches the next stage as a labelled artifact and never as an instruction. | `services/agent-runtime/src/iacode_agent_runtime/context.py` | `test_previous_stage_output_is_an_artifact_not_an_instruction`. |
| 7.6 | A team run produces one agent run per stage, in order, with separate outputs. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_team_run_produces_one_agent_run_per_stage`. |

## 8. The agent turn protocol

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 8.1 | A turn produces exactly one of a final answer, a message or a tool request. | `services/agent-runtime/src/iacode_agent_runtime/protocol.py` | `AgentEnvelopeTests`. |
| 8.2 | The envelope carries an explicit version and is documented, so a consumer can detect an incompatible change instead of discovering one. | `services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `docs/runbooks/AGENT-RUNTIME.md` | `test_envelope_version_is_declared`. |
| 8.3 | The parser is strict: an output that does not conform is rejected rather than partially accepted. | `services/agent-runtime/src/iacode_agent_runtime/protocol.py` | `test_invalid_envelope_is_not_accepted_silently`. |
| 8.4 | Native structured output is requested only from a model whose capability is known; otherwise the envelope is validated JSON text produced by the same contract. | `services/agent-runtime/src/iacode_agent_runtime/gateway_client.py` | `test_structured_output_is_used_only_when_the_capability_is_known`. |
| 8.5 | No capability is asserted on a model's behalf to make a turn work. | `services/agent-runtime/src/iacode_agent_runtime/gateway_client.py` | `test_runtime_never_declares_a_capability`. |
| 8.6 | At most one repair attempt follows an invalid turn, and it happens through the Model Gateway like any other call. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_repair_is_attempted_at_most_once`. |
| 8.7 | A repair call counts against the run's budget and is recorded as a repair rather than hidden. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_repair_counts_against_the_budget`. |
| 8.8 | A second invalid output ends the run with a normalised invalid-output error rather than looping. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_two_invalid_outputs_fail_the_run`. |

## 9. Model Gateway integration

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 9.1 | Every inference this Gate performs travels through the Model Gateway client port and through nothing else. | `services/agent-runtime/src/iacode_agent_runtime/gateway_client.py` | `test_every_inference_goes_through_the_gateway`. |
| 9.2 | A run may carry a route alias or an explicit model, and the gateway decides whether it can be served. | `services/agent-runtime/src/iacode_agent_runtime/contracts.py` | `test_route_and_model_override_are_passed_through`. |
| 9.3 | A run that names neither uses the configured default, and the runtime never picks a provider itself. | `services/agent-runtime/src/iacode_agent_runtime/gateway_client.py` | `test_runtime_never_chooses_a_provider`. |
| 9.4 | Every model call is attributed to the agent run that caused it. | `services/agent-runtime/src/iacode_agent_runtime/persistence.py` | `test_model_call_is_attributed_to_its_agent_run`. |
| 9.5 | A definitive gateway failure ends the run with a normalised error; the run never stays `RUNNING` for ever. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_gateway_failure_fails_the_run`. |
| 9.6 | The runtime does not repeat a whole model call the gateway has already exhausted its own retries on. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_runtime_does_not_retry_an_exhausted_call`. |
| 9.7 | Cost the gateway does not know is reported as unknown and never as zero. | `services/agent-runtime/src/iacode_agent_runtime/contracts.py` | `test_unknown_cost_is_unknown_not_zero`. |
| 9.8 | A request the model's context cannot hold produces an explicit error rather than a silent truncation of the task. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_context_overflow_is_an_explicit_error`. |

## 10. Tool requests and the Gate 3 boundary

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 10.1 | A tool request is a persisted contract carrying identity, run, agent, name, arguments, creation time and a status from the declared vocabulary. | `services/agent-runtime/src/iacode_agent_runtime/contracts.py` | `ToolRequestContractTests`. |
| 10.2 | A tool result is a contract carrying the request it answers, a status, an output, an error and metadata. | `services/agent-runtime/src/iacode_agent_runtime/contracts.py` | `ToolResultContractTests`. |
| 10.3 | A tool request turn persists the request, records the event and moves the run to `WAITING_FOR_TOOL`. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_tool_request_pauses_the_run`. |
| 10.4 | A paused run performs no further model call until a result arrives. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_a_waiting_run_makes_no_model_call`. |
| 10.5 | A tool name is data. Nothing in this Gate interprets it as a command, a path or an executable. | `services/agent-runtime/src/iacode_agent_runtime/` | `test_tool_name_is_never_interpreted`. |
| 10.6 | A matching tool result is persisted, recorded as an event and resumes the run. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_tool_result_resumes_the_run`. |
| 10.7 | The same tool result delivered twice resolves the request once and resumes the run once. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_duplicate_tool_result_is_idempotent`. |
| 10.8 | A tool result naming another run or an unknown request is refused. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_tool_result_for_another_run_is_refused`. |
| 10.9 | A tool result that arrives after the run reached a terminal state is refused. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_tool_result_after_a_terminal_state_is_refused`. |
| 10.10 | Waiting for a tool has its own configurable timeout, separate from the run deadline, and reaching it ends the run explicitly. | `services/agent-runtime/src/iacode_agent_runtime/contracts.py` | `test_tool_wait_timeout_ends_the_run`. |
| 10.11 | An automated control proves the runtime boundary contains no process, shell, filesystem-mutating or version-control execution path, and the control is a property of the boundary rather than of one file. | `tests/test_gate2_agent_runtime.py` | `ToolExecutionBoundaryTests`; null control. |
| 10.12 | The division of labour with the next Gate is documented: this Gate persists and pauses, the next one executes. | `docs/runbooks/AGENT-RUNTIME.md`, `docs/adr/ADR-0021-tool-execution-boundary.md` | `ADR-0021`; `test_gate_three_boundary_is_documented`. |

## 11. Budgets, loops and deadlines

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 11.1 | Every run carries a maximum turn count, a maximum model-call count and a wall-clock deadline. | `services/agent-runtime/src/iacode_agent_runtime/budgets.py` | `BudgetContractTests`. |
| 11.2 | A token budget is enforced when the provider reports usage and recorded as unenforceable when it does not, rather than invented. | `services/agent-runtime/src/iacode_agent_runtime/budgets.py` | `test_token_budget_is_unenforceable_without_usage`. |
| 11.3 | A budget that is zero, negative or absurd is refused when the run is validated. | `services/agent-runtime/src/iacode_agent_runtime/budgets.py` | `test_absurd_budget_is_refused`. |
| 11.4 | Reaching any budget ends the run with a normalised budget error. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_budget_exhaustion_ends_the_run`. |
| 11.5 | No model call happens after a budget is exhausted. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_no_call_after_budget_exhaustion`. |
| 11.6 | Every call to the gateway counts against the model-call budget, including a repair. | `services/agent-runtime/src/iacode_agent_runtime/budgets.py` | `test_every_gateway_call_counts`. |
| 11.7 | A run cannot execute an unbounded number of turns, and a run that outlives its deadline is ended rather than left running. | `services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `scripts/iacode/scenarios/agent_runtime_deadline.py` | `test_a_stage_turn_limit_stops_a_loop_inside_one_stage`; recorded deadline scenario run. |

## 12. Cancellation

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 12.1 | A run can be cancelled through the API while it is executing. | `apps/api/src/iacode_api/routes/agent_runs.py` | `AgentRunApiTests`. |
| 12.2 | Cancellation reaches the durable workflow and stops it rather than only marking a row. | `services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `scripts/iacode/scenarios/agent_runtime_cancellation.py` | Recorded cancellation scenario run. |
| 12.3 | A cancelled run is terminal and records the cancellation event. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_cancelled_run_is_terminal_and_recorded`. |
| 12.4 | A run waiting for a tool can be cancelled, and a tool result that arrives afterwards is refused. | `apps/api/src/iacode_api/routes/agent_runs.py`, `scripts/iacode/scenarios/agent_runtime_cancellation.py` | `test_cancel_while_waiting_for_tool`; recorded cancellation scenario run. |
| 12.5 | No model call happens after a run is cancelled. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `test_no_model_call_after_cancellation`. |

## 13. Durability

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 13.1 | Temporal is the durable execution engine, and no second scheduler or background orchestration loop competes with it. | `services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py` | `test_no_second_orchestrator_exists`. |
| 13.2 | Workflow code stays deterministic: every external effect — model call, persistence, notification — happens in an activity. | `services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py` | `WorkflowDeterminismTests`. |
| 13.3 | A worker restart while a run waits for a tool preserves the run, and the run resumes and completes when the result arrives. | `scripts/iacode/scenarios/agent_runtime_durability.py`, `services/orchestrator/rehearsal/durability.py` | Recorded durability scenario run. |
| 13.4 | An API restart does not lose a run in progress: the state lives in the store and in the workflow, never in process memory. | `apps/api/src/iacode_api/routes/agent_runs.py`, `scripts/iacode/scenarios/agent_runtime_durability.py` | `test_run_state_is_not_held_in_process_memory`; recorded durability scenario run. |
| 13.5 | The workflow receives a frozen plan, so editing a profile while a run executes cannot change what that run is doing. | `services/agent-runtime/src/iacode_agent_runtime/contracts.py` | `test_workflow_plan_is_frozen_at_creation`. |

## 14. The HTTP API and the event stream

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 14.1 | A versioned API creates a run, reads it, lists runs, streams its events, cancels it and accepts a tool result. | `apps/api/src/iacode_api/routes/agent_runs.py` | `AgentRunApiTests`. |
| 14.2 | Creation answers immediately with the run identifier, its state and its creation time, without holding the request open for the run. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_creation_answers_immediately`. |
| 14.3 | Creation accepts no provider credential and no provider address. | `packages/contracts/src/iacode_contracts/agent_runtime.py` | `test_creation_cannot_supply_a_credential_or_address`. |
| 14.4 | A run's status carries its state, current stage, timestamps, budget consumption, final result when there is one and error summary when there is one. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_run_status_carries_the_declared_fields`. |
| 14.5 | A failed run answers with an error type, a safe message, the stage that failed and the correlation identifier, and never with a traceback. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_failure_summary_is_safe`. |
| 14.6 | Run events are readable as a page and as a live stream. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_events_are_readable_as_page_and_stream`. |
| 14.7 | A consumer that reconnects with a cursor receives exactly the events that follow it. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_event_stream_resumes_from_a_cursor`. |
| 14.8 | Reconnecting or retrying a read creates no new event. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_reconnection_creates_no_event`. |
| 14.9 | The available agent profiles and team profiles are enumerable through the API. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_profiles_and_teams_are_enumerable`. |
| 14.10 | Task input size is bounded by configuration and an oversized task is refused rather than stored. | `services/agent-runtime/src/iacode_agent_runtime/limits.py` | `test_oversized_task_is_refused`. |

## 15. Idempotency and concurrency

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 15.1 | A creation request repeated with the same idempotency key returns the run the first one created. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_same_idempotency_key_returns_the_same_run`. |
| 15.2 | A creation request with a different key creates a different run. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_a_different_key_creates_a_new_run`. |
| 15.3 | Two runs execute at the same time without sharing state, context or events. | `services/agent-runtime/src/iacode_agent_runtime/engine.py` | `ConcurrentRunIsolationTests`. |
| 15.4 | One task may carry two independent runs with separate results and separate events. | `apps/api/src/iacode_api/routes/agent_runs.py` | `test_one_task_can_have_two_independent_runs`. |
| 15.5 | Identifiers use the strategy the repository already defines rather than a second format. | `services/agent-runtime/src/iacode_agent_runtime/contracts.py` | `test_identifiers_use_the_existing_strategy`. |

## 16. Observability

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 16.1 | The runtime publishes the declared instruments for runs, turns, failures, waiting runs, budget exhaustions and cancellations. | `services/agent-runtime/src/iacode_agent_runtime/telemetry.py` | `AgentRuntimeMetricsTests`. |
| 16.2 | No metric label carries a task, a prompt, a response or tool arguments, and every label is low cardinality. | `services/agent-runtime/src/iacode_agent_runtime/telemetry.py` | `test_no_metric_label_carries_content`. |
| 16.3 | Structured logs carry correlation, task, run, agent, agent run, stage, event type, model call and status when those exist. | `services/agent-runtime/src/iacode_agent_runtime/telemetry.py` | `test_logs_carry_the_declared_identifiers`. |
| 16.4 | No log record carries the whole task by default, and a secret nested inside a payload is redacted. | `services/agent-runtime/src/iacode_agent_runtime/telemetry.py` | `test_nested_secret_is_redacted_in_runtime_logs`. |

## 17. The operational frontend

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 17.1 | An operational page creates a run from a written task, a chosen team and an optional route or model. | `apps/web/src/app/agent-runtime/agent-runtime.ts` | `apps/web/src/app/agent-runtime/agent-runtime.spec.ts`; browser smoke. |
| 17.2 | The page follows the run's state and its events as they happen. | `apps/web/src/app/agent-runtime/agent-runtime.service.ts` | `apps/web/src/app/agent-runtime/agent-runtime.service.spec.ts`. |
| 17.3 | The page shows the final result of a successful run and the safe failure summary of a failed one. | `apps/web/src/app/agent-runtime/agent-runtime.html` | `apps/web/src/app/agent-runtime/agent-runtime.spec.ts`. |
| 17.4 | The page can cancel a run that is executing. | `apps/web/src/app/agent-runtime/agent-runtime.ts` | `apps/web/src/app/agent-runtime/agent-runtime.spec.ts`. |
| 17.5 | A run waiting for a tool is shown as waiting, with the tool name and the pending status, and the page offers nothing that would execute it. | `apps/web/src/app/agent-runtime/agent-runtime.html` | `apps/web/src/app/agent-runtime/agent-runtime.spec.ts`; `test_the_page_offers_nothing_that_would_execute_a_tool`. |
| 17.6 | Model output is rendered as text, never as trusted markup. | `apps/web/src/app/agent-runtime/agent-runtime.html`, `apps/web/src/app/agent-runtime/agent-runtime.spec.ts` | `test_model_output_is_not_rendered_as_markup`. |

## 18. Security, limits and rights

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 18.1 | No provider credential reaches the runtime, the store, a log record, a metric or the browser. | `services/agent-runtime/src/iacode_agent_runtime/` | `AgentRuntimeSecretContainmentTests`. |
| 18.2 | Tool arguments, agent output and tool results are bounded by configuration, and an oversized payload is refused. | `services/agent-runtime/src/iacode_agent_runtime/limits.py` | `PayloadLimitTests`. |
| 18.3 | Nothing this Gate persists becomes training data: rights default to denial and no run, event or result is marked otherwise. | `packages/persistence/src/iacode_persistence/models.py` | `test_nothing_this_gate_persists_is_training_eligible`. |
| 18.4 | The runtime asks for no private reasoning and stores none; what it keeps are short verifiable summaries. | `services/agent-runtime/src/iacode_agent_runtime/` | `test_no_chain_of_thought_is_requested_or_stored`. |

## 19. Live provider evidence

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 19.1 | A single-agent run executes live, through the Model Gateway, against the configured provider, and succeeds. | `scripts/iacode/agent_runtime_smoke.py` | Recorded live smoke run reporting `PASS`. |
| 19.2 | A planner and reviewer run executes live, in order, with separate outputs and the reviewer receiving the planner's output. | `scripts/iacode/agent_runtime_smoke.py` | Recorded live smoke run reporting `PASS`. |
| 19.3 | The live check uses an explicitly configured model and fails clearly when that model is not in the catalog, rather than substituting one. | `scripts/iacode/agent_runtime_smoke.py` | `test_live_smoke_never_substitutes_a_model`. |
| 19.4 | The live check reports `BLOCKED` rather than `FAIL` when the local configuration carries no credential, and names the variable that is missing. | `scripts/iacode/agent_runtime_smoke.py` | `test_live_smoke_blocks_without_a_credential`. |
| 19.5 | The live evidence records model provenance — provider, model, endpoint, model call identity — and no prompt or completion. | `scripts/iacode/agent_runtime_smoke.py` | Live smoke report contents. |

## 20. Verification, documentation and decisions

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 20.1 | The repository's one verification command covers this Gate, in its targeted and its full mode. | `scripts/iacode/verify.py` | `Gate2VerificationStageTests`; full verification run recorded in `VERIFICATION-REPORT.json`. |
| 20.2 | A runbook documents starting the runtime, creating a run, following it, cancelling it, tool requests and results, budgets, the live smoke and troubleshooting. | `docs/runbooks/AGENT-RUNTIME.md` | File content; `test_agent_runtime_runbook_covers_the_declared_topics`. |
| 20.3 | The architecture, development, version and entry documents describe what this Gate delivered rather than what was planned. | `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/VERSIONS.md`, `README.md`, `START-HERE.md` | `Gate2DocumentationTests`. |
| 20.4 | The structural decisions of this Gate are recorded as ADRs. | `docs/adr/` | `ADR-0020`, `ADR-0021`, `ADR-0022`; `Gate2AdrTests`. |
| 20.5 | The Gate produces its retrospective from the canonical template. | `.iacode/memory/retrospectives/GATE-2-CP-0001.md` | `validate_lessons.py`; the retrospective is present and follows `.iacode/templates/retrospective/TEMPLATE.md`. |
| 20.6 | The Gate closes at the project's own internal verdict and starts no part of the Gate that follows it. | `docs/checkpoints/GATE-2-CP-0001/STATE.json` | Checkpoint validation; `Gate2ScopeTests`. |
