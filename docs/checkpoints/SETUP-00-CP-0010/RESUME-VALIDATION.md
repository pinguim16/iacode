# Resume Validation

## Clean cold start

This delivery began from the repository alone: `START-HERE.md` resolved the phase, the Gate, the
delivery order and `docs/checkpoints/LATEST.md`; `LATEST.md` named `SETUP-00-CP-0009`; that
checkpoint's `REVIEW-REPORT.md` carried the acceptance criteria and the regression scenario for each
finding, and its `HANDOFF.md` carried the reproduction commands. No external summary of the audit was
used as evidence anywhere: every finding corrected here was re-read from the sealed report.

## Clean clone execution

`m0_mirror_audit.py --clean-clone` cloned the repository with no workspace state and ran the full
suite, `compileall`, the memory validation, the integrity chain and the completeness audit inside the
clone. Recorded as `MIR-017`: `suite=ok, compileall=ok, lessons=ok, integrity=ok, completeness=ok`.

A second clean clone ran the controls that check adds, with no session state:

| Check | Exit | Observed |
|---|---|---|
| `compileall` | 0 | no output |
| `validate_lessons.py` | 0 | `LESSONS_VALID total=30 active=30 guarded=28` |
| `verify_integrity.py` | 0 | `INTEGRITY_VALID anchors=9 latest=SETUP-00-CP-0009` |
| `derive_counts.py` | 0 | every derived count matches the stored derivation |
| `check_completeness.py` | 0 | `DELIVERY_COMPLETENESS_GATE=PASS` with total coverage |
| `derive_requirements.py` | 0 | the expected set re-derives to the declared set |
| `milestone_status.py --milestone M0` | 1 | `no independent audit attestation exists for milestone M0` |
| `promotion_simulation.py` | 0 | `POSITIVE_PROMOTION=PASS verdict=PASSED checks=7/7` |
| `successor_durability.py` | 0 | `SUCCESSOR_DURABILITY=PASS checks=8/8` |

The single non-zero exit is the honest one: `M0` has no attestation yet, because this delivery is the
*subject* of the next audit and not its author. A delivery that could produce its own milestone
verdict would be the defect `CP9-F-001` exists to prevent.

## Truthful blocked continuation

Attempted next action: close `M0` and authorize `GATE 0 — FOUNDATION`.

Result: `BLOCKED`, not `PASS`. The five `CP-0009` findings are closed and both positive paths are
executed, but a milestone verdict requires an independent audit checkpoint that this run may not
author. `milestone_status.py` says so from the repository rather than from a claim here.

No Gate 0 implementation was started, and no attestation was written.

## Validation of this checkpoint after sealing

`seal_checkpoint.py` validates the committed content with a clean worktree and records that run as
`post-commit-validation` before creating the canonical tag. A commit cannot contain a validation of
itself, so the final confirmation is reported in this delivery's closing response and will be
anchored by this checkpoint's successor — which, under the corrected model, is the audit checkpoint
that judges it.
