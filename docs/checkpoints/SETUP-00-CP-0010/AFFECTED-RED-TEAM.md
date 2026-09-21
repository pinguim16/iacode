# Affected Red Team

Result: `DEFENDED`

- Checkpoint: `SETUP-00-CP-0010`
- Generated: `2026-09-21T05:41:08Z`
- Executed battery: `M0-INTERNAL-RED-TEAM.json`
- Null-mutation control: `VALID`

Every number below is derived from the machine-readable battery and the audit registry; no
total here is maintained by hand, and the categories do not overlap.

| Category | Count | Missing |
|---|---|---|
| `originalRedTeam` | 26 | none |
| `additionalControlAttacks` | 30 | none |
| `attestationScenarios` | 14 | none |
| `positiveControls` | 2 | none |

- Total adversarial scenarios executed: `56`
- Defended: `56`; escaped: `0`

## Categories

### originalRedTeam

the mandatory battery of every registered audit, re-parsed from its sealed report.

- Executed: `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`, `I`, `J`, `K`, `L`, `M`, `N`, `O`, `P`, `Q`, `R`, `S`, `T`, `U`, `V`, `W`, `X`, `Y`, `Z`

### additionalControlAttacks

the additional battery of every registered audit, plus the attacks this delivery's new surfaces deserve.

- Executed: `AA`, `AB`, `AC`, `AD`, `AE`, `AF`, `AG`, `AH`, `AI`, `AJ`, `AK`, `AL`, `AM`, `AN`, `AO`, `AP`, `AQ`, `AR`, `AS`, `AT`, `AU`, `AV`, `AW`, `AX`, `AY`, `AZ`, `BA`, `BB`, `BC`, `BD`

### attestationScenarios

attacks that target the audit-attestation model and the milestone status vocabulary, which is the surface this delivery changed.

- Executed: `AI`, `AJ`, `AK`, `AU`, `AV`, `AW`, `AX`, `AY`, `AZ`, `BA`, `BB`, `BC`, `BD`, `R`

### positiveControls

executed positive paths; an adversarial battery cannot contain them, and a control proven only by refusals is not proven.

- `positive milestone promotion`: `PASS`, 7 of 7 checks (`POSITIVE-PROMOTION-VALIDATION.json`)
- `successor anchor durability`: `PASS`, 8 of 8 checks (`SUCCESSOR-DURABILITY.json`)
