# Risks

## R1 — The independence of this verdict is session independence, not tool independence

Severity: `HIGH`. The auditing run shares the tool, the provider and the model with the implementing
run. A systematic blind spot of that tool or that model is not detected by this audit and would not
be. The verdict is recorded as `MILESTONE_INDEPENDENT_AUDIT_PASS` and never as an external pass, the
attestation records `crossToolValidation: NOT_AVAILABLE`, and the validator refuses the cross-tool
status for this mechanism. Mitigation: a cross-tool audit when one becomes operationally available;
the vocabulary already exists for it and needs no change.

## R2 — The trust model of a milestone verdict is structural, not cryptographic

Severity: `MEDIUM`. A verdict requires a second sealed, tagged, anchored checkpoint authored as the
audit of an already sealed subject. There is no signature and no external key, so an actor with full
control of the repository can forge the relationship. The limit is recorded in
`docs/MILESTONE-VALIDATION.md`, in `.iacode/attestations/README.md` and in the anchor trust model,
and nothing claims more. Mitigation available and not taken here: signed attestations.

## R3 — Reproducing the suite in a fully sealed checkout skips one conditional case

Severity: `LOW`. One case guards itself on the presence of an unsealed checkpoint directory and
another on a checkpoint that carries no preflight yet, so the exact passing count moves by one
between environments while failures and errors stay at zero in all of them. Mitigation: the count is
read from the result object and both environments are reported separately rather than merged.

## R4 — An audit harness is an instrument, and an instrument can be wrong

Severity: `LOW`. One defect in this harness was found and corrected during the audit: the first
matrix generation read the closure record with the wrong field names and derived no regression row.
It was repaired and the matrix regenerated rather than the rows dropped. Mitigation: every harness
result that matters is cross-checked against a product execution or an independent recomputation,
and the harness is sealed with the audit so a later reader can re-run it.

## R5 — The open finding blocks the next delivery, not only this audit

Severity: `HIGH`. `CP11-F-001` prevents any checkpoint that corrects no audit from reaching a
positive terminal status through the shipped tooling. Registering this audit in the audit registry
makes the *corrective* delivery satisfiable, which can hide the underlying defect: the first Gate 0
delivery will correct nothing and will hit it again. Mitigation: `NEXT.md` states plainly that the
registration is a side effect and not the fix, and the acceptance criteria require the positive path
to be produced by executing the tool.

## R6 — Gate 0 has no specification yet

Severity: `MEDIUM`. `.iacode/policies/canonical-requirements.json` declares no requirements for
`GATE-0`, so the expected requirement set of a Gate 0 delivery cannot be derived until the Gate 0
checklist exists in the repository. This is not a defect of `M0` — Gate 0 has not started — but it is
the first deliverable of that Gate, not an aside. Mitigation: recorded here so the next Gate does not
discover it after starting.

## R7 — Three refusal branches of the attestation model have no test

Severity: `LOW`. The unsealed auditor, the unanchored auditor and the non-ancestor subject are
refused correctly, which this audit verified by executing them, but no case in the suite exercises
them. They were uncovered before this delivery as well, so this is a standing gap rather than a
regression. Mitigation: a future delivery can add three cases; nothing depends on them today beyond
the execution recorded here.
