# ADR-0065 — Self-qualification uses immutable product inputs, not checkpoint outputs

Status: Accepted
Date: 2026-10-22
Owners: GATE7 corrective M2 validation

## Context

Runtime-v5's whole49-stage verifier rejects its self-qualification snapshot at the unchanged64MiB
source ceiling. The committed tree has grown past that ceiling; approximately60MiB are accumulated
checkpoint outputs. The original rejection and all archived evidence remain preserved. Increasing
a security ceiling, deleting historical evidence, trimming tests or changing the expected verdict
would not resolve this input-domain mismatch.

The existing canonical assurance boundary deliberately excludes docs/checkpoints/ because recording
evidence cannot invalidate the product inputs that evidence describes. Those outputs have separate
whole-ledger, integrity, archive, secret-scan and immutable reconstruction controls. They are not a
deployable application root.

## Decision

Only the operator-owned IACode self-qualification scenario uses an immutable product-input view.
Resolve HEAD once, enumerate its complete Git tree and read its exact blobs in one Git batch. Omit only the
top-level docs/checkpoints/ output namespace already excluded by canonical assurance. Refuse if
canonical assurance treats that namespace as a required product input. There is no caller-supplied
include/exclude list, no working-tree substitution and no change to general workspace snapshots.

Keep every other committed path, including every project manifest, source, test, policy, migration
and root build input, byte-exact. Verify batch membership, object identities and lengths against the
independently enumerated Git tree before writing into a fresh empty destination. Do not use archive
or working-tree conversion filters: real initial controls rejected altered archive bytes. Bind the entire original tree and the
selection/exclusion inventories in a deterministic sidecar, and record the exact commit, counts and
bytes in the live proof. Unknown paths and future non-checkpoint projects remain included.

Do not change64MiB admission/read limits, workspace limits, policy, runner selection, applicability,
timeouts, assertion results, gate/stage membership or promotion rules. The complete canonical
quality/functional controls still run, including all16 gates, all49 stages, full ledger validation,
hostile review-bundle transport, fresh internal controls and post-commit sealing. No evidence is
removed from the repository or from the review payload. Independent M2 validation remains separate.

## Alternatives Considered

- Raise snapshot ceilings: changes product resource/security policy instead of correcting the
  self-qualification input domain.
- Delete/compress/rewrite old checkpoint evidence: destroys or changes immutable audit inputs.
- Hand-pick project roots or skip failed checks: lets the delivery shrink mandatory coverage.
- Read the live working tree: no longer proves the exact published subject.

## Consequences

The self-qualification snapshot no longer grows with archived observations. Actual product growth
still meets the same capacity refusal. Full original evidence remains available to its owning
validators, independently of the product snapshot. The view is not a general archive filter and
grants no new execution, network, storage, rights or training authority.

## Validation and Risks

Execute real Git controls for exact immutable bytes, all non-checkpoint files and future project
roots, dirty-worktree exclusion, checkpoint namespace confinement, deterministic identity and
failure on policy disagreement/nonregular inputs. Compare actual evaluator project/check selection
before and after the view, then execute the full live self-qualification and unchanged whole
assurance. The previous whole-tree rejection remains a red original, not a passing capacity test.

## Reversal Strategy

Replace the view only with equivalent immutable-input and complete-membership proof. No reversal
may rewrite historical subjects, weaken snapshot admission or waive the separate ledger controls.

## Related Artifacts

- [Canonical assurance boundary](../../scripts/development-ledger/ledger_common.py)
- [Original complete failure](../checkpoints/GATE-7-CP-0003/FULL-VERIFICATION-FAILURE-0001.json)
- [Live self-qualification](../../scripts/iacode/scenarios/quality_engine_e2e.py)
