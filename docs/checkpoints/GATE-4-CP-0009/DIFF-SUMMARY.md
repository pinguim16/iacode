# Diff Summary

- Review transport is reconstructed from an immutable Git subject, byte-compared twice across
  non-local detached transport and bound by schema 3.4 declaration evidence.
- Detached pre-seal validation accepts only the matching checkpoint-named `iacode-subjects/` tag;
  sealed and handoff-ready states still require the canonical checkpoint tag.
- Durable evaluator cancellation observes persisted `CANCELLING` before and during the activity,
  handles pre-assignment signals and gives accepted cancellation precedence over racing success.
- Gate 4 attack T, command provenance, subject refusal, review-context and declaration validation
  are strengthened with positive and negative regressions.
- ADR-0035 and ADR-0036 document the structural choices; the ADR index is updated atomically.
- Engineering Memory records all confirmed failures and guarded recurrences, including cancellation,
  checkpoint self-evidence, ephemeral evidence, structural indexing, assurance denominators and
  lesson applicability.
- CP0009 preserves every failed full verifier and Green Keeper cycle before the final green evidence.

`FILES.json` is the authoritative path and hash inventory.
