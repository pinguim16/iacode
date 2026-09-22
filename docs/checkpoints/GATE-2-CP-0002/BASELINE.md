# Baseline — GATE-2-CP-0002

The state the closure starts from, observed rather than assumed.

## Predecessor

`GATE 2 — AGENT RUNTIME`, checkpoint `GATE-2-CP-0001`, status `BLOCKED`, sealed under
`refs/tags/iacode-checkpoints/GATE-2-CP-0001` at commit `424650d58167422cda08ebd580cc70fe75433668`. Its only blocker: rows 19.1,
19.2 and 19.5 need a live model call and DevWorld's quota was exhausted.

Before the closure changed anything, the observed Git state agreed with that checkpoint's
`STATE.json`: branch `main`, head `424650d58167422cda08ebd580cc70fe75433668`, and a working tree whose only extra entry was an
archive of the checkpoint the operator had made for an outside review. With the archive in place
`validate_checkpoint.py` reported the undeclared file; the operator removed it, and the sealed
checkpoint then validated: `CHECKPOINT_VALID`. `validate_lessons.py` reported
`LESSONS_VALID total=46 active=46 guarded=44` and `verify_integrity.py` reported
`INTEGRITY_VALID anchors=15`. No divergence was found, so no `DIVERGENCE.md` exists.

`M1` is `PENDING` and covers Gates 0 to 3. It is audited after GATE 3.
