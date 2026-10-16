# Diff Summary

- Durable cancellation is re-read after activity completion and before final derivation; persistence
  races return to terminal cancellation while unrelated activity errors remain errors.
- Verdict derivation fails closed on accepted cancellation. Both stores serialize the cancellation
  window against immutable verdict commitment; the API reports a late request as HTTP 409.
- Behavioral tests cover activity/result/verdict races, both commit orders, real PostgreSQL
  concurrency, normal success, unrelated error propagation and the API's no-signal conflict path.
- Live contracts and adapters use the existing milestone cadence under explicit owner authorization.
  Every original canonical row, executable gate, attack and functional requirement is retained;
  output containment adds a mandatory functional obligation rather than replacing an original one.
- Sandbox output, complete decoded streams and provisioning diagnostics are scanned before the
  first artifact or activity response becomes durable. Runtime and publication share the same
  bounded nested/mixed-JSON transport views and canonical credential taxonomy.
- Polling cleanup recognizes only its own typed Temporal cancellation and preserves completed
  checks; the authoritative cancellation read remains safe after the active handle is cleared.
- Test discovery and evidence share policy-bound collection boundaries. Live input repositories
  remain mandatory scenario inputs, without counting their uncollected fixture tests as regressions.
- Memory policy 2.4.0 enforces truthful current internal verdicts while sealed historical subjects
  retain their own policy semantics. No historical checkpoint or approval is rewritten.
- Two historical synthetic alphabet-sequence redaction markers were reviewed by exact component
  digest and sanitized AST provenance; no path, commit or finding kind was broadly excluded.
- ADR-0037 through ADR-0045, escalated Engineering Memory, the predecessor integrity anchor,
  preserved red attempts and this checkpoint record the implementation and its actual evidence.
- No CLI, extension, future-Gate implementation or sealed CP0009 file is changed.

## Published verification subject

V3 has completed PASS (cmd-0299): 42/42 stages and all cleanup/isolation checks. Its actual result
is preserved unchanged under attempts/published-v3 (cmd-0300). Older active-v3 notes below are
historical, not the current process state. The next subject must include the later resumability
correction and receive its own complete execution before current-source approval.

Immutable v3 at 0b1fa85c46cf3ce0bcb13fd4792f389d97d71ea4 is executing unchanged. A later mandatory
resumability correction requires a new subject before approval: generated live state in ignored
var/, real SHA/staleness checks, truthful latest steps, strict checkpoint projection and preserved
legacy meanings. Ten actual CLI/Git controls pass. The complete latest denominator derives to
1804 cases and 220 obligations. V3 does not approve these later changes.

The complete corrected implementation is published at
`4c53e4f788adc24e1b9cd9f581a7dc0d0f3c1340`, tagged
`iacode-subjects/GATE-4-CP-0010-internal-corrective-v2`. Its single complete remote-clone verifier
completed FAIL (41/42). Its five reports are preserved in attempts/published-v2. Nine historical
collection incompatibilities have a targeted versioned correction; the missing UTF-8 case was
reproduced on exact published v2 and all current Foundation controls passed after correction.
Scanner line metadata has measured-cost and coordinate-equivalence regressions;
the verifier now retains bounded sanitized failed-case identifiers beyond its tail. Publication is
not a Gate verdict. A new complete subject, final assurance, internal closure and sealing remain due.
