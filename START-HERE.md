# Start Here

IACode is a planned private, autonomous, general-purpose software engineering platform. The repository is self-contained context and is the only source of truth.

- Phase: `M1 — IACode V0 foundation`.
- Current Gate: `GATE 0 — FOUNDATION`.
- Previous Gate: `SETUP-00`, closed; `M0` passed its independent audit.
- Latest checkpoint: follow [docs/checkpoints/LATEST.md](docs/checkpoints/LATEST.md).
- Gate 1 is not implemented and may not begin until Gate 0 closes and Gate 1 is authorized.

The Gate 0 runtime runs locally. To start it, read [docs/runbooks/FOUNDATION.md](docs/runbooks/FOUNDATION.md);
to work on it, read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md). Neither replaces the start protocol
below for anyone about to change the repository.

## Required start protocol

1. Read [docs/DEVELOPMENT-CONTRACT.md](docs/DEVELOPMENT-CONTRACT.md).
2. Read [docs/MASTER-PLAN.md](docs/MASTER-PLAN.md) and the canonical specification of the current
   Gate: [docs/GATE-0-CHECKLIST.md](docs/GATE-0-CHECKLIST.md) now,
   [docs/SETUP-00-CHECKLIST.md](docs/SETUP-00-CHECKLIST.md) for the Gate before it.
3. Read [docs/checkpoints/LATEST.md](docs/checkpoints/LATEST.md) and every file in the checkpoint it names.
4. Run `python scripts/development-ledger/validate_checkpoint.py`.
5. Run `git status --short --branch`, `git branch --show-current`, and `git rev-parse HEAD`.
6. Compare the observed Git state with `STATE.json`; if an unexpected divergence exists, stop and create `DIVERGENCE.md` as specified by the [checkpoint protocol](docs/CHECKPOINT-PROTOCOL.md).
7. Execute the validation commands in `HANDOFF.md`.
8. Continue only from `NEXT.md` and do not advance a Gate without explicit authorization and a passing prior Gate.

## Mandatory delivery order

Every delivery runs, in order: the lesson preflight, requirement derivation into
`REQUIREMENTS-MATRIX.json`, baseline, plan, implementation, test and quality execution,
[Test Rework / Green Keeper](.iacode/agents/test-rework-greenkeeper.md),
[Delivery Completeness Validator](.iacode/agents/delivery-completeness-validator.md),
the internal Red Team, the [Milestone Closure Auditor](.iacode/agents/m0-closure-auditor.md),
`READY_FOR_REVIEW`, independent tool review, Red Team, and only then `GATE_PASS`. No step may be
skipped, and nothing red, incomplete or unattacked is handed to the independent tool.

The requirement set is derived, not transcribed: the canonical Gate checklist, the lesson preflight
and the open audit findings decide it, and a delivery that declares anything else is refused.

See the [Master Plan](docs/MASTER-PLAN.md), the [Quality Gates](docs/QUALITY-GATES.md), and the
[Handoff Protocol](docs/HANDOFF-PROTOCOL.md).


## Engineering memory and validation cadence

Before a Gate starts, run the mandatory lesson preflight; every applicable lesson in
[.iacode/memory/](.iacode/memory/README.md) becomes a requirement of that Gate. Confirmed failures
become lessons, and important lessons become automated guardrails rather than prose. See
[docs/ENGINEERING-MEMORY.md](docs/ENGINEERING-MEMORY.md).

An intermediate Gate closes at `INTERNAL_GATE_PASS` on the project's own controls. Independent
validation happens once per milestone, in a separate audit checkpoint that judges a sealed subject
and carries the verdict: `MILESTONE_INDEPENDENT_AUDIT_PASS` for a fresh-session audit,
`MILESTONE_EXTERNAL_PASS` for a cross-tool one. An internal verdict is never described as either. See
[docs/MILESTONE-VALIDATION.md](docs/MILESTONE-VALIDATION.md).
