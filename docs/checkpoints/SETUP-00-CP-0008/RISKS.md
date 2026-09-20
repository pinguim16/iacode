# Risks

- **The final `M0` audit has not run.** This checkpoint is internally green and externally
  unvalidated. Nothing here is a Gate verdict, and Gate 0 stays blocked.
- **The integrity anchors are tamper evidence, not cryptography.** They detect a moved tag, a
  rewritten commit, an unexpected tree and a broken chain link. An actor with full control of the
  repository can recompute the whole chain. The upgrade to signed anchors is available and not taken
  in SETUP-00.
- **The external attestation is structural, not cryptographic.** It makes an external PASS require a
  separate sealed, tagged, anchored audit checkpoint, which cannot be produced by editing one field.
  An actor able to author that checkpoint could still forge the relationship.
- **A checkpoint cannot anchor its own tag.** `SETUP-00-CP-0008` is anchored by its successor, so
  between this seal and the next checkpoint its own tag has no anchor. The gap is one checkpoint
  wide, it is refused for every predecessor, and it is inherent rather than accidental.
- **The internal Red Team and the mirror audit are not independent.** They are authored by the
  implementing run on the same tooling. They reduce what the external audit has to discover; they do
  not replace it, and the validator refuses any attempt to record them as an external verdict.
- **The attack battery attacks a model of the sealed state.** The fixture is a disposable clone with
  this checkpoint presented as sealed. It is faithful to the shape the seal produces, but it is a
  model, and a defect that only appears in the real sealing sequence would escape it. The end-to-end
  lifecycle test exists to cover that gap and is itself a fixture.
- **The derived expected set is only as good as its canonical sources.** If a future Gate's
  checklist omits a requirement, the derivation omits it too. The control removes the delivery's
  ability to shrink the set; it does not decide what the specification should contain.
- **A count is verified where it is stated in the canonical form.** Prose that states a number in
  another shape is not checked. The rule is deliberately narrow so that it is exact.
- **The Green Keeper, completeness, Red Team and mirror results are fresh only against the
  delivery-assurance scope.** A change to a checkpoint's own evidence does not invalidate them, by
  design, because recording evidence must not invalidate the evidence being recorded.
- **`LSN-0013` cannot be guarded from this repository.** An arbitrary machine's installation state
  is not observable here. It stays `CONFIRMED` and is carried by the mandatory preflight.
- **Sealed `SETUP-00-CP-0006` still contains the aggregate contradiction the audit found.** It is
  immutable, the contradiction is recorded as a closed finding, and the cross-check applies from
  `schemaVersion` `3.2.0` onward.
