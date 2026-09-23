# Final M1 audit matrix

Result: `FAIL` — 16/20 criteria

| Criterion | Dimension | Verdict | Observed |
|---|---|---|---|
| AM-01 | Four Gates sealed and valid | `FAIL` | this repository: 5/5; published remote: 4/5, invalid there: ['GATE-1-CP-0001'] |
| AM-02 | Integrity and tags | `PASS` | 18 anchors; every M1 tag at its anchored commit; M1-M DEFENDED (control VALID): moved GATE-2-CP-0002 tag: exit 1 INTEGRITY_INVALID; rewritten with the same tree and the tag moved (exit codes): {'GATE-2-CP-0002': 1, 'GATE-3-CP-0001 anchored, unmutated': 0, 'GATE-3-CP-0001': 1} |
| AM-03 | Remote synchronised | `PASS` | REMOTE_SYNC_PASS remote=origin branch=main tags=iacode-checkpoints/GATE-3-CP-0001; origin is the authorised URL; M1-N DEFENDED (control VALID): unpushed commit: exit 1; tag deleted on the remote: exit 1; remote not the authorised URL: exit 1 |
| AM-04 | Full verification | `PASS` | PASS 31/31 stages, fast=False |
| AM-05 | Clean clone | `FAIL` | clone the authorised remote exit 0; validate the latest checkpoint exit 0; verify the integrity chain exit 0; validate the engineering memory exit 0; full verification in the clone exit 1 |
| AM-06 | Foundation operational | `PASS` | stack=PASS, integration=PASS, infra=PASS, smoke=PASS, backup=PASS, restart=PASS, dependency-failure=PASS, fresh-install=PASS, gate:apiTests=PASS, gate:webTests=PASS |
| AM-07 | Gateway functional | `PASS` | gate:gatewayTests=PASS, gateway-smoke=PASS |
| AM-08 | Agent Runtime functional | `PASS` | gate:agentRuntimeTests=PASS, agent-runtime-smoke=PASS, agent-durability=PASS, agent-cancellation=PASS, agent-deadline=PASS |
| AM-09 | Sandbox functional | `PASS` | gate:sandboxTests=PASS, sandbox-integration=PASS, sandbox-coding=PASS, sandbox-timeout=PASS, sandbox-cancellation=PASS, sandbox-recovery=PASS |
| AM-10 | Cross-gate flow | `PASS` | model calls through the gateway: 7 model call(s) recorded; the runtime's only model path is the gateway's /api/v1/gateway/infer; tool requests executed in a sandbox: 1 execution(s) in sandbox session(s) ['01a0cc832449']; tool results delivered to the runtime: 2 of 2 tool request(s) RESOLVED; the runtime called the model again after a sandbox result: a MODEL_CALL_STARTED event follows a TOOL_RESULT |
| AM-11 | No tool runs on the host | `PASS` | host sentinel untouched=True; M1-A DEFENDED (control VALID): the command ran as uid 10001 on host name '9e009c1be9d5', which is the sandbox container's ('9e009c1be9d5') and not the controller's ('dcf117055cf0'); host mount points absent |
| AM-12 | Host secrets absent from the sandbox | `PASS` | M1-B DEFENDED (control VALID): controller variables visible: none; secret value visible: False; credential files: none; files holding private key material: none |
| AM-13 | Workspace isolation | `PASS` | M1-E DEFENDED (control VALID): victim container cac301e5b2f2, attacker container 891b1ff37597; files holding the victim's token seen from the attacker's sandbox: none |
| AM-14 | Path traversal and link escapes defended | `PASS` | M1-D DEFENDED (control VALID): ../../../etc/passwd -> DENIED/PATH_ESCAPE; /etc/shadow -> DENIED/PATH_ABSOLUTE_OUTSIDE; ..\..\windows -> DENIED/PATH_BACKSLASH; sub/../../x -> DENIED/PATH_ESCAPE; root-link/etc/passwd -> DENIED/PATH_S |
| AM-15 | Engine socket absent from an executed sandbox | `PASS` | M1-C DEFENDED (control VALID): socket paths absent, DOCKER_HOST empty, connecting fails; the container has 0 mount(s) and 0 bind(s); R-G3-001 C2 PASS |
| AM-16 | Git remote unavailable to an agent | `PASS` | M1-H DEFENDED (control VALID): remotes: none; credential configuration: ['file:/opt/iacode/gitconfig\tcredential.helper='] (an empty helper disables helpers); exposures: none; push over the network failed; remote tools ['DENIED/UNK |
| AM-17 | No unresolved Critical/High finding | `FAIL` | 3 finding(s); unresolved Critical/High: ['M1-F-003'] |
| AM-18 | Completeness and evidence of the Gates | `FAIL` | GATE-0-CP-0001 118 requirements 100.0% completeness PASS; GATE-1-CP-0001 161 requirements 100.0% completeness PASS; GATE-2-CP-0002 186 requirements 100.0% completeness PASS; GATE-3-CP-0001 192 requirements 100.0% completeness PASS; from the published remote the evidence of ['GATE-1-CP-0001'] does not resolve |
| AM-19 | R-G3-001 dispositioned from proof | `PASS` | 10/10 controls, disposition ACCEPTED_LOCAL_ARCHITECTURAL_RISK; M1-G DEFENDED (control VALID): [{"runId": "--privileged", "result": "FAILED/None", "privileged": false, "binds": [], "mounts": 0, "capAdd": [], "capDrop": ["ALL"], "network": "none", "label": "--privileged"}, {"runId": "x --volume  |
| AM-20 | The audit's Red Team | `PASS` | RED_TEAM_PASS 14/14 control VALID |
