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

Nothing inapplicable is red either. A control that judges a derived set reports an empty applicable
set as `NOT_APPLICABLE` with its justification, and a missing required set as `FAIL`; the two states
are never collapsed, and the applicable set is derived from canonical sources the delivery cannot
shrink. A simulation that reports a control as passing executes that control rather than writing the
artifact it would have produced. See [QUALITY-GATES.md](QUALITY-GATES.md).

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

Do not force push, hard reset, destructively clean, or rewrite history without explicit authorization and a validated checkpoint immediately before the operation. Do not mix Gates in a commit. Prefer clear prefixes: `setup:`, `gate0:`, `gate1:`, `fix:`, `test:`, `docs:`, and `refactor:`, or a semantic `type(scope): subject`.

From `GATE 3` the repository has a public remote, `origin` =
`https://github.com/pinguim16/iacode.git`, and `main` is the branch pushed
([ADR-0024](adr/ADR-0024-public-remote-and-atomic-commits.md)):

- the whole history is scanned with `secret_scan.py --history` before it is first made public, and
  a finding blocks the push rather than triggering a rewrite;
- a commit is one logical advance: implementation complete, its targeted tests green, only its own
  files staged, and `secret_scan.py --staged` clean;
- every green commit is pushed with `git push origin main`, not held until the Gate closes;
- a pushed commit is never amended, rebased or reset; a mistake is corrected by a new commit;
- a sealed checkpoint's tag is pushed and never moved or deleted on the remote;
- authentication stays in the local credential store, never in a URL, a config file, the repository
  or a chat;
- a Gate claims remote synchronisation only when `git log origin/main..main` is empty and its
  final tag is on the remote.

The Git an agent uses inside a sandbox is not this Git: it is local to a disposable workspace, has
its own identity, and has no remote and no credential
([ADR-0027](adr/ADR-0027-tool-execution-policy.md)).

## Gate discipline

The previous Gate is mandatory. A Gate may advance only when it is `GATE_PASS` and the next Gate is explicitly authorized. Blocked or failed work remains explicit; scope never changes silently.

## Evidence discipline

Assertions by an implementer are not test evidence. Record concise observable decision summaries, not private chain-of-thought. Provenance is required and training is denied by default.

