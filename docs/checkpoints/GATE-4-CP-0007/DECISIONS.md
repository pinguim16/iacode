# Decisions

1. CP0006 and its canonical tag are immutable evidence of the failed publication attempt; CP0007
   succeeds it rather than repairing it in place.
2. `G4-F-003` is registered as mandatory corrective work and is not inferred from delivery prose.
3. The failure matches `LSN-0040` and is handled as a guardrail failure.
4. A forward-only schema revision will enforce the stronger rule without retroactively changing the
   schema contract under which earlier checkpoints were sealed.
5. A generated review archive is an output, not a repository input. Its repository-carried report,
   manifest and digest are the durable evidence.
