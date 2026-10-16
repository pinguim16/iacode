# ADR-0049 — Root assurance inputs follow subject policy

- Status: Accepted
- Gate: GATE 5

## Decision and context

The existing assurance fingerprint covered source trees but not root `ruff.toml` or `.gitignore`.
Both influence Gate 5 checks/packages. Add a versioned `assurance-scope.json` with an exact closed
root-file set. Include existing root inputs even when ignored, so changing lint/ignore behavior
invalidates current evidence. Gate 5+ checkpoint validation requires this policy and refuses a
missing, unsupported or narrowed declaration. The independently authored control checks all cases.

Subjects without the new policy retain their old fingerprint semantics; no sealed predecessor is
rewritten or reinterpreted. Applying a global retroactive scope expansion would invalidate genuine
historical fingerprints, while caller-supplied extras alone would allow omission. This versioned
subject policy preserves history and makes current requirements mandatory. Future root toolchain
inputs require an explicit policy/version decision, not an ad hoc delivery exclusion.

## Related artifacts

- `.iacode/policies/assurance-scope.json`
- `scripts/development-ledger/ledger_common.py`
- `scripts/development-ledger/validate_checkpoint.py`
- `tests/test_gate5_clients.py`
