# Decisions

- Adopt ADR-0037 under the explicit owner authorization in AUTHORIZATION.md: intermediate closure
  is internal, not GATE_PASS, and independent M2 validation remains pending until its closure.
- Preserve CP0009 at its original sealed tag. Its status, evidence and original handoff are historical.
- Adopt ADR-0038: cancellation and immutable verdict commitment serialize on the same run-row lock.
  Durable cancellation wins when accepted first; later cancellation receives an explicit conflict.
- Recover cancellation-boundary activity failures only when authoritative state confirms accepted
  cancellation. Unrelated failures propagate and remain visible.
- Preserve cmd-0005, cmd-0009 and cmd-0014 as red evidence. The two unittest filename precondition
  refusals executed no tests; replayable globs subsequently ran the intended suites successfully.
- Every verification is internal to this same session. No second-tool or fresh-session attestation
  is created, and M2 is never marked PASSED here.
- Cancellation adds a verdict reason only when otherwise-complete results would permit PASS.
  Existing FAIL derivations retain their canonical reason set and digest, preserving immutable
  retry compatibility rather than rewriting an already-failing fact.
- Preserve cmd-0022 and escalate the LSN-0011 bookkeeping recurrence. Finish all evidence producers
  before inventory binding, derive the preflight aggregates and run commit semantics together with
  sync_in_progress_metadata.py, and then refresh hashes. The synchronizer refuses sealed, terminal
  or wrong-Gate state and cannot promote requirements or verdicts.
