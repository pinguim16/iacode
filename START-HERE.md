# Start Here

IACode is a planned private, autonomous, general-purpose software engineering platform. The repository is self-contained context and is the only source of truth.

- Phase: `SETUP-00 — Development Control Plane`.
- Current Gate: `SETUP-00`.
- Latest checkpoint: follow [docs/checkpoints/LATEST.md](docs/checkpoints/LATEST.md).
- Gate 0 is not implemented and may not begin until SETUP-00 is `GATE_PASS`.

## Required start protocol

1. Read [docs/DEVELOPMENT-CONTRACT.md](docs/DEVELOPMENT-CONTRACT.md).
2. Read [docs/MASTER-PLAN.md](docs/MASTER-PLAN.md).
3. Read [docs/checkpoints/LATEST.md](docs/checkpoints/LATEST.md) and every file in the checkpoint it names.
4. Run `python scripts/development-ledger/validate_checkpoint.py`.
5. Run `git status --short --branch`, `git branch --show-current`, and `git rev-parse HEAD`.
6. Compare the observed Git state with `STATE.json`; if an unexpected divergence exists, stop and create `DIVERGENCE.md` as specified by the [checkpoint protocol](docs/CHECKPOINT-PROTOCOL.md).
7. Execute the validation commands in `HANDOFF.md`.
8. Continue only from `NEXT.md` and do not advance a Gate without explicit authorization and a passing prior Gate.

See the [Master Plan](docs/MASTER-PLAN.md) and [Handoff Protocol](docs/HANDOFF-PROTOCOL.md).

