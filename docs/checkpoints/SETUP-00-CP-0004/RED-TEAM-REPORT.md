# Independent Red Team Report

Result: `RED_TEAM_FAIL`

All attacks ran in temporary repositories or the existing isolated unit-test fixtures. The main
repository stayed unchanged until this validation checkpoint was created.

## Required attacks

| Attack | Result | Evidence |
|---|---|---|
| invalid `STATE.status` | DETECTED | `test_invalid_status_fails` |
| `STATUS.md` differs from `STATE.json` | DETECTED | `test_status_document_mismatch_fails` |
| forged `currentCommit` | DETECTED | `test_wrong_commit_fails` |
| moved/wrong checkpoint tag | DETECTED | new-clone R1 run: exit 1, tag/HEAD mismatch |
| invalid `LATEST.md` target | DETECTED | `test_latest_to_nonexistent_checkpoint_fails` |
| path traversal in `LATEST.md` | DETECTED | new clone: exit 1, `LATEST.md points outside docs/checkpoints` |
| dirty tree | DETECTED | new-clone R1 run: exit 1, dirty-state and hash errors |
| missing mandatory file | DETECTED | `test_missing_handoff_fails`, `test_missing_provenance_fails` |
| empty mandatory file | DETECTED | `test_empty_next_fails` |
| fake secret | DETECTED | secret, JSON-escaped secret, JSONL-escaped secret tests |
| `redTeam=NOT_EXECUTED` during `GATE_PASS` | DETECTED | isolated finalization: exit 1 with both Red Team quality errors |
| quality PASS without evidence | DETECTED | `test_pass_without_evidence_fails` |
| TESTS/QUALITY mismatch | DETECTED | `test_quality_cannot_contradict_tests` |
| missing `FINAL-REPORT.md` | DETECTED | new clone: exit 1, `READY_FOR_REVIEW requires FINAL-REPORT.md` |
| inverted timestamps | DETECTED | new clone: exit 1, ordered RFC 3339 error |
| malformed `COMMANDS.jsonl` | DETECTED | new clone: exit 1, invalid JSON on line 27 |
| `blockedBy` incompatible with review-ready status | **ESCAPED** | see RT-01 |
| FILES entry removed | DETECTED | `test_removed_manifest_entry_fails` |
| silent tracked-file modification | DETECTED | `test_silent_tracked_modification_fails` |
| wrong `hashBefore` | DETECTED | `test_wrong_hash_before_fails` |
| wrong `hashAfter` | DETECTED | `test_wrong_hash_after_fails` |

## RT-01 — Incompatible blockedBy state validates

Severity: blocking control-plane consistency defect.

Reproduction in a clean clone of CP-0003:

1. Keep `STATE.status = READY_FOR_REVIEW`.
2. Set `STATE.blockedBy = ["validation fixture blocker"]`.
3. Run the real finalizer for `READY_FOR_REVIEW`, commit its output, and move only the clone's CP-0003
   tag to the fixture commit.
4. Run the validator.

Observed: finalization exited `0` and the sealed fixture returned `CHECKPOINT_VALID` while simultaneously
claiming it was ready for review and blocked. The validator checks `blockedBy` only for `GATE_PASS`.
This mandatory attack therefore escaped.

## RT-02 — Early finalization refusal is not recorded

Severity: blocking auditability defect; also causes review finding R3.

Reproduction in a clean clone detached at the CP-0003 tag:

1. Count CP-0003 `COMMANDS.jsonl` records: 26.
2. Invoke finalization with `READY_FOR_REVIEW` and the CP-0003 tag.
3. Observe exit `2` with the expected detached-HEAD refusal.
4. Count command records again: 26.

The refusal itself is correct, but the attempted finalization disappears from the ledger, contrary to
the protocol and tool documentation.

## Adapter defense in depth

`ClaudeAdapterTests` passed 3 of 3. They protect one-to-one role names, supported frontmatter, and
canonical-contract delegation. The checkpoint validator separately protects declared path and hash
integrity. Semantic adapter protection is provided by the dedicated suite, not falsely attributed to
the validator.

## Verdict

Because RT-01 escaped and RT-02 violates mandatory finalization auditability, Red Team is
`RED_TEAM_FAIL`. SETUP-00 cannot be promoted.
