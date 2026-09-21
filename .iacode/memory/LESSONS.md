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
| `LSN-0011` | `GUARDED` | MEDIUM | tooling | A control over a checkpoint's own evidence must be scoped to the moment it matters | `DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`, `green_keeper._refresh_declared_hashes` |
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
| `LSN-0028` | `GUARDED` | MEDIUM | tooling | A configuration key that no code reads is a defect, not documentation | `.iacode/schemas/memory-policy.schema.json`, `lessons.validate_memory_policy_document`, `MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared` |
| `LSN-0029` | `GUARDED` | CRITICAL | process | A required protocol transition must never turn a mandatory gate red | `scripts/development-ledger/successor_durability.py`, `SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`, `scripts/development-ledger/gate_transition_simulation.py` |
| `LSN-0030` | `CONFIRMED` | LOW | process | The lesson preflight presumes an implementing delivery and constrains an audit run badly | _not yet guarded_ |
| `LSN-0031` | `GUARDED` | CRITICAL | quality | An empty applicable set is not a missing required set, and a control must tell them apart | `scripts/development-ledger/mirror_semantics_validation.py`, `MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`, `MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`, `validate_checkpoint._validate_mirror_applicability` |

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

- Status: `GUARDED`, severity HIGH, category tooling, recurrences 1.
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

- Status: `GUARDED`, severity MEDIUM, category tooling, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0005, finding REWORK-LOG cycles 1 to 3 and 6.
- Symptom: The gate that validates the checkpoint kept failing because running it appends to the very ledger and inventory the validation binds.
- Root cause: Consistency rules written for a finished delivery were applied while the delivery was still writing its own evidence, which no ordering of steps can satisfy.
- Resolution: Gate consistency is enforced when the delivery is offered for review and treated as provisional while work is in progress, and the harness re-derives declared hashes immediately before validating.
- Prevention:
  - `test` DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress — Provisional in progress, strict at handoff.
  - `invariant` green_keeper._refresh_declared_hashes — Declared hashes are re-derived before the validation gate runs, never invented.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0005/DECISIONS.md`, `file:docs/checkpoints/SETUP-00-CP-0005/REWORK-LOG.jsonl`

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

- Status: `GUARDED`, severity MEDIUM, category tooling, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0009, finding CP9-F-005.
- Symptom: The memory policy declared a relocatable guardrail registry path while the implementation resolved a fixed constant, so re-pointing the documented key changed nothing.
- Root cause: The policy document was never validated against a schema, so a key could be added without any consumer and without any check noticing.
- Resolution: The unread key was removed, the fixed path is documented and resolved by one function, and the policy document is validated against a closed schema that refuses an unknown key.
- Prevention:
  - `schema` .iacode/schemas/memory-policy.schema.json — The memory policy schema is closed to keys no code reads.
  - `invariant` lessons.validate_memory_policy_document — The declared policy is validated like every other governing document.
  - `test` MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared — Declaring an unread setting is a validation error.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md`, `file:.iacode/memory/POLICY.json`, `file:.iacode/schemas/memory-policy.schema.json`

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
