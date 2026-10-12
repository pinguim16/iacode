# Plan

1. Register sealed audit `G4-CP-0008`, record `LSN-0097`, run the mandatory lesson preflight and
   derive the complete 222-requirement denominator before implementation.
2. Define the structural contract in ADR-0035: schema 3.4 checkpoints declare a review archive over
   an immutable Git content commit; the digest declaration is a seal-evidence sidecar and is
   excluded from its own payload to break self-reference explicitly.
3. Make `review_bundle.py` collect only Git-object bytes from the declared subject, remove live
   remote/working-tree inputs, and expose a strict declared-versus-rebuilt verifier.
4. Integrate two non-local Git-transport reconstructions into `seal_checkpoint.py`; require equal
   bytes, digest, size, manifest validation and secret cleanliness before the evidence commit/tag.
5. Make `validate_checkpoint.py` independently rebuild schema 3.4 declarations and refuse stale,
   mutable, missing or mismatched subjects, while retaining historical schema behavior.
6. Add focused producer, validator, seal-flow and attack-T regressions. Promote LSN-0097 to
   `GUARDED` only after the automated guardrail executes.
7. Execute focused tests, the complete 42-stage verifier, all 13 Green Keeper gates, completeness,
   internal Red Team A–T and the 18-dimension milestone mirror. Preserve every red attempt.
8. Finalize only `READY_FOR_REVIEW`, create the immutable content and seal-evidence commits, publish
   `main` and the CP0009 tag, then rebuild twice from a fresh remote clone and require exact agreement
   with the sealed declaration. Do not start Gate 5 or claim independent validation.

## Rework amendment

The first published-subject verifier passed 40/42. Preserve it. Repair the confirmed cancellation
signal/activity-handle race, promote its lesson only after the rebuilt evaluator suite passes, publish
an immutable CP0009 implementation subject, and execute the whole 42-stage verifier again. The new
run must defend attack T with the schema 3.4 producer and pass `quality-cancellation`; neither failed
stage may be replaced by an isolated rerun.

The second published-subject verifier passed the cancellation repair and exposed only deterministic
fixture, incomplete-subject selection, and reference-classification defects. Preserve that 39/42
run. Close those defects under the existing Gate 4 scope, require focused promotion/succession,
lesson, preserved-reference, bundle and twenty-attack controls to pass, then publish a new exact
subject under `iacode-subjects/` for one complete 42-stage execution.
