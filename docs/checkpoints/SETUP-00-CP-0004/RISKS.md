# Risks

- `READY_FOR_REVIEW` can currently coexist with a nonempty `blockedBy` list and validate after
  resealing, so consumers can receive contradictory state.
- Early finalizer refusals, including detached-HEAD invocation, are not appended to the ledger even
  though the protocol states every attempt is recorded.
- CP-0003 finalizer command strings omit the executable path/prefix and do not resolve from their
  recorded working directory, weakening literal replay.
- The secret-detector limitations documented by CP-0003 remain; this review did not expand scope.
- Gate 0 remains blocked, and no current checkpoint grants SETUP-00.
