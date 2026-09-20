# Risks

- The Gate is not granted. `SETUP-00` stays open at `READY_FOR_REVIEW` until an independent Codex run
  performs the review and Red Team and records `secondToolValidation`.
- `secondToolValidation` reads `PENDING_MANUAL`. The previous independent verdict was `FAILED`; this
  checkpoint answers it but cannot clear it.
- Role separation between the Green Keeper and the Delivery Completeness Validator is emulated inside
  one session. It is a separation of contract and artifact, not of process.
- The completeness audit verifies that evidence resolves, not that the evidence is the right evidence
  for the requirement. Mapping a reference to a requirement remains a review judgement.
- `NOT_APPLICABLE` requirements and declared external blockers are judgement calls constrained by a
  mandatory justification, not by a mechanism.
- Three schema rule sets now coexist. All are covered by tests, including validation of the four
  sealed checkpoints, but a fourth version would increase that cost again.
- The command reproducibility rule checks the first script path token and the declared inputs; it
  cannot prove that re-running the command reproduces the same result on a different machine.
- The inventory and the gates depend on the immutability of the checkpoint tag. Moving a tag or
  rewriting history defeats them, which is why both stay prohibited.
- Secret detection covers only the families documented in `.iacode/policies/secret-policy.md`. A bare
  AWS access key id, a Slack `xox` token, a Google `AIza` key, a JWT, a database URL with an embedded
  password, an Azure connection string, an `npm_` token, and a Stripe `sk_live_` key are not detected
  unless they appear in a named assignment.
- `write_json` still emits platform-native line endings. Content hashing normalizes them and
  `.gitattributes` forces LF in the repository, so this is cosmetic and remains out of scope.
- `SETUP-00` supplies governance and tooling only. No runtime described by the Master Plan exists.
