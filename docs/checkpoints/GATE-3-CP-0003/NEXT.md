# Next

## Required next action

**A new fresh-session `M1` audit** of the corrected milestone, in its own audit checkpoint
(`GATE-3-CP-0004`), by a session with no memory of this one. `M1` is **not passed**: this
checkpoint is an implementing delivery closed at `READY_FOR_REVIEW`, and the milestone verdict
belongs to an audit attestation about a sealed subject — this checkpoint, sealed under
`refs/tags/iacode-checkpoints/GATE-3-CP-0003`.

The audit should, at least:

1. anchor this sealed checkpoint in `.iacode/anchors/checkpoint-chain.json`;
2. clone the **remote** (`https://github.com/pinguim16/iacode.git`) over its transport and run the
   full verification there — the control that failed for `M1-F-003`;
3. validate every sealed `M1` checkpoint, this one included, from that clone;
4. confirm the three findings closed (`M1-FINDINGS-CLOSURE.json`), attacking each independently:
   a forged tool result for a sandboxed request, a sealed record naming an unpublished commit, and
   a live run of the configured model;
5. record its own attestation; `milestone_status.py --milestone M1` derives the verdict from it.

The audit harness of `GATE-3-CP-0002/audit-harness/` re-runs against a new subject; this
checkpoint's `delivery-harness/` holds the published-history, live-run and clean-clone probes.

Before anything, from a clean checkout:

```bash
python scripts/development-ledger/validate_checkpoint.py
```

```bash
python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0003
```

```bash
python scripts/development-ledger/milestone_status.py --milestone M1
```

The last one must report `MILESTONE_NOT_PASSED`: the only attestation is `M1-CP-0002`, whose
verdict is `REWORK_REQUIRED`.

## What must not happen

**`GATE 4` is not started** before `M1` passes a fresh-session audit and the owner authorises it.

**This checkpoint is not rewritten to fit the audit.** A correction is a later checkpoint.

**Published history is not rewritten**, and no tag is moved or deleted — the three
`refs/tags/iacode-preserved/` tags included: each is what keeps a sealed record verifiable.

**The owner rotates the credential of `R-G2-009`** outside the repository; no run asks for it.
