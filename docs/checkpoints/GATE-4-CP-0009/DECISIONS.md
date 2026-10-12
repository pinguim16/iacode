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
