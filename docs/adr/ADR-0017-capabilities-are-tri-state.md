# ADR-0017 — A capability is tri-state and carries its provenance

Status: Accepted
Date: 2026-09-22
Owners: GATE 1 — Model Gateway

## Context

The router has to answer questions like "can this model call tools" and "can this model return
structured output" before spending money on finding out. The catalog is discovered from each
provider's own API, and providers disagree about what they publish: some declare capabilities,
most declare almost nothing, and the fields they do declare are not the same fields.

The tempting shortcut is inference from the identifier. A model whose name contains `vision`
probably takes images; one called `gpt-4o` probably calls tools. This works until a provider
renames a model, or serves a different model behind a familiar name, or a name that never implied
anything acquires a meaning.

The question this ADR settles: what does the catalog record when the provider says nothing?

## Decision

**Three states, never two, and every state carries where it came from.**

`CapabilityState` is `SUPPORTED`, `UNSUPPORTED` or `UNKNOWN`. `CapabilityProvenance` is
`PROVIDER_METADATA`, `MANUAL_CONFIGURATION`, `OBSERVED` or `UNKNOWN`.

`UNKNOWN` means the provider said nothing. It is **not** a synonym for `UNSUPPORTED`, and the
gateway never converts one into the other.

There is deliberately no `INFERRED_FROM_NAME` provenance. A model identifier is marketing copy; it
is not an interface description, and a catalog that guesses is a catalog that is wrong in a way
nobody can audit.

Where a capability is `UNKNOWN`, the router **refuses** the candidate for a request that requires
it, and says so in the rejection. A route may opt into the risk explicitly through
`allowUnknownCapability`, which names the capabilities an operator has decided to gamble on for
that route. The gamble is written down, in a versioned file, per route.

An administrator's statement in `.iacode/policies/providers.json` under `capabilities` is applied
with provenance `MANUAL_CONFIGURATION`, and **only where the model's own metadata is silent**. A
provider that publishes `tools: false` is not overruled by an operator who thinks otherwise.

## Evidence

- `services/model-gateway/src/iacode_model_gateway/contracts.py`: `CapabilityState`,
  `CapabilityProvenance`; no member derived from a name.
- `services/model-gateway/src/iacode_model_gateway/catalog/normalize.py`: `provider_capabilities`
  is applied only to capabilities the model did not state.
- `services/model-gateway/tests/test_catalog.py` covers an unknown capability, invalid metadata and
  a provider statement that does not overrule the model's own.
- `services/model-gateway/tests/test_routing.py` covers a required capability the catalog reports
  as `UNKNOWN` being rejected, and the explicit opt-in allowing it.
- Observed live: all 36 DevWorld models report `tools`, `vision`, `structured-output` and
  `reasoning` as `UNKNOWN`, because the provider's `/models` publishes nothing about them, while
  `streaming` is `SUPPORTED` with provenance `MANUAL_CONFIGURATION`.

## Alternatives Considered

**Two states, defaulting `UNKNOWN` to `UNSUPPORTED`.** Safe-looking and wrong in practice: with the
provider we integrated, it would mark every model as incapable of tool calling, making the whole
catalog unusable for Gate 2 — while the provider's own configuration says every one of them
supports it. A default that is wrong for 100% of a real catalog is not a conservative default.

**Two states, defaulting `UNKNOWN` to `SUPPORTED`.** Optimistic, and it spends money to discover
each error, with the failure arriving as a provider-specific 400 the user has to interpret.

**Infer from the model identifier.** Rejected above. It also produces a catalog that silently
changes meaning when a provider renames something, which is the worst kind of change: invisible.

**Probe each model once and record `OBSERVED`.** Attractive, and it costs a real inference per
model per capability — 36 models times four capabilities, against a provider we are told not to
hammer. The `OBSERVED` provenance exists for the Gate that wants to pay that cost deliberately;
nothing in Gate 1 writes it.

## Consequences

- The router is honest about what it does not know, and a rejection says which capability was
  unknown rather than just "no candidate".
- An operator who knows more than the provider publishes has one place to say so, and their
  statement is distinguishable from the provider's in the catalog.
- Requests that require tools will be refused for a provider that publishes nothing, until either
  the operator states the capability or the route opts in. That is friction by design, and the
  runbook says how to resolve it.
- Every capability answer in the system can be traced to who claimed it.

## Risks

- **Operators route around the friction by allowing unknowns everywhere.** Mitigated by
  `allowUnknownCapability` being per-route and per-capability in a versioned file, so the blanket
  version is visible in a diff.
- **`MANUAL_CONFIGURATION` drifts from reality.** Real: an operator's statement is not revalidated.
  The `OBSERVED` provenance is the intended answer, in the Gate that has a reason to probe.

## Reversal Strategy

Collapsing to two states means choosing a default and deleting the provenance map — a migration
that drops two columns. Nothing outside the catalog depends on the third state except the router's
rejection reasons, which would lose detail but keep working.

## Related Artifacts

- [ADR-0016](ADR-0016-model-gateway-boundary.md)
- [ADR-0004](ADR-0004-provenance-default-deny.md) — the same principle applied to rights
- `docs/GATE-1-CHECKLIST.md` rows 6.x, 7.x
- `docs/runbooks/MODEL-GATEWAY.md`
