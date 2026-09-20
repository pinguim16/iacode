# Development Red Team (not independent)

Result: `DEV_RED_TEAM_PASS`

This battery was executed by the implementing run. It is development evidence and reproduction
material for the independent Codex Red Team, not a substitute for it. The independent verdict is
still outstanding.

## Method

The working tree was copied to an isolated directory outside the repository, the checkpoint was
finalized, committed, and tagged there, and each attack ran against a fresh copy of that sealed
fixture. Attacks that would otherwise only show as a dirty worktree were committed and the fixture tag
was moved onto the tampered commit, so the reported error is the one the attack targets rather than a
side effect. The real repository was never modified: `git status` remained limited to the intended
correction, and every fixture was deleted afterwards.

## Finding against this run's own work

The first rehearsal failed. `SETUP-00-CP-0003` had been created before `new_checkpoint.py` was updated,
so its metadata still declared `schemaVersion` `1.0.0`; the new inventory and evidence rules therefore
did not apply to it, and finalization failed on a stale hash. The checkpoint metadata was moved to
`2.0.0` and the rehearsal was repeated. This is recorded rather than hidden because it is exactly the
class of silent version-dispatch error the corrections must not introduce.

## Attacks and results

| # | Attack | Result | Observed error |
|---|---|---|---|
| 1 | Tracked adapter `.claude/agents/red-team.md` deleted | DETECTED | `FILES.json omits a changed path: .claude/agents/red-team.md (deleted)` |
| 2 | `FILES.json` entry removed for `docs/SETUP-00-CHECKLIST.md` | DETECTED | `FILES.json omits a changed path: docs/SETUP-00-CHECKLIST.md (added)` |
| 3 | Tracked file altered silently and re-sealed | DETECTED | `FILES.json omits a changed path: .claude/agents/architect.md (modified)` |
| 4 | Non-canonical status in `STATE.json` | DETECTED | schema enum rejection plus hash mismatch |
| 5 | Invalid JSON in `TESTS.json` | DETECTED | parse error plus hash mismatch |
| 6 | Commit advanced past the checkpoint tag | DETECTED | `commit mismatch` |
| 7 | Checkpoint tag moved to an earlier commit | DETECTED | `commit mismatch` |
| 8 | Dirty worktree | DETECTED | `dirty-state mismatch` |
| 9 | Required file `RISKS.md` removed | DETECTED | missing required file plus missing hashed path |
| 10 | Secret injected into `DECISIONS.md` | DETECTED | `named secret assignment` plus hash mismatch |
| 11 | `NEXT.md` emptied | DETECTED | hash mismatch plus inventory hash mismatch |
| 12 | `PROVENANCE.json` removed | DETECTED | missing required file plus missing hashed path |
| 13 | Quality `PASS` with no evidence | DETECTED | `QUALITY.json lint=PASS requires at least one evidence reference` |
| 14 | Quality `PASS` citing a nonexistent command | DETECTED | `references an unknown command id 'cmd-9999'` |
| 15 | `STATE.json` timestamp field removed | DETECTED | missing required property plus unexpected property |
| 16 | Self-granted `GATE_PASS` through the real finalization path | DETECTED | `GATE_PASS requires secondToolValidation PASSED or NOT_REQUIRED, found 'PENDING_MANUAL'` |
| 17 | `LATEST.md` repointed outside the checkpoint tree | DETECTED | `LATEST.md points outside docs/checkpoints` |

Attacks 1, 2, and 3 are the three that returned `CHECKPOINT_VALID` against the sealed
`SETUP-00-CP-0002`. All three are now rejected by the validator alone.

## Supported modes that must stay valid

| Mode | Result |
|---|---|
| Detached checkout at the checkpoint's own tag, clean worktree | `CHECKPOINT_VALID` |
| Detached checkout at a different commit | rejected with `commit mismatch` and a tag-resolution error |
| Clean clone on the default branch | `CHECKPOINT_VALID` |
| Checkout with `core.autocrlf=true` | `CHECKPOINT_VALID`, hashes unaffected |
| Clean clones detached at `SETUP-00-CP-0001` and `SETUP-00-CP-0002` under the corrected tooling | `CHECKPOINT_VALID` for both |

## Coverage decision for tool adapters

The validator now rejects a deleted or altered adapter through the file inventory, because every
tracked change must be declared and hash-bound. Semantic equivalence between `.claude/agents/` and
`.iacode/agents/` stays the responsibility of `ClaudeAdapterTests` in the suite, which fails on a
missing adapter, a wrong `name`, a missing `description`, a changed `model`, or a body that stops
deferring to the canonical contract. Both layers are required and neither is redundant: the validator
detects undeclared change, the suite detects a declared change that breaks the contract. This division
is stated here rather than left implicit.

## Not attacked

Credential shapes outside the documented detector scope were confirmed undetected in the previous
review and are recorded as residual risk in `RISKS.md`; the detector was deliberately left unchanged in
this checkpoint. History rewriting and tag moving remain prohibited operations rather than defended
ones, and attack 7 shows what validation reports when a tag moves.
