# Final report

## Status

`REWORK_REQUIRED`. Independent Red Team: `RED_TEAM_FAIL` (19/20).

## Environment

Windows 11, Docker Compose, remote published clone, and detached canonical subject tag.

## Tool / Model / Effort

Codex desktop application, OpenAI, GPT-5, fresh session; effort not exposed.

## Deliverables

Audit matrix, precise finding, review, full verification report, subject inventory/count/mirror audits, G4-X7 probe, transport attacks, deterministic bundle audit, Red Team, completeness, internal closure mirror, and failed attestation.

## Files Created

Independent audit checkpoint evidence and `.iacode/attestations/G4-CP-0008.json`.

## Files Modified

Only the checkpoint pointer and predecessor anchor; no product path changed.

## Validation

The published full verifier passed all 42 stages once with no retry. Architecture passed 12/12, functional acceptance passed 12/12, and counts independently matched 201/201 requirements, 1709/1709 tests, 97/97 guardrails, and 13/13 subject Green Keeper gates.

## Tests

The subject's product and policy suites are green. The blocking failure is review-transport reconstruction, not product execution.

## Red Team

`RED_TEAM_FAIL`: attacks A-S were defended, but T escaped because two valid detached rebuilds did not reproduce CP0007's declared digest or size.

## Known Risks

Promotion could rely on a valid but stale archive that does not represent final sealed content.

## Remaining Work

Correct `G4-F-004` in a new implementing checkpoint and repeat the complete delivery and independent audit sequence.

## Handoff Readiness

Ready to publish the blocking audit verdict and evidence; not ready for Gate 4 approval.

## Next Gate

Gate 5 is not authorized and must not start.

## Evidence

See `FINDINGS.json`, `FINAL-GATE-4-AUDIT-MATRIX.json`, `SUBJECT-BUNDLE-AUDIT.json`, `GATE-4-INDEPENDENT-RED-TEAM.json`, `VERIFICATION-REPORT.json`, and `REVIEW-REPORT.md`.
