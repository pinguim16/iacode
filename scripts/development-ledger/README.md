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

## Finalize

```text
python scripts/development-ledger/finalize_checkpoint.py --status READY_FOR_REVIEW
python scripts/development-ledger/finalize_checkpoint.py --status GATE_PASS --commit-ref refs/tags/iacode-checkpoints/SETUP-00-CP-0001
```

Finalization records timestamps, expects the checkpoint to become clean after commit, and performs a pre-commit validation. A Gate-closing checkpoint uses a namespaced tag reference: commit the result, create that tag at the resulting commit, and then run the validator normally. The tag binds the checkpoint to one immutable Git object without requiring a commit to contain its own hash.

## Redact

```text
python scripts/development-ledger/redact_secrets.py input.txt
python scripts/development-ledger/redact_secrets.py input.txt --in-place
```

Standard output is the safest default. In-place mode writes a redacted temporary replacement; it never prints the original value.

## Schema scope

`checkpoint.schema.json` validates `STATE.json`; run metadata, command lines, tests, quality, and provenance each have a bound schema. `decision.schema.json` defines future structured decision exports while ADRs remain the canonical Markdown records. `experience.schema.json` is reserved for Gate 6 and later and implements no runtime.
