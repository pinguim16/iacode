# Baseline

CP0009 is sealed at `ff2814f7d7bf06fa8a99858b958daf3f22197496`. The entry validator
returned `CHECKPOINT_VALID`; `main`, HEAD, origin/main and the canonical tag agree and the
working tree was clean before this successor was created. CP0009 is never edited or re-tagged.

The sealed implementation has complete verifier and functional evidence. Those historical
results are baseline evidence, not executions by this checkpoint. Fresh mandatory assurance
must judge every change made here.

The owner explicitly requested self-review, correction and advancement to Gate 5, deferring the
independent audit until the end. This run applies the existing milestone cadence: M2 comprises
Gates 4 through 7. It does not claim session independence or cross-tool validation.

Review found contradictory per-Gate and milestone cadence text. It also identified a cancellation
race candidate: persisted CANCELLING may outlive the activity watcher and precede the signal or
the result write. Behavioral regressions must reproduce it before correction.
