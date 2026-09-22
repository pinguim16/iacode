# Next

## Required next action

`REQUEST EXPLICIT AUTHORIZATION TO OPEN GATE 1 — MODEL GATEWAY`.

`GATE 0 — FOUNDATION` is closed at `INTERNAL_GATE_PASS`: the project's own controls passed. That is
not an independent verdict and is not described as one. `M1` covers Gates 0 to 3 and is audited
after Gate 3, so no audit is due here and none was requested.

Gate 1 is `AUTHORIZED` in the sense that its predecessor has closed. It is **not** started, and it
may not be started inside this checkpoint. Opening it requires the owner's explicit authorization
and a new pre-Gate checkpoint of its own.

No Gate 1 work exists in this change set and none was begun.

## What the next run receives

- A Foundation that runs: an API, a Temporal worker, a web shell, PostgreSQL with pgvector, Redis,
  MinIO, Temporal, Prometheus and Grafana, from `python scripts/iacode/stack.py up`.
- A persistence contract with the structural tables later Gates record into, so Gate 1 adds rows to
  `providers`, `models` and `model_calls` rather than adding tables.
- One command that verifies the whole Gate, reading the mandatory gate set from policy:
  `python scripts/iacode/verify.py`.
- Four control-plane controls generalised so that a Gate other than SETUP-00 can be delivered at
  all. `DECISIONS.md` records each one and why it is broader rather than weaker.
- Four new lessons and one recorded `GUARDRAIL_FAILURE`, each with an automated control.
- `RISKS.md`: nine risks carried into `M1`, each with the condition that turns it into a defect.

## The first deliverable of Gate 1

`.iacode/policies/canonical-requirements.json` declares no requirements for `GATE-1`. Authoring that
specification is the **first** deliverable of that Gate: the expected requirement set of its first
delivery comes from that file, from the lesson preflight, and from the open audit findings, of which
it will have none.

`docs/GATE-0-CHECKLIST.md` is the worked example of the shape, and the derivation is already
Gate-agnostic — `policies.gate_specification` reads the path from the registry, so Gate 1 declares
its document and derives.

## How to open Gate 1, when it is authorised

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`,
   `docs/DEFINITION-OF-DONE.md`, `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`,
   `docs/checkpoints/LATEST.md` and this complete checkpoint.
2. Read `docs/ARCHITECTURE.md` and `docs/runbooks/FOUNDATION.md`, then **start the stack and run
   `python scripts/iacode/smoke.py`**. The Foundation is the thing Gate 1 builds on; confirm it runs
   before changing it.
3. Run `python scripts/development-ledger/validate_checkpoint.py` and the commands in `HANDOFF.md`.
4. Run `python scripts/development-ledger/lesson_preflight.py --gate GATE-1 --scope <scope> --write`
   before any Gate 1 work, and carry every derived `LESSON-REQ-` requirement into the matrix.
5. Author the canonical `GATE 1` requirement specification, add it to
   `.iacode/policies/canonical-requirements.json`, then derive with
   `python scripts/development-ledger/derive_requirements.py --write`.
6. Follow the mandatory delivery order without skipping a step, and close the first Gate 1 delivery
   at `INTERNAL_GATE_PASS`.

## What Gate 1 should know about this Gate's boundaries

- `services/model-gateway/` is reserved for it and holds a README and nothing else.
  `.iacode/policies/gate-scope.json` records the reservation; the scope control fails a delivery
  that fills it early, and it stops constraining Gate 1 because Gate 1 owns it.
- `providers`, `models` and `model_calls` exist with identity and capability columns only. Routing
  and pricing are Gate 1's to design; `model_calls` stores no prompt or completion, because that is
  a rights decision `.iacode/policies/training-data-policy.md` governs.
- Credentials are never persisted. Gate 1 resolves a provider credential from configuration, and
  `test_no_table_stores_a_credential` keeps that true.
- A new configuration key must be read by the implementation.
  `test_every_declared_key_is_read_somewhere` fails on one that is not.
- Adding a mandatory gate means adding it to `.iacode/policies/quality-gates.json`. The verification
  reads that registry, so a new gate is covered immediately, and it must be runnable without the
  whole stack up.

## What must not happen

- Do not rewrite, re-tag or re-seal this checkpoint or any sealed predecessor.
- Do not begin Gate 1 without explicit authorization and its own pre-Gate checkpoint.
- Do not describe `INTERNAL_GATE_PASS` as independent validation. It is the project's own verdict;
  `M1` has not been audited and will not be until Gate 3 closes.
- Do not weaken a control to make a delivery pass. Four were generalised here; each became broader,
  and each is covered by a test and an attack.

## Next Gate

`GATE 1 — MODEL GATEWAY`: `AUTHORIZED`, not started. Its milestone is `M1`, which it does not close,
so it will end at `INTERNAL_GATE_PASS` rather than at a milestone verdict.
