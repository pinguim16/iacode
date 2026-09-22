# Delivery Completeness Report

Result: `PASS`

- Checkpoint: `GATE-1-CP-0001`
- Matrix: `REQUIREMENTS-MATRIX.json`
- Generated: `2026-09-22T08:28:15Z`
- Auditor: Delivery Completeness Validator
- Expected set: derived by policies.expected_requirement_refs from the canonical Gate specification, the lesson preflight and the open independent audit findings and attacks

## Counts

| Metric | Value |
|---|---|
| expectedRequirements | 161 |
| totalRequirements | 161 |
| mandatoryRequirements | 160 |
| complete | 161 |
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
| `REQ-0001` | yes | `COMPLETE` | `file:.iacode/policies/canonical-requirements.json`, `test:Gate1CanonicalSpecificationTests`, `file:docs/GATE-1-CHECKLIST.md` |
| `REQ-0002` | yes | `COMPLETE` | `file:.iacode/policies/quality-gates.json` |
| `REQ-0003` | yes | `COMPLETE` | `file:.iacode/policies/test-suites.json`, `test:test_gateway_suite_is_declared_and_discovered` |
| `REQ-0004` | yes | `COMPLETE` | `file:scripts/development-ledger/gate1_red_team.py` |
| `REQ-0005` | yes | `COMPLETE` | `file:.iacode/policies/gate-scope.json`, `test:test_model_gateway_reservation_is_consumed_by_its_owner`, `file:services/model-gateway/README.md` |
| `REQ-0006` | yes | `COMPLETE` | `file:scripts/iacode/verify.py` |
| `REQ-0007` | yes | `COMPLETE` | `test:test_gateway_package_is_importable`, `file:docs/adr/ADR-0016-model-gateway-boundary.md` |
| `REQ-0008` | yes | `COMPLETE` | `test:test_no_provider_specific_name_escapes_the_adapter_layer` |
| `REQ-0009` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/ports.py`, `test:test_gateway_imports_no_application_module` |
| `REQ-0010` | yes | `COMPLETE` | `test:test_no_future_gate_capability_is_implemented` |
| `REQ-0011` | yes | `COMPLETE` | `test:test_gateway_readme_describes_the_delivery`, `file:services/model-gateway/README.md` |
| `REQ-0012` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/contracts.py`, `test:test_request_is_validated_when_it_is_built` |
| `REQ-0013` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/contracts.py`, `test:test_message_roles_are_provider_independent` |
| `REQ-0014` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/contracts.py`, `test:test_response_never_exposes_the_raw_provider_payload` |
| `REQ-0015` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/contracts.py`, `test:test_gateway_normalises_a_tool_call_without_executing_it` |
| `REQ-0016` | yes | `COMPLETE` | `test:test_invalid_tool_arguments_produce_a_normalised_error` |
| `REQ-0017` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`, `test:test_structured_output_requires_a_capable_candidate` |
| `REQ-0018` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/contracts.py`, `test:test_contract_version_is_declared` |
| `REQ-0019` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/providers/base.py`, `test:test_provider_contract_is_not_coupled_to_one_provider` |
| `REQ-0020` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/protocols/openai_chat.py`, `test:OpenAiChatProtocolTests` |
| `REQ-0021` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/protocols/openai_responses.py`, `test:OpenAiResponsesProtocolTests` |
| `REQ-0022` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/protocols/anthropic_messages.py`, `test:AnthropicMessagesProtocolTests` |
| `REQ-0023` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/protocols/selection.py`, `test:test_endpoint_selection_reads_the_declared_endpoints` |
| `REQ-0024` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/protocols/selection.py`, `test:test_unsupported_endpoint_is_refused_before_the_call` |
| `REQ-0025` | yes | `COMPLETE` | `file:.iacode/policies/providers.json`, `test:test_no_fake_provider_is_registered_at_runtime` |
| `REQ-0026` | yes | `COMPLETE` | `file:.iacode/policies/providers.json`, `test:test_provider_configuration_carries_no_credential` |
| `REQ-0027` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/db/models.py`, `test:test_no_table_stores_a_credential`, `test:test_provider_registry_persists_operational_metadata` |
| `REQ-0028` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/config.py`, `test:SecretContainmentTests` |
| `REQ-0029` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/config.py`, `file:infra/compose/.env.example`, `test:test_every_declared_key_is_read_somewhere` |
| `REQ-0030` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/security/base_url.py`, `test:BaseUrlSafetyTests` |
| `REQ-0031` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/contracts.py`, `file:apps/api/src/iacode_api/routes/gateway.py`, `test:test_request_cannot_supply_a_provider_address` |
| `REQ-0032` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py`, `test:test_catalog_comes_from_the_provider_api` |
| `REQ-0033` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/catalog/normalize.py`, `test:test_normalised_model_carries_the_declared_fields` |
| `REQ-0034` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/catalog/normalize.py`, `test:test_unknown_capability_is_not_turned_into_false` |
| `REQ-0035` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/catalog/normalize.py`, `test:test_capability_provenance_is_recorded`, `test:test_capability_is_never_inferred_from_a_name` |
| `REQ-0036` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py`, `test:test_sync_is_idempotent` |
| `REQ-0037` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py`, `test:test_missing_model_is_deactivated_not_deleted` |
| `REQ-0038` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py`, `test:test_failed_sync_preserves_the_previous_catalog` |
| `REQ-0039` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/db/models.py`, `file:services/model-gateway/src/iacode_model_gateway/contracts.py`, `test:test_same_model_id_in_two_providers_does_not_collide` |
| `REQ-0040` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`, `test:test_routing_reads_normalised_fields_only` |
| `REQ-0041` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`, `test:test_router_is_deterministic` |
| `REQ-0042` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`, `test:test_explicit_model_is_honoured_or_refused` |
| `REQ-0043` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/config.py`, `test:test_missing_default_model_is_an_explicit_error` |
| `REQ-0044` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/policy.py`, `test:test_unknown_capability_is_rejected_by_default` |
| `REQ-0045` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/context.py`, `test:ContextWindowTests` |
| `REQ-0046` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/policy.py`, `test:test_incompatible_reasoning_effort_is_not_sent_silently` |
| `REQ-0047` | yes | `COMPLETE` | `file:.iacode/policies/model-routes.json`, `test:test_route_aliases_come_from_configuration` |
| `REQ-0048` | yes | `COMPLETE` | `test:test_no_model_quality_claim_is_hardcoded` |
| `REQ-0049` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`, `test:test_route_explanation_is_structured_and_short` |
| `REQ-0050` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`, `test:test_disabled_provider_and_inactive_model_are_excluded` |
| `REQ-0051` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/errors.py`, `test:ErrorTaxonomyTests` |
| `REQ-0052` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/config.py`, `file:services/model-gateway/src/iacode_model_gateway/providers/http_provider.py`, `test:test_no_call_is_unbounded`, `test:test_timeout_is_normalised` |
| `REQ-0053` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/resilience/retry.py`, `test:RetryClassificationTests` |
| `REQ-0054` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/resilience/retry.py`, `test:test_retry_after_is_bounded` |
| `REQ-0055` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/resilience/retry.py`, `test:test_backoff_is_exponential_with_jitter` |
| `REQ-0056` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/resilience/circuit.py`, `test:CircuitBreakerTests` |
| `REQ-0057` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`, `test:test_fallback_chain_is_bounded_and_recorded` |
| `REQ-0058` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/routing/policy.py`, `test:FallbackSemanticsTests` |
| `REQ-0059` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/gateway.py`, `test:test_cancellation_stops_the_upstream_call` |
| `REQ-0060` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/resilience/limits.py`, `test:RequestLimitTests` |
| `REQ-0061` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/providers/http_provider.py`, `test:test_oversized_provider_response_is_refused` |
| `REQ-0062` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/gateway.py`, `test:test_provider_outage_does_not_affect_process_health` |
| `REQ-0063` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/gateway.py`, `test:test_streaming_uses_the_same_router` |
| `REQ-0064` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/contracts.py`, `test:StreamEnvelopeTests` |
| `REQ-0065` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/gateway.py`, `test:test_no_fallback_after_the_first_delivered_content` |
| `REQ-0066` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/gateway.py`, `test:test_failure_after_content_ends_with_an_error_event` |
| `REQ-0067` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/gateway.py`, `test:test_stream_endpoint_emits_sse_and_stops_on_disconnect` |
| `REQ-0068` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/catalog/normalize.py`, `test:UsageNormalisationTests` |
| `REQ-0069` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/pricing.py`, `test:test_unknown_cost_is_absent_not_zero` |
| `REQ-0070` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/gateway/store.py`, `test:test_model_call_records_the_operational_metadata` |
| `REQ-0071` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/config.py`, `file:apps/api/src/iacode_api/gateway/store.py`, `test:test_prompt_is_not_persisted_by_default`, `test:PromptCaptureTests` |
| `REQ-0072` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/fingerprint.py`, `test:test_request_fingerprint_is_stable_and_carries_no_content`, `file:docs/runbooks/MODEL-GATEWAY.md` |
| `REQ-0073` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/gateway/store.py`, `test:test_no_reasoning_content_is_persisted` |
| `REQ-0074` | yes | `COMPLETE` | `test:test_gate_one_records_no_training_eligible_data`, `file:.iacode/policies/training-data-policy.md` |
| `REQ-0075` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/telemetry/metrics.py`, `test:GatewayMetricsTests` |
| `REQ-0076` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/telemetry/metrics.py`, `test:test_metric_labels_are_bounded_and_carry_no_content` |
| `REQ-0077` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/telemetry/logs.py`, `test:test_gateway_log_contract` |
| `REQ-0078` | yes | `COMPLETE` | `file:services/model-gateway/src/iacode_model_gateway/telemetry/logs.py`, `test:SecretContainmentTests` |
| `REQ-0079` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/gateway.py`, `test:test_correlation_reaches_the_persisted_model_call` |
| `REQ-0080` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/gateway.py`, `test:test_openapi_documents_the_gateway_endpoints` |
| `REQ-0081` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/gateway.py`, `test:test_provider_listing_exposes_no_secret` |
| `REQ-0082` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/gateway.py`, `test:test_model_listing_filters` |
| `REQ-0083` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/gateway.py`, `test:test_sync_endpoint_reports_its_outcome` |
| `REQ-0084` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/gateway.py`, `test:test_infer_endpoint_returns_the_normalised_response`, `test:test_infer_endpoint_leaks_no_internal_detail` |
| `REQ-0085` | yes | `COMPLETE` | `file:apps/api/src/iacode_api/routes/gateway.py`, `test:test_gateway_health_separates_process_from_provider` |
| `REQ-0086` | yes | `COMPLETE` | `file:apps/web/src/app/gateway/gateway.ts`, `file:apps/web/src/app/gateway/gateway.spec.ts`, `file:docs/runbooks/MODEL-GATEWAY.md` |
| `REQ-0087` | yes | `COMPLETE` | `file:apps/web/src/app/gateway/gateway.html`, `file:apps/web/src/app/gateway/gateway.spec.ts`, `file:docs/runbooks/MODEL-GATEWAY.md` |
| `REQ-0088` | yes | `COMPLETE` | `test:test_frontend_calls_only_the_iacode_backend` |
| `REQ-0089` | yes | `COMPLETE` | `test:test_frontend_adds_no_conversation_capability` |
| `REQ-0090` | yes | `COMPLETE` | `file:scripts/iacode/verify.py` |
| `REQ-0091` | yes | `COMPLETE` | `file:scripts/iacode/gateway_smoke.py`, `command:cmd-0002` |
| `REQ-0092` | yes | `COMPLETE` | `file:scripts/iacode/gateway_smoke.py`, `command:cmd-0002` |
| `REQ-0093` | yes | `COMPLETE` | `file:scripts/iacode/gateway_smoke.py`, `command:cmd-0002` |
| `REQ-0094` | yes | `COMPLETE` | `file:scripts/iacode/gateway_smoke.py`, `test:test_absent_smoke_model_fails_rather_than_substitutes` |
| `REQ-0095` | yes | `COMPLETE` | `file:scripts/iacode/gateway_smoke.py`, `test:test_live_smoke_is_bounded_and_minimal` |
| `REQ-0096` | yes | `COMPLETE` | `file:scripts/iacode/gateway_smoke.py`, `command:cmd-0002` |
| `REQ-0097` | yes | `COMPLETE` | `file:infra/prometheus/prometheus.yml`, `command:cmd-0002` |
| `REQ-0098` | yes | `COMPLETE` | `file:scripts/iacode/gateway_smoke.py`, `test:test_missing_credential_blocks_rather_than_passes` |
| `REQ-0099` | yes | `COMPLETE` | `file:services/model-gateway/tests/test_provider_contract.py` |
| `REQ-0100` | yes | `COMPLETE` | `file:services/model-gateway/tests/test_catalog.py` |
| `REQ-0101` | yes | `COMPLETE` | `file:services/model-gateway/tests/test_routing.py` |
| `REQ-0102` | yes | `COMPLETE` | `file:services/model-gateway/tests/test_resilience.py` |
| `REQ-0103` | yes | `COMPLETE` | `file:services/model-gateway/tests/test_resilience.py` |
| `REQ-0104` | yes | `COMPLETE` | `file:services/model-gateway/tests/test_streaming.py` |
| `REQ-0105` | yes | `COMPLETE` | `file:services/model-gateway/tests/test_streaming.py`, `test:test_no_two_models_are_concatenated_in_one_stream` |
| `REQ-0106` | yes | `COMPLETE` | `file:services/model-gateway/tests/test_structured_output.py` |
| `REQ-0107` | yes | `COMPLETE` | `file:services/model-gateway/tests/test_secrets.py` |
| `REQ-0108` | yes | `COMPLETE` | `file:services/model-gateway/tests/test_resilience.py`, `file:services/model-gateway/tests/test_provider_contract.py`, `file:services/model-gateway/tests/test_secrets.py` |
| `REQ-0109` | yes | `COMPLETE` | `test:test_no_fake_provider_is_registered_at_runtime` |
| `REQ-0110` | yes | `COMPLETE` | `test:test_previous_migrations_are_unmodified` |
| `REQ-0111` | yes | `COMPLETE` | `test:test_migrations_run_from_zero`, `test:test_the_declared_model_matches_the_migrated_schema` |
| `REQ-0112` | yes | `COMPLETE` | `test:test_a_previous_gate_database_upgrades`, `test:test_the_upgrade_carries_forward_what_the_booleans_said` |
| `REQ-0113` | yes | `COMPLETE` | `file:scripts/iacode/verify.py` |
| `REQ-0114` | yes | `COMPLETE` | `file:docs/runbooks/MODEL-GATEWAY.md` |
| `REQ-0115` | yes | `COMPLETE` | `file:docs/ARCHITECTURE.md` |
| `REQ-0116` | yes | `COMPLETE` | `file:README.md`, `file:docs/DEVELOPMENT.md` |
| `REQ-0117` | yes | `COMPLETE` | `file:docs/VERSIONS.md` |
| `REQ-0118` | yes | `COMPLETE` | `file:docs/runbooks/MODEL-GATEWAY.md` |
| `REQ-0119` | yes | `COMPLETE` | `file:docs/adr/ADR-0016-model-gateway-boundary.md`, `file:docs/adr/ADR-0017-capabilities-are-tri-state.md`, `file:docs/adr/ADR-0018-streaming-commitment-point.md`, `file:docs/adr/ADR-0019-credentials-are-named-not-stored.md` |
| `REQ-0120` | yes | `COMPLETE` | `file:START-HERE.md`, `file:docs/MASTER-PLAN.md`, `file:docs/checkpoints/LATEST.md` |
| `REQ-0121` | yes | `COMPLETE` | `file:.iacode/memory/retrospectives/GATE-1-CP-0001.md` |
| `REQ-0122` | yes | `COMPLETE` | `file:docs/checkpoints/GATE-1-CP-0001/STATE.json` |
| `LESSON-REQ-0001` | yes | `COMPLETE` | `test:DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates`, `test:DetachedHeadValidationTests.test_detached_head_at_wrong_commit_fails` |
| `LESSON-REQ-0002` | yes | `COMPLETE` | `test:DeltaInventoryTests.test_removed_manifest_entry_fails`, `test:DeltaInventoryTests.test_silent_tracked_modification_fails` |
| `LESSON-REQ-0003` | yes | `COMPLETE` | `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded` |
| `LESSON-REQ-0004` | yes | `COMPLETE` | `test:ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected`, `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails` |
| `LESSON-REQ-0005` | yes | `COMPLETE` | `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`, `test:QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`, `test:QualityEvidenceTests.test_pass_without_evidence_fails` |
| `LESSON-REQ-0006` | yes | `COMPLETE` | `test:SetupChecklistTests.test_checklist_exists_and_is_referenced`, `test:SetupChecklistTests.test_documentation_links_resolve` |
| `LESSON-REQ-0007` | yes | `COMPLETE` | `test:DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review`, `test:ExternalAttestationTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`, `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough`, `test:SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass` |
| `LESSON-REQ-0008` | yes | `COMPLETE` | `test:DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`, `test:DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`, `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails` |
| `LESSON-REQ-0009` | yes | `COMPLETE` | `test:DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `test:DeliveryAssuranceGateTests.test_red_tests_block_review`, `test:GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_the_policy_declares_a_non_empty_closed_set` |
| `LESSON-REQ-0010` | yes | `COMPLETE` | `test:CommandInputBindingTests.test_a_clean_tree_claim_is_checked_against_the_declared_commit`, `test:CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`, `test:CommandReproducibilityTests.test_bare_script_name_is_rejected`, `test:CommandReproducibilityTests.test_unresolvable_script_path_is_rejected` |
| `LESSON-REQ-0011` | yes | `COMPLETE` | `test:DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`, `test:test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test:test_no_other_module_executes_the_mandatory_gate_set`, `test:test_the_refresh_has_one_definition` |
| `LESSON-REQ-0012` | yes | `COMPLETE` | `test:HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`, `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`, `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected` |
| `LESSON-REQ-0013` | no | `COMPLETE` | `file:docs/TOOL-CAPABILITIES.md` |
| `LESSON-REQ-0014` | yes | `COMPLETE` | `test:SealChronologyTests.test_a_dirty_tree_validation_is_not_evidence_of_a_sealed_commit`, `test:SealChronologyTests.test_a_missing_post_commit_validation_is_rejected`, `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected` |
| `LESSON-REQ-0015` | yes | `COMPLETE` | `test:PromotionInvariantTests.test_a_terminal_status_requires_an_independent_verdict`, `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension` |
| `LESSON-REQ-0016` | yes | `COMPLETE` | `test:MandatoryGatePolicyTests.test_a_cycle_missing_one_mandatory_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_a_mandatory_gate_that_exited_nonzero_is_rejected`, `test:MandatoryGatePolicyTests.test_a_pass_measured_before_a_source_change_is_stale` |
| `LESSON-REQ-0017` | yes | `COMPLETE` | `test:ExpectedRequirementSetTests.test_a_downgraded_matrix_cannot_escape_the_comparison`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`, `test:ExpectedRequirementSetTests.test_the_checklist_is_reparsed_rather_than_trusted`, `test:ExpectedRequirementSetTests.test_the_expected_set_is_derived_from_the_canonical_sources` |
| `LESSON-REQ-0018` | yes | `COMPLETE` | `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`, `test:LessonResolutionTests.test_an_invariant_control_must_be_defined_in_the_tooling`, `test:LessonResolutionTests.test_lesson_evidence_must_resolve` |
| `LESSON-REQ-0019` | yes | `COMPLETE` | `test:PreflightFreshnessTests.test_a_changed_fingerprint_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_preflight_from_another_gate_is_refused` |
| `LESSON-REQ-0020` | yes | `COMPLETE` | `test:CommandInputBindingTests.test_a_digest_that_omits_an_input_is_rejected`, `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically` |
| `LESSON-REQ-0021` | yes | `COMPLETE` | `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`, `test:IntegrityAnchorTests.test_a_recomputed_anchor_hash_must_match_its_fields`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`, `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected` |
| `LESSON-REQ-0022` | yes | `COMPLETE` | `test:DerivedCountTests.test_a_forged_count_is_rejected`, `test:DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`, `test:SourceCardinalityPolicyTests`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_the_cardinality_of_a_derived_set` |
| `LESSON-REQ-0023` | yes | `COMPLETE` | `test:LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected`, `test:LessonProvenanceTests.test_a_nonexistent_checkpoint_is_rejected` |
| `LESSON-REQ-0024` | yes | `COMPLETE` | `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output` |
| `LESSON-REQ-0025` | yes | `COMPLETE` | `test:IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint`, `test:SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain` |
| `LESSON-REQ-0026` | yes | `COMPLETE` | `test:InternalAssuranceTests.test_a_failed_null_mutation_control_cannot_produce_a_pass`, `test:InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected` |
| `LESSON-REQ-0027` | yes | `COMPLETE` | `test:MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded`, `test:MemoryPolicyDocumentTests.test_the_repository_memory_has_no_status_contradiction` |
| `LESSON-REQ-0028` | yes | `COMPLETE` | `test:MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared`, `test:MemoryPolicyDocumentTests.test_the_declared_policy_validates_against_its_schema`, `test:test_every_declared_key_is_read_somewhere`, `test:test_test_settings_ignore_the_ambient_environment` |
| `LESSON-REQ-0029` | yes | `COMPLETE` | `test:GateTransitionSimulationTests.test_its_mirror_audit_passes_with_the_empty_dimensions_inapplicable`, `test:GateTransitionSimulationTests.test_the_first_checkpoint_of_the_next_gate_reaches_review_readiness`, `test:SuccessorDurabilityTests.test_a_missing_anchor_is_still_detected_after_the_chain_advances`, `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies` |
| `LESSON-REQ-0030` | yes | `COMPLETE` | `test:MirrorApplicabilitySemanticsTests.test_a_missing_required_set_fails_rather_than_being_inapplicable`, `test:MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`, `test:MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output` |
| `LESSON-REQ-0031` | yes | `COMPLETE` | `test:test_assurance_scope_covers_the_runtime_source`, `test:test_declared_suites_are_discovered`, `test:test_expected_set_names_the_gate_specification`, `test:test_no_future_gate_capability_is_implemented`, `test:test_the_scope_control_detects_an_implementation`, `test:test_the_scope_control_ignores_a_gate_that_has_already_run` |
| `LESSON-REQ-0032` | yes | `COMPLETE` | `test:test_a_missing_route_uses_the_error_contract`, `test:test_internal_error_leaks_nothing`, `test:test_internal_error_still_carries_a_correlation_identifier` |
| `LESSON-REQ-0033` | yes | `COMPLETE` | `test:test_metrics_endpoint_exposes_request_metrics`, `test:test_metrics_label_routes_by_template_not_by_url`, `test:test_the_api_instruments_reach_prometheus` |
| `LESSON-REQ-0034` | yes | `COMPLETE` | `test:test_every_tool_that_re_emits_captured_output_configures_its_own_stream`, `test:test_no_capture_relies_on_the_platform_codepage`, `test:test_the_rule_detects_a_capture_that_would_fail` |
| `LESSON-REQ-0035` | yes | `COMPLETE` | `test:test_every_image_gate_builds_before_it_measures`, `test:test_the_image_gate_rule_detects_a_gate_that_would_skip_the_build` |
| `LESSON-REQ-0036` | yes | `COMPLETE` | `test:test_no_control_names_a_migration_revision_literally`, `test:test_no_shared_control_is_bound_to_a_gate_literal`, `test:test_the_gate_literal_rule_accepts_a_derived_gate_and_a_fixture_root`, `test:test_the_gate_literal_rule_detects_a_bound_control`, `test:test_the_head_revision_has_one_derivation`, `test:test_the_revision_rule_detects_a_named_head` |
| `LESSON-REQ-0037` | yes | `COMPLETE` | `test:test_a_documented_placeholder_is_not_redacted`, `test:test_both_redactors_agree_on_every_value_the_example_file_carries`, `test:test_no_module_writes_its_own_credential_name_rule`, `test:test_the_rule_detects_a_second_opinion`, `test:test_the_two_questions_stay_different` |
| `LESSON-REQ-0038` | yes | `COMPLETE` | `test:test_the_operational_catalog_holds_only_providers_the_policy_declares` |
| `LESSON-REQ-0039` | yes | `COMPLETE` | `test:test_an_ignored_input_is_bound_by_content_rather_than_by_presence`, `test:test_an_ignored_input_without_a_bound_digest_is_still_refused`, `test:test_an_input_the_repository_carries_is_still_required_to_exist`, `test:test_every_sealed_checkpoint_validates_from_its_own_tag`, `test:test_the_recorder_never_declares_an_ignored_path_as_an_input` |
