# Final M1 audit matrix

Result: `PASS` — 32/32 criteria

| Criterion | Dimension | Verdict | Observed |
|---|---|---|---|
| AM-01 | Subject identity and immutability | `PASS` | local=3ef2bf77ddbddd378d35f5c4d32f2d90d42fc97d remote=3ef2bf77ddbddd378d35f5c4d32f2d90d42fc97d expected=3ef2bf77ddbddd378d35f5c4d32f2d90d42fc97d |
| AM-02 | Local subject validity | `PASS` | result=PASS subject=True anchors=22 |
| AM-03 | Published history | `PASS` | result=PASS valid=9/9 |
| AM-04 | Remote synchronization | `PASS` | objects=PASS subjects=PASS remote=https://github.com/pinguim16/iacode.git |
| AM-05 | Unpublished-evidence negative control | `PASS` | result=PASS checks=6/6 |
| AM-06 | Fresh dependency security | `PASS` | result=PASS pypi=SCANNED npm=SCANNED critical=0 high=0 |
| AM-07 | Dependency graph reality | `PASS` | package-lock packages plus pip-audit inputs present; live scan PASS |
| AM-08 | Full verification | `PASS` | result=PASS fast=False passed=32/32 clone=PASS |
| AM-09 | Count integrity | `PASS` | TESTS=1551/1551 categories=714/0:clean-clone-full-verification:gate-tests,788/0:clean-clone-full-verification:image-and-service-suites,49/0:clean-clone-full-verification:infra-and-live-scenarios |
| AM-10 | Foundation functional path | `PASS` | stack=PASS, integration=PASS, infra=PASS, smoke=PASS, backup=PASS, restart=PASS, dependency-failure=PASS, fresh-install=PASS |
| AM-11 | Configured Model Gateway | `PASS` | result=PASS state=SUCCEEDED model=openai:gpt-4o-mini configured=openai:gpt-4o-mini |
| AM-12 | Agent Runtime functional path | `PASS` | live=SUCCEEDED; gate:agentRuntimeTests=PASS, agent-runtime-smoke=PASS, agent-durability=PASS |
| AM-13 | Cross-Gate tool path | `PASS` | result=PASS state=SUCCEEDED; model calls through the gateway=True, the configured model made a valid tool request=True, at least one tool executed in a sandbox=True, tool results delivered to the runtime=True, the runtime called the model again after a sandbox result=True, host sentinel untouched=True, no sandbox container outlives the run=True |
| AM-14 | Live ToolRequest contract | `PASS` | result=PASS repairs=0 requests=7 |
| AM-15 | Forged ToolResult defense | `PASS` | probe=PASS steps={'forgery.refused_while_the_sandbox_executes': 'PASS', 'forgery.stored_result_is_the_sandbox_result': 'PASS', 'forgery.refused_after_the_run_ended': 'PASS', 'forgery.nothing_changed_after_the_refusals': 'PASS'}; M1-P=DEFENDED, control=VALID |
| AM-16 | Sandbox filesystem isolation | `PASS` | M1-D=DEFENDED, M1-E=DEFENDED, control=VALID |
| AM-17 | Sandbox privilege boundary | `PASS` | M1-A=DEFENDED, M1-C=DEFENDED, M1-F=DEFENDED, M1-G=DEFENDED, control=VALID; hostSentinel=True |
| AM-18 | Host secret isolation | `PASS` | M1-B=DEFENDED, control=VALID |
| AM-19 | Network boundary | `PASS` | M1-I=DEFENDED, control=VALID |
| AM-20 | Resource, timeout and cleanup | `PASS` | M1-K=DEFENDED, M1-R=DEFENDED, control=VALID; gate:sandboxTests=PASS, sandbox-timeout=PASS, sandbox-cancellation=PASS |
| AM-21 | R-G3-001 | `PASS` | result=PASS controls=10/10 untrusted=False; M1-G=DEFENDED, control=VALID |
| AM-22 | Durability | `PASS` | agent-durability=PASS, agent-cancellation=PASS, agent-deadline=PASS, sandbox-recovery=PASS, sandbox-tool-result-origin=PASS, restart=PASS |
| AM-23 | SSE terminal drain | `PASS` | result=PASS exit=0 test=test_a_terminal_stream_drains_every_page_after_the_cursor |
| AM-24 | Secret and public-history scans | `PASS` | history=[('cmd-0006', 0)] checkpointValidation=PASS |
| AM-25 | Documentation and runbooks | `PASS` | review=PASS checks=3/3 |
| AM-26 | Engineering Memory | `PASS` | review=PASS effective=60/60 failures=0 |
| AM-27 | Accumulated M1 completeness | `PASS` | finalGates=4/4 current=PASS coverage=100.0 evidence=100.0 |
| AM-28 | Independent Red Team | `PASS` | result=RED_TEAM_PASS defended=19/19 escaped=0 control=VALID |
| AM-29 | Findings threshold | `PASS` | total=1 blocking=none requiredFields=True |
| AM-30 | Audit-checkpoint assurance | `PASS` | green=PASS completeness=PASS mirror=PASS; build=PASS, unitTests=PASS, integrationTests=PASS, e2e=PASS, lint=PASS, staticAnalysis=PASS, security=PASS, documentation=PASS, checkpointValidation=PASS, greenKeeper=PASS, deliveryCompleteness=PASS |
| AM-31 | Attestation and derived verdict | `PASS` | attestation=present mechanism=FRESH_SESSION_INDEPENDENT_AUDIT fresh=True review=APPROVED; verdict derives post-seal |
| AM-32 | Review bundle | `PASS` | pre-seal=PASS 9/9; regenerated and revalidated after publication |
