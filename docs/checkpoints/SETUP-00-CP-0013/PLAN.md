# Plan

## Mandate

Audit the sealed `SETUP-00-CP-0012` in a fresh session, without trusting the implementer's summary,
and decide `M0` definitively: pass, or return it for rework. Do not modify product code. Do not
implement Gate 0.

`SETUP-00-CP-0012` is the corrective delivery of `CP11-F-001`, the single critical finding of the
fresh-session independent audit recorded in `SETUP-00-CP-0011`. The finding was that the internal
mirror audit could not pass for a delivery that corrects no audit, while checkpoint validation
required it to pass, so the protocol's own next step was unreachable with the shipped tooling.

## What this run is and is not

This is a `FRESH_SESSION_INDEPENDENT_AUDIT`. It is independent of the implementing run and of its
session, and it is **not** cross-tool validation: the tool, the provider and the model are the same
as the implementer's. `crossToolValidation` is recorded as `NOT_AVAILABLE` so the limit stays
visible rather than implied. The verdict this run may grant is
`MILESTONE_INDEPENDENT_AUDIT_PASS`; `MILESTONE_EXTERNAL_PASS` is not available to it and the
derivation refuses it.

The verdict belongs to **this** checkpoint, about the sealed subject. `SETUP-00-CP-0012` is not
rewritten, re-tagged or re-sealed to become approved.

## Order of work

1. Read the canonical contracts, `SETUP-00-CP-0011` and `SETUP-00-CP-0012` in full, and the sealed
   `CP11-F-001` finding from the review report that raised it rather than from the closure record.
2. Write the audit matrix before substantive execution, with every row `NOT_STARTED`
   (`audit-harness/matrix_rows.py`, rendered by `build_matrix.py --skeleton`).
3. Run the lesson preflight for this Gate and this run's scope, and derive the requirement set from
   the canonical sources.
4. Execute, never read: the real `m0_mirror_audit.py` over every applicability state, the product's
   own semantics validation, the Gate 0 transition, the positive promotion, successor durability,
   the whole suite, the mandatory validators, and all of it again in a clean clone.
5. Attack the state the repair opened, with a null-mutation control accepted first.
6. Re-derive rather than believe: the expected requirement set, the evidence resolution, the derived
   counts, the guardrail measurement and the integrity chain, each with this audit's own readers.
7. Decide, record the verdict in this checkpoint with an attestation about the sealed subject, and
   seal.

## Independent derivation

Nothing in `audit-harness/derive_expected.py`, `resolve_evidence.py` or `verify_memory.py` imports
`policies.py`, `delivery_assurance.py` or `lessons.py`. Agreeing with the delivery therefore means
two independent readers agreed, not that one function was called twice.

## Stop conditions

Stop on unexpected Git divergence, on any need to modify a sealed checkpoint or move a historical
tag, on a mandatory row that cannot be executed, on secret exposure, and on any attempt to begin
Gate 0.

## What this run may not do

- Repair product code. A finding returns to the implementer; an auditor that fixes what it judges
  is no longer independent.
- Record an internal verdict as an independent one, or a same-tool audit as a cross-tool one.
- Close a dimension by writing the artifact a control would have produced.
- Narrow a mandatory gate set, a denominator or a promotion rule by argument.
