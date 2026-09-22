# Delivery Completeness Report

Result: `PASS`

- Checkpoint: `GATE-2-CP-0002`
- Matrix: `REQUIREMENTS-MATRIX.json`
- Generated: `2026-09-22T21:24:29Z`
- Auditor: Delivery Completeness Validator
- Expected set: derived by policies.expected_requirement_refs from the canonical Gate specification, the lesson preflight and the open independent audit findings and attacks

## Counts

| Metric | Value |
|---|---|
| expectedRequirements | 186 |
| totalRequirements | 186 |
| mandatoryRequirements | 185 |
| complete | 186 |
| partial | 0 |
| missing | 0 |
| notApplicable | 0 |
| inProgress | 0 |
| notStarted | 0 |
| coveragePercent | 100.00 |
| evidenceCoveragePercent | 100.00 |

## Findings

No finding. Every requirement is satisfied and every evidence reference resolved.

## Per-requirement audit

| ID | Mandatory | Status | Evidence references |
|---|---|---|---|
| `REQ-0001` | yes | `COMPLETE` | `file:.iacode/policies/canonical-requirements.json`, `test:Gate2CanonicalSpecificationTests`, `file:docs/GATE-2-CHECKLIST.md` |
| `REQ-0002` | yes | `COMPLETE` | `file:.iacode/policies/quality-gates.json`, `test:Gate2MandatoryGateTests` |
| `REQ-0003` | yes | `COMPLETE` | `file:.iacode/policies/test-suites.json`, `test:Gate2TestSuiteRegistryTests` |
| `REQ-0004` | yes | `COMPLETE` | `file:scripts/development-ledger/gate2_red_team.py`, `test:Gate2RedTeamHarnessTests` |
| `REQ-0005` | yes | `COMPLETE` | `file:.iacode/policies/gate-scope.json`, `test:Gate2ScopeTests`, `file:agents/README.md` |
| `REQ-0006` | yes | `COMPLETE` | `file:scripts/iacode/verify.py`, `test:Gate2VerificationStageTests` |
| `REQ-0007` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`, `test:test_agent_runtime_package_is_importable`, `file:docs/adr/ADR-0020-agent-runtime-boundary.md` |
| `REQ-0008` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/ports.py`, `test:test_agent_runtime_imports_no_application_module` |
| `REQ-0009` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`, `file:.iacode/policies/providers.json`, `test:test_no_provider_specific_name_escapes_the_runtime`, `test:test_runtime_holds_no_provider_address_or_credential` |
| `REQ-0010` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`, `test:test_runtime_does_not_reimplement_gateway_resilience` |
| `REQ-0011` | yes | `COMPLETE` | `test:test_no_future_gate_capability_is_implemented_in_gate_two` |
| `REQ-0012` | yes | `COMPLETE` | `file:packages/persistence/src/iacode_persistence/__init__.py`, `test:test_persistence_package_is_the_single_schema_definition` |
| `REQ-0013` | yes | `COMPLETE` | `test:test_agents_readme_describes_the_delivery`, `file:agents/README.md` |
| `REQ-0014` | yes | `COMPLETE` | `file:apps/api/migrations/versions/0003_agent_runtime.py`, `test:test_applied_migrations_are_not_edited`, `test:Gate2MigrationTests` |
| `REQ-0015` | yes | `COMPLETE` | `file:packages/persistence/src/iacode_persistence/models.py`, `test:test_no_parallel_entity_is_created` |
| `REQ-0016` | yes | `COMPLETE` | `test:test_fresh_database_reaches_head` |
| `REQ-0017` | yes | `COMPLETE` | `file:apps/api/migrations/versions/0003_agent_runtime.py`, `test:test_gate1_database_upgrades_to_gate2_head` |
| `REQ-0018` | yes | `COMPLETE` | `file:packages/contracts/src/iacode_contracts/agent_runtime.py`, `test:Gate2MigrationTests`, `test:test_the_run_state_vocabulary_has_one_source` |
| `REQ-0019` | yes | `COMPLETE` | `file:packages/persistence/src/iacode_persistence/models.py`, `test:test_run_event_log_is_append_only` |
| `REQ-0020` | yes | `COMPLETE` | `file:packages/persistence/src/iacode_persistence/models.py`, `test:test_a_tool_request_carries_at_most_one_result` |
| `REQ-0021` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/registry.py`, `test:test_bootstrap_does_not_overwrite_a_customised_profile` |
| `REQ-0022` | yes | `COMPLETE` | `file:packages/persistence/src/iacode_persistence/models.py`, `test:test_agent_run_usage_is_derived_from_model_calls` |
| `REQ-0023` | yes | `COMPLETE` | `file:packages/persistence/src/iacode_persistence/models.py`, `test:test_no_raw_provider_prompt_is_persisted`, `file:docs/runbooks/AGENT-RUNTIME.md` |
| `REQ-0024` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/states.py`, `test:test_declared_states_are_exactly_the_contract` |
| `REQ-0025` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/states.py`, `test:RunStateMachineTests` |
| `REQ-0026` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/states.py`, `test:test_impossible_transition_is_refused` |
| `REQ-0027` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/states.py`, `test:test_terminal_state_never_transitions` |
| `REQ-0028` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_a_terminal_run_is_never_resumed` |
| `REQ-0029` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_every_state_change_records_an_event` |
| `REQ-0030` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/states.py`, `test:test_state_machine_has_one_definition` |
| `REQ-0031` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/events.py`, `test:test_event_vocabulary_covers_the_declared_moments` |
| `REQ-0032` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`, `test:test_event_sequence_is_monotonic_per_run` |
| `REQ-0033` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`, `test:test_event_correction_is_a_new_event` |
| `REQ-0034` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`, `test:test_duplicate_append_does_not_duplicate_the_event` |
| `REQ-0035` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/events.py`, `test:test_event_payload_carries_no_private_reasoning` |
| `REQ-0036` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/limits.py`, `test:test_oversized_event_payload_is_refused` |
| `REQ-0037` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/profiles.py`, `test:AgentProfileContractTests` |
| `REQ-0038` | yes | `COMPLETE` | `test:test_builtin_profiles_are_exactly_the_declared_set` |
| `REQ-0039` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/registry.py`, `test:AgentRegistryTests` |
| `REQ-0040` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/registry.py`, `test:test_profile_bootstrap_is_idempotent` |
| `REQ-0041` | yes | `COMPLETE` | `test:test_prompts_are_versioned_files` |
| `REQ-0042` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/prompts.py`, `test:test_agent_run_records_profile_and_template_version` |
| `REQ-0043` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/context.py`, `test:InstructionHierarchyTests` |
| `REQ-0044` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/context.py`, `test:test_task_never_enters_the_system_channel` |
| `REQ-0045` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:ProvenanceTests` |
| `REQ-0046` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/profiles.py`, `test:test_tool_request_outside_allowed_actions_is_refused` |
| `REQ-0047` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/profiles.py`, `test:TeamProfileContractTests` |
| `REQ-0048` | yes | `COMPLETE` | `test:test_builtin_teams_are_the_declared_set` |
| `REQ-0049` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`, `test:test_team_composition_is_not_inferred` |
| `REQ-0050` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:TeamExecutionTests` |
| `REQ-0051` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/context.py`, `test:test_previous_stage_output_is_an_artifact_not_an_instruction` |
| `REQ-0052` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_team_run_produces_one_agent_run_per_stage` |
| `REQ-0053` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `test:AgentEnvelopeTests` |
| `REQ-0054` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `test:test_envelope_version_is_declared`, `file:docs/runbooks/AGENT-RUNTIME.md` |
| `REQ-0055` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `test:test_invalid_envelope_is_not_accepted_silently` |
| `REQ-0056` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`, `test:test_structured_output_is_used_only_when_the_capability_is_known` |
| `REQ-0057` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`, `test:test_runtime_never_declares_a_capability` |
| `REQ-0058` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_repair_is_attempted_at_most_once` |
| `REQ-0059` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_repair_counts_against_the_budget` |
| `REQ-0060` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_two_invalid_outputs_fail_the_run` |
| `REQ-0061` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`, `test:test_every_inference_goes_through_the_gateway` |
| `REQ-0062` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`, `test:test_route_and_model_override_are_passed_through` |
| `REQ-0063` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/gateway_client.py`, `test:test_runtime_never_chooses_a_provider` |
| `REQ-0064` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`, `test:test_model_call_is_attributed_to_its_agent_run` |
| `REQ-0065` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_gateway_failure_fails_the_run` |
| `REQ-0066` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_runtime_does_not_retry_an_exhausted_call` |
| `REQ-0067` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`, `test:test_unknown_cost_is_unknown_not_zero` |
| `REQ-0068` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_context_overflow_is_an_explicit_error` |
| `REQ-0069` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`, `test:ToolRequestContractTests` |
| `REQ-0070` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`, `test:ToolResultContractTests` |
| `REQ-0071` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_tool_request_pauses_the_run` |
| `REQ-0072` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_a_waiting_run_makes_no_model_call` |
| `REQ-0073` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`, `test:test_tool_name_is_never_interpreted` |
| `REQ-0074` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_tool_result_resumes_the_run` |
| `REQ-0075` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_duplicate_tool_result_is_idempotent` |
| `REQ-0076` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_tool_result_for_another_run_is_refused` |
| `REQ-0077` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_tool_result_after_a_terminal_state_is_refused` |
| `REQ-0078` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`, `test:test_tool_wait_timeout_ends_the_run` |
| `REQ-0079` | yes | `COMPLETE` | `file:tests/test_gate2_agent_runtime.py`, `test:ToolExecutionBoundaryTests` |
| `REQ-0080` | yes | `COMPLETE` | `test:test_gate_three_boundary_is_documented`, `file:docs/runbooks/AGENT-RUNTIME.md`, `file:docs/adr/ADR-0021-tool-execution-boundary.md` |
| `REQ-0081` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`, `test:BudgetContractTests` |
| `REQ-0082` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`, `test:test_token_budget_is_unenforceable_without_usage` |
| `REQ-0083` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`, `test:test_absurd_budget_is_refused` |
| `REQ-0084` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_budget_exhaustion_ends_the_run` |
| `REQ-0085` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_no_call_after_budget_exhaustion` |
| `REQ-0086` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/budgets.py`, `test:test_every_gateway_call_counts` |
| `REQ-0087` | yes | `COMPLETE` | `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:scripts/iacode/scenarios/agent_runtime_deadline.py`, `test:test_a_stage_turn_limit_stops_a_loop_inside_one_stage` |
| `REQ-0088` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:AgentRunApiTests` |
| `REQ-0089` | yes | `COMPLETE` | `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:scripts/iacode/scenarios/agent_runtime_cancellation.py` |
| `REQ-0090` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_cancelled_run_is_terminal_and_recorded` |
| `REQ-0091` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `file:scripts/iacode/scenarios/agent_runtime_cancellation.py`, `test:test_cancel_while_waiting_for_tool` |
| `REQ-0092` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:test_no_model_call_after_cancellation` |
| `REQ-0093` | yes | `COMPLETE` | `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `test:test_no_second_orchestrator_exists` |
| `REQ-0094` | yes | `COMPLETE` | `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `test:WorkflowDeterminismTests` |
| `REQ-0095` | yes | `COMPLETE` | `file:scripts/iacode/scenarios/agent_runtime_durability.py`, `file:services/orchestrator/rehearsal/durability.py` |
| `REQ-0096` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `file:scripts/iacode/scenarios/agent_runtime_durability.py`, `test:test_run_state_is_not_held_in_process_memory` |
| `REQ-0097` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`, `test:test_workflow_plan_is_frozen_at_creation` |
| `REQ-0098` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:AgentRunApiTests` |
| `REQ-0099` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_creation_answers_immediately` |
| `REQ-0100` | yes | `COMPLETE` | `file:packages/contracts/src/iacode_contracts/agent_runtime.py`, `test:test_creation_cannot_supply_a_credential_or_address` |
| `REQ-0101` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_run_status_carries_the_declared_fields` |
| `REQ-0102` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_failure_summary_is_safe` |
| `REQ-0103` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_events_are_readable_as_page_and_stream` |
| `REQ-0104` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_event_stream_resumes_from_a_cursor` |
| `REQ-0105` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_reconnection_creates_no_event` |
| `REQ-0106` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_profiles_and_teams_are_enumerable` |
| `REQ-0107` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/limits.py`, `test:test_oversized_task_is_refused` |
| `REQ-0108` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_same_idempotency_key_returns_the_same_run` |
| `REQ-0109` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_a_different_key_creates_a_new_run` |
| `REQ-0110` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `test:ConcurrentRunIsolationTests` |
| `REQ-0111` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_one_task_can_have_two_independent_runs` |
| `REQ-0112` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/contracts.py`, `test:test_identifiers_use_the_existing_strategy` |
| `REQ-0113` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/telemetry.py`, `test:AgentRuntimeMetricsTests` |
| `REQ-0114` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/telemetry.py`, `test:test_no_metric_label_carries_content` |
| `REQ-0115` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/telemetry.py`, `test:test_logs_carry_the_declared_identifiers` |
| `REQ-0116` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/telemetry.py`, `test:test_nested_secret_is_redacted_in_runtime_logs` |
| `REQ-0117` | yes | `COMPLETE` | `file:apps/web/src/app/agent-runtime/agent-runtime.ts`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts` |
| `REQ-0118` | yes | `COMPLETE` | `file:apps/web/src/app/agent-runtime/agent-runtime.service.ts`, `file:apps/web/src/app/agent-runtime/agent-runtime.service.spec.ts` |
| `REQ-0119` | yes | `COMPLETE` | `file:apps/web/src/app/agent-runtime/agent-runtime.html`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts` |
| `REQ-0120` | yes | `COMPLETE` | `file:apps/web/src/app/agent-runtime/agent-runtime.ts`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts` |
| `REQ-0121` | yes | `COMPLETE` | `file:apps/web/src/app/agent-runtime/agent-runtime.html`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts`, `test:test_the_page_offers_nothing_that_would_execute_a_tool` |
| `REQ-0122` | yes | `COMPLETE` | `file:apps/web/src/app/agent-runtime/agent-runtime.html`, `file:apps/web/src/app/agent-runtime/agent-runtime.spec.ts`, `test:test_model_output_is_not_rendered_as_markup` |
| `REQ-0123` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`, `test:AgentRuntimeSecretContainmentTests` |
| `REQ-0124` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/limits.py`, `test:PayloadLimitTests` |
| `REQ-0125` | yes | `COMPLETE` | `file:packages/persistence/src/iacode_persistence/models.py`, `test:test_nothing_this_gate_persists_is_training_eligible` |
| `REQ-0126` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/__init__.py`, `test:test_no_chain_of_thought_is_requested_or_stored` |
| `REQ-0127` | yes | `COMPLETE` | `file:scripts/iacode/agent_runtime_smoke.py`, `command:cmd-0006`, `command:cmd-0005` |
| `REQ-0128` | yes | `COMPLETE` | `file:scripts/iacode/agent_runtime_smoke.py`, `command:cmd-0006` |
| `REQ-0129` | yes | `COMPLETE` | `file:scripts/iacode/agent_runtime_smoke.py`, `test:test_live_smoke_never_substitutes_a_model` |
| `REQ-0130` | yes | `COMPLETE` | `file:scripts/iacode/agent_runtime_smoke.py`, `test:test_live_smoke_blocks_without_a_credential` |
| `REQ-0131` | yes | `COMPLETE` | `file:scripts/iacode/agent_runtime_smoke.py`, `command:cmd-0006`, `command:cmd-0007` |
| `REQ-0132` | yes | `COMPLETE` | `file:scripts/iacode/verify.py`, `test:Gate2VerificationStageTests` |
| `REQ-0133` | yes | `COMPLETE` | `test:test_agent_runtime_runbook_covers_the_declared_topics`, `file:docs/runbooks/AGENT-RUNTIME.md` |
| `REQ-0134` | yes | `COMPLETE` | `test:Gate2DocumentationTests`, `file:docs/ARCHITECTURE.md`, `file:docs/DEVELOPMENT.md`, `file:docs/VERSIONS.md`, `file:README.md`, `file:START-HERE.md` |
| `REQ-0135` | yes | `COMPLETE` | `test:Gate2AdrTests` |
| `REQ-0136` | yes | `COMPLETE` | `file:.iacode/memory/retrospectives/GATE-2-CP-0001.md`, `file:.iacode/templates/retrospective/TEMPLATE.md` |
| `REQ-0137` | yes | `COMPLETE` | `test:Gate2ScopeTests`, `file:docs/checkpoints/GATE-2-CP-0001/STATE.json` |
| `LESSON-REQ-0001` | yes | `COMPLETE` | `test:DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates`, `test:DetachedHeadValidationTests.test_detached_head_at_wrong_commit_fails` |
| `LESSON-REQ-0002` | yes | `COMPLETE` | `test:DeltaInventoryTests.test_removed_manifest_entry_fails`, `test:DeltaInventoryTests.test_silent_tracked_modification_fails` |
| `LESSON-REQ-0003` | yes | `COMPLETE` | `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded` |
| `LESSON-REQ-0004` | yes | `COMPLETE` | `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`, `test:ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected` |
| `LESSON-REQ-0005` | yes | `COMPLETE` | `test:QualityEvidenceTests.test_pass_without_evidence_fails`, `test:QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension` |
| `LESSON-REQ-0006` | yes | `COMPLETE` | `test:SetupChecklistTests.test_checklist_exists_and_is_referenced`, `test:SetupChecklistTests.test_documentation_links_resolve` |
| `LESSON-REQ-0007` | yes | `COMPLETE` | `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`, `test:ExternalAttestationTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough`, `test:SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass`, `test:DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review` |
| `LESSON-REQ-0008` | yes | `COMPLETE` | `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`, `test:DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `test:DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review` |
| `LESSON-REQ-0009` | yes | `COMPLETE` | `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_the_policy_declares_a_non_empty_closed_set`, `test:GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `test:DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `test:DeliveryAssuranceGateTests.test_red_tests_block_review` |
| `LESSON-REQ-0010` | yes | `COMPLETE` | `test:CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`, `test:CommandInputBindingTests.test_a_clean_tree_claim_is_checked_against_the_declared_commit`, `test:CommandReproducibilityTests.test_bare_script_name_is_rejected`, `test:CommandReproducibilityTests.test_unresolvable_script_path_is_rejected` |
| `LESSON-REQ-0011` | yes | `COMPLETE` | `test:DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`, `test:GateRunnerTests.test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test:GateRunnerTests.test_the_refresh_has_one_definition`, `test:GateRunnerTests.test_no_other_module_executes_the_mandatory_gate_set` |
| `LESSON-REQ-0012` | yes | `COMPLETE` | `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`, `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`, `test:HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates` |
| `LESSON-REQ-0013` | no | `COMPLETE` | `file:docs/TOOL-CAPABILITIES.md` |
| `LESSON-REQ-0014` | yes | `COMPLETE` | `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected`, `test:SealChronologyTests.test_a_missing_post_commit_validation_is_rejected`, `test:SealChronologyTests.test_a_dirty_tree_validation_is_not_evidence_of_a_sealed_commit` |
| `LESSON-REQ-0015` | yes | `COMPLETE` | `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`, `test:PromotionInvariantTests.test_a_terminal_status_requires_an_independent_verdict` |
| `LESSON-REQ-0016` | yes | `COMPLETE` | `test:MandatoryGatePolicyTests.test_a_cycle_missing_one_mandatory_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_a_mandatory_gate_that_exited_nonzero_is_rejected`, `test:MandatoryGatePolicyTests.test_a_pass_measured_before_a_source_change_is_stale` |
| `LESSON-REQ-0017` | yes | `COMPLETE` | `test:ExpectedRequirementSetTests.test_the_expected_set_is_derived_from_the_canonical_sources`, `test:ExpectedRequirementSetTests.test_the_checklist_is_reparsed_rather_than_trusted`, `test:ExpectedRequirementSetTests.test_a_downgraded_matrix_cannot_escape_the_comparison`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected` |
| `LESSON-REQ-0018` | yes | `COMPLETE` | `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`, `test:LessonResolutionTests.test_an_invariant_control_must_be_defined_in_the_tooling`, `test:LessonResolutionTests.test_lesson_evidence_must_resolve` |
| `LESSON-REQ-0019` | yes | `COMPLETE` | `test:PreflightFreshnessTests.test_a_changed_fingerprint_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_preflight_from_another_gate_is_refused` |
| `LESSON-REQ-0020` | yes | `COMPLETE` | `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically`, `test:CommandInputBindingTests.test_a_digest_that_omits_an_input_is_rejected` |
| `LESSON-REQ-0021` | yes | `COMPLETE` | `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`, `test:IntegrityAnchorTests.test_a_recomputed_anchor_hash_must_match_its_fields`, `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected` |
| `LESSON-REQ-0022` | yes | `COMPLETE` | `test:DerivedCountTests.test_a_forged_count_is_rejected`, `test:DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_the_cardinality_of_a_derived_set`, `test:SourceCardinalityPolicyTests` |
| `LESSON-REQ-0023` | yes | `COMPLETE` | `test:LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected`, `test:LessonProvenanceTests.test_a_nonexistent_checkpoint_is_rejected` |
| `LESSON-REQ-0024` | yes | `COMPLETE` | `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed` |
| `LESSON-REQ-0025` | yes | `COMPLETE` | `test:IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint`, `test:SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain` |
| `LESSON-REQ-0026` | yes | `COMPLETE` | `test:InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected`, `test:InternalAssuranceTests.test_a_failed_null_mutation_control_cannot_produce_a_pass` |
| `LESSON-REQ-0027` | yes | `COMPLETE` | `test:MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded`, `test:MemoryPolicyDocumentTests.test_the_repository_memory_has_no_status_contradiction` |
| `LESSON-REQ-0028` | yes | `COMPLETE` | `test:MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared`, `test:MemoryPolicyDocumentTests.test_the_declared_policy_validates_against_its_schema`, `test:test_configuration.test_every_declared_key_is_read_somewhere`, `test:test_configuration.test_test_settings_ignore_the_ambient_environment` |
| `LESSON-REQ-0029` | yes | `COMPLETE` | `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `test:SuccessorDurabilityTests.test_a_missing_anchor_is_still_detected_after_the_chain_advances`, `test:GateTransitionSimulationTests.test_the_first_checkpoint_of_the_next_gate_reaches_review_readiness`, `test:GateTransitionSimulationTests.test_its_mirror_audit_passes_with_the_empty_dimensions_inapplicable` |
| `LESSON-REQ-0030` | yes | `COMPLETE` | `test:MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`, `test:MirrorApplicabilitySemanticsTests.test_a_missing_required_set_fails_rather_than_being_inapplicable`, `test:MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed` |
| `LESSON-REQ-0031` | yes | `COMPLETE` | `test:Gate1ScopeTests.test_no_future_gate_capability_is_implemented`, `test:MonorepoStructureTests.test_no_future_gate_capability_is_implemented`, `test:MonorepoStructureTests.test_the_scope_control_detects_an_implementation`, `test:MonorepoStructureTests.test_the_scope_control_ignores_a_gate_that_has_already_run`, `test:ExpectedRequirementSetTests.test_expected_set_names_the_gate_specification`, `test:AssuranceScopeTests.test_assurance_scope_covers_the_runtime_source`, `test:TestSuiteRegistryTests.test_declared_suites_are_discovered` |
| `LESSON-REQ-0032` | yes | `COMPLETE` | `test:test_errors_and_correlation.test_internal_error_still_carries_a_correlation_identifier`, `test:test_errors_and_correlation.test_internal_error_leaks_nothing`, `test:test_errors_and_correlation.test_a_missing_route_uses_the_error_contract` |
| `LESSON-REQ-0033` | yes | `COMPLETE` | `test:test_observability.test_metrics_endpoint_exposes_request_metrics`, `test:test_observability.test_metrics_label_routes_by_template_not_by_url`, `test:PrometheusConfigurationTests.test_the_api_instruments_reach_prometheus` |
| `LESSON-REQ-0034` | yes | `COMPLETE` | `test:SubprocessDecodingTests.test_no_capture_relies_on_the_platform_codepage`, `test:SubprocessDecodingTests.test_every_tool_that_re_emits_captured_output_configures_its_own_stream`, `test:SubprocessDecodingTests.test_the_rule_detects_a_capture_that_would_fail` |
| `LESSON-REQ-0035` | yes | `COMPLETE` | `test:Gate1GuardrailTests.test_every_image_gate_builds_before_it_measures`, `test:Gate1GuardrailTests.test_the_image_gate_rule_detects_a_gate_that_would_skip_the_build` |
| `LESSON-REQ-0036` | yes | `COMPLETE` | `test:Gate1GuardrailTests.test_no_shared_control_is_bound_to_a_gate_literal`, `test:Gate1GuardrailTests.test_the_gate_literal_rule_detects_a_bound_control`, `test:Gate1GuardrailTests.test_the_gate_literal_rule_accepts_a_derived_gate_and_a_fixture_root`, `test:Gate1GuardrailTests.test_no_control_names_a_migration_revision_literally`, `test:Gate1GuardrailTests.test_the_revision_rule_detects_a_named_head`, `test:Gate1GuardrailTests.test_the_head_revision_has_one_derivation` |
| `LESSON-REQ-0037` | yes | `COMPLETE` | `test:test_common_primitives.test_a_documented_placeholder_is_not_redacted`, `test:Gate1GuardrailTests.test_both_redactors_agree_on_every_value_the_example_file_carries`, `test:CredentialVocabularyTests.test_no_module_writes_its_own_credential_name_rule`, `test:CredentialVocabularyTests.test_the_rule_detects_a_second_opinion`, `test:CredentialVocabularyTests.test_the_two_questions_stay_different` |
| `LESSON-REQ-0038` | yes | `COMPLETE` | `test:test_gateway_persistence.test_the_operational_catalog_holds_only_providers_the_policy_declares` |
| `LESSON-REQ-0039` | yes | `COMPLETE` | `test:RecordedInputTests.test_every_sealed_checkpoint_validates_from_its_own_tag`, `test:RecordedInputTests.test_the_recorder_never_declares_an_ignored_path_as_an_input`, `test:RecordedInputTests.test_an_ignored_input_is_bound_by_content_rather_than_by_presence`, `test:RecordedInputTests.test_an_input_the_repository_carries_is_still_required_to_exist`, `test:RecordedInputTests.test_an_ignored_input_without_a_bound_digest_is_still_refused` |
| `LESSON-REQ-0040` | yes | `COMPLETE` | `test:SourceIntegrityTests.test_no_source_file_carries_a_stray_control_character`, `test:SourceIntegrityTests.test_the_scan_detects_one`, `test:FrontendSafetyTests.test_the_page_offers_nothing_that_would_execute_a_tool`, `test:RepositoryToolExecutionBoundaryTests.test_the_boundary_has_something_to_scan` |
| `LESSON-REQ-0041` | yes | `COMPLETE` | `test:Gate2MigrationTests.test_the_agent_runtime_migration_is_reversible`, `test:test_migrations.test_the_declared_model_matches_the_migrated_schema`, `test:MigrationConstraintNamingTests.test_a_check_constraint_is_created_and_dropped_by_its_bare_name`, `test:MigrationConstraintNamingTests.test_a_unique_constraint_keeps_exactly_the_name_it_was_given` |
| `LESSON-REQ-0042` | yes | `COMPLETE` | `test:ScenarioReadinessTests.test_readiness_is_asked_of_temporal`, `test:ScenarioReadinessTests.test_readiness_is_not_read_from_a_log_line`, `test:ScenarioReadinessTests.test_the_harness_asks_the_server_for_the_answer` |
| `LESSON-REQ-0043` | yes | `COMPLETE` | `test:ToolExecutionBoundaryTests.test_the_null_control_detects_a_mutation`, `test:test_boundary.test_the_provider_scan_would_catch_one`, `test:test_boundary.test_the_credential_scan_would_catch_one`, `test:RepositoryToolExecutionBoundaryTests.test_the_scan_detects_a_module_that_does_it`, `test:WorkflowDeterminismTests.test_the_determinism_scan_detects_a_module_that_breaks_it` |
| `LESSON-REQ-0044` | yes | `COMPLETE` | `test:CountedSuiteExpansionTests.test_no_counted_pytest_case_expands_at_run_time`, `test:CountedSuiteExpansionTests.test_the_scan_detects_an_expansion` |
| `LESSON-REQ-0045` | yes | `COMPLETE` | `test:DeadlineEnforcementTests.test_the_engine_is_not_wrapped_in_wait_for`, `test:DeadlineEnforcementTests.test_the_deadline_races_an_explicit_child_task`, `test:DeadlineEnforcementTests.test_the_wait_accepts_every_way_a_cancelled_activity_surfaces`, `test:DeadlineEnforcementTests.test_the_deadline_path_writes_the_failure_down`, `test:DeadlineEnforcementTests.test_the_scenario_asserts_the_run_ended_and_said_so` |
| `LESSON-REQ-0046` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `file:services/agent-runtime/src/iacode_agent_runtime/context.py`, `test:test_content_of_the_wrong_type_is_refused_by_its_real_defect`, `test:test_the_runtime_instructions_state_that_content_is_one_string`, `test:test_invalid_envelope_is_not_accepted_silently`, `command:cmd-0006`, `command:cmd-0008` |
| `LESSON-REQ-0047` | yes | `COMPLETE` | `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:apps/api/src/iacode_api/routes/agent_runs.py`, `test:test_a_terminal_state_is_never_visible_before_its_terminal_event`, `test:DeadlineEnforcementTests.test_the_workflow_writes_the_terminal_event_before_the_terminal_state`, `test:test_a_workflow_that_cannot_start_fails_the_run_rather_than_leaving_it_created`, `command:cmd-0006` |
| `LESSON-REQ-0048` | yes | `COMPLETE` | `file:scripts/iacode/gateway_smoke.py`, `file:scripts/iacode/smoke.py`, `test:LiveSmokeContractTests.test_the_observability_check_waits_for_a_scrape_and_asks_only_prometheus`, `test:LiveSmokeContractTests.test_live_smoke_is_bounded_and_minimal`, `test:ObserverCycleTests.test_every_script_that_reads_prometheus_waits_for_a_scrape`, `test:ObserverCycleTests.test_the_scan_fires_on_a_read_that_does_not_wait`, `test:ObserverCycleTests.test_the_foundation_smoke_waits_for_both_targets_and_asks_only_prometheus`, `command:cmd-0005`, `command:cmd-0067` |
| `LESSON-REQ-0049` | yes | `COMPLETE` | `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/seal_checkpoint.py`, `file:docs/adr/ADR-0023-sealed-checkpoint-binds-its-own-tag.md`, `test:DetachedHeadValidationTests.test_sealing_refuses_a_state_that_does_not_name_its_own_tag`, `test:DetachedHeadValidationTests.test_a_symbolic_head_validates_from_its_own_canonical_tag`, `test:DetachedHeadValidationTests.test_a_symbolic_head_away_from_its_canonical_tag_is_still_refused`, `test:RecordedInputTests.test_every_sealed_checkpoint_validates_from_its_own_tag`, `file:docs/CHECKPOINT-PROTOCOL.md`, `command:cmd-0020` |
