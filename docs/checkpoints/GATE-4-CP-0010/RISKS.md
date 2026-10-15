# Risks

- Same-session review is not independent review. M2 and secondToolValidation remain pending.
- The cancellation window closes at immutable verdict commitment; an operator arriving later gets
  an explicit conflict rather than a false accepted cancellation. The committed verdict is immutable.
- Durable reads alone cannot prevent races; the store's serialization and refusal paths must remain
  covered by real PostgreSQL and workflow behavior, not only source-text assertions.
- Targeted green results are not a substitute for integral verification, fresh Green Keeper,
  total completeness, internal Red Team or clean-clone mirror assurance. Those are still pending.
- A failed verifier must be preserved before any replacement execution. Never reuse only its green
  stages, remove a correct test, increase a product timeout or edit historical sealed evidence.
- Gate 5 is authorized by the owner but cannot begin until this Gate 4 checkpoint actually seals
  a valid internal closure. No authorization for Gate 6 is inferred.
- A clean-control live run once stalled after its first result. The complete repeat passed without
  increasing the deadline, but the original ephemeral history was not retained. Bounded pre-cleanup
  diagnostics now guard recurrence. A matching polling-cleanup race was reproduced and corrected,
  but that is not reconstruction of the lost history. Fresh full verification must not hide or
  reuse that attempt.
- Plain, escaped, nested JSON and beyond-inline output must remain rejected at the first durable
  boundary. Matching digests do not exempt legacy objects from rescanning.
