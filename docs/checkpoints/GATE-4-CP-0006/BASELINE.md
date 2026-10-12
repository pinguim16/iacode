# Baseline — Gate 4 final independent audit

## Immutable subject

- Subject checkpoint: `GATE-4-CP-0005`.
- Canonical tag: `refs/tags/iacode-checkpoints/GATE-4-CP-0005`.
- Sealed commit: `c631270e49c095a9777825c0bc18818694c07ffb`.
- Content commit: `cac77ddef9c351ce828442d9312db69083aab81e`.
- Sealed tree: `cc63f56a6d49caf8aa3f137d00dbf15f8c271719`.
- Declared review bundle SHA-256:
  `bb130be4e4e871af158bb71b0bc4c0f0a1da73af50a5db74df49f870b2d14d59`.

## Preflight observations

- `validate_checkpoint.py` returned `CHECKPOINT_VALID` before this checkpoint was created.
- The worktree was clean on `main` at the sealed commit.
- Local `HEAD`, `origin/main`, the canonical tag and the tag published by `origin` all resolved to
  the sealed commit.
- `STATE.json.currentCommit` named the canonical tag and resolved to the same commit.
- The predecessor anchor chain validated with 27 anchors. As the newest sealed checkpoint, the
  subject was the one permitted pending anchor; this successor must add that anchor.
- The remote was `https://github.com/pinguim16/iacode.git`.

## Frozen audit scope

This run audits Gate 4 only. It may write audit evidence, the audit attestation, the subject's owed
anchor, `LATEST.md`, and generated review transport. It may not change product code, repair a
finding, rewrite the subject, reduce any denominator, retry a failed verifier stage, or start Gate 5.

## Derived denominator

The audit lesson preflight considered 96 lessons, selected 95, and derived 95 `LESSON-REQ-` rows.
Canonical derivation produced 200 audit-checkpoint requirements: 105 Gate 4 rows and 95 lesson rows.
The audit must additionally revalidate the subject's sealed 221/221 requirement set and its exact
20-attack A–T denominator.
