# Diff Summary

Base commit: `90b67a7e0a11179465bc5c92dee22c78da36801f`, which is
`refs/tags/iacode-checkpoints/SETUP-00-CP-0010`.

## Outside this checkpoint

| Path | Change | Why |
|---|---|---|
| `.iacode/anchors/checkpoint-chain.json` | modified | The tenth anchor, for `SETUP-00-CP-0010`. A checkpoint cannot anchor its own tag, so its successor owes it; this audit is that successor. |
| `.iacode/attestations/M0-CP-0011.json` | added | The attestation this audit authored about the sealed subject. It names the subject, the commit its tag resolves to, this checkpoint as the auditor, the mechanism, the availability of cross-tool execution and the four results. It never names its own commit. |
| `docs/checkpoints/LATEST.md` | modified | Points at this checkpoint. |

No product script, test, schema, policy, canonical memory file, governing document, sealed
checkpoint or historical tag was modified. An auditor does not repair the delivery it judges.

## Inside this checkpoint

The audit matrix and its append-only execution record, the independent review, the adversarial
battery of this audit and its report, the milestone report, the machine-readable record of every
execution, the requirement matrix and completeness report of this checkpoint, its internal assurance
reports, the standard checkpoint ledger, and `audit-harness/`, which is kept here so every result
reproduces from a clean clone.

## Gate 0

Nothing. No Gate 0 artifact exists in this change set.
