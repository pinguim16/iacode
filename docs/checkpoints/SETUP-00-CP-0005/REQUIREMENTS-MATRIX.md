# Requirements Matrix — SETUP-00-CP-0005

Authoritative machine-readable form: [REQUIREMENTS-MATRIX.json](REQUIREMENTS-MATRIX.json),
validated against `.iacode/schemas/requirements-matrix.schema.json`. This document is the
rendered view; the JSON is what the Delivery Completeness Validator audits.

Statuses: `NOT_STARTED`, `IN_PROGRESS`, `COMPLETE`, `PARTIAL`, `MISSING`, `NOT_APPLICABLE`.
`PARTIAL` or `MISSING` on any requirement blocks `READY_FOR_REVIEW`.

| ID | Mandatory | Status | Requirement | Source |
|---|---|---|---|---|
| `REQ-0001` | yes | `COMPLETE` | Record every finalization attempt, including refusals that happen before the main operation runs, such as detached HEAD, a checkpoint that is not the LATEST target, and an invalid commit reference. | CP-0004 REVIEW-REPORT.md R3.1 / RED-TEAM-REPORT.md RT-02 |
| `REQ-0002` | yes | `COMPLETE` | Every recorded command string must be executable from its declared working directory, including the interpreter and repository-relative script path. | CP-0004 REVIEW-REPORT.md R3.2 / NEXT.md item 3 |
| `REQ-0003` | yes | `COMPLETE` | READY_FOR_REVIEW must be impossible while blockedBy is non-empty, for every schema version and regardless of which tool sealed the checkpoint. | CP-0004 RED-TEAM-REPORT.md RT-01 / NEXT.md item 1 |
| `REQ-0004` | yes | `COMPLETE` | Command records must be reproducible and auditable: identifier, timestamp, runtime, working directory, command, sanitized arguments, repository commit, purpose, referenced inputs, result, exit code or canonical result code, duration, and stream artifacts. | CP-0004 RED-TEAM-REPORT.md RT-02 / prompt section 7 |
| `REQ-0005` | yes | `COMPLETE` | Regression that rejects READY_FOR_REVIEW with a non-empty blockedBy after a fully resealed fixture, reproducing the escaped RT-01 attack end to end. | CP-0004 NEXT.md item 1 |
| `REQ-0006` | yes | `COMPLETE` | Regressions proving each early finalization refusal is appended to the ledger before the error is returned. | CP-0004 NEXT.md item 2 |
| `REQ-0007` | yes | `COMPLETE` | Re-execute the new tests, the entire suite, static analysis, checkpoint validation, the secret scan, and the adversarial battery. | CP-0004 NEXT.md item 4 / prompt section 19 |
| `REQ-0008` | yes | `COMPLETE` | Close CP-0005 at READY_FOR_REVIEW for an independent Codex review, never at GATE_PASS. | CP-0004 NEXT.md item 5 / prompt section 22 |
| `REQ-0009` | yes | `COMPLETE` | Execute the cold start and read the authoritative documents plus SETUP-00-CP-0003 and SETUP-00-CP-0004 in full before altering any file. | prompt section 2 |
| `REQ-0010` | yes | `COMPLETE` | Produce REQUIREMENTS-MATRIX.json and REQUIREMENTS-MATRIX.md with the mandated fields and canonical statuses before implementation begins. | prompt section 3 |
| `REQ-0011` | yes | `COMPLETE` | Create .iacode/schemas/requirements-matrix.schema.json validating unique identifiers, boolean mandatory, canonical status, evidence arrays, justified NOT_APPLICABLE, and evidence-bearing COMPLETE. | prompt section 15 |
| `REQ-0012` | yes | `COMPLETE` | Create the canonical Test Rework / Green Keeper role contract at .iacode/agents/test-rework-greenkeeper.md. | prompt section 8 |
| `REQ-0013` | yes | `COMPLETE` | Create the Green Keeper adapters using mechanisms the tools actually support, without claiming unsupported capability. | prompt section 8 and 13 |
| `REQ-0014` | yes | `COMPLETE` | Record every Green Keeper cycle in REWORK-LOG.jsonl with cycle, trigger, failed gate, failure evidence, root cause summary, files changed, commands executed, result, and remaining failures. | prompt section 8 |
| `REQ-0015` | yes | `COMPLETE` | Create .iacode/schemas/rework-log.schema.json and validate the log against it. | prompt section 17 |
| `REQ-0016` | yes | `COMPLETE` | Create the canonical Delivery Completeness Validator role contract at .iacode/agents/delivery-completeness-validator.md, as an auditor that may not implement or silently correct. | prompt section 9 |
| `REQ-0017` | yes | `COMPLETE` | Create the Delivery Completeness Validator adapters using supported mechanisms. | prompt section 9 and 13 |
| `REQ-0018` | yes | `COMPLETE` | Produce COMPLETENESS-REPORT.json and COMPLETENESS-REPORT.md carrying total, mandatory, complete, partial, missing, not applicable, coverage percent, evidence coverage percent, and result. | prompt section 9 |
| `REQ-0019` | yes | `COMPLETE` | Create .iacode/schemas/completeness-report.schema.json and validate the report against it. | prompt section 16 |
| `REQ-0020` | yes | `COMPLETE` | Create the DELIVERY_COMPLETENESS_GATE control with PASS, FAIL, and NOT_EXECUTED states, and make READY_FOR_REVIEW require PASS. | prompt section 10 |
| `REQ-0021` | yes | `COMPLETE` | Create the GREEN_KEEPER_GATE control that is PASS only when every mandatory executable gate is green, remaining failures are zero, and unresolved rework items are zero; an external blocker yields BLOCKED, never PASS. | prompt section 11 |
| `REQ-0022` | yes | `COMPLETE` | Make the eleven-step delivery order mandatory in the development contract, quality gates, checkpoint protocol, handoff protocol, definition of done, START-HERE, AGENTS.md, and CLAUDE.md. | prompt section 12 |
| `REQ-0023` | yes | `COMPLETE` | Separate the two new roles honestly: the Green Keeper may change code, the Completeness Validator may not, and any emulation limit is documented rather than overstated. | prompt section 13 |
| `REQ-0024` | yes | `COMPLETE` | Extend the checkpoint schema with requirementsMatrix, greenKeeper, deliveryCompleteness, reworkCycles, independentReview, and redTeam, and make READY_FOR_REVIEW impossible when the Green Keeper or completeness gate is not PASS. | prompt section 14 |
| `REQ-0025` | yes | `COMPLETE` | Add the thirteen mandated control tests covering coverage, partial, missing, unjustified NOT_APPLICABLE, evidence-free COMPLETE, red tests, unresolved rework, blockers, inconsistent gate claims, and an unexecuted validator. | prompt section 18 |
| `REQ-0026` | yes | `COMPLETE` | Run the full re-execution sequence in order and escalate to the Green Keeper on any red result. | prompt section 19 |
| `REQ-0027` | yes | `COMPLETE` | Apply the Green Keeper to CP-0005 itself and record every cycle, including failures caused by this run's own development. | prompt section 20 |
| `REQ-0028` | yes | `COMPLETE` | Run the Delivery Completeness Validator against CP-0005 before READY_FOR_REVIEW and repeat the correction loop until coverage is total. | prompt section 21 |
| `REQ-0029` | yes | `COMPLETE` | Enforce the CP-0005 exit conditions: total coverage, both new gates PASS, green tests, mandatory quality green, empty blockedBy, and zero unresolved rework. | prompt section 22 |
| `REQ-0030` | yes | `COMPLETE` | Create docs/checkpoints/SETUP-00-CP-0005/ containing every mandated artifact. | prompt section 23 |
| `REQ-0031` | yes | `COMPLETE` | Give Codex a handoff that allows verification of every CP-0004 finding, the matrix, completeness, the Green Keeper, the rework log, quality evidence, reproducibility, the READY_FOR_REVIEW invariants, and the tests, with exact commands. | prompt section 24 |
| `REQ-0032` | yes | `COMPLETE` | Maintain the Engineering Ledger continuously with requirement, plan, file, command, exit code, failure, cause, correction, retest, result, and evidence, and no private chain-of-thought. | prompt section 25 |
| `REQ-0033` | yes | `COMPLETE` | Keep trainingAllowed false by default and change no rights policy without evidence. | prompt section 26 |
| `REQ-0034` | yes | `COMPLETE` | Respect every prohibition: no Gate 0, no modification of sealed checkpoints or historical tags, no GATE_PASS, no skipped Green Keeper or Completeness Validator, no red test, no partial requirement, and no blocker at READY_FOR_REVIEW. | prompt section 27 |
| `REQ-0035` | yes | `COMPLETE` | Deliver the final report with checkpoint, status, requirement counts and coverage, Green Keeper result and cycles, completeness result, tests, quality gates, per-finding CP-0004 status, remaining blockers, commit, tag, next step, and Gate 0 state. | prompt section 28 |
| `REQ-0036` | yes | `COMPLETE` | Preserve backward compatibility: CP-0001, CP-0002, CP-0003, and CP-0004 must keep validating under the corrected tooling, with their tags unchanged. | docs/CHECKPOINT-PROTOCOL.md schema versions / ADR-0007 |
| `REQ-0037` | yes | `COMPLETE` | Record the structural decisions of this checkpoint as an ADR, including the new schema version and the two new control gates. | docs/DEVELOPMENT-CONTRACT.md structural decisions |
| `REQ-0038` | yes | `COMPLETE` | Do not start Gate 0 and keep it explicitly blocked. | prompt section 27 / docs/MASTER-PLAN.md |

## Evidence

### REQ-0001

Record every finalization attempt, including refusals that happen before the main operation runs, such as detached HEAD, a checkpoint that is not the LATEST target, and an invalid commit reference.

- Implementation: `file:scripts/development-ledger/finalize_checkpoint.py`
- Test: `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_invalid_commit_reference_refusal_is_recorded`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `command:cmd-0011`
- Notes: Preconditions are evaluated before any write and the attempt is appended before the error is returned.

### REQ-0002

Every recorded command string must be executable from its declared working directory, including the interpreter and repository-relative script path.

- Implementation: `file:scripts/development-ledger/finalize_checkpoint.py`, `file:scripts/development-ledger/record_command.py`
- Test: `test:FinalizationAttemptRecordingTests.test_recorded_finalizer_command_is_executable_from_its_working_directory`, `test:CommandReproducibilityTests.test_bare_script_name_is_rejected`, `test:CommandReproducibilityTests.test_unresolvable_script_path_is_rejected`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `command:cmd-0011`

### REQ-0003

READY_FOR_REVIEW must be impossible while blockedBy is non-empty, for every schema version and regardless of which tool sealed the checkpoint.

- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`, `test:StatusBlockerInvariantTests.test_gate_pass_with_blocker_fails`, `test:StatusBlockerInvariantTests.test_blocked_requires_a_reason`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `command:cmd-0013`
- Notes: Enforced for every schema version, so the sealed checkpoints are judged by it too.

### REQ-0004

Command records must be reproducible and auditable: identifier, timestamp, runtime, working directory, command, sanitized arguments, repository commit, purpose, referenced inputs, result, exit code or canonical result code, duration, and stream artifacts.

- Implementation: `file:.iacode/schemas/command.schema.json`, `file:scripts/development-ledger/record_command.py`, `file:scripts/development-ledger/ledger_common.py`
- Test: `test:CommandReproducibilityTests.test_complete_record_passes`, `test:CommandReproducibilityTests.test_precondition_rejection_must_not_fake_an_exit_code`, `test:CommandReproducibilityTests.test_declared_input_must_exist`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `command:cmd-0013`

### REQ-0005

Regression that rejects READY_FOR_REVIEW with a non-empty blockedBy after a fully resealed fixture, reproducing the escaped RT-01 attack end to end.

- Implementation: `file:tests/test_development_ledger.py`
- Test: `test:ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected`
- Documentation: `checkpoint:HANDOFF.md`
- Validation: `command:cmd-0011`
- Notes: The fixture reseals through the real finalizer and then validates, reproducing the escaped attack.

### REQ-0006

Regressions proving each early finalization refusal is appended to the ledger before the error is returned.

- Implementation: `file:tests/test_development_ledger.py`
- Test: `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_invalid_commit_reference_refusal_is_recorded`
- Documentation: `checkpoint:HANDOFF.md`
- Validation: `command:cmd-0011`

### REQ-0007

Re-execute the new tests, the entire suite, static analysis, checkpoint validation, the secret scan, and the adversarial battery.

- Implementation: `checkpoint:REWORK-LOG.jsonl`
- Test: `test:DeliveryLifecycleTests.test_full_delivery_assurance_flow_reaches_ready_for_review`
- Documentation: `checkpoint:FINAL-REPORT.md`
- Validation: `command:cmd-0011`, `command:cmd-0012`, `command:cmd-0013`

### REQ-0008

Close CP-0005 at READY_FOR_REVIEW for an independent Codex review, never at GATE_PASS.

- Implementation: `checkpoint:STATE.json`
- Test: `test:DeliveryLifecycleTests.test_full_delivery_assurance_flow_reaches_ready_for_review`
- Documentation: `checkpoint:NEXT.md`
- Validation: `command:cmd-0013`

### REQ-0009

Execute the cold start and read the authoritative documents plus SETUP-00-CP-0003 and SETUP-00-CP-0004 in full before altering any file.

- Implementation: `checkpoint:COMMANDS.jsonl`
- Test: _none recorded_
- Documentation: `checkpoint:PLAN.md`
- Validation: `checkpoint:FILES.json`
- Notes: FILES.json filesRead records the sealed CP-0003 and CP-0004 checkpoints read before any change.

### REQ-0010

Produce REQUIREMENTS-MATRIX.json and REQUIREMENTS-MATRIX.md with the mandated fields and canonical statuses before implementation begins.

- Implementation: `checkpoint:REQUIREMENTS-MATRIX.json`
- Test: _none recorded_
- Documentation: `checkpoint:REQUIREMENTS-MATRIX.md`
- Validation: `checkpoint:COMPLETENESS-REPORT.json`

### REQ-0011

Create .iacode/schemas/requirements-matrix.schema.json validating unique identifiers, boolean mandatory, canonical status, evidence arrays, justified NOT_APPLICABLE, and evidence-bearing COMPLETE.

- Implementation: `file:.iacode/schemas/requirements-matrix.schema.json`
- Test: `test:DeliveryCompletenessMatrixTests.test_complete_without_evidence_fails`, `test:DeliveryCompletenessMatrixTests.test_not_applicable_without_justification_fails`
- Documentation: `file:scripts/development-ledger/README.md`
- Validation: `command:cmd-0013`

### REQ-0012

Create the canonical Test Rework / Green Keeper role contract at .iacode/agents/test-rework-greenkeeper.md.

- Implementation: `file:.iacode/agents/test-rework-greenkeeper.md`
- Test: `test:ClaudeAdapterTests.test_project_agents_match_canonical_role_names`
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `command:cmd-0011`

### REQ-0013

Create the Green Keeper adapters using mechanisms the tools actually support, without claiming unsupported capability.

- Implementation: `file:.claude/agents/test-rework-greenkeeper.md`
- Test: `test:ClaudeAdapterTests.test_project_agents_defer_to_canonical_contracts`
- Documentation: `file:AGENTS.md`, `file:CLAUDE.md`
- Validation: `command:cmd-0011`
- Notes: Claude uses the verified .claude/agents mechanism; Codex adopts the canonical contract through AGENTS.md because it has no per-agent project file mechanism here.

### REQ-0014

Record every Green Keeper cycle in REWORK-LOG.jsonl with cycle, trigger, failed gate, failure evidence, root cause summary, files changed, commands executed, result, and remaining failures.

- Implementation: `file:scripts/development-ledger/green_keeper.py`
- Test: `test:GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `test:GreenKeeperToolTests.test_gate_invocations_are_recorded_reproducibly`
- Documentation: `file:scripts/development-ledger/README.md`
- Validation: `checkpoint:REWORK-LOG.jsonl`

### REQ-0015

Create .iacode/schemas/rework-log.schema.json and validate the log against it.

- Implementation: `file:.iacode/schemas/rework-log.schema.json`
- Test: `test:GreenKeeperToolTests.test_repaired_gate_is_reported_as_green_in_a_new_cycle`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `command:cmd-0013`

### REQ-0016

Create the canonical Delivery Completeness Validator role contract at .iacode/agents/delivery-completeness-validator.md, as an auditor that may not implement or silently correct.

- Implementation: `file:.iacode/agents/delivery-completeness-validator.md`
- Test: `test:ClaudeAdapterTests.test_project_agents_match_canonical_role_names`
- Documentation: `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `command:cmd-0011`

### REQ-0017

Create the Delivery Completeness Validator adapters using supported mechanisms.

- Implementation: `file:.claude/agents/delivery-completeness-validator.md`
- Test: `test:ClaudeAdapterTests.test_project_agents_have_supported_required_frontmatter`
- Documentation: `file:AGENTS.md`, `file:CLAUDE.md`
- Validation: `command:cmd-0011`

### REQ-0018

Produce COMPLETENESS-REPORT.json and COMPLETENESS-REPORT.md carrying total, mandatory, complete, partial, missing, not applicable, coverage percent, evidence coverage percent, and result.

- Implementation: `file:scripts/development-ledger/check_completeness.py`
- Test: `test:DeliveryCompletenessMatrixTests.test_every_requirement_complete_passes`
- Documentation: `file:scripts/development-ledger/README.md`
- Validation: `checkpoint:COMPLETENESS-REPORT.json`, `checkpoint:COMPLETENESS-REPORT.md`

### REQ-0019

Create .iacode/schemas/completeness-report.schema.json and validate the report against it.

- Implementation: `file:.iacode/schemas/completeness-report.schema.json`
- Test: `test:DeliveryAssuranceGateTests.test_completeness_report_inconsistent_with_the_matrix_is_rejected`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `command:cmd-0013`

### REQ-0020

Create the DELIVERY_COMPLETENESS_GATE control with PASS, FAIL, and NOT_EXECUTED states, and make READY_FOR_REVIEW require PASS.

- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`, `test:DeliveryAssuranceGateTests.test_completeness_pass_claimed_over_an_incomplete_matrix_is_rejected`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `command:cmd-0013`

### REQ-0021

Create the GREEN_KEEPER_GATE control that is PASS only when every mandatory executable gate is green, remaining failures are zero, and unresolved rework items are zero; an external blocker yields BLOCKED, never PASS.

- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`, `file:scripts/development-ledger/green_keeper.py`
- Test: `test:DeliveryAssuranceGateTests.test_green_keeper_not_executed_blocks_review`, `test:DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `test:GreenKeeperToolTests.test_external_blocker_never_reports_pass`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `command:cmd-0013`

### REQ-0022

Make the eleven-step delivery order mandatory in the development contract, quality gates, checkpoint protocol, handoff protocol, definition of done, START-HERE, AGENTS.md, and CLAUDE.md.

- Implementation: `file:docs/SETUP-00-CHECKLIST.md`
- Test: `test:SetupChecklistTests.test_documentation_links_resolve`
- Documentation: `file:docs/DEVELOPMENT-CONTRACT.md`, `file:docs/QUALITY-GATES.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/HANDOFF-PROTOCOL.md`, `file:docs/DEFINITION-OF-DONE.md`, `file:START-HERE.md`, `file:AGENTS.md`, `file:CLAUDE.md`
- Validation: `command:cmd-0011`

### REQ-0023

Separate the two new roles honestly: the Green Keeper may change code, the Completeness Validator may not, and any emulation limit is documented rather than overstated.

- Implementation: `file:AGENTS.md`, `file:CLAUDE.md`
- Test: _none recorded_
- Documentation: `file:docs/adr/ADR-0008-delivery-assurance-gates.md`, `checkpoint:DECISIONS.md`
- Validation: `checkpoint:RISKS.md`
- Notes: The separation is one of role and artifact inside a single session; it is documented as emulation, not claimed as independence.

### REQ-0024

Extend the checkpoint schema with requirementsMatrix, greenKeeper, deliveryCompleteness, reworkCycles, independentReview, and redTeam, and make READY_FOR_REVIEW impossible when the Green Keeper or completeness gate is not PASS.

- Implementation: `file:.iacode/schemas/checkpoint.schema.json`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:DeliveryAssuranceGateTests.test_missing_assurance_block_is_rejected`, `test:DeliveryAssuranceGateTests.test_green_keeper_not_executed_blocks_review`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `command:cmd-0013`

### REQ-0025

Add the thirteen mandated control tests covering coverage, partial, missing, unjustified NOT_APPLICABLE, evidence-free COMPLETE, red tests, unresolved rework, blockers, inconsistent gate claims, and an unexecuted validator.

- Implementation: `file:tests/test_development_ledger.py`
- Test: `test:DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `test:DeliveryCompletenessMatrixTests.test_missing_mandatory_requirement_fails`, `test:DeliveryCompletenessMatrixTests.test_partial_requirement_fails`, `test:DeliveryAssuranceGateTests.test_red_tests_block_review`, `test:DeliveryAssuranceGateTests.test_unresolved_rework_blocks_review`, `test:DeliveryAssuranceGateTests.test_complete_delivery_passes_every_gate`
- Documentation: `checkpoint:FINAL-REPORT.md`
- Validation: `command:cmd-0011`

### REQ-0026

Run the full re-execution sequence in order and escalate to the Green Keeper on any red result.

- Implementation: `checkpoint:REWORK-LOG.jsonl`
- Test: _none recorded_
- Documentation: `checkpoint:FINAL-REPORT.md`
- Validation: `command:cmd-0011`, `command:cmd-0012`, `command:cmd-0013`

### REQ-0027

Apply the Green Keeper to CP-0005 itself and record every cycle, including failures caused by this run's own development.

- Implementation: `checkpoint:REWORK-LOG.jsonl`
- Test: _none recorded_
- Documentation: `checkpoint:DECISIONS.md`
- Validation: `command:cmd-0011`
- Notes: Cycle 1 failed on checkpoint validation and a later suite failure came from this run's own fixture; both were repaired at the cause.

### REQ-0028

Run the Delivery Completeness Validator against CP-0005 before READY_FOR_REVIEW and repeat the correction loop until coverage is total.

- Implementation: `checkpoint:COMPLETENESS-REPORT.json`
- Test: _none recorded_
- Documentation: `checkpoint:DECISIONS.md`
- Validation: `checkpoint:COMPLETENESS-REPORT.md`

### REQ-0029

Enforce the CP-0005 exit conditions: total coverage, both new gates PASS, green tests, mandatory quality green, empty blockedBy, and zero unresolved rework.

- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:DeliveryAssuranceGateTests.test_complete_delivery_passes_every_gate`, `test:DeliveryLifecycleTests.test_full_delivery_assurance_flow_reaches_ready_for_review`
- Documentation: `file:docs/QUALITY-GATES.md`
- Validation: `command:cmd-0013`

### REQ-0030

Create docs/checkpoints/SETUP-00-CP-0005/ containing every mandated artifact.

- Implementation: `checkpoint:STATUS.md`
- Test: _none recorded_
- Documentation: `checkpoint:FINAL-REPORT.md`
- Validation: `checkpoint:FILES.json`, `command:cmd-0013`

### REQ-0031

Give Codex a handoff that allows verification of every CP-0004 finding, the matrix, completeness, the Green Keeper, the rework log, quality evidence, reproducibility, the READY_FOR_REVIEW invariants, and the tests, with exact commands.

- Implementation: `checkpoint:HANDOFF.md`
- Test: _none recorded_
- Documentation: `checkpoint:HANDOFF.md`
- Validation: `command:cmd-0013`

### REQ-0032

Maintain the Engineering Ledger continuously with requirement, plan, file, command, exit code, failure, cause, correction, retest, result, and evidence, and no private chain-of-thought.

- Implementation: `checkpoint:COMMANDS.jsonl`
- Test: _none recorded_
- Documentation: `checkpoint:DECISIONS.md`
- Validation: `command:cmd-0013`

### REQ-0033

Keep trainingAllowed false by default and change no rights policy without evidence.

- Implementation: `checkpoint:PROVENANCE.json`
- Test: _none recorded_
- Documentation: `file:.iacode/policies/provenance-policy.md`
- Validation: `command:cmd-0013`

### REQ-0034

Respect every prohibition: no Gate 0, no modification of sealed checkpoints or historical tags, no GATE_PASS, no skipped Green Keeper or Completeness Validator, no red test, no partial requirement, and no blocker at READY_FOR_REVIEW.

- Implementation: `checkpoint:STATE.json`
- Test: `test:HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`
- Documentation: `checkpoint:DECISIONS.md`
- Validation: `command:cmd-0013`

### REQ-0035

Deliver the final report with checkpoint, status, requirement counts and coverage, Green Keeper result and cycles, completeness result, tests, quality gates, per-finding CP-0004 status, remaining blockers, commit, tag, next step, and Gate 0 state.

- Implementation: `checkpoint:FINAL-REPORT.md`
- Test: _none recorded_
- Documentation: `checkpoint:FINAL-REPORT.md`
- Validation: `command:cmd-0013`

### REQ-0036

Preserve backward compatibility: CP-0001, CP-0002, CP-0003, and CP-0004 must keep validating under the corrected tooling, with their tags unchanged.

- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_second_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_third_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `command:cmd-0011`

### REQ-0037

Record the structural decisions of this checkpoint as an ADR, including the new schema version and the two new control gates.

- Implementation: `file:docs/adr/ADR-0008-delivery-assurance-gates.md`
- Test: _none recorded_
- Documentation: `file:docs/adr/ADR-0008-delivery-assurance-gates.md`
- Validation: `test:SetupChecklistTests.test_documentation_links_resolve`

### REQ-0038

Do not start Gate 0 and keep it explicitly blocked.

- Implementation: `checkpoint:STATE.json`
- Test: _none recorded_
- Documentation: `checkpoint:NEXT.md`
- Validation: `command:cmd-0013`
- Notes: No runtime, model gateway, agent runtime, sandbox, quality runtime, or IDE integration exists in the change set.

