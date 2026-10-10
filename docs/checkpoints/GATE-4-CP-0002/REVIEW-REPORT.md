# Gate 4 fresh-session independent audit

- Audit checkpoint: `GATE-4-CP-0002`
- Sealed subject: `GATE-4-CP-0001` at `70a22e824705f414e0c295bbdf89187db9b391f7`
- Mechanism: `FRESH_SESSION_INDEPENDENT_AUDIT` by Codex desktop application, OpenAI. This is not a cross-tool milestone verdict.
- Verdict: **`REWORK_REQUIRED`**.

## Subject identity and provenance

The local tag, published branch, published tag and transport clone all resolve to the expected subject commit. The supplied sealed bundle has SHA-256 `af98b920cc4849298486d58f0ac96262e949006c02f02138943044188af49df7` and validates against the subject. The audit revalidated the checkpoint chain and the published objects named by sealed evidence.

## Blocking finding

`G4-F-001` is HIGH: a credential-shaped value recognized by the canonical secret scanner can cross the Quality Engine's durable evidence boundary. The delivered evaluator image reproduced the exact activity-to-store path with a synthetic marker assembled in memory. The scanner detected it; the normal redaction did not remove it; the evidence store committed it and returned it unchanged. The audit artifact contains only a digest and boolean observations, not the marker.

This contradicts `canonical:GATE-4#19.2`, which requires secret-bearing output to be quarantined and the prohibited bytes not to be persisted. A later repository source scanner does not protect this boundary.

## Required correction

A later implementing checkpoint must scan the fully serialized evidence object before durable commit, quarantine or fail closed on detection, prove that the object cannot be resolved, and add a regression test for credential material under an unremarkable structured key. It must not weaken the canonical scanner, requirement, denominator, or promotion policy.

## Verdict

`REWORK_REQUIRED`. Gate 4 does not receive `GATE_PASS`; M2 remains pending; Gate 5 is not advanced. This auditor made no product correction and issued no passing attestation.
