# Final Gate 4 audit matrix

Result: `REWORK_REQUIRED`

| Criterion | Title | Observed | Result |
|---|---|---|---|
| `G4A-01` | Sealed subject identity | tag/origin/HEAD=e21d30fde473f302d0f8f60b59acf008fa52e250 | `PASS` |
| `G4A-02` | Published checkpoint and Git integrity | files=41 commands=62 | `PASS` |
| `G4A-03` | Single full verifier | stages=42/42 | `PASS` |
| `G4A-04` | No verifier retry | invocation=1 retry=0 rerun=False | `PASS` |
| `G4A-05` | Compose isolation and cleanup | project=iacode-verify-67b6ff3ce117 sharedUnchanged=True ownedRemoved=True | `PASS` |
| `G4A-06` | Requirements | 201/201 | `PASS` |
| `G4A-07` | Tests | 1709/1709 | `PASS` |
| `G4A-08` | Guardrails | 97/97; zero unresolved guardrail failures | `PASS` |
| `G4A-09` | Green Keeper | 13/13 subject gates | `PASS` |
| `G4A-10` | Prior findings | G4-F-001, G4-F-002, G4-F-003 | `PASS` |
| `G4A-11` | Internal mirror evidence | passed=17/18 notApplicable=1; internal evidence only | `PASS` |
| `G4A-12` | Architecture and Gate scope | 12/12 | `PASS` |
| `G4A-13` | G4-X7 secret containment | ERROR, FAIL, objects=0, metadata=0 | `PASS` |
| `G4A-14` | G4-X7 scanner unavailable | ERROR, FAIL, objects=0, metadata=0 | `PASS` |
| `G4A-15` | G4-X7 legacy object | resolution refused after re-scan; verdict FAIL | `PASS` |
| `G4A-16` | Command-input transport | .git, absolute temporary and ignored refused; untracked local-only refused at validation | `PASS` |
| `G4A-17` | Bundle deterministic rebuild | rebuilt=['07bb328a4316297d0b6bd2df986c7b5f5fb41b30c8b2fb58cd99a8d96c24c168', '07bb328a4316297d0b6bd2df986c7b5f5fb41b30c8b2fb58cd99a8d96c24c168'] | `PASS` |
| `G4A-18` | Bundle portable validation | both rebuilt archives secret-clean, manifest-complete and portable | `PASS` |
| `G4A-19` | Declared bundle reconstructibility | declared=8856ce50acebfa02528ad318247c22e6e460c224eb62774c99a35cb5cd734578 rebuilt=['07bb328a4316297d0b6bd2df986c7b5f5fb41b30c8b2fb58cd99a8d96c24c168', '07bb328a4316297d0b6bd2df986c7b5f5fb41b30c8b2fb58cd99a8d96c24c168']; declaredSize=562710 rebuiltSize=751518 | `FAIL` |
| `G4A-20` | Independent Red Team control | VALID | `PASS` |
| `G4A-21` | Independent Red Team A-T | 19/20 defended; T escaped | `FAIL` |
| `G4A-22` | Independent review | HIGH G4-F-004 blocks approval | `FAIL` |
