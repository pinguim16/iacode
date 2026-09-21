# Next

## Required next action

`REQUEST EXPLICIT AUTHORIZATION TO OPEN GATE 0 — FOUNDATION`.

`M0` has passed its fresh-session independent audit and `SETUP-00` is closed. `GATE 0 — FOUNDATION`
is `AUTHORIZED` in the sense that the milestone precondition is satisfied; it is **not** started, and
it may not be started inside this checkpoint. Opening it requires the owner's explicit
authorization and a new pre-Gate checkpoint of its own.

No Gate 0 work exists in this change set and none was begun.

## What the next run receives

- `M0` `PASSED`, carried by this audit checkpoint about the sealed `SETUP-00-CP-0012` and derived
  from `.iacode/attestations/M0-CP-0013.json` rather than asserted.
- Seventeen findings across three independent audits, all closed, each closure re-verified against
  the sealed report that raised it.
- A control plane whose two states — something to audit, and nothing to audit — are both reachable
  and both audited. The first delivery of Gate 0 will be in the second state.
- `REVIEW-REPORT.md`, `MILESTONE-REPORT.md`, `RED-TEAM-REPORT.md`, `FINAL-M0-AUDIT-MATRIX.json` and
  `AUDIT-EXECUTIONS.json`: what this audit examined, what it executed, and what it examined and
  deliberately did not raise.
- `RISKS.md`: four risks carried into `M1`, each with the condition that would turn it into a
  defect.

## The first deliverable of Gate 0

`.iacode/policies/canonical-requirements.json` declares no requirements for `GATE 0`. Authoring that
specification is the **first** deliverable of that Gate, not of this one, and nothing can be derived
for Gate 0 until it exists: the expected requirement set of its first delivery comes from that file,
from the lesson preflight, and from the open audit findings, of which it will have none.

## How to open Gate 0, when it is authorised

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`,
   `docs/DEFINITION-OF-DONE.md`, `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`,
   `docs/checkpoints/LATEST.md` and this complete checkpoint.
2. Confirm the milestone verdict by derivation, not by reading a status field:
   `python scripts/development-ledger/milestone_status.py --milestone M0` must report `PASSED` on
   `M0-CP-0013`.
3. Run `python scripts/development-ledger/lesson_preflight.py --gate GATE-0 --scope <scope> --write`
   before any Gate 0 work, and carry every derived `LESSON-REQ-` requirement into the matrix.
4. Author the canonical `GATE 0` requirement specification, then derive the requirement set with
   `python scripts/development-ledger/derive_requirements.py --write`.
5. Follow the mandatory delivery order without skipping a step, and close the first Gate 0 delivery
   at `READY_FOR_REVIEW`.

## What must not happen

- Do not rewrite, re-tag or re-seal this checkpoint or any sealed predecessor, including the
  subject.
- Do not begin Gate 0 without explicit authorization and its own pre-Gate checkpoint.
- Do not describe this verdict as cross-tool validation. It is a fresh-session audit by the same
  tool, provider and model as the implementer, and `crossToolValidation` is `NOT_AVAILABLE`.
- Do not treat `M0 PASSED` as permission to relax a control. Every gate that applied to `SETUP-00`
  applies to `GATE 0`.

## Next Gate

`GATE 0 — FOUNDATION`: `AUTHORIZED`, not started. Its milestone is `M1`, which it does not close, so
it will end at `INTERNAL_GATE_PASS` rather than at a milestone verdict.
