# Risks — SETUP-00-CP-0009

- **CRITICAL** `CP9-F-001`. `MILESTONE_EXTERNAL_PASS` has no reachable positive path, so the
  milestone cadence the project depends on cannot complete. Until it is repaired, no milestone can
  be recorded as externally validated by the mechanism the project built for that purpose.
- **CRITICAL** `CP9-F-002`. The mandatory suite is red in this repository right now, because
  anchoring the sealed predecessor is both required by the protocol and fatal to a test bound to a
  literal checkpoint name. The next delivery inherits it.
- **MEDIUM** This audit is session-independent but not tool-independent. The implementing run used
  the same tool, provider and model. Blind spots shared with the implementer would not have been
  caught here, whichever way the verdict had gone.
- **MEDIUM** The integrity anchors and the attestation are tamper-evident inside the local trust
  model, not cryptographic. An actor controlling the repository can recompute both. This audit
  reproduced that limit rather than disproving it, and the repository states it honestly.
- **LOW** `CP9-F-003`, `CP9-F-004` and `CP9-F-005` are cosmetic in effect, but each is an instance
  of a class the project guards against elsewhere, which is why they are findings rather than notes.
- **LOW** The lesson preflight has no audit-role input, so an audit run cannot derive a requirement
  set that genuinely constrains it. Recorded as lesson candidate `M0-CP9-CANDIDATE-007`.
- **LOW** A defended attack is evidence about that attack. The battery is large and it includes a
  null-mutation control, but it is finite.
