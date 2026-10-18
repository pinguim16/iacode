# ADR-0056 — Minimal protocol fixtures inherit only control contracts

Status: Accepted
Date: 2026-10-18
Owners: GATE 7 — inherited protocol assurance and source ownership

## Context

The minimal protocol builder copies all of `.iacode`, including the new deployment-owned
curator source root. Its README references an actual owning ADR absent from the minimal
fixture. The actual MIR-015 report retained by cmd-0110 explains five setup errors. Copying
the whole family could also copy operator content unrelated to a protocol simulation.

## Decision

Construct the minimal fixture from explicit canonical control asset families: agents,
policies, schemas, templates, VERSION and the public attestations README. Keep the ledger
and its declared packages/common dependency through the existing shared runtime copier.
Do not inherit curator sources, real memory, anchors, unrelated attestations or arbitrary
new operational directories. The fixture creates its own history, lessons and attestations.

Keep the actual requirement, Green Keeper, completeness, Red Team, mirror, finalizer and
sealer execution. No applicable set, production check or report is replaced or waived.
Retained-contract broken links must still cause the actual mirror/finalizer to refuse.

The producer owns a shared `promotion_repository(workdir)` locator. Both the actual positive
promotion builder and its diagnostic use it. Archive safe original mirror bytes before any
interpretation and before the owned temporary repository is removed.

## Evidence

G7-INT-015/017; original full runtime-v1 failure; cmd-0103/0104 setup refusals; cmd-0105
zero-capture failure; exact original MIR-015 from cmd-0110. Positive promotion/succession,
owner-data isolation, retained-link refusal and original-byte/cleanup controls are required
after implementation. No current successful correction is asserted by this ADR.

## Alternatives Considered

- Remove links from the real operator documentation or disable MIR-015: rejected.
- Copy unrelated deployment payloads and their complete documentation graph: wrong boundary.
- Fabricate a successful mirror or shrink the fixture's mandatory invocation: rejected.
- Duplicate the producer's child-path literal in diagnostics: recreates evidence-loss risk.

## Consequences

The fixture inherits control contracts, not the real project's runtime data or verdicts.
New control dependencies must be explicit and exercised by real positive protocol paths.
Production curated-source behavior, grants and the original source directory remain unchanged.

## Risks

An explicit asset boundary can omit a future control dependency; the real positive simulations
must expose that omission. It does not claim that an arbitrary repository copy is privacy-safe.

## Reversal Strategy

Extend the reviewed control asset set when a real dependency requires it and execute positive
and adverse transitions. Never include deployment data or real approvals as a shortcut.

## Related Artifacts

promotion_fixture.py; diagnostic producer capture; LSN-0093/0135/0148; current Gate7 findings.
