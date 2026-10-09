# Diff Summary

This is an audit-only checkpoint over immutable subject `GATE-3-CP-0005`.

## Modified outside the checkpoint

- `.iacode/anchors/checkpoint-chain.json` — adds the successor-owned anchor for the sealed subject.
- `docs/checkpoints/LATEST.md` — points to `GATE-3-CP-0006`.

## Created outside the checkpoint

- `.iacode/attestations/M1-CP-0006.json` — fresh-session independent M1 attestation.

## Created inside the checkpoint

- Cold-start, published-history, dependency, full-verification, clean-clone, configured-model,
  cross-Gate, forged-result, SSE, documentation/memory and R-G3-001 evidence.
- The 19-attack independent Red Team, its readable report and the preserved first invalid-reader
  attempt.
- The 198-row requirements matrix, completeness report, canonical counts, findings and frozen
  32-row audit matrix.
- Review, milestone, final, handoff, risk, provenance and status documents.
- Audit-only harnesses that produce the evidence and the post-seal review bundle.

## Explicitly unchanged

No file under `apps/`, `services/`, `packages/`, `infra/`, `scripts/`, `tests/`, `prompts/` or the
canonical policy set changed. No sealed checkpoint or historical tag changed. Gate 4 was not
started.
