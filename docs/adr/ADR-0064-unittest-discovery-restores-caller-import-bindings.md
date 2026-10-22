# ADR-0064 — Unittest discovery restores caller import bindings

Status: Accepted

Execution and whole acceptance remain evidence obligations, not consequences of this decision.

## Context

The current validator counts cases in an inspected checkout before reconstructing its declared
review archive. Actual native-import diagnostic run0002 for GATE-5-CP-0001 selected that inspected
tag's old review_bundle module: imported test modules had prepended the inspected helper paths.
Both immutable producers then failed with Filename too long. Run0001, with the current reader
preloaded, reconstructed the exact declaration. This is a distinct consumer-import failure, not a
reason to rewrite historical producers or declare the earlier complete failed cycle green.

See [recorded cause](../checkpoints/GATE-7-CP-0003/IMPORT-ISOLATION-001.json),
[native original output](../checkpoints/GATE-7-CP-0003/declaration-diagnostics/run-0002/stdout.log),
and [real causal red](../checkpoints/GATE-7-CP-0003/causal-attempts/discovery-isolation/run-0001.json).

## Decision

Keep real unittest discovery, its unchanged default discovery scope, inherited and skipped cases,
and distinct physical case identities. Use a fresh loader rather than the mutable shared default.
Within the single-threaded counting operation, snapshot caller sys.path and sys.modules bindings;
temporarily evict colliding inspected top-level Python modules/packages so a different checkout's
cached tests cannot become the measured suite. Restore original container identities, paths and
all prior module-cache bindings, and remove newly added module bindings in a finally block.

A loader collection error is not one successfully discovered case: refuse it with LedgerError.
No case body is run to derive the denominator. No Git setting, historical declaration, mandatory
gate, archive member, promotion rule, or counted suite is changed.

This is a scoped import-binding transaction for trusted repository tooling, not a security sandbox
for arbitrary hostile Python. It does not roll back filesystem writes, existing module globals,
parent-package attributes or arbitrary interpreter mutations. The validator remains single-threaded;
concurrent unrelated imports in the same interpreter are outside this contract. The later CLI audit
still requires its own process/workspace isolation.

## Alternatives and consequences

Preloading review_bundle alone would hide this particular late import while leaving other consumers
and repeated-root counts vulnerable. Static approximation would change the real unittest denominator.
A new subprocess collector could provide stronger interpreter separation but would require a separate
owned-process, lifecycle and minimal-fixture dependency contract; that larger migration is not hidden
inside this corrective transport repair.

Actual positive, adverse, collision, repeated-root, refusal and finally-path controls must pass.
Then run unpreloaded complete current validation on the unchanged Gates5/6/7 tags and repeat whole
immutable assurance on a newly published subject. Earlier failed outputs and tags remain immutable;
local controls do not grant independent milestone approval.
