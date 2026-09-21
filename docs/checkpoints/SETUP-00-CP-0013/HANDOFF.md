# Handoff

Current Gate: SETUP-00
Current Status: MILESTONE_INDEPENDENT_AUDIT_PASS

Last valid commit: 3f730dca1a12245ee8fdf8dfad7a523ed5c1c186
Current branch: main

Checkpoint schema version: `3.2.0`. Base checkpoint: `SETUP-00-CP-0012` at
`3f730dca1a12245ee8fdf8dfad7a523ed5c1c186`. Final reference:
`refs/tags/iacode-checkpoints/SETUP-00-CP-0013`, to be resolved with `git rev-parse`.

## Objective

Audit the sealed `SETUP-00-CP-0012` in a fresh session, without trusting the implementer's summary,
and decide `M0` definitively. Do not modify product code and do not implement Gate 0.

## What was completed

- `CP11-F-001` verified `CLOSED` against the sealed `SETUP-00-CP-0011` review report that raised it,
  not against the closure record that claims to have closed it.
- The six applicability states of the mirror executed against the real `m0_mirror_audit.py` in
  disposable clones by this audit's own probe, and the delivery's own semantics control executed
  separately.
- The Gate 0 transition, the positive promotion and the successor durability simulations executed:
  9/9, 9/9 and 8/8.
- Twenty-six adversarial scenarios executed over two accepted null-mutation controls, none escaped;
  six of them target the state the repair opened, and three re-derive the declared inventory hashes
  so the refusal is attributable to the control under test rather than to the inventory binding.
- The delivery's own battery re-executed: 73 of 73 defended, 38 of 38 mandatory.
- The expected requirement set, the evidence resolution, the derived counts, the engineering memory
  and the guardrail registry all re-derived with this audit's own readers, which import neither
  `policies.py`, `delivery_assurance.py` nor `lessons.py`.
- Every mandatory validation and the whole suite re-run in a clean clone detached at the subject's
  canonical tag.
- The verdict recorded in this checkpoint, with `.iacode/attestations/M0-CP-0013.json` about the
  sealed subject, and the subject left untouched.

## What was NOT completed

No Gate 0 work. `.iacode/policies/canonical-requirements.json` still declares no requirements for
`GATE 0`; authoring that specification is that Gate's first deliverable and was deliberately not
started here.

No cross-tool validation. The auditing tool, provider and model are the implementing run's, so this
is session independence only. `crossToolValidation` is `NOT_AVAILABLE` and
`MILESTONE_EXTERNAL_PASS` is refused for this mechanism.

Twenty-five additional attacks of the sealed `SETUP-00-CP-0011` battery were not re-executed by this
audit's own battery; they are not mandatory for this checkpoint, and the whole 73-attack battery was
re-executed separately through `m0_red_team.py`.

## Current repository state

Branch `main`, base commit `3f730dca1a12245ee8fdf8dfad7a523ed5c1c186`, final commit bound by
`refs/tags/iacode-checkpoints/SETUP-00-CP-0013`. `STATE.json` records the exact values.

## Files changed

See `FILES.json` and `DIFF-SUMMARY.md`. No sealed checkpoint was modified, no historical tag was
moved, no commit was rewritten and no file under `scripts/` or `tests/` was touched. The only
changes outside this checkpoint directory are the twelfth integrity anchor, the attestation this
audit authored, and `LATEST.md`.

## Important decisions

See `DECISIONS.md`. The load-bearing ones: the verdict belongs to this checkpoint about a sealed
subject; the mechanism is fresh-session and is recorded as such; every mirror conclusion comes from
running the mirror; the independent readers import none of the product tooling; the reverse escape
was attacked rather than assumed closed; and the first draft of this audit's own expected-set reader
was wrong and is recorded as wrong.

## Tests executed

`python -m unittest discover -s tests`, with the result read directly: 410 discovered, 410 run, 0
failures, 0 errors, 1 skipped. The skip is
`AuditAttestationModelTests.test_an_unsealed_subject_is_rejected`, which needs an unsealed checkpoint
directory and therefore executes during any delivery and skips only in a checkout at rest; it is
investigated in `REVIEW-REPORT.md` and recorded in `RISKS.md` as `R4`. The same suite was executed
again as the mandatory `tests` gate of the Green Keeper cycle, and again in a clean clone detached at
the subject tag.

Also `python -m compileall -q scripts tests`, `validate_lessons.py`, `verify_integrity.py`,
`derive_counts.py`, `check_completeness.py`, `derive_requirements.py`, `milestone_status.py`,
`mirror_semantics_validation.py`, `gate_transition_simulation.py`, `promotion_simulation.py`,
`successor_durability.py`, `m0_red_team.py`, `m0_mirror_audit.py --clean-clone`,
`validate_checkpoint.py`, and this checkpoint's own harness.

## Known failures

None outstanding. Two recorded failures remain in `COMMANDS.jsonl` deliberately: `validate_checkpoint`
and `check_completeness` were run against this checkpoint before it carried its own artifacts, and a
failed attempt keeps its record so corrections stay visible. Both are green in the final state.

## Known risks

See `RISKS.md`. Especially: this audit's independence is of the session and not of the tool; the
trust model is structural rather than cryptographic; `NOT_APPLICABLE` is a new state that must not
become a habit; and one test stops asserting in a repository at rest.

## Do not repeat

Do not verify a closure against the record that claims it; read the sealed report that raised the
finding. Do not conclude anything about a control from an artifact a delivery wrote; run the control.
Do not accept an attack as defended because the exit code is non-zero; require the refusal the attack
was aimed at, and repair the attacker's tracks when an unrelated control fires first. Do not describe
a same-tool audit as cross-tool validation.

## Required next action

Request explicit authorization to open `GATE 0 — FOUNDATION`, as described in `NEXT.md`. Gate 0 is
authorised by the milestone but not started, and it may not be started without its own pre-Gate
checkpoint.

## Exact continuation sequence

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`,
   `docs/DEFINITION-OF-DONE.md`, `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`,
   `docs/checkpoints/LATEST.md` and this complete checkpoint.
2. Read `REVIEW-REPORT.md` and `MILESTONE-REPORT.md`, then confirm the verdict by derivation with
   `milestone_status.py` rather than by reading `STATE.json`.
3. Run the validation commands below and compare the observed Git state with `STATE.json`.
4. Follow `NEXT.md`.

## Validation commands

- `git status --short --branch`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse refs/tags/iacode-checkpoints/SETUP-00-CP-0013`
- `python scripts/development-ledger/validate_checkpoint.py`
- `python scripts/development-ledger/validate_lessons.py`
- `python scripts/development-ledger/verify_integrity.py`
- `python scripts/development-ledger/derive_counts.py`
- `python scripts/development-ledger/check_completeness.py`
- `python scripts/development-ledger/derive_requirements.py`
- `python scripts/development-ledger/milestone_status.py --milestone M0` — expect `MILESTONE_PASSED`
  derived from `.iacode/attestations/M0-CP-0013.json` about `SETUP-00-CP-0012`
- `python scripts/development-ledger/m0_mirror_audit.py --clean-clone`
- `python docs/checkpoints/SETUP-00-CP-0013/audit-harness/derive_expected.py --checkpoint SETUP-00-CP-0012`
- `python docs/checkpoints/SETUP-00-CP-0013/audit-harness/resolve_evidence.py --checkpoint SETUP-00-CP-0012`
- `python docs/checkpoints/SETUP-00-CP-0013/audit-harness/verify_memory.py`
- `sh docs/checkpoints/SETUP-00-CP-0013/audit-harness/clean_clone.sh . SETUP-00-CP-0013`
- `python -m compileall -q scripts tests`
- `python -m unittest discover -s tests`

## Stop conditions

Stop on unexpected Git divergence, on a failing validation, on any need to modify a sealed checkpoint
or move a historical tag, on secret exposure, and on any attempt to begin Gate 0 without explicit
authorization and a new pre-Gate checkpoint.
