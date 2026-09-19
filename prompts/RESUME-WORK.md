# Resume Work

You are continuing an execution initiated by another tool.

Do not make any alteration yet.

1. Read `START-HERE.md`.
2. Read `docs/DEVELOPMENT-CONTRACT.md`.
3. Read `docs/MASTER-PLAN.md`.
4. Read `docs/checkpoints/LATEST.md`.
5. Read the entire checkpoint it identifies.
6. Run `python scripts/development-ledger/validate_checkpoint.py`.
7. Compare `git status --short --branch`, `git branch --show-current`, and `git rev-parse HEAD` with `STATE.json`.
8. Execute the validation commands from `HANDOFF.md`.
9. Confirm the real state.

If any unexpected inconsistency exists, stop, create `DIVERGENCE.md`, record expected and observed state plus possible cause, mark the run `BLOCKED`, and do not silently repair it.

After successful validation, continue exactly from `NEXT.md`, maintain the Engineering Ledger, and create or finalize a checkpoint before ending.

