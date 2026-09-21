# Lesson Candidate Assessment — the eight `SETUP-00-CP-0009` candidates

The audit produced eight `OBSERVED` candidates and promoted none of them, which is correct: promotion
belongs to the implementing run. Each candidate is assessed below, with the decision and the reason.
Six became lessons, one was merged into an existing lesson as a recurrence, and one was recorded as
not requiring a lesson.

| Candidate | Finding | Decision | Result |
|---|---|---|---|
| `M0-CP9-CANDIDATE-001` | `CP9-F-001` | NEW | `LSN-0024`, `GUARDED` by `GRD-0023` |
| `M0-CP9-CANDIDATE-002` | `CP9-F-002` | NEW | `LSN-0025`, `GUARDED` by `GRD-0024` |
| `M0-CP9-CANDIDATE-003` | audit harness | NEW | `LSN-0026`, `GUARDED` by `GRD-0025` |
| `M0-CP9-CANDIDATE-004` | `CP9-F-003` | RECURRENCE | `LSN-0022`, reopened and repaired, new `GRD-0026` |
| `M0-CP9-CANDIDATE-005` | `CP9-F-004` | NEW | `LSN-0027`, `GUARDED` by `GRD-0027` |
| `M0-CP9-CANDIDATE-006` | `CP9-F-005` | NEW | `LSN-0028`, `GUARDED` by `GRD-0028` |
| `M0-CP9-CANDIDATE-007` | audit observation | NEW, scoped | `LSN-0030`, `CONFIRMED`, scope `independent-audit` |
| `M0-CP9-CANDIDATE-008` | audit observation | NOT REGISTERED | documented gap; policy and implementation agree |

One further lesson was written that no candidate proposed: `LSN-0029`, because the systemic class of
`CP9-F-002` is wider than the literal identifier. Performing a transition the protocol *requires* of
every successor turned a mandatory gate red, and the general rule — a required protocol transition
must never do that — now has its own automated control.

## Candidate by candidate

### `M0-CP9-CANDIDATE-001` — a control is finished only when its positive path is executed

New systemic class. Nothing in the memory covered it: `LSN-0015` governs the shared promotion
invariant and `LSN-0019` the recomputation of derived artifacts, but neither says that a control
whose reachable state space is empty looks perfect from the refusing side. Registered as `LSN-0024`
at `CRITICAL`, guarded by `GRD-0023`: the positive promotion is executed by
`promotion_simulation.py` and asserted by `PositivePromotionTests`.

### `M0-CP9-CANDIDATE-002` — a guardrail test must derive what it excludes

New systemic class, distinct from `LSN-0021`, which guards the integrity chain itself rather than the
way a test selects what it excludes. Registered as `LSN-0025` at `CRITICAL`, guarded by `GRD-0024`:
one helper, `anchors.pending_anchor_exclusion`, answers the question for the CLI, the validator and
the suite.

### `M0-CP9-CANDIDATE-003` — an adversarial fixture needs a null-mutation control

New systemic class. The audit classified its own harness failure as `AUDIT_ENVIRONMENT` and repaired
it there, which is correct for an auditor, but the *class* belongs to every battery this project
runs. Registered as `LSN-0026` at `HIGH`, guarded by `GRD-0025`: the report schema requires a
`baselineControl`, validation refuses a report whose control is missing or not `VALID`, and
`m0_red_team.py` records the control it actually ran.

### `M0-CP9-CANDIDATE-004` — a derived-count control that inspects one file type

Recurrence, not a new lesson. `LSN-0022` already says that an authoritative count is derived once and
verified wherever it is stated, and it was `GUARDED` when `CP9-F-003` happened, so the repeat is a
`GUARDRAIL_FAILURE` rather than a new observation. `LSN-0022` therefore carries `recurrenceCount` 1,
severity escalated to `CRITICAL`, and a failure record resolved in `SETUP-00-CP-0010`; the control
now reaches comments and docstrings through `GRD-0026`, and the policy decision — a count in prose is
never evidence — is recorded in `docs/QUALITY-GATES.md`.

### `M0-CP9-CANDIDATE-005` — a lesson's prose must not contradict its status

New class, in the memory's own governance. Registered as `LSN-0027`, guarded by `GRD-0027`: memory
validation refuses a `GUARDED` lesson whose notes assert that it is not guarded. `LSN-0014` now
records the residual limit of its control instead of restating a status.

### `M0-CP9-CANDIDATE-006` — a configuration key that no code reads is a defect

New class. Registered as `LSN-0028`, guarded by `GRD-0028`: the memory policy schema is closed and
the policy document is validated like every other governing document, so a key without a consumer is
a validation error rather than a promise. The smaller architecture was chosen — the key is removed and
the registry path is documented as fixed — because nothing in the design needs it to move.

### `M0-CP9-CANDIDATE-007` — the preflight presumes an implementing delivery

Real, but it constrains audit runs only, and an implementing Gate should not be made to answer it.
Registered as `LSN-0030` at `LOW` with `status` `CONFIRMED` and applicability scoped to
`independent-audit`, so it selects itself when a run declares that scope and stays silent otherwise.
It is deliberately not `GUARDED`: no automated control exists yet, and documentation alone never
earns that status. The limitation is recorded in `docs/ENGINEERING-MEMORY.md`.

### `M0-CP9-CANDIDATE-008` — the secret detector's documented scope

Not registered, and the candidate says so itself: a bare cloud access key identifier is outside the
documented scope of the detector, the assignment form of the same value is covered, and
`.iacode/policies/secret-policy.md` states the boundary. Policy and implementation agree, which is
what checklist row 3.2 requires. Recording a lesson here would create a Gate requirement for a gap
that is disclosed rather than hidden. If the scope is widened later, the policy is widened in the
same change.

## Guardrail effectiveness after this assessment

Seven guardrails were added, `GRD-0023` to `GRD-0029`, each naming the lessons it guards, the tests
that fail when the control is removed, and what removing it would allow. No guardrail failure remains
unresolved: the single one recorded, against `LSN-0022`, names `SETUP-00-CP-0010` as the checkpoint
that repaired the control.
