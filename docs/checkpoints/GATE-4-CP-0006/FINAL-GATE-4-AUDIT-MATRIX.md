# Final Gate 4 audit matrix

Result: `APPROVED`

| Criterion | Title | Observed | Result |
|---|---|---|---|
| `G4A-01` | Subject identity and immutability | sealed=c631270e49c095a9777825c0bc18818694c07ffb content=cac77ddef9c351ce828442d9312db69083aab81e | `PASS` |
| `G4A-02` | Subject anchor | checkpoint=GATE-4-CP-0005 commit=c631270e49c095a9777825c0bc18818694c07ffb | `PASS` |
| `G4A-03` | Review bundle identity | sha256=bb130be4e4e871af158bb71b0bc4c0f0a1da73af50a5db74df49f870b2d14d59 | `PASS` |
| `G4A-04` | Bundle determinism and portability | rebuilt=['6fdd6f990f7c0c7c67cc623ad5e428b8edcac50b8292d79f7dcb0c73a3e30499', '6fdd6f990f7c0c7c67cc623ad5e428b8edcac50b8292d79f7dcb0c73a3e30499'] | `PASS` |
| `G4A-05` | Published detached validity | detached subject returned CHECKPOINT_VALID | `PASS` |
| `G4A-06` | Historical compatibility | 27 sealed checkpoints validate under this tooling | `PASS` |
| `G4A-07` | Canonical requirement denominator | subject=221 audit=200 | `PASS` |
| `G4A-08` | Requirement evidence | subject=221/221 auditComplete=True | `PASS` |
| `G4A-09` | Quality architecture | architecture=12/12 Gate4Stages=True | `PASS` |
| `G4A-10` | Cross-Gate integration | countedSuites=True verification=PASS | `PASS` |
| `G4A-11` | Full published verification | stages=42/42 exit=0 | `PASS` |
| `G4A-12` | No hidden rerun | invocationCount=1 retryCount=0 verifierRerun=False | `PASS` |
| `G4A-13` | Historical infra/smoke order | canonicalOrder=True contiguous=True infra=PASS smoke=PASS | `PASS` |
| `G4A-14` | Compose isolation | project=iacode-verify-09b742f9550c ports=docker-allocated | `PASS` |
| `G4A-15` | Cleanup and shared-project preservation | pre=PASS post=PASS sharedUnchanged=True ownedRemoved=True | `PASS` |
| `G4A-16` | G4-F-002 closure | singleRun=PASS focusedGuardrails=True | `PASS` |
| `G4A-17` | G4-F-001 closure | probe=PASS scannerKinds=['GitHub credential'] | `PASS` |
| `G4A-18` | G4-X7 marker containment | status=ERROR verdict=FAIL objects=0 records=0 | `PASS` |
| `G4A-19` | Scanner unavailable | status=ERROR verdict=FAIL | `PASS` |
| `G4A-20` | Legacy object | resolved=False verdict=FAIL | `PASS` |
| `G4A-21` | Independent Red Team A-T | result=RED_TEAM_PASS defended=20/20 | `PASS` |
| `G4A-22` | Test denominator | tests=1701/1701 verification=PASS | `PASS` |
| `G4A-23` | Guardrail denominator | guardrails=97/97 failures=0 | `PASS` |
| `G4A-24` | Lessons and recurrence | lessons=93/96 focusedGuardrails=True | `PASS` |
| `G4A-25` | Wrapper schema | canonical result-field and contradictory-alias guard passed | `PASS` |
| `G4A-26` | Ledger auto-invalidation | Green Keeper, Red Team and mirror staleness guards passed | `PASS` |
| `G4A-27` | Security and dependencies | dependency=PASS falsePass=PASS | `PASS` |
| `G4A-28` | Documentation and architecture | architecture=12/12 docs=202/202 relative documentation links resolve | `PASS` |
| `G4A-29` | Review-bundle content | categories={'tests': True, 'migrations': True, 'schemas': True, 'policies': True, 'documentation': True, 'changeset': True, 'gitState': True, 'manifest': True} | `PASS` |
| `G4A-30` | Audit checkpoint assurance | green=GREEN completeness=PASS mirror=PASS | `PASS` |
| `G4A-31` | Independent review | Critical=0 High=0; no blocking criterion failed | `PASS` |
| `G4A-32` | Second-tool/session validation | fresh-session evidence executed by Codex/OpenAI; no internal subject verdict relabelled | `PASS` |
| `G4A-33` | Audit attestation | state=VERIFIED audit=G4-CP-0006 | `PASS` |
| `G4A-34` | Gate verdict | secondTool=PASSED review=APPROVED redTeam=RED_TEAM_PASS | `PASS` |
