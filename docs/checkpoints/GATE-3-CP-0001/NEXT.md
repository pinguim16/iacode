# Next

## Required next action

GATE 3 is closed at `INTERNAL_GATE_PASS`, and with it every Gate of `M1`. The milestone is **ready
for its audit**: `M1 FRESH-SESSION MILESTONE AUDIT`, in a new session that did not implement it. That
audit judges the sealed subjects — `GATE-0-CP-0001` to `GATE-3-CP-0001` — and writes its verdict
into an audit checkpoint of its own; this checkpoint is never rewritten to become approved.

In `STATE.json` the milestone reads `PENDING`, the vocabulary's word for a milestone whose audit has
not happened (`DECISIONS.md` D-12).

Before the audit starts, from a clean clone:

```bash
python scripts/development-ledger/validate_checkpoint.py
```

```bash
python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0001
```

## What must not happen

**GATE 4 does not start.** The quality engine is reserved (`services/evaluator/` holds its README
and nothing else), and it waits for the milestone audit and the owner's authorization.

**This run does not audit itself.** The internal mirror and the internal Red Team in this
checkpoint are the delivery's own controls; they do not become the milestone audit, and
`MILESTONE_INDEPENDENT_AUDIT_PASS` or `MILESTONE_EXTERNAL_PASS` is written only by the audit that
earns it.

**Published history is not rewritten.** No amend, rebase, reset or force push of `origin/main`, and
no moved tag; a correction is a new commit.

**A sealed checkpoint is closed by its successor.** Do not edit this checkpoint after its tag;
open the next one.
