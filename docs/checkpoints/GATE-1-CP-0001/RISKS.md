# Risks — GATE-1-CP-0001

Each risk names what would go wrong, what currently holds it down, and what is left over after the
control. A risk with no residual is a risk that has not been thought about honestly.

## Open

**A provider credential leaves the environment.** The value exists in `infra/compose/.env`, which
Git ignores, and is resolved into a `SecretStr` used only in outbound request headers.
`test_secrets.py` asserts separately that it appears in no log, exception, response, record, metric
or catalog entry; `ProviderConfig` refuses a value where a variable name belongs; the browser bundle
was checked live and carries nothing. *Residual:* none of this controls what happens to a credential
outside the machine. A key that has travelled through a chat, a screenshot or an old configuration
file is already exposed and must be rotated — the controls make the blast radius knowable, not
zero.

**A provider changes its API and the catalog silently degrades.** Normalisation drops what it does
not recognise rather than refusing the whole catalog, so one unfamiliar field cannot take the
catalog offline. *Residual:* a provider that renames the field carrying context windows would
produce a catalog of models with no context window, and the router would reject them for prompts
that actually fit. Detection is the operator noticing `NO_CANDIDATE`; there is no alarm for it.

**The free-tier models are unreliable and were not proved.** The live smoke exercised exactly one
model. The provider returned `502 upstream_error` for the free Gemini model at the time of the
delivery. *Residual:* 35 of 36 catalogued models have never been called through this gateway. The
adapters are protocol-level and the provider serves all of them over one protocol, so the risk is
about individual models, not about the boundary.

**Every capability except streaming is `UNKNOWN` for this provider.** The provider publishes no
capability metadata, and the gateway refuses to guess. *Residual:* a Gate 2 agent requiring tool
calling will be refused by the router until an operator states the capability in `providers.json`
or a route opts in through `allowUnknownCapability`. This is deliberate friction, and the runbook
says how to resolve it, but it is friction that will be met on the first day of Gate 2.

**`max_output_tokens` is absent for every live model.** The provider does not publish it. The
global ceiling `IACODE_GATEWAY_MAX_OUTPUT_TOKENS` bounds every request regardless. *Residual:* a
request within the global ceiling but above a specific model's limit fails at the provider rather
than at the gateway, with the provider's own message.

**Cost is never computed.** No pricing table is configured, so every recorded call has a null cost.
*Residual:* the operational record answers "how many tokens" but not "how much money". The Gate
that introduces a budget introduces the table.

**A hash is treated as anonymisation.** `request_fingerprint` is a SHA-256 of the canonicalised
request. *Residual:* anyone holding a candidate prompt can confirm a match. The runbook says so in
as many words; nothing enforces that a reader believes it.

**The stale-image defect class may exist elsewhere.** `GRD-0038` covers gates whose command runs
inside an image. *Residual:* the rule recognises the shapes present today. A future gate that
measures a different kind of build artefact — a frontend bundle, a wheel — would need the rule
extended, and the failure mode would again be silence.

## Closed during this Gate

| Risk | Closed by |
|---|---|
| A mandatory gate reporting on source that is not in the repository | `GRD-0038`, and the defect it had concealed was fixed |
| A scope control refusing the authorized Gate | `GRD-0039` |
| The two redactors disagreeing about a placeholder | `GRD-0040` |
| Test fixtures accumulating in the operational catalog | `GRD-0041`, plus per-test cleanup and a purge of the existing residue |
| A provider name reaching a provider-neutral module | The boundary scan, with a negative control |
| Two models' output spliced into one stream | The commitment-point rule and its named test |
| A prompt reaching the database | The schema, asserted against the real database |

## Accepted, with the reason

**The gateway cannot be deployed or scaled independently of the API.** Accepted: nothing in this
Gate needs it, and `ADR-0016` records the reversal path.

**The live smoke spends tokens on every full verification.** Accepted: one short prompt with a
32-token cap is the price of evidence that the integration works. The alternative is a Gate that
claims a live integration it never ran.

**`services/` contains one thing that is not a service.** Accepted: the directory name comes from
the Gate 0 reservation, and renaming it would break the scope registry for no functional gain. The
README says so in its first line.
