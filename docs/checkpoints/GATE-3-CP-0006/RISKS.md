# Risks

## R1 — Fresh-session independence is not cross-tool independence

This audit is independent of the implementing session, but it uses Codex/OpenAI/GPT-5. No different
tool or provider is exposed here. The attestation records `crossToolValidation=NOT_AVAILABLE`, and
the permitted verdict is `MILESTONE_INDEPENDENT_AUDIT_PASS` only.

## R2 — Attestation trust is structural, not cryptographic

The subject/auditor split, canonical tags and anchored chain prevent a delivery from self-asserting
approval. They do not provide an external signature. An actor able to author and publish both the
audit checkpoint and its tag remains inside the trust boundary documented by the project.

## R3 — R-G3-001 remains an accepted local architectural risk

The Sandbox controller requires access to the local container engine. Ten controls and a fresh
adversarial mutation prove that agent input cannot choose engine operations, mounts, capabilities,
privilege or network. The residual capability remains local and operational; it is accepted, not
eliminated.

## R4 — Broad live prompts can consume their turn budget

`M1-F-005` is LOW and non-blocking. Two broad diagnostic prompts exhausted twelve turns after
eleven valid Sandbox tool cycles. The required configured-model proof succeeded with seven tool
cycles, zero repair and final approval. A later implementing checkpoint should make the broad
diagnostic terminate deterministically without weakening production budgets.

## R5 — Advisory and configured-provider evidence is time-bound

The dependency and configured-model results describe the sources and service state reached on
2026-10-09. The scanner fails closed when a mandatory source is unavailable; later deliveries must
repeat it rather than inherit this PASS indefinitely.
