# Guardrails

How a lesson became an automated control, and what breaks if the control is removed.

A guardrail entry exists for every `GUARDED` lesson. Removing a control listed here must fail a test,
so a guardrail cannot be quietly deleted.

| Lesson | Control | Removing it would allow |
|---|---|---|
| `LSN-0001` | `DetachedHeadValidationTests`, git binding in `validate_checkpoint.py` | The documented tag-checkout validation procedure to fail again. |
| `LSN-0002` | `DeltaInventoryTests`, `_validate_delta_inventory` | An undeclared or silently altered file to ship inside a valid checkpoint. |
| `LSN-0003` | `FinalizationAttemptRecordingTests`, `_record_attempt` on every path | A refused operation to disappear from the ledger. |
| `LSN-0004` | `StatusBlockerInvariantTests`, `ResealedBlockerFixtureTests`, `_validate_status_blockers` | A checkpoint to claim readiness and blockage at once. |
| `LSN-0005` | `QualityEvidenceTests`, `_validate_quality_evidence` | A PASS with no execution behind it. |
| `LSN-0006` | `SetupChecklistTests` | A Gate to be accepted against a specification that is not in the repository. |
| `LSN-0007` | `SecondToolValidationTests`, `DeliveryAssuranceGateTests` | An implementing run to certify itself. |
| `LSN-0008` | `DeliveryCompletenessMatrixTests`, `check_completeness.py` | A delivery to ship with an unimplemented requirement. |
| `LSN-0009` | `GreenKeeperToolTests`, `green_keeper.py` | A red gate to be handed to the auditor. |
| `LSN-0010` | `CommandReproducibilityTests`, `record_command.py` | A ledger that cannot be replayed. |
| `LSN-0011` | `DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress` | A control that its own run makes unsatisfiable. |
| `LSN-0012` | `HistoricalCheckpointCompatibilityTests` | A new rule to invalidate sealed history. |

`LSN-0013` and `LSN-0014` are `CONFIRMED` and deliberately not guarded: neither can be observed from
this repository alone. They are carried by the mandatory preflight instead, which is why the preflight
is not optional.
