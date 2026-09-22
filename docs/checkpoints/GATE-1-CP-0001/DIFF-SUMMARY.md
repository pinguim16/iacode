# Diff Summary — GATE-1-CP-0001

What changed, grouped by why. The authoritative, hash-bound list is `FILES.json`.

## New: the Model Gateway

`services/model-gateway/` stops being a reservation and becomes the boundary it was reserved for.
It is a package, not a service: the API composes it in process and implements the ports it declares
— [ADR-0016](../../adr/ADR-0016-model-gateway-boundary.md).

| Area | What it is |
|---|---|
| `src/iacode_model_gateway/contracts.py` | the provider-neutral request, response, stream event, model reference and capability vocabulary |
| `errors.py` | the error taxonomy, with `retryable` and `fallbackable` decided by class rather than by call site |
| `config.py` | providers and routes read from versioned policy; the credential resolved from the environment into a `SecretStr` |
| `ports.py` | the storage and the clock the gateway needs, declared inward |
| `protocols/` | three adapters — OpenAI Chat Completions, OpenAI Responses, Anthropic Messages — that translate and perform no I/O |
| `providers/` | the one place that opens a socket, and the provider health contract |
| `catalog/` | discovery from the provider's own API, normalisation, and a synchronisation that is one transaction and refuses an empty answer |
| `routing/` | candidate selection, capability filtering with explained rejections, and the context estimate |
| `resilience/` | retry with full-jitter backoff on an injected clock, the circuit breaker, and the request limits |
| `telemetry/`, `security/`, `pricing.py`, `fingerprint.py` | metrics and log fields that carry no prompt, base-URL validation that resolves no DNS, a cost that is absent rather than invented, and a hash that correlates without storing content |
| `tests/` | the suite: deterministic, no network, no stack, with the provider doubles unreachable from any runtime path |

## New: the application's side of the boundary

| Path | What it is |
|---|---|
| `apps/api/src/iacode_api/gateway/` | the SQLAlchemy stores that answer the gateway's ports, and the runtime that composes it |
| `apps/api/src/iacode_api/routes/gateway.py` | the HTTP API, with an allow-list of public error detail keys |
| `apps/api/migrations/versions/0002_model_gateway.py` | the schema change, with a real downgrade |
| `packages/contracts/src/iacode_contracts/gateway.py` | the camelCase wire contracts |
| `apps/web/src/app/gateway/` | the Model Gateway page and its one-shot playground |

The web shell gains a router, because it now has two pages; the Foundation page moves under the
route that owns it.

## New: the live check and its policy

`scripts/iacode/gateway_smoke.py` runs the three kinds of live call this Gate is allowed — catalog,
one inference, one stream — and then reads the record the API wrote and the series Prometheus
scraped. Without a credential it exits `BLOCKED` naming the variable, never `PASS`.

`.iacode/policies/providers.json` and `.iacode/policies/model-routes.json` declare which providers
exist and which route aliases resolve to what. Neither holds a value: they name environment
variables — [ADR-0019](../../adr/ADR-0019-credentials-are-named-not-stored.md).

## Changed: the control plane, because this Gate's own findings required it

| Path | Why |
|---|---|
| `scripts/iacode/compose.py` | `build_service`, so a gate cannot measure a stale image (`G1-F-001`), and `psql`, which authenticates from inside the container |
| `scripts/iacode/gates/api_tests.py`, `gates/gateway_tests.py` | both build before they measure |
| `scripts/iacode/image_tests.py` | every counted suite that lives in the image, in one execution, so the executed count can be compared with the derived denominator |
| `scripts/development-ledger/policies.py`, `ledger_common.py` | `reservations_in_force` and `delivered_gate`, so a shared control derives the Gate instead of naming one (`G1-F-002`) |
| `scripts/development-ledger/record_command.py`, `validate_checkpoint.py` | a path Git ignores is not an input the repository carries, and is judged by the content it binds (`G1-F-007`) |
| `packages/common/src/iacode_common/redaction.py` | one definition of what a placeholder is and one of what a name carrying a secret is (`G1-F-003`, `G1-F-005`, `G1-F-008`) |
| `infra/tests/test_compose_definition.py`, `test_backup_tooling.py` | both ask the redaction package instead of writing a third and fourth opinion |
| `tests/test_gate0_foundation.py` | two controls derive the Gate instead of naming `GATE-0` |
| `tests/test_gate1_model_gateway.py` | this Gate's control-plane suite, including the five guardrails its own failures produced |

## Changed: the documentation

`README.md`, `START-HERE.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md` and `docs/VERSIONS.md`
describe what exists after this Gate. `docs/runbooks/MODEL-GATEWAY.md` is new, and `ADR-0016` to
`ADR-0019` record the four structural decisions.

## Changed: the engineering memory

Five lessons and five guardrails, one of them a recorded `GUARDRAIL_FAILURE` against an existing
lesson whose control was too narrow. The Gate retrospective is
`.iacode/memory/retrospectives/GATE-1-CP-0001.md`.

## Not changed

No sealed checkpoint. No historical tag. Nothing under a directory reserved for a later Gate:
`.iacode/policies/gate-scope.json` still declares them and the scope control still refuses them,
now derived from the Gate being delivered rather than from a Gate written into the control.
