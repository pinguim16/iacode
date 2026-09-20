# Incidents

A narrative record of an individual failure that needs more than a lesson row: what happened, what
was observed, what was tried, and what finally explained it.

An incident is written when the failure was expensive, surprising, or hard to reproduce. Routine red
gates belong in the delivery's `REWORK-LOG.jsonl`, not here.

No private chain-of-thought and no secrets. Record observations, actions, and evidence.

## INC-0001 — Two blocking findings escaped internal checks and were found by the external auditor

`SETUP-00-CP-0004` returned `REWORK_REQUIRED` and `RED_TEAM_FAIL`. The implementing run had produced
a green suite and a valid checkpoint, yet an early finalization refusal left no ledger record and a
resealed checkpoint could claim readiness while declaring a blocker.

What made it expensive: both defects were in controls the documents described as already working, so
no one thought to test them. The green suite was necessary and not sufficient.

What changed: the delivery-assurance gates in `SETUP-00-CP-0005`, and this memory, so that the class
of "documented but unenforced" is checked before an external auditor has to find it.

Evidence: `docs/checkpoints/SETUP-00-CP-0004/REVIEW-REPORT.md`,
`docs/checkpoints/SETUP-00-CP-0004/RED-TEAM-REPORT.md`,
`docs/checkpoints/SETUP-00-CP-0005/FINAL-REPORT.md`.
