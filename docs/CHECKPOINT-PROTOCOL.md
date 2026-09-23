# Checkpoint Protocol

A checkpoint is a reconstructible snapshot of observable engineering state.

## Canonical statuses

`NOT_STARTED`, `BASELINING`, `IN_PROGRESS`, `BLOCKED`, `READY_FOR_REVIEW`, `REWORK_REQUIRED`, `READY_FOR_RED_TEAM`, `INTERNAL_GATE_PASS`, `MILESTONE_INDEPENDENT_AUDIT_PASS`, `MILESTONE_EXTERNAL_PASS`, `GATE_PASS`, `GATE_FAIL`.

`MILESTONE_INDEPENDENT_AUDIT_PASS` and `MILESTONE_EXTERNAL_PASS` are the two verdicts an independent
audit can record, and both belong to the **audit checkpoint**, never to the delivery it judges. See
[MILESTONE-VALIDATION.md](MILESTONE-VALIDATION.md).

## Required events

Create or finalize a checkpoint before a Gate, after baseline, after a material architecture decision or milestone, before and after destructive change, on important failure, before switching tools, before ending a session or likely context exhaustion, before merge, after Red Team, and at Gate closure.

## Required contents

Each checkpoint contains status, handoff, run metadata, state, plan, decisions, commands, file inventory, tests, quality, provenance, diff summary, risks, and next action. `LATEST.md` points textually to the last checkpoint accepted by validation.

## Schema versions

`schemaVersion` selects the rules a checkpoint is judged by. Version `1.0.0` is the historical
format used by the first sealed SETUP-00 checkpoints. Version `2.0.0` adds the structured cross-tool
validation state, evidence-referenced quality results, command identifiers, and the bound file
inventory described below. Version `3.0.0` adds the delivery-assurance blocks, the reproducible
command record, and the delivery gates. Version `3.1.0` adds the engineering memory preflight and
the milestone validation policy. Validation applies the rules of the version a checkpoint declares,
so a sealed checkpoint never becomes invalid because the tooling advanced. New checkpoints use
`3.1.0`.

## Status and blockers

A checkpoint may never claim readiness and blockage at the same time. `READY_FOR_REVIEW`,
`READY_FOR_RED_TEAM`, `INTERNAL_GATE_PASS`, `MILESTONE_INDEPENDENT_AUDIT_PASS`,
`MILESTONE_EXTERNAL_PASS`, and `GATE_PASS` require `blockedBy` to be empty, in every schema version
and
whichever tool sealed the checkpoint. `BLOCKED` requires at least one entry in `blockedBy`, because a
blocked checkpoint must say what blocks it.

## Delivery assurance

A `3.0.0` checkpoint carries `requirementsMatrix`, `greenKeeper`, `deliveryCompleteness`,
`reworkCycles`, `independentReview`, and `redTeam` in `STATE.json`, plus
`REQUIREMENTS-MATRIX.json` and `REQUIREMENTS-MATRIX.md`. Offering it for review additionally
requires `REWORK-LOG.jsonl`, `COMPLETENESS-REPORT.json`, `COMPLETENESS-REPORT.md`, and
`FINAL-REPORT.md`.

`READY_FOR_REVIEW` is refused unless `greenKeeper.status` and `deliveryCompleteness.status` are both
`PASS`, coverage is total, no requirement is `PARTIAL` or `MISSING`, no non-independent quality
dimension is `NOT_EXECUTED` or `FAIL`, and `independentReview` and `redTeam` are still `PENDING`.
The recorded gate values are cross-checked against the rework log and against a recomputation of the
requirements matrix, so a checkpoint cannot assert a gate it did not earn.

## Commit semantics

Git commits cannot embed their own hash. Work-in-progress checkpoints may use the canonical symbolic value `HEAD`, which validation resolves to the checked-out commit. Any handoff-ready or terminal state (`READY_FOR_REVIEW`, `READY_FOR_RED_TEAM`, `GATE_PASS`, or `GATE_FAIL`) must instead use an immutable namespaced reference such as `refs/tags/iacode-checkpoints/SETUP-00-CP-0001`, created at the checkpoint commit after that commit exists. Validation resolves the tag and requires it to equal the checked-out commit. A checkpoint is sealed only when its `currentCommit` names its own canonical tag, at every status, because a sealed checkpoint is later validated from that tag with a detached HEAD; `seal_checkpoint.py` refuses anything else, and a sealed state that kept the symbolic `HEAD` is bound to the checkpoint's own canonical tag instead (`ADR-0023`). `UNBORN` is allowed only before a first commit; exact 40-character commit IDs are compared literally. The final report delivered to a user provides the resolved hash.

Self-hashes in `FILES.json` are omitted because changing that file changes its own hash. Other hashes are included when useful and stable. Text hashes use UTF-8 with line endings normalized to LF so validation remains portable across Git checkouts.

## Published history

Sealed evidence is judged from the published history, because that is what a reviewer receives
([ADR-0028](adr/ADR-0028-sealed-evidence-is-judged-from-the-published-history.md)). Every commit a
checkpoint's evidence names — a command record's `commit`, `subjectCommit` or
`repositoryState.head`, and the checkpoint's `baseCommit`, `currentCommit`, `initialCommit` and
`finalCommit` — must be reachable from a published reference: a branch, a tag or a remote-tracking
branch. An object that exists only in one machine's store is refused, and validation says so,
whatever schema version the checkpoint declares.

A commit that a record names and that is replaced before it is published is kept reachable by a
lightweight tag of its own under `refs/tags/iacode-preserved/`, pushed with the history. The record
is never rewritten. Every control that clones this repository to judge sealed history clones the
published history only (`ledger_common.published_clone`, Git's transport), never a copy of the
local object store (`M1-F-003`).

## Checkout modes

Validation normally runs on an attached branch, where the branch name and the checked-out commit
must both match `STATE.json`. A sealed checkpoint may also be validated from a detached checkout,
which is how another tool inspects an immutable reference. Detached validation removes the branch
control, so every remaining anchor becomes mandatory: the worktree must be clean and `dirty` must be
`false`, `currentCommit` must name the checkpoint's canonical `refs/tags/iacode-checkpoints/` tag,
that tag must exist, and it must resolve to the checked-out commit. Finalization always requires an
attached branch; a detached checkout is read-only.

## File inventory binding

For `schemaVersion` `2.0.0`, `FILES.json` is the authoritative description of the change set between
`baseCommit` and the validated tree, and validation recomputes that change set from Git. Every added,
modified, or deleted path must be declared exactly once with a reason, an undeclared change or a
declared non-change is an error, added and modified paths carry `hashAfter`, and modified and deleted
paths carry `hashBefore`. Hashes are re-derived by `finalize_checkpoint.py`; the author still supplies
every declaration and reason, because the tool never invents one. The single exclusion is
`FILES.json` itself, which cannot contain its own hash and is instead bound by the checkpoint commit,
its required presence, and its schema. See
[ADR-0006](adr/ADR-0006-checkpoint-inventory-binding.md).

## Finalization

Finalization is observable. Every attempt appends its own sanitized record to the checkpoint's
`COMMANDS.jsonl`, including an attempt refused by a precondition before the operation ran. A refusal
carries `result = PRECONDITION_REJECTED`, a documented `resultCode`, a `failureReason`, the evaluated
preconditions, and no `exitCode`, because no process was launched and a fabricated exit code would be
false evidence. A failed attempt restores the previous metadata but its record stays, so corrections
remain visible. The successful attempt is recorded before the inventory hashes are sealed, so the
command that produced the final state is itself covered by the inventory it seals.

## Command reproducibility

A `3.0.0` command record carries an identifier, timestamp, runtime, working directory, the command,
sanitized arguments, referenced inputs, the repository commit, a purpose, a canonical result, an exit
code or a result code, a duration, and stream artifacts when they exist. The recorded command is the
literal invocation: it starts with an explicit runtime and any script path resolves from the working
directory. A bare script name that cannot be executed from where the record says it ran is invalid
evidence.

## Promotion

The run that implements a Gate closes its checkpoint at `READY_FOR_REVIEW`. `GATE_PASS` is granted by
a later, independent run, and for `schemaVersion` `2.0.0` the validator refuses `GATE_PASS` unless
`secondToolValidation.status` is `PASSED`, or `NOT_REQUIRED` with a recorded justification.

## Divergence

If Git state differs unexpectedly from the checkpoint, do not continue. Create `DIVERGENCE.md` with expected, observed, difference, and possible cause; set status `BLOCKED`; wait for reconciliation.

## Engineering memory and milestone policy

`schemaVersion` `3.1.0` adds the engineering memory preflight and the milestone validation policy on
top of `3.0.0`. A `3.1.0` checkpoint carries `lessonPreflight`, `milestone`, `externalAuditRequired`
and `externalAuditReason` in `STATE.json`, and a checkpoint offered for review additionally carries
`LESSON-PREFLIGHT.json`.

Validation checks that the recorded preflight counts match the artifact, that the milestone
identifier and gate grouping match the published plan, that an extraordinary audit names a recorded
trigger, and that the engineering memory itself is valid. `INTERNAL_GATE_PASS` records the project's
own verdict; only `MILESTONE_EXTERNAL_PASS` records an independent one, and it requires both the
milestone and the cross-tool validation to be `PASSED`.

Every completed Gate also produces a retrospective in `.iacode/memory/retrospectives/`.

## Milestone closure controls

`schemaVersion` `3.2.0` adds the controls recorded in
[ADR-0010](adr/ADR-0010-milestone-closure-controls.md). A `3.2.0` checkpoint carries
`CLOSURE-REQUIREMENTS.json` and `.md` from its first moment, and, once it is offered for review,
`COUNTS.json`, `<milestone>-INTERNAL-RED-TEAM.json` and `<milestone>-INTERNAL-MIRROR.json`, plus the
findings-closure artifact of every audit whose corrective work it is.

`STATE.json` additionally carries `guardrailEffectiveness`, `integrity` and `externalAttestation`.
The requirements matrix and the completeness report are `schemaVersion` `2.0.0`, the lesson preflight
is `2.0.0`, and the engineering memory declares policy `2.0.0` in `.iacode/memory/POLICY.json`.

### Integrity anchors

`.iacode/anchors/checkpoint-chain.json` records, for every sealed checkpoint, its canonical tag, its
commit, its tree and the digest of its predecessor's anchor. Validation re-derives all of it from
Git, so a moved tag, a rewritten commit, an unexpected tree or a broken link is detected.

A checkpoint cannot anchor its own tag, because the anchor would have to contain the commit that
contains it. Its successor anchors it, and a checkpoint that fails to anchor a sealed predecessor is
refused.

Exactly one checkpoint may therefore carry no anchor: the newest sealed one, whose anchor its
successor still owes. That exclusion is **derived**, by `anchors.pending_anchor_exclusion`, from the
sealed history itself. The CLI, the validator and the test suite all ask the same function, because
the second `M0` audit found a guardrail test that named the excluded checkpoint by literal and so
turned the mandatory `tests` gate red the moment a successor anchored its predecessor.

This is **tamper evidence inside the local trust model**, not a signature. An actor who controls the
whole repository can recompute the chain. What the chain removes is the coordinated edit that leaves
the ledger internally consistent, which is the failure the `M0` audit demonstrated.

### Sealing

Sealing is monotonic and post-commit, in two steps:

1. commit the prepared content;
2. run `python scripts/development-ledger/seal_checkpoint.py`, which validates that commit with a
   clean worktree, records the run as `post-commit-validation` bound to it, stamps the end of the
   run after that record, refreshes the declared inventory hashes, commits the append-only evidence
   and creates the canonical tag.

Validation then requires a `post-commit-validation` record that exited zero over a clean tree and
describes `HEAD` or `HEAD^`; in the second case the difference between them may be nothing but
`COMMANDS.jsonl`, `FILES.json` and `RUN-METADATA.json`. No command timestamp may be later than
`RUN-METADATA.finishedAt`.

The residual limit is stated plainly: a commit cannot contain a validation of itself, so the evidence
commit is validated by the reader and anchored by the next checkpoint.
