# Affected Red Team

Result: `DEFENDED`

- Checkpoint: `SETUP-00-CP-0012`
- Generated: `2026-09-21T15:28:03Z`
- Executed battery: `M0-INTERNAL-RED-TEAM.json`
- Null-mutation control: `VALID`

Every number below is derived from the machine-readable battery and the audit registry; no
total here is maintained by hand, and the categories do not overlap.

| Category | Count | Missing |
|---|---|---|
| `originalRedTeam` | 38 | none |
| `additionalControlAttacks` | 35 | ATT-01, ATT-02, ATT-03, ATT-04, ATT-05, ATT-06, ATT-07, ATT-08, ATT-09, ATT-10, ATT-11, ATT-12, ATT-13, ATT-14, ATT-15, ATT-16, ATT-17, ATT-18, INT-06, MEM-02, MEM-03, MEM-04, PRE-02, PRE-03, STL-03 |
| `attestationScenarios` | 14 | none |
| `positiveControls` | 2 | none |

- Total adversarial scenarios executed: `73`
- Defended: `73`; escaped: `0`

## Categories

### originalRedTeam

the mandatory battery of every registered audit, re-parsed from its sealed report.

- Executed: `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`, `I`, `INT-01`, `INT-02`, `INT-03`, `INT-04`, `INT-05`, `J`, `K`, `L`, `M`, `MEM-01`, `N`, `O`, `P`, `PRE-01`, `Q`, `R`, `S`, `SEC-01`, `STL-01`, `STL-02`, `STL-04`, `STL-05`, `T`, `U`, `V`, `W`, `X`, `Y`, `Z`

### additionalControlAttacks

the additional battery of every registered audit, plus the attacks this delivery's new surfaces deserve.

- Executed: `AA`, `AB`, `AC`, `AD`, `AE`, `AF`, `AG`, `AH`, `AI`, `AJ`, `AK`, `AL`, `AM`, `AN`, `AO`, `AP`, `AQ`, `AR`, `AS`, `AT`, `AU`, `AV`, `AW`, `AX`, `AY`, `AZ`, `BA`, `BB`, `BC`, `BD`, `BE`, `BF`, `BG`, `BH`, `BI`

### attestationScenarios

attacks that target the audit-attestation model and the milestone status vocabulary, which is the surface this delivery changed.

- Executed: `AI`, `AJ`, `AK`, `AU`, `AV`, `AW`, `AX`, `AY`, `AZ`, `BA`, `BB`, `BC`, `BD`, `R`

### positiveControls

executed positive paths; an adversarial battery cannot contain them, and a control proven only by refusals is not proven.

- `positive milestone promotion`: `PASS`, 9 of 9 checks (`POSITIVE-PROMOTION-VALIDATION.json`)
- `successor anchor durability`: `PASS`, 8 of 8 checks (`SUCCESSOR-DURABILITY.json`)
