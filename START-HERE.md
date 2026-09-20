# Start Here

IACode is a planned private, autonomous, general-purpose software engineering platform. The repository is self-contained context and is the only source of truth.

- Phase: `SETUP-00 — Development Control Plane`.
- Current Gate: `SETUP-00`.
- Latest checkpoint: follow [docs/checkpoints/LATEST.md](docs/checkpoints/LATEST.md).
- Gate 0 is not implemented and may not begin until SETUP-00 is `GATE_PASS`.

## Required start protocol

1. Read [docs/DEVELOPMENT-CONTRACT.md](docs/DEVELOPMENT-CONTRACT.md).
2. Read [docs/MASTER-PLAN.md](docs/MASTER-PLAN.md) and, for this Gate, [docs/SETUP-00-CHECKLIST.md](docs/SETUP-00-CHECKLIST.md).
3. Read [docs/checkpoints/LATEST.md](docs/checkpoints/LATEST.md) and every file in the checkpoint it names.
4. Run `python scripts/development-ledger/validate_checkpoint.py`.
5. Run `git status --short --branch`, `git branch --show-current`, and `git rev-parse HEAD`.
6. Compare the observed Git state with `STATE.json`; if an unexpected divergence exists, stop and create `DIVERGENCE.md` as specified by the [checkpoint protocol](docs/CHECKPOINT-PROTOCOL.md).
7. Execute the validation commands in `HANDOFF.md`.
8. Continue only from `NEXT.md` and do not advance a Gate without explicit authorization and a passing prior Gate.

## Mandatory delivery order

Every delivery runs, in order: requirement extraction into `REQUIREMENTS-MATRIX.json`, baseline,
plan, implementation, test and quality execution, [Test Rework / Green Keeper](.iacode/agents/test-rework-greenkeeper.md),
[Delivery Completeness Validator](.iacode/agents/delivery-completeness-validator.md),
`READY_FOR_REVIEW`, independent tool review, Red Team, and only then `GATE_PASS`. No step may be
skipped, and nothing red or incomplete is handed to the independent tool.

See the [Master Plan](docs/MASTER-PLAN.md), the [Quality Gates](docs/QUALITY-GATES.md), and the
[Handoff Protocol](docs/HANDOFF-PROTOCOL.md).


## Engineering memory and validation cadence

Before a Gate starts, run the mandatory lesson preflight; every applicable lesson in
[.iacode/memory/](.iacode/memory/README.md) becomes a requirement of that Gate. Confirmed failures
become lessons, and important lessons become automated guardrails rather than prose. See
[docs/ENGINEERING-MEMORY.md](docs/ENGINEERING-MEMORY.md).

An intermediate Gate closes at `INTERNAL_GATE_PASS` on the project's own controls. Independent
external validation happens once per milestone and produces `MILESTONE_EXTERNAL_PASS`; an internal
verdict is never described as an external one. See
[docs/MILESTONE-VALIDATION.md](docs/MILESTONE-VALIDATION.md).
