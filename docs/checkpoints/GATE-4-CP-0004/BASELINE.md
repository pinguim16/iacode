# Baseline — Gate 4 fresh-session independent re-audit

## Immutable subject

- Checkpoint: `GATE-4-CP-0003`.
- Canonical tag: `refs/tags/iacode-checkpoints/GATE-4-CP-0003`.
- Sealed commit: `5d47200fde08c47b7a6410be2204b4c1b9fbadc1`.
- Content commit: `4d0cc8e3bb9a329e50af99cf58f01c19087c3433`.
- Implementing status: `READY_FOR_REVIEW`; independent review, Red Team and second-tool
  validation are pending.

## Pre-audit observations

- `python scripts/development-ledger/validate_checkpoint.py` returned `CHECKPOINT_VALID` before
  this audit checkpoint was created.
- The worktree was clean on `main`; local `HEAD`, `origin/main`, the local canonical tag and the
  published canonical tag all resolved to the sealed commit.
- The canonical tag's parent resolved to the declared content commit.
- The handed-off review archive exists at `artifacts/review/GATE-4-CP-0003.zip`, is 591,695 bytes,
  and has SHA-256 `197cd4c82b7e6fa75f51c72d7db3daf2e84cb7df03ac4028e0efa572a80562cd`.
- No divergence was observed, so `DIVERGENCE.md` is neither required nor created.

## Derived audit scope

The mandatory preflight considered 94 lessons, selected 93 and derived 93 lesson requirements.
Canonical derivation produced 198 requirements: 105 Gate 4 rows and 93 lesson rows. The auditor
will not reduce that denominator and will not accept the implementing checkpoint's claims as
independent evidence.

## Boundary

This run may add only the audit checkpoint, the audit attestation, the successor-owned integrity
anchor for the sealed subject, the textual `LATEST.md` pointer, and a generated review archive
outside Git. It may not change product code, product tests, canonical policy, engineering-memory
source, the sealed subject, historical tags, or any Gate 5 surface.
