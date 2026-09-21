# CP-0009 Findings Closure

Result: `CLOSED`

- Audit: `M0-CP-0009`
- Source: `docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md`
- Corrective checkpoint: `SETUP-00-CP-0010`
- Closed: `5` of `5` FINDINGS

| Finding | Severity | Status | Regression tests | Negative tests |
|---|---|---|---|---|
| `CP9-F-001` | `CRITICAL` | `CLOSED` | 7 | 15 |
| `CP9-F-002` | `CRITICAL` | `CLOSED` | 6 | 4 |
| `CP9-F-003` | `LOW` | `CLOSED` | 3 | 2 |
| `CP9-F-004` | `LOW` | `CLOSED` | 1 | 1 |
| `CP9-F-005` | `LOW` | `CLOSED` | 2 | 1 |

## CP9-F-001 — CRITICAL — the milestone attestation could be written but never consumed, so a milestone PASS was unreachable

- Expected: An attestation authored by a different sealed, anchored checkpoint, carrying APPROVED, RED_TEAM_PASS, 100.0, 100.0 and PASS, lets the audited subject reach a milestone PASS.
- Observed: The attestation was verified against the checkpoint being validated, so satisfying it required a tree containing its own commit identifier. Three attempts and a fixed-point iteration ended in 'attests commit X, not the subject commit Y'; writing it in the audit checkpoint moved HEAD past the subject's tag; and adding it marked the subject's assurance results STALE. Twelve rejection tests passed and no acceptance case existed.
- Root cause: The verdict was attached to the object being judged. A delivery checkpoint and its audit are different immutable objects, and consuming the attestation as if it belonged to the subject made the reachable state space empty.
- Implementation: `file:scripts/development-ledger/attestation.py`, `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/milestone_status.py`, `file:scripts/development-ledger/promotion_fixture.py`, `file:scripts/development-ledger/promotion_simulation.py`, `file:.iacode/schemas/external-audit-attestation.schema.json`, `file:.iacode/schemas/checkpoint.schema.json`
- Regression tests: `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:PositivePromotionTests.test_the_audit_checkpoint_validates_as_sealed`, `test:PositivePromotionTests.test_the_audit_checkpoint_carries_the_milestone_verdict`, `test:PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit`, `test:PositivePromotionTests.test_the_integrity_chain_still_verifies_after_the_audit`, `test:AuditAttestationModelTests.test_a_legitimate_attestation_over_the_sealed_history_is_accepted`, `test:AuditAttestationModelTests.test_the_attestation_never_names_the_commit_of_the_tree_that_contains_it`
- Negative tests: `test:AuditAttestationModelTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:AuditAttestationModelTests.test_an_attestation_for_another_checkpoint_is_rejected`, `test:AuditAttestationModelTests.test_an_attestation_for_another_commit_is_rejected`, `test:AuditAttestationModelTests.test_a_subject_commit_that_is_not_the_sealed_one_is_rejected`, `test:AuditAttestationModelTests.test_an_unsealed_subject_is_rejected`, `test:AuditAttestationModelTests.test_a_checkpoint_may_not_claim_a_verdict_another_checkpoint_authored`, `test:AuditAttestationModelTests.test_a_failed_review_cannot_produce_a_milestone_pass`, `test:AuditAttestationModelTests.test_a_failed_red_team_cannot_produce_a_milestone_pass`, `test:AuditAttestationModelTests.test_incomplete_audit_coverage_cannot_produce_a_milestone_pass`, `test:AuditAttestationModelTests.test_a_failed_test_result_cannot_produce_a_milestone_pass`, `test:AuditAttestationModelTests.test_an_unknown_validation_mechanism_is_rejected`, `test:AuditAttestationModelTests.test_a_cross_tool_claim_without_cross_tool_availability_is_rejected`, `test:AuditAttestationModelTests.test_a_fresh_session_claim_requires_a_fresh_session`, `test:AuditAttestationModelTests.test_no_attestation_means_no_milestone_pass`, `test:PositivePromotionTests.test_a_fresh_session_audit_cannot_reach_the_external_status`
- Verification: `python -m unittest discover -s tests`
- Evidence: `checkpoint:POSITIVE-PROMOTION-VALIDATION.json`, `checkpoint:POSITIVE-PROMOTION-VALIDATION.md`, `file:docs/adr/ADR-0011-audit-checkpoint-carries-the-verdict.md`, `file:docs/MILESTONE-VALIDATION.md`, `file:.iacode/attestations/README.md`
- Status: `CLOSED`

## CP9-F-002 — CRITICAL — a guardrail test was bound to a literal checkpoint name, so the protocol's own next step turned the mandatory tests gate red

- Expected: Carrying out the protocol's own next step -- a successor anchoring its sealed predecessor -- leaves the mandatory gate set green.
- Observed: tests/test_development_ledger.py called verify_chain with exclude={'SETUP-00-CP-0008'} while verify_integrity.py derived the same exclusion from repository state. Anchoring the sealed predecessor took the suite from 306/306 to 305/306, and sealing a successor produced the mirror failure.
- Root cause: One semantic rule had two implementations: one derived, one typed. The typed copy encoded the repository as it looked on the day it was written.
- Implementation: `file:scripts/development-ledger/anchors.py`, `file:scripts/development-ledger/verify_integrity.py`, `file:scripts/development-ledger/successor_durability.py`, `file:scripts/development-ledger/promotion_fixture.py`, `file:tests/test_development_ledger.py`
- Regression tests: `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `test:SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain`, `test:SuccessorDurabilityTests.test_each_successor_anchors_its_predecessor`, `test:SuccessorDurabilityTests.test_three_checkpoints_were_sealed_in_succession`, `test:IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint`, `test:IntegrityAnchorTests.test_every_sealed_checkpoint_but_the_newest_is_anchored`
- Negative tests: `test:SuccessorDurabilityTests.test_a_missing_anchor_is_still_detected_after_the_chain_advances`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`, `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`, `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`
- Verification: `python -m unittest discover -s tests`
- Evidence: `checkpoint:SUCCESSOR-DURABILITY.json`, `checkpoint:SUCCESSOR-DURABILITY.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:.iacode/memory/guardrails/registry.json`
- Status: `CLOSED`

## CP9-F-003 — LOW — a stale count survived in a current artifact because the count guardrail only inspected Markdown

- Expected: No current artifact states a count that contradicts the derivation.
- Observed: A test docstring stated a cardinality for the derived requirement set that the derivation had outgrown, and COUNT_CLAIM only matched the N/M NOUN form in checkpoint Markdown, so a prose count in a .py file was outside the control.
- Root cause: The control's scope was one artifact type, and the same failure class stayed alive everywhere else. The recurrence is recorded against LSN-0022 as a GUARDRAIL_FAILURE.
- Implementation: `file:tests/test_development_ledger.py`, `file:docs/QUALITY-GATES.md`, `file:.iacode/memory/lessons.jsonl`, `file:.iacode/memory/guardrails/registry.json`
- Regression tests: `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_the_cardinality_of_a_derived_set`, `test:SourceCardinalityPolicyTests.test_the_count_policy_is_documented`
- Negative tests: `test:SourceCardinalityPolicyTests.test_the_control_detects_a_cardinality_written_in_a_docstring`, `test:DerivedCountTests.test_a_forged_count_is_rejected`
- Verification: `python -m unittest discover -s tests`
- Evidence: `file:docs/QUALITY-GATES.md`, `file:.iacode/memory/LESSONS.md`
- Status: `CLOSED`

## CP9-F-004 — LOW — a lesson's own note contradicted its status

- Expected: A GUARDED lesson does not describe itself as unguarded.
- Observed: LSN-0014 was GUARDED and named GRD-0013 while its notes field still read 'Not guarded: nothing can prove from the artifact alone that a record was written at execution time.'
- Root cause: The note was written while the lesson was unguarded and was never revisited when the control arrived, because nothing compared the prose with the status.
- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:scripts/development-ledger/lessons.py`
- Regression tests: `test:MemoryPolicyDocumentTests.test_the_repository_memory_has_no_status_contradiction`
- Negative tests: `test:MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded`
- Verification: `python -m unittest discover -s tests`
- Evidence: `file:.iacode/memory/LESSONS.md`, `file:docs/ENGINEERING-MEMORY.md`
- Status: `CLOSED`

## CP9-F-005 — LOW — a policy key was declared and never read

- Expected: A configuration value either governs behaviour or is not declared.
- Observed: .iacode/memory/POLICY.json declared 'guardrailRegistry' while lessons.guardrail_registry_path returned a constant path, so re-pointing the key in a clone changed nothing.
- Root cause: The policy document was never validated against its schema, so a key without a consumer could be added and nothing noticed.
- Implementation: `file:.iacode/memory/POLICY.json`, `file:.iacode/schemas/memory-policy.schema.json`, `file:scripts/development-ledger/lessons.py`, `file:docs/ENGINEERING-MEMORY.md`
- Regression tests: `test:MemoryPolicyDocumentTests.test_the_declared_policy_validates_against_its_schema`, `test:MemoryPolicyDocumentTests.test_the_guardrail_registry_path_has_one_resolver`
- Negative tests: `test:MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared`
- Verification: `python -m unittest discover -s tests`
- Evidence: `file:.iacode/memory/POLICY.json`, `file:docs/ENGINEERING-MEMORY.md`
- Status: `CLOSED`
