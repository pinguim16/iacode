# CP-0011 Findings Closure

Result: `CLOSED`

- Audit: `M0-CP-0011`, the fresh-session independent M0 audit of `SETUP-00-CP-0010`
- Source: `docs/checkpoints/SETUP-00-CP-0011/REVIEW-REPORT.md`
- Corrective delivery: `SETUP-00-CP-0012`

The finding set is not transcribed. `policies.audit_findings` re-parses it from the sealed
review report at every validation, so this record cannot close a finding the report does not
raise, and it cannot omit one the report does.

| Finding | Severity | Status |
|---|---|---|
| `CP11-F-001` | CRITICAL | `CLOSED` |

## `CP11-F-001` — CRITICAL — the internal mirror audit cannot pass for a delivery that corrects no audit, and checkpoint validation requires it to pass

### What the audit expected

A checkpoint that carries out the protocol's own next step reaches a handoff-ready status with the shipped tooling: the audit checkpoint closes at MILESTONE_INDEPENDENT_AUDIT_PASS, and the delivery that follows it reaches READY_FOR_REVIEW.

### What it observed

m0_mirror_audit.py derived two of its eighteen checks from the audits whose corrective delivery the checkpoint is. MIR-002 returned 'closed == total and total > 0' and MIR-003 returned '... and bool(expected)', so both reported FAIL rather than NOT_APPLICABLE when there was nothing to audit. The report was then FAIL and validate_checkpoint._validate_internal_assurance refused every positive terminal status. Two states were executed rather than predicted: the CP-0011 audit checkpoint itself, and a GATE-0 checkpoint created in a disposable clone.

### Root cause

The checks conflated two states of a derived set. Zero items derived because nothing of this kind applies was treated as zero items derived because the delivery failed to supply them. An empty applicable set is legitimate; a missing required set is a failure. The role contract already prescribed NOT_APPLICABLE and the report schema already permitted it, but no check ever emitted one, so the reachable state space of a passing mirror excluded every delivery that corrects no audit. The defect survived because promotion_simulation.py wrote the mirror artifact by hand instead of running the tool, so the rehearsal of the positive path never exercised the control it rehearsed.

### Implementation

- scripts/development-ledger/m0_mirror_audit.py: a NotApplicable outcome that cannot be constructed without a reason and a derivation source; Mirror.record refuses an unjustified or non-empty NOT_APPLICABLE by recording it as FAIL; MIR-002 and MIR-003 derive their applicable set first and report NOT_APPLICABLE only when it is empty; the report is schemaVersion 1.1.0 and carries the justification of every inapplicable dimension.
- scripts/development-ledger/policies.py: audit_applicability derives the applicable findings and mandatory attacks from the audit registry and the sealed reports at every call, and raises when a named report cannot be parsed instead of reducing to an empty set; parse_findings is bounded to the report's own Findings section and parse_attacks reads a table by its header, so all three sealed renderings parse and none of the earlier parses moves.
- scripts/development-ledger/validate_checkpoint.py: the counts of the mirror report must add up, an inapplicable dimension must carry a reason, an expected count of zero and a derivation source, report version 1.0.0 may not carry one at all, and _validate_mirror_applicability re-derives the registry-bound dimensions so a delivery cannot declare away work the canonical sources still name.
- scripts/development-ledger/promotion_fixture.py: the fixture executes m0_mirror_audit.py instead of writing its artifact, records the command and the exit code, and exposes run_gate_transition and run_mirror_scenario.
- scripts/development-ledger/mirror_semantics_validation.py and gate_transition_simulation.py: new entry points that execute the tool in every applicability state and across the transition into the first delivery of the next Gate.
- .iacode/schemas/mirror-audit.schema.json: report version 1.1.0 adds reason, expectedCount and derivationSource; sealed 1.0.0 reports keep the rules they were written for.
- .iacode/agents/m0-closure-auditor.md, docs/QUALITY-GATES.md, docs/DEVELOPMENT-CONTRACT.md, docs/DEFINITION-OF-DONE.md and docs/SETUP-00-CHECKLIST.md row 7d.16: the distinction and the rule that a simulation executes the control it reports.

### Positive regression

- `MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`
- `MirrorApplicabilitySemanticsTests.test_a_satisfied_applicable_set_passes`
- `GateTransitionSimulationTests.test_the_first_checkpoint_of_the_next_gate_reaches_review_readiness`
- `GateTransitionSimulationTests.test_its_mirror_audit_passes_with_the_empty_dimensions_inapplicable`
- `SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`

### Negative regression

- `MirrorApplicabilitySemanticsTests.test_an_open_finding_fails`
- `MirrorApplicabilitySemanticsTests.test_a_missing_required_set_fails_rather_than_being_inapplicable`
- `MirrorApplicabilitySemanticsTests.test_a_delivery_cannot_declare_its_own_applicable_set_empty`
- `MirrorApplicabilitySemanticsTests.test_an_unexecuted_mandatory_attack_fails`
- `MirrorApplicabilityValidationTests.test_an_inapplicable_dimension_without_a_reason_is_refused`
- `MirrorApplicabilityValidationTests.test_an_inapplicable_dimension_with_items_is_refused`
- `MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`
- `MirrorApplicabilityValidationTests.test_an_inapplicable_dimension_under_the_older_report_version_is_refused`
- `MirrorApplicabilityValidationTests.test_an_inapplicable_dimension_counted_as_a_pass_is_refused`
- `NotApplicableRecordingTests.test_an_unjustified_inapplicable_record_becomes_a_failure`
- `NotApplicableRecordingTests.test_an_inapplicable_record_with_items_becomes_a_failure`

### Reproduction of the original defect and of the repair

The audit reproduced the defect with `python scripts/development-ledger/m0_mirror_audit.py --checkpoint docs/checkpoints/SETUP-00-CP-0011`, which reported `MIR-002 FAIL: 0/0 audit findings CLOSED`. The same command against the same sealed checkpoint now reports `MIR-002 NOT_APPLICABLE` with its reason and the report no longer fails for having nothing to audit. The second state the audit executed, a `GATE-0` checkpoint created in a disposable clone, is now executed end to end by `python scripts/development-ledger/gate_transition_simulation.py`, which reaches `READY_FOR_REVIEW` with `CHECKPOINT_VALID`.

### Verification

- `python scripts/development-ledger/mirror_semantics_validation.py`
- `python scripts/development-ledger/gate_transition_simulation.py`
- `python scripts/development-ledger/promotion_simulation.py`

### Evidence

- `checkpoint:MIRROR-SEMANTICS-VALIDATION.json`
- `checkpoint:GATE0-TRANSITION-SIMULATION.json`
- `checkpoint:M0-INTERNAL-MIRROR.json`
- `checkpoint:POSITIVE-PROMOTION-VALIDATION.json`
- `file:scripts/development-ledger/m0_mirror_audit.py`
- `file:scripts/development-ledger/mirror_semantics_validation.py`
- `file:scripts/development-ledger/gate_transition_simulation.py`

### Memory

- Lesson: `LSN-0031`
- Guardrail: `GRD-0030`
- `LSN-0024` and `LSN-0029` each carry a `GUARDRAIL_FAILURE` for this recurrence, resolved in this checkpoint by `GRD-0031` and `GRD-0032`.
