# Engineering Ledger Checkpoints

Checkpoints are reconstructible, versioned snapshots. `LATEST.md` textually identifies the checkpoint to validate; it is intentionally not a symlink for Windows compatibility.

Never trust a checkpoint only because it is named here. Run:

```text
python scripts/development-ledger/validate_checkpoint.py
```

Then compare Git state and execute the named checkpoint's handoff validation commands. Creation, validation, finalization, status rules, event triggers, and symbolic commit semantics are defined in `docs/CHECKPOINT-PROTOCOL.md`.

