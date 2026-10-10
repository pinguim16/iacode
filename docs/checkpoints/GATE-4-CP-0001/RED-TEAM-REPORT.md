# Internal Red Team — GATE 4 — QUALITY ENGINE

Result: `RED_TEAM_PASS`

- Baseline control: `VALID`
- Attacks defended: 10/10

| Attack | Target | Mutation | Expected | Observed | Result |
|---|---|---|---|---|---|
| `G4-A` | missing result | remove the only mandatory result | derived verdict FAIL names the missing check | verdict=FAIL; reasons=('missing result for q001-unit',) | `DEFENDED` |
| `G4-B` | exit-code forgery | keep PASSED and flip exitCode to 1 | the result contract refuses the contradictory shape | contract refused non-zero PASS | `DEFENDED` |
| `G4-C` | forged evidence | replace the resolved digest set | the evidence reference is unresolved and verdict is FAIL | verdict=FAIL; reasons=('q001-unit has unresolved evidence evidence-red-team',) | `DEFENDED` |
| `G4-D` | policy mutation | change maxCheckSeconds under the same planId | the immutable store refuses PLAN_ID_CONFLICT | store refused PLAN_ID_CONFLICT | `DEFENDED` |
| `G4-E` | snapshot mutation | change snapshotDigest under the same planId | the immutable store refuses PLAN_ID_CONFLICT | store refused PLAN_ID_CONFLICT | `DEFENDED` |
| `G4-F` | wrong origin | post a result with origin CALLER | the closed origin contract refuses it | contract refused origin | `DEFENDED` |
| `G4-G` | timed_out result | replace PASSED with TIMED_OUT | the derived verdict is FAIL | verdict=FAIL; reasons=('q001-unit ended TIMED_OUT',) | `DEFENDED` |
| `G4-H` | denied result | replace PASSED with DENIED | the derived verdict is FAIL | verdict=FAIL; reasons=('q001-unit ended DENIED',) | `DEFENDED` |
| `G4-I` | cancelled result | replace PASSED with CANCELLED | the derived verdict is FAIL | verdict=FAIL; reasons=('q001-unit ended CANCELLED',) | `DEFENDED` |
| `G4-J` | unknown status | submit status ASSERTED_GOOD | the closed result-status contract refuses it | contract refused status | `DEFENDED` |
