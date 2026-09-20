# Quality Gates

## Canonical outcomes

Quality checks use only `PASS`, `FAIL`, `NOT_APPLICABLE`, or `NOT_EXECUTED`. Gate state uses only the statuses defined by `CHECKPOINT-PROTOCOL.md`.

## Required dimensions

Every Gate records build, unit tests, integration tests, end-to-end tests, lint, static analysis, security, documentation, checkpoint validation, and Red Team. Applicability and evidence are Gate-specific.

## Evidence references

From `schemaVersion` `2.0.0`, `QUALITY.json` records each dimension as `{status, evidence, justification}`.
A `PASS` requires at least one resolvable evidence reference: `command:<id>` must name a record in the
checkpoint's `COMMANDS.jsonl` that exited `0`, and `file:<name>` must name a non-empty file inside the
checkpoint. `NOT_APPLICABLE` requires a justification. A verdict inherited from an earlier checkpoint
without re-execution is `NOT_EXECUTED`, never `PASS`.

## Promotion rule

A Gate can be `GATE_PASS` only when:

1. every acceptance criterion has direct evidence;
2. every applicable quality dimension is PASS with resolvable evidence;
3. unexecuted required work is absent;
4. independent review is approved;
5. Red Team has no unresolved failure;
6. the final checkpoint validates;
7. the next Gate has not been started;
8. the run granting `GATE_PASS` is independent of the run that implemented the Gate, and
   `secondToolValidation` records `PASSED` or a justified `NOT_REQUIRED`.

Any unmet mandatory criterion produces `GATE_FAIL`, `REWORK_REQUIRED`, or `BLOCKED`, as appropriate.

