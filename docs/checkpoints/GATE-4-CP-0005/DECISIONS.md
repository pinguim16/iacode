# Decisions

## D-001 — Isolate verification by checkout-owned Compose identity

The canonical verifier owns a project name derived from its resolved checkout and asks Docker for
ephemeral published ports. It cleans only that project before and after execution. This preserves a
developer's `iacode` stack and prevents a transport clone from reusing another checkout's runtime.

## D-002 — Observe asynchronous scrape state; never retry the judged action

Infrastructure and smoke use one bounded target observer whose deadline is derived from the
versioned Prometheus scrape interval. The observer only reads Prometheus until it has observed the
required target state; it does not restart services or rerun a failed check.

## D-003 — Keep the canonical denominator and security controls intact

The 42 verification stages retain their order and membership. The G4-X7 scanner path, scanner
failure control and legacy-object resolution are not weakened or replaced.

## D-004 — Separate pre-final published identity from final detached validation

Before the canonical checkpoint tag exists, the representative transport clone remains attached to
`main` at the exact remote commit so checkpoint validation judges a legitimate in-progress
checkpoint. Final validation still uses a detached checkout of the sealed canonical tag.

## D-005 — Include executable checkpoint harnesses in the UTF-8 guard

Executable evidence harnesses under the current checkpoint use `use_utf8_stdout` and enter the same
repository control as ordinary scripts. Evidence transport is not exempt from output portability.
