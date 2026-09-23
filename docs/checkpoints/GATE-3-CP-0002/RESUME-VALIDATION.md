# Resume Validation

How this audit started, and what it checked before relying on anything the repository said.

## Cold start

`START-HERE.md`, `AGENTS.md`, `CLAUDE.md`, the development contract, the master plan, the roadmap,
the definition of done, the quality gates, the checkpoint, handoff, engineering-memory and
milestone-validation protocols, `LATEST.md` and the whole of `GATE-3-CP-0001` were read before any
change. The session has no memory of the runs that implemented `GATE 0` to `GATE 3`.

## Git baseline

`main` at `3bc8e9d8a94d44163d1af9325ad5b2272f71f8ed`, equal to `origin/main`, tagged
`iacode-checkpoints/GATE-3-CP-0001`; `origin` is `https://github.com/pinguim16/iacode.git`. The one
untracked file was the owner's archive `docs/checkpoints/GATE-3-CP-0001.rar`, excluded locally and
left in place (`DECISIONS.md` D-01). No divergence.

## The subject before the audit

| Check | Result | Evidence |
|---|---|---|
| `validate_checkpoint.py` on `GATE-3-CP-0001` | `CHECKPOINT_VALID` | cold start, before the audit checkpoint existed |
| `validate_lessons.py` | `LESSONS_VALID total=54 active=54 guarded=51` | `cmd-0006` |
| `verify_integrity.py` | `INTEGRITY_VALID`, 17 anchors, then 18 with the subject | `cmd-0002`, `cmd-0003` |
| `remote_sync.py --tag iacode-checkpoints/GATE-3-CP-0001` | `REMOTE_SYNC_PASS` | `cmd-0007` |
| `secret_scan.py --history` | clean | `cmd-0009` |

## Sealed subjects from their tags

Every sealed checkpoint of `M1` was checked out detached at its canonical tag and validated by the
current validator with `--root` on that checkout: 5 of 5 from worktrees of this repository
(`SEALED-SUBJECTS.json`, `cmd-0010`), 4 of 5 from a clone of the published remote
(`SEALED-SUBJECTS-PUBLISHED.json`, `cmd-0029`). The
validator each shipped with was run too; `GATE-0-CP-0001` and `GATE-2-CP-0001` fail it, for the two
defects the following Gates repaired in the tooling (`M1-O-001`).

## Clean clone

A fresh clone of the public remote, holding only published history and given only the machine's
local configuration file, validated the latest checkpoint and verified the chain and the memory; its
full verification passed 30 of 31 stages and failed `gate:tests` (`CLEAN-CLONE-REPORT.json`,
`cmd-0023`). The failing case, reproduced in a second clone and then recorded as the validation of
every sealed checkpoint from a clone of the remote (`SEALED-SUBJECTS-PUBLISHED.json`, `cmd-0029`), is
`GATE-1-CP-0001`: finding `M1-F-003`.
