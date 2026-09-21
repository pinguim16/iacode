# Decisions

## D1 — The milestone verdict belongs to the audit checkpoint, not to the delivery it judges

`CP9-F-001` was not a missing check but a control attached to the wrong object: the attestation was
verified against the checkpoint being promoted, so satisfying it required a tree containing its own
commit identifier. The subject is now immutable and the audit checkpoint carries the verdict, naming
the subject and the commit its canonical tag already resolves to. Recorded as
[ADR-0011](../../adr/ADR-0011-audit-checkpoint-carries-the-verdict.md).

Alternatives considered and rejected: binding `subjectCommit` to the content commit, which leaves the
verdict on the judged object; and excluding `.iacode/attestations/` from the assurance scope, which
would have turned the staleness green without making any positive path reachable and would have
blinded the audit checkpoint to a file it authors.

## D2 — `MILESTONE_INDEPENDENT_AUDIT_PASS` exists because the honest name mattered

The owner-authorised mechanism is a fresh session of the same tool. Calling that `EXTERNAL` would
have been the kind of vocabulary the audit itself warned about, so the mechanism is recorded in the
attestation and each mechanism authorises only the status its evidence supports. Gate authorisation
follows from either accepted mechanism; the cross-tool status stays available and unused.

## D3 — One derived rule for the checkpoint whose anchor is still owed

`CP9-F-002` was one semantic rule with two implementations, one derived and one typed. The typed copy
is gone: `anchors.pending_anchor_exclusion` answers the question for the CLI, the validator and the
suite, and it is derived from sealed history by ancestry rather than by name order, so a future Gate
prefix cannot make "newest" wrong.

## D4 — A count in a comment or a docstring is not evidence

The decision the audit asked for is recorded in `docs/QUALITY-GATES.md`: canonical counts live in
`COUNTS.json`, derived and recomputed; comments and docstrings describe semantics. The control scans
comments and docstrings only, because a count inside an ordinary string literal is data — the Red
Team forges one deliberately, and forbidding that would forbid the attack that proves the control.

## D5 — `CP9-F-003` is a recurrence, not a new lesson

`LSN-0022` already carried the class — an authoritative count maintained in a second place — and it
was `GUARDED` when the repeat happened, so it is recorded as a `GUARDRAIL_FAILURE`, escalated to
`CRITICAL`, and resolved by naming this checkpoint as the one that repaired the control. Creating a
second lesson would have split one failure class in two and hidden the recurrence.

## D6 — The unread policy key is removed rather than made configurable

`CP9-F-005` offered both architectures. The registry has exactly one location, nothing in the design
needs it to move, and a configurable path would add resolution and traversal rules for no behaviour.
The key is gone, the fixed path is documented, and the policy document is now validated against a
closed schema, so the *class* of defect — a declared setting no code reads — is prevented rather than
this instance being cleaned up.

## D7 — The delivery executes the protocol's own positive paths

Two simulations run before handoff, both in disposable repositories: a complete two-checkpoint
promotion, and a sealed chain advanced through three checkpoints with the integrity controls re-run
at every state. They exist because both critical findings were failures that only appear when the
sequence of repository states is executed rather than reasoned about.

## D8 — Test fixtures derive from current policy instead of copying a sealed claim

The closure fixture copied a sealed checkpoint's preflight and requirement matrix, so every new
lesson or checklist row made the fixture fail for its own reasons. It now re-derives both from
current policy. This is the same class as `CP9-F-002`: a test must not encode the repository as it
looked on the day it was written.

## D9 — One physical test run is one measurement

`SETUP-00-CP-0009` disclosed that it had recorded a single 306-case execution as both unit and
integration and derived 610 passing tests. `TESTS.json` now carries an optional `runId`, the
derivation deduplicates by physical execution, and validation refuses a numerator larger than its
denominator.

## D10 — Every adversarial battery records its null-mutation control

The audit's own harness reported every attack as defended while the refusals came from leftover
state. A battery now records the unmutated control it ran, the report schema requires it, and
validation refuses a `PASS` whose control is missing or `INVALID`.

## D11 — The audit registry, not a literal, names the reports a delivery corrects

`derive_requirements.py` hardcoded the CP-0007 report paths as its sources. They are now read from
the registry entry that binds an audit to this corrective checkpoint, and `parse_attacks` decides
which battery a row belongs to from its section heading rather than from the width of its table, so
registering a second audit does not silently promote twenty-six additional attacks to mandatory.

## D12 — The remaining literal checkpoint identifiers are fixtures, and are documented as such

`HistoricalCheckpointCompatibilityTests` names each sealed checkpoint on purpose: the contract is
that every one of them keeps validating. `ClosureFixture` copies one checkpoint as a template and
re-derives everything that could go stale. `LessonProvenanceTests` cites real checkpoints because it
tests resolution against real evidence. No generic guard decides behaviour from a historical name.
