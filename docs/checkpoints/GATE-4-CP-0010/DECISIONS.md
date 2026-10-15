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
- Adopt ADR-0039: scanning must precede sandbox artifacts, persisted provisioning diagnostics and
  activity responses, not only evaluator evidence. Decode full streams and nested JSON with the
  canonical taxonomy; reject scanner failures and retain clean positive controls.
- Adopt ADR-0040: regression counts and evidence share canonical runner collection policy. Live
  input repositories remain mandatory functional inputs but are not uncollected regression cases.
- Keep failed live attempts, including the clean-control timeout, visible. Cmd-0079 proves the
  complete inline/full-stream output scenario with decoded history, MinIO absence and owned cleanup;
  it does not explain the earlier transient control stall or approve later nested-transport changes.
- The complete v1 verifier is about published subject 33c3f42 only. Its failing root suite and any
  subsequent result remain historical; a new complete immutable-subject execution is mandatory.
- Adopt ADR-0041 after causal red regressions and a probe of the pinned SDK: polling cleanup
  recognizes only its own typed cancellation, preserves completed checks, and never suppresses
  unrelated or precompleted failures. Durable cancellation survives handle clearance after a read.
- Extend the owned output proof with nested inline JSON and a second clean run after both refusals.
  Every timeout writes a red bounded diagnostic report before cleanup; no deadline is increased.
- Publication uses the same bounded transport views as runtime, with exact digest review and a
  negative same-kind control. The two additionally detected historical alphabet-sequence markers
  are tied to their actual introducing redaction-test literal, not broadly allowlisted by source.
- Adopt ADR-0042 after the complete v1 root regression: strict current internal-role semantics are
  versioned at memory policy 2.4.0. Current-policy downgrade is refused by a mandatory regression;
  immutable legacy field meanings remain valid without granting independence.
