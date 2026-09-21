# Milestone Report — M0, Development control plane

| Field | Value |
|---|---|
| Milestone | `M0` |
| Gates | `SETUP-00` |
| Subject checkpoint | `SETUP-00-CP-0010` |
| Subject commit | `90b67a7e0a11179465bc5c92dee22c78da36801f` |
| Audit checkpoint | `SETUP-00-CP-0011` |
| Audit mechanism | `FRESH_SESSION_INDEPENDENT_AUDIT` |
| Same tool as the implementer | yes |
| Same provider as the implementer | yes |
| Same model as the implementer | yes |
| Session independence | new session, no memory of the implementing run |
| Cross-tool validation | `NOT_AVAILABLE` |
| Attestation | `.iacode/attestations/M0-CP-0011.json`, recording `reviewResult: REWORK_REQUIRED` |
| Milestone verdict | `NOT_PASSED`, derived by `milestone_status.py` |
| Milestone status | `REWORK_REQUIRED` |
| `SETUP-00` | `REWORK_REQUIRED` |
| `GATE 0 — FOUNDATION` | `BLOCKED` |
| Findings | one, `CP11-F-001`, `CRITICAL` |

## How the verdict is produced

The verdict is not a field this checkpoint fills in about the subject. It is derived from the
repository by `attestation.derive_milestone_verdict`, which re-verifies the attestation against the
subject it names, the commit that subject's canonical tag resolves to, the auditor that wrote it,
the integrity chain, the ancestry between the two commits, the mechanism, and the four results that
make a milestone pass.

The attestation this audit wrote records the real verdict, so the derivation refuses to promote on
it:

```text
MILESTONE_NOT_PASSED milestone=M0 attestations=1 accepted=0
- REJECTED .iacode/attestations/M0-CP-0011.json: reviewResult is 'REWORK_REQUIRED'; a milestone
  PASS requires APPROVED
```

That is the mechanism working in the direction that matters here. It was also exercised in the other
direction: in a sealed snapshot of this checkpoint, built by the same finalize and seal tooling the
real one uses and carrying an attestation with the four results a pass requires,
`validate_checkpoint.py` exits zero and `milestone_status.py --milestone M0` prints
`MILESTONE_PASSED` with one accepted attestation. A milestone PASS is therefore reachable; this
milestone did not earn one.

## The milestone as a whole

`M0` contains one Gate, `SETUP-00`, delivered over ten checkpoints and three independent audits. The
audit examined the accumulated state rather than the last change set alone.

| Dimension | Result |
|---|---|
| `CP-0009` findings closed | five of five, each verified against the implementation and the executed tests |
| Positive milestone promotion | reachable; executed in simulation and in a sealed snapshot of this checkpoint |
| Successor durability | green at every state of a three-checkpoint succession, then performed for real |
| Full suite, working repository | three hundred and sixty-three discovered, three hundred and sixty-three run, zero failures, zero errors |
| Full suite, clean clone at the subject tag | three hundred and sixty-three discovered, three hundred and sixty-three run, zero failures, zero errors |
| Canonical mandatory validators | every one exits zero in both environments |
| Green Keeper | `PASS`, measured against the canonical mandatory gate set, fingerprint still fresh |
| Delivery completeness | total coverage and total evidence coverage against an independently derived expected set |
| Engineering memory | valid; thirty lessons, twenty-eight guarded, twenty-nine guardrails all effective, no unresolved guardrail failure |
| Lesson preflight | fresh by recomputation; every derived requirement present in the matrix |
| History integrity | ten anchors re-derived from Git; every sealed checkpoint validates from its own tag |
| Adversarial position | every scenario defended over an accepted null-mutation control |
| Internal mirror audit for a checkpoint that corrects no audit | **FAIL**, and checkpoint validation requires it to pass — finding `CP11-F-001` |
| Gate 0 | not started, not present |

## Why the milestone does not pass

Everything the previous audit asked for was delivered, and the architecture it demanded works. One
control that the milestone did not change is nevertheless unusable for the state the protocol now
requires: `m0_mirror_audit.py` reports `FAIL` for any checkpoint that corrects no audit, because two
of its checks treat "nothing to audit" as a failure instead of as `NOT_APPLICABLE`, which is what the
role contract prescribes and what the schema already permits. Checkpoint validation requires a
passing mirror for every positive terminal status, so:

- this audit could not close at `MILESTONE_INDEPENDENT_AUDIT_PASS`, the status the subject's
  `NEXT.md` instructs it to use; and
- the first `GATE 0` delivery cannot reach `READY_FOR_REVIEW`, which was executed in a disposable
  clone rather than predicted.

This is the class the milestone has now met three times: a control whose positive path is not
reachable, and a required protocol transition that turns a mandatory gate red. `LSN-0024` and
`LSN-0029` both cover it and both are `GUARDED`, so the recurrence is a `GUARDRAIL_FAILURE` and the
guardrails themselves need investigation, not only the defect.

## Integration across the milestone

`M0` has a single Gate, so integration is between the controls rather than between Gates, and that
is where all three audits found their defects. The controls were examined as a system: the
attestation model and the checkpoint validator agree on which object carries a verdict; the anchor
rule has one implementation that the command-line tool, the validator and the suite all ask; the
count derivation and the documents that quote counts are cross-checked; the preflight, the
requirement derivation and the completeness audit share one expected set; and the assurance
fingerprint ties every gate result to the content it judged. The one seam that does not hold is
between the internal mirror audit and the statuses the validator gates on it.

## Residual limits, stated rather than implied

The independence of this audit is session independence. The trust model of a milestone verdict is
structural, not cryptographic: it requires a second sealed, tagged, anchored checkpoint authored as
the audit of an already sealed subject, and an actor with full control of the repository could forge
that relationship. Both limits are recorded in `docs/MILESTONE-VALIDATION.md` and in `RISKS.md`, and
no artifact in this repository claims more than they allow.

## Decision

`M0` = `REWORK_REQUIRED`. `SETUP-00` = `REWORK_REQUIRED`. `GATE 0 — FOUNDATION` = `BLOCKED`. The
single finding returns to the implementer with acceptance criteria and a regression scenario; no
product code was changed by this audit.
