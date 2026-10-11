# Baseline — GATE-4-CP-0003

## Proven predecessor

- `GATE-4-CP-0002` is sealed and published at
  `a3a12a84480a84be61d3e445001c923379a70cdc`.
- Local `main`, `origin/main`, the canonical checkpoint tag, and `STATE.json` agreed before this
  checkpoint was created; the worktree was clean.
- `validate_checkpoint.py` returned `CHECKPOINT_VALID` for the predecessor.
- The predecessor's independent verdict is `REWORK_REQUIRED`; Gate 4, M2, and Gate 5 remain
  unadvanced.

## Observable pre-change state

- `python scripts/iacode/verify.py --keep-going --report
  var/gate4-cp-0003-prechange-baseline.json` returned `VERIFY=PASS 42/42 stages in 3754.7s`.
- The baseline includes the real Quality Engine PASS, FAIL, IACode, reproduction, recovery,
  cancellation, and timeout scenarios; the existing internal false-PASS battery defended 10/10.
- The independent audit's `G4-X7` attack remains reproducible: serialized credential-shaped output
  can reach durable evidence before the repository scanner sees it.
- The first requirement derivation attempt was correctly refused because the sealed independent
  review renders its single finding as prose under `## Blocking finding`, a shape the canonical
  parser did not yet recognize. The refusal is recorded as `cmd-0003`; the sealed predecessor will
  not be rewritten.

## Corrective boundary

This checkpoint may close only `G4-F-001`, `G4-X7`, and the corresponding canonical requirement
`GATE-4#19.2`, together with the smallest ledger compatibility change needed to consume the sealed
audit report. It may not grant `GATE_PASS`, approve M2, or start Gate 5.
