# Quality Gates

## Canonical outcomes

Quality checks use only `PASS`, `FAIL`, `NOT_APPLICABLE`, or `NOT_EXECUTED`. Gate state uses only the statuses defined by `CHECKPOINT-PROTOCOL.md`.

## Required dimensions

Every Gate records build, unit tests, integration tests, end-to-end tests, lint, static analysis, security, documentation, checkpoint validation, and Red Team. Applicability and evidence are Gate-specific.

## Promotion rule

A Gate can be `GATE_PASS` only when:

1. every acceptance criterion has direct evidence;
2. every applicable quality dimension is PASS;
3. unexecuted required work is absent;
4. independent review is approved;
5. Red Team has no unresolved failure;
6. the final checkpoint validates;
7. the next Gate has not been started.

Any unmet mandatory criterion produces `GATE_FAIL`, `REWORK_REQUIRED`, or `BLOCKED`, as appropriate.

