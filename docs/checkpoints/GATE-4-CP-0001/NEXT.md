# Next

## Required next action

Perform a later independent Gate 4 review of the sealed `GATE-4-CP-0001` subject in a new
checkpoint, expected to be `GATE-4-CP-0002`.

The reviewer must treat this checkpoint and its canonical tag as immutable, reproduce the required
quality-engine and cross-Gate evidence from a clean published checkout, independently examine the
194-requirement denominator, and attack the false-PASS boundary. Only that later run may populate
`secondToolValidation`, record the independent Red Team verdict, and decide `GATE_PASS`.

Before opening the review, from a clean checkout:

```powershell
python scripts/development-ledger/validate_checkpoint.py
python scripts/development-ledger/verify_integrity.py
python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-4-CP-0001
```

Do not begin Gate 5 until Gate 4 has an independent `GATE_PASS` and the owner explicitly authorizes
the next Gate.
