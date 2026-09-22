# Runbook — the Model Gateway

Everything an operator does to the Gate 1 gateway: configuring a provider, discovering its models,
sending a request, reading what went wrong, and adding a protocol adapter.

The gateway is a library — `services/model-gateway/` — that the API composes. It has no process of
its own, no port of its own and no database of its own. It declares the storage it needs as ports
and the API implements them, which is why a second consumer can use it later without inheriting a
web application.

## What the gateway is, and what it is not

It does: register providers, discover models from the provider's own API, normalise capabilities,
select a model, send an inference request, stream the answer, normalise usage and tool calls,
record what the call cost in latency and tokens, retry, fall back, break the circuit, enforce
limits, expose metrics and keep the credential out of everything.

It does not: run agents, execute tools, index anything, train anything, or store a conversation.
There is no prompt in the database and no memory between requests. A tool call is *normalised* —
the gateway reports what the model asked for; nothing here executes it.

## Configuration

Two files and one environment. The split is the point:

| Where | What lives there | Committed |
|---|---|---|
| `.iacode/policies/providers.json` | which providers exist, which adapter serves each, and the **names** of the variables that carry the address and the credential | yes |
| `.iacode/policies/model-routes.json` | route aliases (`default`, `fast`, `deep`, `coding`, `review`) and their candidate order | yes |
| `infra/compose/.env` | the address and the credential themselves | **no** — Git ignores it |

A value never appears in a committed file. A versioned credential is a published credential, and
`ProviderConfig` refuses a `*_env` field that holds anything other than a variable name, so the
mistake fails at load rather than at the first request.

### The variables

| Variable | What it is |
|---|---|
| `IACODE_DEVWORLD_BASE_URL` | the provider's API root, the part `/models` and `/chat/completions` are appended to |
| `IACODE_DEVWORLD_API_KEY` | the credential. Set it only in `infra/compose/.env` |
| `IACODE_OPENAI_BASE_URL` | the second provider's API root, for example `https://api.openai.com/v1` |
| `IACODE_OPENAI_API_KEY` | its credential. Set it only in `infra/compose/.env`; left empty, the provider is reported unconfigured and routed around |
| `IACODE_GATEWAY_DEFAULT_MODEL` | `provider:model`, used when a request names neither a model nor a route |
| `IACODE_GATEWAY_SMOKE_MODEL` | `provider:model` the live smoke check is authorised to spend on |
| `IACODE_GATEWAY_CONNECT_TIMEOUT_SECONDS` | connect timeout; there is no unbounded wait anywhere |
| `IACODE_GATEWAY_READ_TIMEOUT_SECONDS` | read timeout, which also bounds a stream between events |
| `IACODE_GATEWAY_MAX_ATTEMPTS` | attempts per candidate including the first; `1` disables retrying |
| `IACODE_GATEWAY_MAX_FALLBACKS` | additional candidates after the first; the chain is bounded by this |
| `IACODE_GATEWAY_MAX_OUTPUT_TOKENS` | the ceiling a request cannot exceed, whatever it asks for |
| `IACODE_GATEWAY_CIRCUIT_FAILURE_THRESHOLD` | consecutive failures before the circuit opens |
| `IACODE_GATEWAY_CIRCUIT_COOLDOWN_SECONDS` | how long it stays open before one probe is allowed |
| `IACODE_GATEWAY_PERSIST_PROMPTS` | `false`, and it is false by default. See *Privacy* below |

`IACODE_GATEWAY_DEFAULT_MODEL` is deliberately empty in the committed example. A request that names
no model then fails instead of silently spending tokens on a model nobody chose.

### First configuration

```bash
python scripts/iacode/bootstrap_env.py
```

Then set `IACODE_DEVWORLD_BASE_URL` and `IACODE_DEVWORLD_API_KEY` in `infra/compose/.env`, start
the stack, and discover the catalog before choosing the two model variables — the identifiers must
come from the provider, not from memory:

```bash
python scripts/iacode/stack.py up
curl -s -X POST http://localhost:18080/api/v1/gateway/models/sync
curl -s http://localhost:18080/api/v1/gateway/models?limit=200
```

Fill `IACODE_GATEWAY_DEFAULT_MODEL` and `IACODE_GATEWAY_SMOKE_MODEL` with identifiers that listing
actually contains, then `python scripts/iacode/stack.py up` again to load them.

## The HTTP API

Everything is under `/api/v1/gateway`.

| Route | What it does |
|---|---|
| `GET /providers` | every configured provider, whether it is reachable, and whether a credential is present — the name of the variable that carries it, never a value |
| `GET /models` | the catalog, filterable by `provider` and `active` |
| `POST /models/sync` | discover the catalog from every enabled provider and apply it |
| `GET /health` | reach each provider now, and report the contract version, the catalog size, the default model, the route aliases and the state of every circuit |
| `POST /infer` | one non-streaming inference |
| `POST /stream` | one inference as Server-Sent Events |

### Synchronising the catalog

```bash
curl -s -X POST http://localhost:18080/api/v1/gateway/models/sync
```

```json
{"outcomes": [{"provider": "devworld", "added": 36, "updated": 0,
               "deactivated": 0, "unchanged": 0, "errors": []}]}
```

Running it again reports `unchanged` for everything. A synchronisation is one transaction per
provider: a catalog applied model by model can be left half-applied, and an operator is then
holding a catalog that is neither the old one nor the new one.

A model that disappears from the provider is **deactivated, never deleted**. `model_calls` rows
point at it, and deleting it would turn recorded history into a dangling reference.

A provider that answers with an empty list is refused rather than applied. The one thing worse
than a stale catalog is an empty one produced by a provider having a bad minute.

### Listing

```bash
curl -s "http://localhost:18080/api/v1/gateway/models?provider=devworld&active=true&limit=200"
```

Each model reports its capabilities as one of `SUPPORTED`, `UNSUPPORTED` or `UNKNOWN`, with the
provenance of that statement: `PROVIDER_METADATA`, `MANUAL_CONFIGURATION`, `OBSERVED` or `UNKNOWN`.

`UNKNOWN` means the provider said nothing. It is not a synonym for "no", and the gateway never
guesses a capability from a model's name — a name is marketing, not an interface. A request that
requires a capability the catalog reports as `UNKNOWN` is refused with `NO_CANDIDATE` unless the
route explicitly allows it through `allowUnknownCapability`.

### Inference

```bash
curl -s -X POST http://localhost:18080/api/v1/gateway/infer \
  -H 'Content-Type: application/json' \
  -d '{"model": "devworld:devworld/claude-haiku-4-5-t",
       "maxOutputTokens": 32,
       "messages": [{"role": "user", "content": "Reply with exactly: IACODE_GATEWAY_OK"}]}'
```

The answer carries the model that actually served it, the endpoint, the route decision, the usage
the provider reported and the finish reason. Nothing is invented: a field the provider did not
send is absent, not zero. Cost is `null` until a pricing table is configured, because a cost of
zero is a claim and an absent cost is a fact.

Either `model` or `route` — never both. `route` resolves through `model-routes.json`; `model` is
`provider:model` and is never substituted.

### Streaming

```bash
curl -N -X POST http://localhost:18080/api/v1/gateway/stream \
  -H 'Content-Type: application/json' \
  -d '{"model": "devworld:devworld/claude-haiku-4-5-t",
       "maxOutputTokens": 32,
       "messages": [{"role": "user", "content": "Count to three."}]}'
```

Server-Sent Events, each with a monotonic sequence number: `start`, then `content` deltas, then
`usage` if the provider sends it, then `end` — or `error` in place of `end`.

The safety rule that matters: **retry and fallback are permitted only until the first event
reaches the consumer.** After that the gateway can no longer switch models without splicing two
models' output into one stream, so a failure after the first delta becomes an `error` event rather
than a silent substitution. `test_no_two_models_are_concatenated_in_one_stream` is the control.

Cancelling the request closes the upstream connection deterministically; the gateway does not leave
a provider call running for an answer nobody will read.

### Routing and fallback

A request resolves to an ordered list of candidates: an explicit model is a list of one; a route is
its configured candidates in order. Each candidate is filtered on what the catalog says — the
provider is enabled, the model is active, it supports the endpoint, it supports every required
capability, and the estimated prompt fits its context window.

Rejections are explained, up to eight of them, so `NO_CANDIDATE` says *why* rather than just *no*.

Fallback moves to the next candidate only for errors whose class allows it. `INVALID_REQUEST`,
`CONTEXT_LIMIT` and `MODEL_NOT_FOUND` never fall back: the next model would fail the same way, and
a chain of identical failures is a bill, not a recovery. The chain is bounded by
`IACODE_GATEWAY_MAX_FALLBACKS`, and a candidate is never attempted twice.

Retry is separate and narrower: rate limiting, provider timeout, connection failure and transient
server errors, with full-jitter exponential backoff and `Retry-After` honoured when the provider
sends it. Authentication failures are not retried — repeating a rejected credential is how an
account gets locked.

The circuit breaker is scoped both to the provider and to the provider-and-model pair, so one bad
model does not take a whole provider offline and one bad provider does not need each of its models
to fail separately.

## Privacy and what is stored

`model_calls` records the operational facts: which provider, which model, the endpoint, the route,
the status, the timestamps, the latency, the token counts, the retry and fallback counts, the error
type, the correlation id.

There is no column that can hold a prompt, a completion, a message or a credential. That is
enforced by the schema, not by the discipline of the code above it —
`test_no_table_stores_a_prompt` asserts it against the real database.

`IACODE_GATEWAY_PERSIST_PROMPTS` is `false` and there is nothing behind it in this Gate.

### The request fingerprint

A `request_fingerprint` may be stored: the SHA-256 of the canonicalised request, so the same
request made twice can be correlated across logs without storing what it said.

**A hash is not anonymisation.** With a candidate prompt in hand, anyone can confirm a match, so a
fingerprint is a pseudonym for a request, not a guarantee about its content. Treat the column as
sensitive-adjacent, not as sanitised data.

## Secrets

The credential is resolved once at startup from the environment into a `SecretStr` and is used in
exactly one place: the request headers of the outbound provider call.

It appears in no log, no exception message, no HTTP response, no persisted record, no metric label
and no catalog metadata. `services/model-gateway/tests/test_secrets.py` asserts each of those
separately rather than as one claim.

**The provider credential never reaches the browser.** The Angular application talks only to the
IACode API, which holds the credential server-side. Verified during this Gate against the running
stack: the loaded bundle and the rendered DOM contain no credential, no bearer header and no
provider key of any kind.

The API's error responses carry an allow-list of detail keys, so a provider's own error body cannot
leak through the gateway into a client.

## The live smoke check

```bash
python scripts/iacode/gateway_smoke.py
```

Twenty checks against the real provider: catalog discovery, a second synchronisation that changes
nothing, the smoke model's presence in the discovered catalog, normalisation, a non-streaming
inference, attribution, latency, usage, the absence of an invented cost, a streaming inference with
its start/deltas/end and no duplication, the persisted record and its lack of a prompt, and a
Prometheus query proving the observability stack saw the request.

It is deliberately small: one short prompt, a 32-token output cap, no repetition, no deliberate
rate limiting and no repeated authentication failure against a real account. Failure modes are
proved with fixtures in the gateway suite, not by abusing a provider.

Exit codes: `0` PASS, `1` FAIL, `2` BLOCKED. `BLOCKED` is what you get when the credential is not
configured, and it names the variable that is missing — it never degrades into a PASS, and it never
falls back to an unauthenticated call.

The configured smoke model is never substituted. If it is absent from the discovered catalog the
check fails, because quietly spending on a different and possibly far more expensive model is the
failure this rule exists to prevent.

## The web page

<http://localhost:18081/gateway> shows the provider table — adapter, enabled, reachable, whether a
credential is present, model count, last synchronisation — the full catalog with its capabilities
and provenance, a `Synchronise catalog` button, and a one-shot playground.

The playground is one prompt and one answer. It is not a chat: there is no conversation, nothing is
stored, and the gateway keeps no prompt. It reports the model that served the request, the
endpoint, the route reason, the latency, the usage and the finish reason.

Checked in a browser during this Gate: the catalog rendered 36 models, `Synchronise catalog`
returned the same catalog unchanged, and the playground returned a live answer from
`devworld:devworld/claude-haiku-4-5-t` in about two seconds with usage reported and cost shown as
unknown rather than zero.

## Troubleshooting

| Symptom | What it means | What to do |
|---|---|---|
| `GATEWAY_SMOKE=BLOCKED` | a required variable is empty | the message names it; set it in `infra/compose/.env` and `stack.py up` |
| `PROVIDER_UNAVAILABLE` after three attempts | the provider answered 5xx each time | read the API log: the upstream status and body summary are there. A free tier returning *capacity temporarily unavailable* is the provider, not the gateway |
| `AUTHENTICATION_ERROR` | the credential was rejected | it is not retried by design. Check the variable is set in `.env` and that the stack was restarted since |
| `NO_CANDIDATE` | every candidate was filtered out | the response lists the rejections and the reason for each: inactive, unsupported endpoint, unknown capability, context too small |
| `MODEL_NOT_FOUND` | the identifier is not in the catalog | synchronise; the provider may have renamed or withdrawn it |
| `CIRCUIT_OPEN` | too many consecutive failures | it closes itself after the cooldown. `GET /health` reports every open circuit under `circuits`; `GET /providers` reports whether each provider is reachable |
| `CONTEXT_LIMIT` | the prompt does not fit | neither retried nor fallen back to; shorten the prompt or pick a larger model |
| the catalog is empty after a sync | the provider answered with no models | the gateway refuses to apply an empty catalog, so the previous one is still there. Check the provider |
| a model shows every capability as `UNKNOWN` | the provider publishes no metadata for it | state what you know in `providers.json` under `capabilities`; it is applied only where the model itself is silent |

Useful commands:

```bash
docker logs iacode-api --tail 50
curl -s http://localhost:18080/api/v1/gateway/health
curl -s http://localhost:18080/metrics | grep iacode_gateway
```

## Metrics

| Metric | What it answers |
|---|---|
| `iacode_gateway_requests_total` | how many requests, by provider, model, endpoint and outcome |
| `iacode_gateway_request_duration_seconds` | how long they took |
| `iacode_gateway_errors_total` | which error types are happening |
| `iacode_gateway_retries_total` | how much retrying is going on |
| `iacode_gateway_fallbacks_total` | how often a candidate had to be abandoned |
| `iacode_gateway_circuit_state` | which circuits are open |
| `iacode_gateway_provider_health` | which providers are reachable |
| `iacode_model_catalog_size` | how many models each provider offers |

No label carries a prompt, a credential or a user identifier.

## Adding a protocol adapter

An adapter translates between the gateway's contracts and one provider protocol. There are three:
`openai-chat-completions`, `openai-responses` and `anthropic-messages`.

1. Add a module under `services/model-gateway/src/iacode_model_gateway/protocols/`.
2. Implement `ProtocolAdapter`: build the `HttpCall` for a request, parse a completion, decode a
   stream chunk, parse a catalog entry, and classify an error body.
3. **Perform no I/O.** An adapter is pure translation; `HttpModelProvider` is the only thing in the
   package that opens a socket. That is what makes every adapter testable without a network and
   what keeps a transport bug out of nine different files.
4. Register it in `protocols/__init__.py`.
5. Extend `services/model-gateway/tests/test_provider_contract.py`. The contract suite runs the
   same scenarios against every adapter — discovery, generation, streaming, usage, error
   normalisation, timeout, cancellation and tool-call normalisation — so a new adapter proves
   itself against the same bar the existing ones did.
6. Name it in `providers.json` under `adapter` and `protocols`.

Never invent a parameter the provider did not document. The Anthropic adapter, for example, refuses
to guess a reasoning budget: if it is not configured, it is not sent.

## Adding a provider

1. Add an entry to `.iacode/policies/providers.json` with a new `provider_id`, the adapter, and the
   **names** of its two environment variables.
2. Add those variables to `infra/compose/.env.example` with empty values, and to
   `infra/compose/docker-compose.yml` so the API container receives them.
3. Set the real values in `infra/compose/.env`.
4. `python scripts/iacode/stack.py up`, then synchronise.

The base URL is validated before use: it must be `http` or `https`, must carry no userinfo, query
or fragment, and plain `http` is refused for anything that is not loopback. No DNS is resolved
during validation — a configuration check that makes a network call is a configuration check that
fails when the network does.
