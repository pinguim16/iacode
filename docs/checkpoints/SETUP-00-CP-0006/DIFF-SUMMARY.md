# Diff Summary

- Added the IACode engineering memory at `.iacode/memory/`: README, rendered lesson index, the
  machine-readable `lessons.jsonl`, and the patterns, anti-patterns, incidents, guardrails and
  retrospectives directories. The memory is organizational, not personal.
- Seeded fourteen lessons strictly from findings recorded in the five sealed SETUP-00 checkpoints,
  twelve of them `GUARDED` by named automated controls and two deliberately `CONFIRMED`.
- Added `lesson.schema.json` and `lesson-preflight.schema.json`, and the lesson library, validator,
  extractor and preflight tools.
- Made the lesson preflight mandatory before every Gate, and made each applicable lesson a
  `LESSON-REQ-` requirement whose absence fails the completeness audit.
- Made `GUARDED` require a real preventive control; documentation alone is rejected.
- Implemented recurrence: a repeat increments the counter, and a repeat against a guarded lesson
  records a `GUARDRAIL_FAILURE`, escalates severity and reopens the lesson.
- Added lesson validation to the Green Keeper gate set, so a broken memory is a red delivery.
- Added the milestone validation policy: the `M0` to `M6` grouping, the `INTERNAL_GATE_PASS` and
  `MILESTONE_EXTERNAL_PASS` statuses, the milestone checkpoint contents, the auditor role, and
  `externalAuditRequired` with a recorded trigger for an extraordinary audit.
- Introduced checkpoint `schemaVersion` `3.1.0` carrying `lessonPreflight`, `milestone`,
  `externalAuditRequired` and `externalAuditReason`, with version dispatch so all five sealed
  checkpoints keep validating.
- Added the retrospective template and this Gate's retrospective.
- Updated the seven affected canonical agent contracts, the governing documents, the SETUP-00
  checklist, the tooling README, and both tool adapters, and added ADR-0009.
- The suite grew from 131 to 180 tests, covering the lesson schema and lifecycle, recurrence and
  guardrail failure, preflight selection and rejection, derived requirements and their absence,
  milestone grouping and cadence, extraordinary audits, the internal and external verdict
  vocabulary, and compatibility with every sealed checkpoint.
