# Decisions

- **A control may not take its scope, its denominator or its verdict from the thing it constrains.**
  Seven of the eleven `M0` findings are that one mistake in seven places. Every correction in this
  checkpoint derives its expectation from a source the delivery does not own, and recomputes it
  during validation. ADR-0010 records the decision and its consequences.
- **The mandatory gate set is policy, not an argument.** `--gates` was the mechanism of the vacuous
  `PASS`, so it can now only extend a run. A diagnostic flag that could still write a recorded
  verdict was considered and rejected.
- **The requirement set is derived, not transcribed.** The canonical checklist is re-parsed, the
  findings and attacks of the open audit are re-parsed from the sealed reports, and the lesson
  preflight is read. Each matrix row carries an anchored `sourceRef`, and the expected and declared
  sets are compared exactly rather than by size.
- **An external verdict requires a second sealed checkpoint.** `MILESTONE_EXTERNAL_PASS`,
  `secondToolValidation = PASSED` and `milestone.status = PASSED` are derived from an attestation
  whose audit checkpoint is sealed, anchored and different from the one being promoted. The control
  is structural, not cryptographic, and both `docs/MILESTONE-VALIDATION.md` and
  `.iacode/attestations/README.md` state that limit instead of implying more.
- **Integrity anchors are tamper evidence inside the local trust model.** They detect a moved tag, a
  rewritten commit, an unexpected tree and a broken chain link. They are not signatures, and an
  actor with full repository control can recompute them. The claim is written down exactly that way.
- **A checkpoint cannot anchor its own tag.** The anchor would have to contain the commit that
  contains it. The successor anchors it, and a checkpoint that fails to anchor a sealed predecessor
  is refused. That is why `.iacode/anchors/checkpoint-chain.json` ends at `SETUP-00-CP-0007`.
- **Sealing takes two commits.** The content commit is validated with a clean worktree and that run
  is recorded against the commit it judged; the second commit may contain nothing but
  `COMMANDS.jsonl`, `FILES.json` and `RUN-METADATA.json`. The residual limit, that a commit cannot
  contain a validation of itself, is stated rather than hidden.
- **Sealed `SETUP-00-CP-0006` was not corrected.** Its state declares 47 mandatory requirements
  while its matrix and report compute 45. Sealed checkpoints are immutable, so the contradiction is
  recorded as a closed finding and the cross-check applies from `schemaVersion` `3.2.0` onward.
- **New rules are version-dispatched.** Checkpoint `3.2.0`, matrix and completeness report `2.0.0`,
  preflight `2.0.0` and engineering memory policy `2.0.0` carry the new rules; sealed checkpoints
  keep validating under the rules of their own versions. That invariant is `LSN-0012`, and breaking
  it while repairing `LSN-0012` would have been the worst available outcome.
- **Four bypassed guardrails were reopened before they were repaired.** `LSN-0005`, `LSN-0007`,
  `LSN-0008`, `LSN-0009`, `LSN-0010` and `LSN-0012` each recorded a `GUARDRAIL_FAILURE`, which
  escalated their severity and returned them to `CONFIRMED`. They returned to `GUARDED` only after a
  registered guardrail resolved and its verifying tests existed.
- **`LSN-0013` stays `CONFIRMED`.** An arbitrary machine's installation state cannot be observed
  from this repository, so no control can prevent that failure class. Claiming a guardrail for it
  would be exactly the false claim `validate_lessons.py` now refuses.
- **The derivation modules were written before the requirement matrix.** `policies.py`, `anchors.py`
  and `attestation.py` exist so the matrix could be *derived* from the canonical sources rather than
  transcribed from the prompt. No finding was implemented before the matrix existed, and the matrix
  has been regenerated from those sources at every change since.
- **The internal Red Team and the mirror audit are declared, not disguised.** Both run in the
  implementing session on the same tooling. They are recorded as internal quality assurance, the
  mirror audit must say so in its own `independence` field, and the validator refuses either of them
  as an external verdict.
- **Counts are derived once.** Every number used as evidence comes from `COUNTS.json`, and a
  Markdown claim of the form `N/M LABEL` is checked against the derivation. This is the mechanical
  answer to the count drift that recurred across CP-0005, CP-0006 and CP-0007.
- **The first ledger record was bound to the content it actually read.** `cmd-0001` was written by
  the pre-`3.2.0` `new_checkpoint.py`, before input binding existed, so it named an input without a
  digest. The digest was derived from the base commit, which is exactly the content that invocation
  read, and the record says so in its own notes. Its exit code, commit and timestamp are unchanged.
  The alternative, relaxing the rule for records written before the rule existed, would have been a
  weakened check rather than a correction.
