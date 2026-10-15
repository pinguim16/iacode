# Internal Red Team — GATE 4 — QUALITY ENGINE

Result: `RED_TEAM_PASS`

- Baseline control: `VALID`
- Attacks defended: 20/20

| Attack | Target | Mutation | Expected | Observed | Result |
|---|---|---|---|---|---|
| `A` | missing result | remove the only mandatory result | derived verdict FAIL names the missing check | verdict=FAIL; reasons=('missing result for q001-unit',) | `DEFENDED` |
| `B` | exit-code forgery | keep PASSED and flip exitCode to 1 | the result contract refuses the contradictory shape | contract refused non-zero PASS | `DEFENDED` |
| `C` | forged evidence | replace the resolved digest set | the evidence reference is unresolved and verdict is FAIL | verdict=FAIL; reasons=('q001-unit has unresolved evidence evidence-red-team',) | `DEFENDED` |
| `D` | policy mutation | change maxCheckSeconds under the same planId | the immutable store refuses PLAN_ID_CONFLICT | store refused PLAN_ID_CONFLICT | `DEFENDED` |
| `E` | snapshot mutation | change snapshotDigest under the same planId | the immutable store refuses PLAN_ID_CONFLICT | store refused PLAN_ID_CONFLICT | `DEFENDED` |
| `F` | wrong origin | post a result with origin CALLER | the closed origin contract refuses it | contract refused origin | `DEFENDED` |
| `G` | timed_out result | replace PASSED with TIMED_OUT | the derived verdict is FAIL | verdict=FAIL; reasons=('q001-unit ended TIMED_OUT',) | `DEFENDED` |
| `H` | denied result | replace PASSED with DENIED | the derived verdict is FAIL | verdict=FAIL; reasons=('q001-unit ended DENIED',) | `DEFENDED` |
| `I` | cancelled result | replace PASSED with CANCELLED | the derived verdict is FAIL | verdict=FAIL; reasons=('q001-unit ended CANCELLED',) | `DEFENDED` |
| `J` | unknown status | submit status ASSERTED_GOOD | the closed result-status contract refuses it | contract refused status | `DEFENDED` |
| `K` | bundle integrity | alter one payload byte | validator refuses with digest mismatch | result=FAIL; expected-finding=True | `DEFENDED` |
| `L` | mandatory bundle evidence | remove subject STATE.json | validator refuses with missing required checkpoint artifact: STATE.json | result=FAIL; expected-finding=True | `DEFENDED` |
| `M` | archive path safety | add a traversal member | validator refuses with unsafe archive member | result=FAIL; expected-finding=True | `DEFENDED` |
| `N` | bundle secret scan | add canonical credential-shaped bytes | validator refuses with secret scan found | result=FAIL; expected-finding=True | `DEFENDED` |
| `O` | archive uniqueness | duplicate a member name | validator refuses with duplicate member names | result=FAIL; expected-finding=True | `DEFENDED` |
| `P` | live adverse lifecycle | execute restart, cancellation, timeout and forged-origin scenarios | every fail-closed invariant survives in the current verifier run | recovery=PASS; cancellation=PASS; timeout=PASS; forged-origin=PASS | `DEFENDED` |
| `Q` | pre-persistence secret containment | send a canonical scanner-detected marker under an ordinary structured output key | reject before object or metadata persistence and derive FAIL from a sanitized result | status=ERROR; verdict=FAIL; objects=0; records=0; prohibited-bytes-absent=True | `DEFENDED` |
| `R` | scanner availability | make the canonical evidence scanner throw before it can classify clean bytes | fail closed before any lookup or write and derive FAIL | scan-before-store=True; status=ERROR; verdict=FAIL; objects=0; records=0 | `DEFENDED` |
| `S` | legacy persisted object | replace already persisted clean bytes with a canonical credential shape | rescan after read, refuse resolution and derive FAIL | resolved=False; rescanned-after-read=True; verdict=FAIL | `DEFENDED` |
| `T` | review bundle portability, determinism and declaration binding | rebuild twice from a detached transport clone, validate there and mutate the declaration | byte-identical secret-clean rebuilds match the declaration and a stale digest is refused | deterministic=True; portable=True; categories=True; declaration=True; stale-refused=True | `DEFENDED` |
