# Next

## Required next action

Perform a **fresh-session independent M1 audit** of the sealed corrective checkpoint
`GATE-3-CP-0005`, in a new audit checkpoint expected to be `GATE-3-CP-0006`.

The audit must treat `GATE-3-CP-0005` as an immutable subject, anchor it in
`.iacode/anchors/checkpoint-chain.json`, validate it locally and from the authorised remote, and
independently attack the closure of `M1-F-004`. In particular, it must run the live npm and PyPI
advisory scan against the sealed lock graph; unavailable sources, Critical findings and High
findings remain blocking.

It must also evaluate M1 as a whole: accumulated Gate 0–3 completeness and integration,
architecture, regressions, quality, documentation, lessons and guardrails, Red Team and any
cross-Gate inconsistency. Its attestation must name the sealed subject; this checkpoint is never
rewritten to become approved.

Before opening the audit, from a clean checkout:

```powershell
python scripts/development-ledger/validate_checkpoint.py
python scripts/development-ledger/remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0005
python scripts/development-ledger/milestone_status.py --milestone M1
```

The last command must still report that M1 is not passed before the new attestation.

## What must not happen

- `GATE 4` does not start before a fresh-session M1 PASS and explicit owner authorisation.
- Internal evidence from this implementing run is not reclassified as independent validation.
- The sealed checkpoint, canonical tag, audit denominator or dependency severity policy is not
  rewritten to obtain a pass.
