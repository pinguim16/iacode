# Resume Validation

## Clean cold start

This audit began from the repository alone. `START-HERE.md` resolved the phase, the Gate, the
delivery order and `docs/checkpoints/LATEST.md`; `LATEST.md` named `SETUP-00-CP-0010`; that
checkpoint's `HANDOFF.md` carried the reproduction commands and `NEXT.md` the audit protocol, and
`CP9-FINDINGS-CLOSURE.md` carried the per-finding acceptance criteria. The sealed
`SETUP-00-CP-0009` review report was re-read for the original findings rather than taken from the
closure record. No external summary of the subject was used as evidence anywhere.

## Clean clone execution

A clone of the repository, detached at `refs/tags/iacode-checkpoints/SETUP-00-CP-0010`, resolved to
`90b67a7e0a11179465bc5c92dee22c78da36801f` with a clean worktree. Everything below ran inside it,
with no workspace state.

| Check | Exit | Observed |
|---|---|---|
| `validate_checkpoint.py` | 0 | `CHECKPOINT_VALID` |
| `validate_lessons.py` | 0 | `LESSONS_VALID total=30 active=30 guarded=28` |
| `verify_integrity.py` | 0 | `INTEGRITY_VALID anchors=9 latest=SETUP-00-CP-0009` |
| `derive_counts.py` | 0 | every derived count matches the stored derivation |
| `check_completeness.py` | 0 | `DELIVERY_COMPLETENESS_GATE=PASS` with total coverage |
| `derive_requirements.py` | 0 | the expected set re-derives to the declared set |
| `milestone_status.py --milestone M0` | 1 | `MILESTONE_NOT_PASSED`, the honest state of the subject before this audit wrote its attestation |
| `promotion_simulation.py` | 0 | `POSITIVE_PROMOTION=PASS verdict=PASSED` |
| `successor_durability.py` | 0 | `SUCCESSOR_DURABILITY=PASS` |
| `affected_red_team.py` | 0 | `AFFECTED_RED_TEAM=DEFENDED` |
| `m0_red_team.py` | 0 | `INTERNAL_RED_TEAM=RED_TEAM_PASS` |
| `m0_mirror_audit.py --clean-clone` | 0 | `INTERNAL_MIRROR=PASS` |
| `compileall -q scripts tests` | 0 | no output |
| `git diff --check <base> HEAD` | 0 | no whitespace error in the audited change set |
| `python -m unittest discover -s tests` | 0 | three hundred and sixty-three run, zero failures, zero errors, one conditional skip |

The single conditional skip in the clean clone is
`AuditAttestationModelTests.test_an_unsealed_subject_is_rejected`, whose own guard states that every
checkpoint directory in a fully sealed checkout is sealed, so the case has no subject to exercise.
It is recorded as an observation rather than as a failure, and the same suite runs with no skip in a
checkout that contains an unsealed checkpoint.

## Historical checkpoints from their own tags

Each of the ten sealed checkpoints was checked out detached at its own canonical tag and validated
with the current tooling. All ten exited zero. Running each checkpoint's own era of the tooling
instead refuses the two `1.0.0` checkpoints with a branch mismatch, because detached validation did
not exist then; that is a property of the old tooling rather than of the sealed content, which is
why the compatibility question is asked of the current validator.

## Truthful blocked continuation

Attempted next action: close `M0` at `MILESTONE_INDEPENDENT_AUDIT_PASS` and authorize
`GATE 0 — FOUNDATION`, which is what the subject's `NEXT.md` instructs.

Result: `REWORK_REQUIRED`, not `PASS`. This checkpoint anchored the sealed subject and wrote
`.iacode/attestations/M0-CP-0011.json` about it, and the promotion architecture works: in a sealed
snapshot of this checkpoint carrying the four results a pass requires, `validate_checkpoint.py`
exits zero and `milestone_status.py --milestone M0` prints `MILESTONE_PASSED`. The status could not
be recorded here for a different reason, `CP11-F-001`: the internal mirror audit reports `FAIL` for
any checkpoint that corrects no audit, and checkpoint validation requires it to pass. The
attestation therefore records the real verdict, and the derivation refuses to promote on it:

```text
MILESTONE_NOT_PASSED milestone=M0 attestations=1 accepted=0
- REJECTED .iacode/attestations/M0-CP-0011.json: reviewResult is 'REWORK_REQUIRED'
```

No Gate 0 implementation was started and no product code was changed.

## Validation of this checkpoint after sealing

`seal_checkpoint.py` validates the committed content with a clean worktree and records that run as
`post-commit-validation` before creating the canonical tag. A commit cannot contain a validation of
itself, so the final confirmation is reported in this audit's closing response, and it is anchored by
this checkpoint's successor. After sealing, the audit additionally validated this checkpoint from a
clean detached checkout of its canonical tag and re-derived the milestone verdict there; both
results are reported in the closing response with their exit codes.
