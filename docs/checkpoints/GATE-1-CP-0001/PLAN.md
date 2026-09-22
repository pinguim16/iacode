# Plan — GATE-1-CP-0001

## What this Gate delivers

One provider-neutral boundary for invoking a model, and everything that makes such a boundary
trustworthy rather than merely present: providers registered from versioned policy, models
discovered from each provider's own API, capabilities normalised with the provenance of every
claim, a deterministic router, real inference and real streaming, normalised usage and tool calls,
a persisted operational record that carries no prompt, retries and timeouts and a circuit breaker
and a bounded fallback chain, enforced limits, metrics, and a credential that exists only in the
environment.

The success criterion is not "a model answered". It is that a caller can ask for a capability
rather than a vendor; that every failure has a class which decides whether it may be retried and
whether it may fall back; that a stream can never carry two models' text; that no credential
reaches a log, a response, a metric, the database or the browser; and that the live provider
integration is proved by running it, not by asserting it.

## What this Gate does not deliver

Agents, tool execution, training, retrieval, or an experience store. The gateway *normalises* a
tool call — it reports what the model asked for — and nothing here executes one. There is no
conversation, no memory between requests, and no prompt in the database.

`.iacode/policies/gate-scope.json` records which Gate owns each reserved directory, and the scope
control fails a delivery that fills one early. GATE 1 consumes exactly one reservation:
`services/model-gateway/`.

## Order of work

The delivery order in `docs/DEVELOPMENT-CONTRACT.md`, with this Gate's content inside step 4:

1. **Cold start and authorization.** Read the contracts, confirm `GATE-0-CP-0001` closed at
   `INTERNAL_GATE_PASS`, confirm Git state. Recorded in `BASELINE.md`.
2. **Pre-Gate checkpoint.** `GATE-1-CP-0001`, milestone `M1`, status `BASELINING`.
3. **Lesson preflight.** `lesson_preflight.py --gate GATE-1 --scope model-gateway`, with the
   technologies and modules this Gate actually uses. Thirty-four applicable lessons, thirty-four
   derived requirements.
4. **Canonical specification.** `docs/GATE-1-CHECKLIST.md`, 18 sections and 122 requirement rows,
   mirrored row-for-row into `.iacode/policies/canonical-requirements.json` by
   `policies.parse_checklist` rather than by hand.
5. **Requirement derivation.** `derive_requirements.py --write` → 156 rows (122 canonical + 34
   lesson) in `REQUIREMENTS-MATRIX.json`.
6. **Implementation**, in dependency order:
   - contracts, error taxonomy, configuration and secrets, ports;
   - protocol adapters (OpenAI Chat Completions, OpenAI Responses, Anthropic Messages) and the one
     HTTP provider that performs I/O;
   - catalog normalisation and synchronisation;
   - routing, policy and context estimation;
   - retry, circuit breaker, limits;
   - telemetry, pricing, fingerprint, base-URL validation;
   - the application's SQLAlchemy stores, the gateway runtime, the HTTP routes, the migration;
   - the Angular route, the Model Gateway page and its playground.
7. **Tests.** A gateway suite that needs no network and no stack, plus API unit tests, integration
   tests against the real PostgreSQL, frontend tests, infrastructure tests and a control-plane
   suite for this Gate.
8. **Green Keeper**, until every mandatory gate is green, with `gatewayTests` added to the registry.
9. **Delivery Completeness Validator**, until every matrix row has a status and resolvable evidence.
10. **Internal Red Team**, focused on this Gate.
11. **Live provider integration** — the one part that cannot be simulated.
12. **Documentation, ADRs, lessons, guardrails, retrospective**, then seal.

## Architectural decisions taken before implementing

- The gateway is a library in `services/model-gateway/`, composed in process, with its dependencies
  pointing inward — `ADR-0016`.
- A capability is `SUPPORTED`, `UNSUPPORTED` or `UNKNOWN`, and carries its provenance. There is no
  inference from a model's name — `ADR-0017`.
- A stream commits to one model at its first delivered event — `ADR-0018`.
- Policy names the credential's variable; only the environment holds a value — `ADR-0019`.

## How the live integration is bounded

Live provider calls are limited to three kinds: catalog discovery, one non-streaming inference and
one streaming inference, with a short prompt and a 32-token cap. Failure modes — rate limiting,
invalid credentials, unavailability, timeouts — are proved with fixtures. No rate limit is
deliberately provoked and no authentication failure is repeated against a real account.

Without a credential the Gate stops at `BLOCKED` and names the variable that is missing. It does
not claim a live result it did not obtain.

## Stop conditions

Any of: a red mandatory gate; completeness below 100%; a Critical or High finding; a leaked
credential; a prompt persisted by default; an unbounded timeout; a fallback loop; two models mixed
in one stream; a migration that does not apply to a Gate 0 database; or a live integration that was
not executed.
