# External audit attestations

An external milestone verdict is not a field a delivery fills in about itself. It is derived from an
attestation stored here, one JSON document per audit, validated against
`.iacode/schemas/external-audit-attestation.schema.json`.

An attestation is written by the run that performed the independent audit, in that audit's own
checkpoint, and it names:

- the audit, the auditing tool, its provider and its model;
- the subject checkpoint and the exact subject commit it judged;
- the audit checkpoint that carries the evidence;
- the review verdict, the Red Team verdict, completeness with evidence coverage, and the test result.

`scripts/development-ledger/attestation.py` re-derives all of it. An attestation is refused when it
names the audited checkpoint as its own auditor, when the audit checkpoint is not sealed under its
canonical tag or is not in the integrity chain, when it attests a different checkpoint or commit than
the one being promoted, or when any of the four results falls short.

The control is structural, not cryptographic. There is no signature and no external key: what it
removes is the ability to produce an external PASS by editing `STATE.json`. An actor who can create a
sealed, tagged, anchored audit checkpoint could still forge the relationship, and
`docs/MILESTONE-VALIDATION.md` records that limit rather than papering over it.

This directory is empty of attestations until an independent audit produces one.
