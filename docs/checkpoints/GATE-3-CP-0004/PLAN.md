# Plan — M1 fresh-session milestone re-audit

Audit checkpoint `GATE-3-CP-0004`. Subject: the sealed corrective delivery
`GATE-3-CP-0003`, together with every sealed checkpoint of `M1` on which it depends. This session
has no memory of the implementing run and will not change product code. Its allowed writes are the
audit checkpoint, the attestation, the integrity anchor owed to the sealed subject,
`docs/checkpoints/LATEST.md`, and the review bundle outside Git.

The mechanism is `FRESH_SESSION_INDEPENDENT_AUDIT`: same product family, but a new Codex session
independent of the Claude implementation. It is not `CROSS_TOOL_INDEPENDENT_AUDIT` and cannot
produce `MILESTONE_EXTERNAL_PASS`.

## Frozen criteria

These criteria are fixed before substantive audit execution. Results may fill the matrix but may
not add, remove, narrow, or weaken a criterion after execution starts.

| # | Criterion | How it is judged |
|---|---|---|
| AM-01 | Every sealed `M1` checkpoint is valid from published history | each checkpoint validates detached at its own canonical tag from a transport clone |
| AM-02 | Integrity and tags are valid | `verify_integrity.py`; tags resolve to anchored commits; mutation attacks |
| AM-03 | The authorised remote is synchronised | `remote_sync.py` against `origin` and the subject tag; remote attack |
| AM-04 | Full verification is green | `scripts/iacode/verify.py --keep-going`, every stage, executed by this session |
| AM-05 | A clean clone is green | clone the authorised remote, validate, verify integrity and memory, then run full verification |
| AM-06 | Foundation works | stack, integration, infra, smoke, backup, restart and fresh-install stages |
| AM-07 | Model Gateway works | gateway tests and live gateway smoke |
| AM-08 | Agent Runtime works | runtime tests, live smoke, durability, cancellation and deadline stages |
| AM-09 | Sandbox works | sandbox tests, integration, coding, timeout, cancellation and recovery stages |
| AM-10 | The cross-Gate live flow works | Task → Agent Runtime → Model Gateway → ToolRequest → Sandbox → ToolResult → Agent Runtime |
| AM-11 | No tool runs on the host | live-run host sentinel and cross-Gate Red Team attack |
| AM-12 | Host secrets are absent from a sandbox | cross-Gate Red Team attack |
| AM-13 | Workspaces are isolated | cross-Gate Red Team attack |
| AM-14 | Traversal and link escapes are defended | cross-Gate Red Team attack |
| AM-15 | Engine socket is absent from an executed sandbox | attack plus the ten `R-G3-001` controls |
| AM-16 | Git remote is unavailable to an agent | cross-Gate Red Team attack |
| AM-17 | No unresolved Critical or High finding exists | this review, registered audit findings, and consolidated risks |
| AM-18 | Gate completeness and evidence are valid | final Gate matrices recomputed from sealed tags at 100% coverage and evidence |
| AM-19 | `R-G3-001` has an evidence-based disposition | ten controls and an independent attack |
| AM-20 | The audit Red Team passes | full cross-Gate battery over a valid null-mutation control |
| AM-21 | `M1-F-001` remains closed | configured-model live run produces schema-valid tool requests that execute in the sandbox without repair |
| AM-22 | `M1-F-002` remains closed | forged API tool result is refused during and after sandbox execution and cannot replace the stored sandbox result |
| AM-23 | `M1-F-003` remains closed | every commit named by sealed evidence is reachable from published references and the remote clone validates every sealed subject |

## Order

1. Cold start, subject validation, clean Git comparison, anchor `GATE-3-CP-0003`, lesson preflight,
   requirement derivation, remote and history baseline.
2. Reuse the previous audit harness with only checkpoint/subject generalisation; add explicit probes
   for the three corrected findings. No product correction belongs to this audit.
3. Validate every sealed subject locally and from the published remote; review `R-G3-001`.
4. Run the full verification and the cross-Gate live flow against the configured model.
5. Run the audit Red Team, including independent attacks on `M1-F-001`, `M1-F-002` and
   `M1-F-003`, over a valid null-mutation control.
6. Run the clean-clone verification from the authorised remote.
7. Compute the frozen matrix, findings, risk disposition and review verdict from executed evidence.
8. Complete the derived requirements, run Green Keeper, completeness, counts and internal mirror.
9. If all criteria pass, author the fresh-session attestation and milestone reports, finalize as
   `MILESTONE_INDEPENDENT_AUDIT_PASS`, commit, seal, push, verify remote synchronization and build
   the validated review ZIP. Otherwise close `REWORK_REQUIRED` without implementing repairs.

## Stop conditions

- A real Critical or High finding: close `REWORK_REQUIRED`, package evidence, and do not start
  `GATE 4`.
- An untrusted input reaches an arbitrary engine operation: Critical, stop.
- Local/published history divergence that requires rewriting, or any operation requiring force:
  stop.
- The auditor would need to change product code to make a check pass: record a finding and return
  it to an implementing run.
