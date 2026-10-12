# Decisions

- Treat `G4-F-004` as a lifecycle defect, not a bad digest: the producer must bind an immutable Git
  subject and the seal/validator must reproduce it.
- Break the mathematical self-reference explicitly: `REVIEW-BUNDLE-VALIDATION.json` is the sealed
  declaration sidecar and is not a member of the archive whose digest it declares.
- Preserve historical checkpoints under their declared schemas. The stronger reconstruction rule is
  forward-only for schema 3.4 checkpoints.
- The implementing run may produce internal assurance but leaves independent review, independent Red
  Team and `secondToolValidation` pending.
