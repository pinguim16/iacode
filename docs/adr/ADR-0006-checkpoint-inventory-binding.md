# ADR-0006 — Bind the checkpoint file inventory to the repository

Status: ACCEPTED
Date: 2026-09-20
Owners: IACode maintainers

## Context

`FILES.json` claims which files a checkpoint created, modified, and deleted. Until now the strong
completeness and hash checks ran only when `baseCommit` was `UNBORN`, so a delta checkpoint could
omit a changed path, or declare a path whose content had since changed, and still validate. An
independent review reproduced both cases against the sealed `SETUP-00-CP-0002`: removing a manifest
entry and silently altering a tracked file both returned `CHECKPOINT_VALID`. The manifest was
therefore a human assertion, and the contract forbids treating an assertion as evidence.

A naive fix fails on self-reference: a file cannot contain its own hash, and the finalization step
mutates checkpoint metadata after the manifest is written.

## Decision

For `schemaVersion` `2.0.0`, validation recomputes the change set between `baseCommit` and the
validated tree with Git and requires `FILES.json` to match it exactly.

- Every added, modified, or deleted path is declared exactly once, with a reason.
- An undeclared change and a declared non-change are both errors, as is a category mismatch.
- Added and modified paths carry `hashAfter`, verified against the validated content.
- Modified and deleted paths carry `hashBefore`, verified against the content at `baseCommit`.
- A deleted path must be absent and must not carry `hashAfter`.
- Hashes normalize CRLF to LF before hashing, so a checkout with `core.autocrlf` still validates.

`finalize_checkpoint.py` re-derives the hashes from the repository but never invents a declaration:
a missing or extra path is reported and finalization fails until the author corrects the manifest.

### Exclusion set

Exactly one file is excluded from content hashing:

| File | Why | Replacement control |
|---|---|---|
| `<checkpoint>/FILES.json` | Writing its own hash into itself changes that hash. | Required presence, schema validation, its own inventory rules, and the immutable checkpoint commit and tag. |

The exclusion is declared once, in code, as `INVENTORY_SELF_REFERENTIAL_FILES`, and is covered by
tests. Every other checkpoint metadata file, including `COMMANDS.jsonl`, `STATE.json`,
`RUN-METADATA.json`, `STATUS.md`, and `HANDOFF.md`, is hashed like any other file. Finalization
orders its writes so those hashes are sealed after the last mutation.

This exclusion is safe because it is not the only binding on `FILES.json`: a handoff-ready checkpoint
is anchored to an immutable namespaced tag, and the tag fixes the content of every file in the tree,
including the manifest. The exclusion removes a redundant self-check, not the integrity guarantee.

## Alternatives Considered

- Store the manifest hash in a sibling file. Moves the self-reference rather than removing it, and
  adds a required file whose own integrity needs the same argument.
- Hash the manifest with its hash field blanked. Depends on exact serialization and is brittle
  across formatters.
- Keep the manifest advisory and rely on review. Rejected: it is precisely the control that failed.

## Consequences

Authors must declare every changed path before finalization; the tool will not guess. Sealed `1.0.0`
checkpoints keep their original rules and stay valid.

## Risks

An author may declare a path with a misleading reason; reasons remain a review concern, not a
machine-checkable one. Very large change sets make the manifest long.

## Reversal Strategy

The rules are gated on `schemaVersion`, so reverting means issuing a new version with different
inventory rules; sealed checkpoints are unaffected either way.

## Related Artifacts

`scripts/development-ledger/validate_checkpoint.py`, `scripts/development-ledger/finalize_checkpoint.py`,
`scripts/development-ledger/ledger_common.py`, `docs/CHECKPOINT-PROTOCOL.md`,
`tests/test_development_ledger.py`.
