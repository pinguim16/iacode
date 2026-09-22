# GATE 1 — Model Gateway Checklist

This is the canonical specification of `GATE 1 — MODEL GATEWAY`. It is the source the expected
requirement set is derived from, re-parsed at every run by `policies.canonical_requirements` and
mirrored, row for row, by `.iacode/policies/canonical-requirements.json`. A delivery for this Gate
cannot declare a smaller set, and a row cannot be dropped by editing the mirror.

The objective of the Gate is a **single, provider-neutral boundary for model invocation**: a
provider abstraction, a discovered model catalog, a deterministic router, normalized requests,
responses, tool calls, usage and errors, real streaming, bounded retries, timeouts, a circuit
breaker and a fallback chain, operational persistence and telemetry, an HTTP API, an operational
frontend page, and at least one real provider proving the boundary against a live API.

The Gate deliberately does **not** implement the agent runtime, tool execution, the sandbox,
retrieval, the experience store, training or model promotion. The gateway *normalizes* a tool call
so a later Gate can decide what to do with it; deciding is Gate 2's work, and executing is Gate 3's.

`GATE 1` belongs to milestone `M1` and does not close it, so it ends at `INTERNAL_GATE_PASS`.

## 1. Gate specification and requirement derivation

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 1.1 | A canonical, machine-readable requirement specification exists for this Gate and the registry mirrors it row for row. | `docs/GATE-1-CHECKLIST.md`, `.iacode/policies/canonical-requirements.json` | `policies.canonical_requirements` parses and mirrors the document; `Gate1CanonicalSpecificationTests`. |
| 1.2 | The closed mandatory gate registry carries every executable gate this Gate introduces. | `.iacode/policies/quality-gates.json` | A Green Keeper cycle measured against the registry's mandatory set. |
| 1.3 | Every test suite this Gate introduces is declared canonically, is counted by the count derivation and is resolvable as evidence. | `.iacode/policies/test-suites.json` | `COUNTS.json` `TESTS`; `test_gateway_suite_is_declared_and_discovered`. |
| 1.4 | The internal Red Team battery of this Gate is executable, scoped to the Model Gateway, and records a null-mutation control. | `scripts/development-ledger/gate1_red_team.py` | `M1-INTERNAL-RED-TEAM.json` with a `VALID` `baselineControl`. |
| 1.5 | The reservation of the gateway directory is consumed by the Gate that owns it, and the scope registry keeps constraining every path still owned by a later Gate. | `.iacode/policies/gate-scope.json`, `services/model-gateway/README.md` | `test_model_gateway_reservation_is_consumed_by_its_owner`. |
| 1.6 | One documented command verifies this Gate, adds the stages it introduces and keeps a targeted mode that does not restart the stack. | `scripts/iacode/verify.py` | Verification run, targeted and full. |

## 2. Gateway boundary and architecture

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 2.1 | The Model Gateway lives in the directory the Foundation reserved for it and is consumed in process, and the boundary decision is recorded rather than implied. | `services/model-gateway/`, `docs/adr/ADR-0016-model-gateway-boundary.md` | `test_gateway_package_is_importable`; `ADR-0016`. |
| 2.2 | No consumer outside the adapter layer names a provider-specific endpoint, payload field or product name. | `services/model-gateway/src/`, `apps/api/src/`, `apps/web/src/` | `test_no_provider_specific_name_escapes_the_adapter_layer`. |
| 2.3 | The gateway declares its persistence and clock ports and imports no application module, so the dependency points inward. | `services/model-gateway/src/iacode_model_gateway/ports.py` | `test_gateway_imports_no_application_module`. |
| 2.4 | No later-Gate capability — tool execution, agent lifecycle, sandboxing, retrieval, experience storage or training — is implemented, simulated or faked here. | the whole tree | `test_no_future_gate_capability_is_implemented`. |
| 2.5 | The gateway directory stops declaring itself reserved and describes what this Gate delivered. | `services/model-gateway/README.md` | File content; `test_gateway_readme_describes_the_delivery`. |

## 3. The gateway contracts

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 3.1 | A canonical request carries correlation, messages, routing intent, required capabilities, sampling, output limits, streaming intent, tools, structured output and metadata, and is validated when it is built. | `services/model-gateway/src/iacode_model_gateway/contracts.py` | `test_request_is_validated_when_it_is_built`. |
| 3.2 | The message contract expresses the system, developer, user, assistant and tool roles independently of any provider's vocabulary. | `services/model-gateway/src/iacode_model_gateway/contracts.py` | `test_message_roles_are_provider_independent`. |
| 3.3 | The canonical response normalizes content, tool calls, finish reason, usage, latency, provider, model, endpoint, route and fallback chain, and the raw provider payload is never the public contract. | `services/model-gateway/src/iacode_model_gateway/contracts.py` | `test_response_never_exposes_the_raw_provider_payload`. |
| 3.4 | Tool definitions and tool calls are normalized into internal types with identifier, name and arguments, and the gateway executes no tool. | `services/model-gateway/src/iacode_model_gateway/contracts.py` | `test_gateway_normalises_a_tool_call_without_executing_it`. |
| 3.5 | A tool call whose arguments are not valid JSON produces a normalized error instead of a partially parsed call. | `services/model-gateway/src/iacode_model_gateway/protocols/` | `test_invalid_tool_arguments_produce_a_normalised_error`. |
| 3.6 | Structured output is requested only from a model whose capability is known, and a request that needs it is refused or routed elsewhere rather than sent hopefully. | `services/model-gateway/src/iacode_model_gateway/routing/router.py` | `test_structured_output_requires_a_capable_candidate`. |
| 3.7 | The contract carries an explicit version, so a consumer can detect an incompatible change instead of discovering one. | `services/model-gateway/src/iacode_model_gateway/contracts.py` | `test_contract_version_is_declared`. |

## 4. Provider abstraction and protocols

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 4.1 | A provider contract declares health, model discovery, generation and streaming, and is not shaped by any one provider. | `services/model-gateway/src/iacode_model_gateway/providers/base.py` | `test_provider_contract_is_not_coupled_to_one_provider`. |
| 4.2 | An OpenAI-compatible Chat Completions adapter builds the request, parses the response, parses the stream and maps the error. | `services/model-gateway/src/iacode_model_gateway/protocols/openai_chat.py` | `OpenAiChatProtocolTests`. |
| 4.3 | An OpenAI-compatible Responses adapter builds the request, parses the response, parses the stream and maps the error. | `services/model-gateway/src/iacode_model_gateway/protocols/openai_responses.py` | `OpenAiResponsesProtocolTests`. |
| 4.4 | An Anthropic-compatible Messages adapter builds the request, parses the response, parses the stream and maps the error. | `services/model-gateway/src/iacode_model_gateway/protocols/anthropic_messages.py` | `AnthropicMessagesProtocolTests`. |
| 4.5 | The protocol is selected from the capabilities and endpoints the catalog records, the shape of the request and the provider configuration, never assumed from a default path. | `services/model-gateway/src/iacode_model_gateway/protocols/selection.py` | `test_endpoint_selection_reads_the_declared_endpoints`. |
| 4.6 | A request that needs an endpoint the model does not declare is refused before it reaches the network. | `services/model-gateway/src/iacode_model_gateway/protocols/selection.py` | `test_unsupported_endpoint_is_refused_before_the_call`. |
| 4.7 | No fictitious provider is registered in the runtime configuration; the deterministic double exists only inside the test fixtures. | `.iacode/policies/providers.json`, `services/model-gateway/tests/fixtures/` | `test_no_fake_provider_is_registered_at_runtime`. |

## 5. Provider registry, configuration and secrets

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 5.1 | Provider configuration is versionable and carries no credential value: an identifier, an adapter, an enabled flag, a base URL reference, the name of the secret variable, the discovery endpoint and the protocols supported. | `.iacode/policies/providers.json` | `test_provider_configuration_carries_no_credential`. |
| 5.2 | The provider registry persists operational metadata — adapter, enabled state, health, last check and catalog state — and never a credential. | `apps/api/migrations/versions/`, `apps/api/src/iacode_api/db/models.py` | `test_no_table_stores_a_credential`; `test_provider_registry_persists_operational_metadata`. |
| 5.3 | A credential is resolved from the environment at call time and reaches no database row, response body, log record, metric label or catalog record. | `services/model-gateway/src/iacode_model_gateway/config.py` | `SecretContainmentTests`. |
| 5.4 | Every configuration key this Gate declares is read by the implementation. | `apps/api/src/iacode_api/config.py`, `infra/compose/.env.example` | `test_every_declared_key_is_read_somewhere`. |
| 5.5 | A provider base URL is validated: HTTPS for a remote provider, plain HTTP only for a loopback address, and never user information embedded in the URL. | `services/model-gateway/src/iacode_model_gateway/security/base_url.py` | `BaseUrlSafetyTests`. |
| 5.6 | A provider address can never be supplied by an inference request; it comes from administrative configuration alone. | `services/model-gateway/src/iacode_model_gateway/contracts.py`, `apps/api/src/iacode_api/routes/gateway.py` | `test_request_cannot_supply_a_provider_address`. |

## 6. Model catalog and synchronization

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 6.1 | The catalog is discovered from the provider API, and no list written by hand is treated as authoritative. | `services/model-gateway/src/iacode_model_gateway/catalog/sync.py` | `test_catalog_comes_from_the_provider_api`; live catalog run. |
| 6.2 | A normalized model record carries the provider model identifier, display name, family, context window, maximum output tokens, supported endpoints, streaming, vision, tools, structured output, reasoning levels, active state, raw metadata and the synchronization instant. | `services/model-gateway/src/iacode_model_gateway/catalog/normalize.py` | `test_normalised_model_carries_the_declared_fields`. |
| 6.3 | An absent capability stays unknown and is never normalized into a negative answer. | `services/model-gateway/src/iacode_model_gateway/catalog/normalize.py` | `test_unknown_capability_is_not_turned_into_false`. |
| 6.4 | Every capability records where it came from: provider metadata, manual configuration or observation, and never inference from a model's name. | `services/model-gateway/src/iacode_model_gateway/catalog/normalize.py` | `test_capability_provenance_is_recorded`; `test_capability_is_never_inferred_from_a_name`. |
| 6.5 | Synchronization is idempotent: running it twice over the same provider answer changes nothing the second time. | `services/model-gateway/src/iacode_model_gateway/catalog/sync.py` | `test_sync_is_idempotent`. |
| 6.6 | A model that disappears from the provider answer is deactivated rather than destroyed, so the calls recorded against it stay readable. | `services/model-gateway/src/iacode_model_gateway/catalog/sync.py` | `test_missing_model_is_deactivated_not_deleted`. |
| 6.7 | A partial, invalid or failed synchronization leaves the previous catalog usable: the answer is validated and normalized before anything is committed. | `services/model-gateway/src/iacode_model_gateway/catalog/sync.py` | `test_failed_sync_preserves_the_previous_catalog`. |
| 6.8 | Model identity is the provider together with the provider's own model identifier, so two providers exposing the same name do not collide. | `apps/api/src/iacode_api/db/models.py`, `services/model-gateway/src/iacode_model_gateway/contracts.py` | `test_same_model_id_in_two_providers_does_not_collide`. |
| 6.9 | Routing reads normalized fields; the raw provider metadata is kept for diagnosis and is never the thing a decision depends on. | `services/model-gateway/src/iacode_model_gateway/routing/router.py` | `test_routing_reads_normalised_fields_only`. |

## 7. Routing

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 7.1 | The router is deterministic and applies a documented order: validate, explicit override, candidates, capability filter, context filter, route policy, configured priority, execution, fallback. | `services/model-gateway/src/iacode_model_gateway/routing/router.py` | `test_router_is_deterministic`. |
| 7.2 | An explicit model is honored when the policy allows it and is refused, rather than silently replaced, when it cannot serve the request. | `services/model-gateway/src/iacode_model_gateway/routing/router.py` | `test_explicit_model_is_honoured_or_refused`. |
| 7.3 | A default model is configurable, and a request with no model and no usable default fails with a clear error instead of an arbitrary choice. | `services/model-gateway/src/iacode_model_gateway/config.py` | `test_missing_default_model_is_an_explicit_error`. |
| 7.4 | Required capabilities eliminate candidates that cannot satisfy them, and an unknown capability is refused unless the policy explicitly allows it. | `services/model-gateway/src/iacode_model_gateway/routing/policy.py` | `test_unknown_capability_is_rejected_by_default`. |
| 7.5 | The gateway never knowingly sends a request larger than the context window it knows about, and an estimated token count is labelled an estimate rather than reported as exact. | `services/model-gateway/src/iacode_model_gateway/routing/context.py` | `ContextWindowTests`. |
| 7.6 | A reasoning effort is validated against the levels the model or the provider declares, and an incompatible level produces a fallback or an explicit error rather than a silent send. | `services/model-gateway/src/iacode_model_gateway/routing/policy.py` | `test_incompatible_reasoning_effort_is_not_sent_silently`. |
| 7.7 | Route aliases are configuration, not built-in preference, and the system claims no empirical superiority for any of them. | `.iacode/policies/model-routes.json` | `test_route_aliases_come_from_configuration`. |
| 7.8 | No model quality score, benchmark result or comparative claim is invented anywhere in this Gate. | the whole tree | `test_no_model_quality_claim_is_hardcoded`. |
| 7.9 | Every routing result carries a short structured explanation of the decision, and never a model's private reasoning. | `services/model-gateway/src/iacode_model_gateway/routing/router.py` | `test_route_explanation_is_structured_and_short`. |
| 7.10 | A disabled provider and an inactive model are never selected. | `services/model-gateway/src/iacode_model_gateway/routing/router.py` | `test_disabled_provider_and_inactive_model_are_excluded`. |

## 8. Failure handling and reliability

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 8.1 | An internal error taxonomy distinguishes authentication, authorization, rate limiting, unknown model, invalid request, context limit, provider unavailability, provider timeout, transient and permanent provider failure, an open circuit, cancellation and an internal gateway failure, and every adapter maps onto it. | `services/model-gateway/src/iacode_model_gateway/errors.py` | `ErrorTaxonomyTests`. |
| 8.2 | Timeouts are configurable, connect and read are separated, and no provider call can hang without bound. | `services/model-gateway/src/iacode_model_gateway/config.py`, `services/model-gateway/src/iacode_model_gateway/providers/http_provider.py` | `test_no_call_is_unbounded`; `test_timeout_is_normalised`. |
| 8.3 | A retry happens only for an error class a retry can resolve, and never for authentication, authorization, an invalid request, an unknown model, an invalid schema or a context limit. | `services/model-gateway/src/iacode_model_gateway/resilience/retry.py` | `RetryClassificationTests`. |
| 8.4 | A provider's `Retry-After` is honored within a configured bound, and an unreasonably long wait is refused rather than obeyed. | `services/model-gateway/src/iacode_model_gateway/resilience/retry.py` | `test_retry_after_is_bounded`. |
| 8.5 | Backoff is exponential with jitter, and the test suite controls time instead of waiting for it. | `services/model-gateway/src/iacode_model_gateway/resilience/retry.py` | `test_backoff_is_exponential_with_jitter`. |
| 8.6 | A circuit breaker moves between closed, open and half-open per provider and per provider and model, from external configuration. | `services/model-gateway/src/iacode_model_gateway/resilience/circuit.py` | `CircuitBreakerTests`. |
| 8.7 | The fallback chain is bounded, never repeats a candidate, cannot loop, and the chain that was used is recorded. | `services/model-gateway/src/iacode_model_gateway/routing/router.py` | `test_fallback_chain_is_bounded_and_recorded`. |
| 8.8 | Fallback happens only for the error classes another candidate could resolve, and an invalid request is not retried against a second model. | `services/model-gateway/src/iacode_model_gateway/routing/policy.py` | `FallbackSemanticsTests`. |
| 8.9 | A consumer that cancels interrupts the upstream call and the attempt is recorded as cancelled. | `services/model-gateway/src/iacode_model_gateway/gateway.py` | `test_cancellation_stops_the_upstream_call`. |
| 8.10 | Request limits are configurable and enforced: payload size, message count, tool count, output tokens and fallback depth. | `services/model-gateway/src/iacode_model_gateway/resilience/limits.py` | `RequestLimitTests`. |
| 8.11 | A provider response larger than the configured bound is refused instead of being read into memory without limit. | `services/model-gateway/src/iacode_model_gateway/providers/http_provider.py` | `test_oversized_provider_response_is_refused`. |
| 8.12 | An unavailable provider never makes the Foundation liveness endpoint fail; it is visible in the gateway's own health instead. | `apps/api/src/iacode_api/routes/gateway.py` | `test_provider_outage_does_not_affect_process_health`. |

## 9. Streaming

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 9.1 | Streaming goes through the same router and the same adapter abstraction as a non-streaming call, with no parallel architecture. | `services/model-gateway/src/iacode_model_gateway/gateway.py` | `test_streaming_uses_the_same_router`. |
| 9.2 | Stream events are normalized into an envelope covering start, text delta, tool-call delta, usage, end and error. | `services/model-gateway/src/iacode_model_gateway/contracts.py` | `StreamEnvelopeTests`. |
| 9.3 | Automatic fallback is allowed only before the first content reaches the consumer; after it, the error is propagated and no second model continues the stream. | `services/model-gateway/src/iacode_model_gateway/gateway.py` | `test_no_fallback_after_the_first_delivered_content`. |
| 9.4 | A stream that fails after content ends with an explicit error event carrying the partial result, not with a silent completion. | `services/model-gateway/src/iacode_model_gateway/gateway.py` | `test_failure_after_content_ends_with_an_error_event`. |
| 9.5 | The API streams over Server-Sent Events and stops the upstream call when the client disconnects. | `apps/api/src/iacode_api/routes/gateway.py` | `test_stream_endpoint_emits_sse_and_stops_on_disconnect`. |

## 10. Usage, cost, persistence and privacy

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 10.1 | Usage is normalized where the provider supplies it — input, output, total, cached and reasoning tokens — and a field the provider did not supply stays absent rather than being invented. | `services/model-gateway/src/iacode_model_gateway/catalog/normalize.py` | `UsageNormalisationTests`. |
| 10.2 | Cost is absent unless pricing is configured, and zero is never used to mean unknown. | `services/model-gateway/src/iacode_model_gateway/pricing.py` | `test_unknown_cost_is_absent_not_zero`. |
| 10.3 | Every attempt is recorded with its operational metadata: correlation, provider, model, endpoint, route, status, timestamps, latency, tokens, error type, retries and fallbacks. | `apps/api/src/iacode_api/gateway/store.py` | `test_model_call_records_the_operational_metadata`; live persistence check. |
| 10.4 | Prompts, messages and completions are not persisted by default; the debug capture is opt-in, redacted, documented and off in every shipped configuration. | `services/model-gateway/src/iacode_model_gateway/config.py`, `apps/api/src/iacode_api/gateway/store.py` | `test_prompt_is_not_persisted_by_default`; `PromptCaptureTests`. |
| 10.5 | A request fingerprint may be stored for correlation, and its documentation states that a hash is not anonymization. | `services/model-gateway/src/iacode_model_gateway/fingerprint.py`, `docs/runbooks/MODEL-GATEWAY.md` | `test_request_fingerprint_is_stable_and_carries_no_content`. |
| 10.6 | No provider reasoning content is stored; only the reasoning token count a provider reports. | `apps/api/src/iacode_api/gateway/store.py` | `test_no_reasoning_content_is_persisted`. |
| 10.7 | Nothing this Gate persists becomes training data: the rights defaults of the provenance policy are preserved. | `.iacode/policies/training-data-policy.md`, `PROVENANCE.json` | `test_gate_one_records_no_training_eligible_data`. |

## 11. Telemetry, logging and correlation

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 11.1 | The gateway exposes request, duration, error, retry, fallback, circuit state, provider health and catalog size metrics through the existing Prometheus endpoint. | `services/model-gateway/src/iacode_model_gateway/telemetry/metrics.py` | `GatewayMetricsTests`; Prometheus scrape after the live smoke. |
| 11.2 | No metric label carries a prompt, a completion, a credential or an unbounded value. | `services/model-gateway/src/iacode_model_gateway/telemetry/metrics.py` | `test_metric_labels_are_bounded_and_carry_no_content`. |
| 11.3 | Structured logs carry the correlation and request identifiers, the provider, the model, the route, the attempt, the fallback index, the latency, the status and the error type where each is known. | `services/model-gateway/src/iacode_model_gateway/telemetry/logs.py` | `test_gateway_log_contract`. |
| 11.4 | An authorization header, an API key, a full prompt and a full response are never written to a log. | `services/model-gateway/src/iacode_model_gateway/telemetry/logs.py` | `SecretContainmentTests`. |
| 11.5 | A correlation identifier propagates from the HTTP request through every provider attempt to the persisted record, so one call is traceable end to end. | `apps/api/src/iacode_api/routes/gateway.py` | `test_correlation_reaches_the_persisted_model_call`. |

## 12. The gateway HTTP API

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 12.1 | The gateway API is versioned and documented in the OpenAPI document. | `apps/api/src/iacode_api/routes/gateway.py` | `test_openapi_documents_the_gateway_endpoints`. |
| 12.2 | The provider listing returns safe metadata only and never a credential, an authorization header or a secret value. | `apps/api/src/iacode_api/routes/gateway.py` | `test_provider_listing_exposes_no_secret`. |
| 12.3 | The model listing filters by provider, by active state and by capability. | `apps/api/src/iacode_api/routes/gateway.py` | `test_model_listing_filters`. |
| 12.4 | The synchronization endpoint reports what was added, updated, deactivated, unchanged and what failed, without exposing a provider secret. | `apps/api/src/iacode_api/routes/gateway.py` | `test_sync_endpoint_reports_its_outcome`. |
| 12.5 | The inference endpoint returns the normalized response, the route information, the usage and the request identifier, and never a stack trace. | `apps/api/src/iacode_api/routes/gateway.py` | `test_infer_endpoint_returns_the_normalised_response`; `test_infer_endpoint_leaks_no_internal_detail`. |
| 12.6 | The gateway health endpoint separates the process from the external provider, so an unreachable provider is reported without claiming the service is down. | `apps/api/src/iacode_api/routes/gateway.py` | `test_gateway_health_separates_process_from_provider`. |

## 13. Frontend

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 13.1 | A Model Gateway page shows the provider status, the model count, the last synchronization and the model list with its capabilities. | `apps/web/src/app/gateway/` | Frontend unit tests; browser check recorded in the runbook. |
| 13.2 | A minimal playground sends a prompt with a route or a model and an optional reasoning effort, and shows the chosen model, the provider, the answer, the latency and the usage when it exists. | `apps/web/src/app/gateway/` | Frontend unit tests. |
| 13.3 | No provider credential reaches the browser: the page calls the IACode backend and nothing else. | `apps/web/src/app/` | `test_frontend_calls_only_the_iacode_backend`. |
| 13.4 | No conversation persistence, chat history, persona, agent interface or tool execution is added to the frontend. | `apps/web/src/app/` | `test_frontend_adds_no_conversation_capability`. |
| 13.5 | The frontend suite covers the new page and its service, runs headless and is part of the verification command. | `apps/web/src/`, `scripts/iacode/verify.py` | Frontend test run. |

## 14. Live provider integration

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 14.1 | A real catalog synchronization runs against the configured provider API, parses the answer, normalizes it, persists it and repeats without changing anything. | `scripts/iacode/gateway_smoke.py` | Live catalog run. |
| 14.2 | A real non-streaming inference against the explicitly configured smoke model returns the expected text through the normalized response. | `scripts/iacode/gateway_smoke.py` | Live inference run. |
| 14.3 | A real streaming inference produces a start, at least one delta and an end, with no duplicated content. | `scripts/iacode/gateway_smoke.py` | Live streaming run. |
| 14.4 | The configured smoke model is never silently substituted: its absence from the discovered catalog fails the check. | `scripts/iacode/gateway_smoke.py` | `test_absent_smoke_model_fails_rather_than_substitutes`. |
| 14.5 | The live checks are minimal: a short prompt, a small output cap, no repetition, no deliberate rate limiting and no repeated authentication failure against the real provider. | `scripts/iacode/gateway_smoke.py` | `test_live_smoke_is_bounded_and_minimal`. |
| 14.6 | The live inference produced a persisted record carrying the provider, the model, the status, the latency and the usage the provider supplied, and carrying no prompt. | `scripts/iacode/gateway_smoke.py` | Live persistence check. |
| 14.7 | The observability stack observed the live gateway request. | `infra/prometheus/prometheus.yml` | Prometheus query after the live smoke. |
| 14.8 | Without a configured provider credential the live validation fails loudly and the Gate is blocked, and no result is claimed that was not executed. | `scripts/iacode/gateway_smoke.py` | `test_missing_credential_blocks_rather_than_passes`. |

## 15. Deterministic verification

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 15.1 | A provider contract suite proves discovery, generation, streaming, usage, error normalization, timeout, cancellation and tool-call normalization for every adapter. | `services/model-gateway/tests/test_provider_contract.py` | Gateway suite run. |
| 15.2 | The catalog suite covers a new model, changed metadata, a removed model, a duplicate, invalid metadata, an unknown capability, a failed transaction and a repeated synchronization. | `services/model-gateway/tests/test_catalog.py` | Gateway suite run. |
| 15.3 | The routing suite covers an explicit model, the default model, capability filtering, an unknown required capability, a disabled provider, an inactive model, an insufficient context window, route priority, fallback order and fallback exhaustion. | `services/model-gateway/tests/test_routing.py` | Gateway suite run. |
| 15.4 | The retry suite proves which classes are retried — rate limiting, server failure, timeout, connection reset — and which are not: authentication, invalid request and context limit. | `services/model-gateway/tests/test_resilience.py` | Gateway suite run. |
| 15.5 | The circuit breaker suite covers the threshold, the open state, fast failure, the cooldown, the half-open probe, recovery and reopening, without waiting in real time. | `services/model-gateway/tests/test_resilience.py` | Gateway suite run. |
| 15.6 | The streaming suite covers a normal stream, an empty stream, a failure before the first delta, a failure after the first delta, consumer cancellation, usage at the end and a tool-call delta. | `services/model-gateway/tests/test_streaming.py` | Gateway suite run. |
| 15.7 | A test proves that two models' output can never be concatenated into one stream. | `services/model-gateway/tests/test_streaming.py` | `test_no_two_models_are_concatenated_in_one_stream`. |
| 15.8 | The structured-output suite proves that an incapable candidate is rejected and that a capable one receives the right configuration. | `services/model-gateway/tests/test_structured_output.py` | Gateway suite run. |
| 15.9 | The secret suite proves that a credential appears in no log, no exception, no HTTP response, no persisted record, no metric and no catalog metadata. | `services/model-gateway/tests/test_secrets.py` | Gateway suite run. |
| 15.10 | Provider unavailability, an invalid credential and rate limiting are exercised with fixtures rather than against the real provider. | `services/model-gateway/tests/` | Gateway suite run. |
| 15.11 | The deterministic provider double exists only under the test fixtures and cannot be reached from a runtime path. | `services/model-gateway/tests/fixtures/` | `test_no_fake_provider_is_registered_at_runtime`. |

## 16. Migrations and compatibility

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 16.1 | The schema change of this Gate is a new migration, and no migration of the previous Gate is edited. | `apps/api/migrations/versions/` | `test_previous_migrations_are_unmodified`. |
| 16.2 | Every migration runs from zero against an empty database and produces the declared schema. | `apps/api/migrations/` | Fresh-install scenario. |
| 16.3 | A database created by the previous Gate upgrades without loss. | `apps/api/migrations/` | Upgrade run recorded in the checkpoint. |
| 16.4 | The Foundation endpoints, the backup and restore procedure, the restart behaviour and the observability stack do not regress. | `scripts/iacode/verify.py` | Full verification run. |

## 17. Documentation and decisions

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 17.1 | An operational runbook documents provider configuration, the variables, synchronization, listing, inference, streaming, fallback, troubleshooting, the live smoke and how to add an adapter. | `docs/runbooks/MODEL-GATEWAY.md` | Procedure reproduced during the delivery. |
| 17.2 | The architecture document describes the gateway boundary, what crosses it and what is deliberately absent. | `docs/ARCHITECTURE.md` | File content. |
| 17.3 | The entry documentation and the development guide describe what exists after this Gate and how to run it. | `README.md`, `docs/DEVELOPMENT.md` | File content consistent with the runtime. |
| 17.4 | Every dependency and version this Gate pins is recorded in the one place that records versions. | `docs/VERSIONS.md` | Recorded versions match the lock files. |
| 17.5 | The API examples are sanitized and carry no real token. | `docs/runbooks/MODEL-GATEWAY.md` | Repository secret scan. |
| 17.6 | Every structural decision of this Gate that is not already recorded becomes an ADR, and no ADR duplicates an existing decision. | `docs/adr/` | `ADR-0016` to `ADR-0019`. |

## 18. Gate consistency

| Key | Requirement | Artifact | Evidence |
|---|---|---|---|
| 18.1 | The entry contract and the plan describe the current Gate and its status truthfully. | `START-HERE.md`, `docs/MASTER-PLAN.md` | File content consistent with `docs/checkpoints/LATEST.md`. |
| 18.2 | The Gate produces a retrospective from the canonical template. | `.iacode/memory/retrospectives/` | Retrospective file. |
| 18.3 | The Gate closes on the project's own controls and claims no independent, fresh-session or cross-tool verdict. | `docs/checkpoints/GATE-1-CP-0001/STATE.json` | Checkpoint validation. |
