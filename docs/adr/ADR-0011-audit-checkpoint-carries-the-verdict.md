# ADR-0011: The audit checkpoint carries the milestone verdict

- Status: Accepted
- Date: 2026-09-21
- Gate: SETUP-00
- Checkpoint: SETUP-00-CP-0010
- Supersedes: the consumption rule introduced with [ADR-0010](ADR-0010-milestone-closure-controls.md)

## Context

[ADR-0010](ADR-0010-milestone-closure-controls.md) made an external milestone verdict derivable from
an attestation rather than assertable in `STATE.json`. The fresh-session `M0` audit of
`SETUP-00-CP-0008` found that the derivation had been attached to the wrong object.

`validate_checkpoint.py` resolved the subject commit from the *promoted* checkpoint's own canonical
tag and required the attestation's `subjectCommit` to equal it. The attestation file is part of the
tree that the tag names, so satisfying the rule required a tree containing its own commit identifier.
The audit recorded three attempts and a fixed-point iteration, all ending in
`attests commit X, not the subject commit Y`. Writing the attestation in the audit checkpoint instead
moved `HEAD` past the subject's tag, after which the subject could not be validated at all.

Fifteen forged variants were correctly refused and no legitimate audit could ever be accepted:
`CP9-F-001`, a `CRITICAL` finding, and the reason `MILESTONE_EXTERNAL_PASS` was unreachable.

A second observation shaped the decision. `.iacode/attestations/` is inside the delivery-assurance
scope, so adding an attestation marked the subject's Green Keeper, completeness audit, internal Red
Team and mirror audit `STALE`, and re-running them changed the content again.

## Decision

The verdict belongs to the audit checkpoint, not to the delivery it judges.

1. A subject checkpoint is delivered, sealed, anchored and closed at `READY_FOR_REVIEW`, and is
   never rewritten, re-tagged or re-sealed to become approved.
2. A later checkpoint, authored by the auditing run, anchors the subject and writes
   `.iacode/attestations/<auditId>.json` naming the subject and the commit the subject's canonical
   tag already resolves to. The attestation never names its own commit.
3. That audit checkpoint's own status is the milestone verdict, and `STATE.externalAttestation`
   names the subject it judged. Validation verifies the attestation against the *named* subject and
   requires the claiming checkpoint to be the audit checkpoint that authored it.
4. The milestone verdict is derived from the repository by
   `attestation.derive_milestone_verdict`, exposed by `milestone_status.py`, and is never read from
   a status field.
5. The mechanism is recorded honestly. `CROSS_TOOL_INDEPENDENT_AUDIT` authorises
   `MILESTONE_EXTERNAL_PASS`; `FRESH_SESSION_INDEPENDENT_AUDIT` authorises the new
   `MILESTONE_INDEPENDENT_AUDIT_PASS` and nothing stronger, because a new session of the same tool
   is independent of the run and not of the tool.
6. The assurance boundary is drawn by which tree a result describes. The subject's gates describe
   the tree its tag names, which cannot contain a later attestation; the audit checkpoint runs its
   own gates after writing the attestation. Attestations are *not* excluded from the assurance
   scope, because that would have hidden real staleness inside the audit checkpoint.

## Alternatives considered

- **Bind `subjectCommit` to the content commit rather than the tag.** Narrower, but it still left
  the verdict on the object being judged and would have required the subject to be re-sealed once
  the audit existed.
- **Exclude `.iacode/attestations/` from the assurance scope.** It would have turned the staleness
  green without making the positive path reachable, and it would have blinded the audit
  checkpoint's own gates to a file it authors.
- **Keep one status and call a fresh-session audit external.** Rejected: the audit itself warned
  that describing a same-tool audit as cross-tool validation is a false claim.

## Consequences

- A milestone PASS is reachable by an honest sequence of repository states, and the sequence is
  executed end to end before every handoff by `promotion_simulation.py`.
- Sealed subjects stay immutable, so an audit never invalidates the evidence it is judging.
- The status vocabulary grew by one member, and every validator, policy document and report now
  distinguishes an independent audit from an external one.
- The residual limit is unchanged and still stated: the control is structural, not cryptographic.
  An actor who can create a sealed, tagged, anchored audit checkpoint can forge the relationship.
