# Diff Summary

## Purpose

This corrective checkpoint closes independent finding `G4-F-001` / attack `G4-X7`: quality
evidence containing prohibited credential-shaped bytes could previously reach durable storage
before the runtime containment boundary rejected it.

## Product changes

- Added a shared canonical secret-scanning module in `packages/common` and made the development
  ledger consume the same taxonomy.
- Moved evaluator containment ahead of every evidence-store interaction and made scanner errors
  fail closed.
- Added sanitized activity-level handling that emits no evidence or findings and derives `FAIL`.
- Rechecks existing evidence objects when they are resolved.
- Added focused persistence and workflow regression coverage, including exact activity-to-store
  bytes, zero writes, scanner failure, legacy resolution, and marker non-disclosure.
- Hardened the sandbox process sweep after the final Green Keeper reproduced an intermittent
  zombie/PID-cgroup race, with deterministic regression coverage.

## Delivery-system changes

- Extended the Gate 4 Red Team from A-P to mandatory attacks A-Q, with Q replaying `G4-X7` against
  the live evaluator path.
- Added bounded compatibility parsing for the sealed predecessor finding format.
- Updated disposable promotion fixtures to include the shared common package.
- Corrected deterministic review-bundle collection so unchanged tracked migrations, schemas, and
  policies remain available to reviewers without being misrepresented in the Git changeset.
- Recorded four new lessons and guardrails for pre-persistence containment, sealed-audit parsing,
  copied-runtime package dependencies, and complete review context; recorded recurrences instead
  of concealing them.
- Updated architecture, development, runbook, version, ADR, closure, requirements, test, quality,
  and checkpoint evidence.

## Scope boundary

No Gate 5 implementation was started. This checkpoint requests independent review of Gate 4 only
and does not grant `GATE_PASS`.
