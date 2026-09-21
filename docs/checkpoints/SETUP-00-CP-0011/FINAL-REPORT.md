# Final Report — M0 / SETUP-00 final fresh-session independent audit

## Status

- Audit checkpoint: SETUP-00-CP-0011
- Subject: SETUP-00-CP-0010 at 90b67a7e0a11179465bc5c92dee22c78da36801f
- Audit mechanism: FRESH_SESSION_INDEPENDENT_AUDIT
- Independent review: REWORK_REQUIRED
- Red Team: RED_TEAM_PASS
- Cross-tool validation: NOT_AVAILABLE
- Fresh-session independent audit: FAILED
- Milestone M0: REWORK_REQUIRED
- SETUP-00: REWORK_REQUIRED
- Gate 0: BLOCKED
- Findings: one, CP11-F-001, CRITICAL

## Environment

- OS: Windows 11 Pro 10.0.26200
- Shell: Git Bash and PowerShell
- Python: 3.13.15
- Branch: main
- Baseline commit/tag: 90b67a7e0a11179465bc5c92dee22c78da36801f /
  iacode-checkpoints/SETUP-00-CP-0010
- Audit checkpoint tag target: iacode-checkpoints/SETUP-00-CP-0011

## Tool / Model / Effort

- Primary tool: Claude Code 2.1.195, desktop application
- Provider: Anthropic
- Model: claude-opus-5
- Effort: not exposed by the tool; not invented
- Session independence: new session, no memory of the run that produced SETUP-00-CP-0010
- Same tool as the implementer: yes. Same provider: yes. Same model: yes.
- Token accounting: not exposed by the tool

## Deliverables

- A 254-row audit matrix created before substantive execution and completed with every mandatory row
  executed and carrying evidence.
- An independent re-derivation of the expected requirement set of the subject, by a parser that
  never imports the product policy module.
- An independent resolution of all 723 evidence references the subject declares.
- Execution of all 42 regression and negative tests the closure record names, by identifier, in two
  environments.
- Execution of the whole suite in the working repository and in a clean clone detached at the subject
  tag, with the result object read directly so a skip can never be read as a pass.
- Re-execution of every canonical mandatory validator, both positive-path simulations, the mandatory
  attack battery and the internal mirror audit.
- An adversarial battery written for this audit, 37 scenarios over disposable copies of a sealed
  snapshot with a mandatory null-mutation control, all defended.
- An independent re-derivation of the whole integrity chain from Git, and detached validation of all
  ten sealed checkpoints.
- The tenth integrity anchor, which this checkpoint owed its sealed predecessor, and the attestation
  that records the audit.
- One finding with acceptance criteria and a regression scenario, and five recorded observations that
  are deliberately not findings.

## Files Created

All files under docs/checkpoints/SETUP-00-CP-0011, including FINAL-M0-AUDIT-MATRIX.*,
REVIEW-REPORT.md, RED-TEAM-REPORT.md, MILESTONE-REPORT.md, AUDIT-EXECUTIONS.json,
RESUME-VALIDATION.md, COMPLETENESS-REPORT.*, M0-INTERNAL-RED-TEAM.*, M0-INTERNAL-MIRROR.*, the
standard checkpoint ledger, and audit-harness/; plus .iacode/attestations/M0-CP-0011.json.

## Files Modified

Only docs/checkpoints/LATEST.md and .iacode/anchors/checkpoint-chain.json outside this checkpoint.
No product script, test, schema, policy, canonical memory file, governing document, sealed checkpoint
or historical tag was modified.

## Validation

- Audit matrix: every mandatory row executed, no row NOT_STARTED, IN_PROGRESS or UNVERIFIED, no row
  without evidence.
- The declared requirement set of the subject equals an independently derived expected set exactly.
- The subject's completeness recomputed at total coverage and total evidence coverage.
- The Green Keeper cycle of the subject was measured against the canonical mandatory gate set with no
  gate dropped, every gate exited zero with command evidence, and its scope fingerprint still
  describes the sealed content.
- Engineering memory valid; every guardrail effective; no unresolved guardrail failure.
- Lesson preflight fresh by recomputation; every derived requirement present in the matrix.
- Integrity: 10 anchors, each re-derived from Git; every anchored tag resolves to its anchored commit
  and tree; all ten sealed checkpoints validate from a detached checkout of their own tag.
- Internal mirror audit of this checkpoint: FAIL, which is the finding.

## Tests

- Working repository, subject content: 363 discovered, 363 run, 0 failures, 0 errors.
- Clean clone detached at the subject tag: 363 discovered, 363 run, 0 failures, 0 errors.
- This checkpoint, final content: 363/363 TESTS, 0 failures, 0 errors, 0 skips.
- The 42 tests the closure record names: all pass when executed by identifier in the working
  repository, and all pass or are conditionally skipped in the fully sealed clean clone.

## Red Team

- The adversarial battery of this audit: 37 scenarios, 37 defended, 0 escaped, over a null-mutation
  control that was accepted before any refusal was attributed to a mutation.
- The canonical mandatory battery, re-executed against the subject: 56 executed, 56 defended, 26 of
  26 mandatory, 0 escaped.
- The internal mirror audit of the subject, re-executed from a clean clone: 18 of 18 checks pass.
- Result: RED_TEAM_PASS. The first revision of this audit's battery carried four wrong expectations;
  they were corrected and the correction is recorded rather than hidden.

## Known Risks

See RISKS.md. The load-bearing ones: this verdict is independent of the implementing run and not of
the tool; the trust model of a milestone verdict is structural rather than cryptographic; and the
finding blocks the next delivery as well as this audit.

## Remaining Work

The implementer must close CP11-F-001 so that a checkpoint which corrects no audit can obtain a
passing internal mirror through the shipped tooling, add the regression scenario the finding names,
re-run the whole delivery order, and request a new M0 audit. The eight-row observation set in
AUDIT-EXECUTIONS.json needs no action but is worth reading first.

## Handoff Readiness

The handoff is complete and self-contained: the reproduction commands, the per-finding acceptance
criteria, and the harness that produced every result are all in the repository. The milestone is not
ready to pass. No implementation assertion was used as independent proof anywhere in this audit.

## Next Gate

GATE 0 — FOUNDATION is BLOCKED. It may be authorized only after a corrective checkpoint passes a new
M0 audit.

## Evidence

- FINAL-M0-AUDIT-MATRIX.json / .md
- REVIEW-REPORT.md
- RED-TEAM-REPORT.md
- MILESTONE-REPORT.md
- AUDIT-EXECUTIONS.json
- COMPLETENESS-REPORT.json / .md
- REQUIREMENTS-MATRIX.json / .md, CLOSURE-REQUIREMENTS.json / .md
- M0-INTERNAL-RED-TEAM.json, M0-INTERNAL-MIRROR.json / .md
- LESSON-PREFLIGHT.json / .md
- RESUME-VALIDATION.md
- TESTS.json, QUALITY.json, COUNTS.json, COMMANDS.jsonl, REWORK-LOG.jsonl, STATE.json
- audit-harness/
