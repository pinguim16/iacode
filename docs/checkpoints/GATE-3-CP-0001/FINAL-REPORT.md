# Final Report — GATE-3-CP-0001

## Gate

`GATE 3 — SANDBOX + TOOL EXECUTION`, the last Gate of milestone `M1` (Gates 0 to 3). Predecessor:
`GATE 2 — AGENT RUNTIME`, sealed at `INTERNAL_GATE_PASS` as `GATE-2-CP-0002`, validated and anchored
at the start of this checkpoint.

## Status

`INTERNAL_GATE_PASS`.

The project's own controls passed. That is not an independent verdict and is not recorded as one:
`independentReview` is `NOT_REQUIRED` for a Gate, the adversarial battery is the delivery's
internal one (`M1-INTERNAL-RED-TEAM.json`), and the internal mirror audit is not the milestone
audit. `M1` is ready for its fresh-session audit and reads `PENDING` in `STATE.json` until it
happens (`DECISIONS.md` D-12).

## Environment

Windows 11 Pro 10.0.26200, Python 3.13.15, Docker Desktop 29.6.1 (cgroup v2) with Compose v2, Git.
Branch `main`, base commit `d4a3998ce745dcbfcf6a8498f267ee302834543f`. The authorised remote is
`https://github.com/pinguim16/iacode.git`; the credential used to push lives in the operator's Git
credential store and never entered the repository, a URL or a configuration file.

## Tool / Model / Effort

Claude Code in the Claude desktop application, model Claude Opus 5.5 (`claude-opus-5-5`). The
reasoning effort is not exposed to the run.

## Deliverables

- Public history: remote configured, full-history secret scan before the first push, atomic commits
  pushed to `origin/main`, no rewrite (`ADR-0024`, `tests/test_git_policy.py`).
- Phase 0: the five inherited fixes, each test-first and each its own commit.
- The sandbox service with its policy, registry, resolver, helper, backend, sessions, store,
  artifacts, snapshots, image profile, recovery, sweeper, metrics and logs (`ADR-0025` to
  `ADR-0027`, `docs/runbooks/SANDBOX.md`).
- Agent Runtime integration: sandboxed stages, the coding team, the developer and code-reviewer
  profiles, and the executed tools on the run page.
- Migration `0004_sandbox`: `sandbox_sessions`, the evolved `tool_calls`, the run's workspace.
- Four recorded scenarios on the real engine, a 25-attack internal Red Team, the canonical
  specification with 139 rows, four lessons and three guardrails.

## Files Created

The principal additions are `services/sandbox/`, `.iacode/policies/sandbox-policy.json`, migration
`0004_sandbox.py`, the coding profiles and team, the scenarios and harnesses, the Git policy and
Red Team scripts, `docs/GATE-3-CHECKLIST.md`, `ADR-0024` to `ADR-0027`, the ADR index, the sandbox
runbook, `tests/test_gate3_sandbox.py`, `tests/test_git_policy.py`, the retrospective and this
checkpoint. `FILES.json` lists every one with its reason and hash; `DIFF-SUMMARY.md` describes them.

## Files Modified

The Phase 0 ledger and memory tools, the API's event stream, the Agent Runtime's plan and detail,
the worker's workflow and activities, the shared contracts and schema, the run page, the compose
stack and its Prometheus job, the verification command and image runner, the registries, the
memory, and the entry, architecture, development, versions and runbook documents. `FILES.json`
lists every one with its reason and both hashes.

## Validation

| Control | Result | Evidence |
|---|---|---|
| Full verification | 31 of 31 stages `PASS` | `VERIFICATION-REPORT.json`, `cmd-0105` |
| Green Keeper | `PASS`, 12 of 12 mandatory gates, one cycle | `REWORK-LOG.jsonl`, `cmd-0107` to `cmd-0118` |
| Completeness | 192 of 192 complete, evidence 100% | `COMPLETENESS-REPORT.json`, `cmd-0123` |
| Internal mirror | `PASS` (a first run, `cmd-0125`, failed on the handoff and is kept) | `M1-INTERNAL-MIRROR.json`, `cmd-0126` |
| Remote | `origin/main` holds every commit before the closure | `cmd-0121` |
| Checkpoint | valid; sealed at its own tag and validated from it after the seal | `STATE.json` |

## Tests

| Suite | Cases | Result | Evidence |
|---|---|---|---|
| Control-plane suite (`tests/`) | 689 | PASS | `cmd-0107` |
| Image suites: API, gateway and agent runtime (623) and sandbox (141) | 764 | PASS | `cmd-0100` |
| Live infrastructure suite | 49 | PASS | `cmd-0106` |
| **Total** | **1,502 of 1,502 discovered** | **PASS** | `TESTS.json`, `COUNTS.json` |

Beside the counted suites: the frontend build and suite, 49 cases (`cmd-0116`), and the four
sandbox scenarios — coding 27 steps, timeout 13, cancellation 14, recovery 15, all passing
(`cmd-0071` to `cmd-0074`).

## Red Team

25 of 25 attacks defended with a valid null-mutation control (`M1-INTERNAL-RED-TEAM.json`,
`RED-TEAM-REPORT.md`, `cmd-0119`); 21 of them against real containers from inside the sandbox
service's image. Its first run (`cmd-0079`) found `G3-F-004`, the detached fork bomb, repaired in
`540965d`. This is the delivery's internal battery, not independent validation.

## Known Risks

`RISKS.md`: eight open, none blocking — the engine socket the service holds (`R-G3-001`, HIGH), the
shared kernel, the sweep's bound, the runtime's context bound, unscanned system packages, no
retention, the pre-push practice, no live model through the sandbox. `R-G2-002` is closed by this
Gate.

## Remaining Work

None this Gate specifies. Findings `G3-F-001` to `G3-F-004` are repaired; Critical 0, High 0. The
optional live-model smoke through the sandbox was not run.

## Handoff Readiness

`HANDOFF.md` and `NEXT.md` are executable without this session: validation commands, stop
conditions and the exact continuation sequence. Every commit and the checkpoint tag are on the
authorised remote.

## Next Gate

None yet. The next step is the `M1 FRESH-SESSION MILESTONE AUDIT`; `GATE 4` does not start before
it and the owner's authorization.

## Evidence

`STATE.json`, `REQUIREMENTS-MATRIX.json`, `CLOSURE-REQUIREMENTS.json`, `COMPLETENESS-REPORT.json`,
`COUNTS.json`, `TESTS.json`, `QUALITY.json`, `VERIFICATION-REPORT.json`, `REWORK-LOG.jsonl`,
`M1-INTERNAL-RED-TEAM.json`, `M1-INTERNAL-MIRROR.json`, `LESSON-PREFLIGHT.json`, `DECISIONS.md`,
`RISKS.md` and `COMMANDS.jsonl`.
