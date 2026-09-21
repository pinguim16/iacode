# Retrospective — SETUP-00 / SETUP-00-CP-0010

Scope: the corrective checkpoint that closes the fresh-session `M0` audit sealed as
`SETUP-00-CP-0009`. Observations and evidence only; no chain-of-thought and no secrets.

## What went well

- The audit's acceptance criteria were written per finding, with a reproduction and a regression
  scenario each, so the corrective work started from an executable specification rather than from
  interpretation. `docs/checkpoints/SETUP-00-CP-0009/REVIEW-REPORT.md` is the artifact.
- Registering the audit in `.iacode/policies/audit-registry.json` turned its five findings and its
  twenty-six mandatory attacks into requirements automatically. Nothing was transcribed, and the
  matrix could not be smaller than the audit demanded.
- Building the positive paths as *executable simulations* rather than as arguments found real
  defects immediately: the first run of `successor_durability.py` failed on a missing anchor count,
  and the first `promotion_simulation.py` run failed on a memory the fixture had inherited rather
  than described. Both were fixture defects, and both would have been invisible in prose.
- Deriving the requirement set again after every policy change kept the matrix equal to the expected
  set through three checklist rows and seven new lessons.

## What failed

- The mandatory `tests` gate was red at baseline, exactly as the audit recorded: anchoring the
  sealed predecessor made `IntegrityAnchorTests` fail on a hardcoded exclusion. It was repaired by
  deriving the rule, never by editing the assertion.
- The closure test fixture copied a sealed checkpoint's preflight and requirement matrix, so adding
  a lesson or a checklist row made the fixture fail for its own reasons. Four classes went red at
  once; the fixture now re-derives both from current policy.
- The old `ExternalAttestationTests` class described a model that no longer exists. Its cases were
  replaced by the state-level cases it still owns plus `AuditAttestationModelTests`, which exercises
  the attestation against the repository's own sealed history.
- Two internal fixtures wrote artifacts that the new controls refuse — a memory policy declaring the
  removed key, and a modelled Red Team report with no null-mutation control. Both are fixture
  repairs, recorded here rather than hidden.

## What repeated

- `LSN-0022`, the count that is maintained in a second place, repeated as `CP9-F-003` while the
  lesson was `GUARDED`. It is recorded as a `GUARDRAIL_FAILURE`, escalated to `CRITICAL`, and
  resolved by this checkpoint, which extended the control to comments and docstrings.
- No other finding of this audit matched an existing `recurrenceKey`. `CP9-F-001` and `CP9-F-002`
  are new classes and became `LSN-0024` and `LSN-0025`.

## What was learned

- A control is not finished when its refusals pass. If no test reaches the state the control guards,
  the reachable state space can be empty and every rejection test will still be green.
- A guardrail that names a historical artifact decides today's behaviour from yesterday's
  repository. The rule must be derived from repository state, and derived once, in one place.
- A required protocol transition must never turn a mandatory gate red. If it does, the delivery that
  introduced the control owes the repair, not the delivery that performs the transition.
- An adversarial battery without a null-mutation control cannot distinguish a working defence from a
  broken fixture.
- A configuration key that nothing reads is a promise the implementation does not keep, and a
  document that nothing validates will eventually declare one.

## What should become a guardrail

| Item | Kind | Lives in | What breaks if removed |
|---|---|---|---|
| The positive promotion path is executed | automated-check | `promotion_simulation.py` | A status-gating control could again be unreachable while every forgery is refused. |
| The pending-anchor exclusion is derived | invariant | `anchors.pending_anchor_exclusion` | A guardrail could again depend on the checkpoint name that was newest when it was written. |
| A battery records its null-mutation control | invariant | `validate_checkpoint._validate_internal_assurance` | A battery whose refusals come from a broken fixture would read as defended. |
| No count in a comment or docstring | test | `SourceCardinalityPolicyTests` | A cardinality maintained by hand could again contradict the derivation. |
| A GUARDED lesson may not call itself unguarded | invariant | `lessons.validate_lessons` | The prose and the machine-readable status could diverge again. |
| The memory policy declares only what is read | schema | `.iacode/schemas/memory-policy.schema.json` | A dead configuration key could be declared again. |
| The protocol's next steps are executed | automated-check | `successor_durability.py` | A required transition could turn a mandatory gate red in the next delivery. |

## New lessons

| Lesson | Status | Guarded by |
|---|---|---|
| `LSN-0024` | `GUARDED` | `GRD-0023` |
| `LSN-0025` | `GUARDED` | `GRD-0024` |
| `LSN-0026` | `GUARDED` | `GRD-0025` |
| `LSN-0027` | `GUARDED` | `GRD-0027` |
| `LSN-0028` | `GUARDED` | `GRD-0028` |
| `LSN-0029` | `GUARDED` | `GRD-0029` |
| `LSN-0030` | `CONFIRMED` | _none; scoped to audit runs, and documentation alone is not a guardrail_ |

## Updated lessons

| Lesson | Change | Reason |
|---|---|---|
| `LSN-0022` | recurrence recorded, severity escalated to `CRITICAL`, `GRD-0026` added, failure resolved in `SETUP-00-CP-0010` | `CP9-F-003` repeated the class while the lesson was `GUARDED`. |
| `LSN-0014` | notes rewritten as the residual limit of the control | `CP9-F-004`: the note contradicted the status. |

## Retired lessons

| Lesson | Superseded by | Reason |
|---|---|---|
| _none_ | — | No lesson stopped applying during this delivery. |
