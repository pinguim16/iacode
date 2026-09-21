# M0 Internal Mirror Audit

Result: `FAIL`

- Checkpoint: `SETUP-00-CP-0011`
- Generated: `2026-09-21T07:53:42Z`
- Target fingerprint: `5c8c35d1b88514591ff38b5b0283763b8431367588909253897caa216329f098`
- Auditor role: M0 Closure Auditor (.iacode/agents/m0-closure-auditor.md)

## Independence

Internal quality assurance. This mirror audit is authored by the implementing run, on the same tooling, in the same session. It is not independent external validation and may not be recorded as one; only a milestone attestation produced by a separate audit checkpoint can grant MILESTONE_EXTERNAL_PASS.

## Checks

| ID | Dimension | Expectation | Observed | Result |
|---|---|---|---|---|
| `MIR-001` | SETUP requirements | Every row of the canonical Gate specification is declared and COMPLETE. | 74/74 canonical rows COMPLETE | PASS |
| `MIR-002` | Audit findings | Every finding of the open audit is CLOSED. | 0/0 audit findings CLOSED | FAIL |
| `MIR-003` | Mandatory attacks | Every mandatory attack of the sealed Red Team report is defended. | the check itself failed: invalid JSON in E:\iacode\docs\checkpoints\SETUP-00-CP-0011\M0-INTERNAL-RED-TEAM.json: [Errno 2] No such file or directory: 'E:\\iacode\\docs\\checkpoints\\SETUP-00-CP-0011\\M0-INTERNAL-RED-TEAM.json' | FAIL |
| `MIR-004` | Engineering Memory | The memory validates. | LESSONS_VALID total=30 active=30 guarded=28 | PASS |
| `MIR-005` | Lessons | No lesson carries an unresolved guardrail failure. | 30 lessons, 28 GUARDED, 2 CONFIRMED, 0 with an unresolved guardrail failure | PASS |
| `MIR-006` | Guardrails | Every guardrail resolves, is verified by a test, and has no unresolved failure. | 29/29 effective, 29 resolved, 29 tested, 0 failures | PASS |
| `MIR-007` | Lesson preflight | The preflight is bound to the Gate and fresh against the current memory. | fresh; fingerprint recomputed and selection reproduced | PASS |
| `MIR-008` | Green Keeper | The last cycle is GREEN over the closed mandatory set and is not stale. | 2 cycle(s), last GREEN, measured against 5/5 mandatory gates, fresh | PASS |
| `MIR-009` | Delivery Completeness | Coverage and evidence coverage are total over the derived expected set. | 104/104 complete against an expected set of 104, coverage 100.00, evidence 100.00 | PASS |
| `MIR-010` | History integrity | The sealed checkpoint chain resolves. | 10 anchors verified | PASS |
| `MIR-011` | Tags | Every anchored tag resolves to its anchored commit. | 10 tags resolve to their anchored commits | PASS |
| `MIR-012` | Quality evidence | Every PASS carries evidence and nothing is red. | 8 PASS with evidence, 0 FAIL, 0 unevidenced, 0 unjustified | PASS |
| `MIR-013` | Command reproducibility | Every record that names an input binds it by content. | 18 records, 0 without an input digest, 3 recorded failures kept in the ledger | PASS |
| `MIR-014` | Derived counts | Every evidential count matches its derivation. | the check itself failed: invalid JSON in E:\iacode\docs\checkpoints\SETUP-00-CP-0011\COUNTS.json: [Errno 2] No such file or directory: 'E:\\iacode\\docs\\checkpoints\\SETUP-00-CP-0011\\COUNTS.json' | FAIL |
| `MIR-015` | Documentation | Every relative documentation link resolves. | 46/46 relative documentation links resolve | PASS |
| `MIR-016` | Historical compatibility | Every sealed checkpoint still validates under the tooling this Gate changes. | 10 sealed checkpoints validate under this tooling | PASS |
| `MIR-017` | Clean clone | The delivery validates in a fresh clone with no workspace state. | suite=ok, compileall=ok, lessons=ok, integrity=ok, completeness=ok | PASS |
| `MIR-018` | Scope and self-containment | No Gate 0 runtime exists and the delivery is reproducible from the repository. | no Gate 0 runtime present; specification in the repository=True; handoff executable without this session=True | PASS |
