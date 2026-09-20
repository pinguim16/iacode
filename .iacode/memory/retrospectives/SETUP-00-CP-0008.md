# Retrospective — SETUP-00 / SETUP-00-CP-0008

Scope: the corrective checkpoint that closes the first independent `M0` audit. Observations and
evidence only; no chain-of-thought and no secrets.

## What went well

- Deriving the requirement set instead of transcribing it changed the character of the work. The
  expected set is recomputed from the canonical checklist, the preflight and the sealed audit
  reports, so the question "did we cover everything?" stopped being a judgement and became a set
  comparison. `CLOSURE-REQUIREMENTS.json` and `REQUIREMENTS-MATRIX.json` are generated together and
  cannot disagree.
- Re-parsing the findings and attacks from the sealed `CP-0007` reports removed the most likely
  transcription error in a corrective run: quietly dropping a finding. `AuditSourceParsingTests`
  asserts that the battery implements exactly the mandatory attacks the sealed report lists.
- The version-dispatch pattern held again under real pressure. Five schema rule sets now coexist and
  every sealed checkpoint still validates, which matters more here than usual because the checkpoint
  repairing `LSN-0012` could easily have broken `LSN-0012`.
- Writing each test as the attack made the relationship between a finding and its control explicit.
  Every finding in `CP7-FINDINGS-CLOSURE.json` names the regression and the negative test that fail
  if the control is removed.

## What failed

Recorded in `REWORK-LOG.jsonl` and in this delivery's own history. The distinct causes:

- The first attack battery run aborted on a missing import, and the second was refused by its own
  fixture because the checkpoint was not yet internally consistent. Both were correct refusals: the
  fixture validates its baseline before attacking, so it will not attack a broken model.
- The delivery-gate fixtures in the suite could not satisfy the closed mandatory set, because they
  had no memory the validator could resolve, no ignore rules, and a Gate outside the published plan.
  The fixtures were made realistic; the control was not weakened. That is the same choice
  `SETUP-00-CP-0005` made for `DeliveryLifecycleTests`, and it was right again.
- The assurance scope fingerprint drifted across a commit because a file deleted from the working
  tree was still in the index. The fingerprint now describes the working tree, which is what the
  gates actually judged.
- A constant named `COUNT_TOKEN` was flagged by the repository secret scan. The detector was right
  about the shape and wrong about the meaning; the constant was renamed rather than the detector
  narrowed.

## What repeated

`LSN-0011`, the self-reference hazard, appeared four separate times in one delivery: a Green Keeper
gate that validates the checkpoint recording its own cycles, a completeness audit whose freshness
covers the matrix it reads, a seal that must validate the commit containing the validation, and an
attack battery that needs the artifacts it is about to produce. Each was resolved the same way: scope
the control to the moment it matters, and state the residual limit rather than hide it. The lesson
was `GUARDED` before this Gate and the guardrail held; no `GUARDRAIL_FAILURE` was recorded for it.

Six other lessons did record a `GUARDRAIL_FAILURE`, because the independent audit bypassed their
controls: `LSN-0005`, `LSN-0007`, `LSN-0008`, `LSN-0009`, `LSN-0010` and `LSN-0012`. Each was
reopened at escalated severity before it was repaired, and each returned to `GUARDED` only against a
registered guardrail whose verifying tests exist.

## What was learned

- A control that takes its scope, its denominator or its verdict from the thing it constrains is not
  a control. Seven of eleven findings were that one sentence in seven disguises. Looking for that
  shape is now the cheapest review any new control can get.
- An audit that spends itself finding basic gaps is an expensive way to learn something the delivery
  could have learned alone. Running the attack battery and the mirror audit before handoff is not
  duplicated effort; it changes what the external audit is for.
- Honesty about a trust model is a deliverable. The anchors and the attestation are tamper evidence,
  not cryptography, and saying so in the code, the documents and the reports is what keeps the next
  reader from trusting them further than they deserve.
- A count written by hand twice will eventually disagree with itself. Deriving it once and verifying
  it where it is quoted is less work than the corrections it prevents.

## What should become a guardrail

| Item | Control | Kind | Where | Removing it would allow |
|---|---|---|---|---|
| A positive status with no promotion rules | one shared invariant over `POSITIVE_TERMINAL_STATUSES` | invariant | `validate_checkpoint._validate_delivery_assurance` | A new status to start life unguarded. |
| A caller narrowing a mandatory set | the closed gate registry | policy | `.iacode/policies/quality-gates.json` | A vacuous green delivery. |
| A delivery choosing its own denominator | the derived expected set | invariant | `policies.expected_requirement_refs` | Total coverage over whatever was submitted. |
| A self-asserted external verdict | the external audit attestation | validator | `scripts/development-ledger/attestation.py` | A run certifying itself. |
| A stale derived artifact | input fingerprints recomputed at validation | invariant | `lessons.preflight_staleness` | A selection surviving the change that invalidated it. |
| A reference that is typed but not resolved | control and evidence resolution | invariant | `lessons.resolve_control` | A guardrail that names nothing. |
| Sealed history with no external expectation | the anchor chain | invariant | `anchors.verify_chain` | A coordinated tag and content move. |
| A hand-maintained authoritative count | derived counts, verified where stated | invariant | `validate_checkpoint._validate_derived_counts` | Two artifacts stating different facts. |
| Evidence from a dirty tree | input digests | invariant | `ledger_common.build_command_record` | A record naming a commit that never held what it read. |
| A seal whose evidence describes nothing | monotonic post-commit sealing | invariant | `validate_checkpoint._validate_seal_chronology` | Final evidence about an unsealed state. |
| A lesson citing the wrong source | provenance resolution | invariant | `lessons._resolve_source_locator` | Memory that cannot be checked against history. |

All eleven were implemented in this Gate, registered in `.iacode/memory/guardrails/registry.json`,
and are covered by tests that fail when the control is removed.

## New lessons

| Lesson | Status | Guarded by |
|---|---|---|
| `LSN-0015` | `GUARDED` | `GRD-0014`, the shared promotion invariant. |
| `LSN-0016` | `GUARDED` | `GRD-0015`, the closed mandatory gate set. |
| `LSN-0017` | `GUARDED` | `GRD-0016`, the derived expected requirement set. |
| `LSN-0018` | `GUARDED` | `GRD-0017`, resolution of every structured reference. |
| `LSN-0019` | `GUARDED` | `GRD-0018`, input fingerprints on derived artifacts. |
| `LSN-0020` | `GUARDED` | `GRD-0019`, content-bound inputs on every record. |
| `LSN-0021` | `GUARDED` | `GRD-0020`, the checkpoint integrity anchor chain. |
| `LSN-0022` | `GUARDED` | `GRD-0021`, derived counts verified where stated. |
| `LSN-0023` | `GUARDED` | `GRD-0022`, resolved lesson provenance. |

## Updated lessons

| Lesson | Change | Reason |
|---|---|---|
| `LSN-0005` | `GUARDRAIL_FAILURE`, severity escalated, repaired, re-guarded as `GRD-0007` | The evidence rule applied only to one status (`M0-F-001`). |
| `LSN-0007` | `GUARDRAIL_FAILURE`, severity escalated, repaired, re-guarded as `GRD-0008`; provenance corrected | An implementing run certified itself (`M0-F-002`), and the locator cited the wrong checkpoint (`M0-F-011`). |
| `LSN-0008` | `GUARDRAIL_FAILURE`, severity escalated, repaired, re-guarded as `GRD-0009` | The denominator was the delivery's to choose (`M0-F-006`). |
| `LSN-0009` | `GUARDRAIL_FAILURE`, severity escalated, repaired, re-guarded as `GRD-0010` | An empty gate list produced a PASS (`M0-F-005`). |
| `LSN-0010` | `GUARDRAIL_FAILURE`, severity escalated, repaired, re-guarded as `GRD-0011` | Records did not replay at their declared commits (`M0-F-009`). |
| `LSN-0012` | `GUARDRAIL_FAILURE`, severity escalated, repaired, re-guarded as `GRD-0012` | Sealed history could be moved without detection (`M0-F-007`). |
| `LSN-0003` | Provenance locator made precise | It cited a decomposition recorded in a later checkpoint than the one it named. |
| `LSN-0014` | Promoted from `CONFIRMED` to `GUARDED` as `GRD-0013` | Sealing chronology became observable, so the lesson became guardable (`M0-F-010`). |

## Retired lessons

| Lesson | Superseded by | Reason |
|---|---|---|
| _none_ | — | No lesson has stopped applying. `LSN-0013` remains `CONFIRMED` because no control in this repository can observe an arbitrary machine's installation state. |
