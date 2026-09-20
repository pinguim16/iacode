# Diff Summary

- Added checkpoint `schemaVersion` `2.0.0` with version-dispatched validation, so the corrections bind
  to new checkpoints while the two sealed `1.0.0` checkpoints keep validating unchanged.
- R1: the validator now accepts a detached checkout of a checkpoint's own canonical tag, under a clean
  worktree and an exact tag-to-HEAD match, and still rejects a wrong branch, a wrong commit, a moved
  tag, and a dirty tree. Finalization refuses a detached HEAD.
- R2: the file inventory of a delta checkpoint is recomputed from Git and compared exactly, with
  `hashAfter` for added and modified paths and `hashBefore` for modified and deleted paths.
  `FILES.json` is the single self-referential exclusion, declared in code and justified in ADR-0006.
- R3: every finalization attempt appends its own record and exit code to `COMMANDS.jsonl`; failures
  keep their record and a sanitized reason summary, and the successful attempt is recorded before the
  hashes are sealed.
- R4: cross-tool validation moved from a hardcoded sentence to a structured `secondToolValidation`
  object in `STATE.json`, with `PENDING_MANUAL`, `PASSED`, `FAILED`, and `NOT_REQUIRED`.
- R5: added `docs/SETUP-00-CHECKLIST.md` as the in-repository SETUP-00 specification, referenced from
  the Master Plan and the start protocol.
- R6: `QUALITY.json` `2.0.0` records `{status, evidence, justification}` per dimension; a `PASS`
  requires a resolvable `command:` or `file:` reference, and command records carry unique identifiers.
- Promotion changed: an implementing run closes at `READY_FOR_REVIEW`, and `GATE_PASS` requires a
  passed or explicitly justified cross-tool validation.
- Added ADR-0006 and ADR-0007, updated the checkpoint, handoff, quality, and done protocols, the
  ledger tooling README, both tool adapters, and the detected tool capabilities.
- Test suite grew from 37 to 75 tests, including regressions for all six findings and for the three
  attacks that previously escaped detection.
