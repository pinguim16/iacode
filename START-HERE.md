# Start Here

IACode is a planned private, autonomous, general-purpose software engineering platform. The repository is self-contained context and is the only source of truth.

- Phase: `M1 — IACode V0 foundation`.
- Current Gate: `GATE 3 — SANDBOX + TOOL EXECUTION`, the last Gate of `M1`, closing at
  `INTERNAL_GATE_PASS`.
- Previous Gates: `GATE 2 — AGENT RUNTIME`, `GATE 1 — MODEL GATEWAY` and
  `GATE 0 — FOUNDATION`, all closed at `INTERNAL_GATE_PASS`; before them `SETUP-00`, closed,
  with `M0` having passed its independent audit.
- Latest checkpoint: follow [docs/checkpoints/LATEST.md](docs/checkpoints/LATEST.md).
- `M1` is `READY_FOR_MILESTONE_AUDIT` once this Gate closes. Its verdict belongs to a
  fresh-session milestone audit, never to this Gate; `GATE 4` does not begin before it.
- **A tool an agent asks for runs only inside a sandbox**: a disposable container that belongs to
  the run, with no network, no host path, no engine socket and no credential. Nothing an agent
  asks for runs on the host, in the API, in the worker or in the sandbox service's own process.
- The development history is public at `pinguim16/iacode`: atomic commits, pushed while green,
  never rewritten once pushed, with every push preceded by a secret scan of what it carries.

The runtime runs locally. To start it, read [docs/runbooks/FOUNDATION.md](docs/runbooks/FOUNDATION.md);
to configure and operate a model provider, read
[docs/runbooks/MODEL-GATEWAY.md](docs/runbooks/MODEL-GATEWAY.md); to run and follow an
agent, read [docs/runbooks/AGENT-RUNTIME.md](docs/runbooks/AGENT-RUNTIME.md); to see how its
tools execute and what bounds them, read [docs/runbooks/SANDBOX.md](docs/runbooks/SANDBOX.md);
to work on it, read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md). Neither replaces the start protocol
below for anyone about to change the repository.

## Required start protocol

1. Read [docs/DEVELOPMENT-CONTRACT.md](docs/DEVELOPMENT-CONTRACT.md).
2. Read [docs/MASTER-PLAN.md](docs/MASTER-PLAN.md) and the canonical specification of the current
   Gate: [docs/GATE-3-CHECKLIST.md](docs/GATE-3-CHECKLIST.md) now,
   [docs/GATE-2-CHECKLIST.md](docs/GATE-2-CHECKLIST.md),
   [docs/GATE-1-CHECKLIST.md](docs/GATE-1-CHECKLIST.md),
   [docs/GATE-0-CHECKLIST.md](docs/GATE-0-CHECKLIST.md) and
   [docs/SETUP-00-CHECKLIST.md](docs/SETUP-00-CHECKLIST.md) for the Gates before it.
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
