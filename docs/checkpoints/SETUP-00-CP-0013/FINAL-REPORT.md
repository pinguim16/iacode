# Final Report — SETUP-00-CP-0013

## Status

`MILESTONE_INDEPENDENT_AUDIT_PASS`.

`M0` — **`PASSED`**. `SETUP-00` — closed. `GATE 0 — FOUNDATION` — authorised, not started.
`CP11-F-001` is `CLOSED`. No new finding.

This run was asked to audit the sealed `SETUP-00-CP-0012` in a fresh session, without trusting the
implementer's summary, and to decide `M0`. It changed no product code and implemented no Gate 0.

## Environment

Windows 11 Pro 10.0.26200, Python 3.13, Git. Branch `main`, base commit
`3f730dca1a12245ee8fdf8dfad7a523ed5c1c186`, the commit
`refs/tags/iacode-checkpoints/SETUP-00-CP-0012` resolves to. Every adversarial scenario and every
simulation ran in its own disposable clone under the system temporary directory, never in the
repository.

## Tool / Model / Effort

Claude Code 2.1.195, Anthropic, `claude-opus-5`. Effort is not exposed by the runtime and is
recorded as `not-exposed` rather than guessed.

This is a **fresh session** with no memory of the implementing run: independence of the session,
not of the tool. `crossToolValidation` is `NOT_AVAILABLE`, the attestation mechanism is
`FRESH_SESSION_INDEPENDENT_AUDIT`, and the derivation refuses `MILESTONE_EXTERNAL_PASS` from it.

## Deliverables

- `REVIEW-REPORT.md` — the verdict and its basis, including what was examined and not raised.
- `MILESTONE-REPORT.md` — the `M0` verdict, what closed it, and the audit history of the milestone.
- `RED-TEAM-REPORT.md` and `M0-INTERNAL-RED-TEAM.json` — twenty-six scenarios over two accepted
  null-mutation controls.
- `FINAL-M0-AUDIT-MATRIX.json` and `.md` — the audit mandate as twenty-two rows, written before
  execution and rebuilt from the recorded results.
- `AUDIT-EXECUTIONS.json` — every execution this audit relied on.
- `MIRROR-SEMANTICS-PROBE.json`, `NA-ESCAPE-PROBE.json`, `EXPECTED-SET-SUBJECT.json`,
  `EVIDENCE-RESOLUTION-SUBJECT.json`, `MEMORY-MEASUREMENT.json` — this audit's own derivations.
- `.iacode/attestations/M0-CP-0013.json` — the attestation about the sealed subject.
- `audit-harness/` — the instruments, so every result reproduces from a clean clone.

## Files Created

Fifty-eight paths: this checkpoint's artifacts and its harness, plus
`.iacode/attestations/M0-CP-0013.json`. `FILES.json` declares each one with its reason.

## Files Modified

Two paths: `.iacode/anchors/checkpoint-chain.json`, which gains the twelfth anchor for the sealed
predecessor this checkpoint owes it, and `docs/checkpoints/LATEST.md`.

No file under `scripts/`, `tests/`, `prompts/` or `.claude/` was touched, no sealed checkpoint was
modified, and no historical tag was moved.

## Validation

`CHECKPOINT_VALID`. `LESSONS_VALID`. `INTEGRITY_VALID` with twelve anchors.
`DELIVERY_COMPLETENESS_GATE=PASS` at total coverage and total evidence coverage.
`GREEN_KEEPER_GATE=PASS` on cycle two over the closed canonical mandatory set.
`INTERNAL_MIRROR=PASS`, sixteen of eighteen passing with two dimensions `NOT_APPLICABLE` and none
failing. All of it again in a clean clone detached at the subject's canonical tag.

## Tests

Four hundred and ten discovered, four hundred and ten run, no failure and no error, with one skip:
`AuditAttestationModelTests.test_an_unsealed_subject_is_rejected`, which needs an unsealed
checkpoint directory and therefore executes during any delivery and skips only in a repository at
rest. It is investigated in `REVIEW-REPORT.md` and carried as `R4` in `RISKS.md`. The same result in
a clean clone.

## Red Team

`RED_TEAM_PASS`, twenty-six of twenty-six defended, over two null-mutation controls that were
accepted first. Six scenarios attack the state the `CP11-F-001` repair opened; three repair their
own tracks by re-deriving the declared inventory hashes so the refusal is attributable to the
control under test rather than to the file-inventory binding. The delivery's own battery was
re-executed separately and reported seventy-three of seventy-three.

## Known Risks

See `RISKS.md`. The independence of this audit is of the session and not of the tool; the trust
model is structural rather than cryptographic; `NOT_APPLICABLE` is a new state that must not become
a habit; one test stops asserting in a repository at rest; Gate 0 has no canonical specification
yet; and every derived measurement describes the tree it was computed over.

## Remaining Work

None for `M0`. For `GATE 0 — FOUNDATION`: obtain explicit authorization, create its own pre-Gate
checkpoint, and author the canonical requirement specification that
`.iacode/policies/canonical-requirements.json` does not yet declare. That specification is the
Gate's first deliverable and was deliberately not started here.

## Handoff Readiness

Ready. The checkpoint validates, is sealed under its canonical tag, anchors its sealed predecessor,
and carries the attestation the milestone verdict is derived from.
`python scripts/development-ledger/milestone_status.py --milestone M0` re-derives that verdict from
a clean checkout; reading `STATE.json` is not confirmation and this report does not ask anyone to
treat it as such. `HANDOFF.md` lists the exact continuation sequence and `NEXT.md` the single next
allowed action.

## Next Gate

`GATE 0 — FOUNDATION`: authorised by the milestone, **not started**, and blocked on explicit
authorization plus a new pre-Gate checkpoint. Its milestone is `M1`, which it does not close, so it
will end at `INTERNAL_GATE_PASS` rather than at a milestone verdict.

## Evidence

| Claim | Where |
|---|---|
| `CP11-F-001` closed, proved by running the tool | `MIRROR-SEMANTICS-PROBE.json`, `AUDIT-EXECUTIONS.json` `EX-013` |
| The reverse escape is refused | `NA-ESCAPE-PROBE.json`, `M0-INTERNAL-RED-TEAM.json` |
| A delivery that corrects no audit passes its mirror | `M0-INTERNAL-MIRROR.json` — this checkpoint |
| The expected set and the evidence agree with an independent derivation | `EXPECTED-SET-SUBJECT.json`, `EVIDENCE-RESOLUTION-SUBJECT.json` |
| The memory and the guardrails are clean | `MEMORY-MEASUREMENT.json` |
| The audit mandate is fully executed and evidenced | `FINAL-M0-AUDIT-MATRIX.json` |
| The verdict is derived, not asserted | `.iacode/attestations/M0-CP-0013.json`, `MILESTONE-REPORT.md` |
