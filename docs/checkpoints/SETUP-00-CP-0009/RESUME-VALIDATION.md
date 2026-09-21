# Resume Validation

## Clean cold start

This audit began with no knowledge of the run that produced `SETUP-00-CP-0008`, so the cold start
was not a formality. `START-HERE.md` resolved the phase, the Gate, the delivery order and
`docs/checkpoints/LATEST.md`; `LATEST.md` named the subject; the subject's `HANDOFF.md` carried a
reproduction recipe per control. Everything needed to audit the delivery was in the repository, and
no external summary was used as evidence anywhere.

The subject was then validated from a clone with no workspace state, detached at
`refs/tags/iacode-checkpoints/SETUP-00-CP-0008`: `CHECKPOINT_VALID`, the full suite 306/306, and all
fifteen of the handoff's validation commands green, including the delivery's own
`m0_mirror_audit.py --clean-clone` at 18/18 and `m0_red_team.py` at 46/46.

Result: the repository is operationally self-contained for cold start, and a fresh session can
reconstruct what was required, what was done, and how to check it.

## Truthful blocked continuation

Attempted next action: close `M0` and authorize `GATE 0 — FOUNDATION`.

Result: `BLOCKED`, not `PASS`. Two critical findings are open. `CP9-F-001` means the status the
milestone policy depends on has no reachable positive path, so even an approving audit could not
record `MILESTONE_EXTERNAL_PASS` through the mechanism the project built for it. `CP9-F-002` means
the mandatory suite is red in this repository right now, because anchoring the sealed predecessor is
both required of this checkpoint and fatal to a test bound to a literal checkpoint name.

No Gate 0 implementation was started, and no attestation was written.

## Validation of this checkpoint after sealing

`seal_checkpoint.py` validates the committed content with a clean worktree and records that run as
`post-commit-validation` before creating the canonical tag. The sealed checkpoint was then
re-validated from a clean clone detached at `refs/tags/iacode-checkpoints/SETUP-00-CP-0009`, which
is the read-only mode another tool uses to inspect an immutable reference. A commit cannot contain a
validation of itself, so that final confirmation is reported in the audit's closing response and
will be anchored by this checkpoint's successor, exactly as the protocol states.
