# Decisions — SETUP-00-CP-0009

## 1. The stale scaffold in the working tree was replaced, not built on

The audit started with an uncommitted, unsealed `SETUP-00-CP-0009` directory from an earlier
interrupted attempt: a 98-row matrix with every row `NOT_STARTED`, no evidence, and a modified
`LATEST.md`. It was copied to the session scratchpad for the record, removed, and `LATEST.md`
restored, so the audit began from a clean worktree at the sealed subject commit. Building on a
scaffold whose provenance this session cannot verify would have made every later claim weaker.

## 2. The audit matrix was written before any substantive step, and grew transparently

183 rows now; 180 were written before execution with every row `NOT_STARTED`. Three were added
during execution and carry `addedDuringExecution` with the reason: `EXT-011` and `EXT-012`, because
auditing a control means executing its positive path and not only its refusals, and `TST-011`,
because the durability of the mandatory suite past the protocol's own next step is part of auditing
the delivery that seals it.

## 3. The attack harness is the auditor's own

`audit-harness/attacks.py` does not import `m0_red_team.py`. A `DEFENDED` verdict from the
delivery's own harness would be a statement about the harness. The delivery's harness was still run
once, as one of the subject's handoff validation commands, and its result corroborates rather than
substitutes.

## 4. Attribution before volume

Two revisions of the harness produced `DEFENDED` for the wrong reason: one broke the seal
chronology independently of the mutation, one left a moved tag in place across attacks. Both were
repaired in the harness, classified `AUDIT_ENVIRONMENT`, and recorded in `AUDIT-EXECUTIONS.md`. The
harness now carries a null-mutation control that validates, and the scenario harness carries an
accepted baseline, so a rejection can be attributed to the mutation under test.

## 5. No Gate preflight was generated for this checkpoint

`docs/ENGINEERING-MEMORY.md` places the preflight *before a Gate begins*. SETUP-00 began long ago
and its preflight is sealed in `SETUP-00-CP-0008`; this audit recomputed it and reproduced its
selection rather than regenerating one. Generating a preflight here would also have imported
derived requirements that cannot apply to an audit run — for example a readiness status with an
empty `blockedBy`, which an audit that records blockers cannot have. That gap is recorded as lesson
candidate `M0-CP9-CANDIDATE-007` instead of being papered over.

## 6. The requirements matrix of this checkpoint is the audit's verdict, not a delivery plan

It re-states all 71 canonical SETUP-00 rows with the status this audit reached for each, which is
the shape `SETUP-00-CP-0007` used for the same role. Two rows are `PARTIAL`, and each names the
finding that explains it.

## 7. The red gate was recorded, not removed

Anchoring the sealed predecessor — which `docs/CHECKPOINT-PROTOCOL.md` requires of every successor
— took the suite from 306/306 to 305/306. The cause is a product defect, `CP9-F-002`. An auditor
may not repair product code, and no test was edited, so `tests`, `unitTests`, `integrationTests` and
`GREEN_KEEPER_GATE` are recorded `FAIL` and this checkpoint is `REWORK_REQUIRED`.

## 8. No governance document was changed

The owner authorised a fresh Claude Code session to perform this audit. Before relying on that, the
canonical policy was checked: `docs/MILESTONE-VALIDATION.md` and
`scripts/development-ledger/attestation.py` require a different sealed *checkpoint*, not a different
vendor. The same-tool limitation is therefore recorded as a reduction in independence, not as a
policy exception, and nothing was edited to accommodate it. `crossToolValidation` is
`NOT_AVAILABLE`; it is never written as `PASSED`.

## 9. No attestation was written

`.iacode/attestations/` stays empty. An attestation is only meaningful for an approving audit, and
this audit does not approve. Writing one would also have been the very thing `CP9-F-001` says
cannot be consumed.
