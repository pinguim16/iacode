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
| `LSN-0008` | `GUARDED` | CRITICAL | process | Requirement completeness must be total and evidence-backed before handoff | `DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`, `scripts/development-ledger/check_completeness.py`, `ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails` |
| `LSN-0009` | `GUARDED` | CRITICAL | testing | A red gate requires rework, never a waiver, and never a weakened check | `GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `DeliveryAssuranceGateTests.test_red_tests_block_review`, `.iacode/policies/quality-gates.json`, `MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected` |
| `LSN-0010` | `GUARDED` | HIGH | tooling | A recorded command must carry runtime, working directory, commit and purpose to be replayable | `CommandReproducibilityTests.test_bare_script_name_is_rejected`, `CommandReproducibilityTests.test_unresolvable_script_path_is_rejected`, `.iacode/schemas/command.schema.json`, `validate_checkpoint._validate_command_reproducibility`, `CommandInputBindingTests.test_a_record_without_a_digest_is_rejected` |
| `LSN-0011` | `GUARDED` | MEDIUM | tooling | A control over a checkpoint's own evidence must be scoped to the moment it matters | `DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`, `green_keeper._refresh_declared_hashes`, `test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes` |
| `LSN-0012` | `GUARDED` | CRITICAL | git | Sealed checkpoints and their tags are immutable, and tooling must keep validating them | `HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`, `docs/CHECKPOINT-PROTOCOL.md`, `scripts/development-ledger/anchors.py`, `IntegrityAnchorTests.test_a_moved_historical_tag_is_detected` |
| `LSN-0013` | `CONFIRMED` | MEDIUM | environment | An installed capability must be detected by resolved path, not by a bare command lookup | _not yet guarded_ |
| `LSN-0014` | `GUARDED` | MEDIUM | process | Evidence must be recorded as it happens, not reconstructed at the end of a run | `scripts/development-ledger/record_command.py`, `validate_checkpoint._validate_seal_chronology`, `SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected` |
| `LSN-0015` | `GUARDED` | CRITICAL | quality | Every positive terminal status needs one shared promotion invariant | `validate_checkpoint._validate_delivery_assurance`, `PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper` |
| `LSN-0016` | `GUARDED` | CRITICAL | testing | A mandatory set must be closed by policy, never chosen by the caller | `validate_checkpoint._validate_green_keeper_cycle`, `.iacode/policies/quality-gates.json` |
| `LSN-0017` | `GUARDED` | CRITICAL | process | A completeness denominator must come from a source the delivery does not own | `policies.expected_requirement_refs`, `ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected` |
| `LSN-0018` | `GUARDED` | CRITICAL | tooling | A structured reference must be resolved, not merely well typed | `lessons.resolve_control`, `LessonResolutionTests.test_a_test_control_must_exist_in_the_suite` |
| `LSN-0019` | `GUARDED` | HIGH | tooling | A derived artifact must carry a fingerprint of the inputs that produced it | `lessons.preflight_staleness`, `PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale` |
| `LSN-0020` | `GUARDED` | HIGH | tooling | Evidence produced from a dirty tree needs immutable input identity | `ledger_common.build_command_record`, `CommandInputBindingTests.test_the_recorder_binds_inputs_automatically` |
| `LSN-0021` | `GUARDED` | CRITICAL | git | Sealed history needs an anchor outside the content it describes | `anchors.verify_chain`, `IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected` |
| `LSN-0022` | `GUARDED` | CRITICAL | documentation | An authoritative count must be derived once, never maintained by hand twice | `validate_checkpoint._validate_derived_counts`, `DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`, `SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`, `docs/QUALITY-GATES.md` |
| `LSN-0023` | `GUARDED` | MEDIUM | documentation | A lesson must cite a source that actually records the finding it claims | `lessons._resolve_source_locator`, `LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected` |
| `LSN-0024` | `GUARDED` | CRITICAL | quality | A control is finished only when its positive path has been executed, not only its refusals | `PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `scripts/development-ledger/promotion_simulation.py`, `SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output` |
| `LSN-0025` | `GUARDED` | CRITICAL | testing | A generic guardrail derives repository state instead of naming today's checkpoint | `anchors.pending_anchor_exclusion`, `SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain`, `IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint` |
| `LSN-0026` | `GUARDED` | HIGH | testing | An adversarial battery without a null-mutation control proves nothing | `.iacode/schemas/red-team-report.schema.json`, `validate_checkpoint._validate_internal_assurance`, `InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected` |
| `LSN-0027` | `GUARDED` | MEDIUM | documentation | A lesson's prose may record a residual limit but may never contradict its status | `lessons.validate_lessons`, `MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded` |
| `LSN-0028` | `GUARDED` | HIGH | tooling | A configuration key that no code reads is a defect, not documentation | `.iacode/schemas/memory-policy.schema.json`, `lessons.validate_memory_policy_document`, `MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared`, `test_every_declared_key_is_read_somewhere` |
| `LSN-0029` | `GUARDED` | CRITICAL | process | A required protocol transition must never turn a mandatory gate red | `scripts/development-ledger/successor_durability.py`, `SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `scripts/development-ledger/gate_transition_simulation.py` |
| `LSN-0030` | `CONFIRMED` | LOW | process | The lesson preflight presumes an implementing delivery and constrains an audit run badly | _not yet guarded_ |
| `LSN-0031` | `GUARDED` | CRITICAL | quality | An empty applicable set is not a missing required set, and a control must tell them apart | `scripts/development-ledger/mirror_semantics_validation.py`, `MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`, `MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`, `validate_checkpoint._validate_mirror_applicability` |
| `LSN-0032` | `GUARDED` | HIGH | quality | A control written while one Gate was the only Gate stops being a control when the next one starts | `test_expected_set_names_the_gate_specification`, `test_assurance_scope_covers_the_runtime_source`, `test_declared_suites_are_discovered`, `.iacode/policies/gate-scope.json`, `scripts/development-ledger/gate_transition_simulation.py` |
| `LSN-0033` | `GUARDED` | MEDIUM | implementation | A value bound in middleware is absent in the handlers that run outside it | `test_internal_error_still_carries_a_correlation_identifier`, `test_a_missing_route_uses_the_error_contract` |
| `LSN-0034` | `GUARDED` | MEDIUM | implementation | Re-deriving what the framework already computed diverges from the framework | `test_metrics_endpoint_exposes_request_metrics`, `test_metrics_label_routes_by_template_not_by_url`, `test_the_api_instruments_reach_prometheus` |
| `LSN-0035` | `GUARDED` | HIGH | tooling | Captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work | `test_no_capture_relies_on_the_platform_codepage`, `test_every_tool_that_re_emits_captured_output_configures_its_own_stream`, `test_the_rule_detects_a_capture_that_would_fail` |
| `LSN-0036` | `GUARDED` | HIGH | tooling | A gate that runs inside an image measures the image, not the source | `test_every_image_gate_builds_before_it_measures`, `test_the_image_gate_rule_detects_a_gate_that_would_skip_the_build` |
| `LSN-0037` | `GUARDED` | MEDIUM | tooling | A shared control that names an identifier the repository derives stops being a control when that identifier moves | `test_no_shared_control_is_bound_to_a_gate_literal`, `test_the_gate_literal_rule_detects_a_bound_control`, `test_no_control_names_a_migration_revision_literally`, `test_the_revision_rule_detects_a_named_head`, `test_the_head_revision_has_one_derivation` |
| `LSN-0038` | `GUARDED` | MEDIUM | implementation | Two representations of one concept in one module disagree, and the safer one loses | `test_a_documented_placeholder_is_not_redacted`, `test_both_redactors_agree_on_every_value_the_example_file_carries`, `test_no_module_writes_its_own_credential_name_rule`, `test_the_two_questions_stay_different` |
| `LSN-0039` | `GUARDED` | HIGH | testing | A test that writes to the operational database leaves production data behind | `test_the_operational_catalog_holds_only_providers_the_policy_declares` |
| `LSN-0040` | `GUARDED` | HIGH | checkpoint | A control that judges sealed history only runs once a successor anchors it | `test_every_sealed_checkpoint_validates_from_its_own_tag`, `test_the_recorder_never_declares_an_ignored_path_as_an_input`, `test_an_input_the_repository_carries_is_still_required_to_exist` |
| `LSN-0041` | `GUARDED` | HIGH | testing | An editing path that consumes a backslash escape leaves a control character, and the control it belonged to silently matches nothing | `test_no_source_file_carries_a_stray_control_character`, `test_the_scan_detects_one`, `test_the_page_offers_nothing_that_would_execute_a_tool`, `test_the_boundary_has_something_to_scan` |
| `LSN-0042` | `GUARDED` | HIGH | implementation | A naming convention rewrites a CHECK constraint's name and leaves a UNIQUE constraint's alone | `test_the_agent_runtime_migration_is_reversible`, `test_the_declared_model_matches_the_migrated_schema`, `test_a_check_constraint_is_created_and_dropped_by_its_bare_name`, `test_a_unique_constraint_keeps_exactly_the_name_it_was_given` |
| `LSN-0043` | `GUARDED` | MEDIUM | testing | A log line is not evidence that another process is ready | `test_readiness_is_asked_of_temporal`, `test_readiness_is_not_read_from_a_log_line`, `test_the_harness_asks_the_server_for_the_answer` |
| `LSN-0044` | `GUARDED` | HIGH | quality | A boundary scan must read the code rather than the prose, and must be shown to fire on a mutated module | `test_the_null_control_detects_a_mutation`, `test_the_provider_scan_would_catch_one`, `test_the_credential_scan_would_catch_one`, `test_the_scan_detects_a_module_that_does_it`, `test_the_determinism_scan_detects_a_module_that_breaks_it` |
| `LSN-0045` | `GUARDED` | MEDIUM | testing | A counted test suite must declare its cases statically, because the denominator is read from the source | `test_no_counted_pytest_case_expands_at_run_time`, `test_the_scan_detects_an_expansion` |
| `LSN-0046` | `GUARDED` | CRITICAL | implementation | A timeout that cancels the task it runs in leaves nothing able to record what happened | `scripts/iacode/scenarios/agent_runtime_deadline.py`, `test_the_engine_is_not_wrapped_in_wait_for`, `test_the_wait_accepts_every_way_a_cancelled_activity_surfaces`, `test_the_deadline_path_writes_the_failure_down`, `test_the_scenario_asserts_the_run_ended_and_said_so` |
| `LSN-0047` | `GUARDED` | HIGH | implementation | A refusal that misnames the defect spends the only repair on the wrong correction | `test_content_of_the_wrong_type_is_refused_by_its_real_defect`, `test_the_runtime_instructions_state_that_content_is_one_string`, `scripts/iacode/agent_runtime_smoke.py` |
| `LSN-0048` | `GUARDED` | HIGH | implementation | A state and the event that explains it, written in two commits, are written event first | `test_a_terminal_state_is_never_visible_before_its_terminal_event`, `test_the_workflow_writes_the_terminal_event_before_the_terminal_state`, `test_a_workflow_that_cannot_start_fails_the_run_rather_than_leaving_it_created`, `scripts/iacode/agent_runtime_smoke.py` |
| `LSN-0049` | `GUARDED` | MEDIUM | testing | A metric read the instant after the call that moved it is read before the scrape that carries it | `test_the_observability_check_waits_for_a_scrape_and_asks_only_prometheus`, `test_live_smoke_is_bounded_and_minimal`, `test_every_script_that_reads_prometheus_waits_for_a_scrape`, `test_the_scan_fires_on_a_read_that_does_not_wait`, `test_the_foundation_smoke_waits_for_both_targets_and_asks_only_prometheus` |
| `LSN-0050` | `GUARDED` | HIGH | checkpoint | A checkpoint sealed without naming its own tag cannot be validated from that tag | `test_sealing_refuses_a_state_that_does_not_name_its_own_tag`, `test_a_symbolic_head_validates_from_its_own_canonical_tag`, `test_a_symbolic_head_away_from_its_canonical_tag_is_still_refused`, `test_every_sealed_checkpoint_validates_from_its_own_tag` |
| `LSN-0051` | `GUARDED` | HIGH | implementation | A payload one service bounds for another must be bounded as the receiver measures it | `test_the_runtime_accepts_every_result_the_sandbox_hands_over`, `test_an_escaped_output_is_shortened_to_the_bound_and_says_so`, `test_an_output_that_fits_is_handed_over_unchanged` |
| `LSN-0052` | `GUARDED` | HIGH | architecture | Two processes that meet on a queue must name what crosses it once, and a real run must exercise both | `test_both_sides_name_the_result_by_the_shared_key`, `test_the_key_scan_detects_a_literal`, `test_the_activity_answers_the_agent_result_and_the_execution` |
| `LSN-0053` | `GUARDED` | HIGH | security | A process sweep that reads what a forking process holds waits on the processes it has to kill | `test_a_fork_bomb_that_detaches_leaves_a_sandbox_that_still_answers`, `test_a_fork_bomb_is_contained_by_the_process_limit`, `test_a_timeout_kills_the_whole_process_tree` |
| `LSN-0054` | `CONFIRMED` | MEDIUM | git | A pre-push check narrower than the change's reach lets a red gate reach the public remote | _not yet guarded_ |

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

- Status: `GUARDED`, severity CRITICAL, category quality, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0003, finding R6.
- Symptom: A quality dimension was recorded as PASS in a checkpoint that contained no corresponding execution.
- Root cause: Quality results were bare verdicts with no link to the run that produced them, so a verdict could be inherited from an earlier checkpoint without re-execution.
- Resolution: Every dimension records status, evidence and justification, and a PASS needs at least one reference that resolves to a successful command record or a non-empty file.
- Prevention:
  - `test` QualityEvidenceTests.test_pass_without_evidence_fails — A PASS with no evidence is rejected.
  - `test` QualityEvidenceTests.test_pass_referencing_a_failed_command_fails — A PASS pointing at a failed command is rejected.
  - `validator` scripts/development-ledger/validate_checkpoint.py — _validate_quality_evidence resolves every reference.
  - `invariant` validate_checkpoint._validate_quality_evidence — A PASS without resolvable evidence is refused for every positive terminal status.
  - `test` PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension — Every positive status is exercised against every mandatory red dimension.
- Evidence: `file:docs/adr/ADR-0007-checkpoint-schema-2-and-independent-promotion.md`, `file:docs/QUALITY-GATES.md`

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

- Status: `GUARDED`, severity CRITICAL, category process, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0005, finding prompt sections 9 and 10.
- Symptom: The independent tool was spending its effort discovering unimplemented requirements and missing evidence rather than auditing design.
- Root cause: No artifact held the complete requirement set, so completeness was a judgement made from memory of the conversation.
- Resolution: Requirements are extracted into REQUIREMENTS-MATRIX.json before implementation and audited by a validator that resolves every evidence reference and refuses anything short of total coverage.
- Prevention:
  - `test` DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails — Coverage below total fails the audit.
  - `test` DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review — An unexecuted completeness audit blocks readiness.
  - `validator` scripts/development-ledger/check_completeness.py — Completeness is recomputed over an independently derived expected set.
  - `test` ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails — Deleting a requirement and recomputing every count still fails.
- Evidence: `file:docs/adr/ADR-0008-delivery-assurance-gates.md`, `file:docs/checkpoints/SETUP-00-CP-0005/COMPLETENESS-REPORT.md`

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

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 2.
- Source: SETUP-00, SETUP-00-CP-0004, finding R3 (SETUP-00-CP-0004 review, decomposed as R3.2 in SETUP-00-CP-0005).
- Symptom: Recorded finalizer commands named a bare script that does not exist in the working directory they declared, so the ledger could not be replayed.
- Root cause: The record stored a convenient label rather than the literal invocation, and nothing checked that the label could be executed.
- Resolution: Records carry runtime, working directory, sanitized arguments, referenced inputs, repository commit, purpose and a canonical result, and validation rejects a command that does not start with an explicit runtime or whose script path does not resolve.
- Prevention:
  - `test` CommandReproducibilityTests.test_bare_script_name_is_rejected — A bare script name is rejected.
  - `test` CommandReproducibilityTests.test_unresolvable_script_path_is_rejected — A script path that does not resolve is rejected.
  - `schema` .iacode/schemas/command.schema.json — The reproducibility fields are part of the record contract.
  - `invariant` validate_checkpoint._validate_command_reproducibility — A record that names an input must bind it by content hash.
  - `test` CommandInputBindingTests.test_a_record_without_a_digest_is_rejected — A record without an input digest is refused.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0004/REVIEW-REPORT.md`, `file:scripts/development-ledger/record_command.py`

### LSN-0011 — A control over a checkpoint's own evidence must be scoped to the moment it matters

- Status: `GUARDED`, severity MEDIUM, category tooling, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0005, finding REWORK-LOG cycles 1 to 3 and 6.
- Symptom: The gate that validates the checkpoint kept failing because running it appends to the very ledger and inventory the validation binds.
- Root cause: Consistency rules written for a finished delivery were applied while the delivery was still writing its own evidence, which no ordering of steps can satisfy.
- Resolution: Gate consistency is enforced when the delivery is offered for review and treated as provisional while work is in progress, and the harness re-derives declared hashes immediately before validating.
- Prevention:
  - `test` DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress — Provisional in progress, strict at handoff.
  - `invariant` green_keeper._refresh_declared_hashes — Declared hashes are re-derived before the validation gate runs, never invented.
  - `test` test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes — Every command that executes the mandatory gate set re-derives the checkpoint's declared hashes before it does.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0005/DECISIONS.md`, `file:docs/checkpoints/SETUP-00-CP-0005/REWORK-LOG.jsonl`, `file:scripts/development-ledger/finalize_checkpoint.py`, `file:scripts/iacode/verify.py`, `file:tests/test_gate1_model_gateway.py`

### LSN-0012 — Sealed checkpoints and their tags are immutable, and tooling must keep validating them

- Status: `GUARDED`, severity CRITICAL, category git, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0002, finding checkpoint protocol.
- Symptom: Every correction cycle created pressure to edit or retag an earlier checkpoint so the new rules would fit it.
- Root cause: Control-plane rules evolve while history does not, so without version dispatch a new rule silently invalidates sealed evidence.
- Resolution: Checkpoints declare a schema version, validation applies the rules of the declared version, and a regression validates clean clones detached at every sealed tag.
- Prevention:
  - `test` HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates — The first sealed checkpoint still validates.
  - `test` HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates — The most recent sealed review checkpoint still validates.
  - `policy` docs/CHECKPOINT-PROTOCOL.md — Schema versions and immutability are stated in the protocol.
  - `validator` scripts/development-ledger/anchors.py — The sealed chain of tags, commits and trees is re-derived from Git.
  - `test` IntegrityAnchorTests.test_a_moved_historical_tag_is_detected — A moved historical tag is detected.
- Evidence: `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/adr/ADR-0007-checkpoint-schema-2-and-independent-promotion.md`

### LSN-0013 — An installed capability must be detected by resolved path, not by a bare command lookup

- Status: `CONFIRMED`, severity MEDIUM, category environment, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0002, finding detection correction.
- Symptom: A checkpoint recorded that a tool was not installed because a bare command lookup failed, when the tool was installed outside the detecting process PATH.
- Root cause: Absence was inferred from one lookup mechanism rather than from a search of resolved locations, so a configuration detail was recorded as a capability fact.
- Resolution: Capability records name the resolved executable path and the version it reported, and a failed bare lookup is recorded as a PATH observation rather than as absence.
- Prevention:
  - `documentation` docs/TOOL-CAPABILITIES.md — Detected capabilities are recorded with resolved paths and the PATH caveat.
- Evidence: `file:docs/TOOL-CAPABILITIES.md`, `file:docs/adr/ADR-0003-tool-neutral-agents.md`, `file:docs/checkpoints/SETUP-00-CP-0002/DECISIONS.md`

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

- Status: `GUARDED`, severity CRITICAL, category tooling, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-004 / M0-F-003.
- Symptom: A GUARDED lesson naming a nonexistent test, a lesson citing a nonexistent evidence file, and a secret-shaped value nested in prevention.description all validated.
- Root cause: Validation checked that a field had the right shape and never asked the repository whether the thing it named exists.
- Resolution: Every control reference, evidence path and derived artifact is resolved against the repository and the discovered test suite, and the whole object is scanned for secrets at any depth.
- Prevention:
  - `invariant` lessons.resolve_control — Every control reference is resolved against the suite or the repository.
  - `test` LessonResolutionTests.test_a_test_control_must_exist_in_the_suite — A control naming a nonexistent test is refused.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`, `file:docs/checkpoints/SETUP-00-CP-0007/AUDIT-EXECUTIONS.md`

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

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-009 / M0-F-010.
- Symptom: Sampled commands replayed at the sealed tag but failed at their own declared commits, and a run claimed to finish three seconds before the finalizer that sealed it ran.
- Root cause: A record named a commit while its real inputs lived only in an uncommitted working tree, and the sealing order let the recorded chronology contradict itself.
- Resolution: Every record binds its declared inputs by content hash, and sealing is a monotonic post-commit workflow whose final validation is recorded against a clean tree at the sealed content commit.
- Prevention:
  - `invariant` ledger_common.build_command_record — Every declared input is bound by content hash at execution time.
  - `test` CommandInputBindingTests.test_the_recorder_binds_inputs_automatically — The recorder binds inputs without being asked.
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

- Status: `GUARDED`, severity CRITICAL, category documentation, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0007, finding M0-F-008.
- Symptom: The sealed CP-0006 state declared 47 mandatory requirements while the matrix and the completeness report both computed 45, and validation never compared them.
- Root cause: The same number was written by hand in several artifacts, so the artifacts could disagree without any tool noticing.
- Resolution: Counts used as evidence are derived into one machine-readable artifact, cross-checked against state and report aggregates, and verified wherever a report states them.
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

- Status: `GUARDED`, severity CRITICAL, category process, recurrences 1.
- Source: SETUP-00, SETUP-00-CP-0009, finding CP9-F-002.
- Symptom: Carrying out a step the checkpoint protocol requires of every successor, anchoring its sealed predecessor, took the mandatory suite from green to red and left editing a guardrail test as the only apparent remedy.
- Root cause: The controls were written against one repository state instead of against the sequence of states the protocol itself produces.
- Resolution: The successor durability simulation seals a chain of checkpoints and re-runs the controls at every state, so a transition that breaks a gate is found by the delivery that introduces it rather than by the next audit.
- Prevention:
  - `automated-check` scripts/development-ledger/successor_durability.py — The protocol's own next steps are executed and the gates re-checked.
  - `test` SuccessorDurabilityTests.test_every_state_of_the_chain_verifies — Every state of an advancing chain keeps the controls green.
  - `automated-check` scripts/development-ledger/gate_transition_simulation.py — The transition into the first delivery of the next Gate is executed before handoff.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md`, `file:scripts/development-ledger/successor_durability.py`, `file:docs/CHECKPOINT-PROTOCOL.md`

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

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 0.
- Source: GATE-0, GATE-0-CP-0001, finding G0-F-004.
- Symptom: The Green Keeper aborted with UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d while reading the output of a gate that was green. After the read was repaired, the command recorder aborted with UnicodeEncodeError: 'charmap' codec can't encode character '�' while printing what it had just captured -- after an eighteen-minute verification had already passed.
- Root cause: Both ends inherit the machine's codepage. subprocess.run(..., text=True) with no encoding decodes with locale.getencoding(), and sys.stdout encodes with it as well; on Windows that is cp1252, while every tool here writes UTF-8. The failure is intermittent because it depends on which character the measured process happened to print, and it lands after the work succeeded, so it destroys a result rather than reporting one.
- Resolution: Eleven captures now state encoding="utf-8" with errors="replace", and every entry point that re-emits what it captured configures its own streams the same way -- directly through ledger_common.use_utf8_stdout, or through compose.main_guard, which every operational script goes through. Both directions are stated rather than inherited.
- Prevention:
  - `test` test_no_capture_relies_on_the_platform_codepage — Every subprocess capture in the tree is parsed and must state its encoding.
  - `test` test_every_tool_that_re_emits_captured_output_configures_its_own_stream — Every entry point that captures also configures the stream it writes to.
  - `test` test_the_rule_detects_a_capture_that_would_fail — The rule is exercised against a call it must reject.
- Evidence: `file:tests/test_gate0_foundation.py`, `file:scripts/development-ledger/ledger_common.py`, `file:scripts/iacode/compose.py`

### LSN-0036 — A gate that runs inside an image measures the image, not the source

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 0.
- Source: GATE-1, GATE-1-CP-0001, finding G1-F-001.
- Symptom: A red test was found at HEAD during GATE 1: test_a_documented_placeholder_is_not_redacted failed because the redactor's placeholder pattern read change[-_]?me\b while the repository's documented placeholder is change-me-before-starting. The test had existed and the apiTests gate had reported PASS throughout GATE 0.
- Root cause: The apiTests gate executes pytest inside the API image, and nothing rebuilt that image before measuring. The gate therefore reported on whatever source happened to be baked into the last build. A gate in that shape does not fail when the code is wrong; it reports on code nobody is running, so a defect can be introduced, committed and sealed behind a green gate.
- Resolution: compose.build_service(service) was added and every gate whose command executes inside an image calls it before measuring. Building costs a cached layer check when nothing changed. The redaction defect it had been hiding was fixed separately (LSN-0038).
- Prevention:
  - `test` test_every_image_gate_builds_before_it_measures — Every gate command that runs inside an image builds that image first.
  - `test` test_the_image_gate_rule_detects_a_gate_that_would_skip_the_build — The rule is exercised against a gate module it must reject.
- Evidence: `file:scripts/iacode/compose.py`, `file:scripts/iacode/gates/api_tests.py`, `file:scripts/iacode/gates/gateway_tests.py`, `file:tests/test_gate1_model_gateway.py`

### LSN-0037 — A shared control that names an identifier the repository derives stops being a control when that identifier moves

- Status: `GUARDED`, severity MEDIUM, category tooling, recurrences 1.
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
- Evidence: `file:scripts/development-ledger/policies.py`, `file:scripts/development-ledger/ledger_common.py`, `file:scripts/development-ledger/gate0_red_team.py`, `file:tests/test_gate0_foundation.py`, `file:apps/api/migrations/head.py`, `file:scripts/iacode/scenarios/fresh_install.py`

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

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
- Source: GATE-1, GATE-1-CP-0001, finding G1-F-007.
- Symptom: MIR-016 failed with GATE-0-CP-0001: CHECKPOINT_INVALID. Six of that sealed checkpoint's recorded commands name var/verify-report.json as an input; var/ is ignored by Git, so no checkout of the tag carries it, and the validator required every declared input to exist.
- Root cause: Two causes in one failure. The recorder declared a generated, ignored artifact as a command input, which makes the record unreplayable from a checkout. And the defect was invisible for a whole Gate because a checkpoint cannot anchor its own tag: GATE-0-CP-0001 entered the anchor chain only when its successor built the chain, so the first execution of the control over it happened one Gate after the content it judges was sealed.
- Resolution: The recorder no longer declares a path Git ignores as an input, so the situation cannot recur. The validator accepts an ignored input that is absent only when the record binds its content by digest; every path the repository carries must still resolve, and an ignored input with no digest is still refused. Sealed history was not rewritten.
- Prevention:
  - `test` test_every_sealed_checkpoint_validates_from_its_own_tag — Every anchored checkpoint validates from a detached checkout of its tag, asserted by the suite rather than only by the mirror audit.
  - `test` test_the_recorder_never_declares_an_ignored_path_as_an_input — A generated artifact is never recorded as a command input.
  - `test` test_an_input_the_repository_carries_is_still_required_to_exist — The rule still refuses a reference that resolves to nothing.
- Evidence: `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/record_command.py`, `file:tests/test_gate1_model_gateway.py`

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

- Status: `GUARDED`, severity HIGH, category implementation, recurrences 0.
- Source: GATE-2, GATE-2-CP-0001, finding G2-F-002.
- Symptom: Dropping a check constraint by its full name produced ALTER TABLE task_runs DROP CONSTRAINT ck_task_runs_ck_task_runs_status_is_known, and creating a unique constraint by its full name produced one the downgrade could not find, which failed three migration suites at once.
- Root cause: The declarative naming convention is applied only when the template for that constraint kind contains the constraint-name token. The CHECK template does; the UNIQUE template does not. So a check constraint is named by its bare name and a unique constraint keeps exactly what it is given, and using one rule for both is wrong in one direction or the other.
- Resolution: The migration creates and drops a check constraint by its bare name and a unique constraint by exactly the name the model declares, and states the asymmetry in a comment where the code is. The reversibility test applies and reverses the migration against a disposable database, so a mismatch is a failing test rather than a failed downgrade in an incident.
- Prevention:
  - `test` test_the_agent_runtime_migration_is_reversible — The migration is applied and reversed against a disposable database, which is what a name mismatch breaks.
  - `test` test_the_declared_model_matches_the_migrated_schema — Autogenerate against a freshly migrated database finds nothing left to do, which a name mismatch would report.
  - `test` test_a_check_constraint_is_created_and_dropped_by_its_bare_name — The migration uses the bare name for a check constraint.
  - `test` test_a_unique_constraint_keeps_exactly_the_name_it_was_given — The migration uses the declared name for a unique constraint, on both sides.
- Evidence: `file:apps/api/migrations/versions/0003_agent_runtime.py`, `file:apps/api/tests/integration/test_migrations.py`, `file:packages/persistence/src/iacode_persistence/base.py`

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

- Status: `GUARDED`, severity MEDIUM, category testing, recurrences 0.
- Source: GATE-2, GATE-2-CP-0001, finding G2-F-007.
- Symptom: Ninety-five cases of the ledger suite errored at once, all of them on the same message: a test in a counted suite is parametrised and the TESTS denominator cannot reproduce a runtime expansion.
- Root cause: The denominator is derived by reading the source, so a case produced at run time by a parametrisation cannot be counted. The counter already refuses one, but it refuses from inside the counting step, several layers below the file that caused it, so the failure arrives as a wall of unrelated-looking errors rather than as a statement about one function.
- Resolution: Every case in a counted pytest suite is written as a loop over a module-level tuple, which counts as one case and covers the same inputs. A repository test asks the same question of the same files and fails fast, naming the file and the function.
- Prevention:
  - `test` test_no_counted_pytest_case_expands_at_run_time — No test function in a counted pytest suite carries a parametrisation.
  - `test` test_the_scan_detects_an_expansion — The null control: the same scan fires on a parametrised module and stays quiet on a plain one.
- Evidence: `file:tests/test_gate2_agent_runtime.py`, `file:scripts/development-ledger/derive_counts.py`, `file:.iacode/policies/test-suites.json`

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

- Status: `GUARDED`, severity MEDIUM, category testing, recurrences 1.
- Source: GATE-2, GATE-2-CP-0002, finding G2-F-012.
- Symptom: The live gateway smoke failed one check of twenty on a call that had succeeded: observability.scraped found no gateway request series. The stack had been rebuilt seconds before, so the API's counter had restarted and Prometheus had not scraped it since the smoke's own requests.
- Root cause: The check asked Prometheus once, immediately after the inference, while Prometheus scrapes the API every fifteen seconds. Whether the counter had been scraped yet was a matter of timing, so the check passed on a stack that had been running for a while and failed on a freshly started one - the result described the clock, not the gateway.
- Resolution: The check waits for the scrape, bounded by three scrape intervals and polling only Prometheus: the provider is never called again to make the metric appear, so the live check stays one inference and one stream.
- Prevention:
  - `test` test_the_observability_check_waits_for_a_scrape_and_asks_only_prometheus — A scrape that arrives after the call is waited for, one that never arrives fails within the bound, and every read goes to Prometheus.
  - `test` test_live_smoke_is_bounded_and_minimal — The live check still makes exactly one inference and one stream.
  - `test` test_every_script_that_reads_prometheus_waits_for_a_scrape — Every script that reads Prometheus's API waits for a scrape within a bound; the control is the class, read from the syntax tree.
  - `test` test_the_scan_fires_on_a_read_that_does_not_wait — The null control of that scan.
  - `test` test_the_foundation_smoke_waits_for_both_targets_and_asks_only_prometheus — The Foundation smoke waits for both targets and asks only Prometheus.
- Evidence: `file:scripts/iacode/gateway_smoke.py`, `file:tests/test_gate1_model_gateway.py`, `file:infra/prometheus/prometheus.yml`, `file:scripts/iacode/smoke.py`, `file:tests/test_gate2_agent_runtime.py`

### LSN-0050 — A checkpoint sealed without naming its own tag cannot be validated from that tag

- Status: `GUARDED`, severity HIGH, category checkpoint, recurrences 0.
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

- Status: `GUARDED`, severity HIGH, category security, recurrences 0.
- Source: GATE-3, GATE-3-CP-0001, finding G3-F-004.
- Symptom: A fork bomb that detached from its command wedged a sandbox: the sweep after the command killed a handful of processes in fifteen seconds, the survivors refilled the process table, and the next command could not be started.
- Root cause: The sweep read every process's command line, which takes that process's memory lock, held by a process in the middle of a fork; and it killed without stopping first, so every slot it freed was refilled before its next round.
- Resolution: The sweep lists processes and reads only their state, stops every one until no new process appears, and then kills them, with a separate budget for each phase.
- Prevention:
  - `test` test_a_fork_bomb_that_detaches_leaves_a_sandbox_that_still_answers — A detached bomb is swept and the sandbox answers the next command with an empty process table.
  - `test` test_a_fork_bomb_is_contained_by_the_process_limit — A bomb that stays attached is contained by the limit and ended at its timeout.
  - `test` test_a_timeout_kills_the_whole_process_tree — The same sweep ends a command's escaped children.
- Evidence: `file:services/sandbox/src/iacode_sandbox/helper.py`, `file:scripts/development-ledger/gate3_sandbox_attacks.py`, `file:docs/checkpoints/GATE-3-CP-0001/DECISIONS.md`

### LSN-0054 — A pre-push check narrower than the change's reach lets a red gate reach the public remote

- Status: `CONFIRMED`, severity MEDIUM, category git, recurrences 0.
- Source: GATE-3, GATE-3-CP-0001, finding G3-F-002.
- Symptom: Three pushed commits left a mandatory gate red: the first broke the repository-wide decoding scan, two later ones the lint gate. Each ran the suites of what it changed, not the repository-wide gates the change could reach.
- Root cause: The pre-push check was chosen by the commit's subject rather than by its reach: a new script is reached by the scans over every script, and any source file by the lint gate.
- Resolution: Each was repaired by a new commit, never an amend; from then on every push ran the lint gate and the repository-wide scans in addition to the suites of the change.
- Prevention:
  - `documentation` docs/DEVELOPMENT-CONTRACT.md — Before each push: status, the staged diff, a secret scan of the staged content and the tests the change can reach.
- Evidence: `file:docs/checkpoints/GATE-3-CP-0001/DECISIONS.md`, `file:docs/DEVELOPMENT-CONTRACT.md`
