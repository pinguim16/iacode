# Decisions

## D1 — The verdict is carried by this checkpoint, about a sealed subject

`SETUP-00-CP-0012` was not touched. Its tag still resolves to the commit it resolved to before this
audit existed, its tree is unchanged and its `STATE.json` still records `READY_FOR_REVIEW` with
`externalAttestation` `NONE`. This checkpoint anchors it, carries
`.iacode/attestations/M0-CP-0013.json` about it, and takes the milestone verdict itself.

Adding the audit makes nothing in the subject stale: a sealed checkpoint is validated from its
canonical tag, and that tree does not contain a file created afterwards. The clean-clone run at the
subject tag, performed after this checkpoint existed, reproduced every one of the subject's own
results.

## D2 — The mechanism is fresh-session, not cross-tool, and is recorded as such

The auditing tool, provider and model are the same as the implementer's. This run has no memory of
the implementing run, which is session independence and nothing more. The attestation therefore
records `validationMechanism: FRESH_SESSION_INDEPENDENT_AUDIT` and
`crossToolValidation: NOT_AVAILABLE`, and the status it authorises is
`MILESTONE_INDEPENDENT_AUDIT_PASS`. `MILESTONE_EXTERNAL_PASS` is refused for this mechanism, which
this audit executed as an attack rather than assumed.

## D3 — Every conclusion about the mirror comes from running the mirror

`CP11-F-001` survived a passing rehearsal because a simulation wrote the artifact the tool would
have produced. This audit therefore relies on no mirror artifact it did not cause to be produced by
executing `m0_mirror_audit.py`. The six applicability states were re-executed by this audit's own
probe, independently of the delivery's `mirror_semantics_validation.py`, and the delivery's control
was executed as well so that both are on the record.

## D4 — The independent derivations do not import the product tooling

`audit-harness/derive_expected.py`, `resolve_evidence.py` and `verify_memory.py` re-read the Gate
checklist, the audit registry, the sealed reports, the preflight, the matrix, the memory and the
guardrail registry with their own readers. Agreeing with `policies.py`, `delivery_assurance.py` and
`lessons.py` therefore means two independent readers agreed.

The first draft of `derive_expected.py` derived six findings and thirty-seven mandatory attacks for
the subject where the sealed sources name one and twelve. It was wrong, not the delivery: an audit
report re-confirms the previous audit's findings under a heading of its own, and only its own
`## Findings` section raises work for the corrective delivery; a battery table states mandatory or
additional per row in its `Category` column. Both rules are the documents', and the corrected reader
agrees exactly. The wrong first result is recorded here because an audit that hides its own
corrections is not auditable.

## D5 — The reverse escape was attacked, not assumed closed

Making `NOT_APPLICABLE` reachable opens the mirror-image defect: a delivery that declares a
dimension inapplicable rather than satisfying it. This audit attacked that state directly — an
inapplicable dimension with no reason, one over work the registry still names, one carrying items,
one under the report version that cannot justify one, one counted as a pass, and every dimension
declared inapplicable at once — and each was refused with the message the model predicts.

## D6 — Deleting the audit from the registry does not buy a pass

The applicable set is derived from the audit registry, so the obvious escape is to delete the entry.
This audit executed it. The two registry-bound dimensions do become `NOT_APPLICABLE`, and the
overall mirror still fails, because the expected requirement set shrinks with the registry and the
completeness dimension compares the anchored declared set against it, and because changing a policy
file makes the last green Green Keeper cycle stale. The escape is closed twice over and by controls
that were not written for it.

## D7 — The one skip in the suite was investigated and is not raised as a finding

The suite runs 410 cases with one skip:
`AuditAttestationModelTests.test_an_unsealed_subject_is_rejected`, skipped because every checkpoint
directory in a sealed checkout is sealed. The skip is state-conditional and inverts with the
lifecycle: during any delivery the current checkpoint is unsealed and the case executes, and it
skips only in a repository at rest, which is what an auditor checks out. No guardrail and no
checklist row names that method, the class it belongs to is otherwise fully executed, and the
subject's recorded "0 skipped" was true of the pre-seal tree it measured. It is recorded as an
observation with the condition that would promote it, not as a finding.

## D8 — This audit corrects no audit, and that is the proof

No registered audit names `SETUP-00-CP-0013` as its corrective delivery, so its own applicable set
is empty and its own mirror records the two registry-bound dimensions as `NOT_APPLICABLE`. Under the
defect this checkpoint could not have existed in a valid state. The repair is therefore not only
simulated: the audit that judges it is itself the first real delivery to depend on it.
