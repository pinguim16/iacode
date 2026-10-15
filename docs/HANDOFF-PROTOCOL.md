# Handoff Protocol

## Mandatory delivery order

`lesson preflight` → `requirement derivation` → `baseline` → `plan` → `implementation` →
`test and quality` → `Green Keeper` → `Delivery Completeness Validator` → `internal Red Team` →
`Milestone Closure Auditor` → `INTERNAL_GATE_PASS` for an intermediate Gate, or `READY_FOR_REVIEW`
for independent handoff. At milestone closure, separate `independent tool review` → `Red Team` →
attestation-derived milestone verdict follow before the next milestone. No internal step may be skipped.
The independent tool receives a delivery that has already passed
the internal controls; it is not the first line of defense against a red test, a forgotten
requirement or an escaped attack.

## Before changing tools

1. Run the Green Keeper until every mandatory gate is green, or declare `BLOCKED`.
2. Run the Delivery Completeness Validator until coverage is total.
3. Run the internal Red Team until every mandatory attack is defended.
4. Run the Milestone Closure Auditor until every mirrored dimension passes.
5. Finalize the checkpoint.
6. Commit the content, then seal it with `seal_checkpoint.py`, which validates the committed content
   with a clean worktree, records that validation, and creates the canonical tag.
7. Validate the sealed checkpoint.
8. Update `docs/checkpoints/LATEST.md` textually; do not use a symlink.
9. Complete `HANDOFF.md` and `NEXT.md`.
10. Record branch, commit semantics, and dirty state.

No Codex-to-Claude or Claude-to-Codex transition is informal.

## Receiver sequence

1. Read `START-HERE.md`.
2. Read `docs/checkpoints/LATEST.md`.
3. Read the entire named checkpoint.
4. Run `git status --short --branch`, `git branch --show-current`, and `git rev-parse HEAD`.
5. Compare observations with `STATE.json`.
6. On unexpected divergence, stop; create `DIVERGENCE.md` describing expected state, observed state, difference, and possible cause; mark the run `BLOCKED`; do not fix it silently.
7. Run the commands in the handoff's validation section.
8. Continue only after validation, starting exactly from `NEXT.md`.

The receiver must verify the handoff rather than trust it.

## Validating a sealed checkpoint from a clean clone

1. Clone the authorised remote into a new temporary directory — or, for a local check, clone this
   repository with `git clone --no-local`. A clone of the local path without it copies the object
   store, and a sealed record that depends on an object no published reference reaches then
   validates in the clone and nowhere else (`M1-F-003`,
   [ADR-0028](adr/ADR-0028-sealed-evidence-is-judged-from-the-published-history.md)).
2. Either stay on the default branch, or check out the checkpoint's canonical tag; a detached
   checkout of that tag is supported and validates as long as the worktree stays clean.
3. Run `python scripts/development-ledger/validate_checkpoint.py` and the handoff's commands.
4. Record the result in a new checkpoint. Never modify a sealed checkpoint, and never move its tag.

## Granting a Gate

An intermediate Gate may close at `INTERNAL_GATE_PASS` after all internal controls. Its independent
review and independent Red Team are `NOT_REQUIRED` for that checkpoint with the pending milestone
audit named in the justification; `secondToolValidation` stays `PENDING_MANUAL` and the milestone
stays `PENDING`. Only a sealed, validated prior internal closure and explicit next-Gate authorization
allow an advance within that milestone. The independent run owns `GATE_PASS` and all milestone audit
verdicts. It judges a sealed subject and never rewrites the subject into approval.


## Milestone handoff

An intermediate Gate hands off internally and closes at `INTERNAL_GATE_PASS`. The Gate that closes a
milestone produces a milestone checkpoint consolidating the whole group: the Gates included, the
lessons produced, open risks, architecture changes, all tests, the regression position, cross-Gate
integration, requirements completeness, outstanding debt, provenance, and cost and model usage. That
checkpoint is what the external auditor receives, and it is the only handoff that asks for an
independent verdict. See [MILESTONE-VALIDATION.md](MILESTONE-VALIDATION.md).
