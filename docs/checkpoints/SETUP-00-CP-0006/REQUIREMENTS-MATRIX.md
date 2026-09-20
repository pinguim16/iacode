# Requirements Matrix - SETUP-00-CP-0006

Authoritative machine-readable form: [REQUIREMENTS-MATRIX.json](REQUIREMENTS-MATRIX.json),
validated against `.iacode/schemas/requirements-matrix.schema.json`. This document is the
rendered view; the JSON is what the Delivery Completeness Validator audits.

Identifiers prefixed `LESSON-REQ-` are derived from the engineering memory by
[LESSON-PREFLIGHT.md](LESSON-PREFLIGHT.md). A lesson becomes a requirement, the requirement
carries evidence, and the evidence is validated.

Statuses: `NOT_STARTED`, `IN_PROGRESS`, `COMPLETE`, `PARTIAL`, `MISSING`, `NOT_APPLICABLE`.
`PARTIAL` or `MISSING` on any requirement blocks `READY_FOR_REVIEW`.

| ID | Mandatory | Status | Requirement | Source |
|---|---|---|---|---|
| `REQ-0001` | yes | `COMPLETE` | Execute the cold start, reading the entry contract, the development contracts, the Master Plan, the SETUP-00 checklist, LATEST, and the complete CP-0004 and CP-0005 checkpoints, then validate and baseline before altering anything. | prompt section 1 |
| `REQ-0002` | yes | `COMPLETE` | Create the engineering memory tree at .iacode/memory/ with README.md, LESSONS.md, lessons.jsonl, patterns/, anti-patterns/, incidents/, guardrails/, and retrospectives/. | prompt section 2 |
| `REQ-0003` | yes | `COMPLETE` | State that the memory belongs to the IACode engineering organization and is not the user's personal memory. | prompt section 2 |
| `REQ-0004` | yes | `COMPLETE` | Create .iacode/schemas/lesson.schema.json carrying every mandated lesson field, the five canonical statuses, training denied by default, and no chain-of-thought or secrets. | prompt section 3 |
| `REQ-0005` | yes | `COMPLETE` | Support at least the sixteen mandated lesson categories. | prompt section 4 |
| `REQ-0006` | yes | `COMPLETE` | Implement the OBSERVED to CONFIRMED to GUARDED lifecycle, where GUARDED requires concrete preventive evidence such as a test, validator, lint rule, policy, schema, invariant, or automated check, and never documentation alone. | prompt section 5 |
| `REQ-0007` | yes | `COMPLETE` | Give every lesson a recurrence key, increment recurrenceCount on a repeat, and record a GUARDRAIL_FAILURE when a repeat happens against a GUARDED lesson. | prompt section 6 |
| `REQ-0008` | yes | `COMPLETE` | Provide a lesson extraction mechanism that consumes rework logs, review findings, Red Team findings, failures, and retrospectives, and produces candidates no stronger than OBSERVED. | prompt section 7 |
| `REQ-0009` | yes | `COMPLETE` | Provide a lesson validator checking schema, unique identifiers, valid status, provenance, training policy, evidence, preventive evidence for GUARDED, absence of secrets, and recurrence consistency, exiting zero only when valid. | prompt section 8 |
| `REQ-0010` | yes | `COMPLETE` | Provide a mandatory lesson preflight that takes gate, scope, technologies, and modules, and writes LESSON-PREFLIGHT.json and LESSON-PREFLIGHT.md naming each applicable lesson with its reason, required check, and required evidence. | prompt section 9 |
| `REQ-0011` | yes | `COMPLETE` | Turn applicable lessons into derived requirements in the Gate requirements matrix, so a lesson becomes a requirement, then evidence, then validation. | prompt section 10 |
| `REQ-0012` | yes | `COMPLETE` | Populate the initial memory only from facts confirmed by the existing checkpoints, covering at least the twelve listed SETUP-00 lessons, each referencing historical evidence. | prompt section 11 |
| `REQ-0013` | yes | `COMPLETE` | Document the principle that an important lesson must become an automated guardrail and that no control may depend on someone remembering to read LESSONS.md. | prompt section 12 |
| `REQ-0014` | yes | `COMPLETE` | Require a retrospective for every completed Gate, provide its template, and record this checkpoint's own retrospective. | prompt section 13 |
| `REQ-0015` | yes | `COMPLETE` | Make the Implementer, tests, Green Keeper, and Delivery Completeness Validator sequence mandatory for every delivery, and forbid advancing with red gates, coverage below total, any partial, or any missing requirement. | prompt section 14 |
| `REQ-0016` | yes | `COMPLETE` | Define the external validation cadence and the milestone grouping M0 through M6, and state that the auditor evaluates the milestone as a whole rather than only the last Gate. | prompt section 15 |
| `REQ-0017` | yes | `COMPLETE` | Add externalAuditRequired and externalAuditReason so an extraordinary audit before a milestone is possible only with a recorded reason, and list the triggering categories. | prompt section 16 |
| `REQ-0018` | yes | `COMPLETE` | Distinguish INTERNAL_GATE_PASS from MILESTONE_EXTERNAL_PASS so an internal verdict is never described as independent external validation. | prompt section 17 |
| `REQ-0019` | yes | `COMPLETE` | Define the milestone checkpoint that consolidates the included Gates, lessons, open risks, architecture changes, tests, regression, cross-gate integration, requirements completeness, outstanding debt, provenance, and model usage. | prompt section 18 |
| `REQ-0020` | yes | `COMPLETE` | Record that Codex acts primarily as the milestone independent auditor and what it must validate. | prompt section 19 |
| `REQ-0021` | yes | `COMPLETE` | Update the governing documents and add docs/ENGINEERING-MEMORY.md and docs/MILESTONE-VALIDATION.md. | prompt section 20 |
| `REQ-0022` | yes | `COMPLETE` | Update the canonical agent contracts so the Engineering Lead runs the preflight, the Planner incorporates lesson requirements, the Implementer consults applicable checks, the Green Keeper records failures as lesson candidates, the Completeness Validator confirms lesson-derived requirements, the Historian records lessons, and the Reviewer looks for recurrence. | prompt section 21 |
| `REQ-0023` | yes | `COMPLETE` | Add the seventeen mandated tests for the lesson schema, lifecycle, recurrence, preflight, derived requirements, milestone grouping, audit policy, and historical compatibility. | prompt section 22 |
| `REQ-0024` | yes | `COMPLETE` | Use the real Green Keeper on this checkpoint, repairing until green or declaring a real external blocker, and never reaching READY_FOR_REVIEW with anything red. | prompt section 23 |
| `REQ-0025` | yes | `COMPLETE` | Run the real Delivery Completeness Validator before handoff and reach total coverage with zero partial, zero missing, and total evidence coverage. | prompt section 24 |
| `REQ-0026` | yes | `COMPLETE` | Close CP-0006 at READY_FOR_REVIEW rather than GATE_PASS, because SETUP-00 still needs the M0 milestone audit. | prompt section 25 |
| `REQ-0027` | yes | `COMPLETE` | Make NEXT.md request a single Codex M0 validation covering CP-0005, CP-0006, and SETUP-00 as a whole, rather than separate validations. | prompt section 26 |
| `REQ-0028` | yes | `COMPLETE` | Respect every prohibition: no Gate 0, no modification of sealed checkpoints or historical tags, no chain-of-thought, no secrets, no automatic training eligibility, and no removal of the Green Keeper or completeness controls. | prompt section 27 |
| `REQ-0029` | yes | `COMPLETE` | Deliver the final report with checkpoint, status, coverage, Green Keeper, completeness, tests, lessons created and guarded, preflight, milestone policy, historical compatibility, commit, tag, risks, and next action. | prompt section 28 |
| `REQ-0030` | yes | `COMPLETE` | Preserve backward compatibility: CP-0001 through CP-0005 must keep validating under the extended tooling, with their tags unchanged. | docs/CHECKPOINT-PROTOCOL.md schema versions |
| `REQ-0031` | yes | `COMPLETE` | Record the structural decisions of this checkpoint as an ADR, covering the engineering memory, the guardrail principle, and the milestone validation policy. | docs/DEVELOPMENT-CONTRACT.md structural decisions |
| `REQ-0032` | yes | `COMPLETE` | Maintain the Engineering Ledger continuously with requirement, plan, file, command, exit code, failure, cause, correction, retest, result, and evidence. | docs/DEVELOPMENT-CONTRACT.md mandatory controls |
| `REQ-0033` | yes | `COMPLETE` | Keep trainingAllowed false by default for every new artifact and change no rights policy without evidence. | prompt section 3 and 27 |
| `LESSON-REQ-0001` | yes | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag | lesson preflight, LSN-0001 |
| `LESSON-REQ-0002` | yes | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion | lesson preflight, LSN-0002 |
| `LESSON-REQ-0003` | yes | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution | lesson preflight, LSN-0003 |
| `LESSON-REQ-0004` | yes | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked | lesson preflight, LSN-0004 |
| `LESSON-REQ-0005` | yes | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement | lesson preflight, LSN-0005 |
| `LESSON-REQ-0006` | yes | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it | lesson preflight, LSN-0006 |
| `LESSON-REQ-0007` | yes | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work | lesson preflight, LSN-0007 |
| `LESSON-REQ-0008` | yes | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff | lesson preflight, LSN-0008 |
| `LESSON-REQ-0009` | yes | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check | lesson preflight, LSN-0009 |
| `LESSON-REQ-0010` | yes | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable | lesson preflight, LSN-0010 |
| `LESSON-REQ-0011` | yes | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters | lesson preflight, LSN-0011 |
| `LESSON-REQ-0012` | yes | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them | lesson preflight, LSN-0012 |
| `LESSON-REQ-0013` | no | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup | lesson preflight, LSN-0013 |
| `LESSON-REQ-0014` | no | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run | lesson preflight, LSN-0014 |

## Evidence

### REQ-0001

Execute the cold start, reading the entry contract, the development contracts, the Master Plan, the SETUP-00 checklist, LATEST, and the complete CP-0004 and CP-0005 checkpoints, then validate and baseline before altering anything.

- Implementation: `checkpoint:COMMANDS.jsonl`
- Test: _none recorded_
- Documentation: `checkpoint:PLAN.md`
- Validation: `checkpoint:FILES.json`
- Notes: FILES.json filesRead records the sealed CP-0004 and CP-0005 checkpoints read before any change.

### REQ-0002

Create the engineering memory tree at .iacode/memory/ with README.md, LESSONS.md, lessons.jsonl, patterns/, anti-patterns/, incidents/, guardrails/, and retrospectives/.

- Implementation: `file:.iacode/memory/README.md`, `file:.iacode/memory/lessons.jsonl`, `file:.iacode/memory/LESSONS.md`
- Test: `test:EngineeringMemoryStructureTests.test_memory_tree_exists`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `command:cmd-0006`

### REQ-0003

State that the memory belongs to the IACode engineering organization and is not the user's personal memory.

- Implementation: `file:.iacode/memory/README.md`
- Test: `test:EngineeringMemoryStructureTests.test_memory_states_it_is_organizational_not_personal`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `command:cmd-0006`

### REQ-0004

Create .iacode/schemas/lesson.schema.json carrying every mandated lesson field, the five canonical statuses, training denied by default, and no chain-of-thought or secrets.

- Implementation: `file:.iacode/schemas/lesson.schema.json`
- Test: `test:LessonValidationTests.test_valid_lesson_passes`, `test:LessonValidationTests.test_missing_required_field_fails`, `test:EngineeringMemoryStructureTests.test_repository_lessons_deny_training_by_default`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `command:cmd-0008`

### REQ-0005

Support at least the sixteen mandated lesson categories.

- Implementation: `file:.iacode/schemas/lesson.schema.json`, `file:scripts/development-ledger/lessons.py`
- Test: `test:LessonValidationTests.test_invalid_lesson_fails`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `command:cmd-0008`

### REQ-0006

Implement the OBSERVED to CONFIRMED to GUARDED lifecycle, where GUARDED requires concrete preventive evidence such as a test, validator, lint rule, policy, schema, invariant, or automated check, and never documentation alone.

- Implementation: `file:scripts/development-ledger/lessons.py`
- Test: `test:LessonValidationTests.test_guarded_without_preventive_evidence_fails`, `test:LessonValidationTests.test_documentation_alone_does_not_guard_a_lesson`, `test:EngineeringMemoryStructureTests.test_every_guarded_lesson_names_a_real_control`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `command:cmd-0008`

### REQ-0007

Give every lesson a recurrence key, increment recurrenceCount on a repeat, and record a GUARDRAIL_FAILURE when a repeat happens against a GUARDED lesson.

- Implementation: `file:scripts/development-ledger/lessons.py`
- Test: `test:LessonRecurrenceTests.test_recurrence_increments_the_counter`, `test:LessonRecurrenceTests.test_a_repeat_against_a_guarded_lesson_is_a_guardrail_failure`, `test:LessonValidationTests.test_unresolved_guardrail_failure_cannot_stay_guarded`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `command:cmd-0006`

### REQ-0008

Provide a lesson extraction mechanism that consumes rework logs, review findings, Red Team findings, failures, and retrospectives, and produces candidates no stronger than OBSERVED.

- Implementation: `file:scripts/development-ledger/extract_lessons.py`
- Test: `test:LessonRecurrenceTests.test_recurrence_key_is_stable_for_a_failure_class`
- Documentation: `file:scripts/development-ledger/README.md`
- Validation: `command:cmd-0007`
- Notes: Candidates are never stronger than OBSERVED; promotion is a human judgement.

### REQ-0009

Provide a lesson validator checking schema, unique identifiers, valid status, provenance, training policy, evidence, preventive evidence for GUARDED, absence of secrets, and recurrence consistency, exiting zero only when valid.

- Implementation: `file:scripts/development-ledger/validate_lessons.py`, `file:scripts/development-ledger/lessons.py`
- Test: `test:LessonValidationTests.test_duplicate_lesson_id_fails`, `test:LessonValidationTests.test_secret_in_a_lesson_fails`, `test:LessonValidationTests.test_training_allowed_requires_a_rights_justification`, `test:LessonValidationTests.test_reused_recurrence_key_fails`
- Documentation: `file:scripts/development-ledger/README.md`
- Validation: `command:cmd-0008`

### REQ-0010

Provide a mandatory lesson preflight that takes gate, scope, technologies, and modules, and writes LESSON-PREFLIGHT.json and LESSON-PREFLIGHT.md naming each applicable lesson with its reason, required check, and required evidence.

- Implementation: `file:scripts/development-ledger/lesson_preflight.py`, `file:.iacode/schemas/lesson-preflight.schema.json`
- Test: `test:LessonPreflightTests.test_preflight_selects_an_applicable_lesson`, `test:LessonPreflightTests.test_preflight_ignores_a_lesson_declared_for_another_gate`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:LESSON-PREFLIGHT.json`, `checkpoint:LESSON-PREFLIGHT.md`

### REQ-0011

Turn applicable lessons into derived requirements in the Gate requirements matrix, so a lesson becomes a requirement, then evidence, then validation.

- Implementation: `file:scripts/development-ledger/delivery_assurance.py`, `checkpoint:REQUIREMENTS-MATRIX.json`
- Test: `test:DerivedRequirementCompletenessTests.test_a_missing_derived_requirement_blocks_completeness`, `test:DerivedRequirementCompletenessTests.test_a_declared_derived_requirement_passes`, `test:LessonPreflightTests.test_an_applicable_lesson_becomes_a_derived_requirement`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `checkpoint:COMPLETENESS-REPORT.json`

### REQ-0012

Populate the initial memory only from facts confirmed by the existing checkpoints, covering at least the twelve listed SETUP-00 lessons, each referencing historical evidence.

- Implementation: `file:.iacode/memory/lessons.jsonl`
- Test: `test:EngineeringMemoryStructureTests.test_repository_memory_is_valid`, `test:LessonPreflightTests.test_the_repository_preflight_covers_every_active_lesson`
- Documentation: `file:.iacode/memory/LESSONS.md`, `file:.iacode/memory/guardrails/README.md`
- Validation: `command:cmd-0008`
- Notes: Fourteen lessons, each citing a finding recorded in a sealed checkpoint. None was invented.

### REQ-0013

Document the principle that an important lesson must become an automated guardrail and that no control may depend on someone remembering to read LESSONS.md.

- Implementation: `file:.iacode/memory/README.md`
- Test: `test:EngineeringMemoryStructureTests.test_the_guardrail_principle_is_documented`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/adr/ADR-0009-engineering-memory-and-milestone-validation.md`
- Validation: `command:cmd-0006`

### REQ-0014

Require a retrospective for every completed Gate, provide its template, and record this checkpoint's own retrospective.

- Implementation: `file:.iacode/templates/retrospective/TEMPLATE.md`
- Test: _none recorded_
- Documentation: `file:.iacode/memory/retrospectives/SETUP-00-CP-0006.md`, `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `command:cmd-0009`

### REQ-0015

Make the Implementer, tests, Green Keeper, and Delivery Completeness Validator sequence mandatory for every delivery, and forbid advancing with red gates, coverage below total, any partial, or any missing requirement.

- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:DeliveryAssuranceGateTests.test_green_keeper_not_executed_blocks_review`, `test:DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`, `test:DeliveryLifecycleTests.test_full_delivery_assurance_flow_reaches_ready_for_review`
- Documentation: `file:docs/DEVELOPMENT-CONTRACT.md`, `file:docs/QUALITY-GATES.md`
- Validation: `command:cmd-0009`

### REQ-0016

Define the external validation cadence and the milestone grouping M0 through M6, and state that the auditor evaluates the milestone as a whole rather than only the last Gate.

- Implementation: `file:scripts/development-ledger/ledger_common.py`
- Test: `test:MilestoneValidationPolicyTests.test_milestone_grouping_matches_the_published_plan`, `test:MilestoneValidationPolicyTests.test_every_planned_gate_belongs_to_exactly_one_milestone`
- Documentation: `file:docs/MILESTONE-VALIDATION.md`, `file:docs/MASTER-PLAN.md`, `file:docs/ROADMAP.md`
- Validation: `command:cmd-0006`

### REQ-0017

Add externalAuditRequired and externalAuditReason so an extraordinary audit before a milestone is possible only with a recorded reason, and list the triggering categories.

- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`, `file:.iacode/schemas/checkpoint.schema.json`
- Test: `test:MemoryPolicyValidationTests.test_an_extraordinary_audit_requires_a_recorded_trigger`, `test:MemoryPolicyValidationTests.test_an_extraordinary_audit_reason_must_name_a_known_trigger`, `test:MemoryPolicyValidationTests.test_a_reason_without_a_request_is_rejected`
- Documentation: `file:docs/MILESTONE-VALIDATION.md`
- Validation: `command:cmd-0009`

### REQ-0018

Distinguish INTERNAL_GATE_PASS from MILESTONE_EXTERNAL_PASS so an internal verdict is never described as independent external validation.

- Implementation: `file:scripts/development-ledger/ledger_common.py`, `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:MemoryStatusVocabularyTests.test_internal_and_external_pass_are_distinct_statuses`, `test:MemoryPolicyValidationTests.test_an_internal_pass_may_not_carry_an_external_verdict`, `test:MemoryPolicyValidationTests.test_a_milestone_pass_requires_external_validation`
- Documentation: `file:docs/MILESTONE-VALIDATION.md`, `file:docs/QUALITY-GATES.md`
- Validation: `command:cmd-0009`

### REQ-0019

Define the milestone checkpoint that consolidates the included Gates, lessons, open risks, architecture changes, tests, regression, cross-gate integration, requirements completeness, outstanding debt, provenance, and model usage.

- Implementation: `file:.iacode/schemas/checkpoint.schema.json`
- Test: `test:MemoryPolicyValidationTests.test_a_wrong_milestone_grouping_fails`
- Documentation: `file:docs/MILESTONE-VALIDATION.md`, `file:docs/HANDOFF-PROTOCOL.md`
- Validation: `command:cmd-0009`

### REQ-0020

Record that Codex acts primarily as the milestone independent auditor and what it must validate.

- Implementation: `file:AGENTS.md`
- Test: _none recorded_
- Documentation: `file:docs/MILESTONE-VALIDATION.md`
- Validation: `command:cmd-0006`

### REQ-0021

Update the governing documents and add docs/ENGINEERING-MEMORY.md and docs/MILESTONE-VALIDATION.md.

- Implementation: `file:docs/ENGINEERING-MEMORY.md`, `file:docs/MILESTONE-VALIDATION.md`
- Test: `test:SetupChecklistTests.test_documentation_links_resolve`
- Documentation: `file:START-HERE.md`, `file:AGENTS.md`, `file:CLAUDE.md`, `file:docs/DEVELOPMENT-CONTRACT.md`, `file:docs/MASTER-PLAN.md`, `file:docs/ROADMAP.md`, `file:docs/QUALITY-GATES.md`, `file:docs/DEFINITION-OF-DONE.md`, `file:docs/CHECKPOINT-PROTOCOL.md`, `file:docs/HANDOFF-PROTOCOL.md`, `file:docs/SETUP-00-CHECKLIST.md`
- Validation: `command:cmd-0006`

### REQ-0022

Update the canonical agent contracts so the Engineering Lead runs the preflight, the Planner incorporates lesson requirements, the Implementer consults applicable checks, the Green Keeper records failures as lesson candidates, the Completeness Validator confirms lesson-derived requirements, the Historian records lessons, and the Reviewer looks for recurrence.

- Implementation: `file:.iacode/agents/engineering-lead.md`, `file:.iacode/agents/planner.md`, `file:.iacode/agents/implementer.md`, `file:.iacode/agents/test-rework-greenkeeper.md`, `file:.iacode/agents/delivery-completeness-validator.md`, `file:.iacode/agents/historian.md`, `file:.iacode/agents/reviewer.md`
- Test: `test:ClaudeAdapterTests.test_project_agents_match_canonical_role_names`, `test:ClaudeAdapterTests.test_project_agents_defer_to_canonical_contracts`
- Documentation: `file:docs/ENGINEERING-MEMORY.md`
- Validation: `command:cmd-0006`

### REQ-0023

Add the seventeen mandated tests for the lesson schema, lifecycle, recurrence, preflight, derived requirements, milestone grouping, audit policy, and historical compatibility.

- Implementation: `file:tests/test_development_ledger.py`
- Test: `test:LessonValidationTests.test_guarded_without_preventive_evidence_fails`, `test:LessonPreflightTests.test_preflight_ignores_a_retired_lesson`, `test:DerivedRequirementCompletenessTests.test_a_missing_derived_requirement_blocks_completeness`, `test:MilestoneValidationPolicyTests.test_an_intermediate_gate_does_not_require_external_validation`, `test:MilestoneValidationPolicyTests.test_a_milestone_closing_gate_requires_external_validation`, `test:HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`
- Documentation: `checkpoint:FINAL-REPORT.md`
- Validation: `command:cmd-0006`

### REQ-0024

Use the real Green Keeper on this checkpoint, repairing until green or declaring a real external blocker, and never reaching READY_FOR_REVIEW with anything red.

- Implementation: `checkpoint:REWORK-LOG.jsonl`
- Test: `test:GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`
- Documentation: `checkpoint:DECISIONS.md`
- Validation: `command:cmd-0006`, `command:cmd-0007`, `command:cmd-0008`, `command:cmd-0009`

### REQ-0025

Run the real Delivery Completeness Validator before handoff and reach total coverage with zero partial, zero missing, and total evidence coverage.

- Implementation: `checkpoint:COMPLETENESS-REPORT.json`
- Test: _none recorded_
- Documentation: `checkpoint:COMPLETENESS-REPORT.md`
- Validation: `checkpoint:COMPLETENESS-REPORT.json`

### REQ-0026

Close CP-0006 at READY_FOR_REVIEW rather than GATE_PASS, because SETUP-00 still needs the M0 milestone audit.

- Implementation: `checkpoint:STATE.json`
- Test: _none recorded_
- Documentation: `checkpoint:STATUS.md`, `checkpoint:DECISIONS.md`
- Validation: `command:cmd-0009`

### REQ-0027

Make NEXT.md request a single Codex M0 validation covering CP-0005, CP-0006, and SETUP-00 as a whole, rather than separate validations.

- Implementation: `checkpoint:NEXT.md`
- Test: _none recorded_
- Documentation: `checkpoint:NEXT.md`, `checkpoint:HANDOFF.md`
- Validation: `command:cmd-0009`

### REQ-0028

Respect every prohibition: no Gate 0, no modification of sealed checkpoints or historical tags, no chain-of-thought, no secrets, no automatic training eligibility, and no removal of the Green Keeper or completeness controls.

- Implementation: `checkpoint:STATE.json`
- Test: `test:HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`
- Documentation: `checkpoint:DECISIONS.md`
- Validation: `command:cmd-0009`

### REQ-0029

Deliver the final report with checkpoint, status, coverage, Green Keeper, completeness, tests, lessons created and guarded, preflight, milestone policy, historical compatibility, commit, tag, risks, and next action.

- Implementation: `checkpoint:FINAL-REPORT.md`
- Test: _none recorded_
- Documentation: `checkpoint:FINAL-REPORT.md`
- Validation: `command:cmd-0009`

### REQ-0030

Preserve backward compatibility: CP-0001 through CP-0005 must keep validating under the extended tooling, with their tags unchanged.

- Implementation: `file:scripts/development-ledger/validate_checkpoint.py`
- Test: `test:HistoricalCheckpointCompatibilityTests.test_second_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_third_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_fifth_sealed_checkpoint_still_validates`
- Documentation: `file:docs/CHECKPOINT-PROTOCOL.md`
- Validation: `command:cmd-0006`

### REQ-0031

Record the structural decisions of this checkpoint as an ADR, covering the engineering memory, the guardrail principle, and the milestone validation policy.

- Implementation: `file:docs/adr/ADR-0009-engineering-memory-and-milestone-validation.md`
- Test: _none recorded_
- Documentation: `file:docs/adr/ADR-0009-engineering-memory-and-milestone-validation.md`
- Validation: `test:SetupChecklistTests.test_documentation_links_resolve`

### REQ-0032

Maintain the Engineering Ledger continuously with requirement, plan, file, command, exit code, failure, cause, correction, retest, result, and evidence.

- Implementation: `checkpoint:COMMANDS.jsonl`
- Test: _none recorded_
- Documentation: `checkpoint:DECISIONS.md`
- Validation: `command:cmd-0009`

### REQ-0033

Keep trainingAllowed false by default for every new artifact and change no rights policy without evidence.

- Implementation: `checkpoint:PROVENANCE.json`, `file:.iacode/memory/lessons.jsonl`
- Test: `test:EngineeringMemoryStructureTests.test_repository_lessons_deny_training_by_default`
- Documentation: `file:.iacode/policies/provenance-policy.md`
- Validation: `command:cmd-0008`

### LESSON-REQ-0001

Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0002

Verify a file inventory must be recomputed from the repository, never trusted as an assertion

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:DeltaInventoryTests.test_removed_manifest_entry_fails`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0003

Verify every operation attempt must be auditable, including a refusal decided before execution

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0004

Verify a checkpoint may never claim readiness while it also claims to be blocked

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`, `test:MemoryStatusVocabularyTests.test_neither_pass_status_may_carry_a_blocker`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0005

Verify a PASS requires evidence that can be executed or resolved, not a statement

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:QualityEvidenceTests.test_pass_without_evidence_fails`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0006

Verify the repository must be self-contained; a specification may not live outside it

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:SetupChecklistTests.test_checklist_exists_and_is_referenced`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0007

Verify independent validation cannot be declared by the run that did the work

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:MemoryPolicyValidationTests.test_an_internal_pass_may_not_carry_an_external_verdict`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0008

Verify requirement completeness must be total and evidence-backed before handoff

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:DerivedRequirementCompletenessTests.test_a_missing_derived_requirement_blocks_completeness`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0009

Verify a red gate requires rework, never a waiver, and never a weakened check

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0010

Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:CommandReproducibilityTests.test_bare_script_name_is_rejected`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0011

Verify a control over a checkpoint's own evidence must be scoped to the moment it matters

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0012

Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: `test:HistoricalCheckpointCompatibilityTests.test_fifth_sealed_checkpoint_still_validates`
- Documentation: `file:.iacode/memory/LESSONS.md`
- Validation: `command:cmd-0006`

### LESSON-REQ-0013

Verify an installed capability must be detected by resolved path, not by a bare command lookup

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: _none recorded_
- Documentation: `file:docs/TOOL-CAPABILITIES.md`
- Validation: `command:cmd-0009`
- Notes: This Gate records no new capability detection; the existing record in docs/TOOL-CAPABILITIES.md names the resolved executable path and the PATH caveat, and nothing was concluded about availability from a bare lookup.

### LESSON-REQ-0014

Verify evidence must be recorded as it happens, not reconstructed at the end of a run

- Implementation: `checkpoint:LESSON-PREFLIGHT.json`
- Test: _none recorded_
- Documentation: `file:scripts/development-ledger/record_command.py`
- Validation: `command:cmd-0009`
- Notes: Every command of this delivery was recorded by the tooling as it ran; no ledger entry was reconstructed afterwards.
