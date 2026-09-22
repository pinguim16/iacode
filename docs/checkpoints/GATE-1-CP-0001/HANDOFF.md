# Handoff

Current Gate: GATE-1
Current Status: INTERNAL_GATE_PASS

Last valid commit: recorded in `STATE.json` after sealing.
Current branch: main

## Objective

Deliver the Model Gateway: one provider-neutral boundary for invoking a model, with the catalog
discovered from each provider's own API, a deterministic router, real inference and real streaming,
resilience policies that are proved rather than described, an operational record that carries no
prompt, and a credential that exists only in the environment.

## What was completed

Everything `docs/GATE-1-CHECKLIST.md` specifies, 122 rows, plus the 37 requirements the lesson
preflight derived. `REQUIREMENTS-MATRIX.json` carries each one with resolvable evidence and
`COMPLETENESS-REPORT.json` records total coverage.

The live provider integration ran. `scripts/iacode/gateway_smoke.py` reports `PASS` on twenty
checks against the configured DevWorld provider: catalog discovery, a repeated synchronisation that
changed nothing, the smoke model's presence, normalisation, a non-streaming inference, attribution,
latency, usage, an absent rather than invented cost, a streaming inference with no duplication, the
persisted record and its lack of a prompt, and a Prometheus query proving the observability stack
saw it.

## What was NOT completed

Nothing inside this Gate. Nothing reserved for a later Gate was started:
`.iacode/policies/gate-scope.json` declares which path belongs to which Gate, and the scope control
is derived from the checkpoint rather than from a literal.

`M1` remains `PENDING`. It is audited after Gate 3, and no independent, fresh-session or cross-tool
verdict is claimed by this run.

## Current repository state

See `STATE.json`.

## Files changed

See `FILES.json`. The declaration is the author's; the hashes are bound by
`finalize_checkpoint.py`.

## Important decisions

See `DECISIONS.md`, and `ADR-0016` through `ADR-0019` for the structural ones.

## Tests executed

See `TESTS.json` and `VERIFICATION-REPORT.json`.

| Suite | Cases |
|---|---|
| Control plane (`python -m unittest discover -s tests`) | 477 |
| Backend and gateway (`pytest` inside the API image, against the running stack) | 354 |
| Infrastructure (`python -m unittest discover -s infra/tests`) | 48 |
| Frontend (Vitest, inside the toolchain image) | 30 |

## Known failures

None. Every mandatory gate is green and `REWORK-LOG.jsonl` records the cycles, including the red
one.

## Known risks

See `RISKS.md`.

## Do not repeat

- **Do not measure inside an image without building it first.** A gate that does reports on source
  that is not in the repository. `compose.build_service` exists for this and a control-plane test
  enforces it.
- **Do not write a Gate identifier into a shared control.** Derive it with
  `ledger_common.delivered_gate`.
- **Do not let a test write to the stack's database without removing what it wrote.** The catalog
  is operator-visible.
- **Do not put a credential anywhere but `infra/compose/.env`.** The policy files name variables.
- **Do not ask for a secret in a chat and do not put one in a report.**

## Required next action

Obtain explicit authorization for `GATE 2 — AGENT RUNTIME` and create its pre-Gate checkpoint. No
Gate 2 work exists in this change set.

## Exact continuation sequence

```bash
python scripts/development-ledger/validate_checkpoint.py
python scripts/development-ledger/verify_integrity.py
python scripts/iacode/stack.py up
python scripts/iacode/gateway_smoke.py
python scripts/iacode/verify.py --fast
```

The smoke check needs `IACODE_DEVWORLD_BASE_URL`, `IACODE_DEVWORLD_API_KEY` and
`IACODE_GATEWAY_SMOKE_MODEL` in `infra/compose/.env`, which Git ignores. Without them it exits
`BLOCKED` (code `2`) and names the variable that is missing. It never degrades into a `PASS`.

## Validation commands

```bash
python scripts/development-ledger/validate_checkpoint.py
python scripts/development-ledger/validate_lessons.py
python scripts/development-ledger/verify_integrity.py
python scripts/development-ledger/check_completeness.py
python -m unittest discover -s tests
```

## Stop conditions

Stop and record a divergence rather than repairing silently when: the observed Git state disagrees
with `STATE.json`; a mandatory gate is red; the completeness audit is below total coverage; a
credential appears anywhere outside `infra/compose/.env`; the live smoke reports anything other
than `PASS` or a `BLOCKED` naming a variable; or a sealed checkpoint fails to validate.
