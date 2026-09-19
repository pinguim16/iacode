# IACode

IACode is a planned private, autonomous, general-purpose, self-improving software engineering platform. This repository currently contains only the development control plane established by **SETUP-00**; it does not contain the Gate 0 runtime.

Begin with [START-HERE.md](START-HERE.md). The repository is the source of truth; chat history is not.

## Current boundary

- Current phase: `SETUP-00 — Development Control Plane`.
- Current Gate: `SETUP-00`.
- Runtime Gates: not started.
- Canonical agent definitions: `.iacode/agents/`.
- Latest reconstructible state: `docs/checkpoints/LATEST.md`.

## Quick validation

```text
python scripts/development-ledger/validate_checkpoint.py
python -m unittest discover -s tests -v
```

