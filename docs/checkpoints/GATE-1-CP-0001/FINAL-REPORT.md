# Final Report — GATE-1-CP-0001

## Gate

`GATE 1 — MODEL GATEWAY`, milestone `M1` (Gates 0 to 3).

## Status

`INTERNAL_GATE_PASS`.

The project's own controls passed. That is not an independent verdict and is not recorded as one:
`independentReview` and `redTeam` are `NOT_REQUIRED` with the reason, because `M1` is audited after
Gate 3, and the adversarial battery this run executed is filed as `M1-INTERNAL-RED-TEAM.json`
rather than as a Red Team verdict. An implementing run may not grant itself an independent status.

## Authorization

Derived, not assumed. `docs/checkpoints/GATE-0-CP-0001` is sealed at `INTERNAL_GATE_PASS`,
`docs/MASTER-PLAN.md` places `GATE 1` next with `GATE 0` as its predecessor, and the Gate was
authorized explicitly and scoped to itself: not Gate 2, not Gate 3, not the `M1` audit.
`BASELINE.md` records the check, including the two defects this Gate inherited at `HEAD`.

## Environment

Windows 11 Pro 10.0.26200, Python 3.13.15, Docker with Compose v2, Git. Branch `main`, base commit
`195739ffd5a588a55096ebd8a6a7f64057e1f66d`. The stack is the Gate 0 stack: one PostgreSQL server,
Redis, MinIO, Temporal, Prometheus and Grafana from `infra/compose/docker-compose.yml`. The only
thing this Gate adds to it is an outbound HTTPS call to one configured model provider, whose
address and credential live in `infra/compose/.env`, a file Git ignores.

## Tool / Model / Effort

Claude Code, Anthropic, `claude-opus-5`. Effort is not exposed by the runtime and is recorded as
`not-exposed` rather than guessed.

This is the implementing run: a single session with full memory of its own work, which is exactly
why it may not record an independent verdict about itself. `crossToolValidation` is `NOT_AVAILABLE`
and no attestation mechanism is claimed.

## Deliverables

- `docs/GATE-1-CHECKLIST.md` — the Gate's canonical specification, 18 sections and 122 requirement
  rows, mirrored row for row by `.iacode/policies/canonical-requirements.json`, which was generated
  by the same parser the control reads it with rather than transcribed.
- `services/model-gateway/` — the provider-neutral boundary: contracts with tri-state capabilities
  and provenance, an error taxonomy whose classes decide retry and fallback, three protocol
  adapters that perform no I/O, one HTTP provider that does, catalog discovery and normalisation, a
  deterministic router with explained rejections, retry with full-jitter backoff on an injected
  clock, a circuit breaker scoped to a provider and to a provider-and-model pair, enforced limits,
  metrics, base-URL validation and a request fingerprint.
- `apps/api/src/iacode_api/gateway/` — the application's answer to the gateway's ports, in
  SQLAlchemy, plus `/api/v1/gateway/{providers,models,models/sync,health,infer,stream}` with an
  allow-list of public error detail keys.
- `apps/api/migrations/versions/0002_model_gateway.py` — the schema change, with a real downgrade,
  applying to a database created by the previous Gate.
- `apps/web/src/app/gateway/` — the Model Gateway page: provider status, the catalog with its
  capabilities and their provenance, a synchronise button and a one-shot playground.
- `scripts/iacode/gateway_smoke.py` — the live provider check, which exits `BLOCKED` naming the
  variable that is missing rather than degrading into a pass.
- `docs/runbooks/MODEL-GATEWAY.md` and `ADR-0016` to `ADR-0019`.

## Files Created

115 paths. `FILES.json` declares each one with the reason it exists, and
`finalize_checkpoint.py` binds the hashes rather than the author typing them.

## Files Modified

48 paths: the application, the frontend shell, the infrastructure definition, the policies and
registries this Gate extends, the control-plane tooling repaired by this Gate's own findings, the
engineering memory, the entry documentation, and the integrity chain, which gains the fourteenth
anchor.

Two paths were deleted: the Foundation page's template and service moved under the route that owns
them. No sealed checkpoint was modified and no historical tag was moved.

## Validation

`CHECKPOINT_VALID`. `LESSONS_VALID`. `INTEGRITY_VALID` with fourteen anchors.
`DELIVERY_COMPLETENESS_GATE=PASS` at total coverage and total evidence coverage.
`GREEN_KEEPER_GATE=PASS`. `INTERNAL_MIRROR=PASS`. `GATEWAY_SMOKE=PASS`. The final validation runs
after the commit, so it describes the sealed content rather than a working tree.

## Derived values

| Item | Value |
|---|---|
| Requirements | 161 of 161 `COMPLETE` (122 from the Gate specification, 39 from the lesson preflight) |
| Mandatory requirements | 160; the one non-mandatory row is `LESSON-REQ-0013`, which the preflight derives as advisory |
| Coverage | 100.00% |
| Evidence coverage | 100.00% |
| Provider catalog | PASS — 36 models discovered from the provider's own API |
| Catalog idempotence | PASS — a second synchronisation added 0 and deactivated 0 |
| Live inference | PASS |
| Live streaming | PASS |
| Live persistence | PASS |
| Live observability | PASS |
| Routing | PASS |
| Retry | PASS |
| Circuit breaker | PASS |
| Fallback | PASS |
| Limits | PASS |
| Secrets | PASS |
| Migrations | PASS |
| Backend | PASS |
| Frontend | PASS |
| Builds | PASS |
| Static analysis | PASS |
| Lint | PASS |
| Green Keeper | PASS |
| Completeness | PASS |
| Red Team (internal, Gate 1) | 18 of 18 defended, null-mutation control `VALID` |
| Internal mirror audit | PASS |
| Critical findings | 0 |
| High findings | 0 |
| Medium backlog | 0 |
| Low backlog | 0 |
| Blockers | 0 |
| Integrity | 14 anchors verified, 14 tags resolve |

Every number above is derived: `COUNTS.json` holds the count derivation,
`COMPLETENESS-REPORT.json` the coverage, `REWORK-LOG.jsonl` the Green Keeper cycles,
`M1-INTERNAL-RED-TEAM.json` the battery and `VERIFICATION-REPORT.json` the executions.

## Tests

| Suite | Cases | How it ran |
|---|---|---|
| Control plane | 491 | `python -m unittest discover -s tests`, on the host |
| Backend and Model Gateway | 354 | `python scripts/iacode/image_tests.py`, one pytest invocation inside the API image against the running stack |
| Infrastructure | 48 | `python -m unittest discover -s infra/tests`, against the live services |
| **Counted total** | **893** | every suite `.iacode/policies/test-suites.json` declares |
| Frontend | 30 | Vitest, inside the `webTests` gate; declared as not counted, because the derivation cannot enumerate TypeScript cases without executing the toolchain, and a number it cannot re-derive would be a claim |

The three counted runs are three *physical* executions, recorded with distinct `runId` values, so
none is counted twice. `python scripts/iacode/image_tests.py` exists for that reason: two counted
suites live inside the image, the mandatory gates run them separately because a gate measures one
thing, and the evidence needs one execution with one number.

`python scripts/iacode/verify.py` runs twenty stages and reads the mandatory gate set from
`.iacode/policies/quality-gates.json` rather than carrying a copy, so a gate added to the registry
is covered without editing the command.

Ten mandatory gates: `tests`, `staticAnalysis`, `lessons`, `integrity`, `checkpointValidation`,
`apiTests`, `gatewayTests`, `webTests`, `lint`, `infraDefinition`. Then the stack with real health
conditions, the backend suite against the running services, the infrastructure suite against the
live stack, the smoke check including a Temporal workflow that actually executes, the live Model
Gateway check against the configured provider, a backup with a verified restore and read-back, a
dependency scan, and the three scenarios: restart with data intact, dependency failure with
recovery, and a fresh installation from no volumes at all.

## Live provider integration

The part of this Gate that cannot be simulated, and the part it was blocked on until a credential
was configured. `scripts/iacode/gateway_smoke.py` reports `PASS` on twenty checks against the
configured provider: catalog discovery, a repeated synchronisation that changed nothing, the smoke
model's presence in the discovered catalog, normalisation, a non-streaming inference whose answer
is checked rather than its status code, attribution, latency, the usage the provider reported, an
absent rather than invented cost, a streaming inference with a start, deltas, an end and no
duplication, the persisted record with its provider, model, status, latency and usage and without a
prompt, and a Prometheus query proving the observability stack saw the request.

It is deliberately small: one short prompt, a 32-token output cap, no repetition, no deliberate
rate limiting and no repeated authentication failure against a real account. Provider
unavailability, invalid credentials and rate limiting are proved with fixtures instead.

The configured smoke model is checked against the discovered catalog and never substituted. The
free-tier model tried first returned `502 upstream_error: Provider capacity temporarily
unavailable`, so the check runs against a paid model instead: a mandatory gate whose result depends
on free-tier capacity is a gate that reports on the provider's mood.

## Red Team

`scripts/development-ledger/gate1_red_team.py` executes 18 attacks scoped to this Gate: the
credential in every place it could leak, a request field carrying an address, a plain-HTTP or
user-information configured address, an unknown capability assumed, an authentication failure
retried, a duplicated candidate, the circuit not opening, two models spliced into one stream, a
preflight that lets a request leave, an empty or duplicated catalog applied, a prompt in the
record, an unclassified failure, a substituted model, an unbounded timeout, a vanished model
deleted rather than deactivated, a value where a variable name belongs, a gate measuring a stale
image, a control bound to a Gate literal, and a placeholder replaced by a value in the committed
example.

All 18 defended, over a null-mutation control that is `VALID`: the battery is shown to accept the
unmutated path through the identical code, which is what makes a defence mean anything.

It is filed as `M1-INTERNAL-RED-TEAM.json` and `RED-TEAM-REPORT.md`, and `STATE.json` records
`redTeam` as `NOT_REQUIRED` rather than `RED_TEAM_PASS`. An internal battery is not an independent
Red Team and is not recorded as one.

## Findings this Gate raised against itself

Ten, all closed inside the Gate, all turned into automated controls. `DECISIONS.md` carries the
table.

Two of them were inherited: a red test had been failing at `HEAD` throughout Gate 0 behind a green
gate, because the gate ran inside an image nothing rebuilt. That is `G1-F-001`, and the defect it
concealed is `G1-F-003`. A Gate that inherits a red test and does not say so is a Gate whose
evidence begins with a lie.

Three are `GUARDRAIL_FAILURE`s, and they have one shape: a control written against the place a
failure had been fixed rather than against the rule that has to hold. `LSN-0038`'s guardrail was
scoped to two consumers while the class was general; `LSN-0011`'s named a function, so it guarded
one runner of the mandatory gate set and not the other; and `LSN-0037`, written earlier in this
same Gate, said "a Gate", so the scan it produced could not see a migration revision. All three
were investigated as failures of the control and all three controls were broadened, which is what
the contract requires.

## Engineering memory

Five lessons added, each `GUARDED` by an automated control rather than by prose:

| Lesson | Guardrail |
|---|---|
| `LSN-0036` a gate that runs inside an image measures the image, not the source | `GRD-0038` |
| `LSN-0037` a shared control that names a Gate literally stops being shared at the next Gate | `GRD-0039` |
| `LSN-0038` two representations of one concept in one module disagree, and the safer one loses | `GRD-0040` |
| `LSN-0039` a test that writes to the operational database leaves production data behind | `GRD-0041` |
| `LSN-0040` a control that judges sealed history only runs once a successor anchors it | `GRD-0042` |

Guardrail effectiveness: 42 of 42 effective, resolved and verified by a test. Three guardrail
failures, recorded, investigated and resolved inside this Gate, and one lesson added about what
all three had in common: each control had been written against the place a failure was fixed
rather than against the rule that has to hold.

## Scope

Nothing reserved for a later Gate is implemented. `.iacode/policies/gate-scope.json` declares which
path belongs to which Gate, `MIR-018` checks it against the Gate being delivered rather than
against a Gate named in the control, and each remaining reserved directory carries a README stating
the reservation and nothing else.

There is no agent, no tool execution, no retrieval, no training and no experience store. A tool
call is normalised and never executed. There is no conversation, no memory between requests and no
prompt in the database.

## Security

The provider credential exists only in `infra/compose/.env`. The versioned policy names the
variable; a value written where a name belongs is refused at load. The resolved value is a
`SecretStr` used in one place — the headers of the outbound call — and `test_secrets.py` asserts
separately that it appears in no log, no exception, no HTTP response, no persisted record, no
metric label and no catalog entry. The browser was checked against the running stack: the loaded
bundle and the rendered DOM carry no credential of any kind.

The database has no column that could hold a prompt, a completion or a credential, and the schema
is the control rather than the discipline of the code above it.
`IACODE_GATEWAY_PERSIST_PROMPTS` is `false` and nothing stands behind it in this Gate. A stored
request fingerprint is a SHA-256, and the runbook says in as many words that a hash is not
anonymisation.

## Commit and tag

Recorded in `STATE.json` and in `docs/checkpoints/LATEST.md` after sealing. The checkpoint is
sealed with `seal_checkpoint.py`, so the final validation describes the committed content rather
than a dirty working tree, and the tag is `refs/tags/iacode-checkpoints/GATE-1-CP-0001`.

## Known Risks

`RISKS.md` carries them, each with the condition that turns it into a defect rather than a feeling.
The ones that bear on the next Gate:

- Every capability except streaming is `UNKNOWN` for this provider, because it publishes no
  capability metadata. The router refuses an unknown capability rather than guessing, so a Gate 2
  agent that requires tool calling will be refused until an operator states the capability or a
  route opts in. That is deliberate friction and it will be met on Gate 2's first day.
- 35 of the 36 catalogued models have never been called through this gateway. The boundary is
  protocol-level and the provider serves them all over one protocol, so the risk is about
  individual models rather than about the boundary.
- No pricing is configured, so every recorded call has a null cost. The operational record answers
  "how many tokens" and not "how much money".
- A credential that has travelled outside the environment is already exposed; the controls make the
  blast radius knowable, not zero.

## Remaining Work

None inside this Gate. Every requirement is `COMPLETE` with resolved evidence, none is `PARTIAL` or
`MISSING`, and there is no backlog item at any severity: the ten findings this delivery raised
against itself were repaired rather than deferred.

## Handoff Readiness

`HANDOFF.md` states the validation commands and the stop conditions, and `MIR-018` checks that it
is executable without this session. An operator follows `docs/runbooks/MODEL-GATEWAY.md`: set two
variables, start the stack, synchronise the catalog, pick a model the catalog actually contains,
and run the live check.

## Evidence

| Artifact | What it holds |
|---|---|
| `VERIFICATION-REPORT.json` | every execution this checkpoint relies on |
| `COMMANDS.jsonl` | the ledger, with input digests, including the recorded failures |
| `REQUIREMENTS-MATRIX.json` | the requirement set with implementation, test, documentation and validation evidence |
| `COMPLETENESS-REPORT.json` | the completeness audit and the denominator it measured |
| `REWORK-LOG.jsonl` | the Green Keeper cycles, red attempts included |
| `M1-INTERNAL-RED-TEAM.json`, `RED-TEAM-REPORT.md` | the internal battery and its null-mutation control |
| `M1-INTERNAL-MIRROR.json` | the mirror audit of this delivery against the repository |
| `COUNTS.json` | every count, derived once |
| `LESSON-PREFLIGHT.json` | the lessons considered before the Gate started, and what each required |
| `.iacode/memory/retrospectives/GATE-1-CP-0001.md` | the Gate retrospective |

## Next Gate

`GATE 2 — AGENT RUNTIME`, which requires the owner's explicit authorization and a new pre-Gate
checkpoint. No Gate 2 work exists in this change set.

`M1` is `PENDING`: audited after Gate 3.
