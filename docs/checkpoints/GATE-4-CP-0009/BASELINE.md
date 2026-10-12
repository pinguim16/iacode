# Baseline

The published starting point is `GATE-4-CP-0008` at
`e7879006d516898d441217f253e8282f69fa0b80`. Local `main`, `origin/main`, the canonical CP0008 tag
and `STATE.json` agree; the worktree was clean, `validate_checkpoint.py` passed, the integrity chain
reported 30 anchors, lessons reported 96 active with 93 guarded, and remote synchronization passed.

The controlling baseline is intentionally red. Re-running the sealed audit harness from a fresh
non-local clone rebuilt the CP0007 archive twice as byte-identical SHA-256
`07bb328a4316297d0b6bd2df986c7b5f5fb41b30c8b2fb58cd99a8d96c24c168`, while CP0007 declares
`8856ce50acebfa02528ad318247c22e6e460c224eb62774c99a35cb5cd734578`. The harness returned 8/10
checks and exit 1. Product verification remains green at 42/42; the independent Red Team is 19/20
solely because attack T escaped.

Root cause: `review_bundle.py` collected a mutable working tree and emitted the digest declaration
before finalization and post-commit sealing changed checkpoint evidence. The archive also carried
live remote state and had no explicit immutable reconstruction subject. Archive validity and
same-state determinism therefore did not prove that the declaration represented final sealed
content.
