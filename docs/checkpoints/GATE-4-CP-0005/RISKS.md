# Risks

- An isolated Compose project that is not cleaned after interruption can leave resources behind;
  pre-run cleanup makes the next execution safe and post-run cleanup is part of the verdict.
- Dynamic published ports require every host-side check to discover ports through Compose. A
  remaining hard-coded port would be a deterministic regression and must fail focused tests.
- Live provider stages still require explicitly configured external access; isolation must carry
  configuration without logging or persisting its values.
- Retry-based promotion remains prohibited because it would recreate the false-PASS risk identified
  by `G4-F-002`.
- Pre-final clean-clone evidence is attached to published `main`; detached identity is proved only
  after the checkpoint is sealed and its canonical tag exists.
- A future executable checkpoint harness that captures output is within the UTF-8 guard's current
  checkpoint denominator and will fail the root suite if it omits stream configuration.
