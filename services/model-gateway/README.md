# Model Gateway

**Status: DELIVERED by `GATE 1`.** One provider-neutral boundary for model invocation.

Everything above this package — the API today, the agent runtime and the orchestrator of later
Gates — speaks `iacode_model_gateway.contracts` and nothing else. Everything below it is a protocol
adapter translating those contracts into one provider's wire format. Nothing in this package names a
commercial provider: a provider is an entry in
[`.iacode/policies/providers.json`](../../.iacode/policies/providers.json) naming an adapter, an
address variable and a credential variable, which is what lets a second provider be added by
configuration rather than by code.

## What it does

| Area | What the boundary guarantees |
|---|---|
| Discovery | The catalog comes from the provider's own API. A hand-written model list is not authoritative, and a capability the provider did not state stays `UNKNOWN` rather than becoming `false`. |
| Routing | Deterministic: explicit model, configured route alias, or configured default — and a clear error when a request has none of the three. No model quality is asserted anywhere; this project has measured none. |
| Protocols | OpenAI-compatible Chat Completions, OpenAI-compatible Responses and Anthropic-compatible Messages. Which one a model speaks comes from the catalog and the provider configuration, never from an assumption. |
| Streaming | Real, through the same router and the same adapters as a non-streaming call. Fallback and retry are permitted only until the first event reaches the consumer, so two models can never write one answer. |
| Failure | One error taxonomy every adapter maps onto, bounded retries with full jitter, a circuit breaker per provider and per model, and a bounded fallback chain that cannot loop. |
| Recording | Operational metadata only. There is no column for a prompt, a message or a completion, and that absence is the control. |
| Secrets | A credential is read from the environment at call time and reaches the authorization header and nothing else — no configuration object, no store record, no response, no log, no metric. |

## What it deliberately does not do

It does not execute tools. It **normalises** a tool call so a later Gate can decide what to do with
one; deciding is Gate 2's contract and running it is Gate 3's sandbox. It does not orchestrate
agents, retrieve, store experiences or train.

## Where things are

```text
contracts.py          the boundary: requests, responses, tool calls, usage, stream events
errors.py             the error taxonomy, and what may be retried or routed elsewhere
config.py             settings, the provider policy and the route policy — never a credential
ports.py              what the gateway needs from outside: the stores, the clock, the jitter
gateway.py            the assembly: limits, routing, circuit, attempt, retry, fallback, recording
protocols/            one module per wire protocol, plus the selection rule
providers/            the provider contract and the single HTTP implementation of it
catalog/              normalisation and synchronisation
routing/              the router, its policy and the context preflight
resilience/           retries, the circuit breaker and the request limits
security/             the base-URL rules that keep an outbound call from being SSRF
telemetry/            the Prometheus instruments and the structured-log contract
```

## Running it

The gateway is composed by the API — see
[`docs/runbooks/MODEL-GATEWAY.md`](../../docs/runbooks/MODEL-GATEWAY.md) for configuring a provider,
synchronising the catalog, inference, streaming, the live smoke check and how to add an adapter.
