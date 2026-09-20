# ADR-0007 — Checkpoint schema 2.0.0, structured cross-tool validation, and independent promotion

Status: ACCEPTED
Date: 2026-09-20
Owners: IACode maintainers

## Context

Three defects shared one root cause: the ledger encoded judgements as free text or as implicit trust.

- `GATE_PASS` required the literal sentence `SECOND_TOOL_VALIDATION = PENDING_MANUAL` in
  `RESUME-VALIDATION.md`, so a checkpoint that actually completed cross-tool validation could not
  state its real result without failing validation.
- `QUALITY.json` recorded bare verdicts, so `staticAnalysis: "PASS"` survived into a checkpoint that
  contained no corresponding execution.
- The run that implemented a Gate also declared it passed, with its own review and Red Team reports.

Correcting these changes the checkpoint format, and two sealed checkpoints must keep validating.

## Decision

Introduce `schemaVersion` `2.0.0` for checkpoints. Validation dispatches on the declared version, so
`1.0.0` checkpoints keep the rules that applied when they were sealed.

1. **Cross-tool validation becomes structured state.** `STATE.json` carries
   `secondToolValidation` with `status` in `PENDING_MANUAL`, `PASSED`, `FAILED`, or `NOT_REQUIRED`,
   plus `tool`, `provider`, `model`, `validatedAt`, `justification`, and `evidence`. `PASSED` requires
   tool, provider, and an RFC 3339 timestamp; `NOT_REQUIRED` requires a justification; an unknown
   value is rejected by the schema.
2. **Quality verdicts carry evidence.** `QUALITY.json` uses `checks.<dimension> = {status, evidence,
   justification}`. A `PASS` needs at least one reference that resolves: `command:<id>` to a
   `COMMANDS.jsonl` record that exited `0`, or `file:<name>` to a non-empty file inside the
   checkpoint. `COMMANDS.jsonl` records therefore carry a unique `id`.
3. **Promotion is independent.** The implementing run closes at `READY_FOR_REVIEW`. `GATE_PASS`
   requires `secondToolValidation` to be `PASSED`, or `NOT_REQUIRED` with a justification, which a
   self-review cannot honestly produce.

## Alternatives Considered

- Keep parsing prose and add more accepted sentences. Rejected: unverifiable and fragile.
- Rewrite the sealed checkpoints into the new format. Rejected: they are immutable history.
- Infer evidence by matching command text to a dimension name. Rejected as a fragile heuristic; an
  explicit reference is checkable.
- Require an independent *provider* rather than an independent *run*. Rejected for now: the contract
  needs independence of judgement, and provider diversity is recorded in the same structure without
  being a hard precondition.

## Consequences

New checkpoints must record evidence references and cannot self-grant a Gate. The historical
checkpoints stay valid and stay historical. Tooling reads both versions.

## Risks

`NOT_REQUIRED` is an escape hatch; it is constrained by a mandatory justification and remains visible
in the state. Version dispatch adds branches to the validator, covered by tests on both versions.

## Reversal Strategy

Issue a further schema version. Sealed checkpoints are never rewritten, so reversal never rewrites
history.

## Related Artifacts

`.iacode/schemas/checkpoint.schema.json`, `.iacode/schemas/quality-result.schema.json`,
`.iacode/schemas/command.schema.json`, `scripts/development-ledger/`, `docs/CHECKPOINT-PROTOCOL.md`,
`docs/QUALITY-GATES.md`, `docs/HANDOFF-PROTOCOL.md`, `docs/DEFINITION-OF-DONE.md`.
