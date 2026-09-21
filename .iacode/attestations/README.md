# Independent audit attestations

A milestone verdict is not a field a delivery fills in about itself. It is derived from an
attestation stored here, one JSON document per audit, validated against
`.iacode/schemas/external-audit-attestation.schema.json`.

An attestation is written by the run that performed the independent audit, **in that audit's own
checkpoint**, about a checkpoint that was already sealed. It names:

- the audit, its mechanism, and whether cross-tool execution was available;
- the auditing tool, its provider, its model, and whether the session was fresh;
- the subject checkpoint and the exact commit its canonical tag resolves to;
- the audit checkpoint that carries the evidence;
- the review verdict, the Red Team verdict, completeness with evidence coverage, and the test result.

It never names its own commit. An attestation that had to contain the identifier of the commit whose
tree contains it would be unreachable, which is what finding `CP9-F-001` demonstrated: fifteen
forgeries refused and no honest audit able to pass. The audit checkpoint's identity is bound by its
own sealing, its canonical tag, and the integrity anchor its successor records.

The subject stays immutable. It is not rewritten, re-tagged or re-sealed to become approved: it is
audited, and the verdict lives in the later checkpoint that performed the audit.

`scripts/development-ledger/attestation.py` re-derives all of it, and
`scripts/development-ledger/milestone_status.py --milestone M0` prints the derivation. An attestation
is refused when it names the audited checkpoint as its own auditor, when the subject is unsealed,
unanchored or named with the wrong commit, when the claiming checkpoint is not the audit checkpoint
that authored it, when the subject commit is not an ancestor of the audit's history, when the
mechanism does not authorise the status being claimed, or when any of the four results falls short.

Two mechanisms are recognised, and each authorises only the status its evidence supports:

| `validationMechanism` | Status it authorises |
|---|---|
| `CROSS_TOOL_INDEPENDENT_AUDIT` | `MILESTONE_EXTERNAL_PASS`, `MILESTONE_INDEPENDENT_AUDIT_PASS` |
| `FRESH_SESSION_INDEPENDENT_AUDIT` | `MILESTONE_INDEPENDENT_AUDIT_PASS` |

The control is structural, not cryptographic. There is no signature and no external key: what it
removes is the ability to produce a milestone verdict by editing `STATE.json`. An actor who can
create a sealed, tagged, anchored audit checkpoint could still forge the relationship, and
`docs/MILESTONE-VALIDATION.md` records that limit rather than papering over it.

This directory is empty of attestations until an independent audit produces one.
