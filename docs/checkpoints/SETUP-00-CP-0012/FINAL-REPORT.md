# Final Report — SETUP-00-CP-0012, the corrective delivery that closes CP11-F-001

## Status

- Checkpoint: SETUP-00-CP-0012
- Gate: SETUP-00
- Status: READY_FOR_REVIEW
- Milestone M0: PENDING, awaiting a fresh-session independent audit of this checkpoint
- Gate 0: BLOCKED
- Audit findings closed: CP11-F-001, the single critical finding of M0-CP-0011
- Independent review: PENDING
- Red Team: PENDING
- Blockers: none

## Environment

- OS: Windows 11 Pro 10.0.26200
- Shell: Git Bash and PowerShell
- Python: 3.13.15
- Branch: main
- Base commit: 98a9f4ca83d538e9610844086ca74b7ff32492e1 /
  iacode-checkpoints/SETUP-00-CP-0011
- Final reference: refs/tags/iacode-checkpoints/SETUP-00-CP-0012, resolved with git rev-parse

## Tool / Model / Effort

- Primary tool: Claude Code 2.1.195, desktop application
- Provider: Anthropic
- Model: claude-opus-5
- Effort: not exposed by the tool; not invented
- Role: implementing run. Every verdict recorded here is internal quality assurance, and none is
  recorded as independent validation.
- Token accounting: not exposed by the tool

## Deliverables

- The repair of CP11-F-001: an audit control that tells an empty applicable set from a missing
  required set. A dimension with nothing to audit is NOT_APPLICABLE with a reason, an expected count
  of zero and the canonical source the emptiness was derived from; a dimension whose sources name
  items the delivery does not satisfy is still FAIL.
- The reverse escape closed at the same time: an unjustified inapplicable dimension, one carrying
  items, one counted as a pass, one under the older report version and one declared over work the
  audit registry still names are all refused.
- MIRROR-SEMANTICS-VALIDATION.*: the real tool executed over six applicability states.
- GATE0-TRANSITION-SIMULATION.*: a closed milestone followed by the first checkpoint of the next
  Gate reaching READY_FOR_REVIEW, against a synthetic specification that never leaves the disposable
  repository.
- POSITIVE-PROMOTION-VALIDATION.* and SUCCESSOR-DURABILITY.*, both re-executed, with the mirror
  report now produced by running the tool instead of being written by hand.
- The parser repair that made registering the third sealed audit possible at all: its findings and
  its battery were rendered in a third way and were being read as empty.
- The twelve mandatory attacks of the sealed SETUP-00-CP-0011 battery, executed by this delivery's
  own battery, and five new scenarios against the state the repair opens.
- LSN-0031, GRD-0030, GRD-0031 and GRD-0032, and the GUARDRAIL_FAILURE recorded against LSN-0024 and
  LSN-0029 for this recurrence and resolved here.
- The permanent language rule in CLAUDE.md and the canonical checklist row 7d.16.
- CP11-FINDINGS-CLOSURE.* and FINAL-CORRECTION-REQUIREMENTS.*.

## Files Created

Under docs/checkpoints/SETUP-00-CP-0012: the standard ledger plus FINAL-CORRECTION-REQUIREMENTS.*,
CP11-FINDINGS-CLOSURE.*, MIRROR-SEMANTICS-VALIDATION.*, GATE0-TRANSITION-SIMULATION.*,
POSITIVE-PROMOTION-VALIDATION.*, SUCCESSOR-DURABILITY.*, AFFECTED-RED-TEAM.*,
FINAL-INTERNAL-AUDIT.*, M0-INTERNAL-RED-TEAM.* and M0-INTERNAL-MIRROR.*. Outside it:
scripts/development-ledger/mirror_semantics_validation.py and
scripts/development-ledger/gate_transition_simulation.py.

## Files Modified

scripts/development-ledger/m0_mirror_audit.py, policies.py, validate_checkpoint.py,
promotion_fixture.py, promotion_simulation.py, m0_red_team.py; tests/test_development_ledger.py;
.iacode/schemas/mirror-audit.schema.json; .iacode/policies/audit-registry.json and
canonical-requirements.json; .iacode/agents/m0-closure-auditor.md; .iacode/memory/lessons.jsonl,
guardrails/registry.json and LESSONS.md; .iacode/anchors/checkpoint-chain.json; CLAUDE.md;
docs/SETUP-00-CHECKLIST.md, QUALITY-GATES.md, DEVELOPMENT-CONTRACT.md, DEFINITION-OF-DONE.md;
docs/checkpoints/LATEST.md. See FILES.json and DIFF-SUMMARY.md. No sealed checkpoint was modified
and no historical tag was moved.

## Validation

- The finding set of the CP-0011 audit is re-parsed from the sealed review report at every
  validation, so the closure record can neither omit a finding nor invent one.
- The expected requirement set is derived from the canonical checklist, the lesson preflight and the
  registered audit, and compared exactly with the declared set.
- The delivery completeness audit recomputes coverage and evidence coverage from the matrix, and
  checkpoint validation recomputes it again.
- Every count used as evidence is derived once into COUNTS.json and re-derived during validation.
- The integrity chain anchors the sealed predecessor and re-derives every anchor from Git.
- The engineering memory validates, every guardrail resolves and is verified by a test, and no
  guardrail failure is unresolved.
- Every sealed checkpoint still validates under this tooling from a detached checkout of its own
  tag.

## Tests

- python -m unittest discover -s tests: 410 discovered, 410 run, 0 failures, 0 errors, 0 skipped.
  The result object was read directly rather than inferred from the summary line.
- The suite was executed again as the mandatory `tests` gate of the Green Keeper cycle, over the
  same content.

## Red Team

- The internal battery was executed against a disposable copy of this checkpoint, one fresh copy per
  scenario, over a null-mutation control that was accepted before any refusal was attributed to a
  mutation. Its numbers are in COUNTS.json and M0-INTERNAL-RED-TEAM.json.
- It includes the twelve mandatory attacks the sealed SETUP-00-CP-0011 report hands this delivery,
  and five scenarios aimed at the state the applicability repair opens.
- This is internal quality assurance. The independent Red Team belongs to the next M0 audit and is
  recorded as PENDING.

## Known Risks

See RISKS.md. The load-bearing ones: registering the audit gives this delivery work to close and
could mask a repair that only works when there is work, which is why the repair is proven in the
states where there is nothing to close; NOT_APPLICABLE is a new state that must not become a
bypass, which is why four layers refuse an unjustified or contradicted one; and the verdict of this
delivery is internal.

## Remaining Work

A fresh-session independent M0 audit of this checkpoint. It authors its own checkpoint, anchors this
one and carries the attestation about it. Gate 0 remains blocked and unspecified: the canonical
requirement registry declares no requirements for it, which is the first deliverable of that Gate.

## Handoff Readiness

The handoff is complete and self-contained: the validation commands, the reproduction of the finding
and of its repair, and every simulation that produced a result are in the repository and executable
without this session.

## Next Gate

GATE 0 — FOUNDATION is BLOCKED. It requires a passing M0 audit, explicit authorization and a new
pre-Gate checkpoint. No Gate 0 work exists in this change set and none was started.

## Evidence

- CP11-FINDINGS-CLOSURE.json / .md
- FINAL-CORRECTION-REQUIREMENTS.json / .md
- MIRROR-SEMANTICS-VALIDATION.json / .md
- GATE0-TRANSITION-SIMULATION.json / .md
- POSITIVE-PROMOTION-VALIDATION.json / .md
- SUCCESSOR-DURABILITY.json / .md
- M0-INTERNAL-RED-TEAM.json / .md, AFFECTED-RED-TEAM.json / .md
- M0-INTERNAL-MIRROR.json / .md
- FINAL-INTERNAL-AUDIT.json / .md
- REQUIREMENTS-MATRIX.json / .md, CLOSURE-REQUIREMENTS.json / .md
- COMPLETENESS-REPORT.json / .md, REWORK-LOG.jsonl
- LESSON-PREFLIGHT.json / .md
- TESTS.json, QUALITY.json, COUNTS.json, COMMANDS.jsonl, STATE.json, FILES.json
- RESUME-VALIDATION.md
