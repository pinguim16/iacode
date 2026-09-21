# Successor Durability

Result: `PASS`

- Simulation: successor anchor durability
- Closes: `CP9-F-002`
- Generated: `2026-09-21T12:39:44Z`
- Checkpoints sealed: `SETUP-00-CP-0001`, `SETUP-00-CP-0002`, `SETUP-00-CP-0003`

Each state below was produced by sealing a real checkpoint in a disposable repository and
re-running the integrity controls; the exclusion is derived at every state, so advancing
the chain never requires a source change.

| Check | State | Expectation | Observed | Result |
|---|---|---|---|---|
| `SUC-001` | SETUP-00-CP-0001 sealed, its anchor still owed | the chain verifies with a derived exclusion at this state | sealed SETUP-00-CP-0001; anchored none; pending anchor SETUP-00-CP-0001; no divergence | `PASS` |
| `SUC-001I` | SETUP-00-CP-0001 sealed, its anchor still owed | verify_integrity.py exits zero at this state | exit=0 INTEGRITY_VALID anchors=0 latest=none | `PASS` |
| `SUC-002` | SETUP-00-CP-0002 sealed, anchoring SETUP-00-CP-0001 | the chain verifies with a derived exclusion at this state | sealed SETUP-00-CP-0001, SETUP-00-CP-0002; anchored SETUP-00-CP-0001; pending anchor SETUP-00-CP-0002; no divergence | `PASS` |
| `SUC-002I` | SETUP-00-CP-0002 sealed, anchoring SETUP-00-CP-0001 | verify_integrity.py exits zero at this state | exit=0 INTEGRITY_VALID anchors=1 latest=SETUP-00-CP-0001 | `PASS` |
| `SUC-003` | SETUP-00-CP-0003 sealed, anchoring SETUP-00-CP-0002 | the chain verifies with a derived exclusion at this state | sealed SETUP-00-CP-0001, SETUP-00-CP-0002, SETUP-00-CP-0003; anchored SETUP-00-CP-0001, SETUP-00-CP-0002; pending anchor SETUP-00-CP-0003; no divergence | `PASS` |
| `SUC-003I` | SETUP-00-CP-0003 sealed, anchoring SETUP-00-CP-0002 | verify_integrity.py exits zero at this state | exit=0 INTEGRITY_VALID anchors=2 latest=SETUP-00-CP-0002 | `PASS` |
| `SUC-DETECT` | mutation | removing the anchor of a checkpoint the rule does not forgive is detected | removed SETUP-00-CP-0002: sealed checkpoint SETUP-00-CP-0002 has no integrity anchor | `PASS` |
| `SUC-RESTORE` | restored | the chain verifies again once the anchor is restored | no divergence | `PASS` |

Passed: `8` of `8` checks.
