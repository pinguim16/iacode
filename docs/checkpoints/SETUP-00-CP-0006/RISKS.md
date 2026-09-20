# Risks

- The Gate is not granted. `SETUP-00` stays open until the Codex `M0` milestone audit covering
  `SETUP-00-CP-0005`, this checkpoint, and SETUP-00 as a whole.
- The milestone cadence can delay discovery of a systemic defect by up to four Gates. The
  extraordinary-audit trigger exists for the categories where that delay is unacceptable, but
  deciding that a situation qualifies remains a judgement.
- A memory can grow into noise. The applicability filters, the `RETIRED` status and the recurrence
  key bound it, but nothing yet measures whether a lesson is still worth carrying.
- Two lessons are `CONFIRMED` and cannot be guarded from this repository. They depend on the
  preflight being run and answered honestly.
- The derived requirement mechanism proves that a lesson was declared and evidenced, not that the
  evidence actually addresses the lesson. That mapping remains a review judgement.
- Role separation between the Green Keeper and the Delivery Completeness Validator is still emulated
  inside one session: separation of contract and artifact, not of process.
- Four schema rule sets now coexist. All are covered by tests, including validation of every sealed
  checkpoint, but each version adds dispatch cost.
- The lesson extractor classifies a candidate by keyword. It is a starting point for a human
  judgement, not a classifier, and it never promotes beyond `OBSERVED`.
- Secret detection still covers only the families documented in `.iacode/policies/secret-policy.md`.
- `write_json` still emits platform-native line endings; content hashing normalizes them and
  `.gitattributes` forces LF, so this remains cosmetic and out of scope.
- `SETUP-00` supplies governance and tooling only. No runtime described by the Master Plan exists.
