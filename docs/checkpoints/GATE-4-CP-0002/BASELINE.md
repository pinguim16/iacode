# Baseline — GATE-4-CP-0002

## Immutable subject

- Checkpoint: `GATE-4-CP-0001`.
- Canonical tag: `refs/tags/iacode-checkpoints/GATE-4-CP-0001`.
- Expected and observed commit: `70a22e824705f414e0c295bbdf89187db9b391f7`.
- Expected and observed subject status: `READY_FOR_REVIEW`.
- Expected and observed remote: `https://github.com/pinguim16/iacode.git`.
- Local `HEAD`, local subject tag, `origin/main`, remote `main`, and the remote subject tag all
  resolved to the same commit before this checkpoint was opened.
- The worktree was clean before the audit checkpoint was created.

## Sealed review bundle

- Path: `artifacts/review/GATE-4-CP-0001-sealed.zip`.
- Observed SHA-256: `af98bb766d34beaf82f1d9963fc77377816a3cad9a850671313c528ea8701df7`.
- The digest exactly matches the handoff value. Bundle contents and embedded checksums remain to be
  reproduced by this audit rather than inherited from the implementing run.

## Pre-audit controls

- `validate_checkpoint.py` returned `CHECKPOINT_VALID` against the sealed subject.
- `verify_integrity.py` returned `INTEGRITY_VALID` for the pre-audit chain.
- `remote_sync.py --tag iacode-checkpoints/GATE-4-CP-0001` returned `REMOTE_SYNC_PASS`.
- This successor checkpoint rebuilt the integrity chain with 24 anchors, thereby recording the
  anchor owed to the sealed subject without changing the subject or its tag.
- The independent-audit lesson preflight considered 90 lessons, selected 90, and derived 90
  `LESSON-REQ-` requirements.
- Canonical derivation produced 195 audit-checkpoint requirements: 105 Gate 4 rows and 90 lessons.

## Starting assurance position

- The subject claims 194/194 complete requirements, 1,675/1,675 counted tests, 42/42 verification
  stages, 13/13 mandatory Green Keeper gates, 10/10 internal false-PASS attacks, and a passing
  internal M2 mirror. These are claims to reproduce, not evidence this auditor inherits as PASS.
- `secondToolValidation`, independent review, and independent Red Team are pending in the immutable
  subject, as required.
- M2 remains pending. This audit may grant Gate 4 `GATE_PASS`; it does not claim that the M2
  milestone, whose remaining Gates are unimplemented, has passed.

## Stop conditions

- Any mismatch in subject tag, commit, tree, remote, bundle digest, or checkpoint status.
- Any Critical or High finding, escaped mandatory attack, unresolved evidence, red mandatory gate,
  incomplete requirement, stale assurance result, or unavailable mandatory live dependency.
- Any need to change product code, tests, policy, the sealed subject, or a historical tag.
- Any attempt to begin Gate 5 or to describe same-tool session independence as cross-tool or
  milestone completion.
