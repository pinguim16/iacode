# M2 Internal Mirror Audit

Result: `PASS`

- Checkpoint: `GATE-4-CP-0007`
- Generated: `2026-10-12T09:49:23Z`
- Target fingerprint: `f57b19b2a9b07040052671fecb842cf93b3ed680c0fcb1f14d3c889104b3a5b3`
- Auditor role: M0 Closure Auditor (.iacode/agents/m0-closure-auditor.md)

## Independence

Internal quality assurance. This mirror audit is authored by the implementing run, on the same tooling, in the same session. It is not independent external validation and may not be recorded as one; only a milestone attestation produced by a separate audit checkpoint can grant MILESTONE_EXTERNAL_PASS.

## Checks

| ID | Dimension | Expectation | Observed | Result |
|---|---|---|---|---|
| `MIR-001` | Gate specification requirements | Every row of the canonical Gate specification is declared and COMPLETE. | 105/105 canonical rows COMPLETE | PASS |
| `MIR-002` | Audit findings | Every finding of every audit whose corrective delivery this is, is CLOSED. | 1/1 audit findings CLOSED | PASS |
| `MIR-003` | Mandatory attacks | Every mandatory attack of the sealed Red Team report is defended. | 0 applicable mandatory attacks derived from the audit registry | NOT_APPLICABLE |
| `MIR-004` | Engineering Memory | The memory validates. | LESSONS_VALID total=96 active=96 guarded=93 | PASS |
| `MIR-005` | Lessons | No lesson carries an unresolved guardrail failure. | 96 lessons, 93 GUARDED, 3 CONFIRMED, 0 with an unresolved guardrail failure | PASS |
| `MIR-006` | Guardrails | Every guardrail resolves, is verified by a test, and has no unresolved failure. | 97/97 effective, 97 resolved, 97 tested, 0 failures | PASS |
| `MIR-007` | Lesson preflight | The preflight is bound to the Gate and fresh against the current memory. | fresh; fingerprint recomputed and selection reproduced | PASS |
| `MIR-008` | Green Keeper | The last cycle is GREEN over the closed mandatory set and is not stale. | 3 cycle(s), last GREEN, measured against 13/13 mandatory gates, fresh | PASS |
| `MIR-009` | Delivery Completeness | Coverage and evidence coverage are total over the derived expected set. | 201/201 complete; 201 anchored against an expected set of 201 and 0 declared locally, coverage 100.00, evidence 100.00 | PASS |
| `MIR-010` | History integrity | The sealed checkpoint chain resolves. | 29 anchors verified | PASS |
| `MIR-011` | Tags | Every anchored tag resolves to its anchored commit. | 29 tags resolve to their anchored commits | PASS |
| `MIR-012` | Quality evidence | Every PASS carries evidence and nothing is red. | 12 PASS with evidence, 0 FAIL, 0 unevidenced, 0 unjustified | PASS |
| `MIR-013` | Command reproducibility | Every record that names an input binds it by content. | 53 records, 0 without an input digest, 8 recorded failures kept in the ledger | PASS |
| `MIR-014` | Derived counts | Every evidential count matches its derivation. | ATTACKS=20/20; FINDINGS=1/1; GUARDRAILS=97/97; LESSONS=93/96; REQUIREMENTS=201/201; TESTS=1709/1709 | PASS |
| `MIR-015` | Documentation | Every relative documentation link resolves. | 204/204 relative documentation links resolve | PASS |
| `MIR-016` | Historical compatibility | Every sealed checkpoint still validates under the tooling this Gate changes, from a clone that carries only the published history. | 29 sealed checkpoints validate under this tooling | PASS |
| `MIR-017` | Clean clone | The delivery validates in a fresh clone with no workspace state. | suite=ok, compileall=ok, lessons=ok, integrity=ok, completeness=ok | PASS |
| `MIR-018` | Scope and self-containment | No capability reserved for a later Gate is implemented, and the delivery is reproducible from the repository. | 0 later-Gate reservation(s) implemented early; specification docs/GATE-4-CHECKLIST.md in the repository=True; handoff executable without this session=True | PASS |

## Inapplicable dimensions

A dimension whose canonically derived set of items to audit is empty is recorded here with the reason and the source the emptiness was derived from. An empty applicable set is not a missing required set: the second is a failure and is reported as one.

| ID | Expected items | Reason | Derived from |
|---|---|---|---|
| `MIR-003` | 0 | No mandatory attack battery is applicable to this checkpoint: no registered audit names it as its corrective delivery, so no sealed Red Team report hands it a battery to re-defend. | .iacode/policies/audit-registry.json matched on gate='GATE-4' and correctiveCheckpoint='GATE-4-CP-0007', with every finding and mandatory attack re-parsed from the sealed reports the matching entries name |
