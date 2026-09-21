# Decisions

## D1 — The verdict is recorded in this checkpoint, about a sealed subject

`SETUP-00-CP-0010` is audited at its canonical tag and is not modified, re-tagged or re-sealed.
This checkpoint anchors it, carries the attestation about it, and holds the milestone status. That is
the architecture `CP9-F-001` produced, and following it is also how this audit tests it.

## D2 — Independence is recorded at its real strength

The mechanism is `FRESH_SESSION_INDEPENDENT_AUDIT`. The tool, the provider and the model are the
same as the implementing run, and only the session is independent. `crossToolValidation` is
`NOT_AVAILABLE` in the attestation and nothing here is described as cross-tool validation. Had this
audit approved, the status it could record would be `MILESTONE_INDEPENDENT_AUDIT_PASS` and never
`MILESTONE_EXTERNAL_PASS`, which is refused for this mechanism; this audit confirmed that refusal by
execution rather than by reading.

## D3 — The matrix is derived and rebuilt, never edited

Rows that describe repository content come from the repository; rows that describe audit obligations
come from the audit mandate. Results arrive as append-only records and the published matrix is
rebuilt from them, so no row can change without leaving a record.

A correction belongs here: the first generation of the matrix read the closure record with the wrong
field names and therefore derived no row for the regression tests it names. The harness was corrected
and the matrix regenerated with those rows present, every one of them still `NOT_STARTED` at that
moment and executed afterwards. The alternative — leaving the rows out — would have shrunk the
denominator, which is the failure class this project already guards against.

## D4 — Evidence is re-derived rather than trusted

The expected requirement set was re-derived by a parser that never imports `policies.py`. Every
declared evidence reference was resolved by a resolver written for this audit. Every anchor was
recomputed from Git without `anchors.py`. The prose-count control of `CP9-F-003` was re-implemented
and checked against a planted offender. Agreement therefore means two independent derivations agreed.

## D5 — Re-running the Green Keeper against sealed content is not the way to verify it

`green_keeper.py` executed against `SETUP-00-CP-0010` in a disposable clone appends to that
checkpoint's ledger, which makes the worktree dirty and places a command after the recorded end of a
sealed run. Its first four mandatory gates went green and the fifth failed on exactly those two
conditions. That is a property of re-running a finished delivery, not a defect in the subject, so it
is classified `AUDIT_ENVIRONMENT` and the recorded verdict is verified the correct way instead: the
five canonical mandatory gate commands were re-executed individually in a clean clone, all exiting
zero, and the recorded cycle was checked against the canonical gate policy and against a
recomputation of the scope fingerprint.

## D6 — The adversarial battery of this audit is its own

It attacks disposable copies of a pristine snapshot, one copy per scenario, so no refusal can be
inherited from a previous scenario. The null-mutation control runs first and the battery reports
`INVALID` rather than a row of defences if the unmutated snapshot is refused. That rule exists
because the first harness of the previous audit reported every attack as defended while the refusals
came from leftover state.

## D7 — A report cannot contain its own result

The adversarial battery runs against a snapshot of this checkpoint as it stands before the battery
report exists, and the report is added afterwards. The same residual limit is already recorded in the
checkpoint protocol about sealing: a commit cannot contain a validation of itself. Nothing inside the
delivery-assurance scope changes between the snapshot and the seal; only this checkpoint's own
evidence does, and checkpoint evidence is deliberately outside that scope.

## D8 — Observations are recorded, not promoted into findings

Five properties were examined and judged not to be defects: the one-case difference in the passing
count between environments, a loose narrative sentence about adversarial categories, three refusal
branches with no test, the documented scope of the prose-count control, and the structural rather
than cryptographic trust model. Each is recorded in `AUDIT-EXECUTIONS.json` with what would make it a
finding. Promoting any of them would have inflated the audit; hiding them would have hidden what it
looked at.

## D9 — The finding blocks the milestone rather than being worked around

`CP11-F-001` could have been stepped over: the checkpoint validator accepts any schema-valid mirror
report that passes, so this audit could have authored one from its own executed checks and closed at
the milestone status. That was refused. The defect would have survived into the next delivery, which
cannot reach `READY_FOR_REVIEW` either, and the way the defect escaped in the first place was
precisely a rehearsal that wrote the artifact instead of producing it. An audit that works around a
blocked control is an audit that hides it.

## D10 — The attestation is kept and records the real verdict

A rejected audit could simply write no attestation, which is what `SETUP-00-CP-0009` did. This one
keeps it, with `reviewResult: REWORK_REQUIRED`, because the artifact records an audit that really
happened and because the derivation then demonstrates the mechanism in the direction that matters:
`milestone_status.py` reads it, re-verifies it, and refuses to promote on it. `STATE.json` records
`externalAttestation.status` as `PRESENT` rather than `VERIFIED`, which is the honest value.

## D11 — Gate 0 is not started and is not authorized

No Gate 0 artifact exists in this change set. `M0` did not pass, so `GATE 0 — FOUNDATION` stays
`BLOCKED`.
