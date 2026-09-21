# Resume Validation

## Clean cold start

This delivery began from the repository alone. `START-HERE.md` resolved the phase, the Gate, the
mandatory delivery order and `docs/checkpoints/LATEST.md`; `LATEST.md` named `SETUP-00-CP-0011`;
that checkpoint's `HANDOFF.md` carried the validation commands and `NEXT.md` the corrective
protocol. The finding was taken from the sealed `REVIEW-REPORT.md` of that checkpoint and
reproduced by execution before anything was changed:

```text
python scripts/development-ledger/m0_mirror_audit.py --checkpoint docs/checkpoints/SETUP-00-CP-0011
[MIR-002] FAIL Audit findings: 0/0 audit findings CLOSED
[MIR-003] FAIL Mandatory attacks: 0/0 mandatory attacks defended; 37/37 overall
INTERNAL_MIRROR=FAIL
```

No external description of the finding was used as evidence anywhere.

## Clean clone execution

A clone of the repository, brought up to the content this checkpoint seals, with no workspace state.
Everything below ran inside it.

| Check | Exit | Observed |
|---|---|---|
| `python -m unittest discover -s tests` | 0 | four hundred and ten run, zero failures, zero errors, zero skips |
| `python -m compileall -q scripts tests` | 0 | no output |
| `validate_lessons.py` | 0 | `LESSONS_VALID total=31 active=31 guarded=29` |
| `verify_integrity.py` | 0 | `INTEGRITY_VALID anchors=11 latest=SETUP-00-CP-0011` |
| `derive_counts.py` | 0 | every derived count matches the stored derivation |
| `check_completeness.py` | 0 | `DELIVERY_COMPLETENESS_GATE=PASS` with total coverage and total evidence coverage |
| `derive_requirements.py` | 0 | the expected set re-derives to the declared anchored set |
| `milestone_status.py --milestone M0` | 1 | `MILESTONE_NOT_PASSED`; the only attestation in the repository is the CP-0011 audit's own, which records `REWORK_REQUIRED`. That is the honest state of the milestone before the audit of this delivery exists, not a failure of this delivery |
| `promotion_simulation.py` | 0 | `POSITIVE_PROMOTION=PASS verdict=PASSED checks=9 of 9` |
| `successor_durability.py` | 0 | `SUCCESSOR_DURABILITY=PASS checks=8 of 8` |
| `mirror_semantics_validation.py` | 0 | `MIRROR_SEMANTICS=PASS states=6 of 6` |
| `gate_transition_simulation.py` | 0 | `GATE_TRANSITION=PASS checks=9 of 9 status=READY_FOR_REVIEW` |
| `affected_red_team.py` | 0 | `AFFECTED_RED_TEAM=DEFENDED`, with the additional attacks that were not re-executed named individually |
| `m0_mirror_audit.py` | 0 | `INTERNAL_MIRROR=PASS` |
| `audit-harness/final_internal_audit.py` | 0 | `FINAL_INTERNAL_AUDIT=PASS` |

Two of these exited nonzero in an earlier pass of the same clean clone and were repaired rather than
explained away: the derived test count still described the suite as it was before the last four
regression cases were added, and the internal audit refused a checkpoint whose status had not yet
been set to `READY_FOR_REVIEW`. Both were re-run after the repair and are recorded here at their
final result, and the intermediate runs stay in `COMMANDS.jsonl`.

## Validation of the sealed content

A commit cannot contain a validation of itself, so the sealed content is validated post-commit by
`seal_checkpoint.py`, whose record is in `COMMANDS.jsonl` as `post-commit-validation` bound to the
commit it judged. A reader validates the same content from a detached checkout of
`refs/tags/iacode-checkpoints/SETUP-00-CP-0012`, which is the procedure in
`docs/HANDOFF-PROTOCOL.md`.

## Second-tool validation

`SECOND_TOOL_VALIDATION = PENDING_MANUAL`. The implementing run records no independent verdict. The
next fresh-session independent `M0` audit records it in its own checkpoint, about this one as a
sealed subject.
