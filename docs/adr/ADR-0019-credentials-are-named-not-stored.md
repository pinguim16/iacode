# ADR-0019 — Policy names the credential; only the environment holds it

Status: Accepted
Date: 2026-09-22
Owners: GATE 1 — Model Gateway

## Context

Gate 1 is the first Gate that reaches an external paid service, so it is the first Gate that holds
a credential belonging to someone else. The Gate 1 authorization is explicit: never store an API
key in Git, never repeat a credential that may exist in old chats or configuration, never claim a
live integration passed without running it, and never ask for a secret in a chat or put one in a
report.

Two things must be versioned for the delivery to be reproducible: which providers exist, and how to
reach each one. One thing must not be versioned: the credential. The usual compromise — a
committed config file with a placeholder value that the operator edits — puts the value and its
description in the same file, and the first `git add -A` publishes it.

## Decision

**A versioned policy file names the environment variables. It never holds a value. The value
exists only in `infra/compose/.env`, which Git ignores.**

`.iacode/policies/providers.json` declares each provider's `provider_id`, `adapter`, `enabled`,
`models_path`, `protocols` and the **names** `base_url_env` and `credential_env`. A field whose
name ends in `_env` is validated on load: `ProviderConfig._looks_like_a_variable_name` refuses
anything that is not a plausible variable name, so an operator who pastes a key where a name
belongs gets a startup failure rather than a commit.

`resolve_secret` reads the named variable into a `pydantic.SecretStr`. The resolved value is used
in exactly one place — the headers of the outbound provider call — and is deliberately named
`credential` rather than `secret` throughout the package, because the repository secret scan reads
an assignment to a name ending in `SECRET` as a leak and would flag its own protection.

If the variable is empty, the provider reports itself unreachable and names the variable that is
missing. It never falls back to an unauthenticated call, and the live smoke check exits `BLOCKED`
(code `2`) rather than degrading into a `PASS`.

The credential never reaches the browser. The Angular application talks only to the IACode API, and
the API's gateway error responses carry an allow-list of detail keys so a provider's own error body
cannot pass through.

## Evidence

- `.iacode/policies/providers.json` contains `base_url_env` and `credential_env`, no values.
- `services/model-gateway/src/iacode_model_gateway/config.py`: `_looks_like_a_variable_name`,
  `resolve_secret`, `ResolvedProvider.credential: SecretStr`.
- `services/model-gateway/tests/test_secrets.py` asserts separately that the credential appears in
  no log, no exception, no HTTP response, no persisted record, no metric label and no catalog
  metadata.
- `scripts/development-ledger/gate1_runtime_attacks.py` attack `G1-R`: a value placed where a
  variable name belongs is refused. Attack `G1-Q` mutates the real `.env.example` and runs the real
  infrastructure control against it, restoring the file afterwards.
- `apps/api/src/iacode_api/routes/gateway.py`: `PUBLIC_DETAIL_KEYS`.
- Verified in a browser against the running stack: the loaded bundle and the rendered DOM contain
  no credential and no authorization header of any kind.
- The database has no column that could hold a credential; `test_no_table_stores_a_prompt` asserts
  it against the real schema.

## Alternatives Considered

**A committed config file with the value, and `.gitignore` discipline.** One rename or one `git add
-f` away from publication, and the mistake is permanent in history.

**A secret manager (Vault, cloud KMS).** The right answer for a deployed system and the wrong one
for Gate 1: it adds a service, an authentication path to that service, and a bootstrap credential
that has the same problem one level down. The environment variable is the interface a secret
manager injects into anyway, so adopting one later changes how `.env` is populated, not how the
gateway reads it.

**Encrypted secrets in the repository (SOPS, git-crypt).** Reproducible and shareable, and it
requires key distribution the project does not yet have. It also makes a leaked key harder to
notice, because the ciphertext looks the same before and after it is compromised.

**Put the whole provider definition in the environment.** No policy file, no drift. It also makes
"which providers exist" un-reviewable: the definition would live only on whichever machine last set
it, and a code review could not see that a provider was added.

## Consequences

- A fresh clone cannot call a provider until an operator sets two variables, and the error message
  says which two.
- Adding a provider is a reviewable diff that contains no secret.
- The delivery can be blocked on a missing credential and say so precisely, which is what happened
  in this Gate before the credential was configured.
- Rotating a key is an edit to one ignored file and a stack restart.

## Risks

- **`.env` is copied out of the machine.** Outside what this decision can control; the runbook says
  the file is the only place a value lives, which at least makes the blast radius knowable.
- **A credential arrives through some other channel** — a chat, a screenshot, an old configuration
  file — and is therefore already exposed before it is configured. The mitigation is procedural:
  treat any credential that has travelled outside the environment as compromised and rotate it.
- **The `_env` validator is too permissive.** It refuses what does not look like a variable name;
  a key that happened to look like one would pass. `G1-R` is the standing control.

## Reversal Strategy

Adopting a secret manager means replacing `resolve_secret` with a client call and leaving
`credential_env` as the lookup key. Nothing else in the gateway knows where the value came from.

## Related Artifacts

- [ADR-0016](ADR-0016-model-gateway-boundary.md)
- [ADR-0004](ADR-0004-provenance-default-deny.md)
- `docs/GATE-1-CHECKLIST.md` rows 5.x, 14.8, 17.5
- `docs/runbooks/MODEL-GATEWAY.md`
