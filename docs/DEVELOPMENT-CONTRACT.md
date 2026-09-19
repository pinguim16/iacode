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

## Git discipline

Do not force push, hard reset, destructively clean, or rewrite history without explicit authorization and a validated checkpoint immediately before the operation. Do not mix Gates in a commit. Prefer clear prefixes: `setup:`, `gate0:`, `gate1:`, `fix:`, `test:`, `docs:`, and `refactor:`.

## Gate discipline

The previous Gate is mandatory. A Gate may advance only when it is `GATE_PASS` and the next Gate is explicitly authorized. Blocked or failed work remains explicit; scope never changes silently.

## Evidence discipline

Assertions by an implementer are not test evidence. Record concise observable decision summaries, not private chain-of-thought. Provenance is required and training is denied by default.

