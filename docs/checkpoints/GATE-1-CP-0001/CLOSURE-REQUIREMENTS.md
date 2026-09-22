# Closure Requirements - GATE-1-CP-0001

Derived from the canonical sources listed below, before implementation. The expected set
is recomputed by `policies.expected_requirement_refs` and compared exactly with the
declared set, so a requirement cannot be dropped and the denominator cannot be reduced.

## Sources

- SOURCE A: docs/GATE-1-CHECKLIST.md, the canonical GATE-1 specification
- SOURCE B: docs/MILESTONE-VALIDATION.md, the milestone requirements of the audit
- SOURCE C: LESSON-PREFLIGHT.json, the lessons the engineering memory imposes

## Requirements

| ID | Source | Anchor | Mandatory | Implementation | Final | Description |
|---|---|---|---|---|---|---|
| `REQ-0001` | GATE_SPECIFICATION | `canonical:GATE-1#1.1` | yes | `COMPLETE` | `COMPLETE` | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. |
| `REQ-0002` | GATE_SPECIFICATION | `canonical:GATE-1#1.2` | yes | `COMPLETE` | `COMPLETE` | The closed mandatory gate registry carries every executable gate this Gate introduces. |
| `REQ-0003` | GATE_SPECIFICATION | `canonical:GATE-1#1.3` | yes | `COMPLETE` | `COMPLETE` | Every test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence. |
| `REQ-0004` | GATE_SPECIFICATION | `canonical:GATE-1#1.4` | yes | `COMPLETE` | `COMPLETE` | The internal Red Team battery of this Gate is executable, scoped to the Model Gateway, and records a null-mutation control. |
| `REQ-0005` | GATE_SPECIFICATION | `canonical:GATE-1#1.5` | yes | `COMPLETE` | `COMPLETE` | The reservation of the gateway directory is consumed by the Gate that owns it, and the scope registry keeps constraining every path still owned by a later Gate. |
| `REQ-0006` | GATE_SPECIFICATION | `canonical:GATE-1#1.6` | yes | `COMPLETE` | `COMPLETE` | One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack. |
| `REQ-0007` | GATE_SPECIFICATION | `canonical:GATE-1#2.1` | yes | `COMPLETE` | `COMPLETE` | The Model Gateway lives in the directory the Foundation reserved for it and is consumed in process, and the boundary decision is recorded rather than implied. |
| `REQ-0008` | GATE_SPECIFICATION | `canonical:GATE-1#2.2` | yes | `COMPLETE` | `COMPLETE` | No consumer outside the adapter layer names a provider-specific endpoint, payload field or product name. |
| `REQ-0009` | GATE_SPECIFICATION | `canonical:GATE-1#2.3` | yes | `COMPLETE` | `COMPLETE` | The gateway declares its persistence and clock ports and imports no application module, so the dependency points inward. |
| `REQ-0010` | GATE_SPECIFICATION | `canonical:GATE-1#2.4` | yes | `COMPLETE` | `COMPLETE` | No later-Gate capability — tool execution, agent lifecycle, sandboxing, retrieval, experience storage or training — is implemented, simulated or faked here. |
| `REQ-0011` | GATE_SPECIFICATION | `canonical:GATE-1#2.5` | yes | `COMPLETE` | `COMPLETE` | The gateway directory stops declaring itself reserved and describes what this Gate delivered. |
| `REQ-0012` | GATE_SPECIFICATION | `canonical:GATE-1#3.1` | yes | `COMPLETE` | `COMPLETE` | A canonical request carries correlation, messages, routing intent, required capabilities, sampling, output limits, streaming intent, tools, structured output and metadata, and is validated when it is built. |
| `REQ-0013` | GATE_SPECIFICATION | `canonical:GATE-1#3.2` | yes | `COMPLETE` | `COMPLETE` | The message contract expresses the system, developer, user, assistant and tool roles independently of any provider's vocabulary. |
| `REQ-0014` | GATE_SPECIFICATION | `canonical:GATE-1#3.3` | yes | `COMPLETE` | `COMPLETE` | The canonical response normalizes content, tool calls, finish reason, usage, latency, provider, model, endpoint, route and fallback chain, and the raw provider payload is never the public contract. |
| `REQ-0015` | GATE_SPECIFICATION | `canonical:GATE-1#3.4` | yes | `COMPLETE` | `COMPLETE` | Tool definitions and tool calls are normalized into internal types with identifier, name and arguments, and the gateway executes no tool. |
| `REQ-0016` | GATE_SPECIFICATION | `canonical:GATE-1#3.5` | yes | `COMPLETE` | `COMPLETE` | A tool call whose arguments are not valid JSON produces a normalized error instead of a partially parsed call. |
| `REQ-0017` | GATE_SPECIFICATION | `canonical:GATE-1#3.6` | yes | `COMPLETE` | `COMPLETE` | Structured output is requested only from a model whose capability is known, and a request that needs it is refused or routed elsewhere rather than sent hopefully. |
| `REQ-0018` | GATE_SPECIFICATION | `canonical:GATE-1#3.7` | yes | `COMPLETE` | `COMPLETE` | The contract carries an explicit version, so a consumer can detect an incompatible change instead of discovering one. |
| `REQ-0019` | GATE_SPECIFICATION | `canonical:GATE-1#4.1` | yes | `COMPLETE` | `COMPLETE` | A provider contract declares health, model discovery, generation and streaming, and is not shaped by any one provider. |
| `REQ-0020` | GATE_SPECIFICATION | `canonical:GATE-1#4.2` | yes | `COMPLETE` | `COMPLETE` | An OpenAI-compatible Chat Completions adapter builds the request, parses the response, parses the stream and maps the error. |
| `REQ-0021` | GATE_SPECIFICATION | `canonical:GATE-1#4.3` | yes | `COMPLETE` | `COMPLETE` | An OpenAI-compatible Responses adapter builds the request, parses the response, parses the stream and maps the error. |
| `REQ-0022` | GATE_SPECIFICATION | `canonical:GATE-1#4.4` | yes | `COMPLETE` | `COMPLETE` | An Anthropic-compatible Messages adapter builds the request, parses the response, parses the stream and maps the error. |
| `REQ-0023` | GATE_SPECIFICATION | `canonical:GATE-1#4.5` | yes | `COMPLETE` | `COMPLETE` | The protocol is selected from the capabilities and endpoints the catalog records, the shape of the request and the provider configuration, never assumed from a default path. |
| `REQ-0024` | GATE_SPECIFICATION | `canonical:GATE-1#4.6` | yes | `COMPLETE` | `COMPLETE` | A request that needs an endpoint the model does not declare is refused before it reaches the network. |
| `REQ-0025` | GATE_SPECIFICATION | `canonical:GATE-1#4.7` | yes | `COMPLETE` | `COMPLETE` | No fictitious provider is registered in the runtime configuration; the deterministic double exists only inside the test fixtures. |
| `REQ-0026` | GATE_SPECIFICATION | `canonical:GATE-1#5.1` | yes | `COMPLETE` | `COMPLETE` | Provider configuration is versionable and carries no credential value: an identifier, an adapter, an enabled flag, a base URL reference, the name of the secret variable, the discovery endpoint and the protocols supported. |
| `REQ-0027` | GATE_SPECIFICATION | `canonical:GATE-1#5.2` | yes | `COMPLETE` | `COMPLETE` | The provider registry persists operational metadata — adapter, enabled state, health, last check and catalog state — and never a credential. |
| `REQ-0028` | GATE_SPECIFICATION | `canonical:GATE-1#5.3` | yes | `COMPLETE` | `COMPLETE` | A credential is resolved from the environment at call time and reaches no database row, response body, log record, metric label or catalog record. |
| `REQ-0029` | GATE_SPECIFICATION | `canonical:GATE-1#5.4` | yes | `COMPLETE` | `COMPLETE` | Every configuration key this Gate declares is read by the implementation. |
| `REQ-0030` | GATE_SPECIFICATION | `canonical:GATE-1#5.5` | yes | `COMPLETE` | `COMPLETE` | A provider base URL is validated: HTTPS for a remote provider, plain HTTP only for a loopback address, and never user information embedded in the URL. |
| `REQ-0031` | GATE_SPECIFICATION | `canonical:GATE-1#5.6` | yes | `COMPLETE` | `COMPLETE` | A provider address can never be supplied by an inference request; it comes from administrative configuration alone. |
| `REQ-0032` | GATE_SPECIFICATION | `canonical:GATE-1#6.1` | yes | `COMPLETE` | `COMPLETE` | The catalog is discovered from the provider API, and no list written by hand is treated as authoritative. |
| `REQ-0033` | GATE_SPECIFICATION | `canonical:GATE-1#6.2` | yes | `COMPLETE` | `COMPLETE` | A normalized model record carries the provider model identifier, display name, family, context window, maximum output tokens, supported endpoints, streaming, vision, tools, structured output, reasoning levels, active state, raw metadata and the synchronization instant. |
| `REQ-0034` | GATE_SPECIFICATION | `canonical:GATE-1#6.3` | yes | `COMPLETE` | `COMPLETE` | An absent capability stays unknown and is never normalized into a negative answer. |
| `REQ-0035` | GATE_SPECIFICATION | `canonical:GATE-1#6.4` | yes | `COMPLETE` | `COMPLETE` | Every capability records where it came from: provider metadata, manual configuration or observation, and never inference from a model's name. |
| `REQ-0036` | GATE_SPECIFICATION | `canonical:GATE-1#6.5` | yes | `COMPLETE` | `COMPLETE` | Synchronization is idempotent: running it twice over the same provider answer changes nothing the second time. |
| `REQ-0037` | GATE_SPECIFICATION | `canonical:GATE-1#6.6` | yes | `COMPLETE` | `COMPLETE` | A model that disappears from the provider answer is deactivated rather than destroyed, so the calls recorded against it stay readable. |
| `REQ-0038` | GATE_SPECIFICATION | `canonical:GATE-1#6.7` | yes | `COMPLETE` | `COMPLETE` | A partial, invalid or failed synchronization leaves the previous catalog usable: the answer is validated and normalized before anything is committed. |
| `REQ-0039` | GATE_SPECIFICATION | `canonical:GATE-1#6.8` | yes | `COMPLETE` | `COMPLETE` | Model identity is the provider together with the provider's own model identifier, so two providers exposing the same name do not collide. |
| `REQ-0040` | GATE_SPECIFICATION | `canonical:GATE-1#6.9` | yes | `COMPLETE` | `COMPLETE` | Routing reads normalized fields; the raw provider metadata is kept for diagnosis and is never the thing a decision depends on. |
| `REQ-0041` | GATE_SPECIFICATION | `canonical:GATE-1#7.1` | yes | `COMPLETE` | `COMPLETE` | The router is deterministic and applies a documented order: validate, explicit override, candidates, capability filter, context filter, route policy, configured priority, execution, fallback. |
| `REQ-0042` | GATE_SPECIFICATION | `canonical:GATE-1#7.2` | yes | `COMPLETE` | `COMPLETE` | An explicit model is honored when the policy allows it and is refused, rather than silently replaced, when it cannot serve the request. |
| `REQ-0043` | GATE_SPECIFICATION | `canonical:GATE-1#7.3` | yes | `COMPLETE` | `COMPLETE` | A default model is configurable, and a request with no model and no usable default fails with a clear error instead of an arbitrary choice. |
| `REQ-0044` | GATE_SPECIFICATION | `canonical:GATE-1#7.4` | yes | `COMPLETE` | `COMPLETE` | Required capabilities eliminate candidates that cannot satisfy them, and an unknown capability is refused unless the policy explicitly allows it. |
| `REQ-0045` | GATE_SPECIFICATION | `canonical:GATE-1#7.5` | yes | `COMPLETE` | `COMPLETE` | The gateway never knowingly sends a request larger than the context window it knows about, and an estimated token count is labelled an estimate rather than reported as exact. |
| `REQ-0046` | GATE_SPECIFICATION | `canonical:GATE-1#7.6` | yes | `COMPLETE` | `COMPLETE` | A reasoning effort is validated against the levels the model or the provider declares, and an incompatible level produces a fallback or an explicit error rather than a silent send. |
| `REQ-0047` | GATE_SPECIFICATION | `canonical:GATE-1#7.7` | yes | `COMPLETE` | `COMPLETE` | Route aliases are configuration, not built-in preference, and the system claims no empirical superiority for any of them. |
| `REQ-0048` | GATE_SPECIFICATION | `canonical:GATE-1#7.8` | yes | `COMPLETE` | `COMPLETE` | No model quality score, benchmark result or comparative claim is invented anywhere in this Gate. |
| `REQ-0049` | GATE_SPECIFICATION | `canonical:GATE-1#7.9` | yes | `COMPLETE` | `COMPLETE` | Every routing result carries a short structured explanation of the decision, and never a model's private reasoning. |
| `REQ-0050` | GATE_SPECIFICATION | `canonical:GATE-1#7.10` | yes | `COMPLETE` | `COMPLETE` | A disabled provider and an inactive model are never selected. |
| `REQ-0051` | GATE_SPECIFICATION | `canonical:GATE-1#8.1` | yes | `COMPLETE` | `COMPLETE` | An internal error taxonomy distinguishes authentication, authorization, rate limiting, unknown model, invalid request, context limit, provider unavailability, provider timeout, transient and permanent provider failure, an open circuit, cancellation and an internal gateway failure, and every adapter maps onto it. |
| `REQ-0052` | GATE_SPECIFICATION | `canonical:GATE-1#8.2` | yes | `COMPLETE` | `COMPLETE` | Timeouts are configurable, connect and read are separated, and no provider call can hang without bound. |
| `REQ-0053` | GATE_SPECIFICATION | `canonical:GATE-1#8.3` | yes | `COMPLETE` | `COMPLETE` | A retry happens only for an error class a retry can resolve, and never for authentication, authorization, an invalid request, an unknown model, an invalid schema or a context limit. |
| `REQ-0054` | GATE_SPECIFICATION | `canonical:GATE-1#8.4` | yes | `COMPLETE` | `COMPLETE` | A provider's `Retry-After` is honored within a configured bound, and an unreasonably long wait is refused rather than obeyed. |
| `REQ-0055` | GATE_SPECIFICATION | `canonical:GATE-1#8.5` | yes | `COMPLETE` | `COMPLETE` | Backoff is exponential with jitter, and the test suite controls time instead of waiting for it. |
| `REQ-0056` | GATE_SPECIFICATION | `canonical:GATE-1#8.6` | yes | `COMPLETE` | `COMPLETE` | A circuit breaker moves between closed, open and half-open per provider and per provider and model, from external configuration. |
| `REQ-0057` | GATE_SPECIFICATION | `canonical:GATE-1#8.7` | yes | `COMPLETE` | `COMPLETE` | The fallback chain is bounded, never repeats a candidate, cannot loop, and the chain that was used is recorded. |
| `REQ-0058` | GATE_SPECIFICATION | `canonical:GATE-1#8.8` | yes | `COMPLETE` | `COMPLETE` | Fallback happens only for the error classes another candidate could resolve, and an invalid request is not retried against a second model. |
| `REQ-0059` | GATE_SPECIFICATION | `canonical:GATE-1#8.9` | yes | `COMPLETE` | `COMPLETE` | A consumer that cancels interrupts the upstream call and the attempt is recorded as cancelled. |
| `REQ-0060` | GATE_SPECIFICATION | `canonical:GATE-1#8.10` | yes | `COMPLETE` | `COMPLETE` | Request limits are configurable and enforced: payload size, message count, tool count, output tokens and fallback depth. |
| `REQ-0061` | GATE_SPECIFICATION | `canonical:GATE-1#8.11` | yes | `COMPLETE` | `COMPLETE` | A provider response larger than the configured bound is refused instead of being read into memory without limit. |
| `REQ-0062` | GATE_SPECIFICATION | `canonical:GATE-1#8.12` | yes | `COMPLETE` | `COMPLETE` | An unavailable provider never makes the Foundation liveness endpoint fail; it is visible in the gateway's own health instead. |
| `REQ-0063` | GATE_SPECIFICATION | `canonical:GATE-1#9.1` | yes | `COMPLETE` | `COMPLETE` | Streaming goes through the same router and the same adapter abstraction as a non-streaming call, with no parallel architecture. |
| `REQ-0064` | GATE_SPECIFICATION | `canonical:GATE-1#9.2` | yes | `COMPLETE` | `COMPLETE` | Stream events are normalized into an envelope covering start, text delta, tool-call delta, usage, end and error. |
| `REQ-0065` | GATE_SPECIFICATION | `canonical:GATE-1#9.3` | yes | `COMPLETE` | `COMPLETE` | Automatic fallback is allowed only before the first content reaches the consumer; after it, the error is propagated and no second model continues the stream. |
| `REQ-0066` | GATE_SPECIFICATION | `canonical:GATE-1#9.4` | yes | `COMPLETE` | `COMPLETE` | A stream that fails after content ends with an explicit error event carrying the partial result, not with a silent completion. |
| `REQ-0067` | GATE_SPECIFICATION | `canonical:GATE-1#9.5` | yes | `COMPLETE` | `COMPLETE` | The API streams over Server-Sent Events and stops the upstream call when the client disconnects. |
| `REQ-0068` | GATE_SPECIFICATION | `canonical:GATE-1#10.1` | yes | `COMPLETE` | `COMPLETE` | Usage is normalized where the provider supplies it — input, output, total, cached and reasoning tokens — and a field the provider did not supply stays absent rather than being invented. |
| `REQ-0069` | GATE_SPECIFICATION | `canonical:GATE-1#10.2` | yes | `COMPLETE` | `COMPLETE` | Cost is absent unless pricing is configured, and zero is never used to mean unknown. |
| `REQ-0070` | GATE_SPECIFICATION | `canonical:GATE-1#10.3` | yes | `COMPLETE` | `COMPLETE` | Every attempt is recorded with its operational metadata: correlation, provider, model, endpoint, route, status, timestamps, latency, tokens, error type, retries and fallbacks. |
| `REQ-0071` | GATE_SPECIFICATION | `canonical:GATE-1#10.4` | yes | `COMPLETE` | `COMPLETE` | Prompts, messages and completions are not persisted by default; the debug capture is opt-in, redacted, documented and off in every shipped configuration. |
| `REQ-0072` | GATE_SPECIFICATION | `canonical:GATE-1#10.5` | yes | `COMPLETE` | `COMPLETE` | A request fingerprint may be stored for correlation, and its documentation states that a hash is not anonymization. |
| `REQ-0073` | GATE_SPECIFICATION | `canonical:GATE-1#10.6` | yes | `COMPLETE` | `COMPLETE` | No provider reasoning content is stored; only the reasoning token count a provider reports. |
| `REQ-0074` | GATE_SPECIFICATION | `canonical:GATE-1#10.7` | yes | `COMPLETE` | `COMPLETE` | Nothing this Gate persists becomes training data: the rights defaults of the provenance policy are preserved. |
| `REQ-0075` | GATE_SPECIFICATION | `canonical:GATE-1#11.1` | yes | `COMPLETE` | `COMPLETE` | The gateway exposes request, duration, error, retry, fallback, circuit state, provider health and catalog size metrics through the existing Prometheus endpoint. |
| `REQ-0076` | GATE_SPECIFICATION | `canonical:GATE-1#11.2` | yes | `COMPLETE` | `COMPLETE` | No metric label carries a prompt, a completion, a credential or an unbounded value. |
| `REQ-0077` | GATE_SPECIFICATION | `canonical:GATE-1#11.3` | yes | `COMPLETE` | `COMPLETE` | Structured logs carry the correlation and request identifiers, the provider, the model, the route, the attempt, the fallback index, the latency, the status and the error type where each is known. |
| `REQ-0078` | GATE_SPECIFICATION | `canonical:GATE-1#11.4` | yes | `COMPLETE` | `COMPLETE` | An authorization header, an API key, a full prompt and a full response are never written to a log. |
| `REQ-0079` | GATE_SPECIFICATION | `canonical:GATE-1#11.5` | yes | `COMPLETE` | `COMPLETE` | A correlation identifier propagates from the HTTP request through every provider attempt to the persisted record, so one call is traceable end to end. |
| `REQ-0080` | GATE_SPECIFICATION | `canonical:GATE-1#12.1` | yes | `COMPLETE` | `COMPLETE` | The gateway API is versioned and documented in the OpenAPI document. |
| `REQ-0081` | GATE_SPECIFICATION | `canonical:GATE-1#12.2` | yes | `COMPLETE` | `COMPLETE` | The provider listing returns safe metadata only and never a credential, an authorization header or a secret value. |
| `REQ-0082` | GATE_SPECIFICATION | `canonical:GATE-1#12.3` | yes | `COMPLETE` | `COMPLETE` | The model listing filters by provider, by active state and by capability. |
| `REQ-0083` | GATE_SPECIFICATION | `canonical:GATE-1#12.4` | yes | `COMPLETE` | `COMPLETE` | The synchronization endpoint reports what was added, updated, deactivated, unchanged and what failed, without exposing a provider secret. |
| `REQ-0084` | GATE_SPECIFICATION | `canonical:GATE-1#12.5` | yes | `COMPLETE` | `COMPLETE` | The inference endpoint returns the normalized response, the route information, the usage and the request identifier, and never a stack trace. |
| `REQ-0085` | GATE_SPECIFICATION | `canonical:GATE-1#12.6` | yes | `COMPLETE` | `COMPLETE` | The gateway health endpoint separates the process from the external provider, so an unreachable provider is reported without claiming the service is down. |
| `REQ-0086` | GATE_SPECIFICATION | `canonical:GATE-1#13.1` | yes | `COMPLETE` | `COMPLETE` | A Model Gateway page shows the provider status, the model count, the last synchronization and the model list with its capabilities. |
| `REQ-0087` | GATE_SPECIFICATION | `canonical:GATE-1#13.2` | yes | `COMPLETE` | `COMPLETE` | A minimal playground sends a prompt with a route or a model and an optional reasoning effort, and shows the chosen model, the provider, the answer, the latency and the usage when it exists. |
| `REQ-0088` | GATE_SPECIFICATION | `canonical:GATE-1#13.3` | yes | `COMPLETE` | `COMPLETE` | No provider credential reaches the browser: the page calls the IACode backend and nothing else. |
| `REQ-0089` | GATE_SPECIFICATION | `canonical:GATE-1#13.4` | yes | `COMPLETE` | `COMPLETE` | No conversation persistence, chat history, persona, agent interface or tool execution is added to the frontend. |
| `REQ-0090` | GATE_SPECIFICATION | `canonical:GATE-1#13.5` | yes | `COMPLETE` | `COMPLETE` | The frontend suite covers the new page and its service, runs headless and is part of the verification command. |
| `REQ-0091` | GATE_SPECIFICATION | `canonical:GATE-1#14.1` | yes | `COMPLETE` | `COMPLETE` | A real catalog synchronization runs against the configured provider API, parses the answer, normalizes it, persists it and repeats without changing anything. |
| `REQ-0092` | GATE_SPECIFICATION | `canonical:GATE-1#14.2` | yes | `COMPLETE` | `COMPLETE` | A real non-streaming inference against the explicitly configured smoke model returns the expected text through the normalized response. |
| `REQ-0093` | GATE_SPECIFICATION | `canonical:GATE-1#14.3` | yes | `COMPLETE` | `COMPLETE` | A real streaming inference produces a start, at least one delta and an end, with no duplicated content. |
| `REQ-0094` | GATE_SPECIFICATION | `canonical:GATE-1#14.4` | yes | `COMPLETE` | `COMPLETE` | The configured smoke model is never silently substituted: its absence from the discovered catalog fails the check. |
| `REQ-0095` | GATE_SPECIFICATION | `canonical:GATE-1#14.5` | yes | `COMPLETE` | `COMPLETE` | The live checks are minimal: a short prompt, a small output cap, no repetition, no deliberate rate limiting and no repeated authentication failure against the real provider. |
| `REQ-0096` | GATE_SPECIFICATION | `canonical:GATE-1#14.6` | yes | `COMPLETE` | `COMPLETE` | The live inference produced a persisted record carrying the provider, the model, the status, the latency and the usage the provider supplied, and carrying no prompt. |
| `REQ-0097` | GATE_SPECIFICATION | `canonical:GATE-1#14.7` | yes | `COMPLETE` | `COMPLETE` | The observability stack observed the live gateway request. |
| `REQ-0098` | GATE_SPECIFICATION | `canonical:GATE-1#14.8` | yes | `COMPLETE` | `COMPLETE` | Without a configured provider credential the live validation fails loudly and the Gate is blocked, and no result is claimed that was not executed. |
| `REQ-0099` | GATE_SPECIFICATION | `canonical:GATE-1#15.1` | yes | `COMPLETE` | `COMPLETE` | A provider contract suite proves discovery, generation, streaming, usage, error normalization, timeout, cancellation and tool-call normalization for every adapter. |
| `REQ-0100` | GATE_SPECIFICATION | `canonical:GATE-1#15.2` | yes | `COMPLETE` | `COMPLETE` | The catalog suite covers a new model, changed metadata, a removed model, a duplicate, invalid metadata, an unknown capability, a failed transaction and a repeated synchronization. |
| `REQ-0101` | GATE_SPECIFICATION | `canonical:GATE-1#15.3` | yes | `COMPLETE` | `COMPLETE` | The routing suite covers an explicit model, the default model, capability filtering, an unknown required capability, a disabled provider, an inactive model, an insufficient context window, route priority, fallback order and fallback exhaustion. |
| `REQ-0102` | GATE_SPECIFICATION | `canonical:GATE-1#15.4` | yes | `COMPLETE` | `COMPLETE` | The retry suite proves which classes are retried — rate limiting, server failure, timeout, connection reset — and which are not: authentication, invalid request and context limit. |
| `REQ-0103` | GATE_SPECIFICATION | `canonical:GATE-1#15.5` | yes | `COMPLETE` | `COMPLETE` | The circuit breaker suite covers the threshold, the open state, fast failure, the cooldown, the half-open probe, recovery and reopening, without waiting in real time. |
| `REQ-0104` | GATE_SPECIFICATION | `canonical:GATE-1#15.6` | yes | `COMPLETE` | `COMPLETE` | The streaming suite covers a normal stream, an empty stream, a failure before the first delta, a failure after the first delta, consumer cancellation, usage at the end and a tool-call delta. |
| `REQ-0105` | GATE_SPECIFICATION | `canonical:GATE-1#15.7` | yes | `COMPLETE` | `COMPLETE` | A test proves that two models' output can never be concatenated into one stream. |
| `REQ-0106` | GATE_SPECIFICATION | `canonical:GATE-1#15.8` | yes | `COMPLETE` | `COMPLETE` | The structured-output suite proves that an incapable candidate is rejected and that a capable one receives the right configuration. |
| `REQ-0107` | GATE_SPECIFICATION | `canonical:GATE-1#15.9` | yes | `COMPLETE` | `COMPLETE` | The secret suite proves that a credential appears in no log, no exception, no HTTP response, no persisted record, no metric and no catalog metadata. |
| `REQ-0108` | GATE_SPECIFICATION | `canonical:GATE-1#15.10` | yes | `COMPLETE` | `COMPLETE` | Provider unavailability, an invalid credential and rate limiting are exercised with fixtures rather than against the real provider. |
| `REQ-0109` | GATE_SPECIFICATION | `canonical:GATE-1#15.11` | yes | `COMPLETE` | `COMPLETE` | The deterministic provider double exists only under the test fixtures and cannot be reached from a runtime path. |
| `REQ-0110` | GATE_SPECIFICATION | `canonical:GATE-1#16.1` | yes | `COMPLETE` | `COMPLETE` | The schema change of this Gate is a new migration, and no migration of the previous Gate is edited. |
| `REQ-0111` | GATE_SPECIFICATION | `canonical:GATE-1#16.2` | yes | `COMPLETE` | `COMPLETE` | Every migration runs from zero against an empty database and produces the declared schema. |
| `REQ-0112` | GATE_SPECIFICATION | `canonical:GATE-1#16.3` | yes | `COMPLETE` | `COMPLETE` | A database created by the previous Gate upgrades without loss. |
| `REQ-0113` | GATE_SPECIFICATION | `canonical:GATE-1#16.4` | yes | `COMPLETE` | `COMPLETE` | The Foundation endpoints, the backup and restore procedure, the restart behaviour and the observability stack do not regress. |
| `REQ-0114` | GATE_SPECIFICATION | `canonical:GATE-1#17.1` | yes | `COMPLETE` | `COMPLETE` | An operational runbook documents provider configuration, the variables, synchronization, listing, inference, streaming, fallback, troubleshooting, the live smoke and how to add an adapter. |
| `REQ-0115` | GATE_SPECIFICATION | `canonical:GATE-1#17.2` | yes | `COMPLETE` | `COMPLETE` | The architecture document describes the gateway boundary, what crosses it and what is deliberately absent. |
| `REQ-0116` | GATE_SPECIFICATION | `canonical:GATE-1#17.3` | yes | `COMPLETE` | `COMPLETE` | The entry documentation and the development guide describe what exists after this Gate and how to run it. |
| `REQ-0117` | GATE_SPECIFICATION | `canonical:GATE-1#17.4` | yes | `COMPLETE` | `COMPLETE` | Every dependency and version this Gate pins is recorded in the one place that records versions. |
| `REQ-0118` | GATE_SPECIFICATION | `canonical:GATE-1#17.5` | yes | `COMPLETE` | `COMPLETE` | The API examples are sanitized and carry no real token. |
| `REQ-0119` | GATE_SPECIFICATION | `canonical:GATE-1#17.6` | yes | `COMPLETE` | `COMPLETE` | Every structural decision of this Gate that is not already recorded becomes an ADR, and no ADR duplicates an existing decision. |
| `REQ-0120` | GATE_SPECIFICATION | `canonical:GATE-1#18.1` | yes | `COMPLETE` | `COMPLETE` | The entry contract and the plan describe the current Gate and its status truthfully. |
| `REQ-0121` | GATE_SPECIFICATION | `canonical:GATE-1#18.2` | yes | `COMPLETE` | `COMPLETE` | The Gate produces a retrospective from the canonical template. |
| `REQ-0122` | GATE_SPECIFICATION | `canonical:GATE-1#18.3` | yes | `COMPLETE` | `COMPLETE` | The Gate closes on the project's own controls and claims no independent, fresh-session or cross-tool verdict. |
| `LESSON-REQ-0001` | LESSON | `lesson:LSN-0001` | yes | `COMPLETE` | `COMPLETE` | Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag |
| `LESSON-REQ-0002` | LESSON | `lesson:LSN-0002` | yes | `COMPLETE` | `COMPLETE` | Verify a file inventory must be recomputed from the repository, never trusted as an assertion |
| `LESSON-REQ-0003` | LESSON | `lesson:LSN-0003` | yes | `COMPLETE` | `COMPLETE` | Verify every operation attempt must be auditable, including a refusal decided before execution |
| `LESSON-REQ-0004` | LESSON | `lesson:LSN-0004` | yes | `COMPLETE` | `COMPLETE` | Verify a checkpoint may never claim readiness while it also claims to be blocked |
| `LESSON-REQ-0005` | LESSON | `lesson:LSN-0005` | yes | `COMPLETE` | `COMPLETE` | Verify a PASS requires evidence that can be executed or resolved, not a statement |
| `LESSON-REQ-0006` | LESSON | `lesson:LSN-0006` | yes | `COMPLETE` | `COMPLETE` | Verify the repository must be self-contained; a specification may not live outside it |
| `LESSON-REQ-0007` | LESSON | `lesson:LSN-0007` | yes | `COMPLETE` | `COMPLETE` | Verify independent validation cannot be declared by the run that did the work |
| `LESSON-REQ-0008` | LESSON | `lesson:LSN-0008` | yes | `COMPLETE` | `COMPLETE` | Verify requirement completeness must be total and evidence-backed before handoff |
| `LESSON-REQ-0009` | LESSON | `lesson:LSN-0009` | yes | `COMPLETE` | `COMPLETE` | Verify a red gate requires rework, never a waiver, and never a weakened check |
| `LESSON-REQ-0010` | LESSON | `lesson:LSN-0010` | yes | `COMPLETE` | `COMPLETE` | Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable |
| `LESSON-REQ-0011` | LESSON | `lesson:LSN-0011` | yes | `COMPLETE` | `COMPLETE` | Verify a control over a checkpoint's own evidence must be scoped to the moment it matters |
| `LESSON-REQ-0012` | LESSON | `lesson:LSN-0012` | yes | `COMPLETE` | `COMPLETE` | Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them |
| `LESSON-REQ-0013` | LESSON | `lesson:LSN-0013` | no | `COMPLETE` | `COMPLETE` | Verify an installed capability must be detected by resolved path, not by a bare command lookup |
| `LESSON-REQ-0014` | LESSON | `lesson:LSN-0014` | yes | `COMPLETE` | `COMPLETE` | Verify evidence must be recorded as it happens, not reconstructed at the end of a run |
| `LESSON-REQ-0015` | LESSON | `lesson:LSN-0015` | yes | `COMPLETE` | `COMPLETE` | Verify every positive terminal status needs one shared promotion invariant |
| `LESSON-REQ-0016` | LESSON | `lesson:LSN-0016` | yes | `COMPLETE` | `COMPLETE` | Verify a mandatory set must be closed by policy, never chosen by the caller |
| `LESSON-REQ-0017` | LESSON | `lesson:LSN-0017` | yes | `COMPLETE` | `COMPLETE` | Verify a completeness denominator must come from a source the delivery does not own |
| `LESSON-REQ-0018` | LESSON | `lesson:LSN-0018` | yes | `COMPLETE` | `COMPLETE` | Verify a structured reference must be resolved, not merely well typed |
| `LESSON-REQ-0019` | LESSON | `lesson:LSN-0019` | yes | `COMPLETE` | `COMPLETE` | Verify a derived artifact must carry a fingerprint of the inputs that produced it |
| `LESSON-REQ-0020` | LESSON | `lesson:LSN-0020` | yes | `COMPLETE` | `COMPLETE` | Verify evidence produced from a dirty tree needs immutable input identity |
| `LESSON-REQ-0021` | LESSON | `lesson:LSN-0021` | yes | `COMPLETE` | `COMPLETE` | Verify sealed history needs an anchor outside the content it describes |
| `LESSON-REQ-0022` | LESSON | `lesson:LSN-0022` | yes | `COMPLETE` | `COMPLETE` | Verify an authoritative count must be derived once, never maintained by hand twice |
| `LESSON-REQ-0023` | LESSON | `lesson:LSN-0023` | yes | `COMPLETE` | `COMPLETE` | Verify a lesson must cite a source that actually records the finding it claims |
| `LESSON-REQ-0024` | LESSON | `lesson:LSN-0024` | yes | `COMPLETE` | `COMPLETE` | Verify a control is finished only when its positive path has been executed, not only its refusals |
| `LESSON-REQ-0025` | LESSON | `lesson:LSN-0025` | yes | `COMPLETE` | `COMPLETE` | Verify a generic guardrail derives repository state instead of naming today's checkpoint |
| `LESSON-REQ-0026` | LESSON | `lesson:LSN-0026` | yes | `COMPLETE` | `COMPLETE` | Verify an adversarial battery without a null-mutation control proves nothing |
| `LESSON-REQ-0027` | LESSON | `lesson:LSN-0027` | yes | `COMPLETE` | `COMPLETE` | Verify a lesson's prose may record a residual limit but may never contradict its status |
| `LESSON-REQ-0028` | LESSON | `lesson:LSN-0028` | yes | `COMPLETE` | `COMPLETE` | Verify a configuration key that no code reads is a defect, not documentation |
| `LESSON-REQ-0029` | LESSON | `lesson:LSN-0029` | yes | `COMPLETE` | `COMPLETE` | Verify a required protocol transition must never turn a mandatory gate red |
| `LESSON-REQ-0030` | LESSON | `lesson:LSN-0031` | yes | `COMPLETE` | `COMPLETE` | Verify an empty applicable set is not a missing required set, and a control must tell them apart |
| `LESSON-REQ-0031` | LESSON | `lesson:LSN-0032` | yes | `COMPLETE` | `COMPLETE` | Verify a control written while one Gate was the only Gate stops being a control when the next one starts |
| `LESSON-REQ-0032` | LESSON | `lesson:LSN-0033` | yes | `COMPLETE` | `COMPLETE` | Verify a value bound in middleware is absent in the handlers that run outside it |
| `LESSON-REQ-0033` | LESSON | `lesson:LSN-0034` | yes | `COMPLETE` | `COMPLETE` | Verify re-deriving what the framework already computed diverges from the framework |
| `LESSON-REQ-0034` | LESSON | `lesson:LSN-0035` | yes | `COMPLETE` | `COMPLETE` | Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work |
| `LESSON-REQ-0035` | LESSON | `lesson:LSN-0036` | yes | `COMPLETE` | `COMPLETE` | Verify a gate that runs inside an image measures the image, not the source |
| `LESSON-REQ-0036` | LESSON | `lesson:LSN-0037` | yes | `COMPLETE` | `COMPLETE` | Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves |
| `LESSON-REQ-0037` | LESSON | `lesson:LSN-0038` | yes | `COMPLETE` | `COMPLETE` | Verify two representations of one concept in one module disagree, and the safer one loses |
| `LESSON-REQ-0038` | LESSON | `lesson:LSN-0039` | yes | `COMPLETE` | `COMPLETE` | Verify a test that writes to the operational database leaves production data behind |
| `LESSON-REQ-0039` | LESSON | `lesson:LSN-0040` | yes | `COMPLETE` | `COMPLETE` | Verify a control that judges sealed history only runs once a successor anchors it |

## Evidence

### REQ-0001 - canonical:GATE-1#1.1

- Source reference: docs/GATE-1-CHECKLIST.md row 1.1
- Description: A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row.
- Implementation: `file:.iacode/policies/canonical-requirements.json`
- Test: `test:Gate1CanonicalSpecificationTests`
- Negative test: _none_
- Documentation: `file:docs/GATE-1-CHECKLIST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0002 - canonical:GATE-1#1.2

- Source reference: docs/GATE-1-CHECKLIST.md row 1.2
- Description: The closed mandatory gate registry carries every executable gate this Gate introduces.
- Implementation: `file:.iacode/policies/quality-gates.json`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0003 - canonical:GATE-1#1.3

- Source reference: docs/GATE-1-CHECKLIST.md row 1.3
- Description: Every test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence.
- Implementation: `file:.iacode/policies/test-suites.json`
- Test: `test:test_gateway_suite_is_declared_and_discovered`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0004 - canonical:GATE-1#1.4

- Source reference: docs/GATE-1-CHECKLIST.md row 1.4
- Description: The internal Red Team battery of this Gate is executable, scoped to the Model Gateway, and records a null-mutation control.
- Implementation: `file:scripts/development-ledger/gate1_red_team.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0005 - canonical:GATE-1#1.5

- Source reference: docs/GATE-1-CHECKLIST.md row 1.5
- Description: The reservation of the gateway directory is consumed by the Gate that owns it, and the scope registry keeps constraining every path still owned by a later Gate.
- Implementation: `file:.iacode/policies/gate-scope.json`
- Test: `test:test_model_gateway_reservation_is_consumed_by_its_owner`
- Negative test: _none_
- Documentation: `file:services/model-gateway/README.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0006 - canonical:GATE-1#1.6

- Source reference: docs/GATE-1-CHECKLIST.md row 1.6
- Description: One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack.
- Implementation: `file:scripts/iacode/verify.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0007 - canonical:GATE-1#2.1

- Source reference: docs/GATE-1-CHECKLIST.md row 2.1
- Description: The Model Gateway lives in the directory the Foundation reserved for it and is consumed in process, and the boundary decision is recorded rather than implied.
- Implementation: _none_
- Test: `test:test_gateway_package_is_importable`
- Negative test: _none_
- Documentation: `file:docs/adr/ADR-0016-model-gateway-boundary.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0008 - canonical:GATE-1#2.2

- Source reference: docs/GATE-1-CHECKLIST.md row 2.2
- Description: No consumer outside the adapter layer names a provider-specific endpoint, payload field or product name.
- Implementation: _none_
- Test: `test:test_no_provider_specific_name_escapes_the_adapter_layer`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0009 - canonical:GATE-1#2.3

- Source reference: docs/GATE-1-CHECKLIST.md row 2.3
- Description: The gateway declares its persistence and clock ports and imports no application module, so the dependency points inward.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/ports.py`
- Test: `test:test_gateway_imports_no_application_module`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0010 - canonical:GATE-1#2.4

- Source reference: docs/GATE-1-CHECKLIST.md row 2.4
- Description: No later-Gate capability — tool execution, agent lifecycle, sandboxing, retrieval, experience storage or training — is implemented, simulated or faked here.
- Implementation: _none_
- Test: `test:test_no_future_gate_capability_is_implemented`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0011 - canonical:GATE-1#2.5

- Source reference: docs/GATE-1-CHECKLIST.md row 2.5
- Description: The gateway directory stops declaring itself reserved and describes what this Gate delivered.
- Implementation: _none_
- Test: `test:test_gateway_readme_describes_the_delivery`
- Negative test: _none_
- Documentation: `file:services/model-gateway/README.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0012 - canonical:GATE-1#3.1

- Source reference: docs/GATE-1-CHECKLIST.md row 3.1
- Description: A canonical request carries correlation, messages, routing intent, required capabilities, sampling, output limits, streaming intent, tools, structured output and metadata, and is validated when it is built.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/contracts.py`
- Test: `test:test_request_is_validated_when_it_is_built`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0013 - canonical:GATE-1#3.2

- Source reference: docs/GATE-1-CHECKLIST.md row 3.2
- Description: The message contract expresses the system, developer, user, assistant and tool roles independently of any provider's vocabulary.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/contracts.py`
- Test: `test:test_message_roles_are_provider_independent`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0014 - canonical:GATE-1#3.3

- Source reference: docs/GATE-1-CHECKLIST.md row 3.3
- Description: The canonical response normalizes content, tool calls, finish reason, usage, latency, provider, model, endpoint, route and fallback chain, and the raw provider payload is never the public contract.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/contracts.py`
- Test: `test:test_response_never_exposes_the_raw_provider_payload`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0015 - canonical:GATE-1#3.4

- Source reference: docs/GATE-1-CHECKLIST.md row 3.4
- Description: Tool definitions and tool calls are normalized into internal types with identifier, name and arguments, and the gateway executes no tool.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/contracts.py`
- Test: `test:test_gateway_normalises_a_tool_call_without_executing_it`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0016 - canonical:GATE-1#3.5

- Source reference: docs/GATE-1-CHECKLIST.md row 3.5
- Description: A tool call whose arguments are not valid JSON produces a normalized error instead of a partially parsed call.
- Implementation: _none_
- Test: `test:test_invalid_tool_arguments_produce_a_normalised_error`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0017 - canonical:GATE-1#3.6

- Source reference: docs/GATE-1-CHECKLIST.md row 3.6
- Description: Structured output is requested only from a model whose capability is known, and a request that needs it is refused or routed elsewhere rather than sent hopefully.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`
- Test: `test:test_structured_output_requires_a_capable_candidate`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0018 - canonical:GATE-1#3.7

- Source reference: docs/GATE-1-CHECKLIST.md row 3.7
- Description: The contract carries an explicit version, so a consumer can detect an incompatible change instead of discovering one.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/contracts.py`
- Test: `test:test_contract_version_is_declared`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0019 - canonical:GATE-1#4.1

- Source reference: docs/GATE-1-CHECKLIST.md row 4.1
- Description: A provider contract declares health, model discovery, generation and streaming, and is not shaped by any one provider.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/providers/base.py`
- Test: `test:test_provider_contract_is_not_coupled_to_one_provider`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0020 - canonical:GATE-1#4.2

- Source reference: docs/GATE-1-CHECKLIST.md row 4.2
- Description: An OpenAI-compatible Chat Completions adapter builds the request, parses the response, parses the stream and maps the error.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/protocols/openai_chat.py`
- Test: `test:OpenAiChatProtocolTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0021 - canonical:GATE-1#4.3

- Source reference: docs/GATE-1-CHECKLIST.md row 4.3
- Description: An OpenAI-compatible Responses adapter builds the request, parses the response, parses the stream and maps the error.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/protocols/openai_responses.py`
- Test: `test:OpenAiResponsesProtocolTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0022 - canonical:GATE-1#4.4

- Source reference: docs/GATE-1-CHECKLIST.md row 4.4
- Description: An Anthropic-compatible Messages adapter builds the request, parses the response, parses the stream and maps the error.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/protocols/anthropic_messages.py`
- Test: `test:AnthropicMessagesProtocolTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0023 - canonical:GATE-1#4.5

- Source reference: docs/GATE-1-CHECKLIST.md row 4.5
- Description: The protocol is selected from the capabilities and endpoints the catalog records, the shape of the request and the provider configuration, never assumed from a default path.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/protocols/selection.py`
- Test: `test:test_endpoint_selection_reads_the_declared_endpoints`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0024 - canonical:GATE-1#4.6

- Source reference: docs/GATE-1-CHECKLIST.md row 4.6
- Description: A request that needs an endpoint the model does not declare is refused before it reaches the network.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/protocols/selection.py`
- Test: `test:test_unsupported_endpoint_is_refused_before_the_call`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0025 - canonical:GATE-1#4.7

- Source reference: docs/GATE-1-CHECKLIST.md row 4.7
- Description: No fictitious provider is registered in the runtime configuration; the deterministic double exists only inside the test fixtures.
- Implementation: `file:.iacode/policies/providers.json`
- Test: `test:test_no_fake_provider_is_registered_at_runtime`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0026 - canonical:GATE-1#5.1

- Source reference: docs/GATE-1-CHECKLIST.md row 5.1
- Description: Provider configuration is versionable and carries no credential value: an identifier, an adapter, an enabled flag, a base URL reference, the name of the secret variable, the discovery endpoint and the protocols supported.
- Implementation: `file:.iacode/policies/providers.json`
- Test: `test:test_provider_configuration_carries_no_credential`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0027 - canonical:GATE-1#5.2

- Source reference: docs/GATE-1-CHECKLIST.md row 5.2
- Description: The provider registry persists operational metadata — adapter, enabled state, health, last check and catalog state — and never a credential.
- Implementation: `file:apps/api/src/iacode_api/db/models.py`
- Test: `test:test_no_table_stores_a_credential`, `test:test_provider_registry_persists_operational_metadata`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0028 - canonical:GATE-1#5.3

- Source reference: docs/GATE-1-CHECKLIST.md row 5.3
- Description: A credential is resolved from the environment at call time and reaches no database row, response body, log record, metric label or catalog record.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/config.py`
- Test: `test:SecretContainmentTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0029 - canonical:GATE-1#5.4

- Source reference: docs/GATE-1-CHECKLIST.md row 5.4
- Description: Every configuration key this Gate declares is read by the implementation.
- Implementation: `file:apps/api/src/iacode_api/config.py`, `file:infra/compose/.env.example`
- Test: `test:test_every_declared_key_is_read_somewhere`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0030 - canonical:GATE-1#5.5

- Source reference: docs/GATE-1-CHECKLIST.md row 5.5
- Description: A provider base URL is validated: HTTPS for a remote provider, plain HTTP only for a loopback address, and never user information embedded in the URL.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/security/base_url.py`
- Test: `test:BaseUrlSafetyTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0031 - canonical:GATE-1#5.6

- Source reference: docs/GATE-1-CHECKLIST.md row 5.6
- Description: A provider address can never be supplied by an inference request; it comes from administrative configuration alone.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/contracts.py`, `file:apps/api/src/iacode_api/routes/gateway.py`
- Test: `test:test_request_cannot_supply_a_provider_address`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0032 - canonical:GATE-1#6.1

- Source reference: docs/GATE-1-CHECKLIST.md row 6.1
- Description: The catalog is discovered from the provider API, and no list written by hand is treated as authoritative.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py`
- Test: `test:test_catalog_comes_from_the_provider_api`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0033 - canonical:GATE-1#6.2

- Source reference: docs/GATE-1-CHECKLIST.md row 6.2
- Description: A normalized model record carries the provider model identifier, display name, family, context window, maximum output tokens, supported endpoints, streaming, vision, tools, structured output, reasoning levels, active state, raw metadata and the synchronization instant.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/catalog/normalize.py`
- Test: `test:test_normalised_model_carries_the_declared_fields`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0034 - canonical:GATE-1#6.3

- Source reference: docs/GATE-1-CHECKLIST.md row 6.3
- Description: An absent capability stays unknown and is never normalized into a negative answer.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/catalog/normalize.py`
- Test: `test:test_unknown_capability_is_not_turned_into_false`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0035 - canonical:GATE-1#6.4

- Source reference: docs/GATE-1-CHECKLIST.md row 6.4
- Description: Every capability records where it came from: provider metadata, manual configuration or observation, and never inference from a model's name.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/catalog/normalize.py`
- Test: `test:test_capability_provenance_is_recorded`, `test:test_capability_is_never_inferred_from_a_name`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0036 - canonical:GATE-1#6.5

- Source reference: docs/GATE-1-CHECKLIST.md row 6.5
- Description: Synchronization is idempotent: running it twice over the same provider answer changes nothing the second time.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py`
- Test: `test:test_sync_is_idempotent`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0037 - canonical:GATE-1#6.6

- Source reference: docs/GATE-1-CHECKLIST.md row 6.6
- Description: A model that disappears from the provider answer is deactivated rather than destroyed, so the calls recorded against it stay readable.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py`
- Test: `test:test_missing_model_is_deactivated_not_deleted`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0038 - canonical:GATE-1#6.7

- Source reference: docs/GATE-1-CHECKLIST.md row 6.7
- Description: A partial, invalid or failed synchronization leaves the previous catalog usable: the answer is validated and normalized before anything is committed.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py`
- Test: `test:test_failed_sync_preserves_the_previous_catalog`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0039 - canonical:GATE-1#6.8

- Source reference: docs/GATE-1-CHECKLIST.md row 6.8
- Description: Model identity is the provider together with the provider's own model identifier, so two providers exposing the same name do not collide.
- Implementation: `file:apps/api/src/iacode_api/db/models.py`, `file:services/model-gateway/src/iacode_model_gateway/contracts.py`
- Test: `test:test_same_model_id_in_two_providers_does_not_collide`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0040 - canonical:GATE-1#6.9

- Source reference: docs/GATE-1-CHECKLIST.md row 6.9
- Description: Routing reads normalized fields; the raw provider metadata is kept for diagnosis and is never the thing a decision depends on.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`
- Test: `test:test_routing_reads_normalised_fields_only`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0041 - canonical:GATE-1#7.1

- Source reference: docs/GATE-1-CHECKLIST.md row 7.1
- Description: The router is deterministic and applies a documented order: validate, explicit override, candidates, capability filter, context filter, route policy, configured priority, execution, fallback.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`
- Test: `test:test_router_is_deterministic`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0042 - canonical:GATE-1#7.2

- Source reference: docs/GATE-1-CHECKLIST.md row 7.2
- Description: An explicit model is honored when the policy allows it and is refused, rather than silently replaced, when it cannot serve the request.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`
- Test: `test:test_explicit_model_is_honoured_or_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0043 - canonical:GATE-1#7.3

- Source reference: docs/GATE-1-CHECKLIST.md row 7.3
- Description: A default model is configurable, and a request with no model and no usable default fails with a clear error instead of an arbitrary choice.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/config.py`
- Test: `test:test_missing_default_model_is_an_explicit_error`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0044 - canonical:GATE-1#7.4

- Source reference: docs/GATE-1-CHECKLIST.md row 7.4
- Description: Required capabilities eliminate candidates that cannot satisfy them, and an unknown capability is refused unless the policy explicitly allows it.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/policy.py`
- Test: `test:test_unknown_capability_is_rejected_by_default`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0045 - canonical:GATE-1#7.5

- Source reference: docs/GATE-1-CHECKLIST.md row 7.5
- Description: The gateway never knowingly sends a request larger than the context window it knows about, and an estimated token count is labelled an estimate rather than reported as exact.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/context.py`
- Test: `test:ContextWindowTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0046 - canonical:GATE-1#7.6

- Source reference: docs/GATE-1-CHECKLIST.md row 7.6
- Description: A reasoning effort is validated against the levels the model or the provider declares, and an incompatible level produces a fallback or an explicit error rather than a silent send.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/policy.py`
- Test: `test:test_incompatible_reasoning_effort_is_not_sent_silently`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0047 - canonical:GATE-1#7.7

- Source reference: docs/GATE-1-CHECKLIST.md row 7.7
- Description: Route aliases are configuration, not built-in preference, and the system claims no empirical superiority for any of them.
- Implementation: `file:.iacode/policies/model-routes.json`
- Test: `test:test_route_aliases_come_from_configuration`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0048 - canonical:GATE-1#7.8

- Source reference: docs/GATE-1-CHECKLIST.md row 7.8
- Description: No model quality score, benchmark result or comparative claim is invented anywhere in this Gate.
- Implementation: _none_
- Test: `test:test_no_model_quality_claim_is_hardcoded`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0049 - canonical:GATE-1#7.9

- Source reference: docs/GATE-1-CHECKLIST.md row 7.9
- Description: Every routing result carries a short structured explanation of the decision, and never a model's private reasoning.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`
- Test: `test:test_route_explanation_is_structured_and_short`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0050 - canonical:GATE-1#7.10

- Source reference: docs/GATE-1-CHECKLIST.md row 7.10
- Description: A disabled provider and an inactive model are never selected.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`
- Test: `test:test_disabled_provider_and_inactive_model_are_excluded`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0051 - canonical:GATE-1#8.1

- Source reference: docs/GATE-1-CHECKLIST.md row 8.1
- Description: An internal error taxonomy distinguishes authentication, authorization, rate limiting, unknown model, invalid request, context limit, provider unavailability, provider timeout, transient and permanent provider failure, an open circuit, cancellation and an internal gateway failure, and every adapter maps onto it.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/errors.py`
- Test: `test:ErrorTaxonomyTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0052 - canonical:GATE-1#8.2

- Source reference: docs/GATE-1-CHECKLIST.md row 8.2
- Description: Timeouts are configurable, connect and read are separated, and no provider call can hang without bound.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/config.py`, `file:services/model-gateway/src/iacode_model_gateway/providers/http_provider.py`
- Test: `test:test_no_call_is_unbounded`, `test:test_timeout_is_normalised`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0053 - canonical:GATE-1#8.3

- Source reference: docs/GATE-1-CHECKLIST.md row 8.3
- Description: A retry happens only for an error class a retry can resolve, and never for authentication, authorization, an invalid request, an unknown model, an invalid schema or a context limit.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/resilience/retry.py`
- Test: `test:RetryClassificationTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0054 - canonical:GATE-1#8.4

- Source reference: docs/GATE-1-CHECKLIST.md row 8.4
- Description: A provider's `Retry-After` is honored within a configured bound, and an unreasonably long wait is refused rather than obeyed.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/resilience/retry.py`
- Test: `test:test_retry_after_is_bounded`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0055 - canonical:GATE-1#8.5

- Source reference: docs/GATE-1-CHECKLIST.md row 8.5
- Description: Backoff is exponential with jitter, and the test suite controls time instead of waiting for it.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/resilience/retry.py`
- Test: `test:test_backoff_is_exponential_with_jitter`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0056 - canonical:GATE-1#8.6

- Source reference: docs/GATE-1-CHECKLIST.md row 8.6
- Description: A circuit breaker moves between closed, open and half-open per provider and per provider and model, from external configuration.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/resilience/circuit.py`
- Test: `test:CircuitBreakerTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0057 - canonical:GATE-1#8.7

- Source reference: docs/GATE-1-CHECKLIST.md row 8.7
- Description: The fallback chain is bounded, never repeats a candidate, cannot loop, and the chain that was used is recorded.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`
- Test: `test:test_fallback_chain_is_bounded_and_recorded`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0058 - canonical:GATE-1#8.8

- Source reference: docs/GATE-1-CHECKLIST.md row 8.8
- Description: Fallback happens only for the error classes another candidate could resolve, and an invalid request is not retried against a second model.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/routing/policy.py`
- Test: `test:FallbackSemanticsTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0059 - canonical:GATE-1#8.9

- Source reference: docs/GATE-1-CHECKLIST.md row 8.9
- Description: A consumer that cancels interrupts the upstream call and the attempt is recorded as cancelled.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/gateway.py`
- Test: `test:test_cancellation_stops_the_upstream_call`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0060 - canonical:GATE-1#8.10

- Source reference: docs/GATE-1-CHECKLIST.md row 8.10
- Description: Request limits are configurable and enforced: payload size, message count, tool count, output tokens and fallback depth.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/resilience/limits.py`
- Test: `test:RequestLimitTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0061 - canonical:GATE-1#8.11

- Source reference: docs/GATE-1-CHECKLIST.md row 8.11
- Description: A provider response larger than the configured bound is refused instead of being read into memory without limit.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/providers/http_provider.py`
- Test: `test:test_oversized_provider_response_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0062 - canonical:GATE-1#8.12

- Source reference: docs/GATE-1-CHECKLIST.md row 8.12
- Description: An unavailable provider never makes the Foundation liveness endpoint fail; it is visible in the gateway's own health instead.
- Implementation: `file:apps/api/src/iacode_api/routes/gateway.py`
- Test: `test:test_provider_outage_does_not_affect_process_health`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0063 - canonical:GATE-1#9.1

- Source reference: docs/GATE-1-CHECKLIST.md row 9.1
- Description: Streaming goes through the same router and the same adapter abstraction as a non-streaming call, with no parallel architecture.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/gateway.py`
- Test: `test:test_streaming_uses_the_same_router`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0064 - canonical:GATE-1#9.2

- Source reference: docs/GATE-1-CHECKLIST.md row 9.2
- Description: Stream events are normalized into an envelope covering start, text delta, tool-call delta, usage, end and error.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/contracts.py`
- Test: `test:StreamEnvelopeTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0065 - canonical:GATE-1#9.3

- Source reference: docs/GATE-1-CHECKLIST.md row 9.3
- Description: Automatic fallback is allowed only before the first content reaches the consumer; after it, the error is propagated and no second model continues the stream.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/gateway.py`
- Test: `test:test_no_fallback_after_the_first_delivered_content`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0066 - canonical:GATE-1#9.4

- Source reference: docs/GATE-1-CHECKLIST.md row 9.4
- Description: A stream that fails after content ends with an explicit error event carrying the partial result, not with a silent completion.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/gateway.py`
- Test: `test:test_failure_after_content_ends_with_an_error_event`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0067 - canonical:GATE-1#9.5

- Source reference: docs/GATE-1-CHECKLIST.md row 9.5
- Description: The API streams over Server-Sent Events and stops the upstream call when the client disconnects.
- Implementation: `file:apps/api/src/iacode_api/routes/gateway.py`
- Test: `test:test_stream_endpoint_emits_sse_and_stops_on_disconnect`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0068 - canonical:GATE-1#10.1

- Source reference: docs/GATE-1-CHECKLIST.md row 10.1
- Description: Usage is normalized where the provider supplies it — input, output, total, cached and reasoning tokens — and a field the provider did not supply stays absent rather than being invented.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/catalog/normalize.py`
- Test: `test:UsageNormalisationTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0069 - canonical:GATE-1#10.2

- Source reference: docs/GATE-1-CHECKLIST.md row 10.2
- Description: Cost is absent unless pricing is configured, and zero is never used to mean unknown.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/pricing.py`
- Test: `test:test_unknown_cost_is_absent_not_zero`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0070 - canonical:GATE-1#10.3

- Source reference: docs/GATE-1-CHECKLIST.md row 10.3
- Description: Every attempt is recorded with its operational metadata: correlation, provider, model, endpoint, route, status, timestamps, latency, tokens, error type, retries and fallbacks.
- Implementation: `file:apps/api/src/iacode_api/gateway/store.py`
- Test: `test:test_model_call_records_the_operational_metadata`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0071 - canonical:GATE-1#10.4

- Source reference: docs/GATE-1-CHECKLIST.md row 10.4
- Description: Prompts, messages and completions are not persisted by default; the debug capture is opt-in, redacted, documented and off in every shipped configuration.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/config.py`, `file:apps/api/src/iacode_api/gateway/store.py`
- Test: `test:test_prompt_is_not_persisted_by_default`, `test:PromptCaptureTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0072 - canonical:GATE-1#10.5

- Source reference: docs/GATE-1-CHECKLIST.md row 10.5
- Description: A request fingerprint may be stored for correlation, and its documentation states that a hash is not anonymization.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/fingerprint.py`
- Test: `test:test_request_fingerprint_is_stable_and_carries_no_content`
- Negative test: _none_
- Documentation: `file:docs/runbooks/MODEL-GATEWAY.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0073 - canonical:GATE-1#10.6

- Source reference: docs/GATE-1-CHECKLIST.md row 10.6
- Description: No provider reasoning content is stored; only the reasoning token count a provider reports.
- Implementation: `file:apps/api/src/iacode_api/gateway/store.py`
- Test: `test:test_no_reasoning_content_is_persisted`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0074 - canonical:GATE-1#10.7

- Source reference: docs/GATE-1-CHECKLIST.md row 10.7
- Description: Nothing this Gate persists becomes training data: the rights defaults of the provenance policy are preserved.
- Implementation: _none_
- Test: `test:test_gate_one_records_no_training_eligible_data`
- Negative test: _none_
- Documentation: `file:.iacode/policies/training-data-policy.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0075 - canonical:GATE-1#11.1

- Source reference: docs/GATE-1-CHECKLIST.md row 11.1
- Description: The gateway exposes request, duration, error, retry, fallback, circuit state, provider health and catalog size metrics through the existing Prometheus endpoint.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/telemetry/metrics.py`
- Test: `test:GatewayMetricsTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0076 - canonical:GATE-1#11.2

- Source reference: docs/GATE-1-CHECKLIST.md row 11.2
- Description: No metric label carries a prompt, a completion, a credential or an unbounded value.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/telemetry/metrics.py`
- Test: `test:test_metric_labels_are_bounded_and_carry_no_content`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0077 - canonical:GATE-1#11.3

- Source reference: docs/GATE-1-CHECKLIST.md row 11.3
- Description: Structured logs carry the correlation and request identifiers, the provider, the model, the route, the attempt, the fallback index, the latency, the status and the error type where each is known.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/telemetry/logs.py`
- Test: `test:test_gateway_log_contract`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0078 - canonical:GATE-1#11.4

- Source reference: docs/GATE-1-CHECKLIST.md row 11.4
- Description: An authorization header, an API key, a full prompt and a full response are never written to a log.
- Implementation: `file:services/model-gateway/src/iacode_model_gateway/telemetry/logs.py`
- Test: `test:SecretContainmentTests`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0079 - canonical:GATE-1#11.5

- Source reference: docs/GATE-1-CHECKLIST.md row 11.5
- Description: A correlation identifier propagates from the HTTP request through every provider attempt to the persisted record, so one call is traceable end to end.
- Implementation: `file:apps/api/src/iacode_api/routes/gateway.py`
- Test: `test:test_correlation_reaches_the_persisted_model_call`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0080 - canonical:GATE-1#12.1

- Source reference: docs/GATE-1-CHECKLIST.md row 12.1
- Description: The gateway API is versioned and documented in the OpenAPI document.
- Implementation: `file:apps/api/src/iacode_api/routes/gateway.py`
- Test: `test:test_openapi_documents_the_gateway_endpoints`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0081 - canonical:GATE-1#12.2

- Source reference: docs/GATE-1-CHECKLIST.md row 12.2
- Description: The provider listing returns safe metadata only and never a credential, an authorization header or a secret value.
- Implementation: `file:apps/api/src/iacode_api/routes/gateway.py`
- Test: `test:test_provider_listing_exposes_no_secret`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0082 - canonical:GATE-1#12.3

- Source reference: docs/GATE-1-CHECKLIST.md row 12.3
- Description: The model listing filters by provider, by active state and by capability.
- Implementation: `file:apps/api/src/iacode_api/routes/gateway.py`
- Test: `test:test_model_listing_filters`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0083 - canonical:GATE-1#12.4

- Source reference: docs/GATE-1-CHECKLIST.md row 12.4
- Description: The synchronization endpoint reports what was added, updated, deactivated, unchanged and what failed, without exposing a provider secret.
- Implementation: `file:apps/api/src/iacode_api/routes/gateway.py`
- Test: `test:test_sync_endpoint_reports_its_outcome`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0084 - canonical:GATE-1#12.5

- Source reference: docs/GATE-1-CHECKLIST.md row 12.5
- Description: The inference endpoint returns the normalized response, the route information, the usage and the request identifier, and never a stack trace.
- Implementation: `file:apps/api/src/iacode_api/routes/gateway.py`
- Test: `test:test_infer_endpoint_returns_the_normalised_response`, `test:test_infer_endpoint_leaks_no_internal_detail`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0085 - canonical:GATE-1#12.6

- Source reference: docs/GATE-1-CHECKLIST.md row 12.6
- Description: The gateway health endpoint separates the process from the external provider, so an unreachable provider is reported without claiming the service is down.
- Implementation: `file:apps/api/src/iacode_api/routes/gateway.py`
- Test: `test:test_gateway_health_separates_process_from_provider`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0086 - canonical:GATE-1#13.1

- Source reference: docs/GATE-1-CHECKLIST.md row 13.1
- Description: A Model Gateway page shows the provider status, the model count, the last synchronization and the model list with its capabilities.
- Implementation: `file:apps/web/src/app/gateway/gateway.ts`, `file:apps/web/src/app/gateway/gateway.spec.ts`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/runbooks/MODEL-GATEWAY.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0087 - canonical:GATE-1#13.2

- Source reference: docs/GATE-1-CHECKLIST.md row 13.2
- Description: A minimal playground sends a prompt with a route or a model and an optional reasoning effort, and shows the chosen model, the provider, the answer, the latency and the usage when it exists.
- Implementation: `file:apps/web/src/app/gateway/gateway.html`, `file:apps/web/src/app/gateway/gateway.spec.ts`
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/runbooks/MODEL-GATEWAY.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0088 - canonical:GATE-1#13.3

- Source reference: docs/GATE-1-CHECKLIST.md row 13.3
- Description: No provider credential reaches the browser: the page calls the IACode backend and nothing else.
- Implementation: _none_
- Test: `test:test_frontend_calls_only_the_iacode_backend`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0089 - canonical:GATE-1#13.4

- Source reference: docs/GATE-1-CHECKLIST.md row 13.4
- Description: No conversation persistence, chat history, persona, agent interface or tool execution is added to the frontend.
- Implementation: _none_
- Test: `test:test_frontend_adds_no_conversation_capability`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0090 - canonical:GATE-1#13.5

- Source reference: docs/GATE-1-CHECKLIST.md row 13.5
- Description: The frontend suite covers the new page and its service, runs headless and is part of the verification command.
- Implementation: `file:scripts/iacode/verify.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0091 - canonical:GATE-1#14.1

- Source reference: docs/GATE-1-CHECKLIST.md row 14.1
- Description: A real catalog synchronization runs against the configured provider API, parses the answer, normalizes it, persists it and repeats without changing anything.
- Implementation: `file:scripts/iacode/gateway_smoke.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0002`
- Guardrail: _none_

### REQ-0092 - canonical:GATE-1#14.2

- Source reference: docs/GATE-1-CHECKLIST.md row 14.2
- Description: A real non-streaming inference against the explicitly configured smoke model returns the expected text through the normalized response.
- Implementation: `file:scripts/iacode/gateway_smoke.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0002`
- Guardrail: _none_

### REQ-0093 - canonical:GATE-1#14.3

- Source reference: docs/GATE-1-CHECKLIST.md row 14.3
- Description: A real streaming inference produces a start, at least one delta and an end, with no duplicated content.
- Implementation: `file:scripts/iacode/gateway_smoke.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0002`
- Guardrail: _none_

### REQ-0094 - canonical:GATE-1#14.4

- Source reference: docs/GATE-1-CHECKLIST.md row 14.4
- Description: The configured smoke model is never silently substituted: its absence from the discovered catalog fails the check.
- Implementation: `file:scripts/iacode/gateway_smoke.py`
- Test: `test:test_absent_smoke_model_fails_rather_than_substitutes`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0095 - canonical:GATE-1#14.5

- Source reference: docs/GATE-1-CHECKLIST.md row 14.5
- Description: The live checks are minimal: a short prompt, a small output cap, no repetition, no deliberate rate limiting and no repeated authentication failure against the real provider.
- Implementation: `file:scripts/iacode/gateway_smoke.py`
- Test: `test:test_live_smoke_is_bounded_and_minimal`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0096 - canonical:GATE-1#14.6

- Source reference: docs/GATE-1-CHECKLIST.md row 14.6
- Description: The live inference produced a persisted record carrying the provider, the model, the status, the latency and the usage the provider supplied, and carrying no prompt.
- Implementation: `file:scripts/iacode/gateway_smoke.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0002`
- Guardrail: _none_

### REQ-0097 - canonical:GATE-1#14.7

- Source reference: docs/GATE-1-CHECKLIST.md row 14.7
- Description: The observability stack observed the live gateway request.
- Implementation: `file:infra/prometheus/prometheus.yml`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: `command:cmd-0002`
- Guardrail: _none_

### REQ-0098 - canonical:GATE-1#14.8

- Source reference: docs/GATE-1-CHECKLIST.md row 14.8
- Description: Without a configured provider credential the live validation fails loudly and the Gate is blocked, and no result is claimed that was not executed.
- Implementation: `file:scripts/iacode/gateway_smoke.py`
- Test: `test:test_missing_credential_blocks_rather_than_passes`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0099 - canonical:GATE-1#15.1

- Source reference: docs/GATE-1-CHECKLIST.md row 15.1
- Description: A provider contract suite proves discovery, generation, streaming, usage, error normalization, timeout, cancellation and tool-call normalization for every adapter.
- Implementation: _none_
- Test: `file:services/model-gateway/tests/test_provider_contract.py`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0100 - canonical:GATE-1#15.2

- Source reference: docs/GATE-1-CHECKLIST.md row 15.2
- Description: The catalog suite covers a new model, changed metadata, a removed model, a duplicate, invalid metadata, an unknown capability, a failed transaction and a repeated synchronization.
- Implementation: _none_
- Test: `file:services/model-gateway/tests/test_catalog.py`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0101 - canonical:GATE-1#15.3

- Source reference: docs/GATE-1-CHECKLIST.md row 15.3
- Description: The routing suite covers an explicit model, the default model, capability filtering, an unknown required capability, a disabled provider, an inactive model, an insufficient context window, route priority, fallback order and fallback exhaustion.
- Implementation: _none_
- Test: `file:services/model-gateway/tests/test_routing.py`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0102 - canonical:GATE-1#15.4

- Source reference: docs/GATE-1-CHECKLIST.md row 15.4
- Description: The retry suite proves which classes are retried — rate limiting, server failure, timeout, connection reset — and which are not: authentication, invalid request and context limit.
- Implementation: _none_
- Test: `file:services/model-gateway/tests/test_resilience.py`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0103 - canonical:GATE-1#15.5

- Source reference: docs/GATE-1-CHECKLIST.md row 15.5
- Description: The circuit breaker suite covers the threshold, the open state, fast failure, the cooldown, the half-open probe, recovery and reopening, without waiting in real time.
- Implementation: _none_
- Test: `file:services/model-gateway/tests/test_resilience.py`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0104 - canonical:GATE-1#15.6

- Source reference: docs/GATE-1-CHECKLIST.md row 15.6
- Description: The streaming suite covers a normal stream, an empty stream, a failure before the first delta, a failure after the first delta, consumer cancellation, usage at the end and a tool-call delta.
- Implementation: _none_
- Test: `file:services/model-gateway/tests/test_streaming.py`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0105 - canonical:GATE-1#15.7

- Source reference: docs/GATE-1-CHECKLIST.md row 15.7
- Description: A test proves that two models' output can never be concatenated into one stream.
- Implementation: _none_
- Test: `file:services/model-gateway/tests/test_streaming.py`, `test:test_no_two_models_are_concatenated_in_one_stream`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0106 - canonical:GATE-1#15.8

- Source reference: docs/GATE-1-CHECKLIST.md row 15.8
- Description: The structured-output suite proves that an incapable candidate is rejected and that a capable one receives the right configuration.
- Implementation: _none_
- Test: `file:services/model-gateway/tests/test_structured_output.py`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0107 - canonical:GATE-1#15.9

- Source reference: docs/GATE-1-CHECKLIST.md row 15.9
- Description: The secret suite proves that a credential appears in no log, no exception, no HTTP response, no persisted record, no metric and no catalog metadata.
- Implementation: _none_
- Test: `file:services/model-gateway/tests/test_secrets.py`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0108 - canonical:GATE-1#15.10

- Source reference: docs/GATE-1-CHECKLIST.md row 15.10
- Description: Provider unavailability, an invalid credential and rate limiting are exercised with fixtures rather than against the real provider.
- Implementation: _none_
- Test: `file:services/model-gateway/tests/test_resilience.py`, `file:services/model-gateway/tests/test_provider_contract.py`, `file:services/model-gateway/tests/test_secrets.py`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0109 - canonical:GATE-1#15.11

- Source reference: docs/GATE-1-CHECKLIST.md row 15.11
- Description: The deterministic provider double exists only under the test fixtures and cannot be reached from a runtime path.
- Implementation: _none_
- Test: `test:test_no_fake_provider_is_registered_at_runtime`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0110 - canonical:GATE-1#16.1

- Source reference: docs/GATE-1-CHECKLIST.md row 16.1
- Description: The schema change of this Gate is a new migration, and no migration of the previous Gate is edited.
- Implementation: _none_
- Test: `test:test_previous_migrations_are_unmodified`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0111 - canonical:GATE-1#16.2

- Source reference: docs/GATE-1-CHECKLIST.md row 16.2
- Description: Every migration runs from zero against an empty database and produces the declared schema.
- Implementation: _none_
- Test: `test:test_migrations_run_from_zero`, `test:test_the_declared_model_matches_the_migrated_schema`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0112 - canonical:GATE-1#16.3

- Source reference: docs/GATE-1-CHECKLIST.md row 16.3
- Description: A database created by the previous Gate upgrades without loss.
- Implementation: _none_
- Test: `test:test_a_previous_gate_database_upgrades`, `test:test_the_upgrade_carries_forward_what_the_booleans_said`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0113 - canonical:GATE-1#16.4

- Source reference: docs/GATE-1-CHECKLIST.md row 16.4
- Description: The Foundation endpoints, the backup and restore procedure, the restart behaviour and the observability stack do not regress.
- Implementation: `file:scripts/iacode/verify.py`
- Test: _none_
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### REQ-0114 - canonical:GATE-1#17.1

- Source reference: docs/GATE-1-CHECKLIST.md row 17.1
- Description: An operational runbook documents provider configuration, the variables, synchronization, listing, inference, streaming, fallback, troubleshooting, the live smoke and how to add an adapter.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/runbooks/MODEL-GATEWAY.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0115 - canonical:GATE-1#17.2

- Source reference: docs/GATE-1-CHECKLIST.md row 17.2
- Description: The architecture document describes the gateway boundary, what crosses it and what is deliberately absent.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/ARCHITECTURE.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0116 - canonical:GATE-1#17.3

- Source reference: docs/GATE-1-CHECKLIST.md row 17.3
- Description: The entry documentation and the development guide describe what exists after this Gate and how to run it.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:README.md`, `file:docs/DEVELOPMENT.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0117 - canonical:GATE-1#17.4

- Source reference: docs/GATE-1-CHECKLIST.md row 17.4
- Description: Every dependency and version this Gate pins is recorded in the one place that records versions.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/VERSIONS.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0118 - canonical:GATE-1#17.5

- Source reference: docs/GATE-1-CHECKLIST.md row 17.5
- Description: The API examples are sanitized and carry no real token.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/runbooks/MODEL-GATEWAY.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0119 - canonical:GATE-1#17.6

- Source reference: docs/GATE-1-CHECKLIST.md row 17.6
- Description: Every structural decision of this Gate that is not already recorded becomes an ADR, and no ADR duplicates an existing decision.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/adr/ADR-0016-model-gateway-boundary.md`, `file:docs/adr/ADR-0017-capabilities-are-tri-state.md`, `file:docs/adr/ADR-0018-streaming-commitment-point.md`, `file:docs/adr/ADR-0019-credentials-are-named-not-stored.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0120 - canonical:GATE-1#18.1

- Source reference: docs/GATE-1-CHECKLIST.md row 18.1
- Description: The entry contract and the plan describe the current Gate and its status truthfully.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:START-HERE.md`, `file:docs/MASTER-PLAN.md`, `file:docs/checkpoints/LATEST.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0121 - canonical:GATE-1#18.2

- Source reference: docs/GATE-1-CHECKLIST.md row 18.2
- Description: The Gate produces a retrospective from the canonical template.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:.iacode/memory/retrospectives/GATE-1-CP-0001.md`
- Validation: _none_
- Guardrail: _none_

### REQ-0122 - canonical:GATE-1#18.3

- Source reference: docs/GATE-1-CHECKLIST.md row 18.3
- Description: The Gate closes on the project's own controls and claims no independent, fresh-session or cross-tool verdict.
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/checkpoints/GATE-1-CP-0001/STATE.json`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0001 - lesson:LSN-0001

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0001
- Description: Verify checkpoint validation must succeed from a detached checkout of the checkpoint tag
- Implementation: _none_
- Test: `test:DetachedHeadValidationTests.test_detached_head_at_checkpoint_tag_validates`, `test:DetachedHeadValidationTests.test_detached_head_at_wrong_commit_fails`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0002 - lesson:LSN-0002

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0002
- Description: Verify a file inventory must be recomputed from the repository, never trusted as an assertion
- Implementation: _none_
- Test: `test:DeltaInventoryTests.test_removed_manifest_entry_fails`, `test:DeltaInventoryTests.test_silent_tracked_modification_fails`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0003 - lesson:LSN-0003

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0003
- Description: Verify every operation attempt must be auditable, including a refusal decided before execution
- Implementation: _none_
- Test: `test:FinalizationAttemptRecordingTests.test_detached_head_refusal_is_recorded`, `test:FinalizationAttemptRecordingTests.test_non_latest_checkpoint_refusal_is_recorded`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0004 - lesson:LSN-0004

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0004
- Description: Verify a checkpoint may never claim readiness while it also claims to be blocked
- Implementation: _none_
- Test: `test:ResealedBlockerFixtureTests.test_resealed_ready_for_review_with_blocker_is_rejected`, `test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0005 - lesson:LSN-0005

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0005
- Description: Verify a PASS requires evidence that can be executed or resolved, not a statement
- Implementation: _none_
- Test: `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`, `test:QualityEvidenceTests.test_pass_referencing_a_failed_command_fails`, `test:QualityEvidenceTests.test_pass_without_evidence_fails`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0006 - lesson:LSN-0006

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0006
- Description: Verify the repository must be self-contained; a specification may not live outside it
- Implementation: _none_
- Test: `test:SetupChecklistTests.test_checklist_exists_and_is_referenced`, `test:SetupChecklistTests.test_documentation_links_resolve`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0007 - lesson:LSN-0007

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0007
- Description: Verify independent validation cannot be declared by the run that did the work
- Implementation: _none_
- Test: `test:DeliveryAssuranceGateTests.test_self_claimed_independent_review_blocks_review`, `test:ExternalAttestationTests.test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected`, `test:ExternalAttestationTests.test_an_implementer_checkpoint_cannot_declare_an_external_pass`, `test:ExternalAttestationTests.test_second_tool_validation_alone_is_not_enough`, `test:SecondToolValidationTests.test_failed_cross_tool_validation_cannot_grant_gate_pass`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0008 - lesson:LSN-0008

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0008
- Description: Verify requirement completeness must be total and evidence-backed before handoff
- Implementation: _none_
- Test: `test:DeliveryAssuranceGateTests.test_completeness_validator_not_executed_blocks_review`, `test:DeliveryCompletenessMatrixTests.test_one_requirement_short_of_total_fails`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`, `test:ExpectedRequirementSetTests.test_deleting_a_requirement_and_recomputing_the_counts_still_fails`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0009 - lesson:LSN-0009

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0009
- Description: Verify a red gate requires rework, never a waiver, and never a weakened check
- Implementation: _none_
- Test: `test:DeliveryAssuranceGateTests.test_green_keeper_pass_with_a_real_failure_is_rejected`, `test:DeliveryAssuranceGateTests.test_red_tests_block_review`, `test:GreenKeeperToolTests.test_red_gate_is_reported_as_still_red`, `test:MandatoryGatePolicyTests.test_a_cycle_measured_against_no_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_the_policy_declares_a_non_empty_closed_set`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0010 - lesson:LSN-0010

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0010
- Description: Verify a recorded command must carry runtime, working directory, commit and purpose to be replayable
- Implementation: _none_
- Test: `test:CommandInputBindingTests.test_a_clean_tree_claim_is_checked_against_the_declared_commit`, `test:CommandInputBindingTests.test_a_record_without_a_digest_is_rejected`, `test:CommandReproducibilityTests.test_bare_script_name_is_rejected`, `test:CommandReproducibilityTests.test_unresolvable_script_path_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0011 - lesson:LSN-0011

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0011
- Description: Verify a control over a checkpoint's own evidence must be scoped to the moment it matters
- Implementation: _none_
- Test: `test:DeliveryAssuranceGateTests.test_gate_consistency_is_provisional_while_work_is_in_progress`, `test:test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes`, `test:test_no_other_module_executes_the_mandatory_gate_set`, `test:test_the_refresh_has_one_definition`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0012 - lesson:LSN-0012

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0012
- Description: Verify sealed checkpoints and their tags are immutable, and tooling must keep validating them
- Implementation: _none_
- Test: `test:HistoricalCheckpointCompatibilityTests.test_first_sealed_checkpoint_still_validates`, `test:HistoricalCheckpointCompatibilityTests.test_fourth_sealed_checkpoint_still_validates`, `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`, `test:IntegrityAnchorTests.test_a_moved_historical_tag_is_detected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0013 - lesson:LSN-0013

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0013
- Description: Verify an installed capability must be detected by resolved path, not by a bare command lookup
- Implementation: _none_
- Test: _none_
- Negative test: _none_
- Documentation: `file:docs/TOOL-CAPABILITIES.md`
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0014 - lesson:LSN-0014

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0014
- Description: Verify evidence must be recorded as it happens, not reconstructed at the end of a run
- Implementation: _none_
- Test: `test:SealChronologyTests.test_a_dirty_tree_validation_is_not_evidence_of_a_sealed_commit`, `test:SealChronologyTests.test_a_missing_post_commit_validation_is_rejected`, `test:SealChronologyTests.test_a_record_after_the_end_of_the_run_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0015 - lesson:LSN-0015

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0015
- Description: Verify every positive terminal status needs one shared promotion invariant
- Implementation: _none_
- Test: `test:PromotionInvariantTests.test_a_terminal_status_requires_an_independent_verdict`, `test:PromotionInvariantTests.test_every_positive_status_rejects_a_red_green_keeper`, `test:PromotionInvariantTests.test_every_positive_status_rejects_every_red_quality_dimension`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0016 - lesson:LSN-0016

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0016
- Description: Verify a mandatory set must be closed by policy, never chosen by the caller
- Implementation: _none_
- Test: `test:MandatoryGatePolicyTests.test_a_cycle_missing_one_mandatory_gate_is_rejected`, `test:MandatoryGatePolicyTests.test_a_mandatory_gate_that_exited_nonzero_is_rejected`, `test:MandatoryGatePolicyTests.test_a_pass_measured_before_a_source_change_is_stale`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0017 - lesson:LSN-0017

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0017
- Description: Verify a completeness denominator must come from a source the delivery does not own
- Implementation: _none_
- Test: `test:ExpectedRequirementSetTests.test_a_downgraded_matrix_cannot_escape_the_comparison`, `test:ExpectedRequirementSetTests.test_an_unexpected_anchored_requirement_is_rejected`, `test:ExpectedRequirementSetTests.test_the_checklist_is_reparsed_rather_than_trusted`, `test:ExpectedRequirementSetTests.test_the_expected_set_is_derived_from_the_canonical_sources`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0018 - lesson:LSN-0018

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0018
- Description: Verify a structured reference must be resolved, not merely well typed
- Implementation: _none_
- Test: `test:LessonResolutionTests.test_a_test_control_must_exist_in_the_suite`, `test:LessonResolutionTests.test_an_invariant_control_must_be_defined_in_the_tooling`, `test:LessonResolutionTests.test_lesson_evidence_must_resolve`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0019 - lesson:LSN-0019

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0019
- Description: Verify a derived artifact must carry a fingerprint of the inputs that produced it
- Implementation: _none_
- Test: `test:PreflightFreshnessTests.test_a_changed_fingerprint_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_dropped_lesson_makes_the_preflight_stale`, `test:PreflightFreshnessTests.test_a_preflight_from_another_gate_is_refused`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0020 - lesson:LSN-0020

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0020
- Description: Verify evidence produced from a dirty tree needs immutable input identity
- Implementation: _none_
- Test: `test:CommandInputBindingTests.test_a_digest_that_omits_an_input_is_rejected`, `test:CommandInputBindingTests.test_the_recorder_binds_inputs_automatically`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0021 - lesson:LSN-0021

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0021
- Description: Verify sealed history needs an anchor outside the content it describes
- Implementation: _none_
- Test: `test:IntegrityAnchorTests.test_a_broken_link_between_anchors_is_detected`, `test:IntegrityAnchorTests.test_a_recomputed_anchor_hash_must_match_its_fields`, `test:IntegrityAnchorTests.test_a_sealed_checkpoint_without_an_anchor_is_detected`, `test:IntegrityAnchorTests.test_an_unexpected_tree_is_detected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0022 - lesson:LSN-0022

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0022
- Description: Verify an authoritative count must be derived once, never maintained by hand twice
- Implementation: _none_
- Test: `test:DerivedCountTests.test_a_forged_count_is_rejected`, `test:DerivedCountTests.test_a_markdown_claim_that_contradicts_the_derivation_is_rejected`, `test:SourceCardinalityPolicyTests`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_a_derived_count_claim`, `test:SourceCardinalityPolicyTests.test_no_comment_or_docstring_states_the_cardinality_of_a_derived_set`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0023 - lesson:LSN-0023

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0023
- Description: Verify a lesson must cite a source that actually records the finding it claims
- Implementation: _none_
- Test: `test:LessonProvenanceTests.test_a_finding_absent_from_the_cited_checkpoint_is_rejected`, `test:LessonProvenanceTests.test_a_nonexistent_checkpoint_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0024 - lesson:LSN-0024

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0024
- Description: Verify a control is finished only when its positive path has been executed, not only its refusals
- Implementation: _none_
- Test: `test:PositivePromotionTests.test_the_milestone_verdict_is_derived_as_passed`, `test:PositivePromotionTests.test_the_subject_is_not_rewritten_by_its_own_audit`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0025 - lesson:LSN-0025

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0025
- Description: Verify a generic guardrail derives repository state instead of naming today's checkpoint
- Implementation: _none_
- Test: `test:IntegrityAnchorTests.test_the_pending_exclusion_is_the_newest_sealed_checkpoint`, `test:SuccessorDurabilityTests.test_the_pending_exclusion_moves_with_the_chain`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0026 - lesson:LSN-0026

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0026
- Description: Verify an adversarial battery without a null-mutation control proves nothing
- Implementation: _none_
- Test: `test:InternalAssuranceTests.test_a_failed_null_mutation_control_cannot_produce_a_pass`, `test:InternalAssuranceTests.test_a_report_without_a_null_mutation_control_is_rejected`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0027 - lesson:LSN-0027

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0027
- Description: Verify a lesson's prose may record a residual limit but may never contradict its status
- Implementation: _none_
- Test: `test:MemoryPolicyDocumentTests.test_a_guarded_lesson_may_not_describe_itself_as_unguarded`, `test:MemoryPolicyDocumentTests.test_the_repository_memory_has_no_status_contradiction`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0028 - lesson:LSN-0028

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0028
- Description: Verify a configuration key that no code reads is a defect, not documentation
- Implementation: _none_
- Test: `test:MemoryPolicyDocumentTests.test_a_setting_no_code_reads_cannot_be_declared`, `test:MemoryPolicyDocumentTests.test_the_declared_policy_validates_against_its_schema`, `test:test_every_declared_key_is_read_somewhere`, `test:test_test_settings_ignore_the_ambient_environment`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0029 - lesson:LSN-0029

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0029
- Description: Verify a required protocol transition must never turn a mandatory gate red
- Implementation: _none_
- Test: `test:GateTransitionSimulationTests.test_its_mirror_audit_passes_with_the_empty_dimensions_inapplicable`, `test:GateTransitionSimulationTests.test_the_first_checkpoint_of_the_next_gate_reaches_review_readiness`, `test:SuccessorDurabilityTests.test_a_missing_anchor_is_still_detected_after_the_chain_advances`, `test:SuccessorDurabilityTests.test_every_state_of_the_chain_verifies`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0030 - lesson:LSN-0031

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0030
- Description: Verify an empty applicable set is not a missing required set, and a control must tell them apart
- Implementation: _none_
- Test: `test:MirrorApplicabilitySemanticsTests.test_a_missing_required_set_fails_rather_than_being_inapplicable`, `test:MirrorApplicabilitySemanticsTests.test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes`, `test:MirrorApplicabilityValidationTests.test_a_registry_bound_dimension_cannot_be_declared_inapplicable`, `test:SimulationExecutesProductionControlsTests.test_every_simulated_mirror_is_recorded_as_executed`, `test:SimulationExecutesProductionControlsTests.test_the_sealed_artifact_is_the_tools_own_output`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0031 - lesson:LSN-0032

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0031
- Description: Verify a control written while one Gate was the only Gate stops being a control when the next one starts
- Implementation: _none_
- Test: `test:test_assurance_scope_covers_the_runtime_source`, `test:test_declared_suites_are_discovered`, `test:test_expected_set_names_the_gate_specification`, `test:test_no_future_gate_capability_is_implemented`, `test:test_the_scope_control_detects_an_implementation`, `test:test_the_scope_control_ignores_a_gate_that_has_already_run`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0032 - lesson:LSN-0033

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0032
- Description: Verify a value bound in middleware is absent in the handlers that run outside it
- Implementation: _none_
- Test: `test:test_a_missing_route_uses_the_error_contract`, `test:test_internal_error_leaks_nothing`, `test:test_internal_error_still_carries_a_correlation_identifier`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0033 - lesson:LSN-0034

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0033
- Description: Verify re-deriving what the framework already computed diverges from the framework
- Implementation: _none_
- Test: `test:test_metrics_endpoint_exposes_request_metrics`, `test:test_metrics_label_routes_by_template_not_by_url`, `test:test_the_api_instruments_reach_prometheus`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0034 - lesson:LSN-0035

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0034
- Description: Verify captured subprocess output decoded or re-emitted with the platform codepage crashes the tool, not the work
- Implementation: _none_
- Test: `test:test_every_tool_that_re_emits_captured_output_configures_its_own_stream`, `test:test_no_capture_relies_on_the_platform_codepage`, `test:test_the_rule_detects_a_capture_that_would_fail`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0035 - lesson:LSN-0036

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0035
- Description: Verify a gate that runs inside an image measures the image, not the source
- Implementation: _none_
- Test: `test:test_every_image_gate_builds_before_it_measures`, `test:test_the_image_gate_rule_detects_a_gate_that_would_skip_the_build`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0036 - lesson:LSN-0037

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0036
- Description: Verify a shared control that names an identifier the repository derives stops being a control when that identifier moves
- Implementation: _none_
- Test: `test:test_no_control_names_a_migration_revision_literally`, `test:test_no_shared_control_is_bound_to_a_gate_literal`, `test:test_the_gate_literal_rule_accepts_a_derived_gate_and_a_fixture_root`, `test:test_the_gate_literal_rule_detects_a_bound_control`, `test:test_the_head_revision_has_one_derivation`, `test:test_the_revision_rule_detects_a_named_head`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0037 - lesson:LSN-0038

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0037
- Description: Verify two representations of one concept in one module disagree, and the safer one loses
- Implementation: _none_
- Test: `test:test_a_documented_placeholder_is_not_redacted`, `test:test_both_redactors_agree_on_every_value_the_example_file_carries`, `test:test_no_module_writes_its_own_credential_name_rule`, `test:test_the_rule_detects_a_second_opinion`, `test:test_the_two_questions_stay_different`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0038 - lesson:LSN-0039

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0038
- Description: Verify a test that writes to the operational database leaves production data behind
- Implementation: _none_
- Test: `test:test_the_operational_catalog_holds_only_providers_the_policy_declares`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_

### LESSON-REQ-0039 - lesson:LSN-0040

- Source reference: LESSON-PREFLIGHT.json LESSON-REQ-0039
- Description: Verify a control that judges sealed history only runs once a successor anchors it
- Implementation: _none_
- Test: `test:test_an_ignored_input_is_bound_by_content_rather_than_by_presence`, `test:test_an_ignored_input_without_a_bound_digest_is_still_refused`, `test:test_an_input_the_repository_carries_is_still_required_to_exist`, `test:test_every_sealed_checkpoint_validates_from_its_own_tag`, `test:test_the_recorder_never_declares_an_ignored_path_as_an_input`
- Negative test: _none_
- Documentation: _none_
- Validation: _none_
- Guardrail: _none_
