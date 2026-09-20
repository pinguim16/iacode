# Development Contract

## Completion standard

A partial feature is not complete. Functional placeholders, production fakes, fixed-response endpoints, empty error handling, hidden suppressions, skipped validation, removed correct tests, and modified tests that conceal defects are prohibited. Completion requires implementation, execution, testing, measurement where relevant, and documentation.

## Mandatory controls

- Establish and record a baseline before changes.
- Write and execute tests appropriate to the change; `NOT_EXECUTED` never means PASS.
- Log relevant sanitized commands, exit codes, durations, artifacts, failures, attempts, and corrections.
- Keep documentation and the Engineering Ledger current.
- Never store secrets, credentials, private keys, or authentication values.
- Create checkpoints at the events listed in `CHECKPOINT-PROTOCOL.md`.
- Require review independent of the implementer and an adversarial Red Team before Gate PASS.
- Meet `DEFINITION-OF-DONE.md` and the Gate's acceptance criteria.

## Mandatory delivery order

Every delivery follows this sequence. Skipping a step is a contract violation, not a shortcut.

1. Requirement extraction into `REQUIREMENTS-MATRIX.json`.
2. Baseline.
3. Plan.
4. Implementation.
5. Test and quality execution.
6. Test Rework / Green Keeper.
7. Delivery Completeness Validator.
8. `READY_FOR_REVIEW`.
9. Independent tool review.
10. Red Team.
11. `GATE_PASS`.

Steps 6 and 7 exist so the independent tool never has to discover an unimplemented requirement, a
forgotten prompt item, missing documentation, a red test, a red quality gate, a partial artifact, or
absent evidence. The Green Keeper may change code; the Delivery Completeness Validator may not.
Their contracts are `.iacode/agents/test-rework-greenkeeper.md` and
`.iacode/agents/delivery-completeness-validator.md`.

Nothing red ships. A requirement that cannot be finished, or a gate that cannot be repaired inside
the repository, produces `BLOCKED` with the blocker named, never `READY_FOR_REVIEW`.

## Git discipline

Do not force push, hard reset, destructively clean, or rewrite history without explicit authorization and a validated checkpoint immediately before the operation. Do not mix Gates in a commit. Prefer clear prefixes: `setup:`, `gate0:`, `gate1:`, `fix:`, `test:`, `docs:`, and `refactor:`.

## Gate discipline

The previous Gate is mandatory. A Gate may advance only when it is `GATE_PASS` and the next Gate is explicitly authorized. Blocked or failed work remains explicit; scope never changes silently.

## Evidence discipline

Assertions by an implementer are not test evidence. Record concise observable decision summaries, not private chain-of-thought. Provenance is required and training is denied by default.

