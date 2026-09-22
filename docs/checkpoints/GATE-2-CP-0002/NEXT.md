# Next

## Required next action

GATE 2 is closed at `INTERNAL_GATE_PASS`. The next Gate is **GATE 3 — SANDBOX**, and it does not
start without the owner's explicit authorization. Nothing of it exists in this change: no executor,
no shell, no filesystem tool, no Git tool, and no GATE 3 checkpoint.

When the owner authorizes it, the first steps are the GATE 3 checkpoint and its lesson preflight:

```bash
python scripts/development-ledger/new_checkpoint.py --gate GATE-3
```

```bash
python scripts/development-ledger/lesson_preflight.py --gate GATE-3 --scope "sandbox" --write
```

## What must not happen

**GATE 3 does not start on this checkpoint's authority.** The sandbox is reserved,
`services/sandbox/` holds its README and nothing else, and `ADR-0021` states where the executor
belongs.

**`M1` stays `PENDING`.** The milestone is audited after GATE 3, by a fresh session. The internal
mirror and the internal Red Team in this checkpoint are the delivery's own controls and do not
become that audit.

**The live evidence names OpenAI because the operator chose it.** Pointing the smoke back at
DevWorld, or at any other model, is again the operator's decision; the previous DevWorld values are
kept beside the current ones in the ignored local configuration.

**No route gains a candidate by default.** The automatic fallback the gateway can already perform
needs a route with candidates, and GATE 1 row 7.8 keeps every route empty until a preference has
been measured. Changing that is a decision of its own, not a side effect.

**A sealed checkpoint is closed by its successor.** Do not edit a checkpoint after its tag; open
the next one.
