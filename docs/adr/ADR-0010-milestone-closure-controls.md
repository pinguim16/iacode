# ADR-0010 — Milestone closure controls

- Status: Accepted
- Date: 2026-09-20
- Gate: SETUP-00
- Checkpoint: SETUP-00-CP-0008
- Supersedes: nothing. Extends ADR-0006, ADR-0007, ADR-0008 and ADR-0009.

## Context

The first independent `M0` milestone audit, recorded in `SETUP-00-CP-0007`, returned
`REWORK_REQUIRED` with eleven findings and eight escaped attacks out of twenty-six. The failures
were not a list of unrelated defects. Seven of them are the same mistake in seven places:

> A control that takes its own scope, its own denominator or its own verdict from the thing it is
> supposed to constrain is not a control.

- The Green Keeper asked its caller which gates were mandatory, so `--gates ""` produced a PASS.
- The completeness audit asked the submitted matrix how many requirements existed, so deleting one
  produced a smaller denominator and a forged `100%`.
- The checkpoint asserted its own external validation, so an implementing run reached
  `MILESTONE_EXTERNAL_PASS` with the review and the Red Team still pending.
- The promotion rules were attached to one status, so every other positive status began life with
  no rules.
- The preflight was compared with the state that stored a copy of its own counts, so a retired
  lesson left a stale selection in place.
- A lesson's control reference was type-checked but never resolved, so a guardrail could name a
  test that does not exist.
- Sealed history's expected values lived inside mutable checkpoint content, so a coordinated tag
  and content move left nothing to contradict.

## Decision

Every control derives its scope, its expectation and its verdict from a source the delivery does
not own, and the derivation is recomputed during validation.

1. **One promotion invariant.** A single set of checks is evaluated for every positive terminal
   status. Each status adds requirements on top of it; none replaces it.
2. **A closed mandatory gate registry.** `.iacode/policies/quality-gates.json` decides which gates
   are mandatory. An invocation may extend a run and can never shrink it. Every cycle records the
   mandatory set it was measured against.
3. **A derived expected requirement set.** The canonical Gate specification is re-parsed, the
   lesson preflight is read, and the findings and mandatory attacks of every open audit are parsed
   from the sealed audit reports. Each matrix row carries an anchored `sourceRef`, and the expected
   and declared sets are compared exactly.
4. **An external audit attestation.** `MILESTONE_EXTERNAL_PASS`, `secondToolValidation = PASSED`
   and `milestone.status = PASSED` are derived from an attestation naming an audit checkpoint that
   is sealed, anchored, and different from the checkpoint being promoted.
5. **Input fingerprints.** A derived artifact records a content fingerprint of the inputs that
   produced it, and validation recomputes both the fingerprint and the artifact. Staleness is a
   computation, never a date.
6. **Resolved references.** Every lesson control, evidence path and provenance locator is resolved
   against the repository and the discovered suite, and the whole lesson object is scanned for
   secrets at any depth.
7. **A guardrail registry with measured effectiveness.** A `GUARDED` lesson names a registered
   guardrail; the guardrail names an executable control and the tests that fail when it is removed.
8. **A hash-linked integrity anchor chain.** Every sealed checkpoint's tag, commit and tree are
   anchored in an earlier checkpoint, and each anchor binds its predecessor's digest.
9. **Derived counts.** Every count used as evidence is derived once into `COUNTS.json` and verified
   wherever a report states it.
10. **A monotonic, post-commit seal.** The content commit is validated with a clean worktree, that
    validation is recorded against the commit it judged, and the evidence commit may contain
    nothing but the append-only records it wrote.
11. **Internal assurance before external audit.** The delivery runs the full attack battery and a
    mirror of the milestone audit itself, and records both without ever calling either of them
    independent validation.

## Trust model, stated without overclaiming

The integrity anchors and the external attestation are **structural and tamper-evident inside the
local trust model**. Neither is a signature. An actor with full control of the repository can
recompute the anchor chain, and can create a second checkpoint and tag it. What both controls
remove is the class of failure the audit actually demonstrated: a coordinated edit that leaves the
ledger internally consistent, and a verdict that a delivery can write about itself by editing one
field. No document in this repository claims more than that.

## Version dispatch

The controls arrive with checkpoint `schemaVersion` `3.2.0`, requirements matrix and completeness
report `schemaVersion` `2.0.0`, lesson preflight `schemaVersion` `2.0.0`, and engineering memory
policy `2.0.0`. Sealed checkpoints keep validating under the rules of their own versions, which is
the invariant `LSN-0012` exists to protect and which
`HistoricalCheckpointCompatibilityTests` and `HistoricalClosureCompatibilityTests` prove for every
sealed tag.

## Consequences

- A delivery cannot be offered while any audit finding is open, any mandatory attack escapes, any
  guardrail is ineffective, any gate result is stale, or any stated count contradicts its
  derivation.
- Sealing takes two commits: the content, then the append-only evidence of its validation. The
  second commit is constrained to exactly the files the sealing tool writes.
- A checkpoint cannot anchor its own tag. Its successor anchors it, and a checkpoint that fails to
  anchor a sealed predecessor is refused.
- The mandatory gate set now includes checkpoint integrity, so a repository whose sealed history
  has drifted cannot produce a green delivery.

## Alternatives considered

- **Cryptographic signatures for the anchors and the attestation.** Rejected for SETUP-00: there is
  no key management, no trust anchor and no distribution story yet, and claiming cryptographic
  assurance without them would be exactly the kind of overstatement this Gate exists to prevent.
  The trust model is documented so the upgrade stays available.
- **Letting `--gates` narrow a run for debugging.** Rejected: the audit's escape was precisely an
  argument narrowing a control. A diagnostic that cannot produce a recorded verdict would be
  acceptable; an argument that can is not.
- **Correcting the sealed `SETUP-00-CP-0006` aggregate.** Rejected: sealed checkpoints are
  immutable. The contradiction is recorded as a closed finding, and the cross-check applies from
  `3.2.0` onward.
