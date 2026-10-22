# Engineering Lessons

Rendered index of `lessons.jsonl`, which is the authoritative machine-readable memory.
Regenerate with `python scripts/development-ledger/validate_lessons.py --render-index`.

A lesson is `GUARDED` only when an automated control prevents its recurrence. Reading this
file is never the control. See [docs/ENGINEERING-MEMORY.md](../../docs/ENGINEERING-MEMORY.md).

| ID | Status | Severity | Category | Lesson | Guarded by |
|---|---|---|---|---|---|
| `LSN-0001` | `GUARDED` | HIGH | checkpoint | Checkpoint validation must succeed from a detached checkout of the checkpoint tag | `DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates`, `DetachedHeadValidationTests.test_detached_head_at_wrong_commit_fails`, `scripts/development-ledger/validate_checkpoint.py` |
| `LSN-0002` | `GUARDED` | HIGH | checkpoint | A file inventory must be recomputed from the repository, never trusted as an assertion | `DeltaInventoryTests.test_removed_manifest_entry_fails`, `DeltaInventoryTests.test_silent_tracked_modification_fails`, `scripts/development-ledger/validate_checkpoint.py` |
| `LSN-0003` | `GUARDED` | HIGH | checkpoint | Every operation attempt must be auditable, including a refusal decided before execution | `FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded`, `scripts/development-ledger/finalize_checkpoint.py` |
| `LSN-0004` | `GUARDED` | CRITICAL | checkpoint | A checkpoint may never claim readiness while it also claims to be blocked | `StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`, `ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected`, `_validate_status_blockers` |
| `LSN-0005` | `GUARDED` | CRITICAL | quality | A PASS requires evidence that can be executed or resolved, not a statement | `QualityEvidenceTests.test_pass_without_evidence_fails`, `QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`, `scripts/development-ledger/validate_checkpoint.py`, `validate_checkpoint._validate_quality_evidence`, `PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension` |
| `LSN-0006` | `GUARDED` | MEDIUM | documentation | The repository must be self-contained; a specification may not live outside it | `SetupChecklistTests.test_checklist_exists_and_is_referenced`, `SetupChecklistTests.test_documentation_links_resolve` |
| `LSN-0007` | `GUARDED` | CRITICAL | process | Independent validation cannot be declared by the run that did the work | `SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass`, `DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review`, `.iacode/schemas/checkpoint.schema.json`, `scripts/development-ledger/attestation.py`, `ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass` |
| `LSN-0008` | `GUARDED` | CRITICAL | process | Requirement completeness must be total and evidence-backed before handoff | `DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`, `scripts/development-ledger/check_completeness.py`, `ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`, `scripts/development-ledger/validate_checkpoint.py`, `Gate6BookkeepingCausalTests.test_final_report_renderer_consumes_every_canonical_section`, `Gate6BookkeepingCausalTests.test_final_report_renderer_refuses_each_missing_empty_or_extra_section` |
| `LSN-0009` | `GUARDED` | CRITICAL | testing | A red gate requires rework, never a waiver, and never a weakened check | `GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `DeliveryAssuranceGateTests.test_red_tests_block_review`, `.iacode/policies/quality-gates.json`, `MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected` |
| `LSN-0010` | `GUARDED` | CRITICAL | tooling | A recorded command must carry runtime, working directory, commit and purpose to be replayable | `CommandReproducibilityTests.test_bare_script_name_is_rejected`, `CommandReproducibilityTests.test_unresolvable_script_path_is_rejected`, `.iacode/schemas/command.schema.json`, `validate_checkpoint._validate_command_reproducibility`, `CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`, `CheckpointInvocationProducerTests.test_custom_phase_and_quoted_unicode_replay_are_literal`, `CheckpointInvocationProducerTests.test_omitted_default_status_is_not_invented`, `CheckpointInvocationProducerTests.test_nested_working_directory_and_explicit_root_replay`, `CheckpointInvocationProducerTests.test_default_null_control_preserves_supplied_invocation`, `CheckpointInvocationProducerTests.test_registered_m2_attack_runs_actual_null_and_phase_human_replay`, `CheckpointInvocationProducerTests.test_registered_m2_attack_reproduces_old_phase_escape_with_valid_null` |
| `LSN-0011` | `GUARDED` | CRITICAL | tooling | A control over a checkpoint's own evidence must be scoped to the moment it matters | `DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`, `green_keeper._refresh_declared_hashes`, `test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test_green_keeper_declares_its_in_progress_evidence_dirty_before_validation`, `test_preflight_aggregates_and_commit_semantics_are_derived_without_promotion`, `test_a_sealed_or_terminal_checkpoint_is_never_rewritten`, `test_validation_runner_keeps_the_synchronizers_derived_state`, `test_bookkeeping_sequence_awaits_each_recorder_and_keeps_canonical_order`, `test_bookkeeping_sequence_never_validates_after_inventory_recorder_failure`, `InProgressMetadataTests.test_validation_runner_keeps_the_synchronizers_derived_state` |
| `LSN-0012` | `GUARDED` | CRITICAL | git | Sealed checkpoints and their tags are immutable, and tooling must keep validating them | `HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`, `docs/CHECKPOINT-PROTOCOL.md`, `scripts/development-ledger/anchors.py`, `IntegrityAnchorTests.test_a_moved_historical_tag_is_detected` |
| `LSN-0013` | `CONFIRMED` | HIGH | environment | An installed capability must be detected by resolved path, not by a bare command lookup | _not yet guarded_ |
| `LSN-0014` | `GUARDED` | MEDIUM | process | Evidence must be recorded as it happens, not reconstructed at the end of a run | `scripts/development-ledger/record_command.py`, `validate_checkpoint._validate_seal_chronology`, `SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected` |
| `LSN-0015` | `GUARDED` | CRITICAL | quality | Every positive terminal status needs one shared promotion invariant | `validate_checkpoint._validate_delivery_assurance`, `PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper` |
| `LSN-0016` | `GUARDED` | CRITICAL | testing | A mandatory set must be closed by policy, never chosen by the caller | `validate_checkpoint._validate_green_keeper_cycle`, `.iacode/policies/quality-gates.json` |
| `LSN-0017` | `GUARDED` | CRITICAL | process | A completeness denominator must come from a source the delivery does not own | `policies.expected_requirement_refs`, `ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected` |
| `LSN-0018` | `GUARDED` | CRITICAL | tooling | A structured reference must be resolved, not merely well typed | `lessons.resolve_control`, `LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`, `QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`, `QualityEvidenceTests.test_pass_referencing_an_existing_checkpoint_file_passes` |
| `LSN-0019` | `GUARDED` | HIGH | tooling | A derived artifact must carry a fingerprint of the inputs that produced it | `lessons.preflight_staleness`, `PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale` |
| `LSN-0020` | `GUARDED` | CRITICAL | tooling | Evidence produced from a dirty tree needs immutable input identity | `ledger_common.build_command_record`, `CommandInputBindingTests.test_the_recorder_binds_inputs_automatically`, `test_input_digests_are_frozen_before_a_real_child_rewrites_its_inputs` |
| `LSN-0021` | `GUARDED` | CRITICAL | git | Sealed history needs an anchor outside the content it describes | `anchors.verify_chain`, `IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected` |
| `LSN-0022` | `GUARDED` | CRITICAL | documentation | An authoritative count must be derived once, never maintained by hand twice | `validate_checkpoint._validate_derived_counts`, `DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`, `SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`, `docs/QUALITY-GATES.md` |
| `LSN-0023` | `GUARDED` | MEDIUM | documentation | A lesson must cite a source that actually records the finding it claims | `lessons._resolve_source_locator`, `LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected` |
| `LSN-0024` | `GUARDED` | CRITICAL | quality | A control is finished only when its positive path has been executed, not only its refusals | `PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `scripts/development-ledger/promotion_simulation.py`, `SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output` |
| `LSN-0025` | `GUARDED` | CRITICAL | testing | A generic guardrail derives repository state instead of naming today's checkpoint | `anchors.pending_anchor_exclusion`, `SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain`, `IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint` |
| `LSN-0026` | `GUARDED` | HIGH | testing | An adversarial battery without a null-mutation control proves nothing | `.iacode/schemas/red-team-report.schema.json`, `validate_checkpoint._validate_internal_assurance`, `InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected` |
| `LSN-0027` | `GUARDED` | MEDIUM | documentation | A lesson's prose may record a residual limit but may never contradict its status | `lessons.validate_lessons`, `MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded` |
| `LSN-0028` | `GUARDED` | HIGH | tooling | A configuration key that no code reads is a defect, not documentation | `.iacode/schemas/memory-policy.schema.json`, `lessons.validate_memory_policy_document`, `MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared`, `test_every_declared_key_is_read_somewhere` |
| `LSN-0029` | `GUARDED` | CRITICAL | process | A required protocol transition must never turn a mandatory gate red | `scripts/development-ledger/successor_durability.py`, `SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `scripts/development-ledger/gate_transition_simulation.py`, `Gate7FutureBoundaryTests.test_code_graph_is_only_a_future_notice_and_real_scope_rejects_an_added_file` |
| `LSN-0030` | `CONFIRMED` | LOW | process | The lesson preflight presumes an implementing delivery and constrains an audit run badly | _not yet guarded_ |
| `LSN-0031` | `GUARDED` | CRITICAL | quality | An empty applicable set is not a missing required set, and a control must tell them apart | `scripts/development-ledger/mirror_semantics_validation.py`, `MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`, `MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`, `validate_checkpoint._validate_mirror_applicability` |
| `LSN-0032` | `GUARDED` | HIGH | quality | A control written while one Gate was the only Gate stops being a control when the next one starts | `test_expected_set_names_the_gate_specification`, `test_assurance_scope_covers_the_runtime_source`, `test_declared_suites_are_discovered`, `.iacode/policies/gate-scope.json`, `scripts/development-ledger/gate_transition_simulation.py` |
| `LSN-0033` | `GUARDED` | MEDIUM | implementation | A value bound in middleware is absent in the handlers that run outside it | `test_internal_error_still_carries_a_correlation_identifier`, `test_a_missing_route_uses_the_error_contract` |
| `LSN-0034` | `GUARDED` | MEDIUM | implementation | Re-deriving what the framework already computed diverges from the framework | `test_metrics_endpoint_exposes_request_metrics`, `test_metrics_label_routes_by_template_not_by_url`, `test_the_api_instruments_reach_prometheus` |
| `LSN-0035` | `GUARDED` | CRITICAL | tooling | Captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work | `test_no_capture_relies_on_the_platform_codepage`, `test_every_tool_that_re_emits_captured_output_configures_its_own_stream`, `test_the_rule_detects_a_capture_that_would_fail`, `test_cold_diagnostic_entrypoints_use_utf8_before_any_work`, `M2CurrentStreamBootstrapTests.test_actual_capture_entry_blocks_reject_cold_bootstrap_removal`, `PublicationCallerTests.test_unchanged_whole_tree_codepage_guard_covers_current_m2_sources`, `PublicationProofDecisionTests.test_actual_git_capture_states_decoder_and_preserves_unicode` |
| `LSN-0036` | `GUARDED` | HIGH | tooling | A gate that runs inside an image measures the image, not the source | `test_every_image_gate_builds_before_it_measures`, `test_the_image_gate_rule_detects_a_gate_that_would_skip_the_build`, `test_durability_scenario_rebuilds_its_rehearsal_worker` |
| `LSN-0037` | `GUARDED` | HIGH | tooling | A shared control that names an identifier the repository derives stops being a control when that identifier moves | `test_no_shared_control_is_bound_to_a_gate_literal`, `test_the_gate_literal_rule_detects_a_bound_control`, `test_no_control_names_a_migration_revision_literally`, `test_the_revision_rule_detects_a_named_head`, `test_the_head_revision_has_one_derivation`, `test_cli_reservation_membership_follows_every_policy_lifecycle_position` |
| `LSN-0038` | `GUARDED` | MEDIUM | implementation | Two representations of one concept in one module disagree, and the safer one loses | `test_a_documented_placeholder_is_not_redacted`, `test_both_redactors_agree_on_every_value_the_example_file_carries`, `test_no_module_writes_its_own_credential_name_rule`, `test_the_two_questions_stay_different` |
| `LSN-0039` | `GUARDED` | HIGH | testing | A test that writes to the operational database leaves production data behind | `test_the_operational_catalog_holds_only_providers_the_policy_declares` |
| `LSN-0040` | `GUARDED` | CRITICAL | checkpoint | A control that judges sealed history only runs once a successor anchors it | `test_every_sealed_checkpoint_validates_from_its_own_tag`, `test_the_recorder_never_declares_an_ignored_path_as_an_input`, `test_an_input_the_repository_carries_is_still_required_to_exist`, `scripts/development-ledger/validate_checkpoint.py`, `test_the_validator_refuses_a_record_naming_an_unpublished_commit`, `test_every_preserved_reference_is_what_makes_its_checkpoint_valid`, `test_a_published_clone_carries_only_what_a_published_reference_reaches`, `test_every_clone_in_the_tooling_and_the_suite_is_a_published_clone`, `test_a_preserved_reference_missing_from_the_remote_fails_unnamed`, `test_a_preserved_commit_maps_to_the_checkpoint_whose_evidence_names_it`, `test_git_metadata_is_local_even_though_git_check_ignore_does_not_classify_it`, `test_schema_3_3_refuses_a_digest_bound_git_metadata_input`, `test_schema_3_3_refuses_an_ignored_input_even_when_it_exists`, `test_the_recorder_excludes_git_metadata_and_refuses_it_when_explicit`, `test_a_nontransport_input_refusal_is_recomputed_from_its_precondition`, `test_a_fabricated_nontransport_input_refusal_is_rejected`, `scripts/development-ledger/ledger_common.py` |
| `LSN-0041` | `GUARDED` | HIGH | testing | An editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing | `test_no_source_file_carries_a_stray_control_character`, `test_the_scan_detects_one`, `test_the_page_offers_nothing_that_would_execute_a_tool`, `test_the_boundary_has_something_to_scan` |
| `LSN-0042` | `GUARDED` | CRITICAL | implementation | A naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone | `test_the_agent_runtime_migration_is_reversible`, `test_the_declared_model_matches_the_migrated_schema`, `test_a_check_constraint_is_created_and_dropped_by_its_bare_name`, `test_a_unique_constraint_keeps_exactly_the_name_it_was_given`, `test_experience_constraint_names_respect_their_actual_kind` |
| `LSN-0043` | `GUARDED` | MEDIUM | testing | A log line is not evidence that another process is ready | `test_readiness_is_asked_of_temporal`, `test_readiness_is_not_read_from_a_log_line`, `test_the_harness_asks_the_server_for_the_answer` |
| `LSN-0044` | `GUARDED` | HIGH | quality | A boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module | `test_the_null_control_detects_a_mutation`, `test_the_provider_scan_would_catch_one`, `test_the_credential_scan_would_catch_one`, `test_the_scan_detects_a_module_that_does_it`, `test_the_determinism_scan_detects_a_module_that_breaks_it` |
| `LSN-0045` | `GUARDED` | MEDIUM | testing | A counted test suite must declare its cases statically, because the denominator is read from the source | `test_no_counted_pytest_case_expands_at_run_time`, `test_the_scan_detects_an_expansion` |
| `LSN-0046` | `GUARDED` | CRITICAL | implementation | A timeout that cancels the task it runs in leaves nothing able to record what happened | `scripts/iacode/scenarios/agent_runtime_deadline.py`, `test_the_engine_is_not_wrapped_in_wait_for`, `test_the_wait_accepts_every_way_a_cancelled_activity_surfaces`, `test_the_deadline_path_writes_the_failure_down`, `test_the_scenario_asserts_the_run_ended_and_said_so` |
| `LSN-0047` | `GUARDED` | HIGH | implementation | A refusal that misnames the defect spends the only repair on the wrong correction | `test_content_of_the_wrong_type_is_refused_by_its_real_defect`, `test_the_runtime_instructions_state_that_content_is_one_string`, `scripts/iacode/agent_runtime_smoke.py` |
| `LSN-0048` | `GUARDED` | HIGH | implementation | A state and the event that explains it, written in two commits, are written event first | `test_a_terminal_state_is_never_visible_before_its_terminal_event`, `test_the_workflow_writes_the_terminal_event_before_the_terminal_state`, `test_a_workflow_that_cannot_start_fails_the_run_rather_than_leaving_it_created`, `scripts/iacode/agent_runtime_smoke.py` |
| `LSN-0049` | `GUARDED` | HIGH | testing | A metric read the instant after the call that moved it is read before the scrape that carries it | `test_the_observability_check_waits_for_a_scrape_and_asks_only_prometheus`, `test_live_smoke_is_bounded_and_minimal`, `test_every_script_that_reads_prometheus_waits_for_a_scrape`, `test_the_scan_fires_on_a_read_that_does_not_wait`, `test_the_foundation_smoke_waits_for_both_targets_and_asks_only_prometheus`, `test_prometheus_observation_waits_on_the_versioned_scrape_cycle` |
| `LSN-0050` | `GUARDED` | CRITICAL | checkpoint | A checkpoint sealed without naming its own tag cannot be validated from that tag | `test_sealing_refuses_a_state_that_does_not_name_its_own_tag`, `test_a_symbolic_head_validates_from_its_own_canonical_tag`, `test_a_symbolic_head_away_from_its_canonical_tag_is_still_refused`, `test_every_sealed_checkpoint_validates_from_its_own_tag` |
| `LSN-0051` | `GUARDED` | HIGH | implementation | A payload one service bounds for another must be bounded as the receiver measures it | `test_the_runtime_accepts_every_result_the_sandbox_hands_over`, `test_an_escaped_output_is_shortened_to_the_bound_and_says_so`, `test_an_output_that_fits_is_handed_over_unchanged` |
| `LSN-0052` | `GUARDED` | HIGH | architecture | Two processes that meet on a queue must name what crosses it once, and a real run must exercise both | `test_both_sides_name_the_result_by_the_shared_key`, `test_the_key_scan_detects_a_literal`, `test_the_activity_answers_the_agent_result_and_the_execution` |
| `LSN-0053` | `GUARDED` | HIGH | security | A process sweep that reads what a forking process holds waits on the processes it has to kill | `test_a_fork_bomb_that_detaches_leaves_a_sandbox_that_still_answers`, `test_a_fork_bomb_is_contained_by_the_process_limit`, `test_a_timeout_kills_the_whole_process_tree`, `test_the_sweep_waits_for_zombies_to_be_reaped_before_returning` |
| `LSN-0054` | `CONFIRMED` | MEDIUM | git | A pre-push check narrower than the change's reach lets a red gate reach the public remote | `PublicationCallerTests.test_actual_publisher_checks_current_lint_before_publication_effects`, `PublicationCallerTests.test_archived_actual_publisher_without_precondition_is_rejected`, `PublicationProofDecisionTests.test_modeled_valid_proof_is_accepted_without_git_state_effects`, `PublicationProofDecisionTests.test_missing_stale_failed_and_bool_exit_proofs_are_refused`, `PublicationProofDecisionTests.test_other_head_or_unbound_artifact_cannot_serve_as_current_prepublication_proof`, `PublicationProofDecisionTests.test_actual_stream_tamper_and_wrapper_identity_change_are_refused`, `PublicationProofDecisionTests.test_latest_failed_attempt_cannot_fall_back_to_older_success` |
| `LSN-0055` | `GUARDED` | MEDIUM | model-behavior | A contract a model must follow has to reach the model, rendered from the definition the parser enforces | `test_the_runtime_instructions_show_the_exact_envelope_of_every_kind`, `test_the_repair_restates_the_same_shape`, `test_the_rendered_contract_follows_the_schema`, `test_no_second_envelope_contract_is_written_by_hand`, `test_arguments_outside_tool_arguments_are_refused_by_their_real_defect` |
| `LSN-0056` | `GUARDED` | MEDIUM | security | A result is accepted only from the executor that owns the request, decided when the request is created | `test_a_forged_result_cannot_displace_the_sandbox_result`, `test_a_manual_result_for_a_sandbox_request_is_refused`, `test_a_result_for_a_request_the_sandbox_owns_is_refused_and_never_signalled`, `test_every_caller_declares_a_constant_origin`, `test_existing_requests_are_backfilled_from_what_the_sandbox_executed`, `scripts/iacode/scenarios/sandbox_coding_e2e.py` |
| `LSN-0057` | `GUARDED` | CRITICAL | security | A pinned lock can become unsafe without changing, so advisory state is live evidence | `scripts/iacode/dependency_scan.py`, `test_the_dependency_scan_blocks_critical_and_high_findings` |
| `LSN-0058` | `GUARDED` | MEDIUM | environment | Container health does not prove Docker Desktop host-port forwarding | `test_grafana_is_healthy` |
| `LSN-0059` | `GUARDED` | HIGH | process | A lesson exclusion must declare the scope it excludes | `test_the_repository_preflight_covers_every_applicable_lesson` |
| `LSN-0060` | `GUARDED` | MEDIUM | implementation | Parent and child facts without an ORM relationship require an explicit flush boundary | `test_plan_run_results_verdict_and_events_round_trip` |
| `LSN-0061` | `GUARDED` | MEDIUM | testing | Cancellation completion must not bypass cleanup acknowledgement | `test_results_enforce_owner_idempotency_and_late_refusal` |
| `LSN-0062` | `GUARDED` | MEDIUM | implementation | Provenance digests are a set even when their sources are distinct | `test_a_sandbox_answer_becomes_redacted_immutable_evidence` |
| `LSN-0063` | `GUARDED` | HIGH | architecture | An identity shared across services must satisfy the strictest persistence type and remain stable | `test_quality_tool_identity_is_a_stable_uuid` |
| `LSN-0064` | `GUARDED` | HIGH | architecture | A shared execution resource needs an explicit exclusive owner for every owning domain | `test_a_sandbox_session_has_exactly_one_run_owner_and_one_active_slot_per_owner`, `test_plan_run_results_verdict_and_events_round_trip` |
| `LSN-0065` | `GUARDED` | HIGH | implementation | A shared execution identifier must not be written into a foreign key owned by another domain | `test_only_agent_requests_bind_the_agent_tool_request_foreign_key` |
| `LSN-0066` | `GUARDED` | HIGH | architecture | Immutable content identity excludes observation time and the first observer | `test_content_addressed_plan_reuse_ignores_observation_time_and_first_owner` |
| `LSN-0067` | `GUARDED` | HIGH | implementation | Cancellation semantics must survive orchestration-library exception wrapping | `test_an_acknowledged_activity_cancellation_stays_a_cancellation` |
| `LSN-0068` | `GUARDED` | HIGH | implementation | A bounded parser must apply each content limit only to content it interprets | `test_large_non_manifest_content_does_not_block_project_detection`, `test_paths_and_manifest_sizes_are_bounded` |
| `LSN-0069` | `GUARDED` | HIGH | architecture | A polyglot plan binds each check to both its project root and its toolchain | `test_polyglot_monorepo_checks_keep_their_stack_roots`, `test_a_polyglot_plan_selects_each_check_image_from_its_frozen_runner` |
| `LSN-0070` | `GUARDED` | HIGH | architecture | Project discovery must separate deployable roots, nested fixtures and check applicability | `test_nested_fixture_manifests_do_not_become_workspace_roots`, `test_unit_checks_are_not_applicable_without_test_sources`, `test_unit_checks_are_mandatory_when_test_sources_exist` |
| `LSN-0071` | `GUARDED` | HIGH | implementation | Every quality image must provision snapshots on its oldest runtime and prepare each isolated check | `test_every_quality_helper_provisions_a_real_snapshot`, `test_isolated_language_checks_prepare_their_policy_owned_toolchain` |
| `LSN-0072` | `GUARDED` | HIGH | security | Secret findings and reviewed false positives must share one policy-owned taxonomy | `test_quality_images_bind_the_policy_owned_secret_scanner`, `test_a_non_allowlisted_credential_shape_fails_the_secret_check` |
| `LSN-0073` | `GUARDED` | HIGH | quality | The canonical lint denominator must cover every detected project root | `test_mandatory_lint_covers_every_python_project_root` |
| `LSN-0074` | `GUARDED` | CRITICAL | implementation | An importable source tree is not an installed or repository-configured test environment | `test_python_unit_runner_installs_metadata_and_exposes_monorepo_policy`, `test_python_functional_fixtures_reach_their_intended_test_outcome`, `test_real_registry_is_bound_explicitly_when_working_directory_is_nested` |
| `LSN-0075` | `GUARDED` | HIGH | implementation | Offline package installation requires its build backend inside the quality image | `test_python_unit_runner_installs_metadata_and_exposes_monorepo_policy` |
| `LSN-0076` | `GUARDED` | HIGH | architecture | Projected nested configuration requires an explicit monorepo root | `test_python_unit_runner_installs_metadata_and_exposes_monorepo_policy`, `test_no_evaluator_module_can_start_a_process` |
| `LSN-0077` | `GUARDED` | CRITICAL | quality | Harness wait bounds must reflect workload size without changing product deadlines | `test_real_repository_scenario_has_a_separate_bounded_wait`, `Gate7QualityObservationTests.test_large_repository_observer_covers_unchanged_canonical_run_deadline` |
| `LSN-0078` | `GUARDED` | HIGH | quality | Evidence recorders must resolve caller-supplied commit references before execution | `test_inputs_are_canonicalized_and_an_unknown_subject_is_refused` |
| `LSN-0079` | `GUARDED` | HIGH | testing | Test discovery and the unit runner must cover the same project scope | `test_isolated_language_checks_prepare_their_policy_owned_toolchain`, `test_unit_checks_are_mandatory_when_test_sources_exist` |
| `LSN-0080` | `GUARDED` | HIGH | quality | A failed verification stage must not leave an older PASS report addressable | `test_verification_removes_a_stale_stage_report_before_execution`, `test_standalone_live_proof_retires_old_pass_before_dependency_import_failure` |
| `LSN-0081` | `GUARDED` | HIGH | testing | Canonical requirement evidence must name a test the repository actually discovers | `test_every_test_the_specifications_name_exists` |
| `LSN-0082` | `GUARDED` | CRITICAL | quality | Engineering memory cannot depend on an ephemeral generated report | `test_engineering_memory_never_depends_on_ephemeral_var_evidence`, `scripts/development-ledger/validate_lessons.py` |
| `LSN-0083` | `GUARDED` | CRITICAL | tooling | A command that decodes captured UTF-8 must also configure the stream that re-emits it | `test_every_tool_that_re_emits_captured_output_configures_its_own_stream`, `test_cold_diagnostic_entrypoints_use_utf8_before_any_work`, `Gate7DocumentationAndStreamsTests.test_current_entrypoints_configure_the_shared_stream_before_work`, `M2CurrentStreamBootstrapTests.test_actual_capture_entry_blocks_reject_cold_bootstrap_removal` |
| `LSN-0084` | `GUARDED` | HIGH | testing | A historical Gate documentation test must derive the current entry-point state | `test_the_entry_point_names_the_current_gate`, `test_historical_gate4_controls_keep_their_owning_gate` |
| `LSN-0085` | `GUARDED` | MEDIUM | testing | A source-based control must assert syntax semantics rather than formatter layout | `test_the_verification_adds_the_stages_this_gate_introduces` |
| `LSN-0086` | `GUARDED` | MEDIUM | testing | A subprocess assertion must preserve the exit code when both streams are empty | `test_an_empty_validator_failure_keeps_its_process_exit_code` |
| `LSN-0087` | `GUARDED` | HIGH | implementation | A rehearsal worker must register every workflow activity boundary | `test_rehearsal_workers_register_the_post_run_quality_boundary` |
| `LSN-0088` | `GUARDED` | HIGH | testing | A test inside a built image can consume only inputs copied into that image | `test_built_sandbox_test_image_carries_declared_external_fixture_inputs`, `test_python_functional_fixtures_reach_their_intended_test_outcome` |
| `LSN-0089` | `GUARDED` | HIGH | architecture | Domain not-applicability and operational failure need distinct orchestration outcomes | `test_agent_quality_classifies_unsupported_and_failed_plans_without_stranding_run` |
| `LSN-0090` | `GUARDED` | HIGH | testing | A clean-clone control must use only versioned configuration inputs | `test_the_evaluator_service_has_no_engine_socket_or_host_project_mount` |
| `LSN-0091` | `GUARDED` | CRITICAL | security | Secret detection must run on the exact bytes at the durable evidence boundary | `test_canonical_secret_is_rejected_before_any_durable_operation`, `test_secret_bearing_execution_is_contained_and_derives_fail` |
| `LSN-0092` | `GUARDED` | HIGH | tooling | Canonical audit parsers must consume every bounded sealed report rendering | `test_a_blocking_finding_paragraph_in_a_sealed_audit_is_parsed`, `test_blocking_finding_prose_is_bounded_to_its_section` |
| `LSN-0093` | `GUARDED` | HIGH | testing | Disposable control repositories must carry every imported repository package | `test_disposable_ledger_runtime_carries_its_canonical_scanner_dependency`, `test_full_delivery_assurance_flow_reaches_ready_for_review` |
| `LSN-0094` | `GUARDED` | HIGH | checkpoint | A review bundle must include unchanged canonical artifact categories | `test_review_context_includes_unchanged_migrations_schemas_and_policies`, `scripts/development-ledger/review_bundle.py` |
| `LSN-0095` | `GUARDED` | HIGH | testing | A complete verifier must own its Compose runtime by checkout | `test_full_verification_uses_a_checkout_owned_compose_project_and_dynamic_ports`, `test_each_stage_receives_the_frozen_verification_environment`, `test_cleanup_refuses_the_shared_developer_project`, `test_live_stack_stage_builds_every_image_before_it_is_exercised`, `test_order_isolation_probe_preserves_the_historical_contiguous_stage_order` |
| `LSN-0096` | `GUARDED` | HIGH | checkpoint | Evidence publishers must consume the producer's canonical result schema | `test_published_full_verification_counts_the_canonical_result_field`, `test_published_report_reconciliation_allows_only_the_generated_report` |
| `LSN-0097` | `GUARDED` | HIGH | checkpoint | A review-bundle declaration must bind an immutable reconstruction subject | `test_immutable_subject_rebuilds_are_byte_identical_and_exclude_only_the_sidecar`, `test_declared_digest_and_size_are_rebuilt_not_trusted`, `test_full_delivery_assurance_flow_reaches_ready_for_review` |
| `LSN-0098` | `GUARDED` | CRITICAL | implementation | Accepted cancellation must be enforced from durable state across activity boundaries | `test_cancellation_is_rechecked_after_dispatch_before_activity_start`, `test_durable_cancelling_state_stops_an_active_sandbox_activity`, `test_a_signal_flag_set_before_handle_assignment_still_cancels_the_activity`, `test_accepted_cancellation_wins_over_a_racing_success_response`, `test_durable_cancellation_during_result_write_finishes_without_a_signal`, `test_concurrent_cancellation_and_verdict_have_one_winner` |
| `LSN-0099` | `GUARDED` | HIGH | checkpoint | A refused subject is an attempted input, not executed commit evidence | `test_inputs_are_canonicalized_and_an_unknown_subject_is_refused` |
| `LSN-0100` | `GUARDED` | HIGH | checkpoint | Pre-seal detached validation must bind the explicit subject namespace | `test_in_progress_symbolic_head_validates_from_its_matching_subject_tag`, `test_subject_tag_never_substitutes_for_a_sealed_checkpoint_tag` |
| `LSN-0101` | `GUARDED` | HIGH | checkpoint | A structural record and its canonical index are one atomic change | `test_the_index_lists_every_record_with_its_title_and_status`, `test_a_record_missing_from_the_index_is_detected` |
| `LSN-0102` | `GUARDED` | CRITICAL | quality | Assurance denominators must derive category counts from the current source set | `test_corrective_partition_is_derived_from_the_current_reference_set`, `test_current_collection_partition_survives_added_regression_cases`, `test_current_summary_derives_exact_vocabulary_and_ignores_noncanonical_alias`, `test_current_summary_refuses_missing_duplicate_reordered_or_unknown_results`, `test_inherited_gate_assertion_accepts_growth_but_refuses_removal_or_optional_controls`, `Gate7MandatoryMembershipTests.test_current_quality_guard_refuses_every_canonical_removal_and_optional_downgrade`, `Gate7MandatoryMembershipTests.test_quality_guard_consumes_an_added_registered_gate_without_a_second_literal` |
| `LSN-0103` | `GUARDED` | HIGH | testing | Adversarial fixtures must hash the complete validated contract | `test_verdict_before_cancellation_refuses_late_acceptance` |
| `LSN-0104` | `GUARDED` | HIGH | process | Intermediate closure and independent validation must have unambiguous contracts | `test_internal_closure_cannot_claim_independent_review_or_red_team` |
| `LSN-0105` | `GUARDED` | CRITICAL | testing | New behavioral tests must satisfy the unchanged source-quality contract | `test_mandatory_lint_covers_every_python_project_root`, `Gate7LintDenominatorTests.test_inherited_lint_guard_refuses_each_new_python_root_omission`, `docs/checkpoints/GATE-7-CP-0001/audit-harness/format_assurance_helpers.py`, `PublicationCallerTests.test_actual_publisher_checks_current_lint_before_publication_effects`, `PublicationCallerTests.test_archived_actual_publisher_without_precondition_is_rejected`, `AuthoredQualityDecisionTests.test_modeled_valid_whole_scope_acceptance_has_no_source_effects`, `AuthoredQualityDecisionTests.test_missing_stale_narrowed_format_and_nonzero_proofs_are_refused`, `AuthoredQualityDecisionTests.test_changed_original_bytes_failed_cleanup_and_latest_failure_are_refused`, `docs/checkpoints/GATE-7-CP-0003/audit-harness/authored_python_quality.py` |
| `LSN-0106` | `GUARDED` | HIGH | implementation | A security repair must execute at the causal output boundary, not a similarly shaped branch | `test_canonical_secret_output_is_rejected_before_durable_delivery` |
| `LSN-0107` | `GUARDED` | HIGH | testing | An adversarial marker must satisfy the canonical detector before it can judge containment | `test_live_secret_beyond_inline_limit_creates_no_full_output_artifact` |
| `LSN-0108` | `GUARDED` | LOW | process | Evidence timestamp transport must preserve RFC3339 rather than a shell locale rendering | `test_lesson_timestamp_transport_rejects_locale_rendering` |
| `LSN-0109` | `GUARDED` | HIGH | testing | Regression counts and evidence must exclude only policy-bound live input repositories | `test_only_declared_runner_exclusions_leave_both_count_and_evidence` |
| `LSN-0110` | `GUARDED` | CRITICAL | testing | A timed-out live proof retains bounded diagnostics before owned cleanup | `test_live_output_control_timeout_retains_bounded_diagnostics_and_stays_red`, `Gate7QualityObservationTests.test_iacode_wait_timeout_is_red_and_captures_only_closed_runtime_facts`, `Gate7QualityObservationTests.test_late_successful_diagnostic_never_promotes_the_expired_wait`, `Gate7QualityObservationTests.test_timeout_projection_refuses_malformed_private_and_excessive_metadata`, `Gate7QualityObservationTests.test_timeout_projection_follows_all_canonical_closed_states_and_result_statuses`, `Gate7QualityObservationTests.test_iacode_timeout_remains_red_if_its_diagnostic_dependency_is_unavailable`, `Gate7QualityObservationTests.test_actual_iacode_entrypoint_writes_a_red_timeout_report_before_owned_cleanup`, `Gate7NativeCleanupTests.test_deadline_retains_red_bounded_physical_facts`, `Gate7NativeCleanupTests.test_native_run_keeps_drain_failure_red_even_with_a_child_pass_report`, `Gate7NativeCleanupTests.test_failed_physical_wait_never_becomes_success_or_exposes_exception_body` |
| `LSN-0111` | `GUARDED` | HIGH | implementation | Polling watcher cleanup must preserve completed checks and accepted cancellation | `test_completed_check_joins_cancelled_durable_read_without_cancelling_run`, `test_unrelated_watcher_failure_is_not_hidden_by_join_cleanup` |
| `LSN-0112` | `GUARDED` | HIGH | security | Canonical scanner consumers must share transport decoding, not only patterns | `PublicationTransportScanningTests` |
| `LSN-0113` | `GUARDED` | CRITICAL | checkpoint | Stronger delivery controls must follow the immutable subject policy version | `test_live_policy_requires_strict_internal_verdict_semantics` |
| `LSN-0114` | `GUARDED` | MEDIUM | performance | Transport line metadata must not repeatedly scan the source prefix | `test_fragment_carrier_lines_count_each_source_range_at_most_once`, `test_json_error_line_index_matches_builtin_string_coordinates` |
| `LSN-0115` | `GUARDED` | MEDIUM | tooling | A failing full verifier retains every bounded case identifier beyond its output tail | `test_failed_case_identifiers_survive_a_tail_longer_than_the_report_limit` |
| `LSN-0116` | `GUARDED` | CRITICAL | tooling | A live resumability pointer is generated after Git boundaries, not committed into its own subject | `test_real_cli_roundtrip_is_clean_and_supports_internal_closure` |
| `LSN-0117` | `GUARDED` | CRITICAL | documentation | An architecture rollup must not contradict the delivered capability described below it | `test_architecture_rollup_does_not_deny_its_delivered_quality_engine`, `test_live_delivery_status_is_delegated_instead_of_hardcoded_in_rollups`, `Gate7RollupTests.test_current_rollups_do_not_deny_the_owned_capabilities`, `Gate7RollupTests.test_rollup_guard_has_positive_and_each_missing_denied_stale_mutation`, `Gate7RollupTests.test_original_published_readme_is_a_real_causal_negative_not_a_rewritten_fixture`, `Gate7DocumentationAndStreamsTests.test_development_documents_every_current_gate_and_registered_growth` |
| `LSN-0118` | `GUARDED` | HIGH | implementation | Post-response validation failures must preserve an accepted mutation's uncertain outcome | `test_signed_malformed_mutation_keeps_uncertainty_identity_and_one_effect` |
| `LSN-0119` | `GUARDED` | CRITICAL | quality | A clean publication scan does not replace the stricter checkpoint secret scan | `test_strict_checkpoint_sources_do_not_rely_on_publication_allowances`, `test_desktop_credential_remains_a_secret_type_and_safe_dump_redacts_it`, `test_every_current_changed_path_uses_the_strict_detector_including_checkpoint_harnesses`, `test_every_owned_wire_model_resolves_annotations_and_unresolved_control_is_refused` |
| `LSN-0120` | `GUARDED` | MEDIUM | quality | Native installation proofs must resolve the installed CLI entrypoint | `test_installed_cli_adapter_resolves_versioned_layout_and_refuses_escape` |
| `LSN-0121` | `GUARDED` | MEDIUM | quality | Standard-library host probes must not initialize application dependency graphs | `test_live_desktop_harness_cold_start_needs_only_the_standard_library` |
| `LSN-0122` | `GUARDED` | MEDIUM | environment | Engine-allocated host ports must be rediscovered after container restart | `test_restarted_api_rediscovers_its_port_and_checks_actual_authenticated_forwarding` |
| `LSN-0123` | `GUARDED` | HIGH | implementation | Consent binds workspace identity, not an uncanonicalized path spelling | `test_editor_preview_binding_uses_workspace_identity_not_path_spelling` |
| `LSN-0124` | `GUARDED` | HIGH | testing | Durable editor recovery must not use an in-memory test host | `test_native_recovery_proof_uses_persistent_storage_context` |
| `LSN-0125` | `GUARDED` | CRITICAL | environment | Native parent exit is not proof of process and profile cleanup | `test_native_process_tree_is_drained_even_after_parent_exits`, `test_owned_profile_cleanup_refuses_broad_targets_and_retries_only_sharing_locks`, `test_native_installer_and_host_both_pin_their_owned_shared_storage`, `test_zero_job_accounting_does_not_replace_observed_member_completion`, `test_unsignaled_owned_member_cannot_be_reported_as_drained_at_deadline`, `test_owned_job_snapshot_refuses_truncation_and_process_identity_reuse`, `test_owned_cleanup_failure_retains_observed_facts_and_original_error`, `test_owned_cleanup_success_records_real_removal_and_retry`, `test_native_cleanup_failure_report_never_promotes_functional_fixture_pass`, `Gate7NativeCleanupTests.test_natural_physical_completion_precedes_force_inside_original_deadline`, `Gate7NativeCleanupTests.test_forced_fallback_pins_late_members_without_extending_deadline`, `Gate7NativeCleanupTests.test_physical_signal_observed_after_total_deadline_remains_fail`, `Gate7NativeCleanupTests.test_failed_force_snapshot_stays_red_and_releases_original_handles`, `Gate7NativeCleanupTests.test_real_owned_member_premise_and_natural_exit_preserve_outside_sentinel`, `Gate7NativeCleanupTests.test_owned_bootstrap_disables_external_reporting_not_native_or_trust_controls`, `BootstrapOwnershipTests.test_actual_bootstrap_caller_requires_owned_native_process_boundary`, `BootstrapOwnershipTests.test_archived_actual_preimage_is_rejected_by_identical_caller_guard`, `BootstrapOwnershipTests.test_real_parent_exit_with_inherited_output_writer_is_observed_then_exactly_drained`, `BootstrapOwnershipTests.test_actual_history_query_requires_the_same_owned_native_boundary`, `BootstrapOwnershipTests.test_exact_published_history_preimage_is_rejected_by_the_same_guard` |
| `LSN-0126` | `GUARDED` | CRITICAL | security | Known authentication material is not domain or presentation data | `test_authentication_material_is_refused_before_replay_and_domain_io`, `test_known_opaque_capability_refused_in_declared_forms` |
| `LSN-0127` | `GUARDED` | HIGH | environment | Fresh runtime health does not initialize an operator-managed model catalog | `test_fresh_catalog_requires_sync_and_the_exact_authorized_model_without_substitution` |
| `LSN-0128` | `GUARDED` | CRITICAL | testing | Adversarial premises must use the actual public contract | `test_forgery_premise_joins_public_request_ids_to_actual_successful_sandbox_executions`, `test_cleanup_membership_derives_every_canonical_active_state_including_running`, `Gate7QualityObservationTests.test_owned_archive_premise_is_populated_before_observer_target`, `Gate7NativeCleanupTests.test_real_owned_member_premise_and_natural_exit_preserve_outside_sentinel` |
| `LSN-0129` | `GUARDED` | HIGH | implementation | Repeated cancellation must preserve an already cancelled terminal result | `test_repeated_cancel_of_cancelled_run_returns_unchanged_terminal_truth` |
| `LSN-0130` | `GUARDED` | HIGH | quality | Executable export line endings belong to the source and packaging contract | `test_commonjs_and_esm_exports_have_explicit_lf_attributes`, `test_builder_refuses_a_crlf_executable_instead_of_shipping_a_broken_linux_shebang` |
| `LSN-0131` | `GUARDED` | CRITICAL | quality | Raw evidence digests require byte-preserving Git export, not text normalization | `test_exact_byte_evidence_survives_git_transport_and_detects_normalization`, `Gate6BookkeepingCausalTests.test_actual_captured_output_hashes_and_git_attributes_preserve_bytes`, `docs/checkpoints/GATE-6-CP-0001/audit-harness/verify_evidence_transport.py`, `M2ObservationTransportTests.test_every_declared_copied_observation_survives_actual_archive_and_both_checkout_modes`, `M2ObservationTransportTests.test_removing_byte_boundaries_is_detected_beside_actual_binary_null`, `M2ObservationTransportTests.test_next_checkpoint_and_other_gate_observations_keep_the_same_real_byte_boundaries` |
| `LSN-0132` | `GUARDED` | HIGH | quality | Owned Git clones need read-only-aware cleanup, not native-profile lock retry | `test_verification_clone_cleanup_handles_real_readonly_git_objects` |
| `LSN-0133` | `GUARDED` | MEDIUM | tooling | Shared field names do not imply shared schema types | `test_current_provenance_is_validated_by_its_own_artifact_schema` |
| `LSN-0134` | `GUARDED` | MEDIUM | implementation | Configuration classifiers consume decoded values, not dotenv quote syntax | `test_host_literal_reader_matches_actual_compose_and_placeholder_semantics`, `test_malformed_quoted_env_literals_fail_closed_without_exposing_content`, `test_process_environment_overlays_are_values_not_dotenv_tokens` |
| `LSN-0135` | `GUARDED` | CRITICAL | quality | Capture producer evidence before fallible interpretation or owned cleanup | `test_raw_reports_survive_real_postprocessing_exception_and_owned_cleanup`, `test_raw_capture_refuses_secret_material_but_retains_neutral_failure_inventory`, `test_current_producer_bytes_survive_actual_consumer_failure_and_owned_cleanup`, `test_current_producer_capture_refuses_unsafe_bytes_without_losing_neutral_inventory`, `Gate7ProducerBoundaryTests.test_knowledge_raw_producer_survives_actual_consumer_refusal_before_clone_cleanup`, `Gate7ProducerBoundaryTests.test_prior_live_pass_is_preserved_and_retired_before_any_new_producer`, `Gate7PromotionProducerCaptureTests.test_owner_locator_and_all_originals_survive_real_consumer_error_and_cleanup`, `Gate7CanonicalProducerTests.test_all_canonical_producers_and_legacy_outputs_are_captured_without_private_extras`, `Gate7CanonicalProducerTests.test_canonical_registry_growth_is_bound_without_a_caller_selected_report_set`, `Gate7CanonicalProducerTests.test_all_current_originals_survive_real_consumer_refusal_and_actual_owner_cleanup`, `Gate7CanonicalProducerTests.test_claimed_success_cannot_omit_a_canonically_required_producer`, `Gate7CanonicalProducerTests.test_forwarding_uses_every_archived_original_after_actual_producer_cleanup`, `Gate7CanonicalProducerTests.test_bad_archived_input_never_partially_overwrites_any_prior_functional_target`, `Gate7CanonicalProducerTests.test_directory_or_hardlinked_output_is_refused_before_any_forwarding_effect`, `Gate7CanonicalProducerTests.test_verifier_consumer_uses_durable_original_not_a_second_temporary_read`, `Gate7RawReworkContextTests.test_every_original_context_is_inert_byte_bound_and_protected_by_real_git_attributes`, `ClientProducerCleanupEvidenceTests.test_both_failures_retain_distinct_actual_exit_and_streams`, `ClientProducerCleanupEvidenceTests.test_timeout_and_failed_cleanup_preserve_partial_real_output`, `ClientProducerCleanupEvidenceTests.test_successful_producer_with_failed_cleanup_cannot_pass`, `ClientProducerCleanupEvidenceTests.test_secret_and_oversized_output_are_not_disclosed`, `ClientProducerCleanupEvidenceTests.test_clean_null_control_returns_actual_producer`, `NativeProducerObservationTests.test_failed_callback_cannot_replace_real_nonzero_producer`, `NativeProducerObservationTests.test_timeout_and_callback_failure_keep_both_observations`, `NativeProducerObservationTests.test_capture_handle_release_failure_cannot_replace_primary_observation`, `NativeProducerObservationTests.test_native_actor_forwards_producer_facts_without_approving_cleanup_failure`, `BridgePhysicalBoundsTests.test_output_prefix_is_fixed_before_a_controlled_actual_append` |
| `LSN-0136` | `GUARDED` | MEDIUM | implementation | Strict JSON validation loses transport context | `test_exact_closed_roundtrip`, `test_permissions_require_exact_boolean`, `test_numeric_observations_are_not_coerced` |
| `LSN-0137` | `GUARDED` | MEDIUM | testing | SQL text interprets inline JSON colons as bindings | `test_legacy_migration_preserves_identity_body_and_rights_without_promotion`, `test_database_immutability_and_direct_corruption_fail_closed` |
| `LSN-0138` | `GUARDED` | HIGH | security | Secret projection distinguishes public identities from authorization secrets | `test_public_minio_identity_is_not_a_bearer_secret_but_storage_password_stays_protected`, `test_known_opaque_capability_refused_in_declared_forms` |
| `LSN-0139` | `GUARDED` | HIGH | security | Privacy projection begins in the source query | `test_actual_sql_projection_does_not_fetch_unneeded_private_source_columns`, `test_oversized_required_source_json_is_refused_before_materialization_and_writes` |
| `LSN-0140` | `GUARDED` | CRITICAL | quality | Summaries preserve canonical continuation structure | `test_local_handoff_renderer_preserves_the_complete_canonical_contract`, `test_local_handoff_renderer_refuses_omitted_or_empty_sections_and_next_action`, `test_retrospective_preserves_template_and_every_current_gate_lesson`, `Gate7ContinuationContractTests.test_actual_current_handoff_and_next_preserve_canonical_structure`, `Gate7ContinuationContractTests.test_actual_retrospective_uses_exact_template_and_every_current_lesson_guard`, `Gate7ContinuationContractTests.test_actual_renderer_and_each_missing_empty_extra_or_reordered_section_refusal`, `Gate7ContinuationContractTests.test_retrospective_positive_omission_extra_and_registered_lesson_growth`, `Gate7ContinuationContractTests.test_original_failed_documents_remain_exact_inert_and_rejected`, `CorrectiveContinuationTests.test_actual_corrective_and_current_handoff_next_preserve_existing_contract`, `CorrectiveContinuationTests.test_actual_retrospectives_keep_exact_sections_and_every_recorded_lesson_guard`, `CorrectiveContinuationTests.test_actual_failed_original_is_exact_inert_and_rejected_by_identical_contract`, `CorrectiveContinuationTests.test_current_positive_and_omission_empty_extra_order_and_lesson_growth_controls` |
| `LSN-0141` | `GUARDED` | HIGH | testing | Preflight checks honor every declared applicability dimension | `test_repository_preflight_accepts_all_declared_filters_but_refuses_unexplained_omission` |
| `LSN-0142` | `GUARDED` | HIGH | environment | Local Engine recovery keeps transport and cleanup scoped | `test_local_engine_selection_is_child_only_and_preserves_project_and_failure`, `test_owned_recovery_refuses_operational_or_mislabelled_resources_before_removal` |
| `LSN-0143` | `GUARDED` | HIGH | environment | Management recovery is not complete runtime capability | `test_management_only_report_cannot_replace_complete_non_fast_verification` |
| `LSN-0144` | `GUARDED` | HIGH | documentation | Raw archived observations retain original context rather than becoming active relocated documents | `Gate6BookkeepingCausalTests.test_raw_archive_catalog_retains_manifest_and_published_original_bytes`, `SetupChecklistTests.test_documentation_links_resolve` |
| `LSN-0145` | `GUARDED` | MEDIUM | testing | A new persistent capability must extend the explicit structural contract, not bypass its exact inventory | `test_exact_table_inventory_refuses_each_missing_and_extra_table`, `test_fact_lifecycle_classification_refuses_each_wrong_knowledge_role`, `test_actual_foreign_key_contract_refuses_each_changed_knowledge_cascade`, `test_actual_retention_check_tracks_lifecycle_version_without_payload_rewrite` |
| `LSN-0146` | `GUARDED` | CRITICAL | process | A completed command record is not proof that its producing process has exited | `Gate7ProcessCompletionTests.test_process_owned_sequence_waits_for_real_success_before_consumer`, `Gate7ProcessCompletionTests.test_success_looking_output_then_actual_failure_never_starts_consumer`, `Gate7TypedObservationTests.test_real_running_and_failed_children_are_not_completed_source_observations` |
| `LSN-0147` | `GUARDED` | HIGH | tooling | Framework lifecycle errors need bounded identities as well as test methods | `Gate7FrameworkDiagnosticsTests.test_framework_methods_and_lifecycle_headers_survive_without_private_bodies`, `Gate7FrameworkDiagnosticsTests.test_framework_identity_count_and_length_limits_remain_unchanged` |
| `LSN-0148` | `GUARDED` | HIGH | security | Minimal protocol fixtures inherit control contracts, never deployment-owned source data | `Gate7MinimalProtocolIsolationTests.test_fixture_copies_contracts_and_never_source_data_history_or_unrelated_verdicts`, `Gate7MinimalProtocolIsolationTests.test_a_retained_contract_broken_link_still_fails_the_real_mirror`, `PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit` |
| `LSN-0149` | `GUARDED` | HIGH | tooling | A shell exit zero is not a produced digest or verified original evidence | `Gate7TypedObservationTests.test_real_running_and_failed_children_are_not_completed_source_observations`, `Gate7TypedObservationTests.test_only_typed_nonempty_actual_bytes_size_and_digest_are_evidence`, `Gate7TypedObservationTests.test_actual_file_mutations_and_atomic_readonly_source_envelope` |
| `LSN-0150` | `GUARDED` | HIGH | security | Build and verification root inputs need subject-versioned assurance binding | `Gate7RootInputFingerprintTests.test_build_and_verification_edits_invalidate_actual_assurance_fingerprint`, `Gate7RootInputFingerprintTests.test_every_current_root_is_bound_even_if_ignored_and_deletion_invalidates`, `Gate7RootInputFingerprintTests.test_absent_and_v1_subjects_keep_their_original_root_fingerprint_identity`, `Gate7RootInputFingerprintTests.test_current_policy_refuses_missing_narrowed_reordered_extra_and_malformed_inputs` |
| `LSN-0151` | `GUARDED` | CRITICAL | quality | Immutable Git object reads must handle Windows long paths only in the owning child | `Gate7GitTransportTests.test_real_long_object_expression_returns_every_original_binary_byte`, `Gate7GitTransportTests.test_git_override_is_child_scoped_and_leaves_local_and_global_settings_unchanged`, `Gate7GitTransportTests.test_genuine_git_failure_stays_failed_without_rewriting_configuration_or_input`, `ReviewBundleTests.test_immutable_subject_rebuilds_are_byte_identical_and_exclude_only_the_sidecar`, `ReviewBundleTests.test_declared_digest_and_size_are_rebuilt_not_trusted`, `M2HistoryTransportTests.test_real_short_null_and_long_materialization_preserve_config_and_refusal`, `M2HistoryTransportTests.test_genuine_bad_subject_remains_refused_without_configuration_effects`, `M2HistoryTransportTests.test_legacy_git_read_gets_exact_bytes_only_with_child_runtime_override`, `M2HistoryTransportTests.test_child_runtime_configuration_preserves_existing_pairs_and_refuses_malformed_input` |
| `LSN-0152` | `GUARDED` | MEDIUM | security | Private runner inputs require physical containment, not lexical ancestry | `BridgePhysicalBoundsTests.test_actual_inside_null_and_absolute_escape_refusal`, `BridgePhysicalBoundsTests.test_parent_relative_existing_escape_is_refused`, `BridgePhysicalBoundsTests.test_parent_alias_in_the_source_root_is_refused`, `BridgePhysicalBoundsTests.test_redirected_owned_ancestor_and_hardlink_are_refused`, `BridgePhysicalBoundsTests.test_report_escape_keeps_producer_but_never_archives_outside_content` |

## Detail

### LSN-0001 — Checkpoint validation must succeed from a detached checkout of the checkpoint tag

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0003, finding R1.
- Symptom: The documented second-tool procedure checked out the checkpoint tag and then validated, which reported CHECKPOINT_INVALID with a branch mismatch even though the commit was correct.
- Root cause: Validation compared the branch name unconditionally, and a tag checkout produces a detached HEAD, so the branch control rejected the very procedure the handoff prescribed.
- Resolution: Detached validation is accepted only when the worktree is clean, the recorded commit is the checkpoint's canonical tag, that tag exists, and it resolves to the checked-out commit.
- Prevention:
  - `test` DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates — A clean detached checkout at the checkpoint tag validates.
  - `test` DetachedHeadValidationTests.test_detached_head_at_wrong_commit_fails — A detached checkout at any other commit is refused.
  - `validator` scripts/development-ledger/validate_checkpoint.py — The git binding branches on attached and detached checkouts.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0003/DECISIONS.md`, `file:docs/adr/ADR-0006-checkpoint-inventory-binding.md`, `file:docs/checkpoints/SETUP-00-CP-0004/REVIEW-REPORT.md`

### LSN-0002 — A file inventory must be recomputed from the repository, never trusted as an assertion

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0003, finding R2.
- Symptom: Removing an entry from FILES.json, or silently altering a tracked file, still returned CHECKPOINT_VALID for a delta checkpoint.
- Root cause: The completeness and hash controls ran only when the base commit was UNBORN, so a delta checkpoint's manifest was an unverified human claim.
- Resolution: The change set between the base commit and the validated tree is recomputed from Git and compared to the manifest exactly, with hashAfter on added and modified paths and hashBefore on modified and deleted paths.
- Prevention:
  - `test` DeltaInventoryTests.test_removed_manifest_entry_fails — A manifest that omits a changed path is rejected.
  - `test` DeltaInventoryTests.test_silent_tracked_modification_fails — A tracked file altered without declaration is rejected.
  - `validator` scripts/development-ledger/validate_checkpoint.py — _validate_delta_inventory compares the manifest against the real change set.
- Evidence: `file:docs/adr/ADR-0006-checkpoint-inventory-binding.md`, `file:docs/checkpoints/SETUP-00-CP-0003/RED-TEAM-DEV-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0004/REVIEW-REPORT.md`

### LSN-0003 — Every operation attempt must be auditable, including a refusal decided before execution

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0004, finding R3 (SETUP-00-CP-0004 review, decomposed as R3.1 in SETUP-00-CP-0005) and RT-02.
- Symptom: Finalization refused for a detached HEAD returned exit 2 while the command ledger stayed at the same number of records, so the attempt disappeared.
- Root cause: The tool returned before reaching the code that records an attempt, so an entire class of attempts left no trace while the protocol claimed every attempt was recorded.
- Resolution: Preconditions are evaluated first and the attempt is appended before the error is returned, with the evaluated preconditions, a canonical PRECONDITION_REJECTED result, a documented result code and a failure reason, and no fabricated exit code.
- Prevention:
  - `test` FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded — A detached-HEAD refusal is appended to the ledger.
  - `test` FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded — A refusal for a checkpoint that is not LATEST is appended.
  - `validator` scripts/development-ledger/finalize_checkpoint.py — _record_attempt runs on every path, including precondition refusals.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0004/RED-TEAM-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0005/DECISIONS.md`, `file:docs/adr/ADR-0008-delivery-assurance-gates.md`

### LSN-0004 — A checkpoint may never claim readiness while it also claims to be blocked

- Status: `GUARDED`, severity CRITICAL, category checkpoint, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0004, finding RT-01.
- Symptom: A fully resealed checkpoint with status READY_FOR_REVIEW and a non-empty blockedBy returned CHECKPOINT_VALID.
- Root cause: The blocker list was inspected only for GATE_PASS, so every other readiness status could contradict itself without detection.
- Resolution: READY_FOR_REVIEW, READY_FOR_RED_TEAM and GATE_PASS require an empty blockedBy in every schema version, and BLOCKED requires a stated blocker.
- Prevention:
  - `test` StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails — Readiness with a blocker is refused.
  - `test` ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected — The escaped attack is refused end to end by the finalizer and the validator.
  - `invariant` _validate_status_blockers — Status and blocker consistency is a universal invariant, not a per-version rule.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0004/RED-TEAM-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0005/HANDOFF.md`

### LSN-0005 — A PASS requires evidence that can be executed or resolved, not a statement

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 6.
- Source: SETUP-00, SETUP-00-CP-0003, finding R6.
- Symptom: A quality dimension was recorded as PASS in a checkpoint that contained no corresponding execution.
- Root cause: Quality results were bare verdicts with no link to the run that produced them, so a verdict could be inherited from an earlier checkpoint without re-execution.
- Resolution: Every dimension records status, evidence and justification, and a PASS needs at least one reference that resolves to a successful command record or a non-empty file.
- Prevention:
  - `test` QualityEvidenceTests.test_pass_without_evidence_fails — A PASS with no evidence is rejected.
  - `test` QualityEvidenceTests.test_pass_referencing_a_failed_command_fails — A PASS pointing at a failed command is rejected.
  - `validator` scripts/development-ledger/validate_checkpoint.py — _validate_quality_evidence resolves every reference.
  - `invariant` validate_checkpoint._validate_quality_evidence — A PASS without resolvable evidence is refused for every positive terminal status.
  - `test` PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension — Every positive status is exercised against every mandatory red quality dimension.
- Evidence: `file:docs/adr/ADR-0007-checkpoint-schema-2-and-independent-promotion.md`, `file:docs/QUALITY-GATES.md`, `file:docs/checkpoints/GATE-4-CP-0009/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0009/REWORK-LOG.jsonl`

### LSN-0006 — The repository must be self-contained; a specification may not live outside it

- Status: `GUARDED`, severity MEDIUM, category documentation, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0003, finding R5.
- Symptom: The Master Plan accepted the Gate against a checklist that existed only in an external prompt file on one machine.
- Root cause: The authoritative requirement was never committed, so completeness could not be verified from the repository alone even though the entry contract claimed the repository was the only source of truth.
- Resolution: The specification was written into docs/SETUP-00-CHECKLIST.md and the Master Plan and start protocol now reference it.
- Prevention:
  - `test` SetupChecklistTests.test_checklist_exists_and_is_referenced — The in-repository specification exists and is referenced.
  - `test` SetupChecklistTests.test_documentation_links_resolve — Every relative documentation link resolves.
- Evidence: `file:docs/SETUP-00-CHECKLIST.md`, `file:docs/checkpoints/SETUP-00-CP-0004/REVIEW-REPORT.md`

### LSN-0007 — Independent validation cannot be declared by the run that did the work

- Status: `GUARDED`, severity CRITICAL, category process, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0003, finding R4 (SETUP-00-CP-0003 review) and R7 (SETUP-00-CP-0004 review).
- Symptom: The implementing run produced its own review and Red Team reports and the earlier checkpoint reached GATE_PASS on that basis.
- Root cause: Cross-tool validation was a sentence in a document rather than structured state, so nothing prevented an implementer from certifying itself.
- Resolution: secondToolValidation is structured state, GATE_PASS requires it to be PASSED or a justified NOT_REQUIRED, and READY_FOR_REVIEW requires independentReview and redTeam to still be PENDING.
- Prevention:
  - `test` SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass — A failed cross-tool validation cannot promote a Gate.
  - `test` DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review — An implementing run cannot record its own independent verdict.
  - `schema` .iacode/schemas/checkpoint.schema.json — The cross-tool and independent verdict states are enumerated, not free text.
  - `validator` scripts/development-ledger/attestation.py — An external verdict is derived from an attestation authored by another checkpoint.
  - `test` ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass — A delivery that declares its own external PASS is refused.
- Evidence: `file:docs/adr/ADR-0007-checkpoint-schema-2-and-independent-promotion.md`, `file:docs/checkpoints/SETUP-00-CP-0004/DECISIONS.md`, `file:docs/checkpoints/SETUP-00-CP-0004/REVIEW-REPORT.md`

### LSN-0008 — Requirement completeness must be total and evidence-backed before handoff

- Status: `GUARDED`, severity CRITICAL, category process, recurrences 3.
- Source: SETUP-00, SETUP-00-CP-0005, finding prompt sections 9 and 10.
- Symptom: The independent tool was spending its effort discovering unimplemented requirements and missing evidence rather than auditing design.
- Root cause: No artifact held the complete requirement set, so completeness was a judgement made from memory of the conversation.
- Resolution: Requirements are extracted into REQUIREMENTS-MATRIX.json before implementation and audited by a validator that resolves every evidence reference and refuses anything short of total coverage; the terminal finalizer also refuses a handoff whose canonical final-report structure is incomplete. Gate6 recurrence3 adds a canonical final-report renderer which consumes the unchanged owning-validator heading set and rejects incomplete or empty input before writing. Actual cmd-0343 passes the formerly failing positive and every-section adverse controls; whole fresh immutable assurance remains mandatory.
- Prevention:
  - `test` DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails — Coverage below total fails the audit.
  - `test` DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review — An unexecuted completeness audit blocks readiness.
  - `validator` scripts/development-ledger/check_completeness.py — Completeness is recomputed over an independently derived expected set.
  - `test` ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails — Deleting a requirement and recomputing every count still fails.
  - `validator` scripts/development-ledger/validate_checkpoint.py — The unchanged terminal validator refuses a final report lacking any canonical heading.
  - `test` Gate6BookkeepingCausalTests.test_final_report_renderer_consumes_every_canonical_section — The actual assembler consumes the owning validator section set in order with substantive content.
  - `test` Gate6BookkeepingCausalTests.test_final_report_renderer_refuses_each_missing_empty_or_extra_section — Every omitted or empty canonical section and an invented extra section is refused.
- Evidence: `file:docs/adr/ADR-0008-delivery-assurance-gates.md`, `file:docs/checkpoints/SETUP-00-CP-0005/COMPLETENESS-REPORT.md`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/RUNTIME-V6-FINALIZATION-ARCHIVE.json`

### LSN-0009 — A red gate requires rework, never a waiver, and never a weakened check

- Status: `GUARDED`, severity CRITICAL, category testing, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0005, finding prompt section 8.
- Symptom: Nothing structurally prevented a delivery from being offered while a mandatory gate was red.
- Root cause: Greenness was a habit rather than a recorded, verified state, and no artifact tied a failure to the repair that resolved it.
- Resolution: The Green Keeper runs the mandatory gates, records every cycle with its root cause in REWORK-LOG.jsonl, and GREEN_KEEPER_GATE is PASS only when nothing is red and no rework item is unresolved.
- Prevention:
  - `test` GreenKeeperToolTests.test_red_gate_is_reported_as_still_red — A red gate is reported as still red and exits nonzero.
  - `test` DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected — A PASS that contradicts the last cycle is rejected.
  - `test` DeliveryAssuranceGateTests.test_red_tests_block_review — A failing quality dimension blocks readiness.
  - `policy` .iacode/policies/quality-gates.json — The mandatory gate set is closed by policy and cannot be narrowed by an invocation.
  - `test` MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected — A cycle measured against no gate cannot produce a PASS.
- Evidence: `file:.iacode/agents/test-rework-greenkeeper.md`, `file:docs/checkpoints/SETUP-00-CP-0005/REWORK-LOG.jsonl`

### LSN-0010 — A recorded command must carry runtime, working directory, commit and purpose to be replayable

- Status: `GUARDED`, severity CRITICAL, category tooling, recurrences 3.
- Source: SETUP-00, SETUP-00-CP-0004, finding R3 (SETUP-00-CP-0004 review, decomposed as R3.2 in SETUP-00-CP-0005).
- Symptom: Recorded finalizer commands named a bare script that does not exist in the working directory they declared, so the ledger could not be replayed.
- Root cause: The record stored a convenient label rather than the literal invocation, and nothing checked that the label could be executed.
- Resolution: CP0003 local prevention restored by actual current producer/null/adverse controls and unchanged inherited controls. Whole current immutable verification, ordered internal assurance and fresh independent M2 validation remain separate obligations.
- Prevention:
  - `test` CommandReproducibilityTests.test_bare_script_name_is_rejected — A bare script name is rejected.
  - `test` CommandReproducibilityTests.test_unresolvable_script_path_is_rejected — A script path that does not resolve is rejected.
  - `schema` .iacode/schemas/command.schema.json — The reproducibility fields are part of the record contract.
  - `invariant` validate_checkpoint._validate_command_reproducibility — A record that names an input must bind it by content hash.
  - `test` CommandInputBindingTests.test_a_record_without_a_digest_is_rejected — A record without an input digest is refused.
  - `test` CheckpointInvocationProducerTests.test_custom_phase_and_quoted_unicode_replay_are_literal — Actual producer/replay causal boundary with null and adverse controls.
  - `test` CheckpointInvocationProducerTests.test_omitted_default_status_is_not_invented — Actual producer/replay causal boundary with null and adverse controls.
  - `test` CheckpointInvocationProducerTests.test_nested_working_directory_and_explicit_root_replay — Actual producer/replay causal boundary with null and adverse controls.
  - `test` CheckpointInvocationProducerTests.test_default_null_control_preserves_supplied_invocation — Actual producer/replay causal boundary with null and adverse controls.
  - `test` CheckpointInvocationProducerTests.test_registered_m2_attack_runs_actual_null_and_phase_human_replay — Executed actual current positive/adverse control; no production fake or independent verdict.
  - `test` CheckpointInvocationProducerTests.test_registered_m2_attack_reproduces_old_phase_escape_with_valid_null — Executed actual current positive/adverse control; no production fake or independent verdict.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0004/REVIEW-REPORT.md`, `file:scripts/development-ledger/record_command.py`, `file:docs/checkpoints/GATE-7-CP-0002/FINDINGS.json`, `file:tests/test_m2_audit_corrections.py`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0005.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0006.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0011.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/native-observation/run-0003.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge-physical-bounds/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge/run-0005.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/owned-cleanup/run-0004.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/operator-cleanup/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/current-streams/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/inherited-streams/run-0001.json`

### LSN-0011 — A control over a checkpoint's own evidence must be scoped to the moment it matters

- Status: `GUARDED`, severity CRITICAL, category tooling, recurrences 15.
- Source: SETUP-00, SETUP-00-CP-0005, finding REWORK-LOG cycles 1 to 3 and 6.
- Symptom: The gate that validates the checkpoint kept failing because running it appends to the very ledger and inventory the validation binds.
- Root cause: Consistency rules written for a finished delivery were applied while the delivery was still writing its own evidence, which no ordering of steps can satisfy.
- Resolution: Restore the canonical synchronizer/hash/validator adapter without a stale STATE snapshot. The original complete metadata class passes cmd-0127, including terminal/other-gate refusal. Inventory and current whole-delivery validation remain separately mandatory. Local executable guard restoration only; the failed immutable runtime-v1 remains FAIL. A new complete immutable invocation and every ordered internal assurance control are still required before readiness; independent M2 validation remains pending.
- Prevention:
  - `test` DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress — Provisional in progress, strict at handoff.
  - `invariant` green_keeper._refresh_declared_hashes — Declared hashes are re-derived before the validation gate runs, never invented.
  - `test` test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes — Every command that executes the mandatory gate set re-derives the checkpoint's declared hashes before it does.
  - `test` test_green_keeper_declares_its_in_progress_evidence_dirty_before_validation — An in-progress cycle expects its own command and rework evidence to make the tree dirty before checkpoint validation.
  - `test` test_preflight_aggregates_and_commit_semantics_are_derived_without_promotion — The in-progress preflight aggregates and finalCommit semantics are derived together without altering status, verdicts or evidence.
  - `test` test_a_sealed_or_terminal_checkpoint_is_never_rewritten — Synchronization cannot rewrite immutable or terminal evidence.
  - `test` test_validation_runner_keeps_the_synchronizers_derived_state — The actual wrapper preserves real synchronizer output at its hash boundary instead of restoring a stale snapshot.
  - `test` test_bookkeeping_sequence_awaits_each_recorder_and_keeps_canonical_order — The actual synchronous sequencer waits for complete recorder exit and never starts validation after a failed inventory recorder.
  - `test` test_bookkeeping_sequence_never_validates_after_inventory_recorder_failure — The actual synchronous sequencer waits for complete recorder exit and never starts validation after a failed inventory recorder.
  - `test` InProgressMetadataTests.test_validation_runner_keeps_the_synchronizers_derived_state — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0005/DECISIONS.md`, `file:docs/checkpoints/SETUP-00-CP-0005/REWORK-LOG.jsonl`, `file:docs/checkpoints/GATE-4-CP-0005/REWORK-LOG.jsonl`, `file:docs/checkpoints/GATE-4-CP-0009/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0009/REWORK-LOG.jsonl`, `file:docs/checkpoints/GATE-4-CP-0009/audit-harness/run_checkpoint_validation.py`, `file:scripts/development-ledger/finalize_checkpoint.py`, `file:scripts/development-ledger/green_keeper.py`, `file:scripts/iacode/verify.py`, `file:tests/test_development_ledger.py`, `file:tests/test_gate1_model_gateway.py`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:scripts/development-ledger/sync_in_progress_metadata.py`, `file:tests/test_in_progress_metadata.py`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/audit-harness/validate_serial_bookkeeping.py`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:tests/test_gate7_assurance.py`, `file:tests/test_gate7_knowledge.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`

### LSN-0012 — Sealed checkpoints and their tags are immutable, and tooling must keep validating them

- Status: `GUARDED`, severity CRITICAL, category git, recurrences 3.
- Source: SETUP-00, SETUP-00-CP-0002, finding checkpoint protocol.
- Symptom: Every correction cycle created pressure to edit or retag an earlier checkpoint so the new rules would fit it.
- Root cause: Control-plane rules evolve while history does not, so without version dispatch a new rule silently invalidates sealed evidence.
- Resolution: Bind every evolving invariant to the immutable subject's declared policy version: strict internal verdicts under memory policy 2.4.0, collection boundaries under test-suite policy 1.1.0. Keep legacy semantics, refuse current downgrades/new fields under old versions, and execute current validation over every canonical sealed anchor.
- Prevention:
  - `test` HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates — The first sealed checkpoint still validates.
  - `test` HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates — The most recent sealed review checkpoint still validates.
  - `policy` docs/CHECKPOINT-PROTOCOL.md — Schema versions and immutability are stated in the protocol.
  - `validator` scripts/development-ledger/anchors.py — The sealed chain of tags, commits and trees is re-derived from Git.
  - `test` IntegrityAnchorTests.test_a_moved_historical_tag_is_detected — A moved historical tag is detected.
- Evidence: `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/adr/ADR-0007-checkpoint-schema-2-and-independent-promotion.md`

### LSN-0013 — An installed capability must be detected by resolved path, not by a bare command lookup

- Status: `CONFIRMED`, severity HIGH, category environment, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0002, finding detection correction.
- Symptom: A checkpoint recorded that a tool was not installed because a bare command lookup failed, when the tool was installed outside the detecting process PATH.
- Root cause: Absence was inferred from one lookup mechanism rather than from a search of resolved locations, so a configuration detail was recorded as a capability fact.
- Resolution: Capability records name the resolved executable path and the version it reported, and a failed bare lookup is recorded as a PATH observation rather than as absence. Repository quality checks use their canonical gate wrapper and pinned runtime instead of assuming a host Python module exists.
- Prevention:
  - `documentation` docs/TOOL-CAPABILITIES.md — Detected capabilities are recorded with resolved paths and the PATH caveat.
- Evidence: `file:docs/TOOL-CAPABILITIES.md`, `file:docs/adr/ADR-0003-tool-neutral-agents.md`, `file:docs/checkpoints/SETUP-00-CP-0002/DECISIONS.md`, `file:docs/checkpoints/GATE-4-CP-0009/COMMANDS.jsonl`

### LSN-0014 — Evidence must be recorded as it happens, not reconstructed at the end of a run

- Status: `GUARDED`, severity MEDIUM, category process, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0003, finding ledger backfill.
- Symptom: Part of a command ledger was written after the fact because the recorder was introduced mid-run, so timestamps were recording times rather than execution times.
- Root cause: The ledger was treated as a report produced at the end instead of an instrument used during the work.
- Resolution: Commands are recorded through the tooling as they run, and any record written after the fact states that its timestamp is a recording time.
- Prevention:
  - `automated-check` scripts/development-ledger/record_command.py — Recording a command captures its real timing and repository state at execution.
  - `invariant` validate_checkpoint._validate_seal_chronology — Sealing is monotonic and its final evidence describes the sealed commit.
  - `test` SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected — A ledger record later than the recorded end of the run is refused.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0003/DECISIONS.md`, `file:scripts/development-ledger/record_command.py`, `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`

### LSN-0015 — Every positive terminal status needs one shared promotion invariant

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-001 / M0-F-002.
- Symptom: A checkpoint mutated to MILESTONE_EXTERNAL_PASS with greenKeeper.status=FAIL produced no validation error, because the strong promotion checks were written only for READY_FOR_REVIEW.
- Root cause: The promotion rules were attached to one status rather than to the concept of a positive terminal status, so each new status silently started with no rules.
- Resolution: One invariant is evaluated for every positive terminal status, and each status adds requirements on top of it instead of replacing it.
- Prevention:
  - `invariant` validate_checkpoint._validate_delivery_assurance — One promotion invariant is evaluated for every positive terminal status.
  - `test` PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper — Every positive status refuses a red Green Keeper gate.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md`

### LSN-0016 — A mandatory set must be closed by policy, never chosen by the caller

- Status: `GUARDED`, severity CRITICAL, category testing, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-005.
- Symptom: green_keeper.py --gates "" exited zero and wrote GREEN_KEEPER_GATE=PASS with an empty command list, and checkpoint validation accepted it next to a failing test.
- Root cause: The tool asked its caller which gates were mandatory. A control whose scope is an argument can always be reduced to nothing.
- Resolution: The mandatory gate set is read from a machine-readable policy registry. An invocation may extend a run; it can no longer shrink the mandatory set.
- Prevention:
  - `invariant` validate_checkpoint._validate_green_keeper_cycle — A GREEN cycle must have executed exactly the canonical mandatory set.
  - `policy` .iacode/policies/quality-gates.json — The mandatory set is a registry, not an argument.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md`

### LSN-0017 — A completeness denominator must come from a source the delivery does not own

- Status: `GUARDED`, severity CRITICAL, category process, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-006 / M0-F-008.
- Symptom: Deleting a mandatory requirement and recomputing every stored count left the matrix at 46 of 46, and both the completeness audit and checkpoint validation passed.
- Root cause: Coverage was computed over the submitted set, so the submitted set decided what total coverage meant.
- Resolution: The expected identifier set is derived from the canonical Gate specification, the lesson preflight and the open audit findings, and is compared with the declared set exactly.
- Prevention:
  - `invariant` policies.expected_requirement_refs — The expected identifier set is derived from the canonical sources and compared exactly.
  - `test` ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected — An anchored requirement outside the expected set is refused.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0007/MILESTONE-REPORT.md`

### LSN-0018 — A structured reference must be resolved, not merely well typed

- Status: `GUARDED`, severity CRITICAL, category tooling, recurrences 3.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-004 / M0-F-003.
- Symptom: A GUARDED lesson naming a nonexistent test, a lesson citing a nonexistent evidence file, and a secret-shaped value nested in prevention.description all validated.
- Root cause: Validation checked that a field had the right shape and never asked the repository whether the thing it named exists.
- Resolution: G7-INT-005: correct only the guard's test-kind locator to the actual discovered test identity. Cmd-0044 passes every unchanged LessonResolutionTests case (missing test/file, wrong kind and path escape included). Every earlier recurrence and original cmd-0043 refusal remains; canonical full memory validation follows before handoff.
- Prevention:
  - `invariant` lessons.resolve_control — Every control reference is resolved against the suite or the repository.
  - `test` LessonResolutionTests.test_a_test_control_must_exist_in_the_suite — A control naming a nonexistent test is refused.
  - `test` QualityEvidenceTests.test_pass_referencing_a_failed_command_fails — The owning quality evidence resolver refuses a failed command as structured successful execution evidence.
  - `test` QualityEvidenceTests.test_pass_referencing_an_existing_checkpoint_file_passes — A durable actual checkpoint-local file resolves through the owning quality evidence boundary.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0007/AUDIT-EXECUTIONS.md`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`

### LSN-0019 — A derived artifact must carry a fingerprint of the inputs that produced it

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-003.
- Symptom: Retiring a canonical lesson left the stale active preflight in place, and both the memory and the checkpoint still validated; a GATE 1 state also reused a SETUP-00 preflight.
- Root cause: Freshness was judged by comparing the artifact with the state that stored its own counts, and by a timestamp, instead of by recomputing it from its inputs.
- Resolution: The preflight records a content fingerprint of the memory, the guardrail registry, the lesson schema, the selection policy and the Gate inputs, and validation recomputes both the fingerprint and the selection.
- Prevention:
  - `invariant` lessons.preflight_staleness — A derived artifact is recomputed, and a changed input makes it stale.
  - `test` PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale — Retiring or dropping a lesson makes an existing preflight stale.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md`

### LSN-0020 — Evidence produced from a dirty tree needs immutable input identity

- Status: `GUARDED`, severity CRITICAL, category tooling, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-009 / M0-F-010.
- Symptom: Sampled commands replayed at the sealed tag but failed at their own declared commits, and a run claimed to finish three seconds before the finalizer that sealed it ran.
- Root cause: A record named a commit while its real inputs lived only in an uncommitted working tree, and the sealing order let the recorded chronology contradict itself.
- Resolution: Every record binds its declared inputs by content hash, and sealing is a monotonic post-commit workflow whose final validation is recorded against a clean tree at the sealed content commit. A process-owning recorder freezes declared input digests before launching the child and passes that snapshot explicitly to the metadata builder; hashing after completion cannot identify what was launched.
- Prevention:
  - `invariant` ledger_common.build_command_record — Every declared input is bound by content hash at execution time.
  - `test` CommandInputBindingTests.test_the_recorder_binds_inputs_automatically — The recorder binds inputs without being asked.
  - `test` test_input_digests_are_frozen_before_a_real_child_rewrites_its_inputs — Execute a real self-rewriting child and compare both recorded digests with observed pre-execution identities, retaining a stable-input control.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0007/AUDIT-EXECUTIONS.md`

### LSN-0021 — Sealed history needs an anchor outside the content it describes

- Status: `GUARDED`, severity CRITICAL, category git, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-007.
- Symptom: Moving a checkpoint tag together with HEAD validated, and rewriting a sealed predecessor while refreshing the dependent hashes also validated.
- Root cause: Every expected value lived inside the mutable checkpoint content, so a coordinated edit left nothing to contradict.
- Resolution: A hash-linked anchor chain records the tag, commit and tree of every sealed checkpoint in an earlier commit than the objects it anchors, and validation re-derives all of it from Git.
- Prevention:
  - `invariant` anchors.verify_chain — The anchored tag, commit and tree of every sealed checkpoint are re-derived from Git.
  - `test` IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected — A broken link between two anchors is detected.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0007/RED-TEAM-REPORT.md`

### LSN-0022 — An authoritative count must be derived once, never maintained by hand twice

- Status: `GUARDED`, severity CRITICAL, category documentation, recurrences 2.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-008.
- Symptom: The sealed CP-0006 state declared 47 mandatory requirements while the matrix and the completeness report both computed 45, and validation never compared them.
- Root cause: The same number was written by hand in several artifacts, so the artifacts could disagree without any tool noticing.
- Resolution: Counts used as evidence are derived into machine-readable artifacts, cross-checked against state and report aggregates, and verified wherever a report states them; the terminal finalizer remains the authoritative cross-check before promotion.
- Prevention:
  - `invariant` validate_checkpoint._validate_derived_counts — Counts used as evidence are derived once and verified wherever they are stated.
  - `test` DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected — A report that states a count contradicting the derivation is refused.
  - `test` SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim — No comment or docstring in scripts/ or tests/ states a derived count.
  - `policy` docs/QUALITY-GATES.md — A count stated in a source comment or docstring is not evidence.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0007/MILESTONE-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md`

### LSN-0023 — A lesson must cite a source that actually records the finding it claims

- Status: `GUARDED`, severity MEDIUM, category documentation, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-011.
- Symptom: LSN-0007 attributed findings R4 and R7 to SETUP-00-CP-0003, but R7 is recorded in the SETUP-00-CP-0004 review.
- Root cause: Provenance was written from recollection of where a finding had been discussed, and nothing resolved the citation against the cited checkpoint.
- Resolution: Lesson provenance is resolved: the cited checkpoint must exist and the cited finding identifier must appear in that checkpoint's own recorded evidence.
- Prevention:
  - `invariant` lessons._resolve_source_locator — A lesson's cited checkpoint must record the finding identifier it names.
  - `test` LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected — A locator that points at the wrong checkpoint is refused.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0004/REVIEW-REPORT.md`

### LSN-0024 — A control is finished only when its positive path has been executed, not only its refusals

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0009, finding CP9-F-001.
- Symptom: The milestone attestation refused fifteen forged variants and could accept nothing, because the attestation had to live inside the tree of the commit it named as its subject, so the status it guarded was unreachable.
- Root cause: The control was exercised only from the refusing side. Twelve rejection tests passed while the reachable state space was empty, so nothing failed when the positive path disappeared.
- Resolution: The verdict moved to the audit checkpoint, which names an already sealed subject, and the positive promotion is now executed end to end in a disposable repository by promotion_simulation.py and asserted by PositivePromotionTests.
- Prevention:
  - `test` PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed — A legitimate two-checkpoint promotion reaches a derived milestone PASS.
  - `automated-check` scripts/development-ledger/promotion_simulation.py — The positive promotion is executed and recorded as a delivery artifact.
  - `test` SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output — The artifact a simulation seals is bound by content to the tool's own output.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md`, `file:scripts/development-ledger/attestation.py`, `file:scripts/development-ledger/promotion_simulation.py`

### LSN-0025 — A generic guardrail derives repository state instead of naming today's checkpoint

- Status: `GUARDED`, severity CRITICAL, category testing, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0009, finding CP9-F-002.
- Symptom: A chain guardrail test excluded a checkpoint by literal name while the product derived the same exclusion from repository state, so anchoring the sealed predecessor turned the mandatory tests gate red.
- Root cause: The same semantic rule was implemented twice, once derived and once typed, and the typed copy encoded the repository as it looked on the day it was written.
- Resolution: The rule has one implementation, anchors.pending_anchor_exclusion, which the CLI, the validator and the suite all call, and a succession simulation proves it keeps moving.
- Prevention:
  - `invariant` anchors.pending_anchor_exclusion — The checkpoint whose anchor is still owed is derived from history.
  - `test` SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain — The exclusion follows the chain across successive checkpoints.
  - `test` IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint — The exclusion equals the newest sealed checkpoint, never a literal.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md`, `file:scripts/development-ledger/anchors.py`, `file:tests/test_development_ledger.py`

### LSN-0026 — An adversarial battery without a null-mutation control proves nothing

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0009, finding audit harness classified AUDIT_ENVIRONMENT.
- Symptom: An attack harness reported every attack as defended while the refusals came from leftover state and a broken seal chronology rather than from the mutation under test.
- Root cause: The harness never ran an unmutated case through the identical path, so a fixture that refused everything was indistinguishable from a control that worked.
- Resolution: The battery records a baselineControl, the unmutated fixture run through the same path, and validation refuses a report whose control is missing or not VALID.
- Prevention:
  - `schema` .iacode/schemas/red-team-report.schema.json — A Red Team report must carry its null-mutation control.
  - `invariant` validate_checkpoint._validate_internal_assurance — A battery whose control is missing or INVALID cannot produce a PASS.
  - `test` InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected — A report without the control is refused.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0009/AUDIT-EXECUTIONS.md`, `file:scripts/development-ledger/m0_red_team.py`, `file:.iacode/schemas/red-team-report.schema.json`

### LSN-0027 — A lesson's prose may record a residual limit but may never contradict its status

- Status: `GUARDED`, severity MEDIUM, category documentation, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0009, finding CP9-F-004.
- Symptom: A GUARDED lesson carried a note saying it was not guarded, so a reader who trusted the prose reached the opposite conclusion from the machine-readable status.
- Root cause: The note was written while the lesson was unguarded and was never revisited when an automated control was added, because nothing compared the two.
- Resolution: Memory validation refuses a GUARDED lesson whose notes assert that it is not guarded, and the note now describes the residual limit of the control instead of its status.
- Prevention:
  - `invariant` lessons.validate_lessons — A GUARDED lesson may not describe itself as unguarded.
  - `test` MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded — The contradiction is refused by the memory validator.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md`, `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/lessons.py`

### LSN-0028 — A configuration key that no code reads is a defect, not documentation

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0009, finding CP9-F-005.
- Symptom: The memory policy declared a relocatable guardrail registry path while the implementation resolved a fixed constant, so re-pointing the documented key changed nothing.
- Root cause: The policy document was never validated against a schema, so a key could be added without any consumer and without any check noticing.
- Resolution: The unread key was removed, the fixed path is documented and resolved by one function, and the policy document is validated against a closed schema that refuses an unknown key. GATE-0 generalised it: the same class recurred in the application configuration and in an operational helper, so the check now reads the declaring module against the code that must consume it rather than relying on a schema over one document.
- Prevention:
  - `schema` .iacode/schemas/memory-policy.schema.json — The memory policy schema is closed to keys no code reads.
  - `invariant` lessons.validate_memory_policy_document — The declared policy is validated like every other governing document.
  - `test` MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared — Declaring an unread setting is a validation error.
  - `test` test_every_declared_key_is_read_somewhere — The API's declared settings are compared against the application source, so a field nothing consumes fails instead of surviving as documentation.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md`, `file:.iacode/memory/POLICY.json`, `file:.iacode/schemas/memory-policy.schema.json`, `file:apps/api/tests/unit/test_configuration.py`

### LSN-0029 — A required protocol transition must never turn a mandatory gate red

- Status: `GUARDED`, severity CRITICAL, category process, recurrences 2.
- Source: SETUP-00, SETUP-00-CP-0009, finding CP9-F-002.
- Symptom: Carrying out a step the checkpoint protocol requires of every successor, anchoring its sealed predecessor, took the mandatory suite from green to red and left editing a guardrail test as the only apparent remedy.
- Root cause: The controls were written against one repository state instead of against the sequence of states the protocol itself produces.
- Resolution: ADR-0055 declares only a RESERVED Code Graph notice, with no Gate8 implementation or authority. Current real scope/additional-file refusal passes cmd-0123, original scope assertions pass cmd-0127, and all32 actual protocol/succession cases pass cmd-0126. Local executable guard restoration only; the failed immutable runtime-v1 remains FAIL. A new complete immutable invocation and every ordered internal assurance control are still required before readiness; independent M2 validation remains pending.
- Prevention:
  - `automated-check` scripts/development-ledger/successor_durability.py — The protocol's own next steps are executed and the gates re-checked.
  - `test` SuccessorDurabilityTests.test_every_state_of_the_chain_verifies — Every state of an advancing chain keeps the controls green.
  - `automated-check` scripts/development-ledger/gate_transition_simulation.py — The transition into the first delivery of the next Gate is executed before handoff.
  - `test` Gate7FutureBoundaryTests.test_code_graph_is_only_a_future_notice_and_real_scope_rejects_an_added_file — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md`, `file:scripts/development-ledger/successor_durability.py`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:tests/test_gate7_assurance.py`, `file:tests/test_gate7_knowledge.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`

### LSN-0030 — The lesson preflight presumes an implementing delivery and constrains an audit run badly

- Status: `CONFIRMED`, severity LOW, category process, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0009, finding audit observation recorded in LESSON-CANDIDATES.json.
- Symptom: Requirements derived for an implementing delivery, such as an empty blockedBy at a readiness status, cannot apply to an audit checkpoint that legitimately records blockers.
- Root cause: The preflight has one role model, so a run that audits rather than implements would have to answer requirements that do not describe it.
- Resolution: Recorded as a scoped lesson that constrains audit runs only, so an implementing Gate is not asked to answer it, until a delivery-role input is worth building.
- Prevention:
  - `documentation` docs/ENGINEERING-MEMORY.md — The preflight's role assumption is recorded rather than implied.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0009/LESSON-CANDIDATES.json`, `file:docs/ENGINEERING-MEMORY.md`

### LSN-0031 — An empty applicable set is not a missing required set, and a control must tell them apart

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0011, finding CP11-F-001.
- Symptom: The internal mirror audit required its derived set to be non-empty in order to report success, so a delivery that legitimately had no audit to correct was refused for having nothing to correct, and checkpoint validation then refused every positive terminal status.
- Root cause: The check conflated two states of a derived set. Zero items derived because nothing of this kind applies was treated as zero items derived because the delivery failed to supply them.
- Resolution: A dimension whose canonically derived applicable set is empty is NOT_APPLICABLE with a reason, an expected count of zero and the source the emptiness was derived from; a dimension whose sources name items the delivery does not satisfy stays FAIL. The applicable set is derived from the canonical sources at every call, so no delivery can declare its own set empty.
- Prevention:
  - `automated-check` scripts/development-ledger/mirror_semantics_validation.py — Every applicability state is executed through the real tool, including the negatives.
  - `test` MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes — A delivery with nothing to audit reaches a passing mirror.
  - `test` MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable — A dimension the canonical sources make applicable cannot be declared inapplicable.
  - `invariant` validate_checkpoint._validate_mirror_applicability — Checkpoint validation re-derives the applicable set instead of believing the report.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0011/REVIEW-REPORT.md`, `file:scripts/development-ledger/m0_mirror_audit.py`, `file:scripts/development-ledger/mirror_semantics_validation.py`

### LSN-0032 — A control written while one Gate was the only Gate stops being a control when the next one starts

- Status: `GUARDED`, severity HIGH, category quality, recurrences 0.
- Source: GATE-0, GATE-0-CP-0001, finding G0-F-001.
- Symptom: Four control-plane controls refused the first delivery of GATE 0 for reasons that were correct under SETUP-00 and meaningless afterwards: the expected requirement set cited one Gate's checklist by literal, the delivery-assurance scope did not cover the runtime, the TESTS denominator counted one suite, and the internal mirror audit asserted that no Gate 0 runtime existed while Gate 0's job was to create it.
- Root cause: Each control encoded the current Gate's content instead of deriving it. A literal that is true for exactly one Gate looks like a strong control while that Gate runs and becomes a blocker or a blind spot the moment the next one begins.
- Resolution: Each control now derives what it judges from a canonical source: the specification path from the Gate registry, the assurance scope from declared prefixes covering the product, the test denominator from a declared suite registry, and the scope check from a reservation registry naming the Gate that owns each path. The replacements apply to every Gate, including the one that wrote them.
- Prevention:
  - `test` test_expected_set_names_the_gate_specification — A derived requirement cites the document it was derived from.
  - `test` test_assurance_scope_covers_the_runtime_source — A gate result goes stale when the product changes, not only the tooling.
  - `test` test_declared_suites_are_discovered — The TESTS denominator includes every declared suite.
  - `policy` .iacode/policies/gate-scope.json — Scope is judged against a registry of reservations and the Gate that owns each one, never against a directory name written into a tool.
  - `automated-check` scripts/development-ledger/gate_transition_simulation.py — The transition into the next Gate is executed in a disposable repository before handoff, which is what surfaced the first of the four.
- Evidence: `file:docs/checkpoints/GATE-0-CP-0001/DECISIONS.md`, `file:.iacode/policies/gate-scope.json`, `file:tests/test_gate0_foundation.py`

### LSN-0033 — A value bound in middleware is absent in the handlers that run outside it

- Status: `GUARDED`, severity MEDIUM, category implementation, recurrences 0.
- Source: GATE-0, GATE-0-CP-0001, finding G0-F-002.
- Symptom: Error responses told the caller to quote a correlation identifier and carried none. The identifier was bound to a context variable inside the correlation middleware, and the unhandled-exception handler runs in the framework's outermost error middleware, outside the task that binding belonged to.
- Root cause: Context-local state is scoped to the execution it was set in. A handler installed above the middleware in the stack is a different execution, so the value is simply not there — and the failure is silent, because an absent identifier reads as 'not generated yet' rather than as a bug.
- Resolution: The error contract reads the identifier from the request state, which lives on the shared scope and therefore crosses that boundary, and falls back to the context variable. It also sets the response header itself, because a response produced outside the middleware never passes back through it.
- Prevention:
  - `test` test_internal_error_still_carries_a_correlation_identifier — An unhandled exception returns a body and a header carrying the identifier.
  - `test` test_a_missing_route_uses_the_error_contract — A response produced by the framework follows the same contract.
- Evidence: `file:apps/api/src/iacode_api/errors.py`, `file:apps/api/tests/unit/test_errors_and_correlation.py`

### LSN-0034 — Re-deriving what the framework already computed diverges from the framework

- Status: `GUARDED`, severity MEDIUM, category implementation, recurrences 0.
- Source: GATE-0, GATE-0-CP-0001, finding G0-F-003.
- Symptom: Every HTTP metric was labelled with the unmatched-path bucket. The middleware resolved the route template by re-matching the request against the application's top-level route list, and the framework wraps an included router in a single object, so that list does not contain the routes the routers own.
- Root cause: The middleware reimplemented routing instead of reading the result of it. A reimplementation agrees with the original until the original changes shape, and the disagreement is invisible: the endpoint kept answering and the dashboard kept rendering, with one time series for everything.
- Resolution: The template is read from the request scope after the request has been handled, where the router records the route it actually matched. Anything genuinely unmatched still collapses into one bucket, because an unmatched path is caller-controlled.
- Prevention:
  - `test` test_metrics_endpoint_exposes_request_metrics — A handled request is labelled with its route template.
  - `test` test_metrics_label_routes_by_template_not_by_url — Unmatched paths collapse into one series, so cardinality stays bounded.
  - `test` test_the_api_instruments_reach_prometheus — The series the dashboard depends on are queryable in Prometheus.
- Evidence: `file:apps/api/src/iacode_api/observability/metrics.py`, `file:apps/api/tests/unit/test_observability.py`

### LSN-0035 — Captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work

- Status: `GUARDED`, severity CRITICAL, category tooling, recurrences 5.
- Source: GATE-0, GATE-0-CP-0001, finding G0-F-004.
- Symptom: The Green Keeper aborted with UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d while reading the output of a gate that was green. After the read was repaired, the command recorder aborted with UnicodeEncodeError: 'charmap' codec can't encode character '�' while printing what it had just captured -- after an eighteen-minute verification had already passed.
- Root cause: Both ends inherit the machine's codepage. subprocess.run(..., text=True) with no encoding decodes with locale.getencoding(), and sys.stdout encodes with it as well; on Windows that is cp1252, while every tool here writes UTF-8. The failure is intermittent because it depends on which character the measured process happened to print, and it lands after the work succeeded, so it destroys a result rather than reporting one.
- Resolution: Post-quality local prevention is restored only after actual current positive/adverse controls, original historical declarations, full lint, authored read-only quality and quiescent checkpoint validation. Original failures, counters and severity remain. Fresh source-epoch whole quality/functional/internal assurance and independent M2 validation remain mandatory.
- Prevention:
  - `test` test_no_capture_relies_on_the_platform_codepage — Every subprocess capture in the tree is parsed and must state its encoding.
  - `test` test_every_tool_that_re_emits_captured_output_configures_its_own_stream — Every entry point that captures also configures the stream it writes to.
  - `test` test_the_rule_detects_a_capture_that_would_fail — The rule is exercised against a call it must reject.
  - `test` test_cold_diagnostic_entrypoints_use_utf8_before_any_work — Execute the actual three entry blocks and shared stream bootstrap in cold cp1252 children with harmless fixture work; Unicode stdout/stderr must be UTF-8, and removing the bootstrap must raise UnicodeEncodeError before effects. Original capture/cleanup main bodies are never replayed.
  - `test` M2CurrentStreamBootstrapTests.test_actual_capture_entry_blocks_reject_cold_bootstrap_removal — Executed actual current positive/adverse control; no production fake or independent verdict.
  - `test` PublicationCallerTests.test_unchanged_whole_tree_codepage_guard_covers_current_m2_sources — Actual current boundary/null/refusal control; not independent acceptance.
  - `test` PublicationProofDecisionTests.test_actual_git_capture_states_decoder_and_preserves_unicode — Actual current boundary/null/refusal control; not independent acceptance.
- Evidence: `file:tests/test_gate0_foundation.py`, `file:scripts/development-ledger/ledger_common.py`, `file:scripts/iacode/compose.py`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/FULL-PRODUCER-d2b2b71d1263-INTERNAL-FULL-VERIFY.json`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:tests/test_gate6_experience.py`, `file:docs/checkpoints/GATE-7-CP-0003/INTERNAL-ENVIRONMENT-REWORK.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/tests/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0011.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/native-observation/run-0003.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge-physical-bounds/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge/run-0005.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/owned-cleanup/run-0004.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/operator-cleanup/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/current-streams/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/inherited-streams/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/published-green-keeper/run-0003/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/published-green-keeper/run-0003/stdout.log`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/inherited-streams/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/lint/run-0013.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/helper-quality/run-0029/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/all-m2/run-0007.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/inherited-streams/run-0003.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/history-transport/run-0006.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/inherited-git/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/review-reconstruction/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/checkpointValidation/run-0009.json`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0008/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0008/stdout.log`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0006/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0006/stdout.log`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0007/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0007/stdout.log`

### LSN-0036 — A gate that runs inside an image measures the image, not the source

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 1.
- Source: GATE-1, GATE-1-CP-0001, finding G1-F-001.
- Symptom: A red test was found at HEAD during GATE 1: test_a_documented_placeholder_is_not_redacted failed because the redactor's placeholder pattern read change[-_]?me\b while the repository's documented placeholder is change-me-before-starting. The test had existed and the apiTests gate had reported PASS throughout GATE 0.
- Root cause: The apiTests gate executes pytest inside the API image, and nothing rebuilt that image before measuring. The gate therefore reported on whatever source happened to be baked into the last build. A gate in that shape does not fail when the code is wrong; it reports on code nobody is running, so a defect can be introduced, committed and sealed behind a green gate.
- Resolution: compose.build_service(service) was added and every gate whose command executes inside an image calls it before measuring. Building costs a cached layer check when nothing changed. The redaction defect it had been hiding was fixed separately (LSN-0038).
- Prevention:
  - `test` test_every_image_gate_builds_before_it_measures — Every gate command that runs inside an image builds that image first.
  - `test` test_the_image_gate_rule_detects_a_gate_that_would_skip_the_build — The rule is exercised against a gate module it must reject.
  - `test` test_durability_scenario_rebuilds_its_rehearsal_worker — The shared durability/cancellation/deadline harness rebuilds its worker image before starting the rehearsal container.
- Evidence: `file:scripts/iacode/compose.py`, `file:scripts/iacode/gates/api_tests.py`, `file:scripts/iacode/gates/gateway_tests.py`, `file:tests/test_gate1_model_gateway.py`, `file:scripts/iacode/scenarios/agent_runtime_durability.py`, `file:tests/test_gate4_quality_engine.py`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`

### LSN-0037 — A shared control that names an identifier the repository derives stops being a control when that identifier moves

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 4.
- Source: GATE-1, GATE-1-CP-0001, finding G1-F-002.
- Symptom: Twice in one Gate. First: test_no_future_gate_capability_is_implemented failed at the start of GATE 1 with 'services/model-gateway is reserved for GATE 1 but carries ...', because the control called scope_violations(root, 'GATE-0'). Then: the fresh-installation scenario failed with alembic_version='0002_model_gateway', because it compared the recorded revision with the literal '0001_foundation'.
- Root cause: A control that names today's state is a control with an expiry date nobody recorded. The identifier's kind does not matter -- a Gate, a checkpoint, a migration revision -- and the first formulation of this lesson said 'a Gate', so the scan it produced looked for Gate literals and saw nothing else.
- Resolution: ledger_common.delivered_gate reads the Gate from the checkpoint and policies.reservations_in_force expresses which reservations still constrain it; apps/api/migrations/head.py derives the head revision from the migration graph and both its consumers import it. The scan now refuses a Gate literal and a revision compared for equality, and distinguishes naming a revision as an answer from naming one as a starting point, because an upgrade-path test needs the second.
- Prevention:
  - `test` test_no_shared_control_is_bound_to_a_gate_literal — No caller passes a constant Gate identifier to a scope or reservation control.
  - `test` test_the_gate_literal_rule_detects_a_bound_control — The rule is exercised against a call it must reject.
  - `test` test_no_control_names_a_migration_revision_literally — No control compares an observed value against a hard-coded migration revision.
  - `test` test_the_revision_rule_detects_a_named_head — The rule is exercised against an equality it must reject and an upgrade-path argument it must accept.
  - `test` test_the_head_revision_has_one_derivation — The head is derived once, in the migration directory, and neither consumer walks the graph itself.
  - `test` test_cli_reservation_membership_follows_every_policy_lifecycle_position — Execute the strengthened current causal boundary without weakening inherited controls.
- Evidence: `file:scripts/development-ledger/policies.py`, `file:scripts/development-ledger/ledger_common.py`, `file:scripts/development-ledger/gate0_red_team.py`, `file:tests/test_gate0_foundation.py`, `file:apps/api/migrations/head.py`, `file:scripts/iacode/scenarios/fresh_install.py`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`

### LSN-0038 — Two representations of one concept in one module disagree, and the safer one loses

- Status: `GUARDED`, severity MEDIUM, category implementation, recurrences 2.
- Source: GATE-1, GATE-1-CP-0001, finding G1-F-003.
- Symptom: redact_text redacted the committed example environment file's placeholders while redact_value left them alone. Reading a redacted example cannot answer the one question it is read for: whether a real value has leaked into it.
- Root cause: The module defined what a placeholder looks like twice: once anchored, for values under a sensitive key, and once as a negative lookahead inside the text pattern. The two definitions were written at different times and disagreed about the repository's own documented placeholder. A comment noting that they must agree is not a mechanism that makes them agree.
- Resolution: The lookahead was removed. The text redactor now tests the matched value against the single anchored definition and leaves a placeholder in place, so there is one authoritative statement of what a placeholder is.
- Prevention:
  - `test` test_a_documented_placeholder_is_not_redacted — The placeholder the repository documents survives both redactors.
  - `test` test_both_redactors_agree_on_every_value_the_example_file_carries — Every value in the committed example file is classified identically by both redaction paths. Its first run found a second instance of the same failure: an operational limit named ...MAX_OUTPUT_TOKENS was redacted by one path only.
  - `test` test_no_module_writes_its_own_credential_name_rule — No module outside the redaction package decides for itself whether a name carries a credential.
  - `test` test_the_two_questions_stay_different — Redaction and committability are different questions, and the difference is asserted rather than assumed.
- Evidence: `file:packages/common/src/iacode_common/redaction.py`, `file:apps/api/tests/unit/test_common_primitives.py`, `file:tests/test_gate1_model_gateway.py`, `file:infra/tests/test_compose_definition.py`, `file:infra/tests/test_backup_tooling.py`

### LSN-0039 — A test that writes to the operational database leaves production data behind

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-1, GATE-1-CP-0001, finding G1-F-004.
- Symptom: The first live catalog synchronisation returned 36 models from the provider and the catalog endpoint reported 56. Twenty rows belonged to providers named devworld-<hex> carrying models called model-one, keep and drop: fixtures from the integration suite, sitting in the operator-visible catalog and rendered by the web page.
- Root cause: The store tests run against the stack's real database on purpose — that is what makes them prove the stores work against the real schema — and they created rows without removing them. Each run added another provider, its models and a model_calls row. Nothing was wrong with the product; the tests were writing production data.
- Resolution: An async scope context manager gives each test a unique provider slug and unique request identifiers and removes every row it created in a finally block, in foreign-key order. The residue already in the database was purged. A standing invariant now asserts that the catalog holds no provider the policy does not declare, so residue is detected rather than trusted not to appear.
- Prevention:
  - `test` test_the_operational_catalog_holds_only_providers_the_policy_declares — Every provider row traces to .iacode/policies/providers.json.
- Evidence: `file:apps/api/tests/integration/test_gateway_persistence.py`, `file:.iacode/policies/providers.json`

### LSN-0040 — A control that judges sealed history only runs once a successor anchors it

- Status: `GUARDED`, severity CRITICAL, category checkpoint, recurrences 3.
- Source: GATE-1, GATE-1-CP-0001, finding G1-F-007.
- Symptom: MIR-016 failed with GATE-0-CP-0001: CHECKPOINT_INVALID. Six of that sealed checkpoint's recorded commands name var/verify-report.json as an input; var/ is ignored by Git, so no checkout of the tag carries it, and the validator required every declared input to exist.
- Root cause: Two causes in one failure. The recorder declared a generated, ignored artifact as a command input, which makes the record unreplayable from a checkout. And the defect was invisible for a whole Gate because a checkpoint cannot anchor its own tag: GATE-0-CP-0001 entered the anchor chain only when its successor built the chain, so the first execution of the control over it happened one Gate after the content it judges was sealed.
- Resolution: The command-input policy is now versioned. Schema 3.3.0 requires every declared input to be eligible for Git transport, using one shared classifier that rejects Git metadata, ignored output, absolute paths and repository escapes. Automatic discovery excludes local-only paths, explicit inputs are refused before execution, and checkpoint validation independently rejects manually constructed records. Schemas through 3.2.0 retain digest-bound compatibility for sealed generated inputs, so current tooling can audit immutable predecessors without treating their local archives as new evidence.
- Prevention:
  - `test` test_every_sealed_checkpoint_validates_from_its_own_tag — Every anchored checkpoint validates from a detached checkout of its tag, asserted by the suite rather than only by the mirror audit.
  - `test` test_the_recorder_never_declares_an_ignored_path_as_an_input — A generated artifact is never recorded as a command input.
  - `test` test_an_input_the_repository_carries_is_still_required_to_exist — The rule still refuses a reference that resolves to nothing.
  - `validator` scripts/development-ledger/validate_checkpoint.py — Every commit a checkpoint's evidence names must be reachable from a published reference (a branch, a tag or a remote-tracking branch); an object that exists only in the local store is refused, for every schema version (ADR-0028).
  - `test` test_the_validator_refuses_a_record_naming_an_unpublished_commit — A record naming a commit no published reference reaches is refused, as a local object in the repository that holds it and as an absent object in a published clone; the same record passes once a published reference reaches the commit.
  - `test` test_every_preserved_reference_is_what_makes_its_checkpoint_valid — On the real sealed history, removing each refs/tags/iacode-preserved/ reference makes the checkpoint that names its commit invalid in the repository and in a published clone.
  - `test` test_a_published_clone_carries_only_what_a_published_reference_reaches — A published clone does not carry an unreachable object that a copy of the object store does.
  - `test` test_every_clone_in_the_tooling_and_the_suite_is_a_published_clone — A syntax-tree scan refuses any git clone in the tooling or the suite that is not a transport clone.
  - `test` test_a_preserved_reference_missing_from_the_remote_fails_unnamed — remote_sync.py refuses a local preserved or checkpoint tag that is not on the remote.
  - `test` test_a_preserved_commit_maps_to_the_checkpoint_whose_evidence_names_it — Every preserved commit is associated only with a checkpoint whose canonical command evidence fields name it; a SHA appearing merely in an argument cannot capture the guardrail's subject.
  - `test` test_git_metadata_is_local_even_though_git_check_ignore_does_not_classify_it — Git metadata is classified as local-only even though git check-ignore does not report it.
  - `test` test_schema_3_3_refuses_a_digest_bound_git_metadata_input — The strict schema refuses a content-bound .git input.
  - `test` test_schema_3_3_refuses_an_ignored_input_even_when_it_exists — Local presence cannot make an ignored artifact transportable.
  - `test` test_the_recorder_excludes_git_metadata_and_refuses_it_when_explicit — Auto-detection omits Git metadata and explicit declaration is rejected.
  - `test` test_a_nontransport_input_refusal_is_recomputed_from_its_precondition — A recorded refusal is accepted only while the shared classifier reproduces it.
  - `test` test_a_fabricated_nontransport_input_refusal_is_rejected — A fabricated refusal over a repository-carried input is rejected.
  - `validator` scripts/development-ledger/ledger_common.py — command_input_transport_error is the shared transport classifier.
- Evidence: `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/record_command.py`, `file:tests/test_gate1_model_gateway.py`, `file:docs/checkpoints/GATE-3-CP-0002/REVIEW-REPORT.md`, `file:docs/adr/ADR-0028-sealed-evidence-is-judged-from-the-published-history.md`, `file:scripts/development-ledger/ledger_common.py`, `file:tests/test_gate3_sandbox.py`, `file:docs/checkpoints/GATE-3-CP-0005/PRESERVED-REFERENCE-PROBE.json`, `file:DIVERGENCE.md`, `file:docs/adr/ADR-0034-command-inputs-must-cross-git-transport.md`, `file:docs/checkpoints/GATE-4-CP-0007/CP0006-REMOTE-TRANSPORT-BASELINE.json`, `file:tests/test_development_ledger.py`

### LSN-0041 — An editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-2, GATE-2-CP-0001, finding G2-F-001.
- Symptom: A frontend control scan compiled, ran and reported success while matching zero elements. Its regular expression contained a literal backspace where a word-boundary escape belonged, so it could never match anything.
- Root cause: The test was edited through a path that consumed the backslash escape, and the resulting control character survived into the file. Nothing downstream could tell an empty corpus from a clean one, so the control reported the delivery as clean.
- Resolution: Two controls. A repository-wide scan refuses a stray control character in any source file, which prevents the class rather than the instance; and every scan in this Gate asserts that it found something to judge before judging it.
- Prevention:
  - `test` test_no_source_file_carries_a_stray_control_character — No source file under tests, scripts, packages, services or the API carries a control character other than tab, newline or carriage return.
  - `test` test_the_scan_detects_one — The null control: the same scan fires on a mangled fixture and stays quiet on an intact one.
  - `test` test_the_page_offers_nothing_that_would_execute_a_tool — The scan asserts that it found controls to inspect before judging them.
  - `test` test_the_boundary_has_something_to_scan — The boundary scan asserts a non-empty corpus.
- Evidence: `file:tests/test_gate2_agent_runtime.py`, `file:.iacode/memory/retrospectives/GATE-2-CP-0001.md`

### LSN-0042 — A naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone

- Status: `GUARDED`, severity CRITICAL, category implementation, recurrences 1.
- Source: GATE-2, GATE-2-CP-0001, finding G2-F-002.
- Symptom: Dropping a check constraint by its full name produced ALTER TABLE task_runs DROP CONSTRAINT ck_task_runs_ck_task_runs_status_is_known, and creating a unique constraint by its full name produced one the downgrade could not find, which failed three migration suites at once.
- Root cause: The declarative naming convention is applied only when the template for that constraint kind contains the constraint-name token. The CHECK template does; the UNIQUE template does not. So a check constraint is named by its bare name and a unique constraint keeps exactly what it is given, and using one rule for both is wrong in one direction or the other.
- Resolution: The migration creates and drops a check constraint by its bare name and a unique constraint by exactly the name the model declares, and states the asymmetry in a comment where the code is. The reversibility test applies and reverses the migration against a disposable database, so a mismatch is a failing test rather than a failed downgrade in an incident.
- Prevention:
  - `test` test_the_agent_runtime_migration_is_reversible — The migration is applied and reversed against a disposable database, which is what a name mismatch breaks.
  - `test` test_the_declared_model_matches_the_migrated_schema — Autogenerate against a freshly migrated database finds nothing left to do, which a name mismatch would report.
  - `test` test_a_check_constraint_is_created_and_dropped_by_its_bare_name — The migration uses the bare name for a check constraint.
  - `test` test_a_unique_constraint_keeps_exactly_the_name_it_was_given — The migration uses the declared name for a unique constraint, on both sides.
  - `test` test_experience_constraint_names_respect_their_actual_kind — Current strengthened causal boundary; every original control remains.
- Evidence: `file:apps/api/migrations/versions/0003_agent_runtime.py`, `file:apps/api/tests/integration/test_migrations.py`, `file:packages/persistence/src/iacode_persistence/base.py`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/PRE-LIVE-PROGRESS.json`, `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0004.json`

### LSN-0043 — A log line is not evidence that another process is ready

- Status: `GUARDED`, severity MEDIUM, category testing, recurrences 0.
- Source: GATE-2, GATE-2-CP-0001, finding G2-F-003.
- Symptom: A scenario waited for a worker's start-up line, started a run, and then waited out its whole two-minute timeout on a run that had never been scheduled.
- Root cause: The worker prints that it started before it begins polling, so the line reports an intention rather than a state. The observable fact is the one the server holds: whether the task queue has a poller.
- Resolution: The scenario asks Temporal's DescribeTaskQueue through the harness, which is the same question the worker's own container healthcheck asks, and waits on the answer rather than on the narration.
- Prevention:
  - `test` test_readiness_is_asked_of_temporal — The scenario's readiness wait asks the server for the poller count.
  - `test` test_readiness_is_not_read_from_a_log_line — The readiness wait does not read container logs.
  - `test` test_the_harness_asks_the_server_for_the_answer — The harness implements the question against the workflow service rather than against a file.
- Evidence: `file:scripts/iacode/scenarios/agent_runtime_durability.py`, `file:services/orchestrator/rehearsal/durability.py`, `file:services/orchestrator/src/iacode_orchestrator/healthcheck.py`

### LSN-0044 — A boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module

- Status: `GUARDED`, severity HIGH, category quality, recurrences 0.
- Source: GATE-2, GATE-2-CP-0001, finding G2-F-004.
- Symptom: Three boundary scans reported escapes on their first run, every one a false positive: a docstring that explained why the runtime names no provider, a deny-list that refuses an authorisation header, and a call to str.replace read as os.replace.
- Root cause: Each scan matched text. A scan that reads prose forces the explanation out of the file, a scan that reads a deny-list cannot tell a defence from the thing it defends against, and a scan that matches the last segment of a call cannot tell two unrelated functions apart.
- Resolution: Every boundary scan reads the abstract syntax tree: imports by module, calls by their full dotted name, and identifiers with docstrings excluded. Each one carries a null control that runs the identical scan over a module which does the forbidden thing and requires it to fire.
- Prevention:
  - `test` test_the_null_control_detects_a_mutation — The execution scans fire on a module that imports subprocess, writes a file or calls eval, and stay quiet on ordinary code.
  - `test` test_the_provider_scan_would_catch_one — The provider scan fires on a module that names a provider in code and not on one that discusses it in a docstring.
  - `test` test_the_credential_scan_would_catch_one — Each of the four ways a credential could enter is detected on a mutated module.
  - `test` test_the_scan_detects_a_module_that_does_it — The repository-wide execution scan fires on a mutated module and stays quiet on a clean one.
  - `test` test_the_determinism_scan_detects_a_module_that_breaks_it — The workflow determinism scan fires on a module that reads a clock and a random value.
- Evidence: `file:services/agent-runtime/tests/test_boundary.py`, `file:tests/test_gate2_agent_runtime.py`, `file:scripts/development-ledger/gate2_runtime_attacks.py`

### LSN-0045 — A counted test suite must declare its cases statically, because the denominator is read from the source

- Status: `GUARDED`, severity MEDIUM, category testing, recurrences 1.
- Source: GATE-2, GATE-2-CP-0001, finding G2-F-007.
- Symptom: Ninety-five cases of the ledger suite errored at once, all of them on the same message: a test in a counted suite is parametrised and the TESTS denominator cannot reproduce a runtime expansion.
- Root cause: The denominator is derived by reading the source, so a case produced at run time by a parametrisation cannot be counted. The counter already refuses one, but it refuses from inside the counting step, several layers below the file that caused it, so the failure arrives as a wall of unrelated-looking errors rather than as a statement about one function.
- Resolution: Every case in a counted pytest suite is written as a loop over a module-level tuple, which counts as one case and covers the same inputs. A repository test asks the same question of the same files and fails fast, naming the file and the function.
- Prevention:
  - `test` test_no_counted_pytest_case_expands_at_run_time — No test function in a counted pytest suite carries a parametrisation.
  - `test` test_the_scan_detects_an_expansion — The null control: the same scan fires on a parametrised module and stays quiet on a plain one.
- Evidence: `file:tests/test_gate2_agent_runtime.py`, `file:scripts/development-ledger/derive_counts.py`, `file:.iacode/policies/test-suites.json`, `file:docs/checkpoints/GATE-4-CP-0001/VERIFY-FAIL-CMD-0105.json`, `file:services/evaluator/tests/test_core.py`, `file:services/sandbox/tests/test_quality_images.py`

### LSN-0046 — A timeout that cancels the task it runs in leaves nothing able to record what happened

- Status: `GUARDED`, severity CRITICAL, category implementation, recurrences 0.
- Source: GATE-2, GATE-2-CP-0001, finding G2-F-008.
- Symptom: A run with a ten-second deadline was still RUNNING two minutes later. Temporal showed the workflow had in fact ended at 10.07 seconds, failed with 'Activity cancelled', having written nothing: no state change, no event, no reason. The row stayed RUNNING for ever.
- Root cause: Two faults in the same three lines. The deadline was `asyncio.wait_for`, which from Python 3.11 implements its timeout by cancelling the task that awaits it — here the workflow's own — so the next activity it scheduled was cancelled before it started. And the wait on the cancelled work expected `CancelledError`, while Temporal surfaces a cancelled activity as `ActivityError`, so the handler never ran. A deadline enforced against the process rather than against the run looks identical to no deadline at all from the outside, because the only difference is a record nobody wrote.
- Resolution: The engine runs as an explicit child task raced against a timer, so cancellation stays in the child and the workflow's own task is never left cancelling. The wait on that child accepts every way a cancelled activity surfaces. The deadline path then writes the state, the event and the reason from a task that is still able to write.
- Prevention:
  - `automated-check` scripts/iacode/scenarios/agent_runtime_deadline.py — A real run against a real workflow must reach FAILED with RUN_DEADLINE_EXCEEDED and a RUN_FAILED event; this is the control that found the defect.
  - `test` test_the_engine_is_not_wrapped_in_wait_for — The deadline may not be a timeout that cancels the workflow's own task.
  - `test` test_the_wait_accepts_every_way_a_cancelled_activity_surfaces — The handler expects ActivityError as well as CancelledError.
  - `test` test_the_deadline_path_writes_the_failure_down — The deadline path sets the state, records the event and names the reason.
  - `test` test_the_scenario_asserts_the_run_ended_and_said_so — The scenario asserts the record, not only the ending.
- Evidence: `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:scripts/iacode/scenarios/agent_runtime_deadline.py`, `file:tests/test_gate2_agent_runtime.py`

### LSN-0047 — A refusal that misnames the defect spends the only repair on the wrong correction

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-2, GATE-2-CP-0002, finding G2-F-009.
- Symptom: The first live planner-reviewer run failed INVALID_AGENT_OUTPUT: the planner answered twice and was refused twice with 'a FINAL envelope must carry non-empty content'. One diagnostic call through the gateway showed the answer did carry content - a JSON array of two plan steps.
- Root cause: The parser tested 'is a non-empty string' and reported every failure of that test as missing content, so a present value of the wrong type was described as an absent one. The runtime's one repair quotes the refusal back to the model, which then corrected a defect it did not have and returned the same array. Underneath, the runtime contract never said that content is a string, and a planner asked for one step per line reads that as a list.
- Resolution: A present content of the wrong type is refused with its own reason, content-not-a-string, in a sentence that names the JSON type found and says that a multi-line answer is still one string. The runtime instructions state, once and for every agent, that content is one JSON string and never an array or an object. The parser accepts nothing it refused before.
- Prevention:
  - `test` test_content_of_the_wrong_type_is_refused_by_its_real_defect — An array, an object, a number and a boolean are each refused as content-not-a-string, the sentence names the type and never says missing, and absent or blank content keeps missing-content.
  - `test` test_the_runtime_instructions_state_that_content_is_one_string — The contract every agent receives names the type of content.
  - `automated-check` scripts/iacode/agent_runtime_smoke.py — The live planner-reviewer run, the control that found the defect: team.succeeded fails when a stage is refused twice.
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `file:services/agent-runtime/src/iacode_agent_runtime/context.py`, `file:services/agent-runtime/tests/test_protocol.py`, `file:services/agent-runtime/tests/test_context.py`

### LSN-0048 — A state and the event that explains it, written in two commits, are written event first

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-2, GATE-2-CP-0002, finding G2-F-010.
- Symptom: A live single-agent run read SUCCEEDED while its event log held six events and no RUN_COMPLETED. The run before it and the run after it had all seven: the defect showed once in three runs, only to a reader that waited for a terminal state and then read the log.
- Root cause: The engine committed the terminal state and then, in a second activity, the terminal event. Anything reading between the two saw a finished run whose log had not finished - the live smoke, and an SSE stream opened on a finished run, which ends at once because the state is terminal and so never delivers the terminal event. The workflow's deadline and unrecoverable paths used the same order, and the API's workflow-could-not-start path wrote FAILED with no terminal event at all.
- Resolution: Every terminal path writes the terminal event first and the terminal state second: the engine's SUCCEEDED, FAILED and CANCELLED, the workflow's deadline and unrecoverable paths, and the API path that fails a run whose workflow never started, which now records RUN_FAILED. A reader that sees a terminal state therefore always finds the log closed; the reverse window, a closed log over a row one activity behind, is the half a reader can act on safely.
- Prevention:
  - `test` test_a_terminal_state_is_never_visible_before_its_terminal_event — For a succeeded, a failed and a cancelled run, the log already holds the terminal event at the moment the terminal state is written.
  - `test` test_the_workflow_writes_the_terminal_event_before_the_terminal_state — In the workflow's deadline and unrecoverable paths every record_event precedes every set_state.
  - `test` test_a_workflow_that_cannot_start_fails_the_run_rather_than_leaving_it_created — The API records RUN_FAILED before it writes FAILED when the workflow cannot start.
  - `automated-check` scripts/iacode/agent_runtime_smoke.py — The live check that found it: single.events_persisted requires RUN_COMPLETED once the run reads SUCCEEDED.
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/engine.py`, `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:apps/api/src/iacode_api/routes/agent_runs.py`, `file:services/agent-runtime/tests/test_engine.py`, `file:tests/test_gate2_agent_runtime.py`, `file:apps/api/tests/unit/test_agent_runtime_api.py`

### LSN-0049 — A metric read the instant after the call that moved it is read before the scrape that carries it

- Status: `GUARDED`, severity HIGH, category testing, recurrences 2.
- Source: GATE-2, GATE-2-CP-0002, finding G2-F-012.
- Symptom: The live gateway smoke failed one check of twenty on a call that had succeeded: observability.scraped found no gateway request series. The stack had been rebuilt seconds before, so the API's counter had restarted and Prometheus had not scraped it since the smoke's own requests.
- Root cause: The check asked Prometheus once, immediately after the inference, while Prometheus scrapes the API every fifteen seconds. Whether the counter had been scraped yet was a matter of timing, so the check passed on a stack that had been running for a while and failed on a freshly started one - the result described the clock, not the gateway.
- Resolution: Every Prometheus target observation now uses one policy-derived helper bounded by three versioned scrape intervals and polling only Prometheus; neither the action nor the stack is retried.
- Prevention:
  - `test` test_the_observability_check_waits_for_a_scrape_and_asks_only_prometheus — A scrape that arrives after the call is waited for, one that never arrives fails within the bound, and every read goes to Prometheus.
  - `test` test_live_smoke_is_bounded_and_minimal — The live check still makes exactly one inference and one stream.
  - `test` test_every_script_that_reads_prometheus_waits_for_a_scrape — Every script that reads Prometheus's API waits for a scrape within a bound; the control is the class, read from the syntax tree.
  - `test` test_the_scan_fires_on_a_read_that_does_not_wait — The null control of that scan.
  - `test` test_the_foundation_smoke_waits_for_both_targets_and_asks_only_prometheus — The Foundation smoke waits for both targets and asks only Prometheus.
  - `test` test_prometheus_observation_waits_on_the_versioned_scrape_cycle — The infrastructure and smoke paths share the versioned scrape-cycle budget and do not repeat the observed action.
- Evidence: `file:scripts/iacode/gateway_smoke.py`, `file:tests/test_gate1_model_gateway.py`, `file:infra/prometheus/prometheus.yml`, `file:scripts/iacode/smoke.py`, `file:tests/test_gate2_agent_runtime.py`, `file:scripts/iacode/observability.py`, `file:infra/tests/test_running_stack.py`, `file:tests/test_gate4_quality_engine.py`

### LSN-0050 — A checkpoint sealed without naming its own tag cannot be validated from that tag

- Status: `GUARDED`, severity CRITICAL, category checkpoint, recurrences 1.
- Source: GATE-2, GATE-2-CP-0002, finding G2-F-013.
- Symptom: Once GATE-2-CP-0002 anchored its predecessor, test_every_sealed_checkpoint_validates_from_its_own_tag failed for GATE-2-CP-0001: 'detached HEAD validation requires STATE.json currentCommit to name the checkpoint tag'. The checkpoint had been sealed at BLOCKED with currentCommit HEAD and had never been valid from its own tag.
- Root cause: Three rules disagreed. The protocol lets a work-in-progress status keep the symbolic HEAD; the seal tool sealed whatever state it was given; and validation from a tag required the state to spell that tag. A checkpoint sealed at BLOCKED satisfied the first two and could never satisfy the third, and nothing looked until a successor anchored it.
- Resolution: With a detached HEAD, a symbolic HEAD is bound to the checkpoint's own canonical tag derived from its identity - the same binding a named tag gives, and still refused anywhere else. The seal tool refuses a state that does not name its own tag, so no further checkpoint is sealed that way. ADR-0023.
- Prevention:
  - `test` test_sealing_refuses_a_state_that_does_not_name_its_own_tag — The seal is refused, and no tag is created, when currentCommit is not the checkpoint's own canonical tag.
  - `test` test_a_symbolic_head_validates_from_its_own_canonical_tag — A checkpoint that kept the symbolic HEAD validates from its own tag.
  - `test` test_a_symbolic_head_away_from_its_canonical_tag_is_still_refused — The same state checked out anywhere but at its tag is refused.
  - `test` test_every_sealed_checkpoint_validates_from_its_own_tag — Every anchored checkpoint is validated from its own tag.
- Evidence: `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/seal_checkpoint.py`, `file:docs/adr/ADR-0023-sealed-checkpoint-binds-its-own-tag.md`, `file:tests/test_development_ledger.py`

### LSN-0051 — A payload one service bounds for another must be bounded as the receiver measures it

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-3, GATE-3-CP-0001, finding G3-F-001.
- Symptom: The sandbox bounded a tool's raw output to 128 KiB, and the agent runtime refuses a tool result above 256 KiB measured as canonical JSON. A file of control characters inside the read limit renders at 768 KiB, so the runtime would have failed the run that read it.
- Root cause: Two limits on one payload lived in two services and measured two different things: raw bytes on the producer, the escaped JSON rendering on the consumer. Neither service's suite could see the other's measure.
- Resolution: The sandbox shortens what it hands an agent to SANDBOX_AGENT_RESULT_MAX_BYTES, measured exactly as the runtime measures, explicitly and keeping every artifact reference; a repository test reads both limits from their sources and requires the consumer's to be the larger.
- Prevention:
  - `test` test_the_runtime_accepts_every_result_the_sandbox_hands_over — Both limits are read from their sources; the receiver's is at least the sender's.
  - `test` test_an_escaped_output_is_shortened_to_the_bound_and_says_so — An output that renders three times over the bound is shortened to it, explicitly.
  - `test` test_an_output_that_fits_is_handed_over_unchanged — The null control: an ordinary output passes the same path unchanged.
- Evidence: `file:packages/contracts/src/iacode_contracts/sandbox.py`, `file:services/sandbox/src/iacode_sandbox/contracts.py`, `file:docs/checkpoints/GATE-3-CP-0001/DECISIONS.md`

### LSN-0052 — Two processes that meet on a queue must name what crosses it once, and a real run must exercise both

- Status: `GUARDED`, severity HIGH, category architecture, recurrences 0.
- Source: GATE-3, GATE-3-CP-0001, finding G3-F-003.
- Symptom: The first real coding run never finished: its workflow task failed with KeyError 'agentResult'. The sandbox's activity answered with the execution record alone, and the workflow read the tool result under a key the answer did not carry.
- Root cause: The producer and the consumer of one activity result spelled its shape separately, in two processes, and each side's suite drove the other side as a double, so both suites were green over an incompatible pair.
- Resolution: The keys are named once in iacode_contracts.sandbox and used on both sides; the sandbox suite runs the activity as Temporal runs it; a repository scan refuses a literal spelling of either key on either side; and the coding scenario exercises the real pair.
- Prevention:
  - `test` test_both_sides_name_the_result_by_the_shared_key — The workflow and the activity both use the shared names, and neither spells them.
  - `test` test_the_key_scan_detects_a_literal — The null control: a workflow that spells the key itself is detected.
  - `test` test_the_activity_answers_the_agent_result_and_the_execution — The activity, run by Temporal's test environment, answers under the shared keys.
- Evidence: `file:packages/contracts/src/iacode_contracts/sandbox.py`, `file:services/sandbox/src/iacode_sandbox/worker.py`, `file:services/orchestrator/src/iacode_orchestrator/workflows/agent_run.py`, `file:scripts/iacode/scenarios/sandbox_coding_e2e.py`

### LSN-0053 — A process sweep that reads what a forking process holds waits on the processes it has to kill

- Status: `GUARDED`, severity HIGH, category security, recurrences 1.
- Source: GATE-3, GATE-3-CP-0001, finding G3-F-004.
- Symptom: A fork bomb that detached from its command wedged a sandbox: the sweep after the command killed a handful of processes in fifteen seconds, the survivors refilled the process table, and the next command could not be started.
- Root cause: The sweep read every process's command line, which takes that process's memory lock, held by a process in the middle of a fork; and it killed without stopping first, so every slot it freed was refilled before its next round.
- Resolution: The sweep lists processes and reads only their state, stops every one until no new process appears, kills them, and remains inside its bounded loop until /proc proves the init has reaped the resulting zombies.
- Prevention:
  - `test` test_a_fork_bomb_that_detaches_leaves_a_sandbox_that_still_answers — A detached bomb is swept and the sandbox answers the next command with an empty process table.
  - `test` test_a_fork_bomb_is_contained_by_the_process_limit — A bomb that stays attached is contained by the limit and ended at its timeout.
  - `test` test_a_timeout_kills_the_whole_process_tree — The same sweep ends a command's escaped children.
  - `test` test_the_sweep_waits_for_zombies_to_be_reaped_before_returning — The deterministic sweep does not return while a zombie still occupies the PID cgroup.
- Evidence: `file:services/sandbox/src/iacode_sandbox/helper.py`, `file:services/sandbox/tests/test_sandbox_helper.py`, `file:scripts/development-ledger/gate3_sandbox_attacks.py`, `file:docs/checkpoints/GATE-3-CP-0001/DECISIONS.md`

### LSN-0054 — A pre-push check narrower than the change's reach lets a red gate reach the public remote

- Status: `CONFIRMED`, severity MEDIUM, category git, recurrences 2.
- Source: GATE-3, GATE-3-CP-0001, finding G3-F-002.
- Symptom: Three pushed commits left a mandatory gate red: the first broke the repository-wide decoding scan, two later ones the lint gate. Each ran the suites of what it changed, not the repository-wide gates the change could reach.
- Root cause: The pre-push check was chosen by the commit's subject rather than by its reach: a new script is reached by the scans over every script, and any source file by the lint gate.
- Resolution: Current trusted progress publisher requires latest successful canonical lint bound to current source and pre-publication HEAD, original scanned stream bytes and an actual command/input binding before publication effects. Real current lint/new publication and fresh whole assurance were still due at this local-control epoch; checkpoint evidence owns their eventual outcome. Broad manual Git actions remain procedural, so status stays CONFIRMED.
- Prevention:
  - `documentation` docs/DEVELOPMENT-CONTRACT.md — Before each push: status, the staged diff, a secret scan of the staged content and the tests the change can reach.
  - `test` PublicationCallerTests.test_actual_publisher_checks_current_lint_before_publication_effects — Actual trusted publisher caller and modeled receipt/input/byte decisions; does not report real repository lint or execute a push.
  - `test` PublicationCallerTests.test_archived_actual_publisher_without_precondition_is_rejected — Actual trusted publisher caller and modeled receipt/input/byte decisions; does not report real repository lint or execute a push.
  - `test` PublicationProofDecisionTests.test_modeled_valid_proof_is_accepted_without_git_state_effects — Actual trusted publisher caller and modeled receipt/input/byte decisions; does not report real repository lint or execute a push.
  - `test` PublicationProofDecisionTests.test_missing_stale_failed_and_bool_exit_proofs_are_refused — Actual trusted publisher caller and modeled receipt/input/byte decisions; does not report real repository lint or execute a push.
  - `test` PublicationProofDecisionTests.test_other_head_or_unbound_artifact_cannot_serve_as_current_prepublication_proof — Actual trusted publisher caller and modeled receipt/input/byte decisions; does not report real repository lint or execute a push.
  - `test` PublicationProofDecisionTests.test_actual_stream_tamper_and_wrapper_identity_change_are_refused — Actual trusted publisher caller and modeled receipt/input/byte decisions; does not report real repository lint or execute a push.
  - `test` PublicationProofDecisionTests.test_latest_failed_attempt_cannot_fall_back_to_older_success — Actual trusted publisher caller and modeled receipt/input/byte decisions; does not report real repository lint or execute a push.
- Evidence: `file:docs/checkpoints/GATE-3-CP-0001/DECISIONS.md`, `file:docs/DEVELOPMENT-CONTRACT.md`, `file:docs/checkpoints/GATE-7-CP-0003/PRE-PUSH-LINT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/INTERNAL-ENVIRONMENT-REWORK.json`, `file:tests/test_m2_progress_publication.py`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/publication-policy/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/publication-policy/run-0003.json`

### LSN-0055 — A contract a model must follow has to reach the model, rendered from the definition the parser enforces

- Status: `GUARDED`, severity MEDIUM, category model-behavior, recurrences 0.
- Source: GATE-3, GATE-3-CP-0002, finding M1-F-001.
- Symptom: With the operator's configured model the developer stage never produced a valid tool request: the arguments were written at the top level of the envelope, then under 'args' after the one repair, and the run failed INVALID_AGENT_OUTPUT. A second model made two valid requests, then failed the same way.
- Root cause: The runtime described a tool request only as a tool that 'carries its name and arguments' and never showed the keys. The schema that named them reached a model only as a structured-output request, made only for a model whose capability is known, and the configured provider declares none; the docstring said the schema documented the prompt, and nothing checked that it did. The parser also dropped a stray key in the tool object, so an argument sent under 'args' was lost silently and refused later by the sandbox.
- Resolution: protocol.envelope_contract renders the version, every kind, one minimal valid envelope per kind with tool.name and tool.arguments, and where the arguments go, from envelope_schema() and the kind table the parser enforces. The runtime instructions carry it on every turn and the repair restates it verbatim with the stage's tools; the parser refuses a key beside name and arguments by its own reason. A live coding run of the configured model then made eleven valid tool requests, all executed in the sandbox, with no repair.
- Prevention:
  - `test` test_the_runtime_instructions_show_the_exact_envelope_of_every_kind — The instructions carry the contract rendered from the schema, verbatim, with the stage's tools.
  - `test` test_the_repair_restates_the_same_shape — The repair restates the same contract.
  - `test` test_the_rendered_contract_follows_the_schema — A change of the canonical schema changes the rendered text.
  - `test` test_no_second_envelope_contract_is_written_by_hand — The instructions module spells no envelope key of its own.
  - `test` test_arguments_outside_tool_arguments_are_refused_by_their_real_defect — Arguments outside tool.arguments are refused by their real defect.
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/protocol.py`, `file:services/agent-runtime/src/iacode_agent_runtime/context.py`, `file:services/agent-runtime/tests/test_protocol.py`, `file:services/agent-runtime/tests/test_context.py`, `file:docs/checkpoints/GATE-3-CP-0002/FINDINGS.json`, `file:docs/checkpoints/GATE-3-CP-0003/LIVE-CODING-RUN.json`

### LSN-0056 — A result is accepted only from the executor that owns the request, decided when the request is created

- Status: `GUARDED`, severity MEDIUM, category security, recurrences 0.
- Source: GATE-3, GATE-3-CP-0002, finding M1-F-002.
- Symptom: In the deterministic timeout scenario, a SUCCEEDED result posted to the API while the sandbox executed the command was answered 200; the stored result was the forged one, the sandbox's own execution record still said TIMED_OUT, and the agent answered TIMEOUT-NOT-SEEN.
- Root cause: resolve_tool_request accepted any PENDING request of the run whatever its executor, and the workflow resumed the agent with the stored result, answering the sandbox's later delivery with the first one. Nothing recorded that a sandboxed stage's request is answered by the sandbox, so every door looked the same.
- Resolution: A tool request records its executor when it is created: SANDBOX for a stage with a sandbox policy, EXTERNAL otherwise (migration 0005). The store takes the origin of a result from the caller's code path — the API's service passes EXTERNAL, the workflow's internal activity passes SANDBOX — and refuses a mismatch with TOOL_RESULT_ORIGIN_REFUSED (403) before anything is stored or signalled. The audit's null control and mutation are a verification stage.
- Prevention:
  - `test` test_a_forged_result_cannot_displace_the_sandbox_result — A forged result before and after the sandbox's own is refused and the stored result is the sandbox's.
  - `test` test_a_manual_result_for_a_sandbox_request_is_refused — A manual result for a sandbox request is refused and nothing is stored.
  - `test` test_a_result_for_a_request_the_sandbox_owns_is_refused_and_never_signalled — The API answers 403 TOOL_RESULT_ORIGIN_REFUSED and signals nothing.
  - `test` test_every_caller_declares_a_constant_origin — Every caller passes a constant origin, never one read from a payload; the scan fires on a mutated source.
  - `test` test_existing_requests_are_backfilled_from_what_the_sandbox_executed — Existing requests keep their meaning through the migration.
  - `automated-check` scripts/iacode/scenarios/sandbox_coding_e2e.py — The verification stage sandbox-tool-result-origin: the audit's null control and mutation on the real stack.
- Evidence: `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`, `file:services/orchestrator/src/iacode_orchestrator/agent_runtime/activities.py`, `file:apps/api/migrations/versions/0005_tool_request_executor.py`, `file:apps/api/tests/integration/test_agent_runtime_persistence.py`, `file:docs/checkpoints/GATE-3-CP-0002/FORGED-RESULT-PROBE.json`

### LSN-0057 — A pinned lock can become unsafe without changing, so advisory state is live evidence

- Status: `GUARDED`, severity CRITICAL, category security, recurrences 0.
- Source: GATE-3, GATE-3-CP-0004, finding M1-F-004.
- Symptom: A sealed delivery whose implementation checks passed later failed the unchanged dependency gate with two Critical and four High npm advisories in its pinned graph.
- Root cause: The lockfile was reproducible but advisory state changed after it was pinned. Reproducibility fixes the graph; it does not make the graph permanently safe.
- Resolution: Update the direct frontend pins and resolved lock graph to non-vulnerable versions, then require a live scan of both npm and PyPI advisory sources before handoff.
- Prevention:
  - `automated-check` scripts/iacode/dependency_scan.py — The mandatory scan fails closed when either advisory source is unavailable and blocks every relevant Critical or High finding.
  - `test` test_the_dependency_scan_blocks_critical_and_high_findings — The dependency scanner's blocking severities and fail-closed source policy are structural assertions, so weakening either turns the suite red.
- Evidence: `file:docs/checkpoints/GATE-3-CP-0004/FINDINGS.json`, `file:docs/checkpoints/GATE-3-CP-0004/DEPENDENCY-SCAN-REPORT.json`, `file:scripts/iacode/dependency_scan.py`

### LSN-0058 — Container health does not prove Docker Desktop host-port forwarding

- Status: `GUARDED`, severity MEDIUM, category environment, recurrences 0.
- Source: GATE-3, GATE-3-CP-0005, finding cmd-0046-infra.
- Symptom: The complete verifier and two targeted reruns found Grafana, MinIO and Redis accepting host connections and immediately closing them, while Compose reported every affected container healthy.
- Root cause: Docker Desktop's host-side published-port forwarding had entered a stale state. Container-local health checks remained green, so health alone could not observe it.
- Resolution: Restart the full stack without deleting volumes, wait for every service to recover, and repeat the live host-facing infrastructure suite. The unchanged 49-test suite then passed.
- Prevention:
  - `test` test_grafana_is_healthy — Live tests connect through the actual loopback-published Grafana, MinIO and Redis ports instead of trusting container health metadata.
- Evidence: `file:docs/checkpoints/GATE-3-CP-0005/COMMANDS.jsonl`, `file:infra/tests/test_running_stack.py`

### LSN-0059 — A lesson exclusion must declare the scope it excludes

- Status: `GUARDED`, severity HIGH, category process, recurrences 1.
- Source: GATE-3, GATE-3-CP-0005, finding cmd-0064.
- Symptom: The full suite rejected LSN-0058 because technology and module selectors excluded it from a generic preflight while its scopes list was empty.
- Root cause: Applicability dimensions were used as incidental metadata. In this model they are selectors, so they silently narrowed where the lesson constrained delivery.
- Resolution: Remove selectors that were not intended to narrow LSN-0058. Reserve non-empty selectors for deliberate exclusions, with scopes naming the boundary explicitly.
- Prevention:
  - `test` test_the_repository_preflight_covers_every_applicable_lesson — Every active lesson excluded from a canonical preflight must carry a non-empty scopes declaration that makes the exclusion reviewable.
- Evidence: `file:docs/checkpoints/GATE-3-CP-0005/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0009/COMMANDS.jsonl`, `file:tests/test_development_ledger.py`

### LSN-0060 — Parent and child facts without an ORM relationship require an explicit flush boundary

- Status: `GUARDED`, severity MEDIUM, category implementation, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding quality persistence integration failure.
- Symptom: The first real PostgreSQL quality-plan insert attempted to persist quality_checks before their quality_plans parent and failed its foreign key, although both objects had been added to one SQLAlchemy session.
- Root cause: The store assigned the foreign-key UUID directly but declared no ORM relationship between the newly created plan and check objects. The unit of work therefore had no object dependency edge that guaranteed the parent insert first.
- Resolution: Insert and flush the quality plan before adding its checks, and insert and flush a quality run before adding its initial event. Keep the real PostgreSQL lifecycle test in complete verification.
- Prevention:
  - `test` test_plan_run_results_verdict_and_events_round_trip — The real PostgreSQL integration creates the plan with its child checks, creates the run with its first event, and reads the complete lifecycle back.
- Evidence: `file:services/evaluator/src/iacode_evaluator/store.py`, `file:services/evaluator/tests/integration/test_quality_persistence_integration.py`

### LSN-0061 — Cancellation completion must not bypass cleanup acknowledgement

- Status: `GUARDED`, severity MEDIUM, category testing, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0029.
- Symptom: The rebuilt evaluator suite failed because its late-callback test tried to transition a running quality run directly to CANCELLED.
- Root cause: The test used the terminal label as setup and skipped the CANCELLING state that records the cancellation request and reserves time for sandbox cleanup acknowledgement.
- Resolution: Drive the test through RUNNING to CANCELLING with CANCELLATION_REQUESTED, then to CANCELLED with COMPLETED before testing rejection of a late callback.
- Prevention:
  - `test` test_results_enforce_owner_idempotency_and_late_refusal — The store test executes both cancellation transitions and then proves that a callback delivered after cleanup completion is refused.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:services/evaluator/tests/test_persistence.py`

### LSN-0062 — Provenance digests are a set even when their sources are distinct

- Status: `GUARDED`, severity MEDIUM, category implementation, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding quality workflow adapter focused test.
- Symptom: The first workflow-adapter test failed when the snapshot and policy fixtures intentionally shared a digest, because the evidence contract refuses duplicate sourceDigests.
- Root cause: The activity treated semantic source slots as if they implied distinct content hashes. Two different source roles may legitimately resolve to identical bytes, while the evidence contract records the unique content set.
- Resolution: Deduplicate source digests by value while preserving their first-seen order before constructing immutable evidence.
- Prevention:
  - `test` test_a_sandbox_answer_becomes_redacted_immutable_evidence — The adapter test uses equal snapshot and policy digests and proves that redacted evidence is still accepted and persisted once.
- Evidence: `file:services/evaluator/src/iacode_evaluator/activities.py`, `file:services/evaluator/tests/test_workflow.py`

### LSN-0063 — An identity shared across services must satisfy the strictest persistence type and remain stable

- Status: `GUARDED`, severity HIGH, category architecture, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding first live quality execution.
- Symptom: The first end-to-end quality run reached the sandbox and failed when its readable quality-check identity was parsed for a UUID database column.
- Root cause: The evaluator treated toolRequestId as an opaque string while the shared sandbox store persists it as UUID. The contract's syntax was looser than the receiver's durable representation.
- Resolution: Derive each quality execution identity as UUIDv5 from the immutable run and check identities, retaining both retry stability and database compatibility.
- Prevention:
  - `test` test_quality_tool_identity_is_a_stable_uuid — The same run and check always derive the same valid UUID, while another check derives a different one.
- Evidence: `file:services/evaluator/src/iacode_evaluator/executor.py`, `file:services/evaluator/tests/test_core.py`

### LSN-0064 — A shared execution resource needs an explicit exclusive owner for every owning domain

- Status: `GUARDED`, severity HIGH, category architecture, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding first live sandbox persistence for a quality run.
- Symptom: A real evaluator run could not create its sandbox session because sandbox_sessions required task_run_id even though no task run owned the quality run.
- Root cause: Gate 3 encoded the then-only owner in the table shape. Reusing the sandbox from a second durable domain without evolving ownership would have required a fake task run or a nullable unowned session.
- Resolution: Add quality_run_id, constrain exactly one owner with num_nonnulls, and enforce a separate one-active-session partial unique index for each owner domain.
- Prevention:
  - `test` test_a_sandbox_session_has_exactly_one_run_owner_and_one_active_slot_per_owner — The declared model requires one and only one owner and one active slot for both task and quality runs.
  - `test` test_plan_run_results_verdict_and_events_round_trip — Real PostgreSQL accepts a quality-owned session through the lifecycle.
- Evidence: `file:packages/persistence/src/iacode_persistence/models.py`, `file:apps/api/migrations/versions/0006_quality_engine.py`, `file:apps/api/tests/unit/test_domain_model.py`, `file:services/evaluator/tests/integration/test_quality_persistence_integration.py`

### LSN-0065 — A shared execution identifier must not be written into a foreign key owned by another domain

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding live evaluator sandbox execution after owner migration.
- Symptom: After the session gained a quality owner, execution still failed when active_tool_request_id tried to reference the evaluator's stable UUID in tool_requests, where only agent-runtime requests exist.
- Root cause: The sandbox used one request shape for two domains but treated every request identifier as an agent tool-request foreign key. Syntactic compatibility did not imply ownership compatibility.
- Resolution: Bind active_tool_request_id only when agentRunId proves an agent-runtime owner; evaluator execution remains durable through its quality result and session owner.
- Prevention:
  - `test` test_only_agent_requests_bind_the_agent_tool_request_foreign_key — An evaluator request yields no agent FK while an agent request preserves its durable tool-request reference.
- Evidence: `file:services/sandbox/src/iacode_sandbox/service.py`, `file:services/sandbox/tests/test_sandbox_service.py`

### LSN-0066 — Immutable content identity excludes observation time and the first observer

- Status: `GUARDED`, severity HIGH, category architecture, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding live quality plan replay.
- Symptom: Re-running the same snapshot and policy conflicted with its existing frozen quality plan because createdAt and the first owner differed.
- Root cause: The reuse check compared the complete serialized record rather than the material inputs that define plan content, so observational metadata was mistaken for a conflicting plan definition.
- Resolution: Compare plan material identity from snapshot, policy, project profile and frozen checks while retaining the original immutable creation time and owner as provenance.
- Prevention:
  - `test` test_content_addressed_plan_reuse_ignores_observation_time_and_first_owner — The same material plan reuses one row despite a later observation time and a different owner.
- Evidence: `file:services/evaluator/src/iacode_evaluator/store.py`, `file:services/evaluator/tests/test_persistence.py`

### LSN-0067 — Cancellation semantics must survive orchestration-library exception wrapping

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding live running cancellation scenario.
- Symptom: The sandbox acknowledged cancellation and cleaned up, but the evaluator persisted ERROR because Temporal delivered the cancelled activity as ActivityError rather than asyncio.CancelledError.
- Root cause: The workflow classified the Python exception wrapper instead of combining the durable cancellation request with the sandbox's acknowledged activity cancellation semantics.
- Resolution: When cancellation was requested, translate the activity failure that completes WAIT_CANCELLATION_COMPLETED into a CANCELLED quality result and preserve ERROR for activity failures without that request.
- Prevention:
  - `test` test_an_acknowledged_activity_cancellation_stays_a_cancellation — A cancellation-requested activity wrapped as ActivityError produces CANCELLED, while the non-cancelled error path remains distinct.
- Evidence: `file:services/evaluator/src/iacode_evaluator/workflow.py`, `file:services/evaluator/tests/test_workflow.py`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`

### LSN-0068 — A bounded parser must apply each content limit only to content it interprets

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0044.
- Symptom: The complete functional battery passed six scenario classes but could not evaluate the IACode snapshot because a large canonical-requirements JSON file was rejected as an oversized project manifest.
- Root cause: detect_project received a whole snapshot inventory and applied MAX_MANIFEST_BYTES before deciding whether a path was one of the manifest names it reads. An unrelated file therefore inherited a parser-specific limit.
- Resolution: Normalize every path, ignore non-manifest basenames before measuring content, and retain the same fail-closed size check for every actual stack manifest and iacode-quality.json.
- Prevention:
  - `test` test_large_non_manifest_content_does_not_block_project_detection — A supported project containing an unrelated oversized policy file is still detected from its real manifest.
  - `test` test_paths_and_manifest_sizes_are_bounded — The same detector still refuses an oversized actual manifest and unsafe paths.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:services/evaluator/src/iacode_evaluator/projects.py`, `file:services/evaluator/tests/test_core.py`

### LSN-0069 — A polyglot plan binds each check to both its project root and its toolchain

- Status: `GUARDED`, severity HIGH, category architecture, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0049.
- Symptom: After unrelated large files were ignored correctly, the real IACode snapshot was still refused because its Python plus Angular/TypeScript stacks had no exact single-stack policy profile.
- Root cause: Detection collapsed a monorepo into a set of stacks but discarded which roots declared each stack, while execution chose one sandbox policy for the whole run. An exact composite profile alone would still have run commands from the repository root and reused the wrong image.
- Resolution: Preserve every detected stack/root pair in the content-addressed profile, add the exact closed composite policy, expand each policy runner at its matching roots, select sandbox policy from the frozen runner, and release sessions between checks so a run may change toolchains without changing ownership.
- Prevention:
  - `test` test_polyglot_monorepo_checks_keep_their_stack_roots — A Python and Angular/TypeScript monorepo produces checks at each declared root and common checks once at the repository root.
  - `test` test_a_polyglot_plan_selects_each_check_image_from_its_frozen_runner — Python, Angular and common checks select only their policy-owned quality images from frozen runner identity.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:.iacode/policies/quality-policy.json`, `file:services/evaluator/src/iacode_evaluator/projects.py`, `file:services/evaluator/src/iacode_evaluator/planner.py`, `file:services/evaluator/src/iacode_evaluator/executor.py`, `file:services/evaluator/src/iacode_evaluator/workflow.py`, `file:services/evaluator/tests/test_core.py`

### LSN-0070 — Project discovery must separate deployable roots, nested fixtures and check applicability

- Status: `GUARDED`, severity HIGH, category architecture, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0054.
- Symptom: The real IACode evaluation treated deliberately failing evaluator fixtures as independent projects and executed unit runners in packages that had no unit-test sources, producing failures unrelated to the committed repository's quality.
- Root cause: The profile inventory classified every nested manifest as a deployable workspace root and the planner marked every profile runner applicable without preserving enough source inventory to decide whether a unit suite existed.
- Resolution: Preserve the bounded source-path inventory in the content-addressed profile, exclude fixture manifests from workspace-root discovery, and freeze unit checks as non-applicable and non-mandatory only when the corresponding root contains no test source.
- Prevention:
  - `test` test_nested_fixture_manifests_do_not_become_workspace_roots — A manifest below a fixtures directory remains test data and never expands the execution plan.
  - `test` test_unit_checks_are_not_applicable_without_test_sources — A source-only package records an explicit non-applicability reason instead of executing an empty suite.
  - `test` test_unit_checks_are_mandatory_when_test_sources_exist — The same rule cannot suppress a unit check when a test source exists.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:services/evaluator/src/iacode_evaluator/projects.py`, `file:services/evaluator/src/iacode_evaluator/planner.py`, `file:services/evaluator/tests/test_core.py`

### LSN-0071 — Every quality image must provision snapshots on its oldest runtime and prepare each isolated check

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0054.
- Symptom: All Node checks failed before obtaining a sandbox because the shared helper called Python 3.12's tar extraction filter inside the Node image's Python 3.11, while successful provisioning would still have left later isolated checks without dependencies installed by an earlier sandbox.
- Root cause: A shared helper was validated only on its newest interpreter, and the plan assumed dependency installation survived between checks even though toolchain changes intentionally release each sandbox session.
- Resolution: Replace version-specific bulk extraction with manually validated regular-file extraction supported by every pinned runtime, exercise snapshot provisioning in every real quality image, expose local Python packages through a policy-owned wrapper, and make every Node check bootstrap its pinned offline dependency cache.
- Prevention:
  - `test` test_every_quality_helper_provisions_a_real_snapshot — Each pinned quality image provisions and reads an authorised snapshot through its actual helper runtime.
  - `test` test_isolated_language_checks_prepare_their_policy_owned_toolchain — Closed Python and Node runners prove their per-check dependency preparation is part of the frozen command.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:services/sandbox/src/iacode_sandbox/helper.py`, `file:services/sandbox/tests/test_quality_images.py`, `file:services/evaluator/src/iacode_evaluator/runners.py`, `file:services/evaluator/tests/test_core.py`

### LSN-0072 — Secret findings and reviewed false positives must share one policy-owned taxonomy

- Status: `GUARDED`, severity HIGH, category security, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0054.
- Symptom: The repository's mandatory secret gate passed with reviewed digest-bound false positives, but the Quality Engine failed the same immutable snapshot because its three image-local scanners used a different broader pattern and had no policy-owned allowance mechanism.
- Root cause: Secret detection logic was duplicated per image and diverged from the canonical finding kinds and allowlist semantics, so identical evidence received contradictory verdicts.
- Resolution: Use one offline scanner across all quality images, bind its canonical pattern taxonomy and reviewed digest allowlist into every content-addressed image, validate the policy structure fail-closed, and continue rejecting every matching value not explicitly allowed by policy.
- Prevention:
  - `test` test_quality_images_bind_the_policy_owned_secret_scanner — Every quality image fingerprint includes the shared scanner and the canonical reviewed allowlist.
  - `test` test_a_non_allowlisted_credential_shape_fails_the_secret_check — The shared scanner still fails an unreviewed credential-shaped value in every real quality image.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:services/sandbox/images/quality_secret_scan.py`, `file:.iacode/policies/secret-scan-allowlist.json`, `file:services/sandbox/tests/test_sandbox_images.py`, `file:services/sandbox/tests/test_quality_images.py`

### LSN-0073 — The canonical lint denominator must cover every detected project root

- Status: `GUARDED`, severity HIGH, category quality, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0054.
- Symptom: The mandatory lint gate reported PASS while the sandboxed Quality Engine found dozens of findings in the Model Gateway and Orchestrator rehearsal roots of the same committed snapshot.
- Root cause: The lint command carried a manually curated root tuple that omitted two Python project areas, so its green verdict described only a subset of the repository profile detected by the Quality Engine.
- Resolution: Add every omitted source and test root to the canonical lint command, repair the real findings, and enforce that each non-fixture pyproject root intersects the lint denominator.
- Prevention:
  - `test` test_mandatory_lint_covers_every_python_project_root — Every Python project root discovered from repository manifests is covered by at least one canonical lint root.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:scripts/iacode/gates/lint.py`, `file:tests/test_gate4_quality_engine.py`, `file:services/model-gateway/src/iacode_model_gateway/config.py`, `file:services/orchestrator/rehearsal/coding.py`

### LSN-0074 — An importable source tree is not an installed or repository-configured test environment

- Status: `GUARDED`, severity CRITICAL, category implementation, recurrences 2.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0070.
- Symptom: The real repository evaluation imported local Python sources successfully but failed package tests that queried distribution metadata and API tests that resolved repository policy relative to their nested package root.
- Root cause: The quality wrapper treated PYTHONPATH as equivalent to package installation and assumed a package-root working directory exposed repository-root configuration. Neither property is true in an isolated monorepo sandbox.
- Resolution: Before a pytest command, install the current project offline with no dependency resolution into sandbox-local temporary site packages and expose the repository's .iacode directory at the nested project root with an internal workspace symlink.
- Prevention:
  - `test` test_python_unit_runner_installs_metadata_and_exposes_monorepo_policy — A real nested-package snapshot proves distribution metadata and repository policy are both visible through the quality-python wrapper.
  - `test` test_python_functional_fixtures_reach_their_intended_test_outcome — Every Python functional fixture is installed and executed in the real no-network quality image, and none may fail during metadata generation.
  - `test` test_real_registry_is_bound_explicitly_when_working_directory_is_nested — Execute the strengthened current causal boundary without weakening inherited controls.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:services/sandbox/images/quality-python/python_runner.py`, `file:services/sandbox/tests/test_quality_images.py`, `file:docs/checkpoints/GATE-4-CP-0001/QUALITY-IACODE-FAIL-CMD-0070.json`, `file:services/evaluator/tests/fixtures/python-pass/pyproject.toml`, `file:services/evaluator/tests/fixtures/python-fail/pyproject.toml`, `file:services/evaluator/tests/fixtures/python-slow/pyproject.toml`, `file:docs/checkpoints/GATE-4-CP-0001/QUALITY-RECOVERY-PACKAGING-FAIL-CMD-0173.json`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`

### LSN-0075 — Offline package installation requires its build backend inside the quality image

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0072.
- Symptom: The real sandbox guard for installed Python metadata failed before tests because pip could not import setuptools.build_meta while network access and build isolation were deliberately disabled.
- Root cause: The quality wrapper correctly requested an offline no-isolation install, but the image assumed the Python base image supplied the project build backend instead of pinning that backend as part of the policy-owned toolchain.
- Resolution: Pin setuptools 80.9.0 in the content-addressed quality-python image and keep the real nested-package guard running through the canonical sandbox gate that rebuilds the service and image inputs first.
- Prevention:
  - `test` test_python_unit_runner_installs_metadata_and_exposes_monorepo_policy — A real no-network quality image must build and install a setuptools project before its tests query distribution metadata.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:services/sandbox/images/quality-python/Dockerfile`, `file:services/sandbox/images/quality-python/python_runner.py`, `file:services/sandbox/tests/test_quality_images.py`

### LSN-0076 — Projected nested configuration requires an explicit monorepo root

- Status: `GUARDED`, severity HIGH, category architecture, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0084.
- Symptom: The post-rework IACode evaluation reached all 52 applicable results but the evaluator unit suite treated its projected package-local .iacode directory as the repository root and therefore found no evaluator source files.
- Root cause: The sandbox projected repository policy into a nested working directory for relative configuration consumers, while source-boundary tests inferred ownership from the first .iacode directory they encountered. Projection and discovery then gave the same marker two incompatible meanings.
- Resolution: The quality-python wrapper now exports the immutable sandbox repository root explicitly, and evaluator tests prefer that trusted root while retaining filesystem discovery for ordinary checkout execution.
- Prevention:
  - `test` test_python_unit_runner_installs_metadata_and_exposes_monorepo_policy — A real nested snapshot receives both package-local policy compatibility and the canonical absolute repository root.
  - `test` test_no_evaluator_module_can_start_a_process — The evaluator boundary scan resolves and inspects every source module when executed from its nested project root.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:services/sandbox/images/quality-python/python_runner.py`, `file:services/sandbox/tests/test_quality_images.py`, `file:services/evaluator/tests/test_core.py`

### LSN-0077 — Harness wait bounds must reflect workload size without changing product deadlines

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 2.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0084.
- Symptom: The real IACode scenario stopped waiting after 300 seconds while its durable 57-check workflow was still running and later reached a legitimate terminal verdict.
- Root cause: The harness reused the small-fixture wait bound for the full polyglot repository even though per-check isolated package preparation intentionally increased execution time.
- Resolution: Bind only IACode's observer to unchanged canonical maxRunSeconds3600 plus60 finite grace. Ordinary300/durable900 waits and every product/check/workflow deadline remain unchanged. Current60-case Gate7 cmd-0160 and unchanged49-case Gate4 cmd-0163 pass, including timeout/late-success refusal; inherited controls cmd-0164 and whole lint cmd-0161 pass.
- Prevention:
  - `test` test_real_repository_scenario_has_a_separate_bounded_wait — AST-bound control proves the real-repository and durable quality scenarios plus sandbox workflow completion use distinct finite bounds at least twice the ordinary wait.
  - `test` Gate7QualityObservationTests.test_large_repository_observer_covers_unchanged_canonical_run_deadline — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0001/VERIFY-FAIL-CMD-0105.json`, `file:scripts/iacode/scenarios/quality_engine_e2e.py`, `file:scripts/iacode/scenarios/sandbox_coding_e2e.py`, `file:tests/test_gate4_quality_engine.py`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/RUNTIME-V2-FAILED-FULL-MANIFEST.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/CURRENT-REWORK-GATE7-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-LINT-0006.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-HELPER-QUALITY-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-GATE4-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-CONTROLS-0001.json`

### LSN-0078 — Evidence recorders must resolve caller-supplied commit references before execution

- Status: `GUARDED`, severity HIGH, category quality, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0096.
- Symptom: A successful real-repository command record accepted a mistyped 40-character subjectCommit and duplicated an input that was both detected and explicitly declared, leaving evidence metadata that would fail published-history validation.
- Root cause: The recorder validated command replayability but trusted the optional subject commit as opaque text and concatenated detected and caller-supplied inputs without canonicalization.
- Resolution: Resolve every supplied subject through git rev-parse before launching the command, record the canonical full commit, refuse unresolved subjects with an appended precondition record, and deduplicate the ordered input set.
- Prevention:
  - `test` test_inputs_are_canonicalized_and_an_unknown_subject_is_refused — The same recorder path proves duplicate inputs collapse and a nonexistent subject is recorded as a refusal without executing the command.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:scripts/development-ledger/record_command.py`, `file:tests/test_gate3_sandbox.py`

### LSN-0079 — Test discovery and the unit runner must cover the same project scope

- Status: `GUARDED`, severity HIGH, category testing, recurrences 1.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0105.
- Symptom: The intentionally failing Python fixture produced six passing quality results because project detection saw its root-level test_calculator.py while the unit runner collected only the tests directory and executed zero tests.
- Root cause: Applicability used a repository-wide test-source rule, but the closed runner embedded a narrower conventional directory. The plan therefore made a mandatory check applicable and then silently measured a different denominator.
- Resolution: Run pytest from the entire frozen project root and rely on policy-owned markers and project conftest exclusions, so every source that makes a unit check applicable is within the runner's collection scope.
- Prevention:
  - `test` test_isolated_language_checks_prepare_their_policy_owned_toolchain — The closed Python unit runner is bound to the project root rather than a narrower tests directory; the real failing fixture remains required closure evidence.
  - `test` test_unit_checks_are_mandatory_when_test_sources_exist — The planner makes Python unit checks mandatory for root, tests-directory, nested test_*, and *_test.py sources covered by pytest collection.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/VERIFY-FAIL-CMD-0105.json`, `file:services/evaluator/src/iacode_evaluator/runners.py`, `file:services/evaluator/tests/test_core.py`, `file:scripts/iacode/scenarios/quality_engine_e2e.py`, `file:services/evaluator/src/iacode_evaluator/planner.py`, `file:docs/checkpoints/GATE-4-CP-0001/QUALITY-FALSE-PASS-CMD-0161.json`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`

### LSN-0080 — A failed verification stage must not leave an older PASS report addressable

- Status: `GUARDED`, severity HIGH, category quality, recurrences 1.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0105.
- Symptom: The agent-durability stage failed in the complete verification, but var/agent-durability.json still contained a PASS report from the previous day, making a direct artifact inspection contradict the current stage verdict.
- Root cause: The verification reused fixed generated report paths and did not remove the prior artifact before launching a stage. A stage that exited before writing its report left historical success at the current path.
- Resolution: Before every stage carrying a --report argument, remove only that generated path when it resolves inside the repository, so failure yields an absent report rather than stale positive evidence. Gate 5 also retires validated standalone desktop reports before project imports. Cmd-0085 preserved the causal stale-PASS/cold-import red control; cmd-0086 re-executed it unchanged green. The full-verifier pre-launch retirement remains intact.
- Prevention:
  - `test` test_verification_removes_a_stale_stage_report_before_execution — A prior PASS artifact at a stage report path is removed before the stage process can run.
  - `test` test_standalone_live_proof_retires_old_pass_before_dependency_import_failure — Copy the actual standalone probe, seed an old PASS and corrupt its canonical startup data. The real isolated child must fail after retiring the old report, before any runtime stack exists.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0001/VERIFY-FAIL-CMD-0105.json`, `file:scripts/iacode/verify.py`, `file:tests/test_gate4_quality_engine.py`, `file:tests/test_gate5_clients.py`, `file:scripts/iacode/scenarios/desktop_e2e.py`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`

### LSN-0081 — Canonical requirement evidence must name a test the repository actually discovers

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0112.
- Symptom: Fourteen Gate 4 checklist rows named intended test labels that no declared suite defined, so the repository-wide specification-evidence control rejected the canonical requirement source.
- Root cause: The checklist was written against conceptual test names before the executable suites settled on their final discoverable identities, and the registry faithfully mirrored the stale labels.
- Resolution: Bind every affected checklist and canonical-registry row to the existing test identity that exercises its behavior, preserving the requirement text and test denominator.
- Prevention:
  - `test` test_every_test_the_specifications_name_exists — Every backticked test identity in every canonical Gate checklist resolves in the declared test suites.
- Evidence: `file:docs/GATE-4-CHECKLIST.md`, `file:.iacode/policies/canonical-requirements.json`, `file:tests/test_gate1_model_gateway.py`

### LSN-0082 — Engineering memory cannot depend on an ephemeral generated report

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 1.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0112.
- Symptom: Lesson validation failed after the verifier correctly cleared var/gate4-quality-cancel.json before a rerun, because LSN-0067 treated that replaceable report as durable evidence.
- Root cause: The lesson registry referenced a path in var even though verification owns that directory as regenerable current-run output and is allowed to remove stale reports.
- Resolution: Replace ephemeral or unsupported references with checkpoint-owned file evidence and retain repository controls that refuse non-file lesson evidence and every file:var/ evidence reference.
- Prevention:
  - `test` test_engineering_memory_never_depends_on_ephemeral_var_evidence — No lesson may cite a generated file under var as durable evidence.
  - `validator` scripts/development-ledger/validate_lessons.py — Lesson evidence accepts only resolvable repository file references.
- Evidence: `file:.iacode/memory/lessons.jsonl`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0009/COMMANDS.jsonl`, `file:tests/test_gate4_quality_engine.py`

### LSN-0083 — A command that decodes captured UTF-8 must also configure the stream that re-emits it

- Status: `GUARDED`, severity CRITICAL, category tooling, recurrences 6.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0112.
- Symptom: The canonical suite found program_state.py and review_bundle.py capturing subprocess output safely but re-emitting it through the Windows platform codepage without configuring stdout.
- Root cause: The entry points decoded child output explicitly but their own stdout still used the Windows platform codepage; the original guardrail scanned scripts but not executable checkpoint evidence harnesses.
- Resolution: CP0003 local prevention restored by actual current producer/null/adverse controls and unchanged inherited controls. Whole current immutable verification, ordered internal assurance and fresh independent M2 validation remain separate obligations.
- Prevention:
  - `test` test_every_tool_that_re_emits_captured_output_configures_its_own_stream — Every executable script and current-checkpoint evidence harness that captures child output configures UTF-8 output directly or through the shared main guard.
  - `test` test_cold_diagnostic_entrypoints_use_utf8_before_any_work — Execute the actual three entry blocks and shared stream bootstrap in cold cp1252 children with harmless fixture work; Unicode stdout/stderr must be UTF-8, and removing the bootstrap must raise UnicodeEncodeError before effects. Original capture/cleanup main bodies are never replayed.
  - `test` Gate7DocumentationAndStreamsTests.test_current_entrypoints_configure_the_shared_stream_before_work — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
  - `test` M2CurrentStreamBootstrapTests.test_actual_capture_entry_blocks_reject_cold_bootstrap_removal — Executed actual current positive/adverse control; no production fake or independent verdict.
- Evidence: `file:scripts/development-ledger/program_state.py`, `file:scripts/development-ledger/review_bundle.py`, `file:tests/test_gate0_foundation.py`, `file:docs/checkpoints/GATE-4-CP-0005/RUN-PUBLISHED-FULL-VERIFICATION.py`, `file:docs/checkpoints/GATE-4-CP-0005/PUBLISHED-FULL-VERIFY-FAIL-CMD-0040.json`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/FULL-PRODUCER-d2b2b71d1263-INTERNAL-FULL-VERIFY.json`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:tests/test_gate6_experience.py`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:tests/test_gate7_assurance.py`, `file:tests/test_gate7_knowledge.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/INTERNAL-ENVIRONMENT-REWORK.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/tests/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0011.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/native-observation/run-0003.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge-physical-bounds/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge/run-0005.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/owned-cleanup/run-0004.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/operator-cleanup/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/current-streams/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/inherited-streams/run-0001.json`

### LSN-0084 — A historical Gate documentation test must derive the current entry-point state

- Status: `GUARDED`, severity HIGH, category testing, recurrences 1.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0120.
- Symptom: The Gate 3 documentation suite required the current START-HERE.md to contain READY_FOR_MILESTONE_AUDIT even after Gate 4 correctly changed the implementing-run destination to READY_FOR_REVIEW.
- Root cause: A predecessor's regression test mixed preserved historical references with a current-state assertion and hard-coded the predecessor's next lifecycle state.
- Resolution: Keep assertions that the Gate 3 checklist and sandbox runbook remain linked, derive the active Gate from the current checkpoint, and assert the repository-wide implementing-run destination READY_FOR_REVIEW. Gate 5 binds the historical specification controls to the specification's owner and uses CURRENT_GATE only for live-tree scope. A future-Gate behavioral control and an intentionally wrong-selector mutation exercise the unchanged assertions.
- Prevention:
  - `test` test_the_entry_point_names_the_current_gate — The predecessor documentation control derives the active Gate while retaining its historical links and the current implementing-run handoff contract.
  - `test` test_historical_gate4_controls_keep_their_owning_gate — Run the unchanged historical specification/functional assertions after a simulated future Gate, while retaining current-state scope checks and a rejecting selector mutation.
- Evidence: `file:tests/test_gate3_sandbox.py`, `file:START-HERE.md`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/BASELINE.md`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:tests/test_gate5_clients.py`, `file:tests/test_gate4_quality_engine.py`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`

### LSN-0085 — A source-based control must assert syntax semantics rather than formatter layout

- Status: `GUARDED`, severity MEDIUM, category testing, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0126.
- Symptom: The Gate 3 verification-stage test rejected a correct sandbox integration command only because the adjacent tokens -m and integration were formatted on separate lines.
- Root cause: The control searched raw source for one exact whitespace and quoting layout even though Python syntax already represented the stage call and its argument literals independently of formatting.
- Resolution: Parse build_stages with the AST, resolve each declared stage call, and compare its literal argument set to the expected semantic tokens.
- Prevention:
  - `test` test_the_verification_adds_the_stages_this_gate_introduces — The stage control resolves calls and literal arguments through Python syntax rather than substring layout.
- Evidence: `file:tests/test_gate3_sandbox.py`, `file:scripts/iacode/verify.py`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`

### LSN-0086 — A subprocess assertion must preserve the exit code when both streams are empty

- Status: `GUARDED`, severity MEDIUM, category testing, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0132.
- Symptom: The combined canonical suite observed a validator subprocess fail with empty stdout and stderr, and the assertion reported only that its expected marker was absent, erasing the process exit fact needed for diagnosis.
- Root cause: The test helper returned only concatenated streams as diagnostic context and did not synthesize any message when both were empty.
- Resolution: When captured streams are empty, return a stable diagnostic containing the validator process exit code; do not retry or reinterpret the outcome.
- Prevention:
  - `test` test_an_empty_validator_failure_keeps_its_process_exit_code — A mocked empty-stream failure preserves its exact process exit code in the assertion output.
- Evidence: `file:tests/test_gate3_sandbox.py`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`

### LSN-0087 — A rehearsal worker must register every workflow activity boundary

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0143.
- Symptom: The real Agent Runtime durability rehearsal resumed after a worker restart and completed its agent stage, but Temporal then failed the workflow because the rehearsal worker had not registered the new quality planning activity; the database row remained RUNNING.
- Root cause: Gate 4 extended the shared AgentRunWorkflow with post-run quality activities, while the purpose-built durability worker kept a hand-maintained activity list from Gate 2 and therefore no longer implemented the full workflow contract.
- Resolution: Register quality_plan and quality_result on every purpose-built rehearsal worker even when its workspace makes quality not applicable, and scan every rehearsal module that defines run_worker.
- Prevention:
  - `test` test_rehearsal_workers_register_the_post_run_quality_boundary — The durability rehearsal worker's actual Temporal activity list includes both post-run quality activities required by the shared workflow.
- Evidence: `file:services/orchestrator/rehearsal/durability.py`, `file:tests/test_gate4_quality_engine.py`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`, `file:services/orchestrator/rehearsal/coding.py`

### LSN-0088 — A test inside a built image can consume only inputs copied into that image

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0174.
- Symptom: The complete sandbox gate failed before exercising the new Python fixture behavior because the test resolved /evaluator/tests/fixtures from its host source layout, while the built sandbox image contained only /app/sandbox_tests and no evaluator fixture directory.
- Root cause: The test was authored against the repository filesystem visible to the editor rather than the explicit COPY boundary of the image in which pytest actually runs.
- Resolution: Copy the evaluator quality fixtures to a declared /app/quality_fixtures path in the sandbox test image and bind the test to that in-image path.
- Prevention:
  - `test` test_built_sandbox_test_image_carries_declared_external_fixture_inputs — The Dockerfile copy destination and the test fixture root are parsed and required to agree.
  - `test` test_python_functional_fixtures_reach_their_intended_test_outcome — The real built image reads and executes every copied functional fixture.
- Evidence: `file:services/sandbox/Dockerfile`, `file:services/sandbox/tests/test_quality_images.py`, `file:tests/test_gate4_quality_engine.py`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`

### LSN-0089 — Domain not-applicability and operational failure need distinct orchestration outcomes

- Status: `GUARDED`, severity HIGH, category architecture, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0193.
- Symptom: The real sandbox-coding run completed all agent stages over a synthetic snapshot, then the post-run quality activity raised QUALITY_PLAN_FAILED because no supported project stack was detected. Temporal failed the workflow while the durable run row remained RUNNING.
- Root cause: The quality activity collapsed an expected domain result, PROJECT_UNSUPPORTED, and every unexpected planning exception into an application error name outside the Agent Runtime taxonomy. The first should have meant not applicable; the second could not be reconstructed into the classified failure path that writes a terminal state.
- Resolution: Return applicable=false only for PROJECT_UNSUPPORTED, and classify every other planning failure as QUALITY_GATE_FAILED so the engine records RUN_FAILED and a terminal row.
- Prevention:
  - `test` test_agent_quality_classifies_unsupported_and_failed_plans_without_stranding_run — The activity syntax must carry the explicit unsupported branch and map both known and unexpected planning failures to the Agent Runtime quality-failure taxonomy.
- Evidence: `file:services/orchestrator/src/iacode_orchestrator/agent_runtime/activities.py`, `file:tests/test_gate4_quality_engine.py`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`

### LSN-0090 — A clean-clone control must use only versioned configuration inputs

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-4, GATE-4-CP-0001, finding cmd-0243.
- Symptom: The internal milestone mirror passed every pre-clone dimension but the canonical suite failed in its clean clone because the evaluator compose control required infra/compose/.env, an intentionally ignored workstation file.
- Root cause: The structural compose test selected the developer-local .env even though the repository already carries .env.example with the same closed configuration vocabulary. Green Keeper inherited the local file and could not expose the dependency; a published clone correctly did.
- Resolution: Run the structural compose configuration check with the versioned .env.example and assert that input exists before invoking Docker Compose.
- Prevention:
  - `test` test_the_evaluator_service_has_no_engine_socket_or_host_project_mount — The isolation control resolves Compose exclusively with the versioned .env.example, so it executes identically in a clean clone.
- Evidence: `file:tests/test_gate4_quality_engine.py`, `file:infra/compose/.env.example`, `file:docs/checkpoints/GATE-4-CP-0001/M2-INTERNAL-MIRROR.json`, `file:docs/checkpoints/GATE-4-CP-0001/COMMANDS.jsonl`

### LSN-0091 — Secret detection must run on the exact bytes at the durable evidence boundary

- Status: `GUARDED`, severity CRITICAL, category security, recurrences 1.
- Source: GATE-4, GATE-4-CP-0002, finding G4-F-001.
- Symptom: The independent G4-X7 attack sent a credential-shaped value under an ordinary structured key; normal mapping redaction left it intact and the Quality Engine persisted and resolved the serialized evidence.
- Root cause: Runtime redaction and the canonical repository scanner owned different taxonomies, and the evidence store performed no fail-closed scan of the exact serialized bytes before content-addressed lookup and commit. CP0010 also reproduced JSON newline and Unicode escapes hiding a marker that the same detector recognizes before serialization.
- Resolution: Move the canonical credential-shape taxonomy into the shared common package, scan serialized evidence before every lookup or write, refuse scanner failure, recheck downloaded objects during resolution, and persist only a sanitized ERROR result that derives FAIL.
- Prevention:
  - `test` test_canonical_secret_is_rejected_before_any_durable_operation — A canonical synthetic marker under an ordinary key is refused with zero object and metadata writes.
  - `test` test_secret_bearing_execution_is_contained_and_derives_fail — The exact activity-to-store path terminates as sanitized ERROR and derives FAIL without retaining prohibited bytes.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0002/REVIEW-REPORT.md`, `file:docs/checkpoints/GATE-4-CP-0002/RED-TEAM-REPORT.md`, `file:packages/common/src/iacode_common/secret_scanning.py`, `file:services/evaluator/src/iacode_evaluator/evidence.py`, `file:services/evaluator/tests/test_persistence.py`, `file:services/evaluator/tests/test_workflow.py`, `file:scripts/development-ledger/gate4_red_team.py`, `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:services/sandbox/tests/test_sandbox_service.py`, `file:docs/checkpoints/GATE-4-CP-0010/audit-harness/check_escaped_output.py`

### LSN-0092 — Canonical audit parsers must consume every bounded sealed report rendering

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 0.
- Source: GATE-4, GATE-4-CP-0003, finding cmd-0003.
- Symptom: Requirement derivation refused the sealed Gate 4 audit because its single blocking finding was rendered as a severity-bearing paragraph rather than a level-three finding heading.
- Root cause: The canonical parser recognized earlier plural and singular heading layouts but did not recognize the bounded Blocking finding paragraph used by the new sealed audit.
- Resolution: Parse a severity-bearing backticked finding only inside the exact Blocking finding section, retain the fail-closed empty-parse rule, and test both the sealed report and an identical mention outside the bounded section.
- Prevention:
  - `test` test_a_blocking_finding_paragraph_in_a_sealed_audit_is_parsed — The exact sealed Gate 4 review yields G4-F-001 and HIGH.
  - `test` test_blocking_finding_prose_is_bounded_to_its_section — An identical historical mention outside the finding section is not imported as new corrective work.
- Evidence: `file:scripts/development-ledger/policies.py`, `file:tests/test_development_ledger.py`, `file:docs/checkpoints/GATE-4-CP-0003/COMMANDS.jsonl`

### LSN-0093 — Disposable control repositories must carry every imported repository package

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-4, GATE-4-CP-0003, finding cmd-0022.
- Symptom: The complete verifier reached every product and live scenario successfully, but the root suite failed when copied ledger tools imported iacode_common from disposable repositories that contained only scripts/development-ledger.
- Root cause: The disposable-repository boundary copied executable ledger scripts but did not copy their versioned packages/common runtime dependency after the canonical secret taxonomy moved there.
- Resolution: Centralize fixture installation in copy_ledger_runtime, copy both the ledger scripts and packages/common, and make every isolated test helper use that same source boundary without adding a fallback or a second scanner implementation.
- Prevention:
  - `test` test_disposable_ledger_runtime_carries_its_canonical_scanner_dependency — A disposable ledger installation contains the canonical scanner package and can import a copied ledger entry point in isolation.
  - `test` test_full_delivery_assurance_flow_reaches_ready_for_review — The isolated end-to-end delivery path executes its copied lessons, integrity and checkpoint controls successfully.
- Evidence: `file:scripts/development-ledger/promotion_fixture.py`, `file:tests/test_development_ledger.py`

### LSN-0094 — A review bundle must include unchanged canonical artifact categories

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
- Source: GATE-4, GATE-4-CP-0003, finding cmd-0097.
- Symptom: The deterministic review bundle failed its own category validation because a corrective slice had no changed migrations, schemas, or policies, so those mandatory review surfaces were absent.
- Root cause: Bundle collection equated the Git changeset with the complete review surface even though Gate 4 requires both changed files and canonical migrations, schemas, and policies needed to interpret them.
- Resolution: Include every tracked canonical policy, schema, and migration in the deterministic bundle in addition to the complete checkpoint and changed paths, while keeping the generated changeset truthful about what actually changed.
- Prevention:
  - `test` test_review_context_includes_unchanged_migrations_schemas_and_policies — The collected review context always contains tracked migrations, schemas, and policies even when none changed in the current slice.
  - `automated-check` scripts/development-ledger/review_bundle.py — Bundle validation rejects a package missing any mandatory artifact category and scans the complete payload.
- Evidence: `file:scripts/development-ledger/review_bundle.py`, `file:tests/test_gate4_quality_engine.py`, `file:docs/checkpoints/GATE-4-CP-0003/COMMANDS.jsonl`

### LSN-0095 — A complete verifier must own its Compose runtime by checkout

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-4, GATE-4-CP-0004, finding G4-F-002.
- Symptom: The published detached full verifier completed 42 stages but returned 40/42 because infrastructure and smoke failed only inside the complete ordered run; exact isolated reruns then passed.
- Root cause: Independent checkouts defaulted to the same Compose project, fixed host ports, image tags, volumes, and runtime state, while the stack stage did not require a build. One checkout could therefore observe or replace another checkout's mutable verification environment, and an isolated rerun inherited the converged state.
- Resolution: Derive a stable verification-only Compose project from the checkout path, request Docker-allocated host ports, freeze that environment across all 42 stages, build the full stack before measurement, clean only that owned project before and after the run, and retain failed-stage output tails.
- Prevention:
  - `test` test_full_verification_uses_a_checkout_owned_compose_project_and_dynamic_ports — Distinct checkouts receive distinct verification projects and every published port is Docker allocated.
  - `test` test_each_stage_receives_the_frozen_verification_environment — All stages in one verifier run receive the same immutable ownership environment.
  - `test` test_cleanup_refuses_the_shared_developer_project — Verification cleanup cannot target the default shared developer project.
  - `test` test_live_stack_stage_builds_every_image_before_it_is_exercised — The ordered stack stage builds repository images before any live measurement.
  - `test` test_order_isolation_probe_preserves_the_historical_contiguous_stage_order — The targeted two-cycle probe preserves stack, integration, infrastructure, and smoke order without retrying a failed cycle.
- Evidence: `file:scripts/iacode/verify.py`, `file:scripts/iacode/compose.py`, `file:scripts/iacode/scenarios/verification_order_isolation.py`, `file:tests/test_gate4_quality_engine.py`, `file:docs/adr/ADR-0033-verification-runtime-is-owned-by-one-checkout.md`, `file:docs/checkpoints/GATE-4-CP-0005/ORDER-ISOLATION-PROBE.json`

### LSN-0096 — Evidence publishers must consume the producer's canonical result schema

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
- Source: GATE-4, GATE-4-CP-0005, finding cmd-0052.
- Symptom: The canonical published-clone verifier returned PASS for all 42 stages and performed post-run cleanup, but the checkpoint wrapper reported 0/42 because it read a non-existent status alias from each stage.
- Root cause: The evidence publisher duplicated knowledge of the verifier schema without a behavioral regression and counted stage.status even though the producer's versioned field is stage.result.
- Resolution: Centralize strict stage summarization on the canonical result field, require exactly 42 PASS/FAIL stage results, bind publication PASS to the top-level verifier result and both cleanup results, return nonzero for a failed publication summary, and reconcile cmd-0052 from its preserved clone without rerunning the verifier while accepting no Git delta except that generated report.
- Prevention:
  - `test` test_published_full_verification_counts_the_canonical_result_field — The real checkpoint publisher counts the producer's result field and ignores a contradictory status alias.
  - `test` test_published_report_reconciliation_allows_only_the_generated_report — Reconciliation accepts only the verifier's generated report in the preserved clone and rejects any additional delta.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0005/RUN-PUBLISHED-FULL-VERIFICATION.py`, `file:docs/checkpoints/GATE-4-CP-0005/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0005/PUBLISHED-CLEAN-CLONE-REPORT.json`, `file:tests/test_gate4_quality_engine.py`

### LSN-0097 — A review-bundle declaration must bind an immutable reconstruction subject

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
- Source: GATE-4, GATE-4-CP-0008, finding G4-F-004.
- Symptom: Two valid byte-identical review bundles rebuilt from the final published CP0007 tag did not match the digest or size CP0007 declared before its finalization and seal.
- Root cause: The bundle producer collected a mutable working tree and wrote its declaration before finalization and post-commit sealing changed checkpoint evidence. No immutable reconstruction subject or mandatory declared-versus-rebuilt comparison bound the report to the content it claimed to represent.
- Resolution: Checkpoint schema 3.4 now constructs the review payload only from an immutable Git content commit, excludes exactly the declaration sidecar to break self-reference, reconstructs twice through non-local detached Git transport while sealing, and independently reconstructs twice during validation before accepting the declared digest, size and entry count.
- Prevention:
  - `test` test_immutable_subject_rebuilds_are_byte_identical_and_exclude_only_the_sidecar — Two immutable-subject builds are byte-identical and exclude only the self-referential declaration sidecar.
  - `test` test_declared_digest_and_size_are_rebuilt_not_trusted — Validation rebuilds the subject and refuses a stale declared digest.
  - `test` test_full_delivery_assurance_flow_reaches_ready_for_review — The real seal lifecycle crosses non-local Git transport, records a reconstruction declaration and validates the sealed result.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0008/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0008/SUBJECT-BUNDLE-AUDIT.json`, `file:docs/checkpoints/GATE-4-CP-0008/GATE-4-INDEPENDENT-RED-TEAM.json`, `file:docs/adr/ADR-0035-review-bundles-bind-immutable-content.md`, `file:scripts/development-ledger/review_bundle.py`, `file:scripts/development-ledger/seal_checkpoint.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:tests/test_gate4_quality_engine.py`, `file:tests/test_development_ledger.py`

### LSN-0098 — Accepted cancellation must be enforced from durable state across activity boundaries

- Status: `GUARDED`, severity CRITICAL, category implementation, recurrences 3.
- Source: GATE-4, GATE-4-CP-0009, finding cmd-0023, cmd-0060 and focused diagnostic cmd-0068.
- Symptom: Two complete verifiers observed an accepted quality cancellation remain non-terminal for the full 900-second observation bound. The focused cmd-0068 reproduction proved the run was already CANCELLING when a racing sandbox response completed normally; persisting that success was correctly refused as late, and the workflow never reached terminal cancellation.
- Root cause: The first guard covered one in-memory signal race after CHECK_DISPATCHED but not the whole accepted-cancellation state machine. A flag already set before activity-handle assignment could make the watcher exit without cancelling, and a normal response racing with persisted CANCELLING was recorded before cancellation precedence was applied. The store correctly refused that non-cancelled result, leaving the workflow failed and the run non-terminal.
- Resolution: Treat persisted CANCELLING as authoritative before creation and throughout the activity. Cancel immediately when the flag is already set, poll durable state while waiting, and normalize any normal response that races with accepted cancellation to CANCELLED before persistence; release the sandbox before the terminal transition. Cmd-0071 proved the complete path in a disposable real stack. CP0010 closes result and verdict persistence races with durable reconciliation and a cancellation/verdict commit barrier (ADR-0038).
- Prevention:
  - `test` test_cancellation_is_rechecked_after_dispatch_before_activity_start — The workflow re-reads durable run state after CHECK_DISPATCHED and before workflow.start_activity.
  - `test` test_durable_cancelling_state_stops_an_active_sandbox_activity — A CANCELLING run observed while an activity is in flight cancels that activity even without relying on the signal handler.
  - `test` test_a_signal_flag_set_before_handle_assignment_still_cancels_the_activity — An already accepted signal cannot make the durable watcher exit while leaving the newly assigned activity running.
  - `test` test_accepted_cancellation_wins_over_a_racing_success_response — A normal activity response racing with accepted cancellation is persisted as CANCELLED, never as late success.
  - `test` test_durable_cancellation_during_result_write_finishes_without_a_signal — A database cancellation arriving after the durable read recovers from the rejected result callback, reaches CANCELLED and derives FAIL without a signal.
  - `test` test_concurrent_cancellation_and_verdict_have_one_winner — PostgreSQL serializes cancellation acceptance with immutable verdict commitment under the same run-row lock.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0009/VERIFY-FAIL-CMD-0023.json`, `file:docs/checkpoints/GATE-4-CP-0009/VERIFY-FAIL-CMD-0060.json`, `file:docs/checkpoints/GATE-4-CP-0009/QUALITY-CANCELLATION-ISOLATION-FAIL-CMD-0068.json`, `file:docs/checkpoints/GATE-4-CP-0009/QUALITY-CANCELLATION-GUARDRAIL.json`, `file:docs/checkpoints/GATE-4-CP-0009/QUALITY-CANCELLATION-ISOLATION.json`, `file:docs/checkpoints/GATE-4-CP-0009/COMMANDS.jsonl`, `file:services/evaluator/src/iacode_evaluator/workflow.py`, `file:services/evaluator/tests/test_workflow.py`, `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0010/QUALITY-CANCELLATION-GUARDRAIL.json`, `file:docs/checkpoints/GATE-4-CP-0010/QUALITY-CANCELLATION-ISOLATION.json`

### LSN-0099 — A refused subject is an attempted input, not executed commit evidence

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
- Source: GATE-4, GATE-4-CP-0009, finding cmd-0033-invalid-subject-refusal.
- Symptom: A truthful PRECONDITION_REJECTED record for a mistyped subject commit made CP0009 invalid because replay validation no longer recognized the subject-specific refusal and published-history validation required the deliberately unresolved subject to be reachable.
- Root cause: The recorder resolved caller-supplied subjects before execution, but encoded a subject-resolution failure as a generic command replay refusal. The validator could recompute transport-input refusals only, and its published-history scan treated every commit-shaped field as executed evidence even when the command never ran.
- Resolution: Record subject resolution as its own failed precondition, recompute both old and new subject-refusal records during validation, and exclude PRECONDITION_REJECTED records from the published-history evidence denominator while continuing to validate their refusal semantics.
- Prevention:
  - `test` test_inputs_are_canonicalized_and_an_unknown_subject_is_refused — An unknown subject is refused before execution, its subject-specific precondition is recorded, command validation accepts the truthful refusal, and published-history validation does not treat it as executed evidence.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0009/COMMANDS.jsonl`, `file:scripts/development-ledger/record_command.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:tests/test_gate3_sandbox.py`

### LSN-0100 — Pre-seal detached validation must bind the explicit subject namespace

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
- Source: GATE-4, GATE-4-CP-0009, finding cmd-0060-checkpointValidation.
- Symptom: The exact published CP0009 subject passed its repository tests but checkpoint validation failed because the detached validator required a canonical checkpoint seal tag that correctly did not exist before assurance completed.
- Root cause: Detached validation modeled only sealed checkpoint inspection. The repository had already separated exact pre-seal inputs under iacode-subjects from canonical seals under iacode-checkpoints, but the validator could not express the pre-seal mode and therefore demanded premature seal identity.
- Resolution: Permit a clean detached symbolic-HEAD checkpoint only while it is IN_PROGRESS and only when an exact iacode-subjects tag whose name begins with that checkpoint identifier resolves to the checked-out commit. Every other detached status continues to require the canonical checkpoint tag.
- Prevention:
  - `test` test_in_progress_symbolic_head_validates_from_its_matching_subject_tag — A transported IN_PROGRESS checkpoint validates from its own exact pre-seal subject tag.
  - `test` test_subject_tag_never_substitutes_for_a_sealed_checkpoint_tag — A handoff-ready or sealed checkpoint still requires its canonical checkpoint tag even when an exact subject tag exists.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0009/VERIFY-FAIL-CMD-0060.json`, `file:docs/adr/ADR-0036-pre-seal-validation-binds-an-explicit-subject.md`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:tests/test_development_ledger.py`

### LSN-0101 — A structural record and its canonical index are one atomic change

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
- Source: GATE-4, GATE-4-CP-0009, finding cmd-0083-gate-tests.
- Symptom: The exact published replacement subject passed 41 of 42 verifier stages, but the root test gate failed because ADR-0036 existed without the corresponding canonical ADR index row.
- Root cause: The corrective run created a new structural decision record but treated the record file and its repository index as separate edits. Focused detached-checkpoint tests passed, while the comprehensive ADR enumeration control was not run before publication.
- Resolution: Add ADR-0036 to the canonical ADR index and treat creation, title/status agreement, and index membership as one atomic structural change.
- Prevention:
  - `test` test_the_index_lists_every_record_with_its_title_and_status — The canonical ADR index must list every ADR with the exact title and status parsed from the record.
  - `test` test_a_record_missing_from_the_index_is_detected — A disposable mutation that removes an ADR index row must be detected.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0009/VERIFY-FAIL-CMD-0083.json`, `file:docs/checkpoints/GATE-4-CP-0009/COMMANDS.jsonl`, `file:docs/adr/README.md`, `file:docs/adr/ADR-0036-pre-seal-validation-binds-an-explicit-subject.md`, `file:tests/test_gate3_sandbox.py`

### LSN-0102 — Assurance denominators must derive category counts from the current source set

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 4.
- Source: GATE-4, GATE-4-CP-0009, finding cmd-0112-requirement-completion.
- Symptom: The requirement closer resolved all rows but returned failure because its expected partition still hard-coded eight corrective rows after the current corrective reference set had grown to nine.
- Root cause: The harness maintained the corrective reference set and a duplicate numeric partition literal. Adding a required lesson changed the source set without changing the second representation, so the assurance step rejected its own truthful count.
- Resolution: Strengthen the assertion owner with current canonical mandatory IDs while retaining the immutable minimum/all-mandatory checks. Actual removal, optional downgrade and newly registered growth controls pass cmd-0123; original inherited bookkeeping/quality classes pass cmd-0127. Local executable guard restoration only; the failed immutable runtime-v1 remains FAIL. A new complete immutable invocation and every ordered internal assurance control are still required before readiness; independent M2 validation remains pending.
- Prevention:
  - `test` test_corrective_partition_is_derived_from_the_current_reference_set — Adding a corrective reference changes the expected partition automatically without editing a second count.
  - `test` test_current_collection_partition_survives_added_regression_cases — Execute the actual live partition property in an owned collection fixture, add another regression source and re-execute unchanged; deliberately admit an excluded input to prove rejection.
  - `test` test_current_summary_derives_exact_vocabulary_and_ignores_noncanonical_alias — Execute the strengthened current causal boundary without weakening inherited controls.
  - `test` test_current_summary_refuses_missing_duplicate_reordered_or_unknown_results — Execute the strengthened current causal boundary without weakening inherited controls.
  - `test` test_inherited_gate_assertion_accepts_growth_but_refuses_removal_or_optional_controls — Execute the inherited assertion with legitimate mandatory growth, every inherited removal and every mandatory-flag downgrade.
  - `test` Gate7MandatoryMembershipTests.test_current_quality_guard_refuses_every_canonical_removal_and_optional_downgrade — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
  - `test` Gate7MandatoryMembershipTests.test_quality_guard_consumes_an_added_registered_gate_without_a_second_literal — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0009/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-4-CP-0009/audit-harness/complete_requirements.py`, `file:tests/test_checkpoint_audit_harnesses.py`, `file:tests/test_test_suite_input_repositories.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:tests/test_gate6_experience.py`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:tests/test_gate7_assurance.py`, `file:tests/test_gate7_knowledge.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`

### LSN-0103 — Adversarial fixtures must hash the complete validated contract

- Status: `GUARDED`, severity HIGH, category testing, recurrences 1.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-003.
- Symptom: The new cancellation barrier fixtures were refused for VERDICT_DIGEST_MISMATCH before reaching the intended race.
- Root cause: The fixture digest omitted contractVersion, a default emitted by model validation.
- Resolution: Construct the complete canonical verdict before hashing and execute a valid commitment before attributing a refusal to cancellation.
- Prevention:
  - `test` test_verdict_before_cancellation_refuses_late_acceptance — The positive and negative regression must execute the intended boundary with canonical inputs.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`

### LSN-0104 — Intermediate closure and independent validation must have unambiguous contracts

- Status: `GUARDED`, severity HIGH, category process, recurrences 0.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-002.
- Symptom: Live contracts simultaneously required per-Gate independent approval and allowed internal intermediate closure.
- Root cause: The milestone policy was added without reconciling older entry, handoff and Gate-specific wording.
- Resolution: Keep adapters and live Gate rows aligned with the milestone cadence, preserve internal controls and reject independent verdicts on INTERNAL_GATE_PASS.
- Prevention:
  - `test` test_internal_closure_cannot_claim_independent_review_or_red_team — The positive and negative regression must execute the intended boundary with canonical inputs.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`

### LSN-0105 — New behavioral tests must satisfy the unchanged source-quality contract

- Status: `GUARDED`, severity CRITICAL, category testing, recurrences 15.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-004.
- Symptom: The lint gate refused overlong declarations and expressions in new regression tests.
- Root cause: Behavioral proof was expanded without checking the source formatting budget first.
- Resolution: AUTHORED-STYLE-001 local source correction and publication guard are demonstrated by complete unchanged canonical lint, whole authored quality, actual M2 regressions and inherited lint denominator controls. Historical failures remain. Current-source revalidation after this memory update, whole immutable assurance and independent M2 remain due.
- Prevention:
  - `test` test_mandatory_lint_covers_every_python_project_root — The positive and negative regression must execute the intended boundary with canonical inputs.
  - `test` Gate7LintDenominatorTests.test_inherited_lint_guard_refuses_each_new_python_root_omission — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
  - `automated-check` docs/checkpoints/GATE-7-CP-0001/audit-harness/format_assurance_helpers.py — Execute the unchanged pinned quality rules on all checkpoint helpers and current native/pathspec regression sources; actual cmd0214 passes.
  - `test` PublicationCallerTests.test_actual_publisher_checks_current_lint_before_publication_effects — Actual caller guard or explicitly modeled proof-decision control; live quality is separate.
  - `test` PublicationCallerTests.test_archived_actual_publisher_without_precondition_is_rejected — Actual caller guard or explicitly modeled proof-decision control; live quality is separate.
  - `test` AuthoredQualityDecisionTests.test_modeled_valid_whole_scope_acceptance_has_no_source_effects — Actual caller guard or explicitly modeled proof-decision control; live quality is separate.
  - `test` AuthoredQualityDecisionTests.test_missing_stale_narrowed_format_and_nonzero_proofs_are_refused — Actual caller guard or explicitly modeled proof-decision control; live quality is separate.
  - `test` AuthoredQualityDecisionTests.test_changed_original_bytes_failed_cleanup_and_latest_failure_are_refused — Actual caller guard or explicitly modeled proof-decision control; live quality is separate.
  - `automated-check` docs/checkpoints/GATE-7-CP-0003/audit-harness/authored_python_quality.py — Whole Git-derived active helper/test scope; unchanged pinned Ruff and read-only proof before publication.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/PRE-LIVE-PROGRESS.json`, `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0004.json`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/STYLE-RED-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/STYLE-RED-0001.log`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/STYLE-RED-0002.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/STYLE-RED-0002.log`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/STYLE-RED-0003.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/STYLE-RED-0003.log`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/STYLE-RED-0004.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/STYLE-RED-0004.log`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/ARCHIVE-V1-HELPER-PARSE-RED.py.raw`, `file:tests/test_gate7_assurance.py`, `file:tests/test_gate7_knowledge.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/RUNTIME-V2-FAILED-FULL-MANIFEST.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/CURRENT-REWORK-GATE7-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-LINT-0006.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-HELPER-QUALITY-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-GATE4-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-CONTROLS-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-REWORK-HELPER-QUALITY-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-REWORK-HELPER-QUALITY-0001.log`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-REWORK-ALL-OWNERS-0002.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-REWORK-HELPER-QUALITY-0005.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-LINT-0008.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/helper-quality/run-0001/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/lint/run-0010.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/helper-quality/run-0017/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/all-m2/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/lint-denominator/run-0001.json`

### LSN-0106 — A security repair must execute at the causal output boundary, not a similarly shaped branch

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-007.
- Symptom: A security repair must execute at the causal output boundary, not a similarly shaped branch
- Root cause: An ambiguous patch context placed output containment in workspace provisioning rather than the tool result path; the direct behavioral probes remained red.
- Resolution: Bind changes to the intended function and execute its real positive and negative service/activity paths before claiming the repair.
- Prevention:
  - `test` test_canonical_secret_output_is_rejected_before_durable_delivery — Exercise the real causal boundary with the valid control and the intended adverse input.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:services/sandbox/tests/test_sandbox_service.py`, `file:services/sandbox/tests/test_sandbox_engine_limits.py`

### LSN-0107 — An adversarial marker must satisfy the canonical detector before it can judge containment

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-008.
- Symptom: An adversarial marker must satisfy the canonical detector before it can judge containment; cmd-0059 additionally showed pytest captured the passing fixture's marker before it reached the process output boundary.
- Root cause: The beyond-inline probe concatenated a credential-shaped suffix directly to word characters, so the canonical word-boundary precondition was false and the test reported an unrelated failure.
- Resolution: Prove the generated adverse bytes are recognized by the canonical detector before judging rejection, and retain a clean positive path through the identical execution. Emit at process exit outside pytest capture, then prove the real workflow fails and decoded Temporal payloads and object storage contain no marker.
- Prevention:
  - `test` test_live_secret_beyond_inline_limit_creates_no_full_output_artifact — Exercise the real causal boundary with the valid control and the intended adverse input.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:services/sandbox/tests/test_sandbox_service.py`, `file:services/sandbox/tests/test_sandbox_engine_limits.py`

### LSN-0108 — Evidence timestamp transport must preserve RFC3339 rather than a shell locale rendering

- Status: `GUARDED`, severity LOW, category process, recurrences 0.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-009.
- Symptom: Cmd-0056 refused a guardrail observation whose RFC3339 timestamp had been auto-converted and locale-rendered by the shell.
- Root cause: A shell JSON round-trip changed a canonical timestamp's type before the new lesson copied it.
- Resolution: Read the raw command record as JSON and preserve its exact timestamp; validate lesson datetime fields and reject locale renderings before evidence publication.
- Prevention:
  - `test` test_lesson_timestamp_transport_rejects_locale_rendering — Execute the real positive control and reject the observed invalid input without weakening policy.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:services/sandbox/tests/test_sandbox_service.py`, `file:services/sandbox/tests/test_sandbox_engine_limits.py`

### LSN-0109 — Regression counts and evidence must exclude only policy-bound live input repositories

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-010.
- Symptom: Static discovery counted 90 evaluator cases while the runner collected 85; five live input-project tests were never part of evaluator collection.
- Root cause: The static counter and test-reference resolver ignored the runner's pre-existing fixtures collection exclusion.
- Resolution: Declare input repositories in canonical policy with reasons and require exact agreement with literal pytest collection; use one boundary for counts and evidence while retaining every mandatory live scenario.
- Prevention:
  - `test` test_only_declared_runner_exclusions_leave_both_count_and_evidence — Execute the real positive control and reject the observed invalid input without weakening policy.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:services/sandbox/tests/test_sandbox_service.py`, `file:services/sandbox/tests/test_sandbox_engine_limits.py`

### LSN-0110 — A timed-out live proof retains bounded diagnostics before owned cleanup

- Status: `GUARDED`, severity CRITICAL, category testing, recurrences 2.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-012.
- Symptom: Cmd-0066 timed out in its clean control before writing the scenario report; mandatory cleanup then removed the ephemeral history.
- Root cause: The proof let a terminal-wait exception bypass its structured failure report and pre-cleanup observer.
- Resolution: Actual cmd-0195 retains the failed native mode and bounded phase/count/deadline facts while the drain stays FAIL; no inner child PASS is consumed. Cmd-0211 passes red-diagnostic/late-signal controls, cmd-0213 all152 owning root cases, cmd-0214 explicit helper quality and cmd-0215 whole unchanged lint. Every earlier quality-observer control remains. Native physical reliability and whole immutable acceptance are separate.
- Prevention:
  - `test` test_live_output_control_timeout_retains_bounded_diagnostics_and_stays_red — Inject a control timeout into the actual scenario entry point and require a red diagnostic report without starting adverse inputs.
  - `test` Gate7QualityObservationTests.test_iacode_wait_timeout_is_red_and_captures_only_closed_runtime_facts — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7QualityObservationTests.test_late_successful_diagnostic_never_promotes_the_expired_wait — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7QualityObservationTests.test_timeout_projection_refuses_malformed_private_and_excessive_metadata — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7QualityObservationTests.test_timeout_projection_follows_all_canonical_closed_states_and_result_statuses — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7QualityObservationTests.test_iacode_timeout_remains_red_if_its_diagnostic_dependency_is_unavailable — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7QualityObservationTests.test_actual_iacode_entrypoint_writes_a_red_timeout_report_before_owned_cleanup — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7NativeCleanupTests.test_deadline_retains_red_bounded_physical_facts — Executed current positive/adverse boundary; whole immutable acceptance and independent M2 review remain separate.
  - `test` Gate7NativeCleanupTests.test_native_run_keeps_drain_failure_red_even_with_a_child_pass_report — Executed current positive/adverse boundary; whole immutable acceptance and independent M2 review remain separate.
  - `test` Gate7NativeCleanupTests.test_failed_physical_wait_never_becomes_success_or_exposes_exception_body — Executed current positive/adverse boundary; whole immutable acceptance and independent M2 review remain separate.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:services/sandbox/tests/test_sandbox_service.py`, `file:services/sandbox/tests/test_sandbox_engine_limits.py`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/RUNTIME-V2-FAILED-FULL-MANIFEST.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/CURRENT-REWORK-GATE7-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-LINT-0006.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-HELPER-QUALITY-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-GATE4-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-CONTROLS-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/NATIVE-REWORK-CONTEXT.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/RUNTIME-V3-FAILED-FULL-MANIFEST.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-REWORK-ALL-OWNERS-0002.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-REWORK-HELPER-QUALITY-0005.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-LINT-0008.json`

### LSN-0111 — Polling watcher cleanup must preserve completed checks and accepted cancellation

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-013.
- Symptom: A completed check can abort when its polling read is cancelled, and an accepted cancellation read can dereference a handle cleared during its await.
- Root cause: Watcher cleanup assumed only asyncio cancellation and assumed the active handle survived a durable read. The pinned SDK can return typed activity cancellation instead.
- Resolution: Accept typed activity cancellation only when this cleanup requested it, propagate unrelated and precompleted failures, and recheck active handle lifetime after durable reads without losing the accepted cancellation flag.
- Prevention:
  - `test` test_completed_check_joins_cancelled_durable_read_without_cancelling_run — Complete the real workflow adapter while its polling read is pending, preserving normal result/verdict commitment.
  - `test` test_unrelated_watcher_failure_is_not_hidden_by_join_cleanup — An unrelated read failure still propagates rather than becoming a successful check.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:services/sandbox/tests/test_sandbox_service.py`, `file:services/sandbox/tests/test_sandbox_engine_limits.py`, `file:docs/checkpoints/GATE-4-CP-0010/V1-POLLING-FAILURE.json`

### LSN-0112 — Canonical scanner consumers must share transport decoding, not only patterns

- Status: `GUARDED`, severity HIGH, category security, recurrences 0.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-014.
- Symptom: Publication scanning missed nested JSON markers that the runtime detector rejected, and an approved raw value could mask another encoded value of the same kind.
- Root cause: The publication scanner reused SECRET_PATTERNS but scanned only raw text, bypassing the shared transport interpretation.
- Resolution: Use the identical bounded in-memory transport views for runtime and publication, retain exact component-digest review, never expose values, and keep raw/encoded clean and negative controls.
- Prevention:
  - `test` PublicationTransportScanningTests — Execute the causal positive and negative controls without reducing canonical membership or approval rules.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`

### LSN-0113 — Stronger delivery controls must follow the immutable subject policy version

- Status: `GUARDED`, severity CRITICAL, category checkpoint, recurrences 1.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-015.
- Symptom: A current internal-verdict guard invalidated sealed historical checkpoints whose Red Team field had a different declared meaning.
- Root cause: The new invariant was applied unconditionally rather than being bound to the subject's governance policy.
- Resolution: Bind every evolving invariant to the immutable subject's declared policy version: strict internal verdicts under memory policy 2.4.0, collection boundaries under test-suite policy 1.1.0. Keep legacy semantics, refuse current downgrades/new fields under old versions, and execute current validation over every canonical sealed anchor.
- Prevention:
  - `test` test_live_policy_requires_strict_internal_verdict_semantics — Execute the causal positive and negative controls without reducing canonical membership or approval rules.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`

### LSN-0114 — Transport line metadata must not repeatedly scan the source prefix

- Status: `GUARDED`, severity MEDIUM, category performance, recurrences 0.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-018.
- Symptom: A JSONL carrier-line regression examined 100368 source characters for a 1002-character input while preserving the expected credential finding and its line.
- Root cause: Both fragment carrier accounting and JSONDecodeError coordinate construction rescanned prefixes, outside the decoder-work bound. Fixing carrier accounting alone left 20664 characters of decoder metadata work for the same 1002-character input.
- Resolution: Count carrier newlines incrementally and index newline positions lazily only for JSON parser metadata. Preserve original yielded text, decoder messages/positions/line coordinates, traversal and fail-closed budgets.
- Prevention:
  - `test` test_fragment_carrier_lines_count_each_source_range_at_most_once — Measure actual source ranges examined, retain the encoded refusal and exact carrier line, and require aggregate line-count work no larger than the input.
  - `test` test_json_error_line_index_matches_builtin_string_coordinates — Prove indexed count/rfind and JSON error coordinates equal builtin strings, including Unicode and slice boundaries.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`

### LSN-0115 — A failing full verifier retains every bounded case identifier beyond its output tail

- Status: `GUARDED`, severity MEDIUM, category tooling, recurrences 0.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-020.
- Symptom: The full v2 root stage reported ten failures, but the retained 25-line output tail omitted earlier failed-case identifiers, preventing immediate cause attribution.
- Root cause: Human-oriented tail capture was the only durable failed-stage diagnostic; no separate bounded identifier set survived long summaries.
- Resolution: Retain bounded unittest/pytest failure identifiers separately from raw output tails, excluding parameter values and message bodies, while keeping the actual child exit code authoritative.
- Prevention:
  - `test` test_failed_case_identifiers_survive_a_tail_longer_than_the_report_limit — Execute real failing child processes with an early failure and more than 25 later lines; preserve identifiers and test payload exclusion and successful-child refusal.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/attempts/published-v2/VERIFY.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`

### LSN-0116 — A live resumability pointer is generated after Git boundaries, not committed into its own subject

- Status: `GUARDED`, severity CRITICAL, category tooling, recurrences 1.
- Source: GATE-4, GATE-4-CP-0010, finding G4-INT-025.
- Symptom: The current program-state command refuses missing current steps and the committed observation points to an old checkpoint and SHA.
- Root cause: The live pointer was versioned as ordinary repository content, making its exact HEAD self-referential; newer checkpoints and internal closure statuses were not integrated into its producer.
- Resolution: Canonical policy generates schema 1.1 exact-Git observations in ignored var/program-state.json, with explicit regeneration, strict latest-step identity and staleness refusal. Legacy storage/status semantics and the tracked historical snapshot are preserved.
- Prevention:
  - `test` test_real_cli_roundtrip_is_clean_and_supports_internal_closure — Actual subprocesses and Git prove clean live generation, supported internal status, staleness/identity refusal, unsafe-target refusal and unchanged legacy semantics.
- Evidence: `file:docs/checkpoints/GATE-4-CP-0010/FINDINGS.json`, `file:docs/checkpoints/GATE-4-CP-0010/COMMANDS.jsonl`, `file:scripts/development-ledger/program_state.py`, `file:tests/test_program_state_live.py`, `file:.iacode/policies/program-state.json`, `file:docs/adr/ADR-0045-live-program-state-is-generated-after-git-boundaries.md`

### LSN-0117 — An architecture rollup must not contradict the delivered capability described below it

- Status: `GUARDED`, severity CRITICAL, category documentation, recurrences 2.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-002.
- Symptom: The current-state overview denied the Quality Engine that a later section of the same architecture document described.
- Root cause: An overview enumerating delivered capabilities was not updated when the detailed quality-runtime architecture was added.
- Resolution: Restore every registered mandatory gate ID in DEVELOPMENT.md without freezing lifecycle status. Current omission/growth controls pass cmd-0123 and unchanged inherited Gate2/Gate3 documentation classes pass cmd-0127; older README rollup controls remain. Local executable guard restoration only; the failed immutable runtime-v1 remains FAIL. A new complete immutable invocation and every ordered internal assurance control are still required before readiness; independent M2 validation remains pending.
- Prevention:
  - `test` test_architecture_rollup_does_not_deny_its_delivered_quality_engine — Compare the actual delivered evaluator and architecture detail with the current-state rollup, retaining the original causal red assertion.
  - `test` test_live_delivery_status_is_delegated_instead_of_hardcoded_in_rollups — Require live lifecycle status to be delegated to the canonical checkpoint and prove that an injected stale WIP label is detected without loosening the existing delivered-capability assertion.
  - `test` Gate7RollupTests.test_current_rollups_do_not_deny_the_owned_capabilities — Derive the current Gate and owned capability titles from canonical repository state and inspect actual README/architecture rollups.
  - `test` Gate7RollupTests.test_rollup_guard_has_positive_and_each_missing_denied_stale_mutation — Execute clean, omitted-capability, future-denial, frozen-status and missing-live-owner controls.
  - `test` Gate7RollupTests.test_original_published_readme_is_a_real_causal_negative_not_a_rewritten_fixture — Bind the original README observation to the actual published Git object and retain its causal denial as raw data.
  - `test` Gate7DocumentationAndStreamsTests.test_development_documents_every_current_gate_and_registered_growth — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:tests/test_gate5_clients.py`, `file:docs/ARCHITECTURE.md`, `file:START-HERE.md`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/README-ROLLUP-0001.json`, `file:tests/test_gate7_knowledge.py`, `file:tests/test_gate7_assurance.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`

### LSN-0118 — Post-response validation failures must preserve an accepted mutation's uncertain outcome

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-004.
- Symptom: A signed malformed result was correctly refused but the client error lost the fact that the remote mutation may already have happened and omitted its stable retry identity.
- Root cause: Transport failures carried mutation context, while semantic response validation happened after the exchange resolved and constructed a new context-free error.
- Resolution: The shared client retains exchange/mutation context through semantic refusal. Cmd-0066 passed all 26 current Node cases, including both clients' decision controls; cmd-0062 and cmd-0067 executed the canonically resolvable Python guard and its actual causal Node case. Whole-delivery and live cross-client assurance remain separate pending requirements.
- Prevention:
  - `test` test_signed_malformed_mutation_keeps_uncertainty_identity_and_one_effect — Execute the real signed-malformed-mutation Node socket case through the counted Python suite; assert exactly one case ran, its uncertainty and original identity survive, and no retry occurred.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/attempts/CLIENT-CORE-RED-0001.json`, `file:apps/cli/src/client.cjs`, `file:apps/cli/tests/core.test.cjs`

### LSN-0119 — A clean publication scan does not replace the stricter checkpoint secret scan

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 4.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-003.
- Symptom: The publication tree scan was clean after exact code-reference review, but actual checkpoint validation still refused the same five source files.
- Root cause: Publication review allowances were incorrectly assumed to apply to the checkpoint's deliberately strict raw canonical detection boundary.
- Resolution: G7-INT-006: complete the source-only Lexeme alias rename, preserving type bounds and wire schema. Preserve incomplete first correction cmd-0053 (30 pass/two fail/schema refused). Cmd-0052 passes all four unchanged strict/publication causal cases; cmd-0055 passes33 complete owning domain/schema cases including all-owned-model rebuild and unresolved-reference adverse proof. Actual canonical IN_PROGRESS finalizer cmd-0061 exits0 with unchanged strict detection. No scanner, allowance or secret type is relaxed. Whole delivery assurance remains due.
- Prevention:
  - `test` test_strict_checkpoint_sources_do_not_rely_on_publication_allowances — Run the unchanged strict canonical detector over the five changed authentication sources, retain a generated adverse-value control and never consult publication allowances.
  - `test` test_desktop_credential_remains_a_secret_type_and_safe_dump_redacts_it — Construct the actual Settings and prove the credential is still a real Pydantic SecretStr and safe_dump never emits its value.
  - `test` test_every_current_changed_path_uses_the_strict_detector_including_checkpoint_harnesses — Scan the actual Git delta against its checkpoint base, including every new checkpoint harness and undeclared untracked text path, with unchanged strict detection and no publication allowances.
  - `test` test_every_owned_wire_model_resolves_annotations_and_unresolved_control_is_refused — Rebuild every owned actual wire model and schema after a naming correction; an unresolved annotation must refuse, so a source-only rename cannot leave lazy broken contracts.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/attempts/SOURCE-SCAN-REVIEW-PRE-REFACTOR.json`, `file:tests/test_gate5_clients.py`, `file:apps/api/tests/unit/test_desktop_api.py`, `file:docs/checkpoints/GATE-6-CP-0001/STRICT-MEMORY-FINDING.json`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/STRICT-RED-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/STRICT-RED-0001.log`

### LSN-0120 — Native installation proofs must resolve the installed CLI entrypoint

- Status: `GUARDED`, severity MEDIUM, category quality, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-005.
- Symptom: The native VSIX installation attempt opened the graphical process and timed out with zero editor tests.
- Root cause: The harness assumed Code.exe directly executed CLI installation and guessed an extracted metadata filename instead of observing the installed code.cmd and package layout.
- Resolution: Resolve the actual installed CLI adapter, verify its contained cli.js path, use Electron node mode for installation only and inspect the actual extracted package identity. Cmd-0065 passed two fresh isolated native profiles and cmd-0067 passed versioned-layout/escape/unsupported-layout controls.
- Prevention:
  - `test` test_installed_cli_adapter_resolves_versioned_layout_and_refuses_escape — Prove the real adapter resolver accepts a versioned installation and refuses an escaping or unsupported script path; actual native installation remains a separate mandatory proof.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:scripts/iacode/native_editor.py`, `file:tests/test_gate5_clients.py`

### LSN-0121 — Standard-library host probes must not initialize application dependency graphs

- Status: `GUARDED`, severity MEDIUM, category quality, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-007.
- Symptom: The desktop live-proof harness failed during import, before creating any owned stack, because reading a protocol constant initialized the application's Pydantic-dependent package.
- Root cause: A dependency-free JSON contract module was imported through a package initializer that also eagerly imports third-party application contracts.
- Resolution: The host probe reads the exact canonical JSON file directly and keeps only pure cryptographic helpers. Cmd-0078 passed actual -I -S host cold startup and the adverse application-import premise without installing host dependencies.
- Prevention:
  - `test` test_live_desktop_harness_cold_start_needs_only_the_standard_library — Execute the real harness --help under isolated Python -I -S, then prove the prior package-import path requires the unavailable application dependency.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:scripts/iacode/desktop_test_support.py`, `file:tests/test_gate5_clients.py`

### LSN-0122 — Engine-allocated host ports must be rediscovered after container restart

- Status: `GUARDED`, severity MEDIUM, category environment, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-008.
- Symptom: A healthy restarted API refused the test actor's former host endpoint after the real initial client/security controls passed.
- Root cause: The harness froze a daemon-allocated zero host port across restart. The actual engine assigned a different port to the same restarted container; this was endpoint identity change, not broken forwarding.
- Resolution: Cmd-0084 proves actual published port change with working HTTP at both identities and owned cleanup. The test actor now rediscovers the published endpoint after restart, explicitly updates its configuration before mutation and verifies authenticated host reachability. Cmd-0086 passes transport-only transient readiness and immediate typed-authentication-refusal controls.
- Prevention:
  - `test` test_restarted_api_rediscovers_its_port_and_checks_actual_authenticated_forwarding — Derive the current published endpoint, prove a transient socket refusal can recover, and prove an actual authentication refusal is not retried or reclassified as readiness.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/attempts/DESKTOP-LIVE-RED-0001.json`, `file:scripts/iacode/desktop_test_support.py`, `file:tests/test_gate5_clients.py`

### LSN-0123 — Consent binds workspace identity, not an uncanonicalized path spelling

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-010.
- Symptom: The native snapshot command refused before approval even after a valid preview. A canonical filesystem root spelling differed from the selected editor fsPath spelling while both named the same workspace.
- Root cause: The preview cached a canonical root and the editor compared it directly with an uncanonicalized fsPath rather than binding the preview to the actual selected workspace identity.
- Resolution: Bind the preview to the selected URI and generation, then require the re-read canonical root and exact manifest digest to remain unchanged. Cmd-0094 passes all 27 client cases; cmd-0095 executes the actual canonical-root Node case through a resolvable Python guard. Actual native/live acceptance remains separately pending.
- Prevention:
  - `test` test_editor_preview_binding_uses_workspace_identity_not_path_spelling — Execute the actual canonical-root alias case through the counted Python suite, assert one Node case really ran, and retain stale folder/trust and exact canonical-root/digest controls.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/attempts/DESKTOP-LIVE-RED-0002.json`, `file:apps/vscode-extension/src/extension.cjs`, `file:apps/vscode-extension/tests/extension.test.cjs`, `file:tests/test_gate5_clients.py`

### LSN-0124 — Durable editor recovery must not use an in-memory test host

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-011.
- Symptom: The second real editor host could not recover the pending identity after an accepted interrupted create in the first host.
- Root cause: The harness supplied extensionTestsPath; the installed Code source explicitly uses in-memory storage for that test context.
- Resolution: Use an ordinary isolated development host with a separate acceptance driver and the unchanged production VSIX. Keep real SecretStorage/workspaceState and the original recovery assertions. Cmd-0101 confirms the actual installed switch; cmd-0102 exercises the launch guard. Full provider recovery remains pending.
- Prevention:
  - `test` test_native_recovery_proof_uses_persistent_storage_context — Require a persistent native launch context, refuse extensionTestsPath and refuse an absent native report rather than manufacturing PASS.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:scripts/iacode/native_editor.py`, `file:tests/test_gate5_clients.py`

### LSN-0125 — Native parent exit is not proof of process and profile cleanup

- Status: `GUARDED`, severity CRITICAL, category environment, recurrences 4.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-012.
- Symptom: Both native cases passed but deleting their owned profiles raised a Windows dictionary sharing violation.
- Root cause: Parent exit and zero job active accounting do not establish signaled completion of owned descendants. Actual Gate6 cmd-0274 pins a verified owned member still nonsignaled after old close returns zero; cleanup failure facts were also lost when context exit raised. The exact historical log holder is not retroactively established.
- Resolution: The new checkpoint bootstrap now invokes the existing exact owned Job runner. Actual caller/preimage/surviving-writer controls pass, and live same60-second bootstrap exits0 with independent cleanup PASS. Preserve the original240210ms timeout and pinned helper-only recovery. Current complete immutable assurance and independent M2 remain due.
- Prevention:
  - `test` test_native_process_tree_is_drained_even_after_parent_exits — Launch an actual surviving child and observe exact owned job cleanup after its parent exits.
  - `test` test_owned_profile_cleanup_refuses_broad_targets_and_retries_only_sharing_locks — Refuse broad targets, execute a sharing-lock retry and propagate other removal errors without retry.
  - `test` test_native_installer_and_host_both_pin_their_owned_shared_storage — Require explicit owned shared-data-dir on installation and host launch; absent actual storage observations never establish a native PASS.
  - `test` test_zero_job_accounting_does_not_replace_observed_member_completion — Require synchronization after zero accounting while an observed owned handle remains nonsignaled.
  - `test` test_unsignaled_owned_member_cannot_be_reported_as_drained_at_deadline — Refuse completion at the unchanged ten-second deadline and close owned handles.
  - `test` test_owned_job_snapshot_refuses_truncation_and_process_identity_reuse — Refuse incomplete snapshots or foreign/reused process identities without termination authority.
  - `test` test_owned_cleanup_failure_retains_observed_facts_and_original_error — Retain retries, elapsed time and the original typed removal error on failure.
  - `test` test_owned_cleanup_success_records_real_removal_and_retry — Observe actual fixture deletion after a retry rather than equating parent exit with removal.
  - `test` test_native_cleanup_failure_report_never_promotes_functional_fixture_pass — Keep the native verdict FAIL when both functional fixture cases pass but removal fails.
  - `test` Gate7NativeCleanupTests.test_natural_physical_completion_precedes_force_inside_original_deadline — Executed owned native boundary; no extra termination authority, deadline widening or independent verdict.
  - `test` Gate7NativeCleanupTests.test_forced_fallback_pins_late_members_without_extending_deadline — Executed owned native boundary; no extra termination authority, deadline widening or independent verdict.
  - `test` Gate7NativeCleanupTests.test_physical_signal_observed_after_total_deadline_remains_fail — Executed owned native boundary; no extra termination authority, deadline widening or independent verdict.
  - `test` Gate7NativeCleanupTests.test_failed_force_snapshot_stays_red_and_releases_original_handles — Executed owned native boundary; no extra termination authority, deadline widening or independent verdict.
  - `test` Gate7NativeCleanupTests.test_real_owned_member_premise_and_natural_exit_preserve_outside_sentinel — Executed owned native boundary; no extra termination authority, deadline widening or independent verdict.
  - `test` Gate7NativeCleanupTests.test_owned_bootstrap_disables_external_reporting_not_native_or_trust_controls — Executed owned native boundary; no extra termination authority, deadline widening or independent verdict.
  - `test` BootstrapOwnershipTests.test_actual_bootstrap_caller_requires_owned_native_process_boundary — Guard the actual bootstrap caller and archived adverse preimage; real Windows surviving-writer null proves exact owned cleanup without Engine operations.
  - `test` BootstrapOwnershipTests.test_archived_actual_preimage_is_rejected_by_identical_caller_guard — Guard the actual bootstrap caller and archived adverse preimage; real Windows surviving-writer null proves exact owned cleanup without Engine operations.
  - `test` BootstrapOwnershipTests.test_real_parent_exit_with_inherited_output_writer_is_observed_then_exactly_drained — Guard the actual bootstrap caller and archived adverse preimage; real Windows surviving-writer null proves exact owned cleanup without Engine operations.
  - `test` BootstrapOwnershipTests.test_actual_history_query_requires_the_same_owned_native_boundary — Actual current caller/document and exact original adverse controls; no template or budget reduction.
  - `test` BootstrapOwnershipTests.test_exact_published_history_preimage_is_rejected_by_the_same_guard — Actual current caller/document and exact original adverse controls; no template or budget reduction.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:scripts/iacode/native_process.py`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/RUNTIME-V5-ASSURANCE-RED-TEAM-NATIVE.json`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/RUNTIME-V5-ASSURANCE-RED-TEAM-EXECUTIONS.json`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:tests/test_gate6_experience.py`, `file:docs/adr/ADR-0052-native-cleanup-failures-retain-observed-diagnostics.md`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/NATIVE-JOB-COMPLETION-0001.json`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/NATIVE-COMPLETION-PROOF-0001-RECEIPT.json`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/NATIVE-COMPLETION-PROOF-0002-RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0001/NATIVE-REWORK-CONTEXT.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/RUNTIME-V3-FAILED-FULL-MANIFEST.json`, `file:docs/checkpoints/GATE-7-CP-0001/NATIVE-REWORK-CONTEXT-02.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-LATE-SUCCESS-CAUSAL-RED-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-LIFECYCLE-COMPLETE-0003.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-UNINSTRUMENTED-REPETITION-0002.json`, `file:docs/adr/ADR-0060-native-drain-allows-natural-exit-within-the-existing-deadline.md`, `file:docs/checkpoints/GATE-7-CP-0003/INTERNAL-ENVIRONMENT-REWORK.json`, `file:docs/checkpoints/GATE-7-CP-0003/resource-phases/phase-0002/BUILDER-BOOTSTRAP.json`, `file:docs/checkpoints/GATE-7-CP-0003/raw-preimages/BOOTSTRAP-DRAIN-001-current-resources.py`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bootstrap-ownership/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bootstrap-ownership/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/resource-phase/run-0004.json`, `file:docs/checkpoints/GATE-7-CP-0003/resource-phases/phase-0002/BUILDER-BOOTSTRAP-RETRY-0001.json`

### LSN-0126 — Known authentication material is not domain or presentation data

- Status: `GUARDED`, severity CRITICAL, category security, recurrences 1.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-015.
- Symptom: The API guard missed encoded capability forms; the full suite retained one failing boundary case.
- Root cause: Canonical JSON views decode JSON transport, not arbitrary base64, percent or literal Unicode-escape encodings. Shape detection alone cannot recognize a bare known capability.
- Resolution: Keep canonical taxonomy unchanged and separately refuse the configured capability and closed encoded forms before replay/domain IO and client approval/presentation. Cmd-0131 passes all 165 API cases; cmd-0133 passes all 34 client cases, including signed post-effect refusal preserving uncertainty and an offline preview guard.
- Prevention:
  - `test` test_authentication_material_is_refused_before_replay_and_domain_io — Exercise raw/case/base64/percent/literal-Unicode forms through actual authenticated ASGI, assert zero replay/domain IO and no returned value, then authenticate a clean request.
  - `test` test_known_opaque_capability_refused_in_declared_forms — Current strengthened causal boundary; every original control remains.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:apps/api/tests/unit/test_desktop_api.py`, `file:apps/api/src/iacode_api/middleware/desktop_auth.py`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/PRE-LIVE-PROGRESS.json`, `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0004.json`

### LSN-0127 — Fresh runtime health does not initialize an operator-managed model catalog

- Status: `GUARDED`, severity HIGH, category environment, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-016.
- Symptom: Real native recovery passed, but the first provider task failed NO_CANDIDATE against a healthy fresh runtime with zero catalog models.
- Root cause: The isolated proof created empty persistence and omitted the existing explicit operator catalog synchronization prerequisite. Process health and authenticated catalog access do not imply model availability.
- Resolution: Synchronize the requested provider explicitly, then require the exact already-authorized active model. Do not change model, provider, client IPC or production routing. Cmd-0154 proves actual hardened worker synchronization, 135 discovered models, the authorized model present and successful provider inference; cmd-0156/0158 prove executable failure/no-substitution controls.
- Prevention:
  - `test` test_fresh_catalog_requires_sync_and_the_exact_authorized_model_without_substitution — Require explicit sync before listing; accept only the exact authorized active model and refuse synchronization failure or a missing model without fallback.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/HARDENED-GATEWAY.json`, `file:scripts/iacode/desktop_test_support.py`, `file:tests/test_gate5_clients.py`

### LSN-0128 — Adversarial premises must use the actual public contract

- Status: `GUARDED`, severity CRITICAL, category testing, recurrences 3.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-017.
- Symptom: After complete native provider/sandbox/quality success, the forgery test failed before reaching the API because it indexed a non-public executor field.
- Root cause: The harness assumed infrastructure ownership metadata was exposed in ToolRequestView instead of using the public request identifier and actual ToolExecutionView evidence.
- Resolution: Use actual ready bytes, nonempty observed exact Job membership and an independently owned outside sentinel, never an exact guessed count. The actual Win32 positive/control case passes cmd-0211 and complete152-owner cmd-0213. Original pre-target failure has no separately logged failing subcondition, which is not invented. All prior public-contract and archive-premise controls remain.
- Prevention:
  - `test` test_forgery_premise_joins_public_request_ids_to_actual_successful_sandbox_executions — Derive public fields from the actual contract, reproduce the old missing-field expression, select only an executed public identity and refuse an absent successful sandbox premise.
  - `test` test_cleanup_membership_derives_every_canonical_active_state_including_running — Read all canonical active states without application initialization; require RUNNING and STOPPING membership, reject the old guessed set and prove membership grows with a new canonical active state.
  - `test` Gate7QualityObservationTests.test_owned_archive_premise_is_populated_before_observer_target — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7NativeCleanupTests.test_real_owned_member_premise_and_natural_exit_preserve_outside_sentinel — Executed current positive/adverse boundary; whole immutable acceptance and independent M2 review remain separate.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/attempts/DESKTOP-LIVE-RED-0006.json`, `file:scripts/iacode/scenarios/desktop_e2e.py`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/RUNTIME-V2-FAILED-FULL-MANIFEST.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/CURRENT-REWORK-GATE7-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-LINT-0006.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-HELPER-QUALITY-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-GATE4-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-CONTROLS-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/NATIVE-REWORK-CONTEXT.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/RUNTIME-V3-FAILED-FULL-MANIFEST.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-REWORK-ALL-OWNERS-0002.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/NATIVE-REWORK-HELPER-QUALITY-0005.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-LINT-0008.json`

### LSN-0129 — Repeated cancellation must preserve an already cancelled terminal result

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-019.
- Symptom: The real desktop proof reached task cancellation and received INVALID_STATE_TRANSITION; a causal store test separately reproduced refusal when repeating cancellation of CANCELLED.
- Root cause: The store rejected every terminal state uniformly, although observing an already CANCELLED result is an idempotent no-op rather than a transition.
- Resolution: Return unchanged CANCELLED truth without writing fields; continue refusing SUCCEEDED/FAILED and mark only the request flag for RUNNING. Cmd-0184 retains one causal failure with 199 other cases passing; cmd-0185 passes all 200 unchanged/added cases after the minimal correction.
- Prevention:
  - `test` test_repeated_cancel_of_cancelled_run_returns_unchanged_terminal_truth — Execute the actual store method with explicit transaction/row doubles, require an unchanged CANCELLED record and retain success/failure refusal plus requested-not-completed controls.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/attempts/DESKTOP-LIVE-RED-0007.json`, `file:services/agent-runtime/tests/test_cancellation_store.py`, `file:services/agent-runtime/src/iacode_agent_runtime/persistence.py`

### LSN-0130 — Executable export line endings belong to the source and packaging contract

- Status: `GUARDED`, severity HIGH, category quality, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-021.
- Symptom: Current Git attributes left CommonJS EOL unspecified and the deterministic builder accepted a CRLF executable shebang.
- Root cause: New executable suffixes were not included in the repository LF policy; two builds in one checkout cannot reveal platform-dependent checkout conversion.
- Resolution: Declare LF for CommonJS/ESM and reject CR bytes in executable inputs without silently rewriting packaged source. Cmd-0192 retains both causal failures; cmd-0193 passes all 29 root controls and cmd-0194 all 35 complete client cases plus deterministic packages.
- Prevention:
  - `test` test_commonjs_and_esm_exports_have_explicit_lf_attributes — Ask actual Git attributes for CommonJS/ESM EOL, rather than assuming checkout behavior.
  - `test` test_builder_refuses_a_crlf_executable_instead_of_shipping_a_broken_linux_shebang — Present an actual owned CRLF executable to the production closed-map reader and require refusal.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:.gitattributes`, `file:scripts/iacode/build_clients.py`, `file:tests/test_gate5_clients.py`

### LSN-0131 — Raw evidence digests require byte-preserving Git export, not text normalization

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 3.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-022.
- Symptom: Before publication, the staged actual desktop report lost CR bytes and no longer matched the archived observation's raw SHA-256.
- Root cause: Dedicated byte-exact copied observations inherited the generic JSON text/LF policy; local copy equality did not prove Git export equality.
- Resolution: Generic canonical original-observation family attributes now protect current and later auditor checkpoints. Three actual Git controls and206 exact staged original comparisons pass. All recurrences, failed attempts and the canceled incomplete quality run remain; complete immutable assurance is still pending.
- Prevention:
  - `test` test_exact_byte_evidence_survives_git_transport_and_detects_normalization — A real isolated Git repository must retain exact CRLF observation bytes; generic text normalization must demonstrably change them, and restoration must recover equality.
  - `test` Gate6BookkeepingCausalTests.test_actual_captured_output_hashes_and_git_attributes_preserve_bytes — Every archived manifest member, including Markdown/Python, retains its original digest and explicit non-text Git attribute.
  - `validator` docs/checkpoints/GATE-6-CP-0001/audit-harness/verify_evidence_transport.py — Compare every manifest member and original producer to its actual index bytes before publication.
  - `test` M2ObservationTransportTests.test_every_declared_copied_observation_survives_actual_archive_and_both_checkout_modes — Actual Git store/archive and both checkout byte modes for the entire declared observation set, with a real binary null and removed-boundary adverse control.
  - `test` M2ObservationTransportTests.test_removing_byte_boundaries_is_detected_beside_actual_binary_null — Actual Git store/archive and both checkout byte modes for the entire declared observation set, with a real binary null and removed-boundary adverse control.
  - `test` M2ObservationTransportTests.test_next_checkpoint_and_other_gate_observations_keep_the_same_real_byte_boundaries — Real archive and both checkout modes across the next auditor and another Gate's complete original-observation family set, beside actual binary nulls.
- Evidence: `file:.gitattributes`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/RUNTIME-V6-FINALIZATION-ARCHIVE.json`, `file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/index-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/PUBLICATION-INTERRUPTION-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/controls/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/index-0005.json`, `file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/controls/run-0003.json`, `file:docs/checkpoints/GATE-7-CP-0003/published-green-keeper/run-0001/CONTROLLED-CANCELLATION.json`, `file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/controls/run-0004.json`, `file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/index-0006.json`

### LSN-0132 — Owned Git clones need read-only-aware cleanup, not native-profile lock retry

- Status: `GUARDED`, severity HIGH, category quality, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-024.
- Symptom: An intentionally interrupted full verifier leaves a fresh owned Git clone because Windows read-only pack objects cause persistent WinError5.
- Root cause: The clone wrapper reused the native-profile sharing-lock retry helper. A read-only attribute is not a transient process sharing lock, so retrying cannot make the object deletable.
- Resolution: Use standard-library TemporaryDirectory ownership and read-only-aware cleanup only for freshly created verification clones, keep explicit parent/prefix/reparse validation and require observed removal. Preserve the native process/profile helper and all its checks. Cmd-0240 is actual causal red; cmd-0241 passes the unchanged regression and all 32 controls.
- Prevention:
  - `test` test_verification_clone_cleanup_handles_real_readonly_git_objects — Set a real read-only file attribute in an owned Git-object-shaped fixture and require the actual clone lifetime manager to remove only its fresh directory; an outer standard owner contains causal-red residue.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/audit-harness/run_full_verification.py`, `file:tests/test_gate5_clients.py`

### LSN-0133 — Shared field names do not imply shared schema types

- Status: `GUARDED`, severity MEDIUM, category tooling, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-025.
- Symptom: Preparatory finalization refuses a generated-package provenance entry with model=null even though engineering-memory provenance permits that value.
- Root cause: A field name shared by two independent artifact contracts was treated as sharing its nullable type; the target provenance schema was not used when the new entry was authored.
- Resolution: Use explicit non-applicable text for deterministic local build provenance, preserve the target schema and denied training rights, and validate the complete actual artifact through its own schema with an unsupported-type adverse control. Cmd-0253/0254 preserve the refusal before publication.
- Prevention:
  - `test` test_current_provenance_is_validated_by_its_own_artifact_schema — Validate actual current checkpoint provenance using the canonical target schema and require an unsupported-type mutation to be refused, without assuming the schema of another similarly named record.
- Evidence: `file:.iacode/schemas/provenance.schema.json`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/PROVENANCE.json`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`

### LSN-0134 — Configuration classifiers consume decoded values, not dotenv quote syntax

- Status: `GUARDED`, severity MEDIUM, category implementation, recurrences 0.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-027.
- Symptom: Raw-line consumers and the host reader retain the quote delimiters of the committed empty desktop values; actual Compose decodes them to empty. Infrastructure, backup secrecy and the two-redactor corpus then disagree about serialization rather than credential classification.
- Root cause: The consumers passed a serialized dotenv token into an API whose input is a value, and the host literal parser omitted enclosing-quote decoding.
- Resolution: Align literal reading with observed Compose semantics and share that decoded input across consumers without changing canonical credential-name or placeholder definitions.
- Prevention:
  - `test` test_host_literal_reader_matches_actual_compose_and_placeholder_semantics — Actual positive/adverse causal regression, not a prose-only claim.
  - `test` test_malformed_quoted_env_literals_fail_closed_without_exposing_content — Actual positive/adverse causal regression, not a prose-only claim.
  - `test` test_process_environment_overlays_are_values_not_dotenv_tokens — Actual positive/adverse causal regression, not a prose-only claim.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/ENV-TEMPLATE-DIAGNOSIS-0001.json`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`

### LSN-0135 — Capture producer evidence before fallible interpretation or owned cleanup

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 3.
- Source: GATE-5, GATE-5-CP-0001, finding G5-INT-032.
- Symptom: The current publisher retains the top-level completed verifier report but loses unexported detailed scenario reports when a stale stage denominator raises and the temporary clone owner correctly cleans its directory.
- Root cause: Producer capture was sequenced after interpretation, so a consumer exception destroyed the only available detailed observations with the owned temporary workspace.
- Resolution: CP0003 local prevention restored by actual current producer/null/adverse controls and unchanged inherited controls. Whole current immutable verification, ordered internal assurance and fresh independent M2 validation remain separate obligations.
- Prevention:
  - `test` test_raw_reports_survive_real_postprocessing_exception_and_owned_cleanup — Actual positive/adverse causal regression, not a prose-only claim.
  - `test` test_raw_capture_refuses_secret_material_but_retains_neutral_failure_inventory — Actual positive/adverse causal regression, not a prose-only claim.
  - `test` test_current_producer_bytes_survive_actual_consumer_failure_and_owned_cleanup — Current strengthened causal boundary; every original control remains.
  - `test` test_current_producer_capture_refuses_unsafe_bytes_without_losing_neutral_inventory — Current strengthened causal boundary; every original control remains.
  - `test` Gate7ProducerBoundaryTests.test_knowledge_raw_producer_survives_actual_consumer_refusal_before_clone_cleanup — The current Gate7 publisher captures exact knowledge producer bytes before a real interpretation refusal, and they remain after actual temporary-clone cleanup.
  - `test` Gate7ProducerBoundaryTests.test_prior_live_pass_is_preserved_and_retired_before_any_new_producer — Preserve prior producer bytes as noncurrent observations and remove the stale location before a fresh child can fail before main.
  - `test` Gate7PromotionProducerCaptureTests.test_owner_locator_and_all_originals_survive_real_consumer_error_and_cleanup — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
  - `test` Gate7CanonicalProducerTests.test_all_canonical_producers_and_legacy_outputs_are_captured_without_private_extras — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7CanonicalProducerTests.test_canonical_registry_growth_is_bound_without_a_caller_selected_report_set — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7CanonicalProducerTests.test_all_current_originals_survive_real_consumer_refusal_and_actual_owner_cleanup — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7CanonicalProducerTests.test_claimed_success_cannot_omit_a_canonically_required_producer — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7CanonicalProducerTests.test_forwarding_uses_every_archived_original_after_actual_producer_cleanup — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7CanonicalProducerTests.test_bad_archived_input_never_partially_overwrites_any_prior_functional_target — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7CanonicalProducerTests.test_directory_or_hardlinked_output_is_refused_before_any_forwarding_effect — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7CanonicalProducerTests.test_verifier_consumer_uses_durable_original_not_a_second_temporary_read — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7RawReworkContextTests.test_every_original_context_is_inert_byte_bound_and_protected_by_real_git_attributes — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` ClientProducerCleanupEvidenceTests.test_both_failures_retain_distinct_actual_exit_and_streams — Actual producer/replay causal boundary with null and adverse controls.
  - `test` ClientProducerCleanupEvidenceTests.test_timeout_and_failed_cleanup_preserve_partial_real_output — Actual producer/replay causal boundary with null and adverse controls.
  - `test` ClientProducerCleanupEvidenceTests.test_successful_producer_with_failed_cleanup_cannot_pass — Actual producer/replay causal boundary with null and adverse controls.
  - `test` ClientProducerCleanupEvidenceTests.test_secret_and_oversized_output_are_not_disclosed — Actual producer/replay causal boundary with null and adverse controls.
  - `test` ClientProducerCleanupEvidenceTests.test_clean_null_control_returns_actual_producer — Actual producer/replay causal boundary with null and adverse controls.
  - `test` NativeProducerObservationTests.test_failed_callback_cannot_replace_real_nonzero_producer — Executed actual current positive/adverse control; no production fake or independent verdict.
  - `test` NativeProducerObservationTests.test_timeout_and_callback_failure_keep_both_observations — Executed actual current positive/adverse control; no production fake or independent verdict.
  - `test` NativeProducerObservationTests.test_capture_handle_release_failure_cannot_replace_primary_observation — Executed actual current positive/adverse control; no production fake or independent verdict.
  - `test` NativeProducerObservationTests.test_native_actor_forwards_producer_facts_without_approving_cleanup_failure — Executed actual current positive/adverse control; no production fake or independent verdict.
  - `test` BridgePhysicalBoundsTests.test_output_prefix_is_fixed_before_a_controlled_actual_append — Executed actual current positive/adverse control; no production fake or independent verdict.
- Evidence: `file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-5-CP-0001/attempts/FULL-VERIFY-RED-0002-MANIFEST.json`, `file:tests/test_gate5_clients.py`, `file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/PRE-LIVE-PROGRESS.json`, `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0004.json`, `file:tests/test_gate7_knowledge.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-ROOT-0005.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/KNOWLEDGE-LIVE-RAW-RECEIPT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:tests/test_gate7_assurance.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/RUNTIME-V2-FAILED-FULL-MANIFEST.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/CURRENT-REWORK-GATE7-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-LINT-0006.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-HELPER-QUALITY-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-GATE4-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-CONTROLS-0001.json`, `file:docs/checkpoints/GATE-7-CP-0002/FINDINGS.json`, `file:tests/test_m2_audit_corrections.py`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0005.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0006.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0011.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/native-observation/run-0003.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge-physical-bounds/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge/run-0005.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/owned-cleanup/run-0004.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/operator-cleanup/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/current-streams/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/inherited-streams/run-0001.json`

### LSN-0136 — Strict JSON validation loses transport context

- Status: `GUARDED`, severity MEDIUM, category implementation, recurrences 0.
- Source: GATE-6, GATE-6-CP-0001, finding G6-INT-001.
- Symptom: Cmd-0014 actually reports 18 setup errors rejecting valid arrays/dates, one distinct failed security case and seven passed cases; its process exits 1.
- Root cause: An inherited model-before validator materializes the entire JSON model as a Python dictionary before strict tuple/datetime handling. Restrict boolean prevalidation to the permission fields.
- Resolution: Preserve strict JSON-mode collection/date handling; apply exact-boolean checks at their owning fields and retain positive/adverse round-trip controls.
- Prevention:
  - `test` test_exact_closed_roundtrip — Executed causal positive/adverse regression in the actual owning runtime.
  - `test` test_permissions_require_exact_boolean — Executed causal positive/adverse regression in the actual owning runtime.
  - `test` test_numeric_observations_are_not_coerced — Executed causal positive/adverse regression in the actual owning runtime.
- Evidence: `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/PRE-LIVE-PROGRESS.json`, `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0004.json`

### LSN-0137 — SQL text interprets inline JSON colons as bindings

- Status: `GUARDED`, severity MEDIUM, category testing, recurrences 0.
- Source: GATE-6, GATE-6-CP-0001, finding G6-INT-004.
- Symptom: Cmd-0023 preserves two StatementError failures demanding bind parameter true before those fixtures execute; 27 other cases pass and owned cleanup is complete.
- Root cause: Inline JSON literals inside SQLAlchemy text contain colon-prefixed tokens that its lexical binder treats as parameters. Bind the JSON data through CAST(:body AS JSONB), without changing either substantive corruption/legacy assertion.
- Resolution: Bind JSON as data instead of embedding colon-bearing JSON literals in SQLAlchemy text; retain actual database assertions and complete migration execution.
- Prevention:
  - `test` test_legacy_migration_preserves_identity_body_and_rights_without_promotion — Executed causal positive/adverse regression in the actual owning runtime.
  - `test` test_database_immutability_and_direct_corruption_fail_closed — Executed causal positive/adverse regression in the actual owning runtime.
- Evidence: `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0001.log`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/PRE-LIVE-PROGRESS.json`, `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0004.json`

### LSN-0138 — Secret projection distinguishes public identities from authorization secrets

- Status: `GUARDED`, severity HIGH, category security, recurrences 0.
- Source: GATE-6, GATE-6-CP-0001, finding G6-INT-006.
- Symptom: A configured public MinIO identity collides with legitimate quality package/report text and a real runtime classifier returns AUTHORIZATION_MATERIAL_REFUSED.
- Root cause: The runtime put the MinIO public account/access identity in the same exact-value set as bearer keys and passwords. The committed public identity occurs in legitimate quality package/report names, so the actual owning-image classifier refuses those bytes with AUTHORIZATION_MATERIAL_REFUSED. Field masking/type alone is not a definition of a secret. No value is globally allowlisted and actual secret scanning or password protection may not be weakened.
- Resolution: Project actual secret components by their contract: retain HMAC/provider/storage/database/Redis passwords and all declared encoded-form detection; do not add a public account identity as a bearer secret or globally exempt a word.
- Prevention:
  - `test` test_public_minio_identity_is_not_a_bearer_secret_but_storage_password_stays_protected — Executed causal positive/adverse regression in the actual owning runtime.
  - `test` test_known_opaque_capability_refused_in_declared_forms — Executed causal positive/adverse regression in the actual owning runtime.
- Evidence: `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/API-UNIT-0004.log`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/PRE-LIVE-PROGRESS.json`, `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0004.json`, `file:docs/checkpoints/GATE-6-CP-0001/STRICT-MEMORY-FINDING.json`

### LSN-0139 — Privacy projection begins in the source query

- Status: `GUARDED`, severity HIGH, category security, recurrences 0.
- Source: GATE-6, GATE-6-CP-0001, finding G6-INT-007.
- Symptom: Actual SQL retrieves unneeded private source fields although the serialized fact omits them.
- Root cause: Selecting ORM entities loaded whole source records before projecting the closed document. Final serialization excluded private text, but the SQL read still fetched unneeded task results, agent output and event payloads. Cardinality alone did not bound source JSON/text. Select only consumed columns with raiseload, extract exact workspace/permission scalars and bound required command arguments in SQL before loading.
- Resolution: Use explicit raiseload column projections, exact JSON scalar extraction and SQL-side byte bounds before required structured data enters application memory.
- Prevention:
  - `test` test_actual_sql_projection_does_not_fetch_unneeded_private_source_columns — Executed causal positive/adverse regression in the actual owning runtime.
  - `test` test_oversized_required_source_json_is_refused_before_materialization_and_writes — Executed causal positive/adverse regression in the actual owning runtime.
- Evidence: `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0003.json`, `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0003.log`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/PRE-LIVE-PROGRESS.json`, `file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/INTEGRATION-0004.json`

### LSN-0140 — Summaries preserve canonical continuation structure

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 4.
- Source: GATE-6, GATE-6-CP-0001, finding G6-INT-009; G6-INT-016.
- Symptom: A local assembler emits readable prose but removes mandatory handoff/next-action sections. Later manual editing adds an unsupported retrospective heading.
- Root cause: The local assembler replaced structured continuation artifacts with summaries. A later manual update likewise failed to preserve the owning retrospective template exactly. Semantically related prose does not satisfy a canonical structural contract; changing the test would hide the authoring defect.
- Resolution: CONTINUATION-001 is locally corrected with unchanged canonical sections and inherited assertions. The actual corrective/current documents and every recorded lesson/guard are covered, including original rejection, missing/empty/extra/order and growth controls. Current complete lint, whole authored quality and quiescent canonical validation passed. Original failure/counter remain; fresh source-epoch whole assurance and independent M2 are due.
- Prevention:
  - `test` test_local_handoff_renderer_preserves_the_complete_canonical_contract — Actual canonical renderer output and every omitted/empty-section refusal.
  - `test` test_local_handoff_renderer_refuses_omitted_or_empty_sections_and_next_action — Actual canonical renderer output and every omitted/empty-section refusal.
  - `test` test_retrospective_preserves_template_and_every_current_gate_lesson — The actual retrospective keeps the exact canonical heading sequence and every current lesson and guard identity.
  - `test` Gate7ContinuationContractTests.test_actual_current_handoff_and_next_preserve_canonical_structure — Actual current canonical structure and adverse growth/omission boundary; inherited assertions stay unchanged.
  - `test` Gate7ContinuationContractTests.test_actual_retrospective_uses_exact_template_and_every_current_lesson_guard — Actual current canonical structure and adverse growth/omission boundary; inherited assertions stay unchanged.
  - `test` Gate7ContinuationContractTests.test_actual_renderer_and_each_missing_empty_extra_or_reordered_section_refusal — Actual current canonical structure and adverse growth/omission boundary; inherited assertions stay unchanged.
  - `test` Gate7ContinuationContractTests.test_retrospective_positive_omission_extra_and_registered_lesson_growth — Actual current canonical structure and adverse growth/omission boundary; inherited assertions stay unchanged.
  - `test` Gate7ContinuationContractTests.test_original_failed_documents_remain_exact_inert_and_rejected — Actual current canonical structure and adverse growth/omission boundary; inherited assertions stay unchanged.
  - `test` CorrectiveContinuationTests.test_actual_corrective_and_current_handoff_next_preserve_existing_contract — Actual current caller/document and exact original adverse controls; no template or budget reduction.
  - `test` CorrectiveContinuationTests.test_actual_retrospectives_keep_exact_sections_and_every_recorded_lesson_guard — Actual current caller/document and exact original adverse controls; no template or budget reduction.
  - `test` CorrectiveContinuationTests.test_actual_failed_original_is_exact_inert_and_rejected_by_identical_contract — Actual current caller/document and exact original adverse controls; no template or budget reduction.
  - `test` CorrectiveContinuationTests.test_current_positive_and_omission_empty_extra_order_and_lesson_growth_controls — Actual current caller/document and exact original adverse controls; no template or budget reduction.
- Evidence: `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:tests/test_gate6_experience.py`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/CONTINUATION-REFUSAL-0001-MANIFEST.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/CONTINUATION-CAUSAL-RED-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/CONTINUATION-CAUSAL-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/CONTINUATION-ALL-OWNERS-0001.json`, `file:tests/test_gate7_continuation.py`, `file:docs/checkpoints/GATE-7-CP-0003/continuation-attempts/run-0001/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/lint/run-0011.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/helper-quality/run-0020/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/all-m2/run-0004.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/checkpointValidation/run-0007.json`, `file:docs/checkpoints/GATE-7-CP-0003/continuation-attempts/run-0001/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/all-m2/run-0003.json`

### LSN-0141 — Preflight checks honor every declared applicability dimension

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: GATE-6, GATE-6-CP-0001, finding G6-INT-011.
- Symptom: The immutable root suite rejects LSN-0136 because a technology-filtered exclusion has no scope filter; cmd-0138 reproduces the failure in isolation.
- Root cause: The repository-wide preflight regression assumed scopes were the only legitimate selector even though the policy and its existing tests support Gate, scope, technology and module filters. Production applicability was correct; the new Python lesson exposed the stale assertion.
- Resolution: Keep production policy and lesson selectors unchanged. Require an independent mismatch in a declared selector for every excluded active lesson, preserving exact applicable identifier equality. Exercise all four filters, an unfiltered positive control and a producer that falsely omits it.
- Prevention:
  - `test` test_repository_preflight_accepts_all_declared_filters_but_refuses_unexplained_omission — Execute the actual inherited assertion against each legitimate selector and prove that unexplained omission remains refused.
- Evidence: `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:tests/test_development_ledger.py`, `file:tests/test_gate6_experience.py`

### LSN-0142 — Local Engine recovery keeps transport and cleanup scoped

- Status: `GUARDED`, severity HIGH, category environment, recurrences 0.
- Source: GATE-6, GATE-6-CP-0001, finding G6-INT-012.
- Symptom: The active Docker context and default pipe do not answer management requests while unrelated applications remain running. Treating those paths as general Engine availability would suggest a disruptive restart.
- Root cause: Two existing management access paths stalled, but a bounded query through the already exposed docker_engine_linux pipe reached the same local Docker Desktop Linux Engine and the exact interrupted test project. The underlying proxy/alias fault remains undetermined; no daemon-wide outage is inferred.
- Resolution: Pin the already available local pipe only in child process environments, remove inherited context precedence only there, and preserve the parent/global context. Re-derive the interrupted project's identity, validate project-labelled resource names, retain before/after observations and remove only those disposable resources. Actual recovery removed14 test containers,4 volumes and1 network while all37 other container identities/states remained.
- Prevention:
  - `test` test_local_engine_selection_is_child_only_and_preserves_project_and_failure — Parent transport/context and Compose ownership remain unchanged; only the child selects the local endpoint and its nonzero exit propagates.
  - `test` test_owned_recovery_refuses_operational_or_mislabelled_resources_before_removal — Operational project names, inconsistent resource ownership and duplicate identities are refused before removal.
- Evidence: `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/DOCKER-RECOVERY-0001-BEFORE.json`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/DOCKER-RECOVERY-0001-AFTER.json`, `file:tests/test_gate6_experience.py`

### LSN-0143 — Management recovery is not complete runtime capability

- Status: `GUARDED`, severity HIGH, category environment, recurrences 0.
- Source: GATE-6, GATE-6-CP-0001, finding G6-INT-015.
- Symptom: Successful Engine version, inventory and owned cleanup were generalized into readiness for all Docker-dependent controls. The next canonical lint rejected the Windows repository bind and stalled during frontend image construction; later management queries timed out again.
- Root cause: The direct Linux management endpoint does not provide the Windows bind translation used by this lint invocation. The separate builder and renewed management nonresponse have no established backend cause. Management response alone is insufficient capability evidence.
- Resolution: After explicit owner authorization, use supported Desktop restart/force-stop/start only, without data deletion or global WSL shutdown. The normal desktop-linux Server responds; actual cmd-0192 complete canonical lint proves the Windows bind/build path and cmd-0194 observes all37 prior other identities/states preserved. Keep whole immutable verification mandatory; management response alone never grants runtime acceptance.
- Prevention:
  - `test` test_management_only_report_cannot_replace_complete_non_fast_verification — Exercise the actual publisher: reject management-only input, every missing canonical stage and a falsely passing report for each failed canonical stage; derive all stage identifiers from current build_stages(False).
- Evidence: `file:docs/checkpoints/GATE-6-CP-0001/attempts/DOCKER-RETRY-0002.json`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/DOCKER-RESTART-0001-AFTER.json`, `file:tests/test_gate6_experience.py`

### LSN-0144 — Raw archived observations retain original context rather than becoming active relocated documents

- Status: `GUARDED`, severity HIGH, category documentation, recurrences 0.
- Source: GATE-6, GATE-6-CP-0001, finding G6-INT-023.
- Symptom: The unchanged whole-tree relative-link check rejects nine links in a byte-exact archived final report interpreted at the new archive path.
- Root cause: Copied observation suffixes were treated as active document semantics even though relative links belonged to the original location.
- Resolution: Preserve the immutable original manifest and published objects; use explicitly raw data suffixes and a separate catalog binding original locators and unchanged digests, without weakening active-document checks. Actual cmd-0377 preserves raw observations and original manifest, cmd-0378 passes unchanged active-document links and cmd-0380 passes all38 Gate6 cases, including every raw member's actual immutable published-object equality.
- Prevention:
  - `test` Gate6BookkeepingCausalTests.test_raw_archive_catalog_retains_manifest_and_published_original_bytes — Every raw catalog member must match the original manifest and actual immutable published Git object, with original Markdown/Python marked raw.
  - `test` SetupChecklistTests.test_documentation_links_resolve — Every active repository Markdown link still resolves under the unchanged whole-tree check.
- Evidence: `file:docs/checkpoints/GATE-6-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-6-CP-0001/attempts/RUNTIME-V6-RAW-CATALOG.json`, `file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl`

### LSN-0145 — A new persistent capability must extend the explicit structural contract, not bypass its exact inventory

- Status: `GUARDED`, severity MEDIUM, category testing, recurrences 0.
- Source: GATE-7, GATE-7-CP-0001, finding G7-INT-003.
- Symptom: The actual complete API unit gate refuses three exact structural assertions after KnowledgeDocument, KnowledgeIndexEntry and KnowledgeEvent are added: table inventory, immutable fact classification and foreign-key ownership.
- Root cause: The behavior implementation added three declared ORM entities but did not yet extend the owning structural expectations. Correct exact assertions expose incomplete integration; replacing equality by inclusion or classifying mutable rows as facts would conceal it.
- Resolution: Append only authorized knowledge table/fact/cascade entries to the owning exact structural contract. Cmd-0033 passes all192 API cases, including executed clean/missing/extra table, wrong fact/lifecycle classification and each changed knowledge cascade. Cmd-0042 passes all21 real PostgreSQL/HTTP/migration cases, including unchanged legacy experience identity/rights and explicit lifecycle write counters. No inherited exact assertion is dropped or relaxed.
- Prevention:
  - `test` test_exact_table_inventory_refuses_each_missing_and_extra_table — Invoke the actual exact inventory assertion with clean ORM metadata and each missing/extra table.
  - `test` test_fact_lifecycle_classification_refuses_each_wrong_knowledge_role — Invoke existing convention/base-class controls with each wrong knowledge fact/lifecycle role.
  - `test` test_actual_foreign_key_contract_refuses_each_changed_knowledge_cascade — Mutate each actual SQLAlchemy knowledge foreign-key cascade and require the owning exact assertion to refuse.
  - `test` test_actual_retention_check_tracks_lifecycle_version_without_payload_rewrite — Actual PostgreSQL checks and purge track the existing version/update convention while material stays immutable.
- Evidence: `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-APITESTS-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-APITESTS-0001.log`, `file:apps/api/tests/unit/test_knowledge_structure.py`, `file:apps/api/tests/integration/test_knowledge_engine.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-APITESTS-0002.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/KNOWLEDGE-SQL-0003.json`

### LSN-0146 — A completed command record is not proof that its producing process has exited

- Status: `GUARDED`, severity CRITICAL, category process, recurrences 1.
- Source: GATE-7, GATE-7-CP-0001, finding G7-INT-007.
- Symptom: The finalizer had already appended successful cmd-0067 while its session45921 and Python process22984 were still running. The caller started the progress commit from that ledger success instead of waiting for the actual process completion.
- Root cause: An intermediate durable result was mistaken for completion of the whole producer. The canonical finalizer still performs post-record validation; its full exit is a separate observable event.
- Resolution: Use synchronous actual child exits for dependent publication and typed completed/nonempty source observations before building replacements. Cmd-0123 executes real running/failed/successful children, the serial publication controls and readonly original-byte/envelope controls. Cmd-0120 verifies actual retained preimage bytes. The old source-read response was not retained, so its particular asynchronous timing remains an inference, not an observed fact. Local executable guard restoration only; the failed immutable runtime-v1 remains FAIL. A new complete immutable invocation and every ordered internal assurance control are still required before readiness; independent M2 validation remains pending.
- Prevention:
  - `test` Gate7ProcessCompletionTests.test_process_owned_sequence_waits_for_real_success_before_consumer — Actual child processes demonstrate producer completion before consuming its observable file.
  - `test` Gate7ProcessCompletionTests.test_success_looking_output_then_actual_failure_never_starts_consumer — A child prints successful-looking intermediate output then actually exits7; the dependent consumer remains unexecuted.
  - `test` Gate7TypedObservationTests.test_real_running_and_failed_children_are_not_completed_source_observations — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
- Evidence: `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/DECISIONS.md`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/audit-harness/publish_progress.py`, `file:tests/test_gate7_knowledge.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROCESS-COMPLETION-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROCESS-COMPLETION-0001.log`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/ARCHIVE-V1-HELPER-PARSE-RED.py.raw`, `file:tests/test_gate7_assurance.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`

### LSN-0147 — Framework lifecycle errors need bounded identities as well as test methods

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 0.
- Source: GATE-7, GATE-7-CP-0001, finding G7-INT-016.
- Symptom: The full root producer reports five failures and six errors, but its header list retains only six method identities and omits five real setUpClass errors.
- Root cause: The diagnostic parser admits only test-method names while unittest lifecycle error holders use a different framework vocabulary.
- Resolution: Extend only bounded ASCII framework identities to class/module lifecycle errors. Actual method/lifecycle/privacy/malformed/256-count/1024-length controls pass cmd-0123, preserving the incomplete original full producer and all original privacy/truncation bounds. Local executable guard restoration only; the failed immutable runtime-v1 remains FAIL. A new complete immutable invocation and every ordered internal assurance control are still required before readiness; independent M2 validation remains pending.
- Prevention:
  - `test` Gate7FrameworkDiagnosticsTests.test_framework_methods_and_lifecycle_headers_survive_without_private_bodies — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
  - `test` Gate7FrameworkDiagnosticsTests.test_framework_identity_count_and_length_limits_remain_unchanged — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
- Evidence: `file:docs/checkpoints/GATE-7-CP-0001/attempts/RUNTIME-V1-FAILED-VERIFY.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-RED-0001.log`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:tests/test_gate7_assurance.py`, `file:tests/test_gate7_knowledge.py`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`

### LSN-0148 — Minimal protocol fixtures inherit control contracts, never deployment-owned source data

- Status: `GUARDED`, severity HIGH, category security, recurrences 0.
- Source: GATE-7, GATE-7-CP-0001, finding G7-INT-015.
- Symptom: All five real positive-protocol setups fail MIR-015 after wholesale .iacode copying imports the curated-source README into a minimal fixture without its owning ADR.
- Root cause: The fixture copies the entire control directory even though it promises to inherit canonical control contracts rather than unrelated operational source content or real history.
- Resolution: ADR-0056 restricts minimal protocol fixtures to explicit control contracts and declared dependencies, not curator data, real history or unrelated attestations. Actual synthetic owner-isolation/dependency and retained-contract MIR-015 refusal pass cmd-0123; all32 unchanged real promotion/succession tests pass cmd-0126, and cmd-0129 retains two actual clean mirror originals before cleanup. Local executable guard restoration only; the failed immutable runtime-v1 remains FAIL. A new complete immutable invocation and every ordered internal assurance control are still required before readiness; independent M2 validation remains pending.
- Prevention:
  - `test` Gate7MinimalProtocolIsolationTests.test_fixture_copies_contracts_and_never_source_data_history_or_unrelated_verdicts — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
  - `test` Gate7MinimalProtocolIsolationTests.test_a_retained_contract_broken_link_still_fails_the_real_mirror — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
  - `test` PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
- Evidence: `file:docs/checkpoints/GATE-7-CP-0001/attempts/PROMOTION-DIAGNOSTIC-985d6abe15294033a4c5ef1b2a895a54-M0-INTERNAL-MIRROR.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-RED-0001.log`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:tests/test_gate7_assurance.py`, `file:tests/test_gate7_knowledge.py`, `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`

### LSN-0149 — A shell exit zero is not a produced digest or verified original evidence

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 0.
- Source: GATE-7, GATE-7-CP-0001, finding G7-INT-019.
- Symptom: Cmd-0115 copies the file but its legacy child shell cannot resolve Get-FileHash; nonterminating errors leave both digest variables empty and the process exits0.
- Root cause: The ad-hoc verifier treats execution status and equality of absent results as produced evidence instead of requiring typed nonempty data and actual file verification.
- Resolution: Typed actual nonempty bytes, positive integer size and lowercase SHA256 must agree; a shell exit or absent equality cannot substitute. Cmd-0120 verifies both retained originals. Cmd-0123 executes real running/failed/clean children, null/empty/wrong-type/digest/size mutations and actual atomic readonly source-envelope proof. Original cmd-0115 semantic failure and cmd-0116 precondition rejection remain. Local executable guard restoration only; the failed immutable runtime-v1 remains FAIL. A new complete immutable invocation and every ordered internal assurance control are still required before readiness; independent M2 validation remains pending.
- Prevention:
  - `test` Gate7TypedObservationTests.test_real_running_and_failed_children_are_not_completed_source_observations — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
  - `test` Gate7TypedObservationTests.test_only_typed_nonempty_actual_bytes_size_and_digest_are_evidence — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
  - `test` Gate7TypedObservationTests.test_actual_file_mutations_and_atomic_readonly_source_envelope — Executed current positive/adverse regression; unit fixture observations never substitute for actual live or independent milestone proof.
- Evidence: `file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl`, `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/ARCHIVE-V1-HELPER-PARSE-RED.py.raw`, `file:tests/test_gate7_assurance.py`, `file:tests/test_gate7_knowledge.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE7-REWORK-ROOT-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/INHERITED-ROOT-GREEN-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/PROTOCOL-SETUPS-GREEN-0001.json`

### LSN-0150 — Build and verification root inputs need subject-versioned assurance binding

- Status: `GUARDED`, severity HIGH, category security, recurrences 0.
- Source: GATE-7, GATE-7-CP-0001, finding G7-INT-022.
- Symptom: An isolated real Git fixture changes .dockerignore bytes while the actual assurance fingerprint remains equal. The current packaging privacy guard consumes that root input; verify.ps1 is also an unbound real root verification entrypoint.
- Root cause: The v1 subject policy binds only root ignore/lint files. New build-context privacy inputs and an existing public verification launcher are outside the fingerprint even though they can affect what a delivered verification or package means.
- Resolution: ADR-0057 versions the exact four current root inputs. Actual cmd-0160 passes all four real Git mutation/ignored/deletion/narrowing controls and preserves absent/v1 identity; unchanged inherited policy controls cmd-0164 and whole lint cmd-0161 pass. GRD-0153 is locally executed prevention, not full immutable delivery acceptance.
- Prevention:
  - `test` Gate7RootInputFingerprintTests.test_build_and_verification_edits_invalidate_actual_assurance_fingerprint — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7RootInputFingerprintTests.test_every_current_root_is_bound_even_if_ignored_and_deletion_invalidates — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7RootInputFingerprintTests.test_absent_and_v1_subjects_keep_their_original_root_fingerprint_identity — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7RootInputFingerprintTests.test_current_policy_refuses_missing_narrowed_reordered_extra_and_malformed_inputs — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
- Evidence: `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:.iacode/policies/assurance-scope.json`, `file:scripts/development-ledger/ledger_common.py`, `file:tests/test_gate7_knowledge.py`, `file:docs/adr/ADR-0049-root-assurance-inputs-follow-subject-policy.md`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/CURRENT-REWORK-GATE7-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-LINT-0006.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-HELPER-QUALITY-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-GATE4-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-CONTROLS-0001.json`

### LSN-0151 — Immutable Git object reads must handle Windows long paths only in the owning child

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 1.
- Source: GATE-7, GATE-7-CP-0001, finding G7-INT-024.
- Symptom: Completed runtime-v2 root cases and portability attackT cannot reconstruct a valid immutable subject: git show probes a SHA:path expression as a working path and returns Filename too long.
- Root cause: The immutable review reader invokes Git without an explicit child-scoped long-path override. A physical240-character fixture is valid, but its full-commit object expression creates a281-character filesystem probe on Windows.
- Resolution: Post-quality local prevention is restored only after actual current positive/adverse controls, original historical declarations, full lint, authored read-only quality and quiescent checkpoint validation. Original failures, counters and severity remain. Fresh source-epoch whole quality/functional/internal assurance and independent M2 validation remain mandatory.
- Prevention:
  - `test` Gate7GitTransportTests.test_real_long_object_expression_returns_every_original_binary_byte — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7GitTransportTests.test_git_override_is_child_scoped_and_leaves_local_and_global_settings_unchanged — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` Gate7GitTransportTests.test_genuine_git_failure_stays_failed_without_rewriting_configuration_or_input — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` ReviewBundleTests.test_immutable_subject_rebuilds_are_byte_identical_and_exclude_only_the_sidecar — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` ReviewBundleTests.test_declared_digest_and_size_are_rebuilt_not_trusted — Executed current positive/adverse control; inherited assertions and controls remain, and whole immutable assurance is separate.
  - `test` M2HistoryTransportTests.test_real_short_null_and_long_materialization_preserve_config_and_refusal — Actual current boundary/null/refusal control; not independent acceptance.
  - `test` M2HistoryTransportTests.test_genuine_bad_subject_remains_refused_without_configuration_effects — Actual current boundary/null/refusal control; not independent acceptance.
  - `test` M2HistoryTransportTests.test_legacy_git_read_gets_exact_bytes_only_with_child_runtime_override — Actual current boundary/null/refusal control; not independent acceptance.
  - `test` M2HistoryTransportTests.test_child_runtime_configuration_preserves_existing_pairs_and_refuses_malformed_input — Actual current boundary/null/refusal control; not independent acceptance.
- Evidence: `file:docs/checkpoints/GATE-7-CP-0001/FINDINGS.json`, `file:docs/checkpoints/GATE-7-CP-0001/attempts/RUNTIME-V2-FAILED-VERIFY.json`, `file:scripts/development-ledger/review_bundle.py`, `file:tests/test_gate4_quality_engine.py`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/CURRENT-REWORK-GATE7-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/GATE-LINT-0006.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-HELPER-QUALITY-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-GATE4-0001.json`, `file:docs/checkpoints/GATE-7-CP-0001/suite-attempts/REWORK-INHERITED-CONTROLS-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0001/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0001/stdout.log`, `file:docs/checkpoints/GATE-7-CP-0003/published-green-keeper/run-0003/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/lint/run-0013.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/helper-quality/run-0029/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/all-m2/run-0007.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/inherited-streams/run-0003.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/history-transport/run-0006.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/inherited-git/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/review-reconstruction/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/quality-attempts/checkpointValidation/run-0009.json`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0008/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0008/stdout.log`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0006/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0006/stdout.log`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0007/RECEIPT.json`, `file:docs/checkpoints/GATE-7-CP-0003/history-diagnostics/run-0007/stdout.log`

### LSN-0152 — Private runner inputs require physical containment, not lexical ancestry

- Status: `GUARDED`, severity MEDIUM, category security, recurrences 0.
- Source: GATE-7, GATE-7-CP-0003, finding BRIDGE-PATH-001.
- Symptom: The unreleased adapter rejects an absolute outside file but accepts an existing parent-relative outside file under a lexically owned prefix.
- Root cause: Path.is_relative_to compares lexical components and does not establish actual filesystem containment through parent components.
- Resolution: CP0003 local prevention restored by actual current producer/null/adverse controls and unchanged inherited controls. Whole current immutable verification, ordered internal assurance and fresh independent M2 validation remain separate obligations.
- Prevention:
  - `test` BridgePhysicalBoundsTests.test_actual_inside_null_and_absolute_escape_refusal — Executed actual current positive/adverse control; no production fake or independent verdict.
  - `test` BridgePhysicalBoundsTests.test_parent_relative_existing_escape_is_refused — Executed actual current positive/adverse control; no production fake or independent verdict.
  - `test` BridgePhysicalBoundsTests.test_parent_alias_in_the_source_root_is_refused — Executed actual current positive/adverse control; no production fake or independent verdict.
  - `test` BridgePhysicalBoundsTests.test_redirected_owned_ancestor_and_hardlink_are_refused — Executed actual current positive/adverse control; no production fake or independent verdict.
  - `test` BridgePhysicalBoundsTests.test_report_escape_keeps_producer_but_never_archives_outside_content — Executed actual current positive/adverse control; no production fake or independent verdict.
- Evidence: `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge-path-bounds/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/INTERNAL-ENVIRONMENT-REWORK.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0011.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/native-observation/run-0003.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge-physical-bounds/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge/run-0005.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/owned-cleanup/run-0004.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/operator-cleanup/run-0002.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/current-streams/run-0001.json`, `file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/inherited-streams/run-0001.json`
