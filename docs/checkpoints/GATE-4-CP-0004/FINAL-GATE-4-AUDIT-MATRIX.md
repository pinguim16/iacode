# Final Gate 4 audit matrix

Result: `REWORK_REQUIRED`

| Criterion | Title | Observed | Result |
|---|---|---|---|
| `G4A-01` | Subject identity and immutability | sealed=5d47200fde08c47b7a6410be2204b4c1b9fbadc1 content=4d0cc8e3bb9a329e50af99cf58f01c19087c3433 | `PASS` |
| `G4A-02` | Review bundle identity | sha256=197cd4c82b7e6fa75f51c72d7db3daf2e84cb7df03ac4028e0efa572a80562cd | `PASS` |
| `G4A-03` | Bundle completeness | categories={'tests': True, 'migrations': True, 'schemas': True, 'policies': True, 'documentation': True, 'changeset': True, 'gitState': True, 'manifest': True} | `PASS` |
| `G4A-04` | Bundle determinism and portability | rebuilt=['ec394cae89d2f6df750ae1d5ccd802791a0ffc1982b5ead72175f1b9ed3d8e1e', 'ec394cae89d2f6df750ae1d5ccd802791a0ffc1982b5ead72175f1b9ed3d8e1e'] | `PASS` |
| `G4A-05` | Local checkpoint validity | published clone validations all exited zero | `PASS` |
| `G4A-06` | Published detached validity | detached subject returned CHECKPOINT_VALID | `PASS` |
| `G4A-07` | Historical compatibility | integrity and complete verification passed from published content | `FAIL` |
| `G4A-08` | Canonical denominator | subject=216 audit=198 | `PASS` |
| `G4A-09` | Requirement evidence | subjectComplete=True auditComplete=True | `PASS` |
| `G4A-10` | Quality contracts | architecture=PASS Gate4Stages=True | `PASS` |
| `G4A-11` | Detection and planning | architecture=PASS Gate4Stages=True | `PASS` |
| `G4A-12` | Sandbox-only runners | architecture=PASS Gate4Stages=True | `PASS` |
| `G4A-13` | Evidence immutability | architecture=PASS Gate4Stages=True | `PASS` |
| `G4A-14` | Verdict derivation | architecture=PASS Gate4Stages=True | `PASS` |
| `G4A-15` | Durable lifecycle | architecture=PASS Gate4Stages=True | `PASS` |
| `G4A-16` | Ownership and origin | architecture=PASS Gate4Stages=True | `PASS` |
| `G4A-17` | API and runtime integration | architecture=PASS Gate4Stages=True | `PASS` |
| `G4A-18` | Functional PASS and FAIL | quality-pass and quality-fail both passed | `PASS` |
| `G4A-19` | IACode self-evaluation and reproduction | quality-iacode and quality-reproduction passed | `PASS` |
| `G4A-20` | Recovery, cancellation and timeout | quality-recovery=PASS; quality-cancellation=PASS; quality-timeout=PASS | `PASS` |
| `G4A-21` | Cross-Gate regression | verification=FAIL stages=42 | `FAIL` |
| `G4A-22` | Full clean-clone verification | verification=FAIL stages=42 | `FAIL` |
| `G4A-23` | Test and count integrity | policy-owned counted suites passed=True | `PASS` |
| `G4A-24` | Security and dependencies | dependency=PASS redTeam=RED_TEAM_PASS | `PASS` |
| `G4A-25` | Documentation and architecture | architecture=12/12 | `PASS` |
| `G4A-26` | Lessons and guardrails | memory=PASS | `PASS` |
| `G4A-27` | G4-F-001 closure | probe=PASS scannerKinds=['GitHub credential'] | `PASS` |
| `G4A-28` | G4-X7 live evaluator path | status=ERROR verdict=FAIL objects=0 records=0 | `PASS` |
| `G4A-29` | Scanner failure | status=ERROR verdict=FAIL | `PASS` |
| `G4A-30` | Legacy persisted object | resolved=False verdict=FAIL | `PASS` |
| `G4A-31` | Independent review | one or more prior criteria failed | `FAIL` |
| `G4A-32` | Independent Red Team | result=RED_TEAM_PASS defended=20/20 | `PASS` |
| `G4A-33` | Audit checkpoint assurance | green=GREEN completeness=PASS mirror=PASS | `PASS` |
| `G4A-34` | Gate verdict | secondTool=FAILED review=REWORK_REQUIRED redTeam=RED_TEAM_PASS | `FAIL` |
