# Final Report — SETUP-00-CP-0010, the CP-0009 corrective delivery

## Status

- Checkpoint: SETUP-00-CP-0010
- Status: READY_FOR_REVIEW
- Gate: SETUP-00; Milestone: M0, status PENDING
- Audit corrected: M0-CP-0009, the fresh-session independent audit of SETUP-00-CP-0008
- CP9 findings closed: 5/5 FINDINGS
- Independent review: PENDING; Red Team: PENDING
- Gate 0: BLOCKED, pending a passing M0 audit and explicit authorization

## Environment

- OS: Windows 11 Pro 10.0.26200
- Shell: Git Bash and PowerShell
- Python: 3.13.15
- Branch: main
- Base commit: 28c2b487baf216d3745bb6c5a25a5b8aa7274a9e (`iacode-checkpoints/SETUP-00-CP-0009`)
- Final reference: refs/tags/iacode-checkpoints/SETUP-00-CP-0010

## Tool / Model / Effort

- Primary tool: Claude Code 2.1.195, desktop application
- Provider: Anthropic; Model: claude-opus-5
- Effort: not exposed by the tool and not invented
- Independence: none. This is the implementing run; every verdict here is internal.
- Token accounting: not exposed by the tool

## Deliverables

- The corrected milestone verdict architecture: the audit checkpoint carries the verdict about a
  sealed subject, the attestation never names its own commit, and the verdict is derived.
- `MILESTONE_INDEPENDENT_AUDIT_PASS`, so a fresh-session audit is not described as external.
- One derived rule for the checkpoint whose anchor is still owed, used by the CLI, the validator and
  the suite.
- Two executed simulations: a complete two-checkpoint promotion and a three-checkpoint succession.
- Deduplicated test counts, a refused count larger than what exists, and a mandatory null-mutation
  control in every adversarial battery.
- A closed memory policy schema, a repaired lesson note, and the assessment of all eight CP-0009
  lesson candidates.
- 5 finding closures, 32 correction rows, and the Gate retrospective.

## Files Created

See `FILES.json` and `DIFF-SUMMARY.md`. New product files: `milestone_status.py`,
`promotion_fixture.py`, `promotion_simulation.py`, `successor_durability.py`,
`affected_red_team.py`, `docs/adr/ADR-0011-audit-checkpoint-carries-the-verdict.md`, the checkpoint
itself and the retrospective.

## Files Modified

The attestation model, the validator, the anchors, the counts derivation, the policies parser, the
requirement derivation, the memory tooling, both internal assurance tools, the schemas they bind,
the engineering memory, the governing documents and both tool adapters. No sealed checkpoint,
historical tag or audit report was modified.

## Validation

- Requirements: 134/134 REQUIREMENTS, coverage 100.0 per cent,
  evidence coverage 100.0 per cent, 0 partial, 0 missing.
- The declared set equals the derived expected set exactly: 134 expected, 134 declared.
- Green Keeper: PASS, 6 cycle(s), remaining failures
  0, unresolved rework 0.
- Delivery Completeness: PASS.
- Integrity: PASS, 9 anchors, including the one this checkpoint owed
  SETUP-00-CP-0009.
- Engineering memory: 28/30 LESSONS guarded; guardrails 29/29 GUARDRAILS effective,
  0 unresolved guardrail failures.
- Lesson preflight: fresh, 29 applicable lessons, 29 derived requirements.

## Tests

- `python -m unittest discover -s tests`: 363/363 TESTS.
- One physical execution, recorded once: the unit and integration categories share `runId`, so the
  derivation counts 363 passing cases rather than adding the same run to itself.
- Clean clone: see RESUME-VALIDATION.md. See `RESUME-VALIDATION.md`.

## Red Team

- Internal battery: 56/56 ATTACKS defended, escaped 0.
- Null-mutation control: VALID.
- Mandatory battery: 26; additional battery:
  30; attestation scenarios:
  14; positive controls:
  2. The categories do not overlap and each is derived.
- Internal mirror audit: PASS, 18 of 18 checks.
- Neither is independent validation, and neither is recorded as one.

## Known Risks

See `RISKS.md`. The load-bearing ones: the trust model of a milestone verdict is structural rather
than cryptographic; this delivery is not independently validated; and the accepted independence for
the next audit is session independence, not tool independence.

## Remaining Work

A fresh-session independent `M0` audit of this checkpoint, performed as described in `NEXT.md`: the
auditor authors its own checkpoint, anchors this one, writes the attestation about it, and closes at
`MILESTONE_INDEPENDENT_AUDIT_PASS` or `REWORK_REQUIRED`.

## Handoff Readiness

The handoff is complete and self-contained. Every finding closure names its regression tests, both
positive paths are recorded as executed artifacts, and the reproduction commands are in `HANDOFF.md`.
No implementation assertion is used as proof anywhere in this checkpoint.

## Next Gate

`GATE 0 — FOUNDATION` remains `BLOCKED`.

## Evidence

- CP9-FINDINGS-CLOSURE.json / .md
- FINAL-CORRECTION-REQUIREMENTS.json / .md
- POSITIVE-PROMOTION-VALIDATION.json / .md
- SUCCESSOR-DURABILITY.json / .md
- AFFECTED-RED-TEAM.json / .md
- M0-INTERNAL-RED-TEAM.json / .md, M0-INTERNAL-MIRROR.json / .md
- REQUIREMENTS-MATRIX.json / .md, CLOSURE-REQUIREMENTS.json / .md
- COMPLETENESS-REPORT.json / .md, COUNTS.json, TESTS.json, QUALITY.json
- LESSON-PREFLIGHT.json / .md, LESSON-CANDIDATE-ASSESSMENT.md
- RESUME-VALIDATION.md, REWORK-LOG.jsonl, COMMANDS.jsonl, STATE.json, FILES.json

### Findings

- `CP9-F-001` — CRITICAL — `CLOSED`
- `CP9-F-002` — CRITICAL — `CLOSED`
- `CP9-F-003` — LOW — `CLOSED`
- `CP9-F-004` — LOW — `CLOSED`
- `CP9-F-005` — LOW — `CLOSED`

### Positive paths

- Positive promotion: `PASS`, derived milestone verdict `PASSED`,
  7 of 7 checks, subject unchanged.
- Successor durability: `PASS`, 8 of 8 checks across
  3 states.
