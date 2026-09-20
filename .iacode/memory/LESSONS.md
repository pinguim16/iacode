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
| `LSN-0005` | `GUARDED` | HIGH | quality | A PASS requires evidence that can be executed or resolved, not a statement | `QualityEvidenceTests.test_pass_without_evidence_fails`, `QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`, `scripts/development-ledger/validate_checkpoint.py` |
| `LSN-0006` | `GUARDED` | MEDIUM | documentation | The repository must be self-contained; a specification may not live outside it | `SetupChecklistTests.test_checklist_exists_and_is_referenced`, `SetupChecklistTests.test_documentation_links_resolve` |
| `LSN-0007` | `GUARDED` | CRITICAL | process | Independent validation cannot be declared by the run that did the work | `SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass`, `DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review`, `.iacode/schemas/checkpoint.schema.json` |
| `LSN-0008` | `GUARDED` | HIGH | process | Requirement completeness must be total and evidence-backed before handoff | `DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`, `scripts/development-ledger/check_completeness.py` |
| `LSN-0009` | `GUARDED` | HIGH | testing | A red gate requires rework, never a waiver, and never a weakened check | `GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `DeliveryAssuranceGateTests.test_red_tests_block_review` |
| `LSN-0010` | `GUARDED` | MEDIUM | tooling | A recorded command must carry runtime, working directory, commit and purpose to be replayable | `CommandReproducibilityTests.test_bare_script_name_is_rejected`, `CommandReproducibilityTests.test_unresolvable_script_path_is_rejected`, `.iacode/schemas/command.schema.json` |
| `LSN-0011` | `GUARDED` | MEDIUM | tooling | A control over a checkpoint's own evidence must be scoped to the moment it matters | `DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`, `green_keeper._refresh_declared_hashes` |
| `LSN-0012` | `GUARDED` | HIGH | git | Sealed checkpoints and their tags are immutable, and tooling must keep validating them | `HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`, `docs/CHECKPOINT-PROTOCOL.md` |
| `LSN-0013` | `CONFIRMED` | MEDIUM | environment | An installed capability must be detected by resolved path, not by a bare command lookup | _not yet guarded_ |
| `LSN-0014` | `CONFIRMED` | MEDIUM | process | Evidence must be recorded as it happens, not reconstructed at the end of a run | `scripts/development-ledger/record_command.py` |

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
- Source: SETUP-00, SETUP-00-CP-0004, finding R3.1 / RT-02.
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

- Status: `GUARDED`, severity HIGH, category quality, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0003, finding R6.
- Symptom: A quality dimension was recorded as PASS in a checkpoint that contained no corresponding execution.
- Root cause: Quality results were bare verdicts with no link to the run that produced them, so a verdict could be inherited from an earlier checkpoint without re-execution.
- Resolution: Every dimension records status, evidence and justification, and a PASS needs at least one reference that resolves to a successful command record or a non-empty file.
- Prevention:
  - `test` QualityEvidenceTests.test_pass_without_evidence_fails — A PASS with no evidence is rejected.
  - `test` QualityEvidenceTests.test_pass_referencing_a_failed_command_fails — A PASS pointing at a failed command is rejected.
  - `validator` scripts/development-ledger/validate_checkpoint.py — _validate_quality_evidence resolves every reference.
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

- Status: `GUARDED`, severity CRITICAL, category process, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0003, finding R4 / R7.
- Symptom: The implementing run produced its own review and Red Team reports and the earlier checkpoint reached GATE_PASS on that basis.
- Root cause: Cross-tool validation was a sentence in a document rather than structured state, so nothing prevented an implementer from certifying itself.
- Resolution: secondToolValidation is structured state, GATE_PASS requires it to be PASSED or a justified NOT_REQUIRED, and READY_FOR_REVIEW requires independentReview and redTeam to still be PENDING.
- Prevention:
  - `test` SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass — A failed cross-tool validation cannot promote a Gate.
  - `test` DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review — An implementing run cannot record its own independent verdict.
  - `schema` .iacode/schemas/checkpoint.schema.json — The cross-tool and independent verdict states are enumerated, not free text.
- Evidence: `file:docs/adr/ADR-0007-checkpoint-schema-2-and-independent-promotion.md`, `file:docs/checkpoints/SETUP-00-CP-0004/DECISIONS.md`

### LSN-0008 — Requirement completeness must be total and evidence-backed before handoff

- Status: `GUARDED`, severity HIGH, category process, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0005, finding prompt sections 9 and 10.
- Symptom: The independent tool was spending its effort discovering unimplemented requirements and missing evidence rather than auditing design.
- Root cause: No artifact held the complete requirement set, so completeness was a judgement made from memory of the conversation.
- Resolution: Requirements are extracted into REQUIREMENTS-MATRIX.json before implementation and audited by a validator that resolves every evidence reference and refuses anything short of total coverage.
- Prevention:
  - `test` DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails — Coverage below total fails the audit.
  - `test` DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review — An unexecuted completeness audit blocks readiness.
  - `validator` scripts/development-ledger/check_completeness.py — The audit recomputes coverage and resolves every evidence reference.
- Evidence: `file:docs/adr/ADR-0008-delivery-assurance-gates.md`, `file:docs/checkpoints/SETUP-00-CP-0005/COMPLETENESS-REPORT.md`

### LSN-0009 — A red gate requires rework, never a waiver, and never a weakened check

- Status: `GUARDED`, severity HIGH, category testing, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0005, finding prompt section 8.
- Symptom: Nothing structurally prevented a delivery from being offered while a mandatory gate was red.
- Root cause: Greenness was a habit rather than a recorded, verified state, and no artifact tied a failure to the repair that resolved it.
- Resolution: The Green Keeper runs the mandatory gates, records every cycle with its root cause in REWORK-LOG.jsonl, and GREEN_KEEPER_GATE is PASS only when nothing is red and no rework item is unresolved.
- Prevention:
  - `test` GreenKeeperToolTests.test_red_gate_is_reported_as_still_red — A red gate is reported as still red and exits nonzero.
  - `test` DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected — A PASS that contradicts the last cycle is rejected.
  - `test` DeliveryAssuranceGateTests.test_red_tests_block_review — A failing quality dimension blocks readiness.
- Evidence: `file:.iacode/agents/test-rework-greenkeeper.md`, `file:docs/checkpoints/SETUP-00-CP-0005/REWORK-LOG.jsonl`

### LSN-0010 — A recorded command must carry runtime, working directory, commit and purpose to be replayable

- Status: `GUARDED`, severity MEDIUM, category tooling, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0004, finding R3.2.
- Symptom: Recorded finalizer commands named a bare script that does not exist in the working directory they declared, so the ledger could not be replayed.
- Root cause: The record stored a convenient label rather than the literal invocation, and nothing checked that the label could be executed.
- Resolution: Records carry runtime, working directory, sanitized arguments, referenced inputs, repository commit, purpose and a canonical result, and validation rejects a command that does not start with an explicit runtime or whose script path does not resolve.
- Prevention:
  - `test` CommandReproducibilityTests.test_bare_script_name_is_rejected — A bare script name is rejected.
  - `test` CommandReproducibilityTests.test_unresolvable_script_path_is_rejected — A script path that does not resolve is rejected.
  - `schema` .iacode/schemas/command.schema.json — The reproducibility fields are part of the record contract.
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

- Status: `GUARDED`, severity HIGH, category git, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0002, finding checkpoint protocol.
- Symptom: Every correction cycle created pressure to edit or retag an earlier checkpoint so the new rules would fit it.
- Root cause: Control-plane rules evolve while history does not, so without version dispatch a new rule silently invalidates sealed evidence.
- Resolution: Checkpoints declare a schema version, validation applies the rules of the declared version, and a regression validates clean clones detached at every sealed tag.
- Prevention:
  - `test` HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates — The first sealed checkpoint still validates.
  - `test` HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates — The most recent sealed review checkpoint still validates.
  - `policy` docs/CHECKPOINT-PROTOCOL.md — Schema versions and immutability are stated in the protocol.
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

- Status: `CONFIRMED`, severity MEDIUM, category process, recurrences 0.
- Source: SETUP-00, SETUP-00-CP-0003, finding ledger backfill.
- Symptom: Part of a command ledger was written after the fact because the recorder was introduced mid-run, so timestamps were recording times rather than execution times.
- Root cause: The ledger was treated as a report produced at the end instead of an instrument used during the work.
- Resolution: Commands are recorded through the tooling as they run, and any record written after the fact states that its timestamp is a recording time.
- Prevention:
  - `automated-check` scripts/development-ledger/record_command.py — Recording a command captures its real timing and repository state at execution.
- Evidence: `file:docs/checkpoints/SETUP-00-CP-0003/DECISIONS.md`, `file:scripts/development-ledger/record_command.py`
