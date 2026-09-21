# Plan

## Objective

Close `CP11-F-001`, the single critical finding of the fresh-session independent `M0` audit recorded
in `SETUP-00-CP-0011`, so that a checkpoint which corrects no audit can obtain a passing internal
mirror through the shipped tooling, and request a new `M0` audit. Gate 0 is not started.

## What the finding is

Two of the eighteen checks of `m0_mirror_audit.py` required their derived set to be non-empty in
order to report success. `MIR-002` returned `closed == total and total > 0` and `MIR-003` returned
`... and bool(expected)`, so a delivery with nothing to audit was reported as failing. Checkpoint
validation requires a passing mirror for every positive terminal status, so the audit checkpoint of
this milestone could not close at the status its own `NEXT.md` prescribes, and the first delivery of
every later Gate could not reach `READY_FOR_REVIEW`.

The defect is one control unable to tell two states apart:

| State | Meaning | Correct outcome |
|---|---|---|
| empty applicable set | the canonical sources name nothing of this kind to judge | `NOT_APPLICABLE`, justified |
| missing required set | the canonical sources name items the delivery does not carry | `FAIL` |

It survived because `promotion_simulation.py` wrote the mirror artifact by hand instead of running
the tool, so the rehearsal of the positive path passed while the control refused every real
delivery.

## Steps

1. **Cold start.** Read the entry contract, the governing documents, `LATEST.md` and the complete
   `SETUP-00-CP-0011`. Record the Git baseline and run the mandatory validators, without hiding the
   red result the finding causes.
2. **Reproduce.** Execute `m0_mirror_audit.py` against the sealed audit checkpoint and observe
   `MIR-002 FAIL: 0/0 audit findings CLOSED`.
3. **Make the audit registrable.** `NEXT.md` requires registering `M0-CP-0011` as the audit whose
   corrective delivery this checkpoint is. Its sealed reports render their findings and their
   battery differently from the two earlier audits, and the current parsers read them as empty.
   Fix the parsers first: bound `parse_findings` to the report's own `## Findings` section so an
   audit verifying its predecessor's findings does not re-raise them, and read an attack table by
   its header so all three renderings parse while the two earlier parses stay exactly as they were.
4. **Register the audit** in `.iacode/policies/audit-registry.json`, which binds `CP11-F-001` and
   the twelve mandatory attacks of the sealed battery into the expected requirement set of this
   delivery. This is a side effect of the protocol, not the fix.
5. **Repair the semantics.** Derive the applicable set in `policies.audit_applicability` from the
   registry and the sealed reports at every call; report an empty set as `NOT_APPLICABLE` with a
   reason, an expected count of zero and the derivation source; keep a missing or unsatisfied
   required set as `FAIL`; make the overall verdict fail only on a `FAIL` while preserving the
   individual `NOT_APPLICABLE` status in the artifact.
6. **Close the reverse escape.** Making `NOT_APPLICABLE` reachable creates the opposite risk: a
   delivery declaring away work it should do. Evolve the report schema to `1.1.0` with the
   justification fields, refuse an unjustified or non-empty inapplicable dimension, and re-derive
   the registry-bound dimensions in `validate_checkpoint` so the claim is checked rather than
   believed.
7. **Make the simulation execute the control.** `promotion_fixture` runs `m0_mirror_audit.py` and
   records the command and exit code; the simulation report declares what was executed and what was
   modelled.
8. **Execute the states.** `mirror_semantics_validation.py` runs the real tool over six prepared
   states: the empty applicable set, the satisfied set, an open finding, a missing closure record, a
   forged empty declaration and an unexecuted mandatory attack.
9. **Execute the transition.** `gate_transition_simulation.py` closes a milestone in a disposable
   repository and delivers the first checkpoint of the next Gate to `READY_FOR_REVIEW`. The next
   Gate's specification is synthetic and lives only in that repository: no Gate 0 work is done here.
10. **Attack the new surface.** Add the adversarial scenarios the repair opens, and execute the
    twelve mandatory attacks the sealed CP-0011 battery hands this delivery.
11. **Record the memory.** A new lesson for the distinction, new guardrails for the distinction, for
    the simulation rule and for the Gate transition, and a `GUARDRAIL_FAILURE` against `LSN-0024`
    and `LSN-0029`, resolved here.
12. **Record the language rule** in `CLAUDE.md`, and the new control as checklist row `7d.16`.
13. **Run the delivery order to the end**: preflight, requirement derivation, Green Keeper, delivery
    completeness, internal Red Team, milestone closure auditor, an internal audit by a
    non-implementing pass, and `READY_FOR_REVIEW`.

## Tests

Positive: an empty applicable set passes; a satisfied set passes; the first delivery of the next
Gate reaches `READY_FOR_REVIEW`; the sealed simulation artifact is the tool's own output.

Negative: an open finding fails; a missing closure record fails; a forged empty declaration does not
shrink the applicable set; an unexecuted mandatory attack fails; an unjustified inapplicable
dimension is refused; one with items is refused; one counted as a pass is refused; one under the
older report version is refused; a registry-bound dimension cannot be declared inapplicable.

Compatibility: the parses of the two earlier sealed audits are held fixed, and every sealed
checkpoint still validates under the current tooling.

## Risks

Registering the audit makes this delivery's mirror satisfiable by giving it work to close, which
could hide the underlying defect. The mitigation is that the repair is proven in the states where
there is no work at all: the mirror semantics validation and the Gate transition simulation both
exercise deliveries that correct nothing.

Making `NOT_APPLICABLE` reachable is itself an attack surface. The mitigation is that it is
justified, counted separately, re-derived by the validator and attacked by the battery.

## Stop conditions

Stop on unexpected Git divergence, on a failing mandatory gate that cannot be repaired inside the
repository, on any need to modify a sealed checkpoint or move a historical tag, on secret exposure,
and on any attempt to begin Gate 0.
