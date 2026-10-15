# Diff Summary

- Durable cancellation is re-read after activity completion and before final derivation; persistence
  races return to terminal cancellation while unrelated activity errors remain errors.
- Verdict derivation fails closed on accepted cancellation. Both stores serialize the cancellation
  window against immutable verdict commitment; the API reports a late request as HTTP 409.
- Behavioral tests cover activity/result/verdict races, both commit orders, real PostgreSQL
  concurrency, normal success, unrelated error propagation and the API's no-signal conflict path.
- Live contracts and adapters use the existing milestone cadence under explicit owner authorization.
  The canonical Gate row count, executable gate set, attack set and functional scope are preserved.
- ADR-0037/0038, Engineering Memory, integrity anchor and this checkpoint record the evidence.
- No CLI, extension, future-Gate implementation or sealed CP0009 file is changed.
