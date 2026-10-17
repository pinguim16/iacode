# Gate 5 internal Red Team

Same-session audit only; no independent verdict.

Result: RED_TEAM_PASS

| Attack | Observed | Result |
|---|---|---|
| A | verdict=FAIL; reasons=('missing result for q001-unit',) | DEFENDED |
| B | contract refused non-zero PASS | DEFENDED |
| C | verdict=FAIL; reasons=('q001-unit has unresolved evidence evidence-red-team',) | DEFENDED |
| D | store refused PLAN_ID_CONFLICT | DEFENDED |
| E | store refused PLAN_ID_CONFLICT | DEFENDED |
| F | contract refused origin | DEFENDED |
| G | verdict=FAIL; reasons=('q001-unit ended TIMED_OUT',) | DEFENDED |
| H | verdict=FAIL; reasons=('q001-unit ended DENIED',) | DEFENDED |
| I | verdict=FAIL; reasons=('q001-unit ended CANCELLED',) | DEFENDED |
| J | contract refused status | DEFENDED |
| K | result=FAIL; expected-finding=True | DEFENDED |
| L | result=FAIL; expected-finding=True | DEFENDED |
| M | result=FAIL; expected-finding=True | DEFENDED |
| N | result=FAIL; expected-finding=True | DEFENDED |
| O | result=FAIL; expected-finding=True | DEFENDED |
| P | recovery=PASS; cancellation=PASS; timeout=PASS; forged-origin=PASS; secret-output=PASS | DEFENDED |
| Q | status=ERROR; verdict=FAIL; objects=0; records=0; prohibited-bytes-absent=True | DEFENDED |
| R | scan-before-store=True; status=ERROR; verdict=FAIL; objects=0; records=0 | DEFENDED |
| S | resolved=False; rescanned-after-read=True; verdict=FAIL | DEFENDED |
| T | deterministic=True; portable=True; categories=True; declaration=True; stale-refused=True | DEFENDED |
| G5-AUTH | unauthenticated-domain-refused-before-effects: PASS | DEFENDED |
| G5-TOOL-IPC | closed-ipc-refuses-tool-result: PASS | DEFENDED |
| G5-VERDICT-IPC | closed-ipc-refuses-quality-verdict: PASS | DEFENDED |
| G5-HOST-IPC | closed-ipc-refuses-shell.exec: PASS | DEFENDED |
| G5-SECRET | secret-upload-refused-before-sql-or-object-persistence: PASS | DEFENDED |
| G5-REPLAY | redis-replay-refusal-survives-api-restart: PASS | DEFENDED |
| G5-CONSENT | cli-changed-or-wrong-consent-refused-locally: PASS | DEFENDED |
| G5-TASK-LOSS | lost-response-has-one-real-persisted-run: PASS | DEFENDED |
| G5-TOOL-FORGERY | authenticated-external-sandbox-result-forgery-refused: PASS | DEFENDED |
| G5-QUALITY-LOSS | actual-quality-response-loss-reconciles-once-without-replay: PASS | DEFENDED |
| G5-SIGINT | actual-cli-sigint-stops-only-local-observation: PASS | DEFENDED |
| G5-TAMPER | actual-object-tamper-refused-before-task-persistence: PASS | DEFENDED |
| G5-NATIVE-TRUST | actual untrusted refusal count=1 | DEFENDED |
