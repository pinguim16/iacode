# Final Correction Requirements

- Checkpoint: `SETUP-00-CP-0012`
- Gate: `SETUP-00`
- Closes: `CP11-F-001`
- Source: the final corrective delivery brief for SETUP-00-CP-0012

Every row below is also declared in REQUIREMENTS-MATRIX.json as a local anchored reference, so the Delivery Completeness Validator audits it with the rest of the delivery. A requirement that exists only in the session is not a requirement.

| ID | Requirement | Matrix reference | Status |
|---|---|---|---|
| `FCR-001` | The finding set is taken from the sealed audit checkpoint, not from a summary | `local:FCR-001` | `COMPLETE` |
| `FCR-002` | CP11-F-001 is closed | `local:FCR-002` | `COMPLETE` |
| `FCR-003` | MIR-002 reports an empty applicable set as NOT_APPLICABLE | `local:FCR-003` | `COMPLETE` |
| `FCR-004` | MIR-003 is analysed on its own and repaired on its own terms | `local:FCR-004` | `COMPLETE` |
| `FCR-005` | The overall verdict treats NOT_APPLICABLE as non-failing without rewriting it | `local:FCR-005` | `COMPLETE` |
| `FCR-006` | Every NOT_APPLICABLE carries a reason, an empty expected count and a source | `local:FCR-006` | `COMPLETE` |
| `FCR-007` | NOT_APPLICABLE never becomes a bypass | `local:FCR-007` | `COMPLETE` |
| `FCR-008` | A checkpoint with no open audit passes the real mirror | `local:FCR-008` | `COMPLETE` |
| `FCR-009` | The first checkpoint of the next Gate reaches READY_FOR_REVIEW | `local:FCR-009` | `COMPLETE` |
| `FCR-010` | A real open finding still fails | `local:FCR-010` | `COMPLETE` |
| `FCR-011` | An expected audit artifact that is absent fails, and is never inapplicable | `local:FCR-011` | `COMPLETE` |
| `FCR-012` | A forged empty expected set does not reduce the applicable set | `local:FCR-012` | `COMPLETE` |
| `FCR-013` | A milestone with no findings of its own can pass | `local:FCR-013` | `COMPLETE` |
| `FCR-014` | A delivery with closed findings passes | `local:FCR-014` | `COMPLETE` |
| `FCR-015` | A delivery with an open finding does not pass | `local:FCR-015` | `COMPLETE` |
| `FCR-016` | The schema reuses NOT_APPLICABLE and evolves compatibly under a version gate | `local:FCR-016` | `COMPLETE` |
| `FCR-017` | Every sealed checkpoint still validates under the new semantics | `local:FCR-017` | `COMPLETE` |
| `FCR-018` | The positive promotion simulation passes after the repair | `local:FCR-018` | `COMPLETE` |
| `FCR-019` | Successor durability passes after the repair | `local:FCR-019` | `COMPLETE` |
| `FCR-020` | The state machine is proven without implementing the next Gate | `local:FCR-020` | `COMPLETE` |
| `FCR-021` | The lesson is recorded with the precise distinction and is guarded | `local:FCR-021` | `COMPLETE` |
| `FCR-022` | The recurrence is recorded as a GUARDRAIL_FAILURE and resolved | `local:FCR-022` | `COMPLETE` |
| `FCR-023` | The positive simulation executes the mirror instead of writing its artifact | `local:FCR-023` | `COMPLETE` |
| `FCR-024` | A simulation that reports a control as passing calls that control | `local:FCR-024` | `COMPLETE` |
| `FCR-025` | The canonical CLAUDE.md records the language rule | `local:FCR-025` | `COMPLETE` |
| `FCR-026` | The Green Keeper is green over the canonical mandatory gate set | `local:FCR-026` | `COMPLETE` |
| `FCR-027` | Delivery completeness is total over an independently derived expected set | `local:FCR-027` | `COMPLETE` |
| `FCR-028` | The completeness audit covers this whole execution before handoff | `local:FCR-028` | `COMPLETE` |
| `FCR-029` | The internal mirror of this delivery is the tool's own output | `local:FCR-029` | `COMPLETE` |
| `FCR-030` | The adversarial position of the changed surface is executed | `local:FCR-030` | `COMPLETE` |
| `FCR-031` | The whole suite passes and every skip is accounted for | `local:FCR-031` | `COMPLETE` |
| `FCR-032` | The delivery validates from a clean clone | `local:FCR-032` | `COMPLETE` |
| `FCR-033` | The CP-0011 findings closure record exists and is complete | `local:FCR-033` | `COMPLETE` |
| `FCR-034` | An internal auditor that did not implement audits the delivery | `local:FCR-034` | `COMPLETE` |
| `FCR-035` | The checkpoint carries every mandatory artifact of the current protocol | `local:FCR-035` | `COMPLETE` |
| `FCR-036` | The delivery closes at READY_FOR_REVIEW and never grants itself a Gate | `local:FCR-036` | `COMPLETE` |
| `FCR-037` | The next action is a fresh-session independent M0 audit and Gate 0 stays blocked | `local:FCR-037` | `COMPLETE` |
| `FCR-038` | No historical checkpoint, commit or tag is rewritten | `local:FCR-038` | `COMPLETE` |

## Each requirement, with the evidence that answers it

### `FCR-001` — The finding set is taken from the sealed audit checkpoint, not from a summary

Read SETUP-00-CP-0011 in full and derive the finding set from the checkpoint itself rather than from any external description of it.

- Implementation: `file:.iacode/policies/audit-registry.json`, `file:scripts/development-ledger/policies.py`
- Positive regression: `test:SealedReportRenderingTests.test_a_findings_section_bounds_what_the_report_raises_as_its_own`, `test:SealedReportRenderingTests.test_the_registry_binds_the_third_audit_to_this_corrective_checkpoint`
- Documentation: `checkpoint:CP11-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-002` — CP11-F-001 is closed

Close the single critical finding of the CP-0011 audit with implementation, positive regression, negative regression and resolvable evidence.

- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_every_applicability_state_behaves_as_specified`
- Documentation: `checkpoint:CP11-FINDINGS-CLOSURE.json`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-003` — MIR-002 reports an empty applicable set as NOT_APPLICABLE

The audit-findings dimension reports NOT_APPLICABLE when no registered audit names the checkpoint as its corrective delivery, PASS when every applicable finding is closed, and FAIL when one is not.

- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`, `test:MirrorApplicabilitySemanticsTests.test_a_satisfied_applicable_set_passes`
- Negative regression: `test:MirrorApplicabilitySemanticsTests.test_an_open_finding_fails`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-004` — MIR-003 is analysed on its own and repaired on its own terms

The mandatory-attack dimension derives its battery from the sealed Red Team reports of the same audits; an empty battery is NOT_APPLICABLE, an unexecuted mandatory attack is FAIL.

- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`
- Negative regression: `test:MirrorApplicabilitySemanticsTests.test_an_unexecuted_mandatory_attack_fails`
- Documentation: `file:.iacode/agents/m0-closure-auditor.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-005` — The overall verdict treats NOT_APPLICABLE as non-failing without rewriting it

A report fails only on a FAIL. An inapplicable dimension keeps its own status in the artifact, is counted separately, and is never mapped to PASS.

- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`, `file:scripts/development-ledger/validate_checkpoint.py`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`
- Negative regression: `test:MirrorApplicabilityValidationTests.test_an_inapplicable_dimension_counted_as_a_pass_is_refused`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-006` — Every NOT_APPLICABLE carries a reason, an empty expected count and a source

An inapplicable dimension records status, reason, expectedCount zero, derivationSource and evidence, so it is auditable rather than a silent skip.

- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`, `file:.iacode/schemas/mirror-audit.schema.json`
- Positive regression: `test:NotApplicableRecordingTests.test_an_inapplicable_check_records_its_reason_count_and_source`
- Negative regression: `test:MirrorApplicabilityValidationTests.test_an_inapplicable_dimension_without_a_reason_is_refused`, `test:NotApplicableRecordingTests.test_an_unjustified_inapplicable_record_becomes_a_failure`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-007` — NOT_APPLICABLE never becomes a bypass

The applicable set is derived from the canonical sources at every call and no caller or delivery artifact supplies it; checkpoint validation re-derives the registry-bound dimensions instead of believing the report.

- Implementation: `file:scripts/development-ledger/policies.py`, `file:scripts/development-ledger/validate_checkpoint.py`
- Positive regression: `test:ApplicableSetDerivationTests.test_the_mirror_derives_its_own_expected_set_and_takes_none_from_its_caller`
- Negative regression: `test:MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`, `test:MirrorApplicabilityValidationTests.test_an_inapplicable_dimension_with_items_is_refused`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-008` — A checkpoint with no open audit passes the real mirror

A checkpoint that corrects no audit obtains a passing mirror through the shipped CLI, with the two empty dimensions recorded as NOT_APPLICABLE.

- Implementation: `file:scripts/development-ledger/mirror_semantics_validation.py`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`, `test:MirrorApplicabilitySemanticsTests.test_every_state_was_produced_by_executing_the_tool`
- Documentation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-009` — The first checkpoint of the next Gate reaches READY_FOR_REVIEW

The whole transition is executed in a disposable repository: SETUP sealed, independent audit, derived milestone PASS, first checkpoint of the next Gate, READY_FOR_REVIEW. No Gate 0 work exists in this repository.

- Implementation: `file:scripts/development-ledger/gate_transition_simulation.py`
- Positive regression: `test:GateTransitionSimulationTests.test_the_first_checkpoint_of_the_next_gate_reaches_review_readiness`, `test:GateTransitionSimulationTests.test_no_runtime_of_the_next_gate_was_implemented`
- Documentation: `checkpoint:GATE0-TRANSITION-SIMULATION.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-010` — A real open finding still fails

A non-empty applicable set with an unsatisfied item fails and the delivery cannot be sealed, so the repair is not a vacuous pass.

- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_an_open_finding_fails`
- Negative regression: `test:MirrorApplicabilitySemanticsTests.test_an_open_finding_fails`
- Documentation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-011` — An expected audit artifact that is absent fails, and is never inapplicable

When the canonical sources name a finding and the closure record is missing, the dimension fails rather than reporting an empty set.

- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_a_missing_required_set_fails_rather_than_being_inapplicable`
- Negative regression: `test:SealedReportRenderingTests.test_a_report_whose_findings_cannot_be_parsed_is_refused_rather_than_read_as_empty`, `test:ApplicableSetDerivationTests.test_an_unreadable_audit_report_raises_instead_of_reducing_to_an_empty_set`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-012` — A forged empty expected set does not reduce the applicable set

A delivery declaring that it has nothing to close is ignored: the canonical derivation prevails and the open item still fails.

- Implementation: `file:scripts/development-ledger/policies.py`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_a_delivery_cannot_declare_its_own_applicable_set_empty`
- Negative regression: `test:MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`
- Documentation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-013` — A milestone with no findings of its own can pass

A clean audit checkpoint reaches a milestone verdict with the findings dimension inapplicable.

- Implementation: `file:scripts/development-ledger/promotion_fixture.py`
- Positive regression: `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:SimulationExecutesProductionControlsTests.test_the_simulated_mirror_reaches_a_pass_with_inapplicable_dimensions`
- Documentation: `checkpoint:POSITIVE-PROMOTION-VALIDATION.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-014` — A delivery with closed findings passes

Three applicable findings, all CLOSED, and two mandatory attacks, both defended, produce a passing mirror.

- Implementation: `file:scripts/development-ledger/mirror_semantics_validation.py`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_a_satisfied_applicable_set_passes`
- Documentation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-015` — A delivery with an open finding does not pass

Three applicable findings with one OPEN produce a failing mirror and an unsealable delivery.

- Implementation: `file:scripts/development-ledger/mirror_semantics_validation.py`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_an_open_finding_fails`
- Negative regression: `test:MirrorApplicabilitySemanticsTests.test_an_open_finding_fails`
- Documentation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-016` — The schema reuses NOT_APPLICABLE and evolves compatibly under a version gate

No new status is invented. Report version 1.1.0 adds the justification fields; a 1.0.0 report keeps its own rules and may not carry an inapplicable dimension.

- Implementation: `file:.iacode/schemas/mirror-audit.schema.json`, `file:scripts/development-ledger/validate_checkpoint.py`
- Positive regression: `test:MirrorApplicabilityValidationTests.test_a_justified_inapplicable_dimension_is_accepted`
- Negative regression: `test:MirrorApplicabilityValidationTests.test_an_inapplicable_dimension_under_the_older_report_version_is_refused`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-017` — Every sealed checkpoint still validates under the new semantics

The current tooling validates all sealed checkpoints from a detached checkout of their own tags, and no sealed checkpoint is modified.

- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Positive regression: `test:HistoricalClosureCompatibilityTests.test_seventh_sealed_checkpoint_still_validates`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`

### `FCR-018` — The positive promotion simulation passes after the repair

Re-executed end to end, now producing the mirror report by running the tool.

- Implementation: `file:scripts/development-ledger/promotion_simulation.py`
- Positive regression: `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`
- Documentation: `checkpoint:POSITIVE-PROMOTION-VALIDATION.md`
- Validation: `checkpoint:POSITIVE-PROMOTION-VALIDATION.json`, `command:cmd-0002`

### `FCR-019` — Successor durability passes after the repair

The integrity controls stay green at every state of an advancing chain.

- Implementation: `file:scripts/development-ledger/successor_durability.py`
- Positive regression: `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`
- Documentation: `checkpoint:SUCCESSOR-DURABILITY.md`
- Validation: `checkpoint:SUCCESSOR-DURABILITY.json`, `command:cmd-0003`

### `FCR-020` — The state machine is proven without implementing the next Gate

The Gate transition fixture is synthetic and disposable; no Foundation work is implemented and no Gate 0 artifact exists in this repository.

- Implementation: `file:scripts/development-ledger/promotion_fixture.py`
- Positive regression: `test:GateTransitionSimulationTests.test_no_runtime_of_the_next_gate_was_implemented`
- Documentation: `checkpoint:NEXT.md`
- Validation: `checkpoint:GATE0-TRANSITION-SIMULATION.json`, `command:cmd-0005`

### `FCR-021` — The lesson is recorded with the precise distinction and is guarded

LSN-0031 states that an empty applicable set is not a missing required set, and GRD-0030 prevents the recurrence automatically.

- Implementation: `file:.iacode/memory/lessons.jsonl`, `file:.iacode/memory/guardrails/registry.json`
- Positive regression: `test:MirrorApplicabilitySemanticsTests.test_the_declared_states_cover_both_sides_of_the_distinction`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-022` — The recurrence is recorded as a GUARDRAIL_FAILURE and resolved

LSN-0024 and LSN-0029 each carry a guardrail failure for this recurrence, resolved in this checkpoint by a new control, and the occurrence is kept rather than erased.

- Implementation: `file:.iacode/memory/lessons.jsonl`
- Positive regression: `test:GuardrailEffectivenessGateTests.test_the_measured_effectiveness_is_recorded_truthfully`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-023` — The positive simulation executes the mirror instead of writing its artifact

promotion_fixture runs m0_mirror_audit.py, records the command and the exit code, and the sealed artifact is bound to the tool's output by content.

- Implementation: `file:scripts/development-ledger/promotion_fixture.py`
- Positive regression: `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-024` — A simulation that reports a control as passing calls that control

The rule is written down, guarded by GRD-0031, and what a simulation had to model instead is declared rather than implied.

- Implementation: `file:scripts/development-ledger/promotion_simulation.py`
- Positive regression: `test:SimulationExecutesProductionControlsTests.test_the_simulation_declares_which_artifacts_it_modelled`
- Documentation: `file:docs/DEVELOPMENT-CONTRACT.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-025` — The canonical CLAUDE.md records the language rule

Every response to the user is in Brazilian Portuguese, with the technical literals that must stay unchanged named explicitly, and no historical artifact is rewritten to translate it.

- Implementation: `file:CLAUDE.md`
- Positive regression: `test:ClaudeAdapterTests.test_project_agents_defer_to_canonical_contracts`
- Documentation: `file:CLAUDE.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-026` — The Green Keeper is green over the canonical mandatory gate set

Every mandatory gate exits zero with command evidence, with no remaining failure and no unresolved rework item.

- Implementation: `file:scripts/development-ledger/green_keeper.py`
- Positive regression: `test:GreenKeeperToolTests.test_gate_invocations_are_recorded_reproducibly`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `checkpoint:REWORK-LOG.jsonl`

### `FCR-027` — Delivery completeness is total over an independently derived expected set

Coverage and evidence coverage are 100.00, with zero partial and zero missing requirements.

- Implementation: `file:scripts/development-ledger/check_completeness.py`
- Positive regression: `test:DeliveryCompletenessMatrixTests.test_missing_mandatory_requirement_fails`
- Documentation: `checkpoint:CLOSURE-REQUIREMENTS.md`
- Validation: `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-028` — The completeness audit covers this whole execution before handoff

Every requirement of this delivery is declared, complete and evidenced; the auditing role reports gaps and never repairs them silently.

- Implementation: `file:.iacode/agents/delivery-completeness-validator.md`
- Positive regression: `test:DeliveryAssuranceGateTests.test_completeness_pass_claimed_over_an_incomplete_matrix_is_rejected`
- Documentation: `checkpoint:DECISIONS.md`
- Validation: `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-029` — The internal mirror of this delivery is the tool's own output

M0-INTERNAL-MIRROR.json was produced by running m0_mirror_audit.py over this checkpoint, never written by hand.

- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`
- Positive regression: `test:InternalAssuranceTests.test_a_failed_mirror_check_cannot_produce_a_pass`
- Documentation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`

### `FCR-030` — The adversarial position of the changed surface is executed

The battery attacks the states the repair opens as well as the states it closes, including an unjustified inapplicable dimension, one with items, one counted as a pass, one under the older report version, and one declared away while the registry names work.

- Implementation: `file:scripts/development-ledger/m0_red_team.py`
- Positive regression: `test:InternalAssuranceTests.test_a_missing_mandatory_attack_is_rejected`
- Documentation: `checkpoint:CP11-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:M0-INTERNAL-RED-TEAM.json`, `checkpoint:M0-INTERNAL-RED-TEAM.json`

### `FCR-031` — The whole suite passes and every skip is accounted for

The suite is executed in full, the result object is read directly, and any skip is recorded with its condition rather than counted as a pass.

- Implementation: `file:tests/test_development_ledger.py`
- Positive regression: `test:DerivedTestCountTests.test_a_count_larger_than_what_exists_is_refused`
- Documentation: `checkpoint:FINAL-REPORT.md`
- Validation: `checkpoint:TESTS.json`, `checkpoint:COUNTS.json`

### `FCR-032` — The delivery validates from a clean clone

The suite, the validators and the closure controls all run green in a fresh clone with no workspace state.

- Implementation: `file:scripts/development-ledger/m0_mirror_audit.py`
- Positive regression: `test:InternalAssuranceTests.test_a_failed_mirror_check_cannot_produce_a_pass`
- Documentation: `checkpoint:FINAL-REPORT.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`

### `FCR-033` — The CP-0011 findings closure record exists and is complete

Every finding the sealed review report raises is closed, with root cause, implementation, positive and negative regression and evidence.

- Implementation: `checkpoint:CP11-FINDINGS-CLOSURE.json`
- Positive regression: `test:FindingsClosureTests.test_an_open_finding_blocks_the_delivery`
- Documentation: `checkpoint:CP11-FINDINGS-CLOSURE.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-034` — An internal auditor that did not implement audits the delivery

A separate auditing pass verifies the closure, the executed mirror, the three applicability outcomes, the Gate transition, the historical compatibility, the memory and the clean clone, and records its verdict as internal, never as independent validation.

- Implementation: `file:.iacode/agents/m0-closure-auditor.md`
- Positive regression: `test:MemoryStatusVocabularyTests.test_internal_and_external_pass_are_distinct_statuses`
- Documentation: `checkpoint:DECISIONS.md`
- Validation: `checkpoint:GATE0-TRANSITION-SIMULATION.json`

### `FCR-035` — The checkpoint carries every mandatory artifact of the current protocol

The standard ledger plus the artifacts this correction owes: the requirement register, the findings closure, the mirror semantics validation, the Gate transition simulation, the affected Red Team and the final internal audit.

- Implementation: `checkpoint:FINAL-CORRECTION-REQUIREMENTS.json`
- Positive regression: `test:SetupChecklistTests.test_checklist_exists_and_is_referenced`
- Documentation: `checkpoint:FINAL-CORRECTION-REQUIREMENTS.md`
- Validation: `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-036` — The delivery closes at READY_FOR_REVIEW and never grants itself a Gate

The implementing run records no independent verdict; independentReview and redTeam stay PENDING and blockedBy is empty.

- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Positive regression: `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`
- Documentation: `checkpoint:STATUS.md`
- Validation: `checkpoint:STATE.json`

### `FCR-037` — The next action is a fresh-session independent M0 audit and Gate 0 stays blocked

NEXT.md names the audit, not Gate 0, and no Gate 0 work was started.

- Implementation: `checkpoint:NEXT.md`
- Positive regression: `test:GateTransitionSimulationTests.test_no_runtime_of_the_next_gate_was_implemented`
- Documentation: `checkpoint:HANDOFF.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`, `checkpoint:CP11-FINDINGS-CLOSURE.json`

### `FCR-038` — No historical checkpoint, commit or tag is rewritten

Every correction belongs to this checkpoint; the sealed history is read, anchored and validated, never edited.

- Implementation: `file:.iacode/anchors/checkpoint-chain.json`
- Positive regression: `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`
- Documentation: `checkpoint:DIFF-SUMMARY.md`
- Validation: `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`
