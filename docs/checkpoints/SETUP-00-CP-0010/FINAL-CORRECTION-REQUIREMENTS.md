# Final Correction Requirements

- Checkpoint: `SETUP-00-CP-0010`
- Audit: `M0-CP-0009`
- Rows: `32`, complete `32`, partial `0`, missing `0`
- Coverage: `100.0` per cent; evidence coverage `100.0` per cent

The canonical requirement set of this delivery is REQUIREMENTS-MATRIX.json, derived from policy. This artifact is the correction view the CP-0009 audit and the corrective prompt require: one row per finding, per named regression scenario and per positive path, each separating positive from negative evidence.

| Requirement | Source | Status | Positive | Negative | Other evidence |
|---|---|---|---|---|---|
| `CORR-0001` | CP9-F-001 | `COMPLETE` | 2 | 2 | 8 |
| `CORR-0002` | CP9-F-002 | `COMPLETE` | 2 | 2 | 7 |
| `CORR-0003` | CP9-F-003 | `COMPLETE` | 1 | 1 | 7 |
| `CORR-0004` | CP9-F-004 | `COMPLETE` | 0 | 1 | 6 |
| `CORR-0005` | CP9-F-005 | `COMPLETE` | 0 | 1 | 7 |
| `CORR-0101` | CP9-F-001 regression: valid attestation accepted end to end | `COMPLETE` | 2 | 0 | 2 |
| `CORR-0102` | CP9-F-001 regression: the audit checkpoint can be sealed | `COMPLETE` | 2 | 0 | 2 |
| `CORR-0103` | CP9-F-001 regression: the subject commit, tag and tree are unchanged | `COMPLETE` | 1 | 0 | 2 |
| `CORR-0104` | CP9-F-001 regression: no self-referential commit requirement | `COMPLETE` | 0 | 1 | 3 |
| `CORR-0105` | CP9-F-001 regression: the audit does not stale the subject's assurance | `COMPLETE` | 2 | 0 | 2 |
| `CORR-0106` | CP9-F-001 regression: wrong subject, commit, auditor and results rejected | `COMPLETE` | 0 | 10 | 2 |
| `CORR-0107` | CP9-F-001 regression: the mechanism decides the status | `COMPLETE` | 0 | 4 | 6 |
| `CORR-0108` | CP9-F-001 regression: integrity validation still works | `COMPLETE` | 1 | 1 | 2 |
| `CORR-0201` | CP9-F-002 regression: synthetic succession | `COMPLETE` | 4 | 0 | 2 |
| `CORR-0202` | CP9-F-002 regression: removing an anchor still fails | `COMPLETE` | 0 | 2 | 2 |
| `CORR-0203` | CP9-F-002 regression: one canonical exclusion rule | `COMPLETE` | 0 | 0 | 5 |
| `CORR-0204` | CP9-F-002 regression: no literal historical identifier in generic logic | `COMPLETE` | 0 | 0 | 5 |
| `CORR-0301` | CP-0009 disclosure: additive test counts | `COMPLETE` | 0 | 1 | 8 |
| `CORR-0302` | CP-0009 disclosure: ambiguous Red Team totals | `COMPLETE` | 0 | 0 | 4 |
| `CORR-0303` | CP-0009 disclosure: adversarial batteries need a null-mutation control | `COMPLETE` | 0 | 2 | 5 |
| `CORR-0401` | Prompt section 26: the eight CP-0009 lesson candidates are assessed | `COMPLETE` | 0 | 0 | 4 |
| `CORR-0402` | Prompt sections 27 to 29: the three named lessons exist and are guarded | `COMPLETE` | 0 | 0 | 6 |
| `CORR-0403` | Prompt section 30: the preflight is regenerated and fresh | `COMPLETE` | 0 | 0 | 3 |
| `CORR-0404` | CP9 candidate 007: the preflight has no audit-role subset | `COMPLETE` | 0 | 0 | 4 |
| `CORR-0501` | Prompt section 31: Green Keeper | `COMPLETE` | 0 | 0 | 2 |
| `CORR-0502` | Prompt section 32: Delivery Completeness | `COMPLETE` | 0 | 0 | 3 |
| `CORR-0503` | Prompt section 33: internal positive promotion simulation | `COMPLETE` | 1 | 0 | 2 |
| `CORR-0504` | Prompt section 34: internal successor durability simulation | `COMPLETE` | 1 | 0 | 2 |
| `CORR-0505` | Prompt section 35: the whole suite passes | `COMPLETE` | 0 | 0 | 3 |
| `CORR-0506` | Prompt section 36: clean clone | `COMPLETE` | 0 | 0 | 2 |
| `CORR-0507` | Prompt section 37: internal closure audit | `COMPLETE` | 0 | 0 | 3 |
| `CORR-0508` | Prompt section 38: affected Red Team scenarios | `COMPLETE` | 0 | 0 | 3 |

## CORR-0001 — CP9-F-001

A milestone verdict is carried by the audit checkpoint about a sealed subject, and the positive promotion path is reachable end to end.

- Implementation: `file:scripts/development-ledger/attestation.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/milestone_status.py`
- Tests: `test:AuditAttestationModelTests.test_a_legitimate_attestation_over_the_sealed_history_is_accepted`
- Positive path: `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:PositivePromotionTests.test_the_audit_checkpoint_validates_as_sealed`
- Negative path: `test:AuditAttestationModelTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:AuditAttestationModelTests.test_a_checkpoint_may_not_claim_a_verdict_another_checkpoint_authored`
- Documentation: `file:docs/adr/ADR-0011-audit-checkpoint-carries-the-verdict.md`, `file:docs/MILESTONE-VALIDATION.md`
- Validation: `checkpoint:CP9-FINDINGS-CLOSURE.json`, `checkpoint:POSITIVE-PROMOTION-VALIDATION.json`
- Status: `COMPLETE`

## CORR-0002 — CP9-F-002

The pending-anchor exclusion is derived from repository state, and no generic guardrail names a historical checkpoint.

- Implementation: `file:scripts/development-ledger/anchors.py`, `file:scripts/development-ledger/verify_integrity.py`, `file:tests/test_development_ledger.py`
- Tests: `test:IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint`
- Positive path: `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `test:SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain`
- Negative path: `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`, `test:SuccessorDurabilityTests.test_a_missing_anchor_is_still_detected_after_the_chain_advances`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `checkpoint:CP9-FINDINGS-CLOSURE.json`, `checkpoint:SUCCESSOR-DURABILITY.json`
- Status: `COMPLETE`

## CORR-0003 — CP9-F-003

The stale cardinality is removed and a count in a comment or docstring is refused by the suite and by policy.

- Implementation: `file:tests/test_development_ledger.py`, `file:docs/QUALITY-GATES.md`
- Tests: `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_the_cardinality_of_a_derived_set`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`
- Positive path: `test:SourceCardinalityPolicyTests.test_the_count_policy_is_documented`
- Negative path: `test:SourceCardinalityPolicyTests.test_the_control_detects_a_cardinality_written_in_a_docstring`
- Documentation: `file:docs/QUALITY-GATES.md`, `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:CP9-FINDINGS-CLOSURE.json`
- Status: `COMPLETE`

## CORR-0004 — CP9-F-004

LSN-0014 records the residual limit of its control instead of contradicting its status, and the contradiction is refused by memory validation.

- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/lessons.py`
- Tests: `test:MemoryPolicyDocumentTests.test_the_repository_memory_has_no_status_contradiction`
- Positive path: _not applicable_
- Negative path: `test:MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:CP9-FINDINGS-CLOSURE.json`
- Status: `COMPLETE`

## CORR-0005 — CP9-F-005

The unread guardrailRegistry key is removed, the fixed path is documented and resolved by one function, and the policy document is validated against a closed schema.

- Implementation: `file:.iacode/memory/POLICY.json`, `file:.iacode/schemas/memory-policy.schema.json`, `file:scripts/development-ledger/lessons.py`
- Tests: `test:MemoryPolicyDocumentTests.test_the_declared_policy_validates_against_its_schema`, `test:MemoryPolicyDocumentTests.test_the_guardrail_registry_path_has_one_resolver`
- Positive path: _not applicable_
- Negative path: `test:MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:CP9-FINDINGS-CLOSURE.json`
- Status: `COMPLETE`

## CORR-0101 — CP9-F-001 regression: valid attestation accepted end to end

A structurally legitimate attestation over the sealed history is accepted.

- Implementation: `file:scripts/development-ledger/attestation.py`
- Tests: _none_
- Positive path: `test:AuditAttestationModelTests.test_a_legitimate_attestation_over_the_sealed_history_is_accepted`, `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `checkpoint:POSITIVE-PROMOTION-VALIDATION.json`
- Status: `COMPLETE`

## CORR-0102 — CP9-F-001 regression: the audit checkpoint can be sealed

A checkpoint carrying a milestone verdict is finalized, sealed and validated.

- Implementation: `file:scripts/development-ledger/promotion_fixture.py`
- Tests: _none_
- Positive path: `test:PositivePromotionTests.test_the_audit_checkpoint_validates_as_sealed`, `test:PositivePromotionTests.test_the_audit_checkpoint_carries_the_milestone_verdict`
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `checkpoint:POSITIVE-PROMOTION-VALIDATION.json`
- Status: `COMPLETE`

## CORR-0103 — CP9-F-001 regression: the subject commit, tag and tree are unchanged

The audited subject is not rewritten, re-tagged or re-sealed by its own audit.

- Implementation: `file:scripts/development-ledger/attestation.py`
- Tests: _none_
- Positive path: `test:PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit`
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `checkpoint:POSITIVE-PROMOTION-VALIDATION.json`
- Status: `COMPLETE`

## CORR-0104 — CP9-F-001 regression: no self-referential commit requirement

No attestation names the commit of the tree that contains it.

- Implementation: `file:.iacode/schemas/external-audit-attestation.schema.json`
- Tests: `test:AuditAttestationModelTests.test_the_attestation_never_names_the_commit_of_the_tree_that_contains_it`
- Positive path: _not applicable_
- Negative path: `test:AuditAttestationModelTests.test_the_schema_of_the_circular_model_is_refused`
- Documentation: `file:.iacode/attestations/README.md`
- Validation: _none_
- Status: `COMPLETE`

## CORR-0105 — CP9-F-001 regression: the audit does not stale the subject's assurance

The subject's gate results describe the tree its tag names, so a later attestation cannot make them stale; the audit checkpoint fingerprints its own content after writing it.

- Implementation: `file:scripts/development-ledger/promotion_fixture.py`
- Tests: _none_
- Positive path: `test:PositivePromotionTests.test_the_attestation_lives_in_the_audit_checkpoints_change_set`, `test:PositivePromotionTests.test_the_integrity_chain_still_verifies_after_the_audit`
- Negative path: _not applicable_
- Documentation: `file:docs/MILESTONE-VALIDATION.md`
- Validation: _none_
- Status: `COMPLETE`

## CORR-0106 — CP9-F-001 regression: wrong subject, commit, auditor and results rejected

Every forged element of the relationship is refused.

- Implementation: `file:scripts/development-ledger/attestation.py`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: `test:AuditAttestationModelTests.test_an_attestation_for_another_checkpoint_is_rejected`, `test:AuditAttestationModelTests.test_an_attestation_for_another_commit_is_rejected`, `test:AuditAttestationModelTests.test_a_subject_commit_that_is_not_the_sealed_one_is_rejected`, `test:AuditAttestationModelTests.test_an_unsealed_subject_is_rejected`, `test:AuditAttestationModelTests.test_an_attestation_naming_a_checkpoint_that_does_not_exist_is_rejected`, `test:AuditAttestationModelTests.test_a_failed_review_cannot_produce_a_milestone_pass`, `test:AuditAttestationModelTests.test_a_failed_red_team_cannot_produce_a_milestone_pass`, `test:AuditAttestationModelTests.test_incomplete_audit_coverage_cannot_produce_a_milestone_pass`, `test:AuditAttestationModelTests.test_a_failed_test_result_cannot_produce_a_milestone_pass`, `test:AuditAttestationModelTests.test_a_missing_field_is_refused_before_anything_else`
- Documentation: _none_
- Validation: `checkpoint:M0-INTERNAL-RED-TEAM.json`
- Status: `COMPLETE`

## CORR-0107 — CP9-F-001 regression: the mechanism decides the status

A fresh-session attestation may not produce the cross-tool status, and an unknown or self-contradicting mechanism is refused.

- Implementation: `file:scripts/development-ledger/attestation.py`, `file:scripts/development-ledger/validate_checkpoint.py`
- Tests: `test:AuditAttestationModelTests.test_a_fresh_session_audit_may_not_produce_the_external_status`, `test:AuditAttestationModelTests.test_the_status_vocabulary_separates_the_two_verdicts`
- Positive path: _not applicable_
- Negative path: `test:AuditAttestationModelTests.test_an_unknown_validation_mechanism_is_rejected`, `test:AuditAttestationModelTests.test_a_cross_tool_claim_without_cross_tool_availability_is_rejected`, `test:AuditAttestationModelTests.test_a_fresh_session_claim_requires_a_fresh_session`, `test:PositivePromotionTests.test_a_fresh_session_audit_cannot_reach_the_external_status`
- Documentation: `file:docs/QUALITY-GATES.md`, `file:docs/MILESTONE-VALIDATION.md`
- Validation: _none_
- Status: `COMPLETE`

## CORR-0108 — CP9-F-001 regression: integrity validation still works

The chain verifies before, during and after the promotion.

- Implementation: `file:scripts/development-ledger/anchors.py`
- Tests: _none_
- Positive path: `test:PositivePromotionTests.test_the_integrity_chain_still_verifies_after_the_audit`
- Negative path: `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`
- Documentation: _none_
- Validation: `command:cmd-integrity`
- Status: `COMPLETE`

## CORR-0201 — CP9-F-002 regression: synthetic succession

A predecessor is sealed, a successor anchors it, and a further successor advances the chain; every state keeps the controls green with no source change.

- Implementation: `file:scripts/development-ledger/successor_durability.py`
- Tests: _none_
- Positive path: `test:SuccessorDurabilityTests.test_three_checkpoints_were_sealed_in_succession`, `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `test:SuccessorDurabilityTests.test_each_successor_anchors_its_predecessor`, `test:SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain`
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `checkpoint:SUCCESSOR-DURABILITY.json`
- Status: `COMPLETE`

## CORR-0202 — CP9-F-002 regression: removing an anchor still fails

Removing the anchor of a checkpoint the rule does not forgive is detected at every state.

- Implementation: `file:scripts/development-ledger/anchors.py`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: `test:SuccessorDurabilityTests.test_a_missing_anchor_is_still_detected_after_the_chain_advances`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`
- Documentation: _none_
- Validation: `checkpoint:SUCCESSOR-DURABILITY.json`
- Status: `COMPLETE`

## CORR-0203 — CP9-F-002 regression: one canonical exclusion rule

The CLI, the validator and the suite resolve the exclusion through one helper.

- Implementation: `file:scripts/development-ledger/anchors.py`, `file:scripts/development-ledger/verify_integrity.py`
- Tests: `test:IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint`, `test:IntegrityAnchorTests.test_every_sealed_checkpoint_but_the_newest_is_anchored`
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: _none_
- Status: `COMPLETE`

## CORR-0204 — CP9-F-002 regression: no literal historical identifier in generic logic

Executable logic that decides behaviour derives the checkpoint it acts on; the remaining literals are historical fixtures and compatibility cases, documented as such.

- Implementation: `file:tests/test_development_ledger.py`, `file:scripts/development-ledger/derive_requirements.py`, `file:scripts/development-ledger/m0_red_team.py`
- Tests: `test:AuditRegistrySuccessionTests.test_the_registry_binds_the_audit_to_this_corrective_checkpoint`
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: `checkpoint:DECISIONS.md`
- Validation: _none_
- Status: `COMPLETE`

## CORR-0301 — CP-0009 disclosure: additive test counts

One physical test execution recorded under several categories counts once, and a count larger than what exists is refused.

- Implementation: `file:scripts/development-ledger/derive_counts.py`, `file:.iacode/schemas/test-result.schema.json`, `file:scripts/development-ledger/validate_checkpoint.py`
- Tests: `test:DerivedTestCountTests.test_one_run_recorded_in_two_categories_counts_once`, `test:DerivedTestCountTests.test_an_explicit_run_identifier_deduplicates_across_categories`, `test:DerivedTestCountTests.test_two_real_executions_are_both_counted`
- Positive path: _not applicable_
- Negative path: `test:DerivedTestCountTests.test_a_count_larger_than_what_exists_is_refused`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:COUNTS.json`
- Status: `COMPLETE`

## CORR-0302 — CP-0009 disclosure: ambiguous Red Team totals

Adversarial totals are reported by explicit category, each derived from the machine-readable report rather than maintained by hand.

- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Tests: `test:AuditRegistrySuccessionTests.test_the_battery_of_an_additional_section_is_not_promoted_to_mandatory`
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `checkpoint:AFFECTED-RED-TEAM.json`, `checkpoint:M0-INTERNAL-RED-TEAM.json`
- Status: `COMPLETE`

## CORR-0303 — CP-0009 disclosure: adversarial batteries need a null-mutation control

A battery records the unmutated control it ran, and a report without one cannot produce a PASS.

- Implementation: `file:scripts/development-ledger/m0_red_team.py`, `file:.iacode/schemas/red-team-report.schema.json`, `file:scripts/development-ledger/validate_checkpoint.py`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: `test:InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected`, `test:InternalAssuranceTests.test_a_failed_null_mutation_control_cannot_produce_a_pass`
- Documentation: `file:docs/MILESTONE-VALIDATION.md`
- Validation: `checkpoint:M0-INTERNAL-RED-TEAM.json`
- Status: `COMPLETE`

## CORR-0401 — Prompt section 26: the eight CP-0009 lesson candidates are assessed

Each candidate is registered, merged into an existing lesson as a recurrence, or recorded as not requiring a lesson, with the reason.

- Implementation: `file:.iacode/memory/lessons.jsonl`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: `checkpoint:LESSON-CANDIDATE-ASSESSMENT.md`, `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0004`
- Status: `COMPLETE`

## CORR-0402 — Prompt sections 27 to 29: the three named lessons exist and are guarded

A control needs a positive path, a guardrail may not name a historical checkpoint, and a required protocol transition may not turn a mandatory gate red.

- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/memory/guardrails/registry.json`
- Tests: `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0004`
- Status: `COMPLETE`

## CORR-0403 — Prompt section 30: the preflight is regenerated and fresh

The preflight was regenerated after the memory changed and its fingerprint recomputes.

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: `checkpoint:LESSON-PREFLIGHT.md`
- Validation: `command:cmd-validate`
- Status: `COMPLETE`

## CORR-0404 — CP9 candidate 007: the preflight has no audit-role subset

Recorded as a scoped lesson that constrains audit runs only, and documented in the engineering memory policy.

- Implementation: `file:.iacode/memory/lessons.jsonl`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `checkpoint:LESSON-CANDIDATE-ASSESSMENT.md`
- Validation: `command:cmd-0004`
- Status: `COMPLETE`

## CORR-0501 — Prompt section 31: Green Keeper

Every mandatory gate is green with zero remaining failures and zero unresolved rework.

- Implementation: `checkpoint:REWORK-LOG.jsonl`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `command:cmd-greenkeeper`
- Status: `COMPLETE`

## CORR-0502 — Prompt section 32: Delivery Completeness

Coverage and evidence coverage are total, with no PARTIAL and no MISSING requirement.

- Implementation: `checkpoint:COMPLETENESS-REPORT.json`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: `checkpoint:COMPLETENESS-REPORT.md`
- Validation: `command:cmd-completeness`
- Status: `COMPLETE`

## CORR-0503 — Prompt section 33: internal positive promotion simulation

A complete promotion is executed in a disposable repository before handoff.

- Implementation: `file:scripts/development-ledger/promotion_simulation.py`
- Tests: _none_
- Positive path: `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `checkpoint:POSITIVE-PROMOTION-VALIDATION.json`
- Status: `COMPLETE`

## CORR-0504 — Prompt section 34: internal successor durability simulation

A sealed chain is advanced and re-checked at every state before handoff.

- Implementation: `file:scripts/development-ledger/successor_durability.py`
- Tests: _none_
- Positive path: `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `checkpoint:SUCCESSOR-DURABILITY.json`
- Status: `COMPLETE`

## CORR-0505 — Prompt section 35: the whole suite passes

The discovered suite is executed in full and every case passes.

- Implementation: `checkpoint:TESTS.json`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `command:cmd-tests`, `checkpoint:COUNTS.json`
- Status: `COMPLETE`

## CORR-0506 — Prompt section 36: clean clone

The sealed content is validated in a clean clone with no session state.

- Implementation: `checkpoint:RESUME-VALIDATION.md`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `command:cmd-clean-clone`
- Status: `COMPLETE`

## CORR-0507 — Prompt section 37: internal closure audit

An internal non-implementing audit verifies each closed finding and each required property.

- Implementation: `checkpoint:CP9-FINDINGS-CLOSURE.json`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: `checkpoint:CP9-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:M0-INTERNAL-MIRROR.json`
- Status: `COMPLETE`

## CORR-0508 — Prompt section 38: affected Red Team scenarios

Every attack affected by this delivery is re-executed and defended.

- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Tests: _none_
- Positive path: _not applicable_
- Negative path: _not applicable_
- Documentation: _none_
- Validation: `checkpoint:AFFECTED-RED-TEAM.json`, `checkpoint:M0-INTERNAL-RED-TEAM.json`
- Status: `COMPLETE`
