# Final M1 audit matrix

Result: `FAIL` — 7/23 criteria

| Criterion | Dimension | Verdict | Observed |
|---|---|---|---|
| AM-01 | Four Gates sealed and valid | `PASS` | this repository: 7/7; published remote: 7/7 |
| AM-02 | Integrity and tags | `UNVERIFIED` | 20 anchors; every M1 tag at its anchored commit; M1-M not executed |
| AM-03 | Remote synchronised | `UNVERIFIED` | origin/main and the sealed subject tag matched the authorised remote.; M1-N not executed |
| AM-04 | Full verification | `FAIL` | FAIL 31/32 stages, fast=False |
| AM-05 | Clean clone | `UNVERIFIED` | not executed |
| AM-06 | Foundation operational | `PASS` | stack=PASS, integration=PASS, infra=PASS, smoke=PASS, backup=PASS, restart=PASS, dependency-failure=PASS, fresh-install=PASS, gate:apiTests=PASS, gate:webTests=PASS |
| AM-07 | Gateway functional | `PASS` | gate:gatewayTests=PASS, gateway-smoke=PASS |
| AM-08 | Agent Runtime functional | `PASS` | gate:agentRuntimeTests=PASS, agent-runtime-smoke=PASS, agent-durability=PASS, agent-cancellation=PASS, agent-deadline=PASS |
| AM-09 | Sandbox functional | `PASS` | gate:sandboxTests=PASS, sandbox-integration=PASS, sandbox-coding=PASS, sandbox-timeout=PASS, sandbox-cancellation=PASS, sandbox-recovery=PASS |
| AM-10 | Cross-gate flow | `UNVERIFIED` | not executed |
| AM-11 | No tool runs on the host | `UNVERIFIED` | host sentinel untouched=None; M1-A not executed |
| AM-12 | Host secrets absent from the sandbox | `UNVERIFIED` | M1-B not executed |
| AM-13 | Workspace isolation | `UNVERIFIED` | M1-E not executed |
| AM-14 | Path traversal and link escapes defended | `UNVERIFIED` | M1-D not executed |
| AM-15 | Engine socket absent from an executed sandbox | `UNVERIFIED` | M1-C not executed; R-G3-001 C2 PASS |
| AM-16 | Git remote unavailable to an agent | `UNVERIFIED` | M1-H not executed |
| AM-17 | No unresolved Critical/High finding | `FAIL` | 1 finding(s); unresolved Critical/High: ['M1-F-004'] |
| AM-18 | Completeness and evidence of the Gates | `PASS` | GATE-0-CP-0001 118 requirements 100.0% completeness PASS; GATE-1-CP-0001 161 requirements 100.0% completeness PASS; GATE-2-CP-0002 186 requirements 100.0% completeness PASS; GATE-3-CP-0003 197 requirements 100.0% completeness PASS |
| AM-19 | R-G3-001 dispositioned from proof | `UNVERIFIED` | 10/10 controls, disposition ACCEPTED_LOCAL_ARCHITECTURAL_RISK; M1-G not executed |
| AM-20 | The audit's Red Team | `UNVERIFIED` | None None/None control None |
| AM-21 | M1-F-001 remains closed | `UNVERIFIED` | not executed |
| AM-22 | M1-F-002 remains closed | `UNVERIFIED` | not executed |
| AM-23 | M1-F-003 remains closed | `PASS` | publishedObjects=PASS, failedChecks=none, remoteSubjects=7/7 |
