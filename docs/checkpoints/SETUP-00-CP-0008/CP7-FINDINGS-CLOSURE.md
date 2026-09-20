# CP-0007 Findings Closure

Result: `CLOSED`

- Audit: `M0-CP-0007`
- Source: `docs/checkpoints/SETUP-00-CP-0007/REVIEW-REPORT.md`
- Closed: `11/11 FINDINGS`

Every finding below is re-parsed from the sealed review report, not transcribed, so a finding
cannot be dropped by editing this file.

| Finding | Severity | Status | Root cause | Regression |
|---|---|---|---|---|
| `M0-F-001` | CRITICAL | `CLOSED` | The promotion rules were attached to one status rather than to the concept of a positive terminal status, so every other status began with no rules. | `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`, `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_completeness_gate` |
| `M0-F-002` | CRITICAL | `CLOSED` | The external verdict was a field of the checkpoint that benefits from it, so the delivery could write its own approval. | `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`, `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough` |
| `M0-F-003` | CRITICAL | `CLOSED` | Freshness was judged by comparing an artifact with a copy of its own counts, and by a timestamp, instead of by recomputing it from its inputs. | `test:PreflightFreshnessTests.test_a_changed_fingerprint_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_preflight_from_another_gate_is_refused` |
| `M0-F-004` | CRITICAL | `CLOSED` | Validation checked that a field had the right shape and never asked the repository whether the thing it named exists; the secret scan covered a fixed list of fields. | `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`, `test:LessonResolutionTests.test_lesson_evidence_must_resolve` |
| `M0-F-005` | CRITICAL | `CLOSED` | The tool asked its caller which gates were mandatory; a control whose scope is an argument can always be reduced to nothing. | `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_the_policy_declares_a_non_empty_closed_set` |
| `M0-F-006` | CRITICAL | `CLOSED` | Coverage was computed over the submitted set, so the submitted set decided what total coverage meant. | `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`, `test:ExpectedRequirementSetTests.test_the_expected_set_is_derived_from_the_canonical_sources` |
| `M0-F-007` | CRITICAL | `CLOSED` | Every expected value lived inside the mutable checkpoint content, so a coordinated edit left nothing to contradict. | `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`, `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected` |
| `M0-F-008` | HIGH | `CLOSED` | The same authoritative number was written by hand in several artifacts, so they could disagree without any tool noticing. | `test:ExpectedRequirementSetTests.test_the_state_mandatory_count_is_cross_checked`, `test:DerivedCountTests.test_the_stored_counts_match_the_derivation` |
| `M0-F-009` | HIGH | `CLOSED` | A record named a commit while its real inputs lived only in an uncommitted working tree. | `test:CommandInputBindingTests.test_a_bound_record_passes`, `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically` |
| `M0-F-010` | HIGH | `CLOSED` | Sealing was not an ordered workflow: the end of the run was stamped before the records the run still had to write, and the final validation ran against an uncommitted tree. | `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected`, `test:DeliveryLifecycleTests.test_full_delivery_assurance_flow_reaches_ready_for_review` |
| `M0-F-011` | MEDIUM | `CLOSED` | Provenance was written from recollection of where a finding had been discussed, and nothing resolved the citation against the cited checkpoint. | `test:LessonProvenanceTests.test_every_repository_lesson_cites_a_resolvable_source`, `test:LessonProvenanceTests.test_a_correct_locator_resolves` |

## Detail

### M0-F-001 - positive terminal status bypasses delivery assurance

- Expected: MILESTONE_EXTERNAL_PASS is rejected when any mandatory assurance dimension is red.
- Observed: The strong checks were written only for READY_FOR_REVIEW, so a mutated MILESTONE_EXTERNAL_PASS with greenKeeper.status=FAIL produced no error.
- Root cause: The promotion rules were attached to one status rather than to the concept of a positive terminal status, so every other status began with no rules.
- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`, `POSITIVE_TERMINAL_STATUSES and one shared invariant in _validate_delivery_assurance`
- Regression test: `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`, `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_completeness_gate`
- Negative test: `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`, `test:PromotionInvariantTests.test_every_positive_status_rejects_an_unexecuted_mandatory_dimension`, `test:PromotionInvariantTests.test_every_positive_status_rejects_a_partial_requirement`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0015`, guardrail `GRD-0014`
- Status: `CLOSED`

### M0-F-002 - external milestone PASS can be self-asserted on an intermediate Gate

- Expected: An intermediate Gate with externalAuditRequired=false is rejected as MILESTONE_EXTERNAL_PASS.
- Observed: Syntactically filled second-tool metadata, milestone.status=PASSED and matching status text were accepted with no external evidence and both independent verdicts pending.
- Root cause: The external verdict was a field of the checkpoint that benefits from it, so the delivery could write its own approval.
- Implementation: `file:scripts/development-ledger/attestation.py`, `file:.iacode/schemas/external-audit-attestation.schema.json`, `resolve_external_pass wired into _validate_memory_policy`
- Regression test: `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`, `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough`
- Negative test: `test:ExternalAttestationTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:ExternalAttestationTests.test_a_failed_review_cannot_produce_an_external_pass`, `test:ExternalAttestationTests.test_a_failed_red_team_cannot_produce_an_external_pass`, `test:ExternalAttestationTests.test_an_intermediate_gate_cannot_take_the_external_status`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0007`, guardrail `GRD-0008`
- Status: `CLOSED`

### M0-F-003 - lesson preflight is not bound to the checkpoint Gate or canonical memory

- Expected: A GATE 1 state cannot reuse a SETUP-00 preflight, and retiring a lesson invalidates a stale active preflight.
- Observed: Both mutations were accepted: state and artifact were compared with one another rather than with STATE.gate or a recomputation of the canonical memory.
- Root cause: Freshness was judged by comparing an artifact with a copy of its own counts, and by a timestamp, instead of by recomputing it from its inputs.
- Implementation: `file:scripts/development-ledger/lessons.py`, `preflight_fingerprint, preflight_staleness and the Gate binding in _validate_memory_policy`
- Regression test: `test:PreflightFreshnessTests.test_a_changed_fingerprint_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_preflight_from_another_gate_is_refused`
- Negative test: `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_the_checkpoint_refuses_a_stale_preflight`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0019`, guardrail `GRD-0018`
- Status: `CLOSED`

### M0-F-004 - Engineering Memory accepts forged controls, missing evidence, and nested secrets

- Expected: A nonexistent test reference, a nonexistent evidence path, and a secret-shaped value in prevention.description are all rejected.
- Observed: Each independent in-memory mutation returned errors=[].
- Root cause: Validation checked that a field had the right shape and never asked the repository whether the thing it named exists; the secret scan covered a fixed list of fields.
- Implementation: `file:scripts/development-ledger/lessons.py`, `resolve_control, resolve_lesson_evidence and the recursive _walk_strings secret scan`
- Regression test: `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`, `test:LessonResolutionTests.test_lesson_evidence_must_resolve`
- Negative test: `test:LessonResolutionTests.test_an_invariant_control_must_be_defined_in_the_tooling`, `test:LessonResolutionTests.test_a_control_path_may_not_escape_the_repository`, `test:LessonValidationTests.test_secret_in_a_lesson_fails`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0018`, guardrail `GRD-0017`
- Status: `CLOSED`

### M0-F-005 - Green Keeper has a vacuous PASS path

- Expected: An empty gate selection is rejected.
- Observed: green_keeper.py --gates "" exited zero and wrote GREEN_KEEPER_GATE=PASS with empty evidence, and the checkpoint validator accepted it beside a failing test.
- Root cause: The tool asked its caller which gates were mandatory; a control whose scope is an argument can always be reduced to nothing.
- Implementation: `file:.iacode/policies/quality-gates.json`, `file:scripts/development-ledger/green_keeper.py`, `_validate_green_keeper_cycle in validate_checkpoint.py`
- Regression test: `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_the_policy_declares_a_non_empty_closed_set`
- Negative test: `test:MandatoryGatePolicyTests.test_a_cycle_missing_one_mandatory_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_a_mandatory_gate_that_exited_nonzero_is_rejected`, `test:MandatoryGatePolicyTests.test_a_gate_without_command_evidence_is_rejected`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0016`, guardrail `GRD-0015`
- Status: `CLOSED`

### M0-F-006 - completeness denominator is not anchored

- Expected: Deleting REQ-0001 is detected even when every stored count is recomputed.
- Observed: The matrix shrank from 47 to 46 and both completeness and checkpoint validation passed at 100%.
- Root cause: Coverage was computed over the submitted set, so the submitted set decided what total coverage meant.
- Implementation: `file:scripts/development-ledger/policies.py`, `file:.iacode/policies/canonical-requirements.json`, `expected_requirement_refs and compare_requirement_sets wired into evaluate_matrix`
- Regression test: `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`, `test:ExpectedRequirementSetTests.test_the_expected_set_is_derived_from_the_canonical_sources`
- Negative test: `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`, `test:ExpectedRequirementSetTests.test_a_requirement_without_an_anchor_is_rejected`, `test:ExpectedRequirementSetTests.test_a_downgraded_matrix_cannot_escape_the_comparison`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0017`, guardrail `GRD-0016`
- Status: `CLOSED`

### M0-F-007 - historical immutability is not anchored externally

- Expected: Moving a historical tag or rewriting a predecessor remains detectable after coordinated metadata and hash changes.
- Observed: Moving the tag and HEAD together validated, and a CP-0005 rewrite declared in the CP-0006 inventory with refreshed hashes and a moved tag also validated.
- Root cause: Every expected value lived inside the mutable checkpoint content, so a coordinated edit left nothing to contradict.
- Implementation: `file:scripts/development-ledger/anchors.py`, `file:.iacode/anchors/checkpoint-chain.json`, `file:scripts/development-ledger/verify_integrity.py`
- Regression test: `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`, `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected`
- Negative test: `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`, `test:IntegrityAnchorTests.test_a_recomputed_anchor_hash_must_match_its_fields`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0021`, guardrail `GRD-0020`
- Status: `CLOSED`

### M0-F-008 - CP-0006 mandatory count is contradictory and accepted

- Expected: Matrix, completeness report and state aggregates agree.
- Observed: The matrix and the report computed 45 mandatory requirements while the sealed CP-0006 state said 47, and validation never compared them.
- Root cause: The same authoritative number was written by hand in several artifacts, so they could disagree without any tool noticing.
- Implementation: `file:scripts/development-ledger/derive_counts.py`, `the mandatory cross-check in _validate_delivery_assurance and _validate_derived_counts`, `checkpoint:COUNTS.json`
- Regression test: `test:ExpectedRequirementSetTests.test_the_state_mandatory_count_is_cross_checked`, `test:DerivedCountTests.test_the_stored_counts_match_the_derivation`
- Negative test: `test:DerivedCountTests.test_a_forged_count_is_rejected`, `test:DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0022`, guardrail `GRD-0021`
- Status: `CLOSED`

### M0-F-009 - command records are not reproducible at their declared commits

- Expected: Sampled completed commands reproduce their recorded exit code at the recorded commit.
- Observed: CP-0006 cmd-0012 pointed at an input absent at its commit and CP-0005 cmd-0028 failed at its commit; both were recorded from a dirty tree whose inputs were not content-bound.
- Root cause: A record named a commit while its real inputs lived only in an uncommitted working tree.
- Implementation: `file:scripts/development-ledger/ledger_common.py`, `inputsDigest in build_command_record and the replay context check in _validate_command_reproducibility`
- Regression test: `test:CommandInputBindingTests.test_a_bound_record_passes`, `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically`
- Negative test: `test:CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`, `test:CommandInputBindingTests.test_a_digest_that_omits_an_input_is_rejected`, `test:CommandInputBindingTests.test_a_clean_tree_claim_is_checked_against_the_declared_commit`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0020`, guardrail `GRD-0019`
- Status: `CLOSED`

### M0-F-010 - sealed finalization chronology is internally inconsistent

- Expected: A run cannot finish before its recorded finalizer, and the final validator evidence binds the sealed commit.
- Observed: CP-0006 recorded finishedAt three seconds before the finalizer that sealed it, and its last evidence referenced a pre-tag commit with a dirty tree.
- Root cause: Sealing was not an ordered workflow: the end of the run was stamped before the records the run still had to write, and the final validation ran against an uncommitted tree.
- Implementation: `file:scripts/development-ledger/seal_checkpoint.py`, `the monotonic finishedAt in finalize_checkpoint.py`, `_validate_seal_chronology in validate_checkpoint.py`
- Regression test: `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected`, `test:DeliveryLifecycleTests.test_full_delivery_assurance_flow_reaches_ready_for_review`
- Negative test: `test:SealChronologyTests.test_a_missing_post_commit_validation_is_rejected`, `test:SealChronologyTests.test_a_dirty_tree_validation_is_not_evidence_of_a_sealed_commit`, `test:SealChronologyTests.test_a_validation_of_an_unrelated_commit_is_rejected`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0014`, guardrail `GRD-0013`
- Status: `CLOSED`

### M0-F-011 - one lesson source locator is inaccurate

- Expected: LSN-0007 locates both cited findings accurately.
- Observed: It attributed R4 and R7 to SETUP-00-CP-0003, while R7 is recorded in SETUP-00-CP-0004.
- Root cause: Provenance was written from recollection of where a finding had been discussed, and nothing resolved the citation against the cited checkpoint.
- Implementation: `file:.iacode/memory/lessons.jsonl`, `_resolve_source_locator in lessons.py`
- Regression test: `test:LessonProvenanceTests.test_every_repository_lesson_cites_a_resolvable_source`, `test:LessonProvenanceTests.test_a_correct_locator_resolves`
- Negative test: `test:LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected`, `test:LessonProvenanceTests.test_a_nonexistent_checkpoint_is_rejected`
- Verification: `python -m unittest discover -s tests`
- Lesson: `LSN-0023`, guardrail `GRD-0022`
- Status: `CLOSED`
