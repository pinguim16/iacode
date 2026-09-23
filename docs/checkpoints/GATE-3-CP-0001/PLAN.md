# Plan

`GATE 3 — SANDBOX + TOOL EXECUTION`, milestone `M1`. The Gate closes at `INTERNAL_GATE_PASS`; the
milestone verdict belongs to a fresh-session audit, and nothing of `GATE 4` starts here.

The requirement set is `docs/GATE-3-CHECKLIST.md` (139 rows) plus the 49 `LESSON-REQ` requirements
of `LESSON-PREFLIGHT.json`, derived into `REQUIREMENTS-MATRIX.json` by `derive_requirements.py`.

## Order of execution

Every step ends in an atomic commit, pushed to `origin/main` once the checks that step can reach are
green: `git status`, `git diff --cached`, `secret_scan.py --staged`, and the targeted suites of the
step. A failed push is recorded and never undone.

| # | Step | Evidence it produces |
|---|---|---|
| 1 | Cold start, Gate 2 validation, Git identity, authorised remote, full-history secret scan, bootstrap push | `cmd-0001`–`cmd-0011` |
| 2 | Open `GATE-3-CP-0001`, anchor `GATE-2-CP-0002` | `1719e8d` |
| 3 | Phase 0: the five inherited fixes, each test-first | `072c71c`, `aa85069`, `53f1c9d`, `12f98cc`, `e212dc4` |
| 4 | Lesson preflight | `cmd-0030` |
| 5 | Persistence: evolved `tool_calls`, `sandbox_sessions`, migration `0004` | `1604ef8` |
| 6 | Sandbox service: contracts, policy, registry, resolver, helper, backend, service, store, telemetry, image | `24c90e1` |
| 7 | Agent Runtime integration: sandboxed stages, coding team, developer and reviewer profiles | `4e29a33` |
| 8 | Operational page: executed tools | `1696bef` |
| 9 | Agent result bound; canonical specification, registries, control-plane tests, requirement matrix | this step |
| 10 | Sandbox store and artifact integration tests; verification stages; deterministic coding scenario with host sentinel, cancellation and recovery | scenario reports |
| 11 | Focused internal Red Team with a null control | `M1-INTERNAL-RED-TEAM.json` |
| 12 | Documentation, retrospective, lessons and guardrails, preflight re-run | `Gate3DocumentationTests` |
| 13 | Full verification, Green Keeper, counts, completeness, mirror audit | `VERIFICATION-REPORT.json`, `GREEN-KEEPER.json`, `COMPLETENESS.json` |
| 14 | Internal review; finalize at `INTERNAL_GATE_PASS`; seal; post-seal validation | `STATE.json`, the checkpoint tag |
| 15 | Push the final commit and the tag; confirm `origin/main` and the tag on the remote | `remote_sync.py --tag` |

## Stop conditions

- A credential found in history or in staged content: `BLOCKED`, no push, no rewrite.
- `origin` pointing anywhere but the authorised remote: stop.
- A mandatory gate that cannot be made green by repairing its cause: `BLOCKED`, never a weakened check.
- A sandbox property that holds only on the host and not in a container: not a sandbox; stop.
- A push that fails for authentication or network: the commit stays, the blocker is recorded, and
  the final checkpoint cannot claim remote synchronisation.
