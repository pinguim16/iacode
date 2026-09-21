# Diff Summary — SETUP-00-CP-0009

Base: `c53f4c59a77870414324efa6b5f61b35d26c5090` / `refs/tags/iacode-checkpoints/SETUP-00-CP-0008`.

## Created

Everything under `docs/checkpoints/SETUP-00-CP-0009/`, which is this audit's own checkpoint: the
183-row audit matrix, the review, Red Team and milestone reports, the executions record, the lesson
candidates, the requirement and closure matrices, the ledger, and `audit-harness/`, the eighteen
scripts that produced every recorded result and that reproduce from a clean clone.

## Modified

- `docs/checkpoints/LATEST.md` — points at this checkpoint, as every checkpoint does.
- `.iacode/anchors/checkpoint-chain.json` — extended with the eighth anchor, over the sealed tag,
  commit and tree of `SETUP-00-CP-0008`. A checkpoint cannot anchor its own tag, so its successor
  owes it this; `verify_integrity.py --rebuild` derived it from Git and nothing was written by hand.

## Not modified

No product script, test, schema, policy, canonical memory file, guardrail registry entry, sealed
checkpoint or historical tag. No attestation was written. No Gate 0 work exists in this change set.
