# ADR-0008 — Delivery assurance gates and checkpoint schema 3.0.0

Status: ACCEPTED
Date: 2026-09-20
Owners: IACode maintainers

## Context

The independent Codex validation recorded in `SETUP-00-CP-0004` returned `REWORK_REQUIRED` and
`RED_TEAM_FAIL`. Two defects were blocking:

- A finalization refused by a precondition, such as a detached `HEAD`, returned before anything was
  recorded, so the ledger claimed every attempt was observable while an entire class of attempts
  vanished. Recorded finalizer command strings also omitted the interpreter and the repository
  path, so they could not be replayed from the working directory they named.
- `READY_FOR_REVIEW` validated with a non-empty `blockedBy`. A checkpoint could simultaneously claim
  it was ready for review and that it was blocked, and a resealed fixture proved it.

Both defects share a shape: a control that was documented but not enforced. The same shape produced
the earlier CP-0002 findings. The deeper problem is that the independent tool was acting as the first
line of defense against basic gaps, which is expensive and unreliable.

## Decision

Introduce `schemaVersion` `3.0.0` and two mandatory delivery-assurance gates, with version dispatch
so the sealed `1.0.0` and `2.0.0` checkpoints keep validating under the rules they were written for.

1. **Every attempt is recorded, including a refusal.** A refusal carries
   `result = PRECONDITION_REJECTED`, a documented `resultCode`, a `failureReason`, the evaluated
   preconditions with their observed values, and no `exitCode`. Inventing an exit code for a process
   that never started would be false evidence, so the canonical result vocabulary exists instead.
2. **Every command record is reproducible.** Identifier, timestamp, runtime, working directory,
   command, sanitized arguments, referenced inputs, repository commit, purpose, canonical result,
   exit or result code, duration, and stream artifacts. The recorded command starts with an explicit
   runtime and any script path must resolve from the working directory.
   `scripts/development-ledger/record_command.py` produces compliant records so this is tooling, not
   discipline.
3. **Readiness excludes blockage, in every version.** `READY_FOR_REVIEW`, `READY_FOR_RED_TEAM`, and
   `GATE_PASS` require an empty `blockedBy`; `BLOCKED` requires a non-empty one. This is a control
   fix rather than a format change, so it applies to every schema version and to every tool.
4. **`GREEN_KEEPER_GATE`.** Nothing red ships. The Test Rework / Green Keeper role repairs the cause
   of every failing mandatory gate and records each cycle in `REWORK-LOG.jsonl`. The gate is `PASS`
   only when every mandatory executable gate is green, no failure remains, and no rework item is
   unresolved. A real external blocker produces `BLOCKED`.
5. **`DELIVERY_COMPLETENESS_GATE`.** The Delivery Completeness Validator audits
   `REQUIREMENTS-MATRIX.json` requirement by requirement and may not implement or silently correct
   anything. The gate is `PASS` only at total coverage with zero partial, zero missing, and every
   evidence reference resolved.
6. **Both gates are preconditions of `READY_FOR_REVIEW`**, and the validator recomputes the audit
   from the matrix and cross-checks the rework log, so a checkpoint cannot assert a gate it did not
   earn.

## Alternatives Considered

- Fix only the two findings. Rejected: it would leave the independent tool as the first line of
  defense, which is what produced the findings.
- Make the two new roles advisory documents. Rejected: an unenforced control is what failed twice.
- Trust an implementer's statement of completeness. Rejected explicitly; evidence must resolve to a
  file, a successful command record, or a test that exists.
- Let the gates be computed only by a script. Rejected: the validator recomputes them independently,
  so the report and the matrix cannot drift apart.

## Consequences

A delivery costs more before handoff and less during review. Requirements must be extracted before
implementation. The implementing run can no longer reach `READY_FOR_REVIEW` with a red gate, a
partial requirement, an unrecorded refusal, or a self-claimed independent verdict.

## Risks

The two roles are emulated inside one session when the tool offers no true isolation; the
separation is one of role and artifact, not of process, and is documented as such rather than
overstated. `NOT_APPLICABLE` and external blockers remain judgement calls, constrained by mandatory
justifications that stay visible in the ledger. Version dispatch now carries three rule sets, each
covered by tests, including validation of all four sealed checkpoints.

## Reversal Strategy

Issue a further schema version. Sealed checkpoints are never rewritten, so reversal never rewrites
history.

## Related Artifacts

`.iacode/agents/test-rework-greenkeeper.md`, `.iacode/agents/delivery-completeness-validator.md`,
`.iacode/schemas/requirements-matrix.schema.json`, `.iacode/schemas/completeness-report.schema.json`,
`.iacode/schemas/rework-log.schema.json`, `.iacode/schemas/checkpoint.schema.json`,
`.iacode/schemas/command.schema.json`, `scripts/development-ledger/`, `docs/DEVELOPMENT-CONTRACT.md`,
`docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`,
`docs/DEFINITION-OF-DONE.md`, `docs/SETUP-00-CHECKLIST.md`.
