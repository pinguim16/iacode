# Diff Summary

Base: `3bc8e9d8a94d44163d1af9325ad5b2272f71f8ed` (`iacode-checkpoints/GATE-3-CP-0001`).

This audit changed no product file, no test, no policy and no governing document. Every path is
declared in `FILES.json` with its reason.

| Path | Change | Why |
|---|---|---|
| `.iacode/anchors/checkpoint-chain.json` | modified | the eighteenth anchor, for the sealed subject `GATE-3-CP-0001`, which its own checkpoint could not write |
| `.iacode/attestations/M1-CP-0002.json` | created | the attestation this audit authored about the sealed subject; the milestone verdict is derived from it |
| `docs/checkpoints/LATEST.md` | modified | points at this checkpoint |
| `docs/checkpoints/GATE-3-CP-0002/` | created | the audit checkpoint: its plan, execution record, evidence, review, Red Team, milestone report and harness |

The harness under `audit-harness/` is the audit's own code — the inventory declaration, the sealed
subject validation, the live cross-gate run, the `R-G3-001` probe, the Red Team in its two halves,
the forged-result probe, the clean clone, the requirement completion and the matrix builder. It lives
inside the checkpoint, outside the delivery-assurance scope, so running it can never change what
the gates judge.
