# ADR-0057 — Build and verification root inputs follow subject-versioned assurance

Status: Accepted
Date: 2026-10-18
Owners: GATE 7 — packaging privacy and verification freshness

## Context

The current packaging privacy guard consumes `.dockerignore`, but the v1 root assurance policy
binds only `.gitignore` and `ruff.toml`. An actual isolated Git fixture changes build-ignore bytes
without changing its assurance fingerprint. The root Windows `verify.ps1` launcher is also an
executable verification input outside that set. ADR-0049 requires an explicit version decision
for root toolchain inputs rather than retroactive history reinterpretation.

## Decision

Introduce root assurance policy version 2.0.0 with the exact ordered set `.dockerignore`,
`.gitignore`, `ruff.toml`, and `verify.ps1`. Consume that version in the canonical fingerprint
implementation, including required root files even when Git ignores an untracked copy.
Retain the exact absent-policy and v1 semantics for historical subjects. Unknown versions,
narrowed/reordered/duplicated or additional undeclared root sets are refused. Future root inputs
require another explicit policy/version decision; callers cannot choose a smaller denominator.

Preserve every inherited scope assertion and its historical v1 fixture. Strengthen the current
owner assertion to the exact current canonical declaration plus the inherited minimum, instead
of freezing current legitimate growth to the old two-file set. Current Gate7 controls additionally
require both build-context and real Windows verification inputs.

## Evidence

G7-INT-022 and its decoded isolated diagnostic establish the omitted input and observed owner
cleanup. Executed causal red, real mutation/ignored/deletion, policy-shape/narrowing and preserved
legacy controls must precede local prevention. A new complete immutable subject and all ordered
internal controls remain required. The disposable scratch experiment is same-session preparation,
not canonical Gate acceptance or independent M2 validation.

## Alternatives Considered

- Add a caller-selected fingerprint extra: rejected; the mandatory set must be policy-owned.
- Expand every historical subject globally: rejected; genuine sealed fingerprints must retain
  their original interpretation.
- Accept the old two-file current assertion by omitting the new input: rejected as false freshness.
- Treat a material root edit as current because tests once passed: rejected.

## Consequences

Changing build-context privacy or the actual Windows verification launcher invalidates current
evidence. Source/memory must freeze before fresh whole proof. No old tag, sealed checkpoint,
mandatory gate, requirement set or independent verdict is changed.

## Risks

A new root input can be omitted unless its author follows this version boundary. Executed controls
cover every currently registered root and retain a stable inherited minimum; exact subject
transport and actual complete verification remain separate mandatory proofs.

## Reversal Strategy

A later authorized architecture decision may supersede the current version while preserving
historical versions and their tests. Never move tags, relabel stale evidence or narrow a mandatory
current set by a command-line argument.

## Related Artifacts

[ADR-0049](ADR-0049-root-assurance-inputs-follow-subject-policy.md);
[scope policy](../../.iacode/policies/assurance-scope.json);
[canonical consumer](../../scripts/development-ledger/ledger_common.py);
[Gate7 controls](../../tests/test_gate7_assurance.py); G7-INT-022; LSN-0150.
