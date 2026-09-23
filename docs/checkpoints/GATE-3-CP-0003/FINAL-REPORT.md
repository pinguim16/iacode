# Final Report — GATE-3-CP-0003 (M1 corrective delivery)

## Gate

`GATE 3 — SANDBOX + TOOL EXECUTION`, the last Gate of `M1`: the corrective delivery of the
fresh-session `M1` audit `GATE-3-CP-0002` (`M1-CP-0002`, `REWORK_REQUIRED`). It closes the audit's
three findings and nothing else. No architecture change, no new scope, no `GATE 4`.

## Status

`READY_FOR_REVIEW`. The three findings are closed (`M1-FINDINGS-CLOSURE.json`, 3/3). `M1` is **not
passed**: its verdict belongs to a new fresh-session audit of this sealed checkpoint.

## Environment

Windows 11 Pro 10.0.26200, Python 3.13.15, Docker Desktop 29.6.1 with Compose v2, Git. Branch
`main`; the authorised remote `https://github.com/pinguim16/iacode.git`.

## Tool / Model / Effort

Claude Code in the Claude desktop application, model `claude-opus-5-5`, an implementing run. The
reasoning effort is not exposed to the run. Its internal verdicts — the Green Keeper, the
completeness audit, the internal Red Team and the mirror audit — are not independent validation.

## Deliverables

- **`M1-F-003` (HIGH).** Three replaced closure commits sealed evidence names (`b59d66f9f3f9`,
  `13ab172fcc06`, `643e721ee519`) kept by published tags under `refs/tags/iacode-preserved/`, each
  naming exactly its commit (owner-authorised; `D-01`). The validator refuses evidence naming a
  commit no published reference reaches; one definition of the published history; every control
  over sealed history clones it; `remote_sync.py` checks every evidence tag; ADR-0028. Recorded as
  a `GUARDRAIL_FAILURE` of `GRD-0042` and resolved here.
- **`M1-F-001` (MEDIUM).** The envelope contract — version, kinds, one minimal valid envelope per
  kind with `tool.name` and `tool.arguments` — rendered from the schema into the instructions and
  the repair; the tool object closed; the ADR-0022 amendment; a live coding run of the configured
  model.
- **`M1-F-002` (MEDIUM).** Executor ownership on every tool request (migration `0005`); the origin
  of a result fixed by the code path; `403 TOOL_RESULT_ORIGIN_REFUSED`; the audit's null control and
  mutation as the verification stage `sandbox-tool-result-origin`.
- Memory: `LSN-0040` resolved, `LSN-0055` and `LSN-0056` with `GRD-0056` and `GRD-0057`, the
  `LSN-0054` recurrence. The Red Team's `G3-Y` and `G3-AA`. The audit registered, its checkpoint
  anchored.

## Files Created

See `FILES.json`: the migration `0005`, ADR-0028, and the checkpoint with its delivery harness.

## Files Modified

See `FILES.json` and `DIFF-SUMMARY.md`: the ledger tooling, the agent runtime, the orchestrator,
the API, the shared contracts and persistence, the verification, the tests, the memory, the
protocols, the runbooks, the audit registry, the integrity chain and `LATEST.md`.

## Validation

| Control | Result | Evidence |
|---|---|---|
| Preserved commits on the remote | exact SHAs; absent without their tags, present with them | `cmd-0015`, `cmd-0016`, `REMOTE-PUBLISHED-OBJECTS.json` |
| Old tooling against the correction | new tests fail on `0e60b96`; old validator accepts the unpublished commit, new one refuses | `cmd-0029`, `cmd-0031` |
| Full verification | `PASS`, 32/32 stages | `cmd-0070`, `VERIFICATION-REPORT.json` |
| Clean clone of the remote | `PASS`: clone, latest checkpoint, chain (19 anchors), memory, and the full verification 32/32 in the clone | `cmd-0100`, `CLEAN-CLONE-REPORT.json` |
| Sealed `M1` checkpoints from the remote | 6/6 valid | `cmd-0098`, `SEALED-SUBJECTS-PUBLISHED.json` |
| Configured-model live coding run | `PASS`: 11 valid tool requests, all executed in the sandbox, no repair | `cmd-0041`, `LIVE-CODING-RUN.json` |
| Forged tool result | refused `403` during and after execution; stored result the sandbox's | `cmd-0039`, `TOOL-RESULT-ORIGIN.json`, `G3-Y` |
| Green Keeper | `PASS`, 12/12 mandatory gates, cycle 1 | `cmd-0075`–`cmd-0086`, `REWORK-LOG.jsonl` |
| Completeness | `PASS`, 197/197, evidence 100% | `cmd-0104`, `COMPLETENESS-REPORT.json` |
| Internal Red Team | `RED_TEAM_PASS`, 27/27, control `VALID` | `cmd-0087`, `M1-INTERNAL-RED-TEAM.json` |
| Internal mirror audit | `PASS`, 17 checks PASS and MIR-003 `NOT_APPLICABLE` (no registered battery) | `cmd-0107`, `M1-INTERNAL-MIRROR.json` |
| Real credentials in the history | none of the machine's secret values in 1,898 blobs, messages or tags | `cmd-0072`, `SECRET-EXPOSURE-CHECK.json` |

## Tests

See `TESTS.json` and `COUNTS.json`: the control-plane suite (711 cases, `SUITE-SNAPSHOT-FINAL.json`),
the image suites (788: API image 647, sandbox 141, `cmd-0090`) and the infrastructure suite (49,
`cmd-0091`) — 1,548 of 1,548 discovered.

## Red Team

The GATE 3 internal battery, 27 of 27 defended over a valid null-mutation control: the 21 sandbox
attacks on the real engine and the host attacks, including `G3-Y` (a forged tool result through the
real API during and after a sandboxed execution) and `G3-AA` (a preserved reference removed in a
transport clone). The audit registered no mandatory battery (`D-02`). Not independent validation.

## Known Risks

`RISKS.md`. For the owner: rotate the credential of `R-G2-009`; close GitGuardian's incident on
`7d57721` as a false positive (`D-12`); `R-G3-009` — the configured model makes valid requests but
did not finish the task within its budget.

## Remaining Work

A new fresh-session `M1` audit of this sealed checkpoint. `NEXT.md`.

## Handoff Readiness

`HANDOFF.md` and `NEXT.md` are executable without this session. The checkpoint is sealed under its
canonical tag, which is on the authorised remote with the commits that carry it.

## Next Gate

None. `GATE 4` waits for `M1` to pass a fresh-session audit and for the owner's authorisation.

## Evidence

`STATE.json`, `M1-FINDINGS-CLOSURE.json`, `REQUIREMENTS-MATRIX.json`, `COMPLETENESS-REPORT.json`,
`COUNTS.json`, `VERIFICATION-REPORT.json`, `CLEAN-CLONE-REPORT.json`,
`SEALED-SUBJECTS-PUBLISHED.json`, `REMOTE-PUBLISHED-OBJECTS.json`, `LIVE-CODING-RUN.json`,
`TOOL-RESULT-ORIGIN.json`, `M1-INTERNAL-RED-TEAM.json`, `M1-INTERNAL-MIRROR.json`,
`SECRET-EXPOSURE-CHECK.json` and `COMMANDS.jsonl`.
