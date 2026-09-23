# Resume Validation

How this corrective delivery started, and what it checked before relying on anything.

## Cold start

`START-HERE.md`, `AGENTS.md`, `CLAUDE.md`, the development contract, the master plan, the roadmap,
the definition of done, the quality gates, the checkpoint, handoff, engineering-memory and
milestone-validation protocols, `LATEST.md` and the whole of `GATE-3-CP-0002` — its review, final
report, findings, next action, handoff, decisions, risks, audit matrix, clean-clone report,
published sealed-subject report, execution record and harness — were read before any change. The
owner's summary was not used as the source of truth: the findings, their root causes and the
registration fields were taken from the sealed audit checkpoint.

## Git baseline

`main` at `3a526925cf653ffaa9497cff628d08d50424271a`, equal to `origin/main`, tagged
`iacode-checkpoints/GATE-3-CP-0002`, matching the audit's `STATE.json`
(`currentCommit` `refs/tags/iacode-checkpoints/GATE-3-CP-0002`, clean). `origin` is
`https://github.com/pinguim16/iacode.git`. No divergence.

## Baseline checks

| Check | Result | Evidence |
|---|---|---|
| `validate_checkpoint.py` on `GATE-3-CP-0002` | `CHECKPOINT_VALID` | cold start, before this checkpoint existed |
| `validate_lessons.py` | `LESSONS_VALID total=54 active=54 guarded=51` | `cmd-0004` |
| `verify_integrity.py` | `INTEGRITY_VALID`, 18 anchors | `cmd-0005` |
| `milestone_status.py --milestone M1` | `MILESTONE_NOT_PASSED` (expected): the only attestation says `REWORK_REQUIRED` | `cmd-0006` |
| `remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0002` | `REMOTE_SYNC_PASS` | `cmd-0007` |
| `git cat-file -t b59d66f9f3f9…` | `commit`, protected locally by `refs/iacode-preserved/b59d66f9f3f9` | `cmd-0008` |
| every commit sealed evidence names, reachable from a published reference? | 3 of 62 were not — local objects only | `cmd-0009`, `SEALED-EVIDENCE-COMMITS-BASELINE.json` |

`M1` was confirmed `NOT PASSED / REWORK_REQUIRED` before the correction began.
