# Final Report — M0 / SETUP-00 fresh-session independent audit

## Status

- Audit checkpoint: SETUP-00-CP-0009
- Subject: SETUP-00-CP-0008 at c53f4c59a77870414324efa6b5f61b35d26c5090
- Audit mechanism: FRESH_SESSION_INDEPENDENT_AUDIT
- Independent review: REWORK_REQUIRED
- Red Team: RED_TEAM_PASS
- Cross-tool validation: NOT_AVAILABLE
- Fresh-session independent audit: FAILED
- Milestone M0: REWORK_REQUIRED
- SETUP-00: REWORK_REQUIRED
- Gate 0: BLOCKED

## Environment

- OS: Windows 11 Pro 10.0.26200
- Shell: Git Bash and PowerShell
- Python: 3.13.15
- Branch: main
- Baseline commit/tag: c53f4c59a77870414324efa6b5f61b35d26c5090 / iacode-checkpoints/SETUP-00-CP-0008
- Audit checkpoint tag target: iacode-checkpoints/SETUP-00-CP-0009

## Tool / Model / Effort

- Primary tool: Claude Code 2.1.195, desktop application
- Provider: Anthropic
- Model: claude-opus-5
- Effort: not exposed by the tool; not invented
- Session independence: new session, no memory of the run that produced SETUP-00-CP-0008
- Same tool as the implementer: yes. Same provider: yes. Same model: yes.
- Token accounting: not exposed by the tool
- Measurable executions: clean-clone suite 242.7 s; working-repository suite 249.1 s and 270.6 s;
  fixture-clone suite 346.3 s; 53 finding regression tests 76.3 s; new-surface classes 57.0 s

## Deliverables

- A 183-row audit matrix created before substantive execution and completed at 100.00 per cent
  execution and 100.00 per cent evidence.
- An independent re-derivation of the expected requirement set, 131 for 131.
- An independent review with five findings, two of them critical.
- An auditor-owned Red Team battery of 52 attacks with a null-mutation control, plus 33 assurance
  scenarios over an accepted baseline, 7 history scenarios, 15 attestation probes and 6 preflight
  mutations.
- A recomputation of the engineering memory, the guardrail effectiveness, the semantic counts, the
  command ledger, the documentation links and the sealed history.
- The eighth integrity anchor, which this checkpoint owed its sealed predecessor.
- Eight OBSERVED lesson candidates; the canonical memory was not modified.
- The audit harness itself, kept in the checkpoint so every result reproduces from a clean clone.

## Files Created

All files under docs/checkpoints/SETUP-00-CP-0009, including FINAL-M0-AUDIT-MATRIX.*,
REVIEW-REPORT.md, RED-TEAM-REPORT.md, MILESTONE-REPORT.md, AUDIT-EXECUTIONS.*, LESSON-CANDIDATES.*,
RESUME-VALIDATION.md, COMPLETENESS-REPORT.*, FINAL-REPORT.md, the standard checkpoint ledger, and
audit-harness/.

## Files Modified

Only docs/checkpoints/LATEST.md and .iacode/anchors/checkpoint-chain.json outside this checkpoint.
No product script, test, schema, policy, canonical memory file, sealed checkpoint or historical tag
was modified.

## Validation

- Audit matrix: 183/183 executed, 100.00 per cent; evidence 100.00 per cent; 0 NOT_STARTED,
  0 IN_PROGRESS, 0 UNVERIFIED, 0 rows without evidence.
- Two rows record an audited property that did not hold: EXT-012 and TST-011.
- SETUP-00 checklist, audited row by row: 69/71 COMPLETE, 2 PARTIAL, coverage 97.18 per cent.
- Subject's declared requirement set: 131 = 131 against an independently derived expectation.
- Subject's completeness recomputed: 131/131, 100.00/100.00.
- Sealed history: 7 anchors verified read-only; an eighth added for SETUP-00-CP-0008.
- Documentation links: 39/39 resolve.
- Semantic counts: 18 cross-artifact comparisons, 0 mismatches.

## Tests

- Clean detached clone of the subject's tag: 306/306 passed.
- Fresh fixture clone: 306/306 passed.
- Working repository after anchoring the sealed predecessor: 305/306. The single failure is
  IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected and is finding
  CP9-F-002. It was recorded, not repaired, because an auditor may not change product code.
- The 53 regression tests that close the eleven CP-0007 findings: 53/53 passed.
- The 64 tests covering the surfaces this delivery introduced: 64/64 passed.

## Red Team

- Mandatory attacks: 26. Defended: 26. Escaped: 0.
- Additional attacks: 26. Defended: 26. Escaped: 0.
- Positive control POS-EXT: REFUSED, which is finding CP9-F-001 rather than an escape.
- Result: RED_TEAM_PASS.

## Known Risks

Five findings are open: two CRITICAL, three LOW. See REVIEW-REPORT.md and RISKS.md. The two
critical ones block the milestone; the three low ones are each an instance of a class the project
already guards against elsewhere.

## Remaining Work

The implementer must close CP9-F-001 and CP9-F-002 with a regression test each, assess CP9-F-003 to
CP9-F-005 and the eight lesson candidates, re-run the whole delivery order, and request a new M0
audit.

## Handoff Readiness

The handoff is complete and self-contained: the reproduction commands, the acceptance criteria per
finding, and the harness that produced every result are all in the repository. The milestone is not
ready to pass. No implementation assertion was used as independent proof anywhere in this audit.

## Next Gate

Gate 0 is BLOCKED. It may be authorized only after a corrective checkpoint passes a new M0 audit.

## Evidence

- FINAL-M0-AUDIT-MATRIX.json / .md
- REVIEW-REPORT.md
- RED-TEAM-REPORT.md
- MILESTONE-REPORT.md
- AUDIT-EXECUTIONS.json / .md
- COMPLETENESS-REPORT.json / .md
- REQUIREMENTS-MATRIX.json / .md, CLOSURE-REQUIREMENTS.json / .md
- LESSON-CANDIDATES.json / .md
- RESUME-VALIDATION.md
- TESTS.json, QUALITY.json, COUNTS.json, COMMANDS.jsonl, REWORK-LOG.jsonl, STATE.json
- audit-harness/
