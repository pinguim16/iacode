# Final Report — GATE-3-CP-0002 (M1 fresh-session milestone audit)

## Gate

`M1 — IACode V0 foundation`: `GATE 0` to `GATE 3`. The audit judged the sealed subject
`GATE-3-CP-0001` (`3bc8e9d8a94d44163d1af9325ad5b2272f71f8ed`) together with the sealed Gates it builds
on. This checkpoint audits; it implemented nothing.

## Status

`REWORK_REQUIRED`. `M1` is not passed. One HIGH finding (`M1-F-003`) fails four of the twenty frozen
criteria; two MEDIUM findings (`M1-F-001`, `M1-F-002`) go with it to the corrective delivery. By the
owner's rule for this execution, `GATE 4` was not started.

## Environment

Windows 11 Pro 10.0.26200, Python 3.13.15, Docker Desktop 29.6.1 with Compose v2, Git. Branch
`main`; the authorised remote `https://github.com/pinguim16/iacode.git`.

## Tool / Model / Effort

Claude Code in the Claude desktop application, model `claude-opus-5-5`, a fresh session with no
memory of the implementing runs: `FRESH_SESSION_INDEPENDENT_AUDIT`, not cross-tool validation.
Cross-tool execution is available on this machine and was not used, by the owner's mandate. The
reasoning effort is not exposed to the run.

## Deliverables

- The audit checkpoint, with its plan written before execution, its execution record, its evidence
  and its harness.
- The attestation `.iacode/attestations/M1-CP-0002.json` (`REWORK_REQUIRED`).
- The eighteenth integrity anchor, for the sealed subject.
- `REVIEW-REPORT.md`, `MILESTONE-REPORT.md`, `FINDINGS.json`, `RED-TEAM-REPORT.md`,
  `R-G3-001-REVIEW.md`, `FINAL-M1-AUDIT-MATRIX.json` and the consolidated `RISKS.md`.

## Files Created

The checkpoint directory and the attestation. `FILES.json` lists every file with its reason and hash.

## Files Modified

`.iacode/anchors/checkpoint-chain.json` and `docs/checkpoints/LATEST.md`. No product file, test,
policy or governing document changed.

## Validation

| Control | Result | Evidence |
|---|---|---|
| Sealed subjects from this repository | 5/5 | `SEALED-SUBJECTS.json`, `cmd-0010` |
| Sealed subjects from the published remote | 4/5 — `GATE-1-CP-0001` invalid | `SEALED-SUBJECTS-PUBLISHED.json`, `cmd-0029` |
| Full verification of this repository | `PASS`, 31/31 stages | `VERIFICATION-REPORT.json`, `cmd-0012` |
| Clean clone of the remote | `FAIL`, 30/31 stages, `gate:tests` | `CLEAN-CLONE-REPORT.json`, `cmd-0023` |
| Live cross-gate run | crossing `PASS` | `CROSS-GATE-LIVE.json`, `cmd-0016` |
| `R-G3-001` | 10/10 controls, `ACCEPTED_LOCAL_ARCHITECTURAL_RISK` | `R-G3-001-REVIEW.json`, `cmd-0011` |
| The audit's Red Team | `RED_TEAM_PASS`, control `VALID` | `M1-INTERNAL-RED-TEAM.json` |
| Frozen criteria | 16 of 20 hold | `FINAL-M1-AUDIT-MATRIX.json` |
| Green Keeper | see `REWORK-LOG.jsonl` | `REWORK-LOG.jsonl` |
| Completeness | 193 requirements complete, evidence resolved | `COMPLETENESS-REPORT.json` |

## Tests

See `TESTS.json` and `COUNTS.json`: the control-plane suite (Green Keeper), the image suites
(`cmd-0027`) and the infrastructure suite (`cmd-0028`), all passing in this repository. In a clean
clone of the remote one control-plane test fails (`M1-F-003`).

## Red Team

Fourteen cross-gate attacks — nine on real sandboxes on the real engine, five on the stack and on
disposable clones — over a null-mutation control that was accepted first. None escaped. Two earlier
runs were refused by that control for harness errors and are kept in the ledger (`DECISIONS.md`).

## Known Risks

`RISKS.md`. For the owner: rotate the credential of `R-G2-009`, and keep the local reference
`refs/iacode-preserved/b59d66f9f3f9` until `M1-F-003` is corrected.

## Remaining Work

The corrective delivery `GATE-3-CP-0003` closing `M1-F-003`, `M1-F-001` and `M1-F-002`, then a new
fresh-session `M1` audit. `NEXT.md` states each correction.

## Handoff Readiness

`HANDOFF.md` and `NEXT.md` are executable without this session. The checkpoint is sealed under its
tag, which is on the authorised remote with the commits that carry it.

## Next Gate

None. `GATE 4` waits for `M1` to pass a fresh-session audit and for the owner's authorization.

## Evidence

`STATE.json`, `REVIEW-REPORT.md`, `FINDINGS.json`, `MILESTONE-REPORT.md`, `FINAL-M1-AUDIT-MATRIX.json`,
`AUDIT-EXECUTIONS.json`, `SEALED-SUBJECTS.json`, `SEALED-SUBJECTS-PUBLISHED.json`,
`VERIFICATION-REPORT.json`, `CLEAN-CLONE-REPORT.json`, `CROSS-GATE-LIVE.json`,
`FORGED-RESULT-PROBE.json`, `R-G3-001-REVIEW.json`, `M1-INTERNAL-RED-TEAM.json`, `RED-TEAM-REPORT.md`,
`REQUIREMENTS-MATRIX.json`, `COMPLETENESS-REPORT.json`, `COUNTS.json` and `COMMANDS.jsonl`.
