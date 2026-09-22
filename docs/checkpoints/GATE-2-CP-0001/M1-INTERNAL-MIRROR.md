# M1 Internal Mirror Audit

Result: `FAIL`

- Checkpoint: `GATE-2-CP-0001`
- Generated: `2026-09-22T17:36:21Z`
- Target fingerprint: `8ec46519093b0892309f0b7e7469fc4d1ed14895f8eb77b5b6d2dd465fd9bf89`
- Auditor role: M0 Closure Auditor (.iacode/agents/m0-closure-auditor.md)

## Independence

Internal quality assurance. This mirror audit is authored by the implementing run, on the same tooling, in the same session. It is not independent external validation and may not be recorded as one; only a milestone attestation produced by a separate audit checkpoint can grant MILESTONE_EXTERNAL_PASS.

## Checks

| ID | Dimension | Expectation | Observed | Result |
|---|---|---|---|---|
| `MIR-001` | Gate specification requirements | Every row of the canonical Gate specification is declared and COMPLETE. | 134/137 canonical rows COMPLETE; not complete 19.1, 19.2, 19.5 | FAIL |
| `MIR-002` | Audit findings | Every finding of every audit whose corrective delivery this is, is CLOSED. | 0 applicable audit findings derived from the audit registry | NOT_APPLICABLE |
| `MIR-003` | Mandatory attacks | Every mandatory attack of the sealed Red Team report is defended. | 0 applicable mandatory attacks derived from the audit registry | NOT_APPLICABLE |
| `MIR-004` | Engineering Memory | The memory validates. | LESSONS_VALID total=46 active=46 guarded=44 | PASS |
| `MIR-005` | Lessons | No lesson carries an unresolved guardrail failure. | 46 lessons, 44 GUARDED, 2 CONFIRMED, 0 with an unresolved guardrail failure | PASS |
| `MIR-006` | Guardrails | Every guardrail resolves, is verified by a test, and has no unresolved failure. | 48/48 effective, 48 resolved, 48 tested, 0 failures | PASS |
| `MIR-007` | Lesson preflight | The preflight is bound to the Gate and fresh against the current memory. | fresh; fingerprint recomputed and selection reproduced | PASS |
| `MIR-008` | Green Keeper | The last cycle is GREEN over the closed mandatory set and is not stale. | 3 cycle(s), last GREEN, measured against 11/11 mandatory gates, fresh | PASS |
| `MIR-009` | Delivery Completeness | Coverage and evidence coverage are total over the derived expected set. | 179/182 complete; 182 anchored against an expected set of 182 and 0 declared locally, coverage 98.35, evidence 100.00 | FAIL |
| `MIR-010` | History integrity | The sealed checkpoint chain resolves. | 15 anchors verified | PASS |
| `MIR-011` | Tags | Every anchored tag resolves to its anchored commit. | 15 tags resolve to their anchored commits | PASS |
| `MIR-012` | Quality evidence | Every PASS carries evidence and nothing is red. | 10 PASS with evidence, 1 FAIL, 0 unevidenced, 0 unjustified | FAIL |
| `MIR-013` | Command reproducibility | Every record that names an input binds it by content. | 55 records, 0 without an input digest, 11 recorded failures kept in the ledger | PASS |
| `MIR-014` | Derived counts | Every evidential count matches its derivation. | ATTACKS=22/22; GUARDRAILS=48/48; LESSONS=44/46; REQUIREMENTS=179/182; TESTS=1220/1220 | PASS |
| `MIR-015` | Documentation | Every relative documentation link resolves. | 129/129 relative documentation links resolve | PASS |
| `MIR-016` | Historical compatibility | Every sealed checkpoint still validates under the tooling this Gate changes. | 15 sealed checkpoints validate under this tooling | PASS |
| `MIR-017` | Clean clone | The delivery validates in a fresh clone with no workspace state. | not requested in this run; --clean-clone performs the full execution | PASS |
| `MIR-018` | Scope and self-containment | No capability reserved for a later Gate is implemented, and the delivery is reproducible from the repository. | 0 later-Gate reservation(s) implemented early; specification docs/GATE-2-CHECKLIST.md in the repository=True; handoff executable without this session=True | PASS |

## Inapplicable dimensions

A dimension whose canonically derived set of items to audit is empty is recorded here with the reason and the source the emptiness was derived from. An empty applicable set is not a missing required set: the second is a failure and is reported as one.

| ID | Expected items | Reason | Derived from |
|---|---|---|---|
| `MIR-002` | 0 | No audit finding is applicable to this checkpoint: no registered audit names it as its corrective delivery, so there is no finding to close. | .iacode/policies/audit-registry.json matched on gate='GATE-2' and correctiveCheckpoint='GATE-2-CP-0001', with every finding and mandatory attack re-parsed from the sealed reports the matching entries name |
| `MIR-003` | 0 | No mandatory attack battery is applicable to this checkpoint: no registered audit names it as its corrective delivery, so no sealed Red Team report hands it a battery to re-defend. | .iacode/policies/audit-registry.json matched on gate='GATE-2' and correctiveCheckpoint='GATE-2-CP-0001', with every finding and mandatory attack re-parsed from the sealed reports the matching entries name |
