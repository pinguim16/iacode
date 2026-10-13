# ADR-0036 — Pre-seal validation binds an explicit subject

Status: Accepted
Date: 2026-10-12
Owners: GATE 4 — Quality Engine

## Context

The CP0009 verifier checked out its published implementation tag detached so every stage measured
one immutable transported commit. Checkpoint validation nevertheless required the not-yet-created
canonical checkpoint seal tag. Creating that tag before assurance would falsely present unfinished
content as sealed; validating an attached mutable branch would abandon the verifier's exact-subject
contract.

The repository already distinguishes pre-seal verification inputs under `iacode-subjects/` from
sealed checkpoint identities under `iacode-checkpoints/` and retained historical evidence under
`iacode-preserved/`. Validation did not yet express that distinction.

## Decision

A clean detached checkpoint with `status=IN_PROGRESS`, `dirty=false`, and symbolic
`currentCommit=HEAD` may validate when an exact tag under `refs/tags/iacode-subjects/` resolves to
the checked-out commit and the tag name begins with the checkpoint identifier. This is a read-only
pre-seal verification mode.

Every other detached symbolic-HEAD checkpoint continues to require its own canonical
`refs/tags/iacode-checkpoints/<checkpoint>` tag. In particular, a subject tag can never satisfy a
handoff-ready, terminal, or sealed checkpoint. Attached validation and finalization rules are
unchanged.

## Consequences

The full verifier can validate the exact published bytes it is already measuring without creating
a premature seal identity. The tag namespace and checkpoint-name binding prevent an unrelated
subject from authorizing the checkout. The canonical tag remains the only detached identity that
can support sealing or handoff.

## Alternatives considered

Creating the checkpoint tag before assurance was rejected because it would classify an unfinished
subject as sealed. Running checkpoint validation from an attached branch was rejected because the
branch can move between publication and measurement. Accepting any subject tag was rejected because
it would not bind the detached commit to the checkpoint being validated.
