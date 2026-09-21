# Next

## Required next action

`CORRECTIVE DELIVERY FOR THE M0 FRESH-SESSION AUDIT`.

Return to the implementer. Open a new SETUP-00 checkpoint whose first action is the lesson
preflight, and correct the two critical findings:

- `CP9-F-001` — give `MILESTONE_EXTERNAL_PASS` a reachable positive path, and prove it with a test
  that reaches the status through a valid attestation rather than only refusing invalid ones.
- `CP9-F-002` — derive the anchor-chain exclusion instead of naming `SETUP-00-CP-0008` by literal,
  and add a test that seals a synthetic successor so the literal cannot return.

Then assess `CP9-F-003`, `CP9-F-004` and `CP9-F-005`, and the eight `OBSERVED` candidates in
`LESSON-CANDIDATES.json`. Promotion into `.iacode/memory/` belongs to that run, not to this audit.

`REVIEW-REPORT.md` carries, for each finding, the requirement, the expected and observed behaviour,
the reproduction, the evidence, the acceptance criteria and a regression scenario. The audit's own
harness is in `audit-harness/` and reproduces from a clean clone.

## Next Gate

`GATE 0 — FOUNDATION` remains `BLOCKED`. It requires the `M0` audit to pass, explicit
authorization, and a new pre-Gate checkpoint. No Gate 0 work exists in this change set, and this
audit did not begin any.
