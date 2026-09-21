# Lesson Candidates from the M0 fresh-session audit

These are audit-owned `OBSERVED` candidates. Nothing in `.iacode/memory/` was created, modified or
retired by this audit. The implementer assesses provenance, category, severity, applicability and
guardrail evidence in the corrective checkpoint, and only that run may promote a candidate.

1. A control is only finished when its positive path is executed, not only its refusals.
2. A guardrail test must derive what it excludes, never name it by literal.
3. An adversarial fixture needs a null-mutation control and must restore the shared state it writes.
4. A derived-count control that inspects one file type leaves the same defect class alive elsewhere.
5. A lesson's prose must not contradict its own status.
6. A configuration key that no code reads is a defect, not a harmless comment.
7. The lesson preflight presumes an implementing delivery and has no audit-role subset.
8. The secret detector's documented scope excludes bare cloud access key identifiers, and the policy
   says so; this is recorded as an observation, not as a defect.

The observation and the proposed automated guardrail for each are in `LESSON-CANDIDATES.json`.
