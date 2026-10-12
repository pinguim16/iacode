# Gate 4 independent Red Team

Result: `RED_TEAM_FAIL`

- Null control: `VALID`
- Defended: 19/20
- Escaped: 1

The complete A–T battery was executed by this fresh auditing session over valid controls. A–J and Q–S ran in the rebuilt evaluator image; K–O attacked the real bundle validator; P is bound to the single integral verifier; T is bound to detached deterministic rebuilds. Synthetic credential material was assembled only in memory and is absent from this report.

| Attack | Target | Expected | Observed | Result |
|---|---|---|---|---|
| `A` | missing result | derived verdict FAIL names the missing check | verdict=FAIL; reasons=('missing result for q001-unit',) | `DEFENDED` |
| `B` | exit-code forgery | the result contract refuses the contradictory shape | contract refused non-zero PASS | `DEFENDED` |
| `C` | forged evidence | the evidence reference is unresolved and verdict is FAIL | verdict=FAIL; reasons=('q001-unit has unresolved evidence evidence-red-team',) | `DEFENDED` |
| `D` | policy mutation | the immutable store refuses PLAN_ID_CONFLICT | store refused PLAN_ID_CONFLICT | `DEFENDED` |
| `E` | snapshot mutation | the immutable store refuses PLAN_ID_CONFLICT | store refused PLAN_ID_CONFLICT | `DEFENDED` |
| `F` | wrong origin | the closed origin contract refuses it | contract refused origin | `DEFENDED` |
| `G` | timed_out result | the derived verdict is FAIL | verdict=FAIL; reasons=('q001-unit ended TIMED_OUT',) | `DEFENDED` |
| `H` | denied result | the derived verdict is FAIL | verdict=FAIL; reasons=('q001-unit ended DENIED',) | `DEFENDED` |
| `I` | cancelled result | the derived verdict is FAIL | verdict=FAIL; reasons=('q001-unit ended CANCELLED',) | `DEFENDED` |
| `J` | unknown status | the closed result-status contract refuses it | contract refused status | `DEFENDED` |
| `K` | bundle integrity | validator refuses with digest mismatch | result=FAIL; expected-finding=True | `DEFENDED` |
| `L` | mandatory bundle evidence | validator refuses with missing required checkpoint artifact: STATE.json | result=FAIL; expected-finding=True | `DEFENDED` |
| `M` | archive path safety | validator refuses with unsafe archive member | result=FAIL; expected-finding=True | `DEFENDED` |
| `N` | bundle secret scan | validator refuses with secret scan found | result=FAIL; expected-finding=True | `DEFENDED` |
| `O` | archive uniqueness | validator refuses with duplicate member names | result=FAIL; expected-finding=True | `DEFENDED` |
| `P` | live adverse lifecycle | every fail-closed invariant survives in the current verifier run | quality-recovery=PASS; quality-cancellation=PASS; quality-timeout=PASS; sandbox-tool-result-origin=PASS | `DEFENDED` |
| `Q` | pre-persistence secret containment | reject before object or metadata persistence and derive FAIL from a sanitized result | scannerKinds=['GitHub credential']; scan-before-store=True; status=ERROR; verdict=FAIL; objects=0; records=0; evidence=0; logs-clean=True | `DEFENDED` |
| `R` | scanner availability | fail closed before any lookup or write and derive FAIL | scan-before-store=True; status=ERROR; verdict=FAIL; objects=0; records=0 | `DEFENDED` |
| `S` | legacy persisted object | rescan after read, refuse resolution and derive FAIL | resolved=False; rescanned-after-read=True; verdict=FAIL | `DEFENDED` |
| `T` | review transport determinism and command-input portability | byte-identical secret-clean archives and no local-only input can support a sealed checkpoint | bundle=FAIL; digest=07bb328a4316297d0b6bd2df986c7b5f5fb41b30c8b2fb58cd99a8d96c24c168,07bb328a4316297d0b6bd2df986c7b5f5fb41b30c8b2fb58cd99a8d96c24c168; git-metadata=True; absolute-temp=True; ignored=True; untracked-local-only=True | `ESCAPED` |
