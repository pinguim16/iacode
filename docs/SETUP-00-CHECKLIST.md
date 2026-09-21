# SETUP-00 Checklist

This checklist is the in-repository specification of the SETUP-00 Development Control Plane.
It replaces the external prompt that originally described the Gate, so the repository remains the
only source of truth. `docs/MASTER-PLAN.md` accepts SETUP-00 against this document.

A row is satisfied only when the named artifact exists in the repository and the stated evidence is
observable. An unexecuted check is `NOT_EXECUTED`, never `PASS`.

## 1. Entry contract and tool adapters

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 1.1 | A single entry point states the phase, current Gate, latest checkpoint, and start protocol. | `START-HERE.md` | File present and consistent with `docs/checkpoints/LATEST.md`. |
| 1.2 | A Codex adapter binds the canonical contracts without adding independent policy. | `AGENTS.md` | File present; references `.iacode/`. |
| 1.3 | A Claude Code adapter binds the same contracts. | `CLAUDE.md` | File present; references `.iacode/agents/` and the checkpoint protocol. |
| 1.4 | Tool adapters stay semantically equivalent to the canonical roles. | `.claude/agents/*.md` | `ClaudeAdapterTests` in `tests/test_development_ledger.py`. |

## 2. Governing documents

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 2.1 | The Gate sequence, dependencies, acceptance, and fail conditions are recorded. | `docs/MASTER-PLAN.md` | File present; SETUP-00 accepts against this checklist. |
| 2.2 | The completion standard, mandatory controls, and Git and evidence discipline are recorded. | `docs/DEVELOPMENT-CONTRACT.md` | File present. |
| 2.3 | Tool-to-tool transfer is formal in both directions. | `docs/HANDOFF-PROTOCOL.md` | File present; receiver sequence is executable. |
| 2.4 | Checkpoint statuses, required events, required contents, commit semantics, and divergence handling are defined. | `docs/CHECKPOINT-PROTOCOL.md` | File present; enforced by `validate_checkpoint.py`. |
| 2.5 | Done is defined and excludes assertion-only PASS. | `docs/DEFINITION-OF-DONE.md` | File present. |
| 2.6 | Quality outcomes, required dimensions, and the promotion rule are defined. | `docs/QUALITY-GATES.md` | File present; enforced by the validator. |
| 2.7 | Structural decisions are recorded as ADRs. | `docs/adr/ADR-*.md` | At least one ADR per structural decision of this Gate. |
| 2.8 | Architecture, roadmap, provenance, model usage, and detected tool capabilities are documented. | `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/PROVENANCE.md`, `docs/MODEL-USAGE-POLICY.md`, `docs/TOOL-CAPABILITIES.md` | Files present and consistent with observed evidence. |

## 3. Canonical roles and policies

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 3.1 | The canonical, tool-neutral role contracts exist, one per role of the delivery protocol. | `.iacode/agents/` | `test_project_agents_match_canonical_role_names`. |
| 3.2 | Documentation, provenance, secret, tool-execution, and training-data policies exist. | `.iacode/policies/` | Files present; secret policy matches the implemented detector scope. |
| 3.3 | Reusable templates exist for ADRs, checkpoints, gate reports, and handoffs. | `.iacode/templates/` | Files present. |

## 4. Schemas

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 4.1 | Checkpoint state, run metadata, command, test, quality, provenance, and decision schemas exist and are loadable. | `.iacode/schemas/` | `test_all_required_schemas_are_loaded`. |
| 4.2 | An experience schema is reserved for Gate 6 and implements no runtime. | `.iacode/schemas/experience.schema.json` | File present; no runtime consumer exists. |
| 4.3 | Schema evolution is versioned and never invalidates a sealed checkpoint. | `.iacode/schemas/*.json` | `HistoricalCheckpointCompatibilityTests`. |

## 5. Ledger tooling

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 5.1 | A checkpoint can be created with truthful non-PASS defaults. | `scripts/development-ledger/new_checkpoint.py` | `test_new_finalize_commit_validate`. |
| 5.2 | A checkpoint can be finalized, and every finalization attempt is recorded with its exit code. | `scripts/development-ledger/finalize_checkpoint.py` | `FinalizationLedgerTests`. |
| 5.3 | A checkpoint is validated against schemas, Git state, inventory, quality evidence, and secrets. | `scripts/development-ledger/validate_checkpoint.py` | `CHECKPOINT_VALID` plus the validation test classes. |
| 5.4 | Secret redaction is available and documented to its real scope. | `scripts/development-ledger/redact_secrets.py`, `.iacode/policies/secret-policy.md` | Redactor tests; documented residual limits. |
| 5.5 | The tooling is standard-library only and portable across Windows and Unix-like checkouts. | `scripts/development-ledger/README.md` | Suite passes without third-party packages; `.gitattributes` normalizes line endings. |

## 6. Engineering Ledger

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 6.1 | Every checkpoint carries status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. | `docs/checkpoints/<id>/` | Required-file validation. |
| 6.2 | `LATEST.md` points textually to the last checkpoint accepted by validation. | `docs/checkpoints/LATEST.md` | `resolve_latest` plus `test_latest_to_nonexistent_checkpoint_fails`. |
| 6.3 | The file inventory matches the real change set, with bound content hashes. | `FILES.json` | `DeltaInventoryTests`. |
| 6.4 | Provenance is complete and `trainingAllowed` defaults to `false`. | `PROVENANCE.json` | Schema validation plus `.iacode/policies/provenance-policy.md`. |
| 6.5 | A quality `PASS` carries resolvable evidence. | `QUALITY.json` | `QualityEvidenceTests`. |
| 6.6 | Handoff-ready and terminal checkpoints are anchored to an immutable namespaced tag. | `STATE.json` | `test_handoff_ready_status_requires_commit_anchor`. |

## 7. Continuation and validation

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7.1 | A cold-start continuation prompt exists and depends only on checked-in files. | `prompts/RESUME-WORK.md` | Executed from a clean clone. |
| 7.2 | Cold-start validation is executed and recorded truthfully, including a blocked attempt. | `RESUME-VALIDATION.md` of the current checkpoint | Recorded result; a blocked attempt is never a PASS. |
| 7.3 | Cross-tool validation state is structured and explicit. | `STATE.json` `secondToolValidation` | `SecondToolValidationTests`. |
| 7.4 | A sealed checkpoint can be validated from a detached checkout of its own tag. | `validate_checkpoint.py` | `DetachedHeadValidationTests`. |
| 7.5 | The handoff is executable by another tool without the producing session. | `HANDOFF.md` | Required headings plus reproducible validation commands. |

## 7b. Delivery assurance

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7b.1 | Every requirement of a delivery exists in a versioned matrix before implementation. | `REQUIREMENTS-MATRIX.json`, `.iacode/schemas/requirements-matrix.schema.json` | `DeliveryCompletenessMatrixTests`. |
| 7b.2 | A Test Rework / Green Keeper role forbids shipping anything red and records every cycle. | `.iacode/agents/test-rework-greenkeeper.md`, `REWORK-LOG.jsonl`, `scripts/development-ledger/green_keeper.py` | `GreenKeeperToolTests`. |
| 7b.3 | A Delivery Completeness Validator audits the matrix before handoff and may not implement. | `.iacode/agents/delivery-completeness-validator.md`, `COMPLETENESS-REPORT.json`, `scripts/development-ledger/check_completeness.py` | `DeliveryCompletenessMatrixTests`, `DeliveryAssuranceGateTests`. |
| 7b.4 | `GREEN_KEEPER_GATE` and `DELIVERY_COMPLETENESS_GATE` are preconditions of `READY_FOR_REVIEW`. | `scripts/development-ledger/validate_checkpoint.py`, `docs/QUALITY-GATES.md` | `DeliveryAssuranceGateTests`, `DeliveryLifecycleTests`. |
| 7b.5 | Readiness and blockage can never be claimed together. | `validate_checkpoint.py` | `StatusBlockerInvariantTests`, `ResealedBlockerFixtureTests`. |
| 7b.6 | Every operation attempt is recorded, including a refusal decided before execution. | `scripts/development-ledger/finalize_checkpoint.py` | `FinalizationAttemptRecordingTests`. |
| 7b.7 | Every recorded command is reproducible from its declared working directory. | `scripts/development-ledger/record_command.py`, `.iacode/schemas/command.schema.json` | `CommandReproducibilityTests`. |
| 7b.8 | The mandatory delivery order is stated in full in every governing document and both adapters. | `docs/DEVELOPMENT-CONTRACT.md`, `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`, `docs/DEFINITION-OF-DONE.md`, `START-HERE.md`, `AGENTS.md`, `CLAUDE.md` | Documents present and consistent. |

## 7c. Engineering memory and milestone validation

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7c.1 | The project keeps an organizational engineering memory of confirmed failures. | `.iacode/memory/`, `.iacode/schemas/lesson.schema.json` | `EngineeringMemoryStructureTests`. |
| 7c.2 | A lesson is `GUARDED` only when an automated control prevents recurrence. | `scripts/development-ledger/validate_lessons.py` | `LessonValidationTests`. |
| 7c.3 | A repeat increments recurrence, and a repeat against a guardrail is a `GUARDRAIL_FAILURE`. | `scripts/development-ledger/lessons.py` | `LessonRecurrenceTests`. |
| 7c.4 | A mandatory preflight selects the lessons that constrain each Gate. | `scripts/development-ledger/lesson_preflight.py`, `LESSON-PREFLIGHT.json` | `LessonPreflightTests`. |
| 7c.5 | Applicable lessons become requirements whose absence blocks completeness. | `REQUIREMENTS-MATRIX.json`, `check_completeness.py` | `DerivedRequirementCompletenessTests`. |
| 7c.6 | Lesson candidates can be extracted from recorded delivery evidence, never above `OBSERVED`. | `scripts/development-ledger/extract_lessons.py` | Candidates recorded in this checkpoint's evidence. |
| 7c.7 | External validation is grouped into milestones `M0` to `M6`. | `docs/MILESTONE-VALIDATION.md`, `ledger_common.MILESTONES` | `MilestoneValidationPolicyTests`. |
| 7c.8 | An internal verdict is never described as independent external validation. | `INTERNAL_GATE_PASS`, `MILESTONE_EXTERNAL_PASS` | `MemoryStatusVocabularyTests`, `MemoryPolicyValidationTests`. |
| 7c.9 | An extraordinary audit requires a recorded trigger. | `externalAuditRequired`, `externalAuditReason` | `MemoryPolicyValidationTests`. |
| 7c.10 | Every completed Gate produces a retrospective. | `.iacode/templates/retrospective/TEMPLATE.md`, `.iacode/memory/retrospectives/` | Retrospective present for this Gate. |

## 7d. Milestone closure controls

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7d.1 | One promotion invariant governs every positive terminal status, not only `READY_FOR_REVIEW`. | `scripts/development-ledger/validate_checkpoint.py` | `PromotionInvariantTests`. |
| 7d.2 | The mandatory quality gate set is a closed machine-readable registry that an invocation cannot narrow. | `.iacode/policies/quality-gates.json`, `scripts/development-ledger/green_keeper.py` | `MandatoryGatePolicyTests`. |
| 7d.3 | The expected requirement set is derived from canonical sources and compared exactly with the declared set. | `.iacode/policies/canonical-requirements.json`, `scripts/development-ledger/policies.py` | `ExpectedRequirementSetTests`. |
| 7d.4 | An external milestone PASS is derived from an audit attestation authored by another sealed checkpoint. | `.iacode/attestations/`, `scripts/development-ledger/attestation.py` | `ExternalAttestationTests`. |
| 7d.5 | A derived artifact carries a fingerprint of its inputs, and staleness is decided by recomputation. | `scripts/development-ledger/lesson_preflight.py`, `LESSON-PREFLIGHT.json` | `PreflightFreshnessTests`. |
| 7d.6 | Every lesson control, evidence path and provenance locator is resolved against the repository. | `scripts/development-ledger/lessons.py` | `LessonResolutionTests`, `LessonProvenanceTests`. |
| 7d.7 | Every `GUARDED` lesson names a registered guardrail, and guardrail effectiveness is measured. | `.iacode/memory/guardrails/registry.json` | `GuardrailRegistryTests`, `GuardrailEffectivenessGateTests`. |
| 7d.8 | Sealed checkpoints are anchored by a hash-linked chain over tag, commit and tree. | `.iacode/anchors/checkpoint-chain.json`, `scripts/development-ledger/anchors.py` | `IntegrityAnchorTests`. |
| 7d.9 | Every count used as evidence is derived once and verified wherever a report states it. | `COUNTS.json`, `scripts/development-ledger/derive_counts.py` | `DerivedCountTests`. |
| 7d.10 | Sealing is monotonic and post-commit, and every recorded command binds its declared inputs by content. | `scripts/development-ledger/seal_checkpoint.py`, `record_command.py` | `SealChronologyTests`, `CommandInputBindingTests`. |
| 7d.11 | A milestone delivery carries an internal Red Team and an internal mirror audit, and neither is recorded as external validation. | `scripts/development-ledger/m0_red_team.py`, `m0_mirror_audit.py`, `.iacode/agents/m0-closure-auditor.md` | `InternalAssuranceTests`, `AuditSourceParsingTests`. |
| 7d.12 | Every finding of an independent audit is closed before the corrective delivery is offered. | `.iacode/policies/audit-registry.json`, `CP7-FINDINGS-CLOSURE.json` | `FindingsClosureTests`. |
| 7d.13 | A milestone verdict is carried by the audit checkpoint about a sealed subject, and its positive path is executed rather than only its refusals. | `scripts/development-ledger/attestation.py`, `milestone_status.py`, `promotion_simulation.py` | `AuditAttestationModelTests`, `PositivePromotionTests`. |
| 7d.14 | A generic guardrail derives repository state instead of naming a historical checkpoint, and the protocol's own next steps keep every mandatory gate green. | `scripts/development-ledger/anchors.py`, `successor_durability.py` | `SuccessorDurabilityTests`, `IntegrityAnchorTests`. |
| 7d.15 | Every adversarial battery records a null-mutation control, and no count used as evidence is stated in prose. | `scripts/development-ledger/m0_red_team.py`, `.iacode/schemas/red-team-report.schema.json`, `docs/QUALITY-GATES.md` | `InternalAssuranceTests`, `SourceCardinalityPolicyTests`, `DerivedTestCountTests`. |
| 7d.16 | An audit control tells an empty applicable set from a missing required set, justifies every `NOT_APPLICABLE` against a canonical derivation no delivery can shrink, and a simulation that claims a control passed executes that control instead of writing its artifact. | `scripts/development-ledger/m0_mirror_audit.py`, `mirror_semantics_validation.py`, `gate_transition_simulation.py`, `.iacode/schemas/mirror-audit.schema.json` | `MirrorApplicabilitySemanticsTests`, `GateTransitionSimulationTests`, `SimulationExecutesProductionControlsTests`. |

## 8. Independent verification

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 8.1 | An independent review is recorded. | `REVIEW-REPORT.md` | `APPROVED` or `REWORK_REQUIRED` with evidence. |
| 8.2 | An adversarial Red Team is recorded. | `RED-TEAM-REPORT.md` | `RED_TEAM_PASS` or `RED_TEAM_FAIL` with reproducible attacks. |
| 8.3 | `GATE_PASS` is granted only by a run independent of the implementer. | `STATE.json`, `docs/QUALITY-GATES.md` | The implementing run closes at `READY_FOR_REVIEW`; the validator refuses `GATE_PASS` without a passed or explicitly waived cross-tool validation. |

## 9. Scope control

| # | Requirement | Artifact | Evidence |
|---|---|---|---|
| 9.1 | No Gate 0 or later runtime is implemented during SETUP-00. | repository tree | No model gateway, agent runtime, sandbox, quality runtime, or IDE integration exists. |
| 9.2 | Documentation is maintained continuously rather than reconstructed at the end. | `COMMANDS.jsonl`, `DECISIONS.md` | Chronological records inside the checkpoint. |
| 9.3 | No secret, credential, or private chain-of-thought is stored. | whole repository | Validator secret scan over every readable file. |
| 9.4 | Gate advancement requires explicit authorization and a passing previous Gate. | `docs/MASTER-PLAN.md`, `NEXT.md` | Next action never points directly at Gate 0 without authorization. |
