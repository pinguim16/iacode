# Lesson Preflight

- Gate: `SETUP-00`
- Scope: `control-plane`
- Technologies: _none declared_
- Modules: _none declared_
- Generated: `2026-09-20T15:47:23Z`
- Lessons considered: 14
- Lessons applicable: 14

Every applicable lesson below is a requirement of this Gate. The derived identifiers must
appear in `REQUIREMENTS-MATRIX.json`, and the Delivery Completeness Validator fails the
delivery when one is absent.

| Lesson | Status | Severity | Derived requirement | Required check |
|---|---|---|---|---|
| `LSN-0001` Checkpoint validation must succeed from a detached checkout of the checkpoint tag | `GUARDED` | HIGH | `LESSON-REQ-0001` | Validate the checkpoint from a clean clone detached at its own tag, not only on the branch. |
| `LSN-0002` A file inventory must be recomputed from the repository, never trusted as an assertion | `GUARDED` | HIGH | `LESSON-REQ-0002` | Declare every changed path with a reason before finalizing and let the tooling bind the hashes. |
| `LSN-0003` Every operation attempt must be auditable, including a refusal decided before execution | `GUARDED` | HIGH | `LESSON-REQ-0003` | Confirm that a refused operation appends its attempt to the ledger before returning an error. |
| `LSN-0004` A checkpoint may never claim readiness while it also claims to be blocked | `GUARDED` | CRITICAL | `LESSON-REQ-0004` | Verify that the checkpoint carries no blocker while it claims to be ready for review. |
| `LSN-0005` A PASS requires evidence that can be executed or resolved, not a statement | `GUARDED` | HIGH | `LESSON-REQ-0005` | Attach a resolvable evidence reference to every PASS recorded by this Gate. |
| `LSN-0006` The repository must be self-contained; a specification may not live outside it | `GUARDED` | MEDIUM | `LESSON-REQ-0006` | Confirm that every specification this Gate depends on is committed to the repository. |
| `LSN-0007` Independent validation cannot be declared by the run that did the work | `GUARDED` | CRITICAL | `LESSON-REQ-0007` | Close the implementing run at an internal status and leave the independent verdict pending. |
| `LSN-0008` Requirement completeness must be total and evidence-backed before handoff | `GUARDED` | HIGH | `LESSON-REQ-0008` | Extract every requirement before implementing and audit completeness before handoff. |
| `LSN-0009` A red gate requires rework, never a waiver, and never a weakened check | `GUARDED` | HIGH | `LESSON-REQ-0009` | Run the Green Keeper until every mandatory gate is green, repairing causes rather than checks. |
| `LSN-0010` A recorded command must carry runtime, working directory, commit and purpose to be replayable | `GUARDED` | MEDIUM | `LESSON-REQ-0010` | Record commands with the tooling so each one is executable from its declared working directory. |
| `LSN-0011` A control over a checkpoint's own evidence must be scoped to the moment it matters | `GUARDED` | MEDIUM | `LESSON-REQ-0011` | Check whether any new control would be invalidated by the evidence its own run produces. |
| `LSN-0012` Sealed checkpoints and their tags are immutable, and tooling must keep validating them | `GUARDED` | HIGH | `LESSON-REQ-0012` | Confirm that every sealed checkpoint still validates under the tooling this Gate changes. |
| `LSN-0013` An installed capability must be detected by resolved path, not by a bare command lookup | `CONFIRMED` | MEDIUM | `LESSON-REQ-0013` | When this Gate records a capability, resolve the executable path before concluding anything about availability. |
| `LSN-0014` Evidence must be recorded as it happens, not reconstructed at the end of a run | `CONFIRMED` | MEDIUM | `LESSON-REQ-0014` | Record each command through the tooling while the work happens. |

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

- Reason: applies to every Gate; category quality; severity HIGH; already guarded, so the control must keep holding
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

- Reason: applies to every Gate; category process; severity HIGH; already guarded, so the control must keep holding
- Required check: Extract every requirement before implementing and audit completeness before handoff.
- Required evidence: A completeness report with total coverage and total evidence coverage.
- Derived requirement: `LESSON-REQ-0008`

### LSN-0009 — A red gate requires rework, never a waiver, and never a weakened check

- Reason: applies to every Gate; category testing; severity HIGH; already guarded, so the control must keep holding
- Required check: Run the Green Keeper until every mandatory gate is green, repairing causes rather than checks.
- Required evidence: A rework log whose last cycle is GREEN with zero remaining failures.
- Derived requirement: `LESSON-REQ-0009`

### LSN-0010 — A recorded command must carry runtime, working directory, commit and purpose to be replayable

- Reason: applies to every Gate; category tooling; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Record commands with the tooling so each one is executable from its declared working directory.
- Required evidence: A validation run over a ledger whose commands all resolve.
- Derived requirement: `LESSON-REQ-0010`

### LSN-0011 — A control over a checkpoint's own evidence must be scoped to the moment it matters

- Reason: applies to every Gate; category tooling; severity MEDIUM; already guarded, so the control must keep holding
- Required check: Check whether any new control would be invalidated by the evidence its own run produces.
- Required evidence: A passing validation executed by the gate harness itself.
- Derived requirement: `LESSON-REQ-0011`

### LSN-0012 — Sealed checkpoints and their tags are immutable, and tooling must keep validating them

- Reason: applies to every Gate; category git; severity HIGH; already guarded, so the control must keep holding
- Required check: Confirm that every sealed checkpoint still validates under the tooling this Gate changes.
- Required evidence: A passing historical compatibility run over every sealed tag.
- Derived requirement: `LESSON-REQ-0012`

### LSN-0013 — An installed capability must be detected by resolved path, not by a bare command lookup

- Reason: applies to every Gate; category environment; severity MEDIUM; status CONFIRMED, so it is not yet prevented automatically
- Required check: When this Gate records a capability, resolve the executable path before concluding anything about availability.
- Required evidence: A capability record naming the resolved path, or a justification that this Gate detects no capability.
- Derived requirement: `LESSON-REQ-0013`

### LSN-0014 — Evidence must be recorded as it happens, not reconstructed at the end of a run

- Reason: applies to every Gate; category process; severity MEDIUM; status CONFIRMED, so it is not yet prevented automatically
- Required check: Record each command through the tooling while the work happens.
- Required evidence: A ledger whose records were produced by the recording tooling during the run.
- Derived requirement: `LESSON-REQ-0014`
