# Risks

- The Gate is not granted. `SETUP-00` stays open at `READY_FOR_REVIEW` until an independent Codex run
  performs review and Red Team and records `secondToolValidation`.
- `secondToolValidation` still reads `PENDING_MANUAL`. Genuine cross-tool validation has not happened;
  the `C:/Users/cesar/.local/bin/claude.exe` CLI remains unauthenticated, and the authenticated Claude
  Code desktop session that produced this checkpoint is the implementer, not an independent verifier.
- `NOT_REQUIRED` is an escape hatch in the cross-tool validation state. It demands a justification and
  stays visible in `STATE.json`, but a future run could still misuse it.
- The inventory binds declared paths and hashes, not declared reasons. A misleading reason is a review
  concern, not a machine-checkable one.
- The inventory is only as strong as the immutability of the checkpoint tag. Moving a tag, rewriting
  history, or re-sealing a tampered tree defeats it, which is why those operations stay prohibited.
- Secret detection covers only the families documented in `.iacode/policies/secret-policy.md`. A bare
  AWS access key id, a Slack `xox`-prefixed token, a Google `AIza` key, a JWT, a database URL with an
  embedded password, an Azure connection string, an `npm_` token, and a Stripe `sk_live_` key are not
  detected unless they appear in a named assignment. This is unchanged and remains defense in depth.
- `write_json` emits platform-native line endings, so checkpoint JSON written on Windows contains CRLF
  in the working tree while Git stores LF. This is harmless today because content hashing normalizes
  line endings and `.gitattributes` forces LF in the repository, and a `core.autocrlf` checkout was
  tested; it was left unchanged because it is outside the scope of these six findings.
- The validator implements the JSON Schema subset this repository uses, not the whole specification.
  New keywords require validator tests or a managed dependency.
- Schema dispatch adds two rule sets. Both are tested, but a third version would increase that cost.
- Two Claude Code installations remain present with different versions, and the user-local directory
  is still absent from the detecting process's `PATH`.
- `SETUP-00` supplies governance and tooling only. No runtime described by the Master Plan exists.
