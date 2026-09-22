# Red Team Report — GATE 1 — MODEL GATEWAY

Result: `RED_TEAM_PASS`

- Checkpoint: `GATE-1-CP-0001`
- Generated: `2026-09-22T09:12:10Z`
- Source: scripts/development-ledger/gate1_red_team.py with gate1_runtime_attacks.py — the internal adversarial battery of GATE 1 — MODEL GATEWAY, executed against the delivery
- Attacks: 18/18 defended

## Null-mutation control

Result: `VALID`

the unmutated fixture is accepted by every control this battery mutates: the gateway serves an unmutated request (the unmutated path synchronises, answers, streams, records and accepts a clean address); the scope control accepts the real tree (no violation); the secret scan accepts the committed configuration (no finding); the canonical requirement set parses and mirrors (122 row(s))

Without this the battery would prove nothing: a gateway that refused every request would
look perfectly defended. The unmutated path goes through the identical code and is
accepted before any mutation runs.

## Findings

None.

## Attacks

| Attack | Category | Target | Mutation | Expected | Observed | Result |
|---|---|---|---|---|---|---|
| `G1-A` | mandatory | secrets | classify a provider failure while a credential is resolved, then render the error, the resolved provider, its repr, the recorded calls and the provider registry | the credential appears in none of them | the credential is in no error, no record, no repr and no dump | `DEFENDED` |
| `G1-B` | mandatory | trust boundary | look for a request field that could carry an address, then configure a link-local address, an address with user information, a file URL and one with a query string | no request field exists, and every unusable configured address is refused | no request field can carry an address, and a plain-HTTP, user-information, non-HTTP or query-bearing configured address is refused | `DEFENDED` |
| `G1-C` | mandatory | routing | send a request with tools to a model whose tool support is UNKNOWN | the candidate is refused rather than tried | the unknown capability was refused rather than assumed | `DEFENDED` |
| `G1-D` | mandatory | resilience | script an authentication failure followed by a success and count the attempts | exactly one attempt is made | one attempt; an authentication failure is never retried | `DEFENDED` |
| `G1-E` | mandatory | resilience | configure a route whose candidate list repeats one model and fail every call | the duplicate collapses to one attempt and the chain stays bounded | the duplicate candidate collapsed to one attempt; the chain is bounded | `DEFENDED` |
| `G1-F` | mandatory | resilience | fail past the configured threshold, then call again and count the provider's attempts | the circuit opens and the next call never reaches the provider | the circuit opened after 2 failures and the next call never left | `DEFENDED` |
| `G1-G` | mandatory | streaming | stream text from the first candidate, fail it, and give the router a healthy second candidate | the second model is never called and no output is spliced | the second model was never called and no output was spliced | `DEFENDED` |
| `G1-H` | mandatory | routing | send two hundred thousand characters to a model with a one-thousand token window | the preflight refuses before the request leaves the process | the preflight refused before the request left the process | `DEFENDED` |
| `G1-I` | mandatory | catalog | synchronise against an empty answer and then against a duplicate, and read the catalog | the previous catalog survives both, active and intact | an empty answer and a duplicated identifier both left the catalog intact | `DEFENDED` |
| `G1-J` | mandatory | privacy | send a sentence that must not be stored and render every recorded field | neither the prompt nor the completion is present, and no field could hold one | neither the prompt nor the completion is in the record, and no field could hold one | `DEFENDED` |
| `G1-K` | mandatory | resilience | fail both candidates of a route with a transport failure | both are tried once, the failure is classified, and the caller is not held | both candidates were tried once and the failure was classified | `DEFENDED` |
| `G1-L` | mandatory | routing | request an identifier the catalog does not hold while a healthy model exists | the request is refused and no other model is used in its place | the named model was refused and no other model was used in its place | `DEFENDED` |
| `G1-M` | mandatory | resilience | read the client construction, then configure a zero and an absurd timeout | connect and read are separate, always set, and an unusable value is refused at load time | connect and read budgets are separate, always set, and a zero or absurd value is refused at load time | `DEFENDED` |
| `G1-N` | mandatory | catalog | record a call against a model, remove it from the provider's answer, synchronise again | it is deactivated rather than deleted, its recorded call survives, and a new request for it is refused | the vanished model was deactivated rather than deleted, its recorded call survived, and a new request for it was refused | `DEFENDED` |
| `G1-R` | mandatory | secrets | configure a provider whose credential variable is a credential, and one that serves no protocol | both are refused when the configuration loads, not when the first call fails | a value where a variable name belongs is refused at load time, and so is a provider that declares no protocol | `DEFENDED` |
| `G1-O` | mandatory | delivery assurance | plant a failing test in the API suite on disk and run the real mandatory gate | the gate builds the image first and reports the failure | the gate rebuilt and failed on the planted test: [iacode] API_UNIT_TESTS=FAIL | `DEFENDED` |
| `G1-P` | mandatory | delivery assurance | run the scope control with the derived Gate and with the previous Gate written in | the derived answer is clean and the literal one is not, so the derivation is what works | derived from GATE-1 the tree is clean; with the previous Gate written in, the same control reports 1 violation(s) — the literal would have blocked this Gate | `DEFENDED` |
| `G1-Q` | mandatory | secrets | replace the placeholder of the provider credential in the committed example file with a credential-shaped value and run the real infrastructure control | the control refuses the file, naming the key | the control refused the example file the moment its placeholder became a value, and the file was restored | `DEFENDED` |

## What each attack means

### G1-A — A provider echoes the credential back, and every surface the gateway produces is searched.

- Mutation: classify a provider failure while a credential is resolved, then render the error, the resolved provider, its repr, the recorded calls and the provider registry
- Expected defence: the credential appears in none of them
- Observed: the credential is in no error, no record, no repr and no dump
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/config.py`, `test:SecretContainmentTests`

### G1-B — A caller supplies the address the gateway should call.

- Mutation: look for a request field that could carry an address, then configure a link-local address, an address with user information, a file URL and one with a query string
- Expected defence: no request field exists, and every unusable configured address is refused
- Observed: no request field can carry an address, and a plain-HTTP, user-information, non-HTTP or query-bearing configured address is refused
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/security/base_url.py`, `test:BaseUrlSafetyTests`

### G1-C — A request needs a capability the catalog never recorded.

- Mutation: send a request with tools to a model whose tool support is UNKNOWN
- Expected defence: the candidate is refused rather than tried
- Observed: the unknown capability was refused rather than assumed
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/routing/policy.py`, `test:test_unknown_capability_is_rejected_by_default`

### G1-D — A credential failure is retried, burning quota on an answer that cannot change.

- Mutation: script an authentication failure followed by a success and count the attempts
- Expected defence: exactly one attempt is made
- Observed: one attempt; an authentication failure is never retried
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/resilience/retry.py`, `test:RetryClassificationTests`

### G1-E — A route names the same failing candidate twelve times.

- Mutation: configure a route whose candidate list repeats one model and fail every call
- Expected defence: the duplicate collapses to one attempt and the chain stays bounded
- Observed: the duplicate candidate collapsed to one attempt; the chain is bounded
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`, `test:test_fallback_chain_is_bounded_and_recorded`

### G1-F — Traffic keeps arriving at a provider that is down, so every caller pays the full timeout.

- Mutation: fail past the configured threshold, then call again and count the provider's attempts
- Expected defence: the circuit opens and the next call never reaches the provider
- Observed: the circuit opened after 2 failures and the next call never left
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/resilience/circuit.py`, `test:CircuitBreakerTests`

### G1-G — A stream dies after delivering text and a second model is offered the chance to finish it.

- Mutation: stream text from the first candidate, fail it, and give the router a healthy second candidate
- Expected defence: the second model is never called and no output is spliced
- Observed: the second model was never called and no output was spliced
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/gateway.py`, `test:test_no_two_models_are_concatenated_in_one_stream`

### G1-H — A request far larger than the context window is sent anyway.

- Mutation: send two hundred thousand characters to a model with a one-thousand token window
- Expected defence: the preflight refuses before the request leaves the process
- Observed: the preflight refused before the request left the process
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/routing/context.py`, `test:ContextWindowTests`

### G1-I — A synchronisation answers with nothing, then with a duplicated identifier.

- Mutation: synchronise against an empty answer and then against a duplicate, and read the catalog
- Expected defence: the previous catalog survives both, active and intact
- Observed: an empty answer and a duplicated identifier both left the catalog intact
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py`, `test:test_failed_sync_preserves_the_previous_catalog`

### G1-J — A confidential prompt is sent and the record is searched for it.

- Mutation: send a sentence that must not be stored and render every recorded field
- Expected defence: neither the prompt nor the completion is present, and no field could hold one
- Observed: neither the prompt nor the completion is in the record, and no field could hold one
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/ports.py`, `test:PromptCaptureTests`

### G1-K — Every provider is unreachable.

- Mutation: fail both candidates of a route with a transport failure
- Expected defence: both are tried once, the failure is classified, and the caller is not held
- Observed: both candidates were tried once and the failure was classified
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/providers/http_provider.py`, `test:test_provider_unavailability_falls_back`

### G1-L — A caller names a model that is not in the catalog, hoping for a substitute.

- Mutation: request an identifier the catalog does not hold while a healthy model exists
- Expected defence: the request is refused and no other model is used in its place
- Observed: the named model was refused and no other model was used in its place
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/routing/router.py`, `test:test_explicit_model_is_honoured_or_refused`

### G1-M — The configuration is asked for a call with no time limit.

- Mutation: read the client construction, then configure a zero and an absurd timeout
- Expected defence: connect and read are separate, always set, and an unusable value is refused at load time
- Observed: connect and read budgets are separate, always set, and a zero or absurd value is refused at load time
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/config.py`, `test:test_no_call_is_unbounded`

### G1-N — A model vanishes from the provider between two synchronisations.

- Mutation: record a call against a model, remove it from the provider's answer, synchronise again
- Expected defence: it is deactivated rather than deleted, its recorded call survives, and a new request for it is refused
- Observed: the vanished model was deactivated rather than deleted, its recorded call survived, and a new request for it was refused
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/catalog/sync.py`, `test:test_missing_model_is_deactivated_not_deleted`

### G1-R — The key itself is pasted into the field that holds the name of its variable.

- Mutation: configure a provider whose credential variable is a credential, and one that serves no protocol
- Expected defence: both are refused when the configuration loads, not when the first call fails
- Observed: a value where a variable name belongs is refused at load time, and so is a provider that declares no protocol
- Evidence: `file:services/model-gateway/src/iacode_model_gateway/config.py`, `test:test_a_configuration_that_put_a_value_where_a_name_belongs_is_refused`

### G1-O — A gate that runs inside an image measures the image instead of the source.

- Mutation: plant a failing test in the API suite on disk and run the real mandatory gate
- Expected defence: the gate builds the image first and reports the failure
- Observed: the gate rebuilt and failed on the planted test: [iacode] API_UNIT_TESTS=FAIL
- Evidence: `file:scripts/iacode/compose.py`, `file:scripts/iacode/gates/api_tests.py`

### G1-P — A generic control decides from the name of the Gate it was written during.

- Mutation: run the scope control with the derived Gate and with the previous Gate written in
- Expected defence: the derived answer is clean and the literal one is not, so the derivation is what works
- Observed: derived from GATE-1 the tree is clean; with the previous Gate written in, the same control reports 1 violation(s) — the literal would have blocked this Gate
- Evidence: `file:scripts/development-ledger/ledger_common.py`, `test:test_no_future_gate_capability_is_implemented`

### G1-Q — A credential value is committed where a placeholder belongs.

- Mutation: replace the placeholder of the provider credential in the committed example file with a credential-shaped value and run the real infrastructure control
- Expected defence: the control refuses the file, naming the key
- Observed: the control refused the example file the moment its placeholder became a value, and the file was restored
- Evidence: `file:infra/compose/.env.example`, `file:infra/tests/test_compose_definition.py`
