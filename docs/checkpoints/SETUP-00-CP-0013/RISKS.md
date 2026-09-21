# Risks

## R1 — The independence of this audit is of the session, not of the tool

`FRESH_SESSION_INDEPENDENT_AUDIT` means a session with no memory of the implementing run. The tool,
the provider and the model are the implementer's. A defect that both runs share — a blind spot of
the model, or a wrong belief baked into the contracts both read — is not detected by this mechanism.

Mitigation: the limit is recorded structurally rather than described. `crossToolValidation` is
`NOT_AVAILABLE`, the attestation mechanism authorises only the fresh-session status, and validation
refuses `MILESTONE_EXTERNAL_PASS` derived from it. Residual risk accepted, visibly.

## R2 — The trust model is structural, not cryptographic

A milestone verdict requires a second sealed, tagged, anchored checkpoint authored as an audit of an
already sealed subject. That cannot be produced by editing one field, but an actor who controls the
whole repository can still recompute the chain. There is no signature and no external key.

Mitigation: none available inside this Gate. The limit is already written down in
`docs/MILESTONE-VALIDATION.md`, and the upgrade to signed attestations stays available. Risk carried
into `M1`.

## R3 — `NOT_APPLICABLE` is a new state and could become a habit

The repair of `CP11-F-001` made an empty applicable set a first-class outcome. The controls refuse
every misuse this audit could construct, but the risk is cultural as much as technical: a future
delivery may reach for an inapplicable dimension rather than satisfy it.

Mitigation: the state justifies itself — reason, expected count of zero, and the canonical source
the emptiness was derived from — and the validator re-derives that source rather than believing the
claim. `GRD-0030` guards the distinction. Watch the count of inapplicable dimensions across Gates:
a Gate whose mirror grows more inapplicable dimensions than its predecessor deserves a look.

## R4 — One test stops asserting in a repository at rest

`AuditAttestationModelTests.test_an_unsealed_subject_is_rejected` skips when every checkpoint
directory is sealed, which is the state an auditor checks out. The refusal branch it covers is then
unverified until the next delivery creates an unsealed checkpoint.

Mitigation: the case executes during every delivery, which is when the tooling changes; no guardrail
and no checklist row depends on it; the rest of its class executes unconditionally. Recorded as an
observation rather than a finding. It becomes a finding if a guardrail or a checklist row ever names
that method, or if the number of state-conditional skips grows.

## R5 — Gate 0 has no specification yet

`.iacode/policies/canonical-requirements.json` declares no requirements for `GATE 0`. Authoring that
specification is the first deliverable of that Gate. Until it exists, the Gate 0 transition is
proven against a synthetic specification inside a disposable repository only.

Mitigation: the transition simulation creates that specification in a throwaway clone and never in
this repository, and its ninth check asserts that no Gate 0 runtime tree exists here. Carried into
Gate 0 as its first task, not as a defect of this milestone.

## R6 — The counts of this audit describe this tree

Every derived count, fingerprint and measurement in this checkpoint describes the content it was
computed over. A later change to the code, the memory or the policies makes them stale, and the
controls say so rather than letting a stale number pass.

Mitigation: the Green Keeper, the completeness audit, the internal Red Team and the mirror audit all
record a scope fingerprint, and validation refuses a stale one. This is a property of the design,
recorded here so a reader does not mistake a refusal for a defect.
