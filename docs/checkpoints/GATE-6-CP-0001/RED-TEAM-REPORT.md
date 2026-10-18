# Gate 6 internal Red Team

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
| G6-EXPERIENCE-01 | unauthenticated-capture-refused-before-effects: PASS | DEFENDED |
| G6-EXPERIENCE-02 | invalid-signature-refused: PASS | DEFENDED |
| G6-EXPERIENCE-03 | stale-authentication-refused: PASS | DEFENDED |
| G6-EXPERIENCE-04 | consent-missing-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-05 | consent-denied-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-06 | consent-type-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-07 | private-transcript-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-08 | forged-verdict-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-09 | forged-rights-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-10 | secret-ingress-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-11 | known-capability-form-0-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-12 | known-capability-form-1-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-13 | known-capability-form-2-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-14 | known-capability-form-3-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-15 | known-capability-form-4-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-16 | known-capability-form-5-refused-before-persistence: PASS | DEFENDED |
| G6-EXPERIENCE-17 | cross-project-source-capture-refused: PASS | DEFENDED |
| G6-EXPERIENCE-18 | actual-redis-authentication-replay-refused: PASS | DEFENDED |
| G6-EXPERIENCE-19 | actual-accepted-experience-response-loss-one-durable-effect: PASS | DEFENDED |
| G6-EXPERIENCE-20 | actual-concurrent-retry-one-row-one-capture-audit: PASS | DEFENDED |
| G6-EXPERIENCE-21 | cross-project-cursor-refused: PASS | DEFENDED |
| G6-EXPERIENCE-22 | cross-project-get-refused: PASS | DEFENDED |
| G6-EXPERIENCE-23 | cross-project-delete-refused: PASS | DEFENDED |
| G6-EXPERIENCE-24 | denied-rag-use-no-data: PASS | DEFENDED |
| G6-EXPERIENCE-25 | denied-training-use-no-data: PASS | DEFENDED |
| G6-EXPERIENCE-26 | denied-distillation-use-no-data: PASS | DEFENDED |
| G6-EXPERIENCE-27 | denied-unknown-use-no-data: PASS | DEFENDED |
| G6-EXPERIENCE-28 | conflicting-stable-request-refused: PASS | DEFENDED |
| G6-EXPERIENCE-29 | authentication-replay-survives-real-restart: PASS | DEFENDED |
| G6-EXPERIENCE-30 | actual-source-object-corrupt-fails-closed: PASS | DEFENDED |
| G6-EXPERIENCE-31 | actual-source-object-remove-fails-closed: PASS | DEFENDED |
| G6-EXPERIENCE-32 | new-key-cannot-resurrect-withdrawn-source: PASS | DEFENDED |
| G6-EXPERIENCE-33 | expired-read-denied-without-manual-sweep: PASS | DEFENDED |
| G6-EXPERIENCE-34 | actual-owned-background-sweeper-physically-purged: PASS | DEFENDED |
| G6-EXPERIENCE-35 | expired-request-retry-cannot-renew: PASS | DEFENDED |
| G6-EXPERIENCE-36 | expired-source-new-key-cannot-resurrect: PASS | DEFENDED |
| G6-EXPERIENCE-37 | actual-production-logs-retain-observability-not-ingress: PASS | DEFENDED |
| G6-EXPERIENCE-38 | actual-expired-capability-refuses-experience-access: PASS | DEFENDED |
