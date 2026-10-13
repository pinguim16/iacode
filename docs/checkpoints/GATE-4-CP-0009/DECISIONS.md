# Decisions

- Treat `G4-F-004` as a lifecycle defect, not a bad digest: the producer must bind an immutable Git
  subject and the seal/validator must reproduce it.
- Break the mathematical self-reference explicitly: `REVIEW-BUNDLE-VALIDATION.json` is the sealed
  declaration sidecar and is not a member of the archive whose digest it declares.
- Preserve historical checkpoints under their declared schemas. The stronger reconstruction rule is
  forward-only for schema 3.4 checkpoints.
- The implementing run may produce internal assurance but leaves independent review, independent Red
  Team and `secondToolValidation` pending.
- Preserve cmd-0023 as the complete 40/42 red cycle. Attack T was expected to escape on immutable
  CP0008, while the 950-second cancellation failure exposed a separate scheduling race that this
  Gate must repair rather than dismiss as a transient.
- Close the cancellation race by rechecking the accepted signal after the awaited
  `CHECK_DISPATCHED` transition and before sandbox activity creation. Do not weaken the 900-second
  product deadline or replace the failed complete run with an isolated scenario rerun.
- Make review-bundle mandatory artifacts milestone-aware and let an implementation-time transport
  probe choose the newest immutable checkpoint that is actually complete. An unfinished CP0009 is
  not made complete by a test or attack harness.
- Reserve `iacode-preserved/` for commits already named by sealed evidence. Publish exact pre-seal
  verifier inputs under `iacode-subjects/`; cmd-0038 removed only the misclassified remote tag after
  cmd-0037 published the same commit in the correct namespace.
- Treat a pre-execution subject-resolution refusal as an attempted input, never as executed commit
  evidence. Preserve cmd-0033 and make its refusal recomputable; do not publish its mistyped hash.
- Correct cmd-0050's unsealed explicit input metadata to the canonical
  `.iacode/policies/audit-registry.json` path that requirement derivation actually consumed. The
  command, result, timestamp and repository state are unchanged.
- Escalate the cmd-0060 cancellation recurrence as a `GUARDRAIL_FAILURE`. A Temporal signal remains
  the low-latency path, but persisted `CANCELLING` is authoritative: re-read it after dispatch and
  poll it while the sandbox activity is in flight, cancelling the activity when either path fires.
- Preserve cmd-0068 as focused red evidence. When an accepted cancellation races with a normal
  sandbox response, cancellation wins before persistence; recording the normal response into an
  already `CANCELLING` run is correctly forbidden and must never strand the workflow.
- Adopt ADR-0036's pre-seal checkout mode. A clean detached `IN_PROGRESS` checkpoint may bind its
  symbolic HEAD to a matching `iacode-subjects/<checkpoint>...` tag, while every handoff-ready or
  sealed state continues to require `iacode-checkpoints/<checkpoint>`.
- Preserve cmd-0083 as the complete 41/42 red cycle. Treat an ADR and its canonical index row as one
  atomic structural change; repair the index and prove both enumeration and missing-row detection
  rather than waiving the root test or reusing the 41 passing stages.
