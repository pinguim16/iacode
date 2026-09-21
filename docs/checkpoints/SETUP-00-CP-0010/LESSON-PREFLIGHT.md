# Lesson Preflight

- Gate: `SETUP-00`
- Scope: `corrective delivery closing the CP-0009 audit findings`
- Technologies: _none declared_
- Modules: _none declared_
- Generated: `2026-09-21T04:57:38Z`
- Lessons considered: 30
- Lessons applicable: 29

Every applicable lesson below is a requirement of this Gate. The derived identifiers must
appear in `REQUIREMENTS-MATRIX.json`, and the Delivery Completeness Validator fails the
delivery when one is absent.

| Lesson | Status | Severity | Derived requirement | Required check |
|---|---|---|---|---|
| `LSN-0001` Checkpoint validation must succeed from a detached checkout of the checkpoint tag | `GUARDED` | HIGH | `LESSON-REQ-0001` | Validate the checkpoint from a clean clone detached at its own tag, not only on the branch. |
| `LSN-0002` A file inventory must be recomputed from the repository, never trusted as an assertion | `GUARDED` | HIGH | `LESSON-REQ-0002` | Declare every changed path with a reason before finalizing and let the tooling bind the hashes. |
| `LSN-0003` Every operation attempt must be auditable, including a refusal decided before execution | `GUARDED` | HIGH | `LESSON-REQ-0003` | Confirm that a refused operation appends its attempt to the ledger before returning an error. |
| `LSN-0004` A checkpoint may never claim readiness while it also claims to be blocked | `GUARDED` | CRITICAL | `LESSON-REQ-0004` | Verify that the checkpoint carries no blocker while it claims to be ready for review. |
| `LSN-0005` A PASS requires evidence that can be executed or resolved, not a statement | `GUARDED` | CRITICAL | `LESSON-REQ-0005` | Attach a resolvable evidence reference to every PASS recorded by this Gate. |
| `LSN-0006` The repository must be self-contained; a specification may not live outside it | `GUARDED` | MEDIUM | `LESSON-REQ-0006` | Confirm that every specification this Gate depends on is committed to the repository. |
| `LSN-0007` Independent validation cannot be declared by the run that did the work | `GUARDED` | CRITICAL | `LESSON-REQ-0007` | Close the implementing run at an internal status and leave the independent verdict pending. |
| `LSN-0008` Requirement completeness must be total and evidence-backed before handoff | `GUARDED` | CRITICAL | `LESSON-REQ-0008` | Extract every requirement before implementing and audit completeness before handoff. |
| `LSN-0009` A red gate requires rework, never a waiver, and never a weakened check | `GUARDED` | CRITICAL | `LESSON-REQ-0009` | Run the Green Keeper until every mandatory gate is green, repairing causes rather than checks. |
| `LSN-0010` A recorded command must carry runtime, working directory, commit and purpose to be replayable | `GUARDED` | HIGH | `LESSON-REQ-0010` | Record commands with the tooling so each one is executable from its declared working directory. |
| `LSN-0011` A control over a checkpoint's own evidence must be scoped to the moment it matters | `GUARDED` | MEDIUM | `LESSON-REQ-0011` | Check whether any new control would be invalidated by the evidence its own run produces. |
| `LSN-0012` Sealed checkpoints and their tags are immutable, and tooling must keep validating them | `GUARDED` | CRITICAL | `LESSON-REQ-0012` | Confirm that every sealed checkpoint still validates under the tooling this Gate changes. |
| `LSN-0013` An installed capability must be detected by resolved path, not by a bare command lookup | `CONFIRMED` | MEDIUM | `LESSON-REQ-0013` | When this Gate records a capability, resolve the executable path before concluding anything about availability. |
| `LSN-0014` Evidence must be recorded as it happens, not reconstructed at the end of a run | `GUARDED` | MEDIUM | `LESSON-REQ-0014` | Record each command through the tooling while the work happens. |
| `LSN-0015` Every positive terminal status needs one shared promotion invariant | `GUARDED` | CRITICAL | `LESSON-REQ-0015` | Confirm that every positive terminal status this Gate can produce is covered by the shared promotion invariant, not only the status this delivery ends at. |
| `LSN-0016` A mandatory set must be closed by policy, never chosen by the caller | `GUARDED` | CRITICAL | `LESSON-REQ-0016` | Confirm that every control whose scope could be narrowed by an argument derives that scope from policy instead. |
| `LSN-0017` A completeness denominator must come from a source the delivery does not own | `GUARDED` | CRITICAL | `LESSON-REQ-0017` | Confirm that the expected requirement set is derived independently and compared as a set, not only as a count. |
| `LSN-0018` A structured reference must be resolved, not merely well typed | `GUARDED` | CRITICAL | `LESSON-REQ-0018` | Confirm that every reference this Gate records is resolved by a tool, not accepted as a string. |
| `LSN-0019` A derived artifact must carry a fingerprint of the inputs that produced it | `GUARDED` | HIGH | `LESSON-REQ-0019` | Confirm that every derived artifact this Gate stores can be recomputed and is recomputed during validation. |
| `LSN-0020` Evidence produced from a dirty tree needs immutable input identity | `GUARDED` | HIGH | `LESSON-REQ-0020` | Confirm that every recorded command binds its inputs by content and that no timestamp in the ledger is later than the recorded end of the run. |
| `LSN-0021` Sealed history needs an anchor outside the content it describes | `GUARDED` | CRITICAL | `LESSON-REQ-0021` | Confirm that the integrity chain still resolves for every sealed checkpoint and that this Gate anchors every sealed predecessor. |
| `LSN-0022` An authoritative count must be derived once, never maintained by hand twice | `GUARDED` | CRITICAL | `LESSON-REQ-0022` | Confirm that every count used as evidence in this Gate is derived from one source and verified where it is quoted. |
| `LSN-0023` A lesson must cite a source that actually records the finding it claims | `GUARDED` | MEDIUM | `LESSON-REQ-0023` | Confirm that every lesson this Gate writes or updates cites a checkpoint that records the finding identifier it names. |
| `LSN-0024` A control is finished only when its positive path has been executed, not only its refusals | `GUARDED` | CRITICAL | `LESSON-REQ-0024` | For every control this Gate adds or changes that gates a status, execute the path that reaches the status, not only the paths that are refused. |
| `LSN-0025` A generic guardrail derives repository state instead of naming today's checkpoint | `GUARDED` | CRITICAL | `LESSON-REQ-0025` | Confirm that no generic guard, test or policy in this Gate names a historical checkpoint to decide behaviour, and that any such rule is derived from repository state. |
| `LSN-0026` An adversarial battery without a null-mutation control proves nothing | `GUARDED` | HIGH | `LESSON-REQ-0026` | Run every adversarial battery of this Gate with an unmutated control through the same path, and record its result with the battery. |
| `LSN-0027` A lesson's prose may record a residual limit but may never contradict its status | `GUARDED` | MEDIUM | `LESSON-REQ-0027` | Confirm that every lesson this Gate writes or updates describes limits rather than restating its own status. |
| `LSN-0028` A configuration key that no code reads is a defect, not documentation | `GUARDED` | MEDIUM | `LESSON-REQ-0028` | Confirm that every configuration key this Gate declares is read by the implementation, or remove it and document the fixed behaviour. |
| `LSN-0029` A required protocol transition must never turn a mandatory gate red | `GUARDED` | CRITICAL | `LESSON-REQ-0029` | Before handoff, execute the protocol transitions this Gate's successor will perform and confirm the mandatory gates stay green. |

## Why each lesson applies

### LSN-0001 — Checkpoint validation must succeed from a detached checkout of the checkpoint tag

- Reason: applies to every Gate; category checkpoint; severity HIGH; already guarded, so the control must keep holding
- Required check: Validate the checkpoint from a clean clone detached at its own tag, not only on the branch.
- Required evidence: A recorded validate_checkpoint.py run from a detached checkout returning CHECKPOINT_VALID.
- Derived requirement: `LESSON-REQ-0001`

### LSN-0002 — A file inventory must be recomputed from the repository, never trusted as an assertion

- Reason: applies to every Gate; category checkpoint; severity HIGH; already guarded, so the control must keep holding
- Required check: Declare every changed path with a reason before finalizing and let the tooling bind the hashes.
- Required evidence: A FILES.json whose declared change set matches the recomputed one, proven by a passing validation.
- Derived requirement: `LESSON-REQ-0002`

### LSN-0003 — Every operation attempt must be auditable, including a refusal decided before execution

- Reason: applies to every Gate; category checkpoint; severity HIGH; already guarded, so the control must keep holding
- Required check: Confirm that a refused operation appends its attempt to the ledger before returning an error.
- Required evidence: A ledger record with result PRECONDITION_REJECTED, a result code and a failure reason.
- Derived requirement: `LESSON-REQ-0003`

### LSN-0004 — A checkpoint may never claim readiness while it also claims to be blocked

- Reason: applies to every Gate; category checkpoint; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Verify that the checkpoint carries no blocker while it claims to be ready for review.
- Required evidence: A passing validation with blockedBy empty at a readiness status.
- Derived requirement: `LESSON-REQ-0004`

### LSN-0005 — A PASS requires evidence that can be executed or resolved, not a statement

- Reason: applies to every Gate; category quality; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Attach a resolvable evidence reference to every PASS recorded by this Gate.
- Required evidence: A validation run confirming that every PASS reference resolves.
- Derived requirement: `LESSON-REQ-0005`

### LSN-0006 — The repository must be self-contained; a specification may not live outside it

- Reason: applies to every Gate; category documentation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Confirm that every specification this Gate depends on is committed to the repository.
- Required evidence: A passing documentation link and checklist test.
- Derived requirement: `LESSON-REQ-0006`

### LSN-0007 — Independent validation cannot be declared by the run that did the work

- Reason: applies to every Gate; category process; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Close the implementing run at an internal status and leave the independent verdict pending.
- Required evidence: A checkpoint whose independentReview and redTeam are PENDING at handoff.
- Derived requirement: `LESSON-REQ-0007`

### LSN-0008 — Requirement completeness must be total and evidence-backed before handoff

- Reason: applies to every Gate; category process; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Extract every requirement before implementing and audit completeness before handoff.
- Required evidence: A completeness report with total coverage and total evidence coverage.
- Derived requirement: `LESSON-REQ-0008`

### LSN-0009 — A red gate requires rework, never a waiver, and never a weakened check

- Reason: applies to every Gate; category testing; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Run the Green Keeper until every mandatory gate is green, repairing causes rather than checks.
- Required evidence: A rework log whose last cycle is GREEN with zero remaining failures.
- Derived requirement: `LESSON-REQ-0009`

### LSN-0010 — A recorded command must carry runtime, working directory, commit and purpose to be replayable

- Reason: applies to every Gate; category tooling; severity HIGH; already guarded, so the control must keep holding
- Required check: Record commands with the tooling so each one is executable from its declared working directory.
- Required evidence: A validation run over a ledger whose commands all resolve.
- Derived requirement: `LESSON-REQ-0010`

### LSN-0011 — A control over a checkpoint's own evidence must be scoped to the moment it matters

- Reason: applies to every Gate; category tooling; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Check whether any new control would be invalidated by the evidence its own run produces.
- Required evidence: A passing validation executed by the gate harness itself.
- Derived requirement: `LESSON-REQ-0011`

### LSN-0012 — Sealed checkpoints and their tags are immutable, and tooling must keep validating them

- Reason: applies to every Gate; category git; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every sealed checkpoint still validates under the tooling this Gate changes.
- Required evidence: A passing historical compatibility run over every sealed tag.
- Derived requirement: `LESSON-REQ-0012`

### LSN-0013 — An installed capability must be detected by resolved path, not by a bare command lookup

- Reason: applies to every Gate; category environment; severity MEDIUM; status CONFIRMED, so it is not yet prevented automatically
- Required check: When this Gate records a capability, resolve the executable path before concluding anything about availability.
- Required evidence: A capability record naming the resolved path, or a justification that this Gate detects no capability.
- Derived requirement: `LESSON-REQ-0013`

### LSN-0014 — Evidence must be recorded as it happens, not reconstructed at the end of a run

- Reason: applies to every Gate; category process; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Record each command through the tooling while the work happens.
- Required evidence: A ledger whose records were produced by the recording tooling during the run.
- Derived requirement: `LESSON-REQ-0014`

### LSN-0015 — Every positive terminal status needs one shared promotion invariant

- Reason: applies to every Gate; category quality; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every positive terminal status this Gate can produce is covered by the shared promotion invariant, not only the status this delivery ends at.
- Required evidence: A table-driven validation run that exercises every positive status against every mandatory red dimension.
- Derived requirement: `LESSON-REQ-0015`

### LSN-0016 — A mandatory set must be closed by policy, never chosen by the caller

- Reason: applies to every Gate; category testing; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every control whose scope could be narrowed by an argument derives that scope from policy instead.
- Required evidence: A recorded gate run whose requiredGates equal the canonical mandatory set, with a successful command for each one.
- Derived requirement: `LESSON-REQ-0016`

### LSN-0017 — A completeness denominator must come from a source the delivery does not own

- Reason: applies to every Gate; category process; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that the expected requirement set is derived independently and compared as a set, not only as a count.
- Required evidence: A completeness report whose expected and declared identifier sets are equal.
- Derived requirement: `LESSON-REQ-0017`

### LSN-0018 — A structured reference must be resolved, not merely well typed

- Reason: applies to every Gate; category tooling; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every reference this Gate records is resolved by a tool, not accepted as a string.
- Required evidence: A validation run that rejects a nonexistent control, a nonexistent evidence path and a nested secret.
- Derived requirement: `LESSON-REQ-0018`

### LSN-0019 — A derived artifact must carry a fingerprint of the inputs that produced it

- Reason: applies to every Gate; category tooling; severity HIGH; already guarded, so the control must keep holding
- Required check: Confirm that every derived artifact this Gate stores can be recomputed and is recomputed during validation.
- Required evidence: A validation run that rejects a preflight whose inputs have changed.
- Derived requirement: `LESSON-REQ-0019`

### LSN-0020 — Evidence produced from a dirty tree needs immutable input identity

- Reason: applies to every Gate; category tooling; severity HIGH; already guarded, so the control must keep holding
- Required check: Confirm that every recorded command binds its inputs by content and that no timestamp in the ledger is later than the recorded end of the run.
- Required evidence: A validation run over a ledger whose records all carry an input digest, with a post-commit validation record at the sealed commit.
- Derived requirement: `LESSON-REQ-0020`

### LSN-0021 — Sealed history needs an anchor outside the content it describes

- Reason: applies to every Gate; category git; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that the integrity chain still resolves for every sealed checkpoint and that this Gate anchors every sealed predecessor.
- Required evidence: A verification run over the anchor chain returning no divergence.
- Derived requirement: `LESSON-REQ-0021`

### LSN-0022 — An authoritative count must be derived once, never maintained by hand twice

- Reason: applies to every Gate; category documentation; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that every count used as evidence in this Gate is derived from one source and verified where it is quoted.
- Required evidence: A validation run that rejects a report whose stated count contradicts the derived one.
- Derived requirement: `LESSON-REQ-0022`

### LSN-0023 — A lesson must cite a source that actually records the finding it claims

- Reason: applies to every Gate; category documentation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Confirm that every lesson this Gate writes or updates cites a checkpoint that records the finding identifier it names.
- Required evidence: A memory validation run that resolves every lesson source locator.
- Derived requirement: `LESSON-REQ-0023`

### LSN-0024 — A control is finished only when its positive path has been executed, not only its refusals

- Reason: applies to every Gate; category quality; severity CRITICAL; already guarded, so the control must keep holding
- Required check: For every control this Gate adds or changes that gates a status, execute the path that reaches the status, not only the paths that are refused.
- Required evidence: An executed positive-path test or simulation artifact for each such control.
- Derived requirement: `LESSON-REQ-0024`

### LSN-0025 — A generic guardrail derives repository state instead of naming today's checkpoint

- Reason: applies to every Gate; category testing; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Confirm that no generic guard, test or policy in this Gate names a historical checkpoint to decide behaviour, and that any such rule is derived from repository state.
- Required evidence: A derived exclusion with a test proving it moves, or a documented fixture that names a concrete checkpoint on purpose.
- Derived requirement: `LESSON-REQ-0025`

### LSN-0026 — An adversarial battery without a null-mutation control proves nothing

- Reason: applies to every Gate; category testing; severity HIGH; already guarded, so the control must keep holding
- Required check: Run every adversarial battery of this Gate with an unmutated control through the same path, and record its result with the battery.
- Required evidence: A Red Team report whose baselineControl is VALID.
- Derived requirement: `LESSON-REQ-0026`

### LSN-0027 — A lesson's prose may record a residual limit but may never contradict its status

- Reason: applies to every Gate; category documentation; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Confirm that every lesson this Gate writes or updates describes limits rather than restating its own status.
- Required evidence: A memory validation run with no status contradiction reported.
- Derived requirement: `LESSON-REQ-0027`

### LSN-0028 — A configuration key that no code reads is a defect, not documentation

- Reason: applies to every Gate; category tooling; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Confirm that every configuration key this Gate declares is read by the implementation, or remove it and document the fixed behaviour.
- Required evidence: A validated policy document whose every key has a consumer.
- Derived requirement: `LESSON-REQ-0028`

### LSN-0029 — A required protocol transition must never turn a mandatory gate red

- Reason: applies to every Gate; category process; severity CRITICAL; already guarded, so the control must keep holding
- Required check: Before handoff, execute the protocol transitions this Gate's successor will perform and confirm the mandatory gates stay green.
- Required evidence: A successor durability artifact whose every state is green.
- Derived requirement: `LESSON-REQ-0029`
