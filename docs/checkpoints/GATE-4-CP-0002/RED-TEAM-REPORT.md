# Gate 4 independent Red Team

Result: `RED_TEAM_FAIL`  
Valid null control: `VALID`  
Defended: `16/17`  
Escaped: `G4-X7`

The fresh-session battery used a published transport clone at the sealed subject tag. Its canonical
unmutated verdict control and the unmodified sealed review bundle both validated. The canonical ten
false-PASS mutations, five bundle mutations, and the four live adverse scenarios were defended.
The additional pre-persistence credential-containment attack escaped. No credential value is
present in the report or harness; the synthetic marker is assembled only in memory.

## Mandatory battery

| Attack | Category | Target | Mutation | Expected | Observed | Result |
|---|---|---|---|---|---|---|
| A | mandatory | result completeness | remove a mandatory result | derive FAIL | G4-A missing result refused | `DEFENDED` |
| B | mandatory | exit binding | forge an exit code | derive FAIL | G4-B forgery refused | `DEFENDED` |
| C | mandatory | evidence binding | forge evidence content | derive FAIL | G4-C forged evidence refused | `DEFENDED` |
| D | mandatory | policy binding | mutate the policy | derive FAIL | G4-D policy mutation refused | `DEFENDED` |
| E | mandatory | snapshot binding | mutate the snapshot | derive FAIL | G4-E snapshot mutation refused | `DEFENDED` |
| F | mandatory | sandbox origin | submit the wrong origin | derive FAIL | G4-F wrong origin refused | `DEFENDED` |
| G | mandatory | timeout semantics | submit a timed-out result | derive FAIL | G4-G timed-out result refused | `DEFENDED` |
| H | mandatory | denial semantics | submit a denied result | derive FAIL | G4-H denied result refused | `DEFENDED` |
| I | mandatory | cancellation semantics | submit a cancelled result | derive FAIL | G4-I cancelled result refused | `DEFENDED` |
| J | mandatory | closed status vocabulary | submit an unknown status | derive FAIL | G4-J unknown status refused | `DEFENDED` |
| K | mandatory | bundle integrity | alter one payload byte | validator refuses checksum mismatch | G4-X1 bundle refused | `DEFENDED` |
| L | mandatory | mandatory bundle evidence | remove subject STATE.json | validator refuses missing artifact | G4-X2 bundle refused | `DEFENDED` |
| M | mandatory | archive path safety | add a traversal member | validator refuses unsafe path | G4-X3 bundle refused | `DEFENDED` |
| N | mandatory | bundle secret scan | add a synthetic credential-shaped payload assembled in memory | validator refuses bundle | G4-X4 bundle refused | `DEFENDED` |
| O | mandatory | archive uniqueness | duplicate a member name | validator refuses duplicate | G4-X5 bundle refused | `DEFENDED` |
| P | mandatory | live adverse lifecycle | execute restart, cancellation, timeout and forged-origin scenarios | every fail-closed invariant survives | G4-X6 all four stages passed | `DEFENDED` |
| Q | mandatory | pre-persistence secret containment | inject a synthetic scanner-detected marker through record execution | redact or quarantine before durable commit | G4-X7 scanner detected it, but evidence persisted and resolved unchanged | `ESCAPED` |

Machine-readable observations, including the valid baseline control, are in
`GATE-4-INDEPENDENT-RED-TEAM.json`; the non-secret reproduction is in
`SECRET-EVIDENCE-PROBE.json`.
