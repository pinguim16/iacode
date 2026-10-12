# ADR-0034 — Command inputs must cross Git transport

Status: Accepted
Date: 2026-10-11
Owners: GATE 4 — Quality Engine

## Context

`GATE-4-CP-0006` was sealed, tagged and pushed after local validation, but its canonical tag failed
in a fresh remote clone. One command record declared a generated review ZIP under `.git/` as an
input. The archive existed while the command ran, carried a digest and was intentionally excluded
from source control. Git does not classify its own metadata paths through `git check-ignore`, so the
recorder and validator mistook local presence for publication portability.

The pre-existing compatibility rule is still necessary: older sealed checkpoints contain generated,
ignored inputs whose content is digest-bound. Reinterpreting the schema they were sealed under would
break historical evidence without making those old artifacts appear in a checkout.

## Decision

Checkpoint schema `3.3.0` adds a forward-only invariant: every path in a command record's `inputs`
array must be eligible for the checkpoint's Git transport. Paths under `.git`, absolute or escaping
paths, and ignored paths are refused even when they exist locally and have a digest. An untracked,
non-ignored path is provisionally eligible during implementation because the file inventory and the
checkpoint commit must carry it before sealing.

One shared classifier owns the rule. Automatic input detection excludes local-only paths; an
explicit `--input` that names one is rejected before the command executes and the rejected attempt
is still recorded; checkpoint validation independently refuses a manually constructed record.

Schemas through `3.2.0` keep their prior compatibility behavior: a missing ignored or Git-metadata
input may be judged by a valid content digest. That exception does not make the generated artifact
review evidence. New review-bundle commands cite the versioned validation report and manifest; the
ZIP remains an output outside Git.

## Consequences

A checkpoint created under `3.3.0` cannot seal successfully when its command evidence depends on a
machine-local archive or repository metadata. The same classifier applies whether the input was
auto-detected, explicitly supplied or written directly into a record. Existing sealed history stays
interpretable under its own schema, including CP0006 when current tooling performs historical
compatibility checks, but CP0006 remains the immutable failed publication attempt and is not reused
as the Gate verdict.

The rule does not prove that an eligible untracked input will be committed. `FILES.json`, final Git
state validation and detached-tag validation own that later transition.

## Alternatives considered

Moving or rebuilding the CP0006 tag was rejected because published checkpoint references are
immutable. Committing generated ZIP archives was rejected because review transports are outputs,
not source. Treating every content digest as sufficient was rejected because a reviewer could not
re-run the command without its input. Rejecting legacy ignored inputs retroactively was rejected
because schema contracts are versioned and sealed history must remain readable.
