# Development Ledger Tools

These Python 3 tools use only the standard library and are portable across Windows and Unix-like systems.

## Create

```text
python scripts/development-ledger/new_checkpoint.py --gate GATE-0 --status IN_PROGRESS --phase "GATE 0 — Foundation"
```

The command allocates the next four-digit checkpoint ID, creates every mandatory file with truthful non-PASS defaults, and updates the textual `LATEST.md` pointer.

## Validate

```text
python scripts/development-ledger/validate_checkpoint.py
```

Exit code `0` means valid. Any nonzero exit means invalid. Validation checks required and nonempty files, JSON parsing, bound JSON Schemas, command JSONL, file manifest structure, canonical status, branch, commit, dirty state, secret-shaped values, provenance, quality, handoff, next action, and the `LATEST.md` target.

Dirty-state relaxation is internal to `finalize_checkpoint.py` and is not exposed by the validation CLI, so unrelated working-tree changes cannot be hidden from a normal validation.

A checkpoint declaring `schemaVersion` `2.0.0` is additionally checked for a file inventory that
matches the real change set since `baseCommit` with bound content hashes, unique command identifiers,
quality verdicts backed by resolvable evidence references, and a structured `secondToolValidation`
state. A `1.0.0` checkpoint keeps the rules it was sealed under.

Validation also runs from a detached checkout of a checkpoint's own canonical tag, which is how a
second tool inspects an immutable reference. That mode requires a clean worktree and an existing tag
that resolves to the checked-out commit.

## Finalize

```text
python scripts/development-ledger/finalize_checkpoint.py --status READY_FOR_REVIEW
python scripts/development-ledger/finalize_checkpoint.py --status GATE_PASS --commit-ref refs/tags/iacode-checkpoints/SETUP-00-CP-0001
```

Finalization records timestamps, expects the checkpoint to become clean after commit, and performs a pre-commit validation. A Gate-closing checkpoint uses a namespaced tag reference: commit the result, create that tag at the resulting commit, and then run the validator normally. The tag binds the checkpoint to one immutable Git object without requiring a commit to contain its own hash.

Every attempt appends its own record, with its exit code, to the checkpoint's `COMMANDS.jsonl`. A
failed attempt restores the previous metadata and keeps its record, including a sanitized summary of
the validation errors, so the correction that followed stays visible. The successful attempt is
recorded before the inventory hashes are sealed. For `2.0.0` checkpoints, finalization re-derives
every declared hash from the repository, but it never adds or removes a declaration: an incomplete
manifest fails finalization until the author declares the missing paths. Finalization requires an
attached branch.

## Redact

```text
python scripts/development-ledger/redact_secrets.py input.txt
python scripts/development-ledger/redact_secrets.py input.txt --in-place
```

Standard output is the safest default. In-place mode writes a redacted temporary replacement; it never prints the original value.

## Schema scope

`checkpoint.schema.json` validates `STATE.json`; run metadata, command lines, tests, quality, and provenance each have a bound schema. `decision.schema.json` defines future structured decision exports while ADRs remain the canonical Markdown records. `experience.schema.json` is reserved for Gate 6 and later and implements no runtime.
