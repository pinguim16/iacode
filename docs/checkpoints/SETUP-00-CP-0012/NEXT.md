# Next

## Required next action

`REQUEST A FRESH-SESSION INDEPENDENT M0 AUDIT OF SETUP-00-CP-0012`.

This checkpoint is the corrective delivery that closes `CP11-F-001`. It closes at
`READY_FOR_REVIEW`, which is the only status an implementing run may give itself. `M0` is still
`PENDING`: a milestone verdict is carried by a separate audit checkpoint about a sealed subject, and
this delivery is the subject, not the audit.

`GATE 0 — FOUNDATION` stays `BLOCKED`. No Gate 0 work exists in this change set and none was
started.

## What the audit receives

- `CP11-F-001` closed, recorded in `CP11-FINDINGS-CLOSURE.json` and `.md`, with the finding set
  re-parsed from the sealed `SETUP-00-CP-0011` review report rather than transcribed.
- The repair of the applicability semantics in `m0_mirror_audit.py`, `policies.py`,
  `validate_checkpoint.py` and `.iacode/schemas/mirror-audit.schema.json`.
- `MIRROR-SEMANTICS-VALIDATION.json` and `.md`: the real tool executed over six applicability
  states, three of them negative.
- `GATE0-TRANSITION-SIMULATION.json` and `.md`: a closed milestone followed by the first checkpoint
  of the next Gate reaching `READY_FOR_REVIEW`, against a synthetic specification that never leaves
  the disposable repository.
- `POSITIVE-PROMOTION-VALIDATION.json` and `SUCCESSOR-DURABILITY.json`, both re-executed, with the
  mirror report now produced by running the tool instead of being written by hand.
- `M0-INTERNAL-RED-TEAM.json` and `AFFECTED-RED-TEAM.json`: the battery including the scenarios the
  repair's own new state space deserves, and the twelve mandatory attacks the sealed CP-0011 battery
  hands this delivery.
- `M0-INTERNAL-MIRROR.json`: produced by executing `m0_mirror_audit.py --clean-clone --write`.
- `FINAL-INTERNAL-AUDIT.json` and `.md`: an internal, non-implementing audit pass. It is internal
  quality assurance and is not recorded as independent validation.

## How to audit it

1. Read `START-HERE.md`, `docs/DEVELOPMENT-CONTRACT.md`, `docs/MASTER-PLAN.md`,
   `docs/QUALITY-GATES.md`, `docs/CHECKPOINT-PROTOCOL.md`, `docs/HANDOFF-PROTOCOL.md`,
   `docs/DEFINITION-OF-DONE.md`, `docs/ENGINEERING-MEMORY.md`, `docs/MILESTONE-VALIDATION.md`,
   `docs/checkpoints/LATEST.md` and this complete checkpoint.
2. Run the validation commands in `HANDOFF.md` and compare the observed Git state with `STATE.json`.
3. Re-derive rather than read: the expected requirement set, the completeness, the counts, the
   integrity chain and the applicable audit set are all derivable from the repository.
4. Re-execute `mirror_semantics_validation.py`, `gate_transition_simulation.py`,
   `promotion_simulation.py`, `successor_durability.py`, `m0_red_team.py` and
   `m0_mirror_audit.py --clean-clone`.
5. Attack the state the repair opened: an inapplicable dimension without a justification, one
   carrying items, one counted as a pass, one under report version `1.0.0`, and one declared over
   work the audit registry still names.
6. Author the verdict in a **new** audit checkpoint that anchors this one and carries
   `.iacode/attestations/<auditId>.json` about it. Do not rewrite this checkpoint.
7. Register that audit in `.iacode/policies/audit-registry.json` only if it produces findings, with
   the corrective checkpoint named.

## What must not happen

- Do not rewrite, re-tag or re-seal this checkpoint or any sealed predecessor.
- Do not record an internal verdict as independent validation, and do not describe a same-tool audit
  as cross-tool validation.
- Do not close a finding by writing the artifact a control would have produced; run the control.
- Do not begin Gate 0.

## Next Gate

`GATE 0 — FOUNDATION`: `BLOCKED`. It requires a passing `M0` audit, explicit authorization, and a
new pre-Gate checkpoint. `.iacode/policies/canonical-requirements.json` declares no requirements for
it yet, and authoring that specification is the first deliverable of that Gate, not of this one.
