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

0. Lesson preflight, before the Gate starts, writing `LESSON-PREFLIGHT.json` and turning every
   applicable lesson into a `LESSON-REQ-` requirement.
1. Requirement extraction into `REQUIREMENTS-MATRIX.json`.
2. Baseline.
3. Plan.
4. Implementation.
5. Test and quality execution.
6. Test Rework / Green Keeper.
7. Delivery Completeness Validator.
8. Internal Red Team over the mandatory attack battery.
9. Milestone Closure Auditor, the internal mirror of the independent audit.
10. `READY_FOR_REVIEW`.
11. Independent tool review.
12. Red Team.
13. `GATE_PASS`.

Steps 6 to 9 exist so the independent tool never has to discover an unimplemented requirement, a
forgotten prompt item, missing documentation, a red test, a red quality gate, a partial artifact,
absent evidence, or an escaped attack. The Green Keeper may change code; the Delivery Completeness
Validator, the internal Red Team and the Milestone Closure Auditor may not. Their contracts are
`.iacode/agents/test-rework-greenkeeper.md`, `.iacode/agents/delivery-completeness-validator.md`,
`.iacode/agents/red-team.md` and `.iacode/agents/m0-closure-auditor.md`.

Any red result in steps 5 to 9 returns the delivery to step 4 and the whole cycle runs again. None of
steps 6 to 9 is independent validation, and none of them may be recorded as one.

Nothing red ships. A requirement that cannot be finished, or a gate that cannot be repaired inside
the repository, produces `BLOCKED` with the blocker named, never `READY_FOR_REVIEW`. No delivery
advances with a red test or gate, with coverage below total, or with any requirement `PARTIAL` or
`MISSING`.

## Engineering memory

Confirmed failures become lessons in `.iacode/memory/`, and important lessons become automated
guardrails. A lesson is `GUARDED` only when a test, validator, lint rule, policy, schema, invariant
or automated check prevents recurrence; documentation alone never is. The preflight is mandatory
before every Gate, and a repeat of a guarded failure class is a `GUARDRAIL_FAILURE` that must be
investigated. See [ENGINEERING-MEMORY.md](ENGINEERING-MEMORY.md).

## External validation cadence

An intermediate Gate closes at `INTERNAL_GATE_PASS` on the project's own controls. Independent
external validation happens once per milestone, over the group of Gates, and produces
`MILESTONE_EXTERNAL_PASS`. An internal verdict is never described as independent external
validation. An extraordinary audit before the milestone requires `externalAuditRequired` with a
recorded trigger. See [MILESTONE-VALIDATION.md](MILESTONE-VALIDATION.md).

## Git discipline

Do not force push, hard reset, destructively clean, or rewrite history without explicit authorization and a validated checkpoint immediately before the operation. Do not mix Gates in a commit. Prefer clear prefixes: `setup:`, `gate0:`, `gate1:`, `fix:`, `test:`, `docs:`, and `refactor:`.

## Gate discipline

The previous Gate is mandatory. A Gate may advance only when it is `GATE_PASS` and the next Gate is explicitly authorized. Blocked or failed work remains explicit; scope never changes silently.

## Evidence discipline

Assertions by an implementer are not test evidence. Record concise observable decision summaries, not private chain-of-thought. Provenance is required and training is denied by default.

